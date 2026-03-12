import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
# Initialize Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_medicine_suggestion(problem, language):
    """
    Common OTC recommendations aur care instructions.
    """
    system_prompt = f"""
    You are a Senior First-Aid Assistant. 
    Explain common remedies for {problem} in {language}.
    
    GUIDELINES:
    - Use very simple language for rural users.
    - Mention Over-The-Counter (OTC) medicines (like Paracetamol for fever).
    - Suggest home care (hydration, rest).
    - Give a clear warning: "If symptoms persist or worsen, see a doctor."
    - Format: Use bullet points.
    """

    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Suggest care and common meds for {problem}"}
            ],
            model="llama-3.3-70b-versatile",
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def common_medicine_section():
    st.subheader("💊 Common Health Guide (Aam Bimariyan)")
    st.info("Yahan aap aam takleefon ke liye prathmik upchar ki jankari le sakte hain.")

    lang = st.selectbox("Information Language:", ["Hindi", "English", "Marathi", "Bengali"])
    
    # Common problems dropdown
    problems = {
        "Fever (Bukhar)": "Fever",
        "Cough (Khansi)": "Cough",
        "Loose Motion (Dust)": "Diarrhea/Loose Motion",
        "Vomiting (Ulti)": "Vomiting/Nausea",
        "Acidity/Gas": "Acidity or Gas",
        "Body Pain (Dard)": "Body ache or Muscle pain",
        "Other (Kuch aur)": "Other"
    }
    
    choice = st.selectbox("Kya samasya hai?", list(problems.keys()))

    if choice == "Other (Kuch aur)":
        final_problem = st.text_input("Apni takleef yahan likhein:")
    else:
        final_problem = problems[choice]

    if st.button("Jankari Payein ✨"):
        if final_problem:
            with st.spinner("AI suggestion taiyar kar raha hai..."):
                advice = get_medicine_suggestion(final_problem, lang)
                st.markdown("---")
                st.markdown(advice)
                st.warning("⚠️ **Note:** Ye sirf jankari ke liye hai. Bina doctor ke consult kiye koi bhi heavy dose na lein.")
        else:
            st.warning("Pehle samasya batayein.")