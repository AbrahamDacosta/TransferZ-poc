import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"  # Assurez-vous que FastAPI tourne sur cette adresse

st.set_page_config(page_title="Transfer Z", page_icon="💰", layout="wide")
st.title("💰 Transfer Z - Plateforme de Transfert")

menu = ["🏠 Accueil", "🆕 Inscription", "💰 Dépôt", "🔄 Conversion", "🔗 Transfert P2P", "💸 Retrait", "✅ Validation des Transactions"]
choice = st.sidebar.selectbox("Navigation", menu)

if choice == "🏠 Accueil":
    st.subheader("Bienvenue sur Transfer Z")
    st.write("🚀 Gérez vos transactions en toute simplicité !")
    st.write("📌 Déposez, convertissez en stablecoins, transférez et retirez vos fonds rapidement.")
    st.image("https://source.unsplash.com/800x400/?finance,money", use_container_width=True)

elif choice == "🆕 Inscription":
    st.subheader("🆕 Inscription d'un nouvel utilisateur")
    phone = st.text_input("📞 Numéro de téléphone")
    if st.button("✅ S'inscrire"):
        response = requests.post(f"{API_URL}/add_user/", json={"phone": phone})
        if response.status_code == 200:
            st.success(response.json().get("message", "Utilisateur ajouté avec succès!"))
        else:
            try:
                data = response.json()
                st.error(f"⚠️ Erreur : {data.get('detail', 'Impossible d\'ajouter l\'utilisateur')} ")
            except requests.exceptions.JSONDecodeError:
                st.write("🔍 API Response:", response.status_code, response.text)
                st.error(f"❌ Erreur: La réponse de l'API est invalide : {response.text}")

elif choice == "💰 Dépôt":
    st.subheader("💰 Effectuer un dépôt")
    st.write("Déposez de l'argent sur votre compte pour pouvoir l'utiliser sur Transfer Z.")
    phone = st.text_input("📞 Numéro de téléphone")
    amount = st.number_input("💵 Montant en FCFA", min_value=1.0, step=100.0)
    if st.button("💰 Déposer"):
        response = requests.post(f"{API_URL}/deposit/", params={"phone": phone, "amount": amount})
        if response.status_code == 200:
            st.success(response.json().get("message", "Dépôt réussi !"))
        else:
            try:
                data = response.json()
                st.error(f"⚠️ Erreur : {data.get('detail', 'Impossible d\'ajouter l\'utilisateur')} ")
            except requests.exceptions.JSONDecodeError:
                st.write("🔍 API Response:", response.status_code, response.text)
                st.error(f"❌ Erreur: La réponse de l'API est invalide : {response.text}")

elif choice == "🔄 Conversion":
    st.subheader("🔄 Convertir FCFA en stablecoin")
    st.write("Transformez votre solde en monnaie locale en stablecoins pour des transactions sécurisées.")
    phone = st.text_input("📞 Numéro de téléphone")
    if st.button("🔄 Convertir"):
        response = requests.post(f"{API_URL}/convert/", params={"phone": phone})
        if response.status_code == 200:
            st.success(response.json().get("message", "Conversion réussie !"))
        else:
            try:
                data = response.json()
                st.error(f"⚠️ Erreur : {data.get('detail', 'Impossible d\'ajouter l\'utilisateur')} ")
            except requests.exceptions.JSONDecodeError:
                st.write("🔍 API Response:", response.status_code, response.text)
                st.error(f"❌ Erreur: La réponse de l'API est invalide : {response.text}")

elif choice == "🔗 Transfert P2P":
    st.subheader("🔗 Transfert de stablecoin entre utilisateurs")
    st.write("Envoyez des stablecoins instantanément à un autre utilisateur Transfer Z.")
    sender = st.text_input("📞 Numéro de l'expéditeur")
    receiver = st.text_input("📞 Numéro du destinataire")
    amount = st.number_input("💰 Montant en stablecoin", min_value=0.01, step=0.01)
    if st.button("📤 Envoyer"):
        response = requests.post(f"{API_URL}/transfer/", json={"sender": sender, "receiver": receiver, "amount": amount})
        if response.status_code == 200:
            st.success(response.json().get("message", "Transfert en attente de validation"))
        else:
            try:
                data = response.json()
                st.error(f"⚠️ Erreur : {data.get('detail', 'Impossible d\'ajouter l\'utilisateur')} ")
            except requests.exceptions.JSONDecodeError:
                st.write("🔍 API Response:", response.status_code, response.text)
                st.error(f"❌ Erreur: La réponse de l'API est invalide : {response.text}")

elif choice == "💸 Retrait":
    st.subheader("💸 Effectuer un retrait")
    st.write("Convertissez vos stablecoins en monnaie électronique pour les retirer sur Mobile Money.")
    phone = st.text_input("📞 Numéro de téléphone")
    amount = st.number_input("💵 Montant en stablecoin", min_value=0.01, step=0.01)
    if st.button("💸 Retirer"):
        response = requests.post(f"{API_URL}/withdraw/", params={"phone": phone, "amount": amount})
        if response.status_code == 200:
            st.success(response.json().get("message", "Retrait enregistré, traitement en cours."))
        else:
            try:
                data = response.json()
                st.error(f"⚠️ Erreur : {data.get('detail', 'Impossible d\'ajouter l\'utilisateur')} ")
            except requests.exceptions.JSONDecodeError:
                st.write("🔍 API Response:", response.status_code, response.text)
                st.error(f"❌ Erreur: La réponse de l'API est invalide : {response.text}")

elif choice == "✅ Validation des Transactions":
    st.subheader("✅ Validation des Transactions en Attente")
    st.write("📌 Liste des transactions en attente de validation.")
    response = requests.get(f"{API_URL}/transactions/")
    transactions = response.json()
    for i, transaction in enumerate(transactions):
        with st.expander(f"🔄 Transaction {i+1}: {transaction['sender']} → {transaction['receiver']} ({transaction['amount']} USDT)"):
            st.write(f"Statut: {transaction['status']}")
            if transaction["status"] == "pending":
                if st.button(f"✅ Valider Transaction {i+1}"):
                    validate_response = requests.post(f"{API_URL}/validate_transaction/", params={"index": i})
                    st.success(validate_response.json().get("message", "Transaction validée."))
