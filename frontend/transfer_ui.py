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

# ------------------------------------------------------------------
# 1)  FORMULAIRE DE CONNEXION
# ───────────────────────────────────
st.subheader("🔐 Connexion")
username = st.text_input("Nom d'utilisateur")
password = st.text_input("Mot de passe", type="password")

if st.button("Se connecter"):
    resp = requests.post(f"{API_URL}/login/", json={"username": username, "password": password})
    if resp.status_code == 200:
        st.session_state["access_token"] = resp.json()["access_token"]
        st.success("✅ Connexion réussie !")
    else:
        st.error("❌ Identifiants incorrects")
# Interface après connexion
if st.session_state["access_token"]:
    st.sidebar.title("📌 Menu")
    option = st.sidebar.radio(
        "Navigation",
        [
            "Mon DID",
            "Ajouter un Numéro Mobile Money",
            "Dépôt Mobile Money",
            "Transfert P2P",
            "Historique des Transactions",
        ],
    )

    # ---------- PROFIL DID ----------------------------------------
    if option == "Mon DID":
        st.subheader("📌 Identité Décentralisée (DID)")
        if st.session_state.get("did"):
            st.write(f"🎯 **Votre DID** : `{st.session_state['did']}`")
        else:
            st.error("❌ Impossible de récupérer votre DID.")

    # ---------- AJOUT NUMÉRO --------------------------------------
    elif option == "Ajouter un Numéro Mobile Money":
        st.subheader("📲 Ajout d’un Numéro Mobile Money")
        phone_number = st.text_input("Numéro Mobile Money")

        if st.button("Ajouter"):
            headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
            resp = requests.post(
                f"{API_URL}/user/add_phone/",
                headers=headers,
                json={"phone_number": phone_number},
            )
            if resp.status_code == 200:
                st.success("✅ Numéro ajouté avec succès !")
            else:
                st.error(f"❌ Erreur : {resp.json().get('detail', 'Échec de l\'ajout')}")

    # ---------- DÉPÔT MOBILE MONEY --------------------------------
    elif option == "Dépôt Mobile Money":
        st.subheader("📲 Dépôt d'argent")

        # 1️⃣  Logos opérateurs
        operator_icons = {
            "MTN":   "https://htxt.co.za/wp-content/uploads/2022/04/mtn-logo-2022-black-header-1536x864.jpg",
            "Orange":"https://www.annuaireci.com/Content/UserFiles/Ivory%20Coast/Upload/LOGO%20ORANGE.png",
            "Moov":  "https://is1-ssl.mzstatic.com/image/thumb/Purple221/v4/34/85/5e/34855e62-f17e-d858-775f-8c269406e610/AppIcon-0-0-1x_U007emarketing-0-8-0-0-85-220.png/1200x600wa.png",
            "Wave":  "https://play-lh.googleusercontent.com/-Mp3XW7uhwn3KGQxUKGPoc4MbA5ti-3-q23TgoVi9ujBgHWW5n4IySvlG5Exwrxsjw=w240-h480-rw",
        }
        op = st.radio("Choisissez votre opérateur :", list(operator_icons.keys()))
        st.image(operator_icons[op], width=100)

        # 2️⃣  Liste dynamique des numéros enregistrés
        @st.cache_data(ttl=60)
        def get_registered_numbers(token):
            h = {"Authorization": f"Bearer {token}"}
            r = requests.get(f"{API_URL}/user/phones/", headers=h)
            return r.json() if r.status_code == 200 else []

        numbers = get_registered_numbers(st.session_state["access_token"])
        if not numbers:
            st.warning("⚠️ Aucun numéro enregistré. Ajoutez‑en un d’abord.")
            st.stop()

        phone_sel = st.selectbox("📱 Numéro Mobile Money", numbers)

        # 3️⃣  Montant
        amount_fcfa = st.number_input("💰 Montant à déposer (FCFA)", min_value=1.0, step=100.0)

        # 4️⃣  Bouton Dépôt
        if st.button("Déposer"):
            headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
            payload = {"phone_number": phone_sel, "amount": amount_fcfa}

            st.write(f"📡 Requête envoyée : {payload}")  # debug

            resp = requests.post(f"{API_URL}/deposit/", headers=headers, json=payload)
            if resp.status_code == 200:
                st.success(f"✅ Dépôt réussi de {amount_fcfa:.0f} FCFA sur TransferZ !")
            else:
                st.error(f"❌ Erreur : {resp.json().get('detail', 'Échec du dépôt')}")

# ------------------------------------------------------------------




    # --------------------- TRANSFERT P2P ------------------------------
    elif option == "Transfert P2P":
        st.subheader("🔄 Transfert P2P via DID")

        headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
        r = requests.get(f"{API_URL}/list_did_users/", headers=headers)

        if r.status_code != 200:
            st.error("❌ Impossible de récupérer les destinataires.")
            st.stop()

        all_dids = r.json()["users"]
        my_did   = st.session_state.get("did")

        # ⚠️  retire le DID courant
        dest_dids = [d for d in all_dids if d != my_did]

        if not dest_dids:
            st.info("Aucun autre utilisateur disponible pour un transfert.")
            st.stop()

        receiver_did = st.selectbox("📌 Sélectionnez un destinataire", dest_dids)
        amount_usdt  = st.number_input("💰 Montant à transférer (USDT)", min_value=0.01, step=0.50)

        if st.button("Transférer"):
            payload = {"receiver_did": receiver_did, "amount": amount_usdt}
            tx = requests.post(f"{API_URL}/transfer/", headers=headers, json=payload)

            if tx.status_code == 200:
                st.success("✅ Transfert réussi !")
            else:
                st.error(f"❌ Erreur : {tx.json().get('detail', 'Échec du transfert')}")
    # ------------------------------------------------------------------


    elif option == "Historique des Transactions":
        st.subheader("📋 Historique des Transactions")
        headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
        response = requests.get(f"{API_URL}/transactions/", headers=headers)

        if response.status_code == 200:
            transactions = response.json()
            st.write(transactions)
        else:
            st.error("❌ Erreur lors de la récupération de l'historique des transactions.")
            
            
            # ----------------- SECTION ADMIN COMPLETE ------------------
    if st.session_state.get("username") == "admin":
        st.markdown("## 👑 Espace Admin")

        with st.expander("➕ Ajouter un utilisateur"):
            with st.form("admin_add_user_form"):
                new_username = st.text_input("👤 Nom d'utilisateur")
                new_password = st.text_input("🔑 Mot de passe")
                phone = st.text_input("📱 Numéro Mobile Money")
                fcfa = st.number_input("💰 Solde FCFA", min_value=0, step=1000, key="fcfa_admin")
                stable = st.number_input("💱 Solde Stablecoin", min_value=0.0, step=10.0, key="stable_admin")
                if st.form_submit_button("Créer"):
                    payload = {
                        "username": new_username,
                        "password": new_password,
                        "phone_number": phone,
                        "balance_fcfa": fcfa,
                        "balance_stablecoin": stable
                    }
                    r = requests.post(f"{API_URL}/admin/add_user/", json=payload)
                    if r.status_code == 200:
                        st.success(f"✅ Utilisateur ajouté avec DID : {r.json().get('did')}")
                    else:
                        st.error(f"❌ {r.json().get('detail')}")

        with st.expander("🗑 Supprimer un utilisateur"):
            user_to_delete = st.text_input("Nom d'utilisateur à supprimer")
            if st.button("Supprimer"):
                r = requests.post(f"{API_URL}/admin/delete_user/", json={"username": user_to_delete})
                if r.status_code == 200:
                    st.success("✅ Utilisateur supprimé.")
                else:
                    st.error(f"❌ {r.json().get('detail')}")

        with st.expander("🛠 Modifier le solde d’un utilisateur"):
            user_to_edit = st.text_input("Nom d'utilisateur à modifier")
            new_fcfa = st.number_input("Nouveau solde FCFA", min_value=0, step=1000, key="fcfa_update")
            new_stable = st.number_input("Nouveau solde Stablecoin", min_value=0.0, step=10.0, key="stable_update")
            if st.button("Mettre à jour le solde"):
                r = requests.post(f"{API_URL}/admin/update_balance/", json={
                    "username": user_to_edit,
                    "balance_fcfa": new_fcfa,
                    "balance_stablecoin": new_stable
                })
                if r.status_code == 200:
                    st.success("✅ Solde mis à jour.")
                else:
                    st.error(f"❌ {r.json().get('detail')}")

