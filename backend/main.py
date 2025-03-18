import os
import json
import uuid
import datetime
import eth_keys
from eth_keys import keys
from eth_utils import encode_hex
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt

app = FastAPI()

# 🔑 Configuration Sécurité
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# 📂 Gestion de la base de données
DB_PATH = "/tmp/database.json"
if not os.path.exists(DB_PATH):
    with open(DB_PATH, "w") as f:
        json.dump({"users": {}, "transactions": []}, f, indent=4)

def load_db():
    db_path = "/tmp/database.json"  # Vérifie si le fichier est bien ici
    if not os.path.exists(db_path):
        with open(db_path, "w") as f:
            json.dump({"users": {}, "transactions": []}, f, indent=4)
    with open(db_path, "r") as f:
        return json.load(f)


def save_db(data):
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=4)

# 🎯 Génération du DID et du compte Blockchain
def generate_did():
    private_key = keys.PrivateKey(os.urandom(32))
    public_key = private_key.public_key
    address = encode_hex(public_key.to_checksum_address())

    did = f"did:transferz:{uuid.uuid4()}"
    return did, encode_hex(private_key), address

# 📌 Modèles Pydantic
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class AddPhoneRequest(BaseModel):
    phone_number: str

class DepositRequest(BaseModel):
    phone_number: str
    amount: float

class TransferRequest(BaseModel):
    receiver_did: str
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

# 📌 Inscription avec génération automatique de DID
import logging
logging.basicConfig(level=logging.DEBUG)

@app.post("/register/")
def register(user: UserRegister):
    logging.debug("📌 Route /register/ appelée")
    
    db = load_db()
    if user.username in db["users"]:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà enregistré")

    did, private_key, blockchain_address = generate_did()

    db["users"][user.username] = {
        "password": get_password_hash(user.password),
        "did": did,
        "private_key": private_key,
        "blockchain_address": blockchain_address,
        "phone_numbers": [],
        "balance_fcfa": 0,
        "balance_stablecoin": 0
    }
    save_db(db)

    return {"message": "Utilisateur créé avec succès", "did": did, "blockchain_address": blockchain_address}

# 🔑 Connexion de l’utilisateur
@app.post("/login/")
def login(user: UserLogin):
    db = load_db()

    if user.username not in db["users"] or not verify_password(user.password, db["users"][user.username]["password"]):
        raise HTTPException(status_code=401, detail="Identifiants invalides")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token}

# 📲 Ajout d’un numéro Mobile Money
@app.post("/user/add_phone/")
def add_phone(data: AddPhoneRequest, user: str = Depends(get_current_user)):
    db = load_db()

    if user not in db["users"]:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    db["users"][user]["phone_numbers"].append(data.phone_number)
    save_db(db)

    return {"message": "Numéro ajouté et lié à votre DID"}

# 📌 Récupération des DID utilisateurs pour les transferts
@app.get("/list_did_users/")
def list_did_users():
    db = load_db()
    return {"users": [user["did"] for user in db["users"].values()]}

# 📲 Dépôt d’argent via Mobile Money
@app.post("/deposit/")
def deposit_funds(data: DepositRequest, user: str = Depends(get_current_user)):
    db = load_db()

    if user not in db["users"] or data.phone_number not in db["users"][user]["phone_numbers"]:
        raise HTTPException(status_code=400, detail="Numéro Mobile Money non enregistré.")

    db["users"][user]["balance_fcfa"] += data.amount
    save_db(db)

    return {"message": "Dépôt réussi", "new_balance_fcfa": db["users"][user]["balance_fcfa"]}

# 🔄 Transfert P2P via DID
@app.post("/transfer/")
def transfer_stablecoins(data: TransferRequest, user: str = Depends(get_current_user)):
    db = load_db()

    if db["users"][user]["did"] == data.receiver_did:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas vous envoyer de l'argent.")

    receiver = next((u for u, v in db["users"].items() if v["did"] == data.receiver_did), None)
    if not receiver:
        raise HTTPException(status_code=404, detail="Destinataire non trouvé.")

    db["users"][user]["balance_stablecoin"] -= data.amount
    db["users"][receiver]["balance_stablecoin"] += data.amount
    save_db(db)

    return {"message": "Transfert réussi"}
