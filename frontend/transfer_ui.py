import os
import json
import jwt
import datetime
import requests
import streamlit as st
from pydantic import BaseModel

API_URL = "https://transferz-api.onrender.com"

# Personnalisation de l'accueil
st.markdown(
    """
    <style>
        .main-title {
            font-size: 36px;
            font-weight: bold;
            color: #4CAF50;
            text-align: center;
        }
        .sub-title {
            font-size: 20px;
            color: #333;
            text-align: center;
        }
        .login-container {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<div class='main-title'>🚀 TransferZ - La Solution de Paiement Innovante</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Simplifiez vos transactions avec notre plateforme sécurisée</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Gestion des sessions utilisateur
if "access_token" not in st.session_state:
    st.session_state["access_token"] = None

# Formulaire de connexion
st.markdown("<div class='login-container'>", unsafe_allow_html=True)
st.subheader("🔐 Connexion")
username = st.text_input("Nom d'utilisateur")
password = st.text_input("Mot de passe", type="password")
if st.button("Se connecter"):
    response = requests.post(f"{API_URL}/login/", json={"username": username, "password": password})
    if response.status_code == 200:
        data = response.json()
        st.session_state["access_token"] = data["access_token"]
        st.success("✅ Connexion réussie !")
    else:
        st.error("❌ Identifiants incorrects")
st.markdown("</div>", unsafe_allow_html=True)

# Si l'utilisateur est connecté, afficher les fonctionnalités
if st.session_state["access_token"]:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.sidebar.title("📌 Menu")
    option = st.sidebar.radio("Navigation", ["Ajouter un utilisateur", "Dépôt Mobile Money", "Conversion en Stablecoin", "Transfert P2P", "Retrait", "Historique des Transactions", "Vérification du Solde"])
    
    if option == "Ajouter un utilisateur":
        st.subheader("👤 Ajouter un utilisateur")
        new_username = st.text_input("Nom du nouvel utilisateur")
        new_password = st.text_input("Mot de passe du nouvel utilisateur", type="password")
        if st.button("Créer l'utilisateur"):
            headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
            response = requests.post(f"{API_URL}/register/", headers=headers, json={"username": new_username, "password": new_password})
            if response.status_code == 200:
                st.success("✅ Utilisateur ajouté avec succès !")
            else:
                st.error("❌ Erreur lors de l'ajout de l'utilisateur")
    
    elif option == "Dépôt Mobile Money":
        st.subheader("📲 Dépôt d'argent via Mobile Money")
        amount_mobile = st.number_input("Montant à déposer", min_value=1.0)
        if st.button("Déposer via Mobile Money"):
            headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
            response = requests.post(f"{API_URL}/deposit_mobile_money/", headers=headers, json={"amount": amount_mobile})
            if response.status_code == 200:
                st.success("✅ Dépôt Mobile Money réussi !")
            else:
                st.error("❌ Erreur lors du dépôt Mobile Money")
    
    elif option == "Conversion en Stablecoin":
        st.subheader("💱 Conversion en Stablecoin")
        convert_amount = st.number_input("Montant à convertir", min_value=1.0)
        if st.button("Convertir en Stablecoin"):
            headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
            response = requests.post(f"{API_URL}/convert_stablecoin/", headers=headers, json={"amount": convert_amount})
            if response.status_code == 200:
                st.success("✅ Conversion réussie !")
            else:
                st.error("❌ Erreur lors de la conversion")

    
    elif option == "Transfert P2P":
        st.subheader("🔄 Transfert P2P")
        receiver = st.text_input("Nom du destinataire")
        amount_transfer = st.number_input("Montant à transférer", min_value=1.0)
        if st.button("Transférer"):
            headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
            response = requests.post(f"{API_URL}/transfer/", headers=headers, json={"receiver": receiver, "amount": amount_transfer})
            if response.status_code == 200:
                st.success("✅ Transfert réussi !")
            else:
                st.error("❌ Erreur lors du transfert")
    
    elif option == "Retrait":
        st.subheader("💸 Retrait en monnaie électronique")
        withdraw_amount = st.number_input("Montant à retirer", min_value=1.0)
        if st.button("Retirer en monnaie électronique"):
            headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
            response = requests.post(f"{API_URL}/withdraw/", headers=headers, json={"amount": withdraw_amount})
            if response.status_code == 200:
                st.success("✅ Retrait réussi !")
            else:
                st.error("❌ Erreur lors du retrait")
    
    elif option == "Historique des Transactions":
        st.subheader("📋 Historique des Transactions")
        headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
        response = requests.get(f"{API_URL}/transactions/", headers=headers)
        if response.status_code == 200:
            transactions = response.json()
            st.write(transactions)
        else:
            st.error("❌ Erreur lors de la récupération de l'historique")
    
    elif option == "Vérification du Solde":
        st.subheader("💳 Solde Disponible")
        headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
        response = requests.get(f"{API_URL}/balance/", headers=headers)
        if response.status_code == 200:
            balance = response.json()
            st.write(f"💰 Solde FCFA : {balance['balance_fcfa']} \n💱 Solde Stablecoin : {balance['balance_stablecoin']}")
        else:
            st.error("❌ Erreur lors de la récupération du solde")
