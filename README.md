# 🏥 NidanAI
### AI Powered Healthcare & Insurance Compliance Platform for Rural India
---

**Nidan** means *diagnosis* or *solution*.

NidanAI started as a simple idea: what if someone in a village could understand their medical report without needing to pay a doctor just to explain it? That grew into a full healthcare platform, and for this hackathon, we added something much more ambitious: an AI agent that processes health insurance claims the way an experienced medical coder and compliance officer would.


---

## Features

### 1. 🤖 Insurance Claim Agent
> *The core hackathon submission: a domain specialized autonomous agent for health insurance claim processing.*

You enter a patient's diagnosis and treatment. The agent does the rest.

**What happens under the hood:**

```
 Input: Diagnosis + Treatment + Insurance Plan
         │
         ▼
 ┌───────────────────────────────────┐
 │         7-Step Agent Pipeline     │
 │                                   │
 │  01  Completeness Check           │  ← Is there enough info to proceed?
 │  02  ICD-10 & CPT Assignment      │  ← Assigns real medical billing codes
 │  03  Code Validation              │  ← Checks against 500+ real codes DB
 │  04  Medical Necessity Review     │  ← Is this treatment justified?
 │  05  Payer Policy Check           │  ← What does this plan actually cover?
 │  06  Compliance Guardrail Engine  │  ← Independent rule engine (not AI)
 │  07  Final Adjudication           │  ← APPROVED / REJECTED / PENDING
 │                                   │
 └───────────────────────────────────┘
         │
         ▼
  Output: Verdict + ICD/CPT Codes + Full Audit Trail
```

**The compliance layer is the most important part.** Step 6 is a hardcoded rule engine that runs *completely independent of the AI*. So even if the LLM reasons incorrectly, this engine catches policy violations and overrides the verdict. The AI handles reasoning, the rule engine handles guarantees.

Things the guardrail engine checks:
- Excluded procedures per plan (cosmetic surgery, IVF, experimental drugs, self-harm)
- Age-based restrictions (maternity: 18–55 only, joint replacement: 40+ only)
- Prior authorization requirements (stents, transplants, ICU, chemotherapy)
- Fraud signals like upcoding (mild fever billed as ICU-level care)
- Duplicate claim detection

**Supported insurance plans:** Ayushman Bharat (PMJAY), BSKY Odisha, ESIC, CGHS, Private PPO

**Prior Authorization:** When a procedure needs pre-approval, the system auto-generates a PA form — urgency level, required documents, estimated cost, and anticipated reviewer questions included.

**Edge Case Stress Test:** A dedicated tab with 6 pre-loaded tricky scenarios to demonstrate that guardrails work even in adversarial inputs.

---

### 2. ⚙️ Dynamic Guardrails Admin Panel
> *Manage compliance rules from a UI, no code changes needed.*

All guardrail rules live in a SQLite database, not hardcoded in a Python file. There's a password-protected admin panel where you can:
- Add or remove plan exclusions
- Edit age restriction limits
- Add new prior auth triggers
- Toggle any rule on or off instantly

Changes go live immediately. No restart needed.

```
Admin Password: nidanai@admin
```

---

### 3. 📍 Govt Scheme Finder *(Location-Aware)*
> *Tell us your condition, we'll tell you what the government covers.*

Most people in rural areas don't know which government health schemes they qualify for. The app uses your browser's geolocation to detect your state automatically. Type in a condition or surgery name and it returns all relevant central and state-specific schemes: Ayushman Bharat, BSKY, MJPJAY, etc. along with coverage details and how to enroll.

You can also manually select any other state to check for family members elsewhere.

---

### 4. 📄 Medical Report Analyzer
> *Upload a report. Get a plain language explanation.*

Upload a photo or PDF of any medical report: blood test, X-ray, discharge summary and the AI breaks it down into three levels:
- **Summary** — what does this report say overall?
- **Key Findings** — what values are abnormal and what do they mean?
- **Action Plan** — what should you do next?

Supports Hindi, English, Odia, Bengali, Telugu, Marathi. Uses a vision model for image-based reports.

---

### 5. 💬 Gramin Seva Chatbot
> *A health assistant that actually knows your history.*

The chatbot pulls from your saved health profile (medical history, current medications) to give more relevant, safer answers. So if you're on blood thinners and ask about a headache, it won't just give a generic response. Responses are also read out loud using text-to-speech useful for users who struggle with reading.

Supports 7 languages: Hindi, English, Marathi, Bengali, Telugu, Odia, Assamese.

---

### 6. 💊 Common Medicine Guide
Practical OTC suggestions for everyday issues: fever, cough, acidity, loose motion, body pain. Simple language, home care tips, Written for people who don't have easy access to a doctor for minor issues. Always ends with a note to see a doctor if things don't get better, because it's an assistant, not a substitute.

---

### 7. 👤 Health Profile
A personal health vault where users store their blood group, medical history, and current medications. This data is used by the chatbot and claim agent to give more personalized responses.

---

### ⚙️ How the compliance engine actually works
The thing we're most proud of technically is the two-layer compliance design. Every claim goes through both layers, in order:
The AI layer handles the reasoning by understanding clinical language, assigning codes, checking policy context, assessing medical necessity. It's good at nuanced judgment calls.
The guardrail engine is a separate system that doesn't care what the AI said. It reads rules from a database and checks five things: whether the procedure is excluded under the plan, whether the patient's age violates any coverage restrictions, whether prior authorization is required, whether there are fraud signals like upcoding or unbundling, and whether the claim looks like a duplicate. If any high severity check fails, it overrides the verdict.
This separation matters. AI models can hallucinate. They can miss edge cases. Having a hardcoded rule layer that runs independently means the system stays compliant even when the LLM reasons incorrectly. It's the same logic that makes critical systems use multiple independent checks instead of relying on one smart thing to get it right every time.

---

## Tech Stack

| Layer | What we used |
|---|---|
| UI | Streamlit |
| Language | Python 3.9+ |
| LLM | Llama 3.3 70B (via Groq Cloud) |
| Vision Model | Llama 4 Scout 17B (via Groq Cloud) |
| Voice | gTTS (Google Text-to-Speech) |
| Database | SQLite |
| Geolocation | streamlit-js-eval + Geopy + OpenStreetMap |

---

## Project Structure

```
NidanAI/
│
├── main.py                  # entry point + page routing
│
│── claim_assistant.py       # claim UI + pipeline controller
├── claim_agent.py           # 7-step autonomous agent
├── icd_cpt_validator.py     # real ICD-10/CPT code validation
├── guardrails.py            # compliance rule engine (DB-backed)
├── guardrails_db.py         # SQLite CRUD for guardrail rules
├── guardrails_admin.py      # admin panel UI
├── prior_auth.py            # PA form generator
├── edge_cases.py            # stress test scenarios
│
├── schemes_finder.py        # geolocation + govt schemes
├── medical_guide.py         # OTC medicine guide
├── patient_data.py          # patient profile DB handler
├── auth.py                  # login / signup / password reset
│
├── requirements.txt
├── .env                     # your API key goes here (never committed)
└── .gitignore
```

---

## Getting Started

```bash
# Clone the repo
git clone https://github.com/Ananya9870/NidanAI.git
cd NidanAI

# Create and activate virtual environment
python -m venv env
env\Scripts\activate          # Windows
source env/bin/activate       # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create a .env file with your Groq API key
# Free key available at: console.groq.com
echo GROQ_API_KEY=your_key_here > .env

# Run the app
streamlit run main.py
```

---

## Testing the Claim Agent

These scenarios are pre-loaded in the Edge Case tab — or you can enter them manually:

| Scenario | Plan | Expected | What it tests |
|---|---|---|---|
| Type 2 Diabetes + nerve conduction study | PMJAY | ✅ Approved | Normal valid claim |
| Cosmetic rhinoplasty | PMJAY | ❌ Rejected | Plan exclusion rule |
| Cardiac stent, elective | CGHS | ⏳ Pending Review | Prior auth required |
| Normal delivery, patient age 14 | BSKY | ❌ Rejected | Age restriction |
| Mild viral fever + ICU billing | PPO | ⏳ Pending Review | Upcoding flag |
| Emergency appendectomy | ESIC | ✅ Approved | Clean claim, no flags |

---

## Disclaimer

NidanAI is built for demonstration and informational purposes. It is not a substitute for professional medical advice, actual insurance adjudication, or any official government process. Always consult a doctor and your insurance provider for real decisions.

---

<p align="center">Made with ❤️ for rural India &nbsp;·&nbsp; Team Astra </p>
