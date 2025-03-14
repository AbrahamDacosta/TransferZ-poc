import os
import json
import jwt
import datetime
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Middleware CORS pour autoriser les requêtes du frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base de données fictive (stockée en JSON temporairement)
DB_FILE = "/tmp/database.json"
SECRET_KEY = "MY_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Gestion des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def load_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}, "transactions": []}
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"users": {}, "transactions": []}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def create_access_token(data: dict, expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_delta)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    db = load_db()
    user = db["users"].get(username)
    if not user or not verify_password(password, user["password"]):
        return False
    return user

def auth_required(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

class UserRegister(BaseModel):
    username: str
    password: str

@app.post("/register/")
def register(user: UserRegister):
    db = load_db()
    if user.username in db["users"]:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = get_password_hash(user.password)
    db["users"][user.username] = {"password": hashed_password, "balance_fcfa": 0.0, "balance_stablecoin": 0.0}
    save_db(db)
    return {"message": "User registered successfully"}

class UserLogin(BaseModel):
    username: str
    password: str



@app.post("/login/")
def login(user: UserLogin):
    auth_user = authenticate_user(user.username, user.password)
    if not auth_user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint pour effectuer un dépôt
@app.post("/deposit/")
def deposit(username: str = Depends(auth_required), amount: float = 0):
    db = load_db()
    if username not in db["users"]:
        raise HTTPException(status_code=404, detail="User not found")
    db["users"][username]["balance_fcfa"] += amount
    save_db(db)
    return {"message": "Deposit successful", "new_balance": db["users"][username]["balance_fcfa"]}


# Endpoint pour convertir en stablecoin
@app.post("/convert_stablecoin/")
def convert_stablecoin(amount: float, user: str = Depends(get_current_user)):
    db = load_db()
    if user not in db["users"]:
        raise HTTPException(status_code=404, detail="User not found")
    if db["users"][user]["balance_fcfa"] < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    db["users"][user]["balance_fcfa"] -= amount
    db["users"][user]["balance_stablecoin"] += amount / 655  # Taux de conversion FCFA → stablecoin
    save_db(db)
    return {"message": "Conversion successful"}



# Endpoint pour transfert P2Pß
@app.post("/transfer/")
def transfer(sender: str = Depends(auth_required), receiver: str = "", amount: float = 0):
    db = load_db()
    if sender not in db["users"] or receiver not in db["users"]:
        raise HTTPException(status_code=404, detail="User not found")
    if db["users"][sender]["balance_stablecoin"] < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    db["users"][sender]["balance_stablecoin"] -= amount
    db["users"][receiver]["balance_stablecoin"] += amount
    save_db(db)
    return {"message": "Transfer successful"}
