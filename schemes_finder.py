import streamlit as st
import os
from groq import Groq
from streamlit_js_eval import get_geolocation
from geopy.geocoders import Nominatim
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_state_from_coords(loc):
    """
    Latitude aur Longitude se State ka naam nikalne ke liye.
    """
    try:
        if loc and 'coords' in loc:
            lat = loc['coords']['latitude']
            lon = loc['coords']['longitude']
            
            geolocator = Nominatim(user_agent="gramin_seva_ai_v2")
            location = geolocator.reverse(f"{lat}, {lon}", timeout=10)
            
            if location and 'address' in location.raw:
                address = location.raw['address']
                state = address.get('state') or address.get('province') or address.get('region')
                return state
    except Exception as e:
        print(f"Location Error: {e}")
    return None

def get_scheme_info(query, language, user_state):
    """
    AI logic to find health schemes based on disease and location.
    """
    system_prompt = f"""
    You are a 'Sarkari Health Scheme Expert'. 
    USER LOCATION: {user_state}
    LANGUAGE: {language}

    TASKS:
    1. If the state is known (e.g., Odisha, Bihar), mention specific state schemes (e.g., BSKY for Odisha, MJPJAY for Maharashtra).
    2. Always mention Ayushman Bharat (PM-JAY) as a primary central option.
    3. Tell if the surgery/treatment '{query}' is covered.
    4. List documentation needed: Aadhar Card, Ration Card, BPL Card.
    5. Give a simple 3-step guide on how to talk to the 'Ayushman Mitra' at the hospital.
    """

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Find government schemes for {query} in {user_state}"}
            ],
            model="llama-3.3-70b-versatile",
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def schemes_section():
    st.subheader("🏥 Smart Sarkari Scheme Finder")
    
    # --- 1. GEOLOCATION LOGIC ---
    loc = get_geolocation()
    detected_state = None

    if loc:
        detected_state = get_state_from_coords(loc)

    # --- 2. OPTIONAL MANUAL OVERRIDE ---
    st.markdown("---")
    # User ko choice dena ki wo auto-location use kare ya manual
    is_manual = st.checkbox("🔍 Doosre state (rajya) ki jankari chahiye?")

    if is_manual:
        # User manually state choose kar sakta hai
        final_state = st.selectbox("Apna pasandida rajya (State) chunein:", 
                                    ["Odisha", "Bihar", "Uttar Pradesh", "Maharashtra", 
                                     "West Bengal", "Delhi", "Rajasthan", "Madhya Pradesh", "Other"])
    else:
        # Automatic flow
        if detected_state:
            st.success(f"📍 Detected Location: **{detected_state}**")
            final_state = detected_state
        else:
            st.info("📍 Location detect kar rahe hain... (Yadi nahi ho rahi toh manual chunein)")
            # Fallback agar location abhi tak load nahi hui
            final_state = st.selectbox("State select karein (Detection Pending):", 
                                       ["Odisha", "Bihar", "UP", "Other"], key="fallback_state")

    # --- 3. UI INPUTS ---
    col1, col2 = st.columns(2)
    with col1:
        lang = st.selectbox("Information Language:", ["Hindi", "English", "Odia", "Bengali"], key="scheme_lang")
    with col2:
        query = st.text_input("Bimari/Surgery ka naam (e.g., Heart Operation, Stone):")

    if st.button("Scheme Ki Jankari Payein ✨"):
        if query:
            with st.spinner(f"{final_state} ke liye schemes dhoondh rahe hain..."):
                details = get_scheme_info(query, lang, final_state)
                st.markdown("---")
                st.markdown(details)
                st.info(f"Yahi jankari **{final_state}** ke niyamo ke anusar hai.")
        else:
            st.warning("Pehle bimari ka naam likhein.")