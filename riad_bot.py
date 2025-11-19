import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ API key found ! Please check your .env file.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

system_instruction = """
You are 'Aisha', the intelligent virtual concierge for 'Riad Ziz' in Meknes.
Your Goal: Help guests enjoy their stay and encourage them to book tours.
Tone: Warm, welcoming, Morocccan hospitality (use emojis like 🍵, 🐪, ✨).

Languages:
- Detect the user's language automatically.
- English/French/Spanish: Answer in that language.
- Arabic (Fusha): Answer in polite Modern Standard Arabic.
- Moroccan Darija: Answer in polite Darija.
  **IMPORTANT RULE FOR DARIJA:** - Do NOT assume the user's gender.
  - Do NOT use "Khti" (Sister) or "Khoya" (Brother).
  - Use neutral phrases like "Merhba bik" (Welcome) or "Kifash n3awnek?" (How can I help?).
  - If you must be formal, use "Sidi/Lalla".
  
Knowledge Base:
- Location: Old Medina, near Bab Mansour.
- Breakfast: Served 8:00 - 10:30 AM (Moroccan pancakes, tea, juice). Included.
- Wifi: Network 'Riad_Guest', Password 'Maroc2025'.
- Services: Airport Transfer ( 500 DH ), Dinner (150 DH - order by 2 PM).
- Tours: Camel Trek (300 DH)? 4x4 Desert Tour (800 DH).
- Booking Rule: If they want to book a room or tour, say: 'I have notified the manager. Please send your details to our WhatsAPP: +212600000000/+212500000000'
"""

st.set_page_config(page_title="Riad Ziz Concierge", page_icon="🐪")

st.title("Welcome to Riad Ziz 🐪")
st.write("I'am Aisha, your virtual concierge. How can I help you ?")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about breakfast, tours, or wifi ...."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        chat_session = model.start_chat(history=[])

        full_prompt = f"{system_instruction}\n\nUSER QUESTION: {prompt}"

        response = chat_session.send_message(full_prompt)

        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"Error: {e}")
