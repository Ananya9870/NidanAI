# 🏥 NidanAI: Empowering Rural Healthcare with Intelligence

**Nidan AI** (meaning *Solution* or *Diagnosis*) is a cutting edge, location aware healthcare ecosystem designed specifically for the rural landscape. It bridges the gap between complex medical data and local accessibility by utilizing advanced Generative AI, Computer Vision, and Real time Geolocation.

---

## 🚀 Key Features

### 📍 1. Smart Sarkari Scheme Finder (Geo-Aware)
* **Automatic Detection:** Uses the **Browser Geolocation API** and **Reverse Geocoding** to instantly identify the user’s state.
* **Hyper-Local Results:** Dynamically fetches state-specific schemes (e.g., BSKY for Odisha, MJPJAY for Maharashtra) alongside central schemes like Ayushman Bharat.
* **Manual Override:** Allows users to manually select any Indian state to find schemes for relatives or friends in different regions.

### 📄 2. AI Medical Report Analyzer
* **Multimodal Processing:** Analyzes medical reports uploaded as images (JPG/PNG) or PDFs.
* **Simplified Insights:** Powered by **Llama-4 Scout**, it breaks down complex medical jargon into three levels: Summary, Key Findings, and a 3 Step Action Plan.
* **Local Language Support:** Explanations are provided in the user's preferred language (Hindi, English, etc.) for better clarity.

### 💬 3. Gramin Seva AI Chatbot
* **Context-Aware Dialogues:** Remembers patient history and current medications to provide personalized first-aid advice.
* **Voice Integration:** Integrated with **gTTS (Google Text-to-Speech)** to narrate responses, making it accessible for users who have difficulty reading.

### 📋 4. Privacy-First Health Profile
* **Patient Vault:** Users can securely store their medical history, blood group, and current medications, which the AI uses to provide safer recommendations.

---

## 🛠️ Tech Stack

### **Core Frameworks**
* **Frontend/UI:** [Streamlit](https://streamlit.io/) (For a fast, responsive web interface)
* **Language:** Python 3.9+

### **Artificial Intelligence & Models**
* **Large Language Model (LLM):** `Llama-3.3-70b-versatile` (via Groq Cloud)
* **Vision Model:** `meta-llama/llama-4-scout-17b` (For high-accuracy report scanning)
* **Voice Engine:** `gTTS` (Google Text-to-Speech)

### **APIs & Intelligence**
* **Inference Engine:** [Groq Cloud API](https://groq.com/) (For ultra-fast AI responses)
* **Location Services:** `streamlit-js-eval` (Browser Geolocation)
* **Geocoding:** `Geopy` (OpenStreetMap Nominatim API for coordinate-to-state mapping)

---

## 📂 Project Structure

```text
Nidan-AI/
├── main.py              # Main Entry point & Navigation
├── schemes_finder.py    # Geolocation & Govt Schemes logic
├── medical_guide.py     # OTC Medicines & First-Aid advice
├── patient_data.py      # Database handlers for patient profiles
├── auth.py              # Secure Login & SignUp system
├── .env                 # Environment variables (Private)
└── requirements.txt     # Project dependencies

⚙️ Installation & Setup
Clone the repository:

Bash
git clone [https://github.com/your-username/Nidan-AI.git](https://github.com/your-username/Nidan-AI.git)
cd Nidan-AI
Setup Virtual Environment:

Bash
python -m venv env
source env/bin/activate  # For Windows: env\Scripts\activate
Install Dependencies:

Bash
pip install -r requirements.txt
Environment Variables:
Create a .env file and add your Groq API Key:

Code snippet
GROQ_API_KEY=your_actual_key_here
Run the App:

Bash
streamlit run main.py

🛡️ Disclaimer
Nidan AI is an informational tool and is NOT a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of a qualified physician.

Developed with ❤️ for Rural India.
