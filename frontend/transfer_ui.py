import requests
import streamlit as st

API_URL = "https://transferz-poc.onrender.com"

# 🎨 UI Personnalisée
st.markdown(
    """
    <style>
        .main-title { font-size: 36px; font-weight: bold; color: #4CAF50; text-align: center; }
        .sub-title { font-size: 20px; color: #333; text-align: center; }
        .login-container { background-color: #f9f9f9; padding: 20px; border-radius: 10px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); max-width: 400px; margin: auto; }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<div class='main-title'>🚀 TransferZ - Paiement Blockchain</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Transférez et gérez votre argent via DID</div>", unsafe_allow_html=True)

# 📌 Gestion des sessions utilisateur
if "access_token" not in st.session_state:
    st.session_state["access_token"] = None

if "did" not in st.session_state:
    st.session_state["did"] = None

# 📌 Formulaire d'inscription
st.subheader("🆕 Inscription")
new_username = st.text_input("Nom d'utilisateur (Inscription)")
new_password = st.text_input("Mot de passe (Inscription)", type="password")

if st.button("S'inscrire"):
    response = requests.post(f"{API_URL}/register/", json={"username": new_username, "password": new_password})
    if response.status_code == 200:
        data = response.json()
        st.success(f"✅ Inscription réussie ! DID : {data['did']}")
        st.session_state["did"] = data["did"]
    else:
        st.error(f"❌ Erreur : {response.json().get('detail', 'Inscription impossible')}")

# 📌 Formulaire de connexion utilisateur
st.subheader("🔐 Connexion")
username = st.text_input("Nom d'utilisateur (Connexion)")
password = st.text_input("Mot de passe (Connexion)", type="password")
if st.button("Se connecter"):
    response = requests.post(f"{API_URL}/login/", json={"username": username, "password": password})
    if response.status_code == 200:
        data = response.json()
        st.session_state["access_token"] = data["access_token"]
        st.success("✅ Connexion réussie !")
    else:
        st.error("❌ Identifiants incorrects")

# 📌 Interface après connexion
if st.session_state["access_token"]:
    st.sidebar.title("📌 Menu")
    option = st.sidebar.radio("Navigation", [
        "Mon DID", "Ajouter un Numéro Mobile Money", "Dépôt Mobile Money",
        "Transfert P2P", "Historique des Transactions"
    ])

    if option == "Mon DID":
        st.subheader("📌 Identité Décentralisée (DID)")
        if st.session_state["did"]:
            st.write(f"🎯 **Votre DID** : `{st.session_state['did']}`")
        else:
            st.error("❌ Impossible de récupérer votre DID.")

    elif option == "Ajouter un Numéro Mobile Money":
        st.subheader("📲 Ajout d’un Numéro Mobile Money")
        phone_number = st.text_input("Numéro Mobile Money")

        if st.button("Ajouter"):
            headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
            response = requests.post(f"{API_URL}/user/add_phone/", headers=headers, json={"phone_number": phone_number})
            if response.status_code == 200:
                st.success("✅ Numéro ajouté avec succès !")
            else:
                st.error(f"❌ Erreur : {response.json().get("detail", "Échec de l'ajout")}")

    elif option == "Dépôt Mobile Money":
        st.subheader("📲 Dépôt d'argent")

        # Interface visuelle pour choisir l'opérateur
        operator_icons = {
            "MTN": "https://htxt.co.za/wp-content/uploads/2022/04/mtn-logo-2022-black-header-1536x864.jpg",
            "Orange": "https://www.annuaireci.com/Content/UserFiles/Ivory%20Coast/Upload/LOGO%20ORANGE.png",
            "Moov": "https://is1-ssl.mzstatic.com/image/thumb/Purple221/v4/34/85/5e/34855e62-f17e-d858-775f-8c269406e610/AppIcon-0-0-1x_U007emarketing-0-8-0-0-85-220.png/1200x600wa.png",
            "Wave": "https://play-lh.googleusercontent.com/-Mp3XW7uhwn3KGQxUKGPoc4MbA5ti-3-q23TgoVi9ujBgHWW5n4IySvlG5Exwrxsjw=w240-h480-rw"
        }

        selected_operator = st.radio("Choisissez votre opérateur :", list(operator_icons.keys()),
                                     format_func=lambda op: f"🟠 {op}")

        st.image(operator_icons[selected_operator], width=100)

        amount_deposit = st.number_input("💰 Montant à déposer (FCFA)", min_value=1.0)
        # Charger les numéros de téléphone enregistrés depuis l'API
    def get_registered_numbers():
        headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
        response = requests.get(f"{API_URL}/user/phones/", headers=headers)

        if response.status_code == 200:
            return response.json()  # Retourne la liste des numéros enregistrés
        else:
            st.error(f"❌ Impossible de récupérer les numéros Mobile Money.")
            return []

    # Récupération dynamique des numéros Mobile Money liés au compte utilisateur
    registered_numbers = get_registered_numbers()

    if st.button("Déposer"):
        # Vérifier si des numéros existent
        if not registered_numbers:
            st.error("❌ Aucun numéro Mobile Money enregistré ! Ajoutez un numéro avant de déposer.")
        else:
            selected_phone_number = st.selectbox("Sélectionnez votre numéro Mobile Money", registered_numbers)
            amount_deposit = st.number_input("Montant à déposer", min_value=1.0)

            st.write(f"📡 Envoi de la requête avec numéro réel : {selected_phone_number}")

            headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
            response = requests.post(f"{API_URL}/deposit/", headers=headers, json={
                "phone_number": selected_phone_number,
                "amount": amount_deposit
            })

            if response.status_code == 200:
                st.success(f"✅ Dépôt réussi de {amount_deposit} FCFA sur TransferZ !")
            else:
                st.error(f"❌ Erreur : {response.json().get('detail', 'Échec du dépôt')}")



    elif option == "Transfert P2P":
        st.subheader("🔄 Transfert P2P via DID")
        headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
        response = requests.get(f"{API_URL}/list_did_users/", headers=headers)

        if response.status_code == 200:
            did_users = response.json()["users"]
            selected_did = st.selectbox("📌 Sélectionnez un destinataire", did_users)
            amount_transfer = st.number_input("💰 Montant à transférer (USDT)", min_value=1.0)

            if st.button("Transférer"):
                response = requests.post(f"{API_URL}/transfer/", headers=headers, json={
                    "receiver_did": selected_did,
                    "amount": amount_transfer
                })
                if response.status_code == 200:
                    st.success("✅ Transfert réussi !")
                else:
                    st.error(f"❌ Erreur : {response.json().get('detail', 'Échec du transfert')}")
        else:
            st.error("❌ Impossible de récupérer les utilisateurs DID.")

    elif option == "Historique des Transactions":
        st.subheader("📋 Historique des Transactions")
        headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
        response = requests.get(f"{API_URL}/transactions/", headers=headers)

        if response.status_code == 200:
            transactions = response.json()
            st.write(transactions)
        else:
            st.error("❌ Erreur lors de la récupération de l'historique des transactions.")
