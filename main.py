import streamlit as st
import os
import io
import base64
from dotenv import load_dotenv
from groq import Groq
from gtts import gTTS
from PyPDF2 import PdfReader

# --- IMPORTS ---
from auth import *
from patient_data import *
from medical_guide import common_medicine_section
from schemes_finder import schemes_section
from claim_assistant import claim_assistant_section
from icd_cpt_validator import validate_codes
from guardrails_db import init_guardrails_db        # ✅ Dynamic guardrails DB
from guardrails_admin import guardrails_admin_section  # ✅ Admin panel

# --- 1. INITIALIZATION ---
load_dotenv()
init_db()
init_patient_db()
init_guardrails_db()   # ✅ Guardrails DB initialize + seed defaults

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Claim assistant session state
if 'claim_age' not in st.session_state:
    st.session_state['claim_age'] = 30
if 'claim_gender' not in st.session_state:
    st.session_state['claim_gender'] = 'Male'
if 'claim_plan' not in st.session_state:
    st.session_state['claim_plan'] = 'Ayushman Bharat (PMJAY)'
if 'claim_diagnosis' not in st.session_state:
    st.session_state['claim_diagnosis'] = ''
if 'claim_treatment' not in st.session_state:
    st.session_state['claim_treatment'] = ''

# --- 2. CORE AI LOGIC ---

def get_ai_response(user_input, language, patient_info, chat_history):
    history_context = ""
    for msg in chat_history[-5:]:
        history_context += f"{msg['role']}: {msg['content']}\n"
    system_prompt = f"""
    You are 'Gramin Seva AI', an empathetic medical chatbot.
    PATIENT PROFILE: {patient_info}
    RECENT HISTORY: {history_context}
    TASKS: Respond in {language}, end with a follow-up, and be empathetic.
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_input}],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def get_report_explanation(content, language, is_image=False):
    system_prompt = f"""
    You are a Senior Medical Consultant AI. Explain medical reports to rural patients.
    Translate everything into {language}. Use extremely simple language.
    STRUCTURE: 1. LEVEL 1 (Summary), 2. LEVEL 2 (Key Findings), 3. LEVEL 3 (Action Plan).
    """
    try:
        if is_image:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": [
                    {"type": "text", "text": system_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{content}"}}
                ]}],
                model="meta-llama/llama-4-scout-17b-16e-instruct",
            )
        else:
            response = client.chat.completions.create(
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": content}],
                model="llama-3.3-70b-versatile",
            )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- 3. UI SECTIONS ---

def report_analysis_section():
    st.subheader("📄 Smart Medical Report Analyzer (Photo/PDF)")
    st.write("Apni medical report ki photo khinchein ya PDF upload karein.")
    lang = st.selectbox("Samajhne ke liye bhasha chunein:", ["Hindi", "English"])
    uploaded_file = st.file_uploader("Upload Report (PDF, JPG, PNG)", type=["pdf", "jpg", "jpeg", "png"])
    if st.button("Analyze Report ✨"):
        if uploaded_file is not None:
            with st.spinner("AI report ko scan kar raha hai..."):
                file_type = uploaded_file.type
                if "image" in file_type:
                    base64_image = base64.b64encode(uploaded_file.read()).decode('utf-8')
                    analysis = get_report_explanation(base64_image, lang, is_image=True)
                elif "pdf" in file_type:
                    pdf_reader = PdfReader(uploaded_file)
                    text = "".join([page.extract_text() for page in pdf_reader.pages])
                    analysis = get_report_explanation(text, lang, is_image=False)
                st.markdown("### 💡 AI Analysis")
                st.markdown(analysis)
                st.info("⚠️ Note: Ye sirf jankari ke liye hai. Doctor se zaroor milein.")
        else:
            st.warning("Pehle file upload karein.")

def health_ai_section():
    st.subheader("💬 Gramin Seva AI Chatbot")
    with st.sidebar:
        st.divider()
        st.header("📜 Chat History")
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
        for msg in st.session_state.messages:
            role_icon = "👤" if msg["role"] == "user" else "🤖"
            st.write(f"{role_icon} {msg['content'][:20]}...")

    lang = st.selectbox("Language / Bhasha", ["Hindi", "English", "Marathi", "Bengali", "Telugu", "Odia", "Assamese"])
    p_data = fetch_patient_data(st.session_state['username'])
    p_context = f"History: {p_data[7]}, Meds: {p_data[8]}" if p_data else "No profile."

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("AI is thinking..."):
                response = get_ai_response(prompt, lang, p_context, st.session_state.messages)
                st.markdown(response)
                try:
                    audio_text = response[:500] if len(response) > 500 else response
                    tts = gTTS(text=audio_text, lang='hi' if lang != "English" else 'en')
                    tts.save("voice.mp3")
                    st.audio("voice.mp3")
                except:
                    pass
        st.session_state.messages.append({"role": "assistant", "content": response})

def profile_section():
    st.subheader("📋 My Personal Health Profile")
    user = st.session_state['username']
    existing = fetch_patient_data(user)
    with st.form("patient_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", value=existing[1] if existing else "")
            age = st.number_input("Age", 0, 120, value=existing[3] if existing else 25)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        with col2:
            contact = st.text_input("Contact No.", value=existing[2] if existing else "")
            bg = st.selectbox("Blood Group", ["A+", "B+", "O+", "AB+", "A-", "B-", "O-", "AB-"])
        history = st.text_area("Medical History", value=existing[7] if existing else "")
        meds = st.text_area("Current Medications", value=existing[8] if existing else "")
        if st.form_submit_button("Update Profile"):
            save_patient_data((user, name, contact, age, "", gender, bg, history, meds, ""))
            st.success("Profile saved! ✅")

# --- 4. MAIN FLOW ---

def main():
    st.set_page_config(
        page_title="NidanAI — Smart Healthcare",
        page_icon="🏥",
        layout="wide"
    )

    if not st.session_state['logged_in']:
        st.title("🏥 NidanAI — Gramin Seva")
        choice = st.sidebar.selectbox("Action", ["Login", "SignUp", "Forgot Password"])
        if choice == "Login":
            u = st.text_input("Username")
            p = st.text_input("Password", type='password')
            if st.button("Enter"):
                if login_user(u, check_hashes(p, make_hashes(p))):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = u
                    st.rerun()
                else:
                    st.error("Wrong credentials")
        elif choice == "SignUp":
            u = st.text_input("New Username")
            p = st.text_input("New Password", type='password')
            if st.button("Register"):
                try:
                    add_userdata(u, make_hashes(p))
                    st.success("Done!")
                except:
                    st.error("Username already exists!")
        elif choice == "Forgot Password":
            u = st.text_input("Username")
            new_p = st.text_input("New Password", type='password')
            if st.button("Reset Password"):
                update_password(u, make_hashes(new_p))
                st.success("Password reset successfully!")
    else:
        st.sidebar.title(f"👋 Hi, {st.session_state['username']}")
        st.sidebar.markdown("---")

        page = st.sidebar.radio(
            "🧭 Navigation",
            [
                "💬 Chatbot Dashboard",
                "📄 Analyze Reports",
                "💊 Common Medicines",
                "🏛️ Govt Schemes",
                "🏥 Insurance Claim Assistant",
                "⚙️ Guardrails Admin",       # ✅ NEW
                "📋 My Profile"
            ]
        )

        if st.sidebar.button("🚪 Logout"):
            st.session_state['logged_in'] = False
            st.rerun()

        st.sidebar.markdown("---")
        st.sidebar.caption("NidanAI v2.0 — Powered by Groq + Llama")

        if page == "💬 Chatbot Dashboard":
            health_ai_section()
        elif page == "📄 Analyze Reports":
            report_analysis_section()
        elif page == "💊 Common Medicines":
            common_medicine_section()
        elif page == "🏛️ Govt Schemes":
            schemes_section()
        elif page == "🏥 Insurance Claim Assistant":
            claim_assistant_section()
        elif page == "⚙️ Guardrails Admin":
            guardrails_admin_section()     # ✅ NEW
        elif page == "📋 My Profile":
            profile_section()

if __name__ == '__main__':
    main()