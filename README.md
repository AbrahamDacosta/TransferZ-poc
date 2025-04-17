# 🚀 TransferZ - Plateforme de Paiement Décentralisée (POC)

TransferZ est une plateforme de preuve de concept (POC) illustrant un système de paiement décentralisé basé sur les identités numériques (DIDs) et les stablecoins, permettant des transferts d'argent entre utilisateurs, même à l'international.

---

## ✅ Fonctionnalités

### Utilisateur
- 🔐 Authentification (login)
- 👤 Création de compte avec génération automatique de DID, clé privée, et adresse blockchain
- 📱 Ajout de numéros Mobile Money
- 💰 Dépôt d’argent via Mobile Money (simulé)
- 💱 Conversion en stablecoin
- 🔄 Transfert P2P vers d’autres utilisateurs (DID to DID)
- 💸 Retrait en monnaie électronique
- 📋 Consultation du solde et historique des transactions

### Admin
- 👑 Ajouter un utilisateur (via Streamlit UI)
- 🗑 Supprimer un utilisateur
- 🛠 Modifier le solde d’un utilisateur (FCFA / stablecoin)

---

## 🏗️ Architecture

- `backend/`: API FastAPI hébergée sur Render
- `frontend/`: Interface Streamlit hébergée sur Streamlit Cloud
- `database.json`: stocke les utilisateurs, soldes et transactions (simule une base de données)

---

## 🚀 Déploiement

### 1. Backend (Render)

#### 🔧 Fichiers nécessaires
- `backend/main.py`
- `backend/database.json`
- `backend/requirements.txt`

#### 📄 Exemple de `render.yaml`
```yaml
services:
  - type: web
    name: transferz-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port 10000
    rootDir: backend
```

#### 🔗 URL attendue
`https://transferz-api.onrender.com`

---

### 2. Frontend (Streamlit Cloud)

#### 🔧 Fichiers nécessaires
- `frontend/transfer_ui.py`
- `frontend/requirements.txt`

#### 📄 Exemple `requirements.txt`
```txt
streamlit
requests
```

Déployez sur [https://streamlit.io/cloud](https://streamlit.io/cloud)

---

## 🧪 Tests & Simulation

### 🔐 Connexion :
- Identifiants test : `admin / adminpass`

### 🛠 Ajouter un utilisateur :
- Utiliser l’espace Admin
- Ou appeler l’API POST `/admin/add_user/`

---

## 📁 Arborescence
```bash
poc-transferZ/
├── backend/
│   ├── main.py
│   ├── database.json
│   └── requirements.txt
├── frontend/
│   ├── transfer_ui.py
│   └── requirements.txt
├── scripts/
│   └── add_user.py (optionnel pour tests locaux)
├── render.yaml
└── README.md
```

---

## 🔐 À venir (Roadmap)
- Intégration API Mobile Money réelles (Orange, MTN, Wave)
- Blockchain réelle (Celo, Ethereum, Polygon)
- Authentification DID + Verifiable Credentials (VC)
- Intégration d’un tableau de bord analytique (ex. : Power BI)

---

## 👨‍💻 Auteur
**Abraham Dacosta** – [LinkedIn](https://www.linkedin.com/in/therealabrahamdacosta/)

---

## 📄 Licence
MIT – Free to use, improve, and extend.

