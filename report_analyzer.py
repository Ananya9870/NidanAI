import streamlit as st
import os
import io
from groq import Groq
from PyPDF2 import PdfReader
from PIL import Image
import base64

# Initialize Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def encode_image(image_file):
    """Image ko base64 mein convert karne ke liye (Groq Vision ke liye)"""
    return base64.b64encode(image_file.read()).decode('utf-8')

def get_report_explanation(content, language, is_image=False):
    """
    GenAI Logic: Agar image hai toh Vision model use karega, 
    agar text/PDF hai toh versatile model.
    """
    system_prompt = f"""
    You are a Senior Medical Consultant AI. Explain medical reports to rural patients.
    Translate everything into {language}. Use extremely simple language.
    
    STRUCTURE:
    1. LEVEL 1 (Summary): 2-line simple summary.
    2. LEVEL 2 (Key Findings): Explain values (e.g., 'High Glucose' means 'Khoon mein shakkar zyada hai').
    3. LEVEL 3 (Action Plan): Next steps/Doctor consultation advice.
    """

    try:
        if is_image:
            # Vision Model Call for Images/Photos
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": system_prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{content}"},
                            },
                        ],
                    }
                ],
                model="llama-3.2-11b-vision-preview", # Vision Model
            )
        else:
            # Standard Text Call for PDFs
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze this report text: {content}"}
                ],
                model="llama-3.3-70b-versatile",
            )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def report_analysis_page():
    st.title("📄 Smart Report Analyzer (OCR & Vision)")
    st.markdown("---")
    st.write("Apni medical report (PDF ya Photo) upload karein.")

    lang = st.selectbox("Bhasha chunein:", ["Hindi", "English"])

    # File Uploader
    uploaded_file = st.file_uploader("Upload Report (PDF, JPG, PNG)", type=["pdf", "jpg", "jpeg", "png"])

    if st.button("Analyze Report ✨"):
        if uploaded_file is not None:
            with st.spinner("AI report ko scan aur analyze kar raha hai..."):
                file_details = uploaded_file.type
                
                # 1. Agar Image hai (JPG/PNG)
                if "image" in file_details:
                    base64_image = encode_image(uploaded_file)
                    analysis = get_report_explanation(base64_image, lang, is_image=True)
                
                # 2. Agar PDF hai
                elif "pdf" in file_details:
                    pdf_reader = PdfReader(uploaded_file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                    analysis = get_report_explanation(text, lang, is_image=False)
                
                # Output display
                st.success("Analysis Complete!")
                st.markdown(analysis)
                st.info("⚠️ Note: Ye sirf jankari ke liye hai. Doctor se zaroor milein.")
        else:
            st.warning("Pehle file upload karein.")