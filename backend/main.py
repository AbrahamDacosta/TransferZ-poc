from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database file
DB_FILE = "database.json"

def load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"users": {}, "transactions": []}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# User Model
class User(BaseModel):
    phone: int
    balance_fcfa: float = 0.0
    balance_stablecoin: float = 0.0

# Transaction Model
class Transaction(BaseModel):
    sender: str
    receiver: str
    amount: float
    status: str = "pending"

@app.get("/")
def root():
    return {"message": "Transfer Z API is running!"}

@app.post("/add_user/")
def add_user(user: User):
    db = load_db()
    if user.phone in db["users"]:
        raise HTTPException(status_code=400, detail="User already exists")
    db["users"][user.phone] = user.dict()
    save_db(db)
    return {"message": "User added"}

@app.post("/deposit/")
def deposit(phone: str, amount: float):
    db = load_db()
    if phone not in db["users"]:
        raise HTTPException(status_code=404, detail="User not found")
    db["users"][phone]["balance_fcfa"] += amount
    save_db(db)
    return {"message": "Deposit successful", "new_balance": db["users"][phone]["balance_fcfa"]}

@app.post("/convert/")
def convert(phone: str):
    db = load_db()
    if phone not in db["users"]:
        raise HTTPException(status_code=404, detail="User not found")
    rate = 0.0016  # FCFA to USDT conversion rate
    amount_fcfa = db["users"][phone]["balance_fcfa"]
    if amount_fcfa <= 0:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    db["users"][phone]["balance_stablecoin"] += amount_fcfa * rate
    db["users"][phone]["balance_fcfa"] = 0
    save_db(db)
    return {"message": "Conversion successful", "new_balance": db["users"][phone]["balance_stablecoin"]}

@app.post("/transfer/")
def transfer(transaction: Transaction):
    db = load_db()
    if transaction.sender not in db["users"] or transaction.receiver not in db["users"]:
        raise HTTPException(status_code=404, detail="Sender or receiver not found")
    if db["users"][transaction.sender]["balance_stablecoin"] < transaction.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    transaction.status = "pending"
    db["transactions"].append(transaction.dict())
    save_db(db)
    return {"message": "Transaction pending validation"}

@app.get("/transactions/")
def get_transactions():
    db = load_db()
    return db["transactions"]

@app.post("/validate_transaction/")
def validate_transaction(index: int):
    db = load_db()
    if index < 0 or index >= len(db["transactions"]):
        raise HTTPException(status_code=404, detail="Transaction not found")
    transaction = db["transactions"][index]
    if transaction["status"] == "completed":
        return {"message": "Transaction already validated"}
    sender = transaction["sender"]
    receiver = transaction["receiver"]
    amount = transaction["amount"]
    if db["users"][sender]["balance_stablecoin"] >= amount:
        db["users"][sender]["balance_stablecoin"] -= amount
        db["users"][receiver]["balance_stablecoin"] += amount
        transaction["status"] = "completed"
        save_db(db)
        return {"message": "Transaction validated"}
    else:
        transaction["status"] = "failed"
        save_db(db)
        return {"message": "Transaction failed due to insufficient balance"}

@app.post("/withdraw/")
def withdraw(phone: str, amount: float):
    db = load_db()
    if phone not in db["users"]:
        raise HTTPException(status_code=404, detail="User not found")
    if db["users"][phone]["balance_stablecoin"] < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    db["users"][phone]["balance_stablecoin"] -= amount
    save_db(db)
    return {"message": "Withdrawal recorded, manual processing required"}
