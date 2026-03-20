# ============================================================
# prior_auth.py — NidanAI Prior Authorization Module
# PA request auto-generate karta hai with all required fields
# ============================================================

import streamlit as st
import os
import json
from groq import Groq
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_pa_request(age, gender, plan, diagnosis, treatment, icd_codes, cpt_codes):
    """
    AI se structured Prior Authorization request generate karta hai.
    """
    system_prompt = """
You are a medical Prior Authorization specialist. Generate a complete PA request.
Respond ONLY with valid JSON, no markdown.

{
  "urgency_level": "ROUTINE" or "URGENT" or "EMERGENCY",
  "urgency_reason": "why this urgency level",
  "clinical_justification": "2-3 sentences justifying medical necessity",
  "alternative_treatments_considered": ["treatment 1", "treatment 2"],
  "expected_duration": "e.g. 5-7 days hospitalization",
  "estimated_cost_range": "e.g. ₹80,000 - ₹1,20,000",
  "required_documents": ["document 1", "document 2"],
  "supporting_clinical_notes": "detailed clinical notes for reviewer",
  "reviewer_questions_anticipated": ["Q1", "Q2"],
  "reviewer_answers": ["Answer to Q1", "Answer to Q2"]
}
"""
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"""
Patient: {age}yr {gender}, Plan: {plan}
Diagnosis: {diagnosis}
Treatment: {treatment}
ICD Codes: {icd_codes}
CPT Codes: {cpt_codes}
Generate complete PA request.
"""}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
        )
        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())
    except Exception as e:
        return {"error": str(e)}


def prior_auth_section(claim_data: dict):
    """
    claim_data = {
        age, gender, plan, diagnosis, treatment,
        icd_codes, cpt_codes, verdict
    }
    """
    st.markdown("---")
    st.markdown("""
        <div style="background:rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.3);
                    border-radius:12px; padding:16px 20px; margin-bottom:20px;">
            <div style="font-size:11px; color:#f59e0b; font-family:monospace;
                        letter-spacing:2px; margin-bottom:4px;">PRIOR AUTHORIZATION REQUIRED</div>
            <div style="font-size:14px; color:#fcd34d;">
                ⚠️ Is procedure ke liye insurance company se pehle approval lena zaroori hai.
                Neeche PA request auto-generate karein.
            </div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        requesting_doctor = st.text_input("🩺 Requesting Doctor Name", placeholder="Dr. Sharma")
    with col2:
        hospital_name = st.text_input("🏥 Hospital Name", placeholder="AIIMS Bhubaneswar")
    with col3:
        pa_date = st.date_input("📅 Request Date", value=datetime.today())

    if st.button("📋 Generate Prior Authorization Request", use_container_width=True):
        if not requesting_doctor or not hospital_name:
            st.warning("Doctor aur Hospital ka naam bharein.")
            return

        with st.spinner("PA request generate ho rahi hai..."):
            pa = generate_pa_request(
                claim_data.get("age"), claim_data.get("gender"),
                claim_data.get("plan"), claim_data.get("diagnosis"),
                claim_data.get("treatment"), claim_data.get("icd_codes", []),
                claim_data.get("cpt_codes", [])
            )

        if "error" in pa:
            st.error(f"Error: {pa['error']}")
            return

        # --- RENDER PA FORM ---
        st.markdown("---")
        st.markdown("### 📄 Prior Authorization Request Form")

        # Header
        urgency_colors = {
            "EMERGENCY": "#ef4444",
            "URGENT": "#f59e0b",
            "ROUTINE": "#10b981"
        }
        urgency = pa.get("urgency_level", "ROUTINE")
        urg_color = urgency_colors.get(urgency, "#6b7280")

        st.markdown(f"""
            <div style="background:#1e293b; border:1px solid #334155; border-radius:12px;
                        padding:20px; margin-bottom:16px;">
                <div style="display:flex; justify-content:space-between; align-items:center;
                            margin-bottom:16px;">
                    <div>
                        <div style="font-size:18px; font-weight:700; color:#e2e8f0;">
                            Prior Authorization Request
                        </div>
                        <div style="font-size:12px; color:#64748b; margin-top:2px;">
                            PA-{datetime.today().strftime('%Y%m%d')}-{abs(hash(claim_data.get('diagnosis',''))) % 9999:04d}
                        </div>
                    </div>
                    <div style="background:rgba(0,0,0,0.3); border:1px solid {urg_color};
                                color:{urg_color}; border-radius:8px; padding:6px 16px;
                                font-family:monospace; font-size:13px; font-weight:700;">
                        {urgency}
                    </div>
                </div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;
                            font-size:13px; color:#94a3b8;">
                    <div><b style="color:#cbd5e1;">Patient Age/Gender:</b> {claim_data.get('age')}yr / {claim_data.get('gender')}</div>
                    <div><b style="color:#cbd5e1;">Insurance Plan:</b> {claim_data.get('plan')}</div>
                    <div><b style="color:#cbd5e1;">Requesting Doctor:</b> {requesting_doctor}</div>
                    <div><b style="color:#cbd5e1;">Hospital:</b> {hospital_name}</div>
                    <div><b style="color:#cbd5e1;">Request Date:</b> {pa_date.strftime('%d %b %Y')}</div>
                    <div><b style="color:#cbd5e1;">Expected Duration:</b> {pa.get('expected_duration','N/A')}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Clinical Details
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**📋 Clinical Justification:**")
            st.info(pa.get("clinical_justification", ""))

            st.markdown("**💰 Estimated Cost:**")
            st.markdown(f"`{pa.get('estimated_cost_range', 'N/A')}`")

            st.markdown("**🔄 Alternative Treatments Considered:**")
            for alt in pa.get("alternative_treatments_considered", []):
                st.markdown(f"• {alt}")

        with col_b:
            st.markdown("**📁 Required Documents:**")
            for doc in pa.get("required_documents", []):
                st.markdown(f"☐ {doc}")

            st.markdown("**⚠️ Urgency Reason:**")
            st.warning(pa.get("urgency_reason", ""))

        # Anticipated Q&A
        st.markdown("**❓ Anticipated Reviewer Questions & Answers:**")
        questions = pa.get("reviewer_questions_anticipated", [])
        answers = pa.get("reviewer_answers", [])
        for i, (q, a) in enumerate(zip(questions, answers), 1):
            with st.expander(f"Q{i}: {q}"):
                st.write(f"**Answer:** {a}")

        # Supporting Notes
        st.markdown("**📝 Supporting Clinical Notes:**")
        st.text_area(
            "Clinical Notes (editable before submission)",
            value=pa.get("supporting_clinical_notes", ""),
            height=120,
            key="pa_notes"
        )

        # Action buttons
        st.markdown("---")
        col_x, col_y, col_z = st.columns(3)
        with col_x:
            st.download_button(
                "⬇️ Download PA Request (TXT)",
                data=json.dumps({
                    "pa_id": f"PA-{datetime.today().strftime('%Y%m%d')}",
                    "patient": f"{claim_data.get('age')}yr {claim_data.get('gender')}",
                    "plan": claim_data.get("plan"),
                    "doctor": requesting_doctor,
                    "hospital": hospital_name,
                    **pa
                }, indent=2),
                file_name=f"PA_Request_{datetime.today().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col_y:
            st.button("📧 Send to Insurance (Demo)", use_container_width=True, disabled=True)
        with col_z:
            st.button("🖨️ Print Form (Demo)", use_container_width=True, disabled=True)

        st.success("✅ PA Request generated successfully! Download karein ya insurance portal pe submit karein.")