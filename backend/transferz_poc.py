from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Middleware CORS pour autoriser les requêtes du frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base de données fictive (stockée en JSON)
DB_FILE = "database.json"

def load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"users": {}}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Modèle utilisateur
class User(BaseModel):
    phone: str
    balance_fcfa: float = 0.0
    balance_stablecoin: float = 0.0

# Modèle de transaction
class Transaction(BaseModel):
    sender: str
    receiver: str
    amount: float

# Endpoint pour ajouter un utilisateur
@app.post("/add_user/")
def add_user(user: User):
    db = load_db()
    if user.phone in db["users"]:
        raise HTTPException(status_code=400, detail="Utilisateur déjà existant")
    db["users"][user.phone] = user.dict()
    save_db(db)
    return {"message": "Utilisateur ajouté"}

# Endpoint pour effectuer un dépôt
@app.post("/deposit/")
def deposit(phone: str, amount: float):
    db = load_db()
    if phone not in db["users"]:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    db["users"][phone]["balance_fcfa"] += amount
    save_db(db)
    return {"message": "Dépôt réussi", "new_balance": db["users"][phone]["balance_fcfa"]}

# Endpoint pour convertir en stablecoin
@app.post("/convert/")
def convert(phone: str):
    db = load_db()
    if phone not in db["users"]:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    rate = 0.0016  # Exemple de taux de conversion FCFA -> USDT
    amount_fcfa = db["users"][phone]["balance_fcfa"]
    if amount_fcfa <= 0:
        raise HTTPException(status_code=400, detail="Solde insuffisant")
    db["users"][phone]["balance_stablecoin"] += amount_fcfa * rate
    db["users"][phone]["balance_fcfa"] = 0
    save_db(db)
    return {"message": "Conversion réussie", "new_balance": db["users"][phone]["balance_stablecoin"]}

# Endpoint pour transfert P2P
@app.post("/transfer/")
def transfer(transaction: Transaction):
    db = load_db()
    if transaction.sender not in db["users"] or transaction.receiver not in db["users"]:
        raise HTTPException(status_code=404, detail="Expéditeur ou destinataire non trouvé")
    if db["users"][transaction.sender]["balance_stablecoin"] < transaction.amount:
        raise HTTPException(status_code=400, detail="Solde insuffisant")
    db["users"][transaction.sender]["balance_stablecoin"] -= transaction.amount
    db["users"][transaction.receiver]["balance_stablecoin"] += transaction.amount
    save_db(db)
    return {"message": "Transfert réussi"}

# Endpoint pour retrait
@app.post("/withdraw/")
def withdraw(phone: str, amount: float):
    db = load_db()
    if phone not in db["users"]:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    if db["users"][phone]["balance_stablecoin"] < amount:
        raise HTTPException(status_code=400, detail="Solde insuffisant")
    db["users"][phone]["balance_stablecoin"] -= amount
    save_db(db)
    return {"message": "Retrait enregistré, traitement manuel requis"}
