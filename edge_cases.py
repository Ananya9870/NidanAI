# ============================================================
# edge_cases.py — NidanAI Edge Case Stress Test Demo
# Judges ke liye: showcases guardrail enforcement on tricky cases
# ============================================================

import streamlit as st

# --- All edge case scenarios ---
EDGE_CASES = [
    {
        "id": "EC-001",
        "category": "EXCLUSION",
        "label": "🚫 Excluded Procedure",
        "title": "Cosmetic Surgery Claim",
        "description": "Patient claims rhinoplasty (nose job) under Ayushman Bharat.",
        "age": 28,
        "gender": "Female",
        "plan": "Ayushman Bharat (PMJAY)",
        "diagnosis": "Deviated nasal septum, patient requests cosmetic rhinoplasty for aesthetic improvement.",
        "treatment": "Cosmetic rhinoplasty surgery, general anaesthesia, 1-day hospitalization.",
        "expected_verdict": "REJECTED",
        "guardrail_triggered": "EXCLUSION — Cosmetic procedures excluded under PMJAY",
        "why_tricky": "AI might approve because 'deviated septum' is a real diagnosis. Guardrail must override.",
        "color": "#ef4444",
        "icon": "❌"
    },
    {
        "id": "EC-002",
        "category": "AGE_RESTRICTION",
        "label": "👶 Age Mismatch",
        "title": "Maternity Claim — Age 14",
        "description": "Minor patient (age 14) filing maternity claim.",
        "age": 14,
        "gender": "Female",
        "plan": "BSKY (Odisha)",
        "diagnosis": "Pregnancy at 38 weeks gestation.",
        "treatment": "Normal delivery, post-natal care, newborn screening.",
        "expected_verdict": "REJECTED",
        "guardrail_triggered": "AGE_RESTRICTION — Maternity coverage age 18-55 only",
        "why_tricky": "Medically valid claim but violates age policy. Must be flagged.",
        "color": "#ef4444",
        "icon": "👶"
    },
    {
        "id": "EC-003",
        "category": "PRIOR_AUTH",
        "label": "⚠️ No Prior Auth",
        "title": "Cardiac Stent Without PA",
        "description": "Stent procedure submitted without prior authorization.",
        "age": 55,
        "gender": "Male",
        "plan": "CGHS",
        "diagnosis": "Stable angina, single vessel CAD, elective intervention planned.",
        "treatment": "Elective PCI with drug-eluting stent in RCA, catheterization lab.",
        "expected_verdict": "PENDING REVIEW",
        "guardrail_triggered": "PRIOR_AUTH — Stent/PCI requires pre-approval under CGHS",
        "why_tricky": "Medically necessary and covered, but PA not obtained. Must go to review.",
        "color": "#f59e0b",
        "icon": "⚠️"
    },
    {
        "id": "EC-004",
        "category": "FRAUD",
        "label": "🔍 Upcoding Fraud",
        "title": "Simple Fever Billed as High Complexity",
        "description": "Routine viral fever billed as high-complexity hospitalization.",
        "age": 32,
        "gender": "Male",
        "plan": "Private PPO",
        "diagnosis": "Mild viral fever, temperature 99.5°F, resolved in 24 hours, no complications.",
        "treatment": "ICU admission, high complexity care, extensive metabolic workup, 5-day stay.",
        "expected_verdict": "PENDING REVIEW",
        "guardrail_triggered": "FRAUD_FLAG — Simple diagnosis with complex billing (upcoding signal)",
        "why_tricky": "ICU for mild fever is a classic upcoding red flag. AI must catch this.",
        "color": "#f59e0b",
        "icon": "🔍"
    },
    {
        "id": "EC-005",
        "category": "EXCLUSION",
        "label": "🚬 Self-Inflicted Injury",
        "title": "Self-Harm Injury Claim",
        "description": "Treatment for self-inflicted injury submitted for coverage.",
        "age": 22,
        "gender": "Male",
        "plan": "ESIC",
        "diagnosis": "Laceration wounds from self-inflicted injury, requires surgical repair.",
        "treatment": "Wound debridement, suturing, tetanus prophylaxis, psychiatric consultation.",
        "expected_verdict": "REJECTED",
        "guardrail_triggered": "EXCLUSION — Self-inflicted injuries excluded under ESIC",
        "why_tricky": "Psychiatric care is covered but self-inflicted injury treatment is excluded.",
        "color": "#ef4444",
        "icon": "🚫"
    },
    {
        "id": "EC-006",
        "category": "LEGITIMATE",
        "label": "✅ Should Be Approved",
        "title": "Valid Emergency Appendectomy",
        "description": "Emergency appendectomy — should pass all guardrails cleanly.",
        "age": 24,
        "gender": "Female",
        "plan": "Ayushman Bharat (PMJAY)",
        "diagnosis": "Acute appendicitis, CT confirmed, Alvarado score 9, emergency presentation.",
        "treatment": "Emergency laparoscopic appendectomy, general anaesthesia, 48hr hospitalization.",
        "expected_verdict": "APPROVED",
        "guardrail_triggered": "None — All guardrails passed",
        "why_tricky": "Clean case — tests that valid claims are not over-rejected.",
        "color": "#10b981",
        "icon": "✅"
    },
]


def edge_cases_section(on_run_claim_callback):
    """
    on_run_claim_callback: function to call when user clicks 'Run This Case'
    It receives (age, gender, plan, diagnosis, treatment) as arguments.
    """
    st.markdown("""
        <div style="margin-bottom:8px;">
            <span style="background:rgba(239,68,68,0.1); color:#ef4444;
                         border:1px solid rgba(239,68,68,0.2); border-radius:20px;
                         padding:3px 12px; font-size:11px; font-family:monospace;
                         letter-spacing:1px;">🧪 STRESS TEST MODE</span>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("🧪 Edge Case Stress Test")
    st.markdown(
        "Yeh section judges ke liye hai — showcases ki guardrails tricky "
        "edge cases mein bhi correctly enforce hoti hain. "
        "Koi bhi case run karo aur dekho system kaise respond karta hai."
    )
    st.markdown("---")

    # Category filter
    categories = ["ALL", "EXCLUSION", "AGE_RESTRICTION", "PRIOR_AUTH", "FRAUD", "LEGITIMATE"]
    selected_cat = st.selectbox("Filter by Category:", categories)

    filtered = EDGE_CASES if selected_cat == "ALL" else [
        ec for ec in EDGE_CASES if ec["category"] == selected_cat
    ]

    for ec in filtered:
        with st.container():
            st.markdown(f"""
                <div style="background:#111827; border:1px solid #1e293b;
                            border-left:4px solid {ec['color']};
                            border-radius:12px; padding:18px 20px; margin-bottom:16px;">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <div style="font-size:10px; color:#64748b; font-family:monospace;
                                        letter-spacing:1px; margin-bottom:4px;">
                                {ec['id']} · {ec['category']}
                            </div>
                            <div style="font-size:16px; font-weight:700; color:#e2e8f0; margin-bottom:4px;">
                                {ec['icon']} {ec['title']}
                            </div>
                            <div style="font-size:13px; color:#94a3b8; margin-bottom:10px;">
                                {ec['description']}
                            </div>
                            <div style="font-size:12px; color:#64748b;">
                                <b style="color:#cbd5e1;">Patient:</b> {ec['age']}yr {ec['gender']} ·
                                <b style="color:#cbd5e1;">Plan:</b> {ec['plan']}
                            </div>
                        </div>
                        <div style="text-align:right; flex-shrink:0; margin-left:16px;">
                            <div style="font-size:10px; color:#64748b; margin-bottom:4px;">Expected</div>
                            <div style="background:rgba(0,0,0,0.3); border:1px solid {ec['color']};
                                        color:{ec['color']}; border-radius:6px; padding:4px 10px;
                                        font-family:monospace; font-size:11px; font-weight:700;">
                                {ec['expected_verdict']}
                            </div>
                        </div>
                    </div>
                    <div style="margin-top:10px; padding:10px; background:rgba(0,0,0,0.2);
                                border-radius:8px; border:1px solid #1e293b;">
                        <div style="font-size:11px; color:#64748b; margin-bottom:4px;">
                            🛡️ GUARDRAIL TRIGGERED:
                        </div>
                        <div style="font-size:12px; color:#a5f3fc; font-family:monospace;">
                            {ec['guardrail_triggered']}
                        </div>
                    </div>
                    <div style="margin-top:8px; font-size:11px; color:#64748b; font-style:italic;">
                        💡 Why tricky: {ec['why_tricky']}
                    </div>
                </div>
            """, unsafe_allow_html=True)

            col_run, col_detail = st.columns([1, 3])
            with col_run:
                if st.button(f"▶ Run Case {ec['id']}", key=f"run_{ec['id']}", use_container_width=True):
                    on_run_claim_callback(
                        ec['age'], ec['gender'], ec['plan'],
                        ec['diagnosis'], ec['treatment']
                    )

            with col_detail:
                with st.expander("📋 View Full Details"):
                    st.markdown(f"**Diagnosis:** {ec['diagnosis']}")
                    st.markdown(f"**Treatment:** {ec['treatment']}")

    st.markdown("---")
    st.markdown("""
        <div style="background:rgba(59,130,246,0.08); border:1px solid rgba(59,130,246,0.2);
                    border-radius:10px; padding:14px; font-size:12px; color:#93c5fd;">
            ℹ️ <b>Note for Judges:</b> Each case above is designed to test a specific guardrail.
            The system uses a <b>two-layer approach</b> — AI reasoning first, then hardcoded rule engine override.
            This ensures compliance even if the LLM produces an incorrect verdict.
        </div>
    """, unsafe_allow_html=True)