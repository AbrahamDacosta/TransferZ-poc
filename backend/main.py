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
from fastapi import Body

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
    try:
        db_path = "/tmp/database.json"
        if not os.path.exists(db_path):
            logging.debug("🚨 `database.json` introuvable, création d’un nouveau fichier.")
            with open(db_path, "w") as f:
                json.dump({"users": {}, "transactions": []}, f, indent=4)

        logging.debug(f"📖 Chargement de `database.json`...")
        with open(db_path, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"❌ Erreur lors du chargement de la base de données : {str(e)}")
        raise



def save_db(data):
    try:
        db_path = "/tmp/database.json"
        logging.debug(f"💾 Sauvegarde des données dans `{db_path}`...")
        with open(db_path, "w") as f:
            json.dump(data, f, indent=4)
        logging.debug("✅ Sauvegarde terminée !")
    except Exception as e:
        logging.error(f"❌ Erreur lors de la sauvegarde : {str(e)}")
        raise


# 🎯 Génération du DID et du compte Blockchain
import binascii

def generate_did():
    try:
        logging.debug("🔧 Génération du DID...")

        # Génération de la clé privée Ethereum
        private_key = keys.PrivateKey(os.urandom(32))
        public_key = private_key.public_key
        address = public_key.to_checksum_address()  # Adresse blockchain

        # Encodage correct de la clé privée
        private_key_hex = binascii.hexlify(private_key.to_bytes()).decode()

        # Génération du DID
        did = f"did:transferz:{uuid.uuid4()}"

        logging.debug(f"✅ DID généré : {did}, Adresse Blockchain : {address}")
        return did, private_key_hex, address

    except Exception as e:
        logging.error(f"🚨 Erreur dans `generate_did()`: {str(e)}")
        raise


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
    expire = datetime.datetime.utcnow() + datetime.timedelta(days=30)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
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

# 🧾 Schéma d'entrée pour ajouter un utilisateur
class AdminUser(BaseModel):
    username: str
    password: str
    phone_number: str
    balance_fcfa: int = 0
    balance_stablecoin: float = 0.0

# 🛠 Route d'ajout manuel (admin)
@app.post("/admin/add_user/")
def admin_add_user(user: AdminUser):
    db = load_db()

    if user.username in db["users"]:
        raise HTTPException(status_code=400, detail="Utilisateur déjà existant.")

    # Simuler les données blockchain/DID
    uid = str(uuid4())
    did = f"did:transferz:{uid}"
    priv_key = f"privkey_{uid[:6]}"
    address = f"0x{uid[:6]}"
    hashed_pw = f"hashed_{user.password}"  # À remplacer si passlib est utilisé

    db["users"][user.username] = {
        "password": hashed_pw,
        "did": did,
        "private_key": priv_key,
        "blockchain_address": address,
        "phone_numbers": [user.phone_number],
        "balance_fcfa": user.balance_fcfa,
        "balance_stablecoin": user.balance_stablecoin
    }

    save_db(db)

    return {"message": "✅ Utilisateur ajouté", "did": did}


from fastapi import Body

@app.post("/admin/delete_user/")
def delete_user_admin(username: str = Body(...)):
    db = load_db()
    if username not in db["users"]:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    del db["users"][username]
    save_db(db)
    return {"message": "Utilisateur supprimé"}

@app.post("/admin/update_balance/")
def update_balance_admin(
    username: str = Body(...),
    balance_fcfa: int = Body(...),
    balance_stablecoin: float = Body(...)
):
    db = load_db()
    if username not in db["users"]:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    db["users"][username]["balance_fcfa"] = balance_fcfa
    db["users"][username]["balance_stablecoin"] = balance_stablecoin
    save_db(db)
    return {"message": "Solde mis à jour"}

@app.get("/user/phones/")
def get_user_phones(user: str = Depends(get_current_user)):
    db = load_db()
    
    if user not in db["users"]:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")
    
    logging.debug(f"📞 Numéros enregistrés pour {user} : {db['users'][user]['phone_numbers']}")
    
    return db["users"][user]["phone_numbers"]


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
def deposit_funds(data: dict, user: str = Depends(get_current_user)):
    db = load_db()

    logging.debug(f"📞 Numéros enregistrés pour {user} : {db['users'][user]['phone_numbers']}")
    logging.debug(f"📡 Données reçues : {data}")

    if user not in db["users"]:
        raise HTTPException(status_code=400, detail="Utilisateur non trouvé.")

    if "phone_number" not in data or "amount" not in data:
        raise HTTPException(status_code=400, detail="Données manquantes : phone_number ou amount.")

    if data["phone_number"] not in db["users"][user]["phone_numbers"]:
        raise HTTPException(status_code=400, detail=f"Numéro Mobile Money non enregistré. Numéros enregistrés : {db['users'][user]['phone_numbers']}")

    db["users"][user]["balance_fcfa"] += data["amount"]
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
