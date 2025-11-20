import streamlit as st
import os
import json
from google import genai
from dotenv import load_dotenv

# --- 1. CHARGEMENT DE LA CONFIGURATION ET DE L'API KEY ---

# Charger les variables d'environnement (API Key)
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Charger les configurations des Riads depuis le fichier JSON
try:
    with open('riads_config.json', 'r', encoding='utf-8') as f:
        RIADS_CONFIG = json.load(f)
except FileNotFoundError:
    st.error("Erreur : Le fichier 'riads_config.json' est introuvable.")
    st.stop()
except json.JSONDecodeError:
    st.error("Erreur : Le fichier 'riads_config.json' est mal formaté.")
    st.stop()

# --- 2. DÉTECTION DU RIAD CLIENT (Via l'URL) ---

# Lire le paramètre 'riad_id' depuis l'URL (ex: ?riad_id=othmane_riad)
# Si aucun ID n'est trouvé, utiliser 'othmane_riad' comme ID par défaut pour la démo
riad_id = st.query_params.get('riad_id', ['othmane_riad'])[0]

# Vérifier si cet ID existe dans notre configuration
if riad_id not in RIADS_CONFIG:
    st.error(f"Erreur : L'ID de Riad '{riad_id}' n'existe pas dans la base de données.")
    st.stop()

# Charger les données spécifiques au Riad
RIAD_DATA = RIADS_CONFIG[riad_id]
RIAD_NAME = RIAD_DATA["name"]
RIAD_WHATSAPP = RIAD_DATA["whatsapp"]
RIAD_CITY = RIAD_DATA["city"]


# --- 3. INSTRUCTION SYSTÈME DYNAMIQUE (LE PROMPT) ---

# Utiliser les données chargées pour construire le prompt
system_instruction = f"""
You are 'Aisha', the intelligent virtual concierge for '{RIAD_NAME}' in {RIAD_CITY}.
Your Goal: Help guests enjoy their stay and encourage them to book tours.
Tone: Warm, welcoming, Moroccan hospitality (use emojis like 🍵, 🐪, ✨).

Languages: 
- Detect the user's language automatically.
- English/French/Spanish: Answer in that language.
- Arabic (Fusha): Answer in polite Modern Standard Arabic.
- Moroccan Darija: Answer in polite Darija. 
  **IMPORTANT RULE FOR DARIJA:** - Do NOT assume the user's gender. 
  - Use neutral phrases like 'Merhba bik' (Welcome).

Knowledge Base:
- Location: {RIAD_DATA['location']}
- Breakfast: {RIAD_DATA['breakfast_info']}
- Wifi: {RIAD_DATA['wifi_info']}
- Services: The Riad offers tours and services. Specifically: {RIAD_DATA['tours_info']}
- Booking Rule: If they want to book a room or tour, say: 'I have notified the manager. Please send your details to our WhatsApp: {RIAD_WHATSAPP}'
"""

# --- 4. CONFIGURATION DE L'APPLICATION STREAMLIT ---

# Initialiser le client Gemini
try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error("Erreur de connexion à l'API Gemini. Vérifiez votre GEMINI_API_KEY dans Streamlit Secrets.")
    st.stop()

st.set_page_config(page_title=f"Aisha - Concierge IA pour {RIAD_NAME}", layout="centered")
st.title(f"Welcome to {RIAD_NAME} 🐪")
st.caption(f"Votre concierge virtuelle 24/7. Envoyez un message !")

# Initialiser la session de chat
if "chat_session" not in st.session_state:
    st.session_state["chat_session"] = client.chats.create(
        model="gemini-2.5-flash",
        config={"system_instruction": system_instruction}
    )

# Afficher l'historique de la conversation
for message in st.session_state.chat_session.get_history():
    role = "assistant" if message.role == "model" else message.role
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# Champ de saisie pour l'utilisateur
if user_prompt := st.chat_input("Posez votre question (en Darija, Français, Anglais...)"):
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Envoyer le message à l'IA
    with st.chat_message("assistant"):
        with st.spinner("Aisha réfléchit..."):
            try:
                response = st.session_state.chat_session.send_message(user_prompt)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Une erreur s'est produite : {e}")

