import requests
import streamlit as st

# 🎨 Personnalisation de l'interface
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
            max-width: 400px;
            margin: auto;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<div class='main-title'>🚀 TransferZ - Paiement Blockchain</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Simplifiez vos transactions avec une solution sécurisée</div>", unsafe_allow_html=True)

# 📌 Configuration dynamique de l'API Backend
if "api_url" not in st.session_state:
    st.session_state["api_url"] = st.text_input("🔗 URL de l'API Backend", "https://transferz-api.onrender.com")

API_URL = st.session_state["api_url"]

# 📌 Gestion des sessions utilisateur
if "access_token" not in st.session_state:
    st.session_state["access_token"] = None

# 📌 Formulaire de connexion utilisateur
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

# 📌 Formulaire d'inscription utilisateur
st.markdown("<div class='login-container'>", unsafe_allow_html=True)
st.subheader("🆕 Inscription")
new_username = st.text_input("Nom d'utilisateur (Inscription)")
new_password = st.text_input("Mot de passe (Inscription)", type="password")

st.markdown("📲 **Ajoutez vos numéros Mobile Money (max 3)**")
phone_numbers = []
for i in range(3):
    phone = st.text_input(f"Numéro Mobile Money {i+1} (optionnel)")
    if phone:
        phone_numbers.append(phone)

if st.button("S'inscrire"):
    response = requests.post(f"{API_URL}/register/", json={
        "username": new_username,
        "password": new_password,
        "phone_numbers": phone_numbers
    })
    if response.status_code == 200:
        st.success("✅ Inscription réussie !")
    else:
        st.error(f"❌ Erreur : {response.json().get('detail', 'Inscription impossible')}")
st.markdown("</div>", unsafe_allow_html=True)

# 📌 Interface après connexion
if st.session_state["access_token"]:
    st.sidebar.title("📌 Menu")
    option = st.sidebar.radio("Navigation", [
        "Profil", "Dépôt Mobile Money", "Conversion en Stablecoin",
        "Transfert P2P", "Retrait", "Historique des Transactions"
    ])
    
    if option == "Profil":
        st.subheader("📱 Mes numéros Mobile Money")
        headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
        response = requests.get(f"{API_URL}/user/phones/", headers=headers)
        if response.status_code == 200:
            phone_numbers = response.json()["phone_numbers"]
            st.write(f"📲 **Numéros liés à votre compte** : {', '.join(phone_numbers)}")
        else:
            st.error("❌ Impossible de récupérer les numéros Mobile Money.")

    elif option == "Dépôt Mobile Money":
        st.subheader("📲 Dépôt d'argent")
        headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
        response = requests.get(f"{API_URL}/user/phones/", headers=headers)
        if response.status_code == 200:
            phone_numbers = response.json()["phone_numbers"]
            selected_phone = st.selectbox("📱 Sélectionnez un numéro Mobile Money", phone_numbers)
            amount_deposit = st.number_input("💰 Montant à déposer (FCFA)", min_value=1.0)
            if st.button("Déposer"):
                response = requests.post(f"{API_URL}/deposit/", headers=headers, json={
                    "phone_number": selected_phone,
                    "amount": amount_deposit
                })
                if response.status_code == 200:
                    st.success(f"✅ Dépôt réussi !")
                else:
                    st.error(f"❌ Erreur : {response.json().get('detail', 'Échec du dépôt')}")
        else:
            st.error("❌ Impossible de récupérer les numéros Mobile Money.")

    elif option == "Conversion en Stablecoin":
        st.subheader("💱 Conversion FCFA → Stablecoin")
        amount_convert = st.number_input("💰 Montant à convertir (FCFA)", min_value=1.0)
        if st.button("Convertir"):
            response = requests.post(f"{API_URL}/convert_stablecoin/", headers=headers, json={"amount": amount_convert})
            if response.status_code == 200:
                st.success("✅ Conversion réussie !")
            else:
                st.error(f"❌ Erreur : {response.json().get('detail', 'Échec de la conversion')}")

    elif option == "Transfert P2P":
        st.subheader("🔄 Transfert P2P")
        receiver = st.text_input("👤 Nom du destinataire")
        amount_transfer = st.number_input("💰 Montant à transférer (USDT)", min_value=1.0)
        if st.button("Transférer"):
            response = requests.post(f"{API_URL}/transfer/", headers=headers, json={
                "receiver": receiver,
                "amount": amount_transfer
            })
            if response.status_code == 200:
                st.success("✅ Transfert réussi !")
            else:
                st.error(f"❌ Erreur : {response.json().get('detail', 'Échec du transfert')}")

    elif option == "Retrait":
        st.subheader("💸 Retrait Mobile Money")
        response = requests.get(f"{API_URL}/user/phones/", headers=headers)
        if response.status_code == 200:
            phone_numbers = response.json()["phone_numbers"]
            selected_phone = st.selectbox("📱 Sélectionnez un numéro Mobile Money", phone_numbers)
            amount_withdraw = st.number_input("💰 Montant à retirer (USDT)", min_value=1.0)
            if st.button("Retirer"):
                response = requests.post(f"{API_URL}/withdraw/", headers=headers, json={
                    "phone_number": selected_phone,
                    "amount": amount_withdraw
                })
                if response.status_code == 200:
                    st.success("✅ Retrait réussi !")
                else:
                    st.error(f"❌ Erreur : {response.json().get('detail', 'Échec du retrait')}")
        else:
            st.error("❌ Impossible de récupérer les numéros Mobile Money.")
