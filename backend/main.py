import os
import json
import jwt
import datetime
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from passlib.context import CryptContext

app = FastAPI()

# 🔑 Configuration de la sécurité
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# 📂 Gestion de la base de données (stockée dans /tmp pour Render)
DB_PATH = "/tmp/database.json"
if not os.path.exists(DB_PATH):
    with open(DB_PATH, "w") as f:
        json.dump({"users": {}, "transactions": []}, f, indent=4)

def load_db():
    with open(DB_PATH, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=4)

# 📌 Modèles Pydantic
class UserRegister(BaseModel):
    username: str
    password: str
    phone_numbers: list[str] 

class UserLogin(BaseModel):
    username: str
    password: str

class DepositRequest(BaseModel):
    phone_number: str
    amount: float

class ConvertRequest(BaseModel):
    amount: float

class TransferRequest(BaseModel):
    receiver: str
    amount: float

class WithdrawRequest(BaseModel):
    phone_number: str
    amount: float

# 🔑 Fonctions d'authentification
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    expire = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

# 🆕 Route d'inscription
@app.post("/register/")
def register(user: UserRegister):
    db = load_db()
    if user.username in db["users"]:
        raise HTTPException(status_code=400, detail="Username already registered")

    if len(user.phone_numbers) > 3:
        raise HTTPException(status_code=400, detail="Maximum 3 mobile money accounts allowed")

    db["users"][user.username] = {
        "password": get_password_hash(user.password),
        "phone_numbers": user.phone_numbers,
        "balance_fcfa": 0,
        "balance_stablecoin": 0
    }
    save_db(db)
    return {"message": "User registered successfully"}

# 🔑 Route de connexion
@app.post("/login/")
def login(user: UserLogin):
    db = load_db()
    if user.username not in db["users"]:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not verify_password(user.password, db["users"][user.username]["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token}

# 📲 Dépôt d'argent via Mobile Money
@app.post("/deposit/")
def deposit_funds(data: DepositRequest, user: str = Depends(get_current_user)):
    db = load_db()
    if user not in db["users"] or data.phone_number not in db["users"][user]["phone_numbers"]:
        raise HTTPException(status_code=400, detail="Numéro Mobile Money non enregistré.")

    db["users"][user]["balance_fcfa"] += data.amount
    save_db(db)
    return {"message": "Dépôt réussi", "new_balance_fcfa": db["users"][user]["balance_fcfa"]}

# 💱 Conversion FCFA → Stablecoin
@app.post("/convert_stablecoin/")
def convert_stablecoin(data: ConvertRequest, user: str = Depends(get_current_user)):
    db = load_db()
    if db["users"][user]["balance_fcfa"] < data.amount:
        raise HTTPException(status_code=400, detail="Fonds insuffisants.")

    conversion_rate = 655  # 1 USDT = 655 FCFA
    stablecoin_amount = data.amount / conversion_rate
    db["users"][user]["balance_fcfa"] -= data.amount
    db["users"][user]["balance_stablecoin"] += stablecoin_amount
    save_db(db)
    return {"message": "Conversion réussie"}

# 🔄 Transfert P2P de Stablecoins
@app.post("/transfer/")
def transfer_stablecoins(data: TransferRequest, user: str = Depends(get_current_user)):
    db = load_db()
    if db["users"][user]["balance_stablecoin"] < data.amount:
        raise HTTPException(status_code=400, detail="Fonds insuffisants.")

    db["users"][user]["balance_stablecoin"] -= data.amount
    db["users"][data.receiver]["balance_stablecoin"] += data.amount
    save_db(db)
    return {"message": "Transfert réussi"}

# 💸 Retrait Mobile Money
@app.post("/withdraw/")
def withdraw_stablecoins(data: WithdrawRequest, user: str = Depends(get_current_user)):
    db = load_db()
    if db["users"][user]["balance_stablecoin"] < data.amount:
        raise HTTPException(status_code=400, detail="Fonds insuffisants.")

    conversion_rate = 655  
    fcfa_amount = data.amount * conversion_rate
    db["users"][user]["balance_stablecoin"] -= data.amount
    db["users"][user]["balance_fcfa"] += fcfa_amount
    save_db(db)
    return {"message": "Retrait réussi"}
