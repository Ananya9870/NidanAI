# ============================================================
# claim_assistant.py — NidanAI Agentic Claim Assistant v3.0
# Full autonomous agent: Completeness → Coding → Validation
# → Necessity → Policy → Guardrails → Verdict
# ============================================================

import streamlit as st
import os
from dotenv import load_dotenv

from guardrails import run_guardrails
from prior_auth import prior_auth_section
from edge_cases import edge_cases_section
from claim_agent import run_claim_agent

load_dotenv()

# ============================================================
# RENDER HELPERS
# ============================================================

def render_verdict_badge(verdict, source="AI_AGENT", forced=False):
    colors = {
        "APPROVED":       ("#10b981", "#052e16", "✅"),
        "REJECTED":       ("#ef4444", "#2d0a0a", "❌"),
        "PENDING REVIEW": ("#f59e0b", "#2d1a00", "⏳"),
    }
    color, bg, icon = colors.get(verdict, ("#6b7280", "#111", "❓"))

    source_badge = ""
    if forced:
        source_badge = '<span style="background:rgba(239,68,68,0.15); color:#ef4444; border:1px solid #ef4444; border-radius:4px; padding:2px 8px; font-size:10px; font-family:monospace; margin-left:10px;">GUARDRAIL OVERRIDE</span>'
    elif source == "AI_AGENT":
        source_badge = '<span style="background:rgba(0,229,195,0.1); color:#00e5c3; border:1px solid rgba(0,229,195,0.3); border-radius:4px; padding:2px 8px; font-size:10px; font-family:monospace; margin-left:10px;">AUTONOMOUS AGENT</span>'

    st.markdown(f"""
        <div style="background:{bg}; border:2px solid {color}; border-radius:12px;
                    padding:18px 24px; margin-bottom:16px;">
            <div style="font-size:11px; color:#94a3b8; font-family:monospace;
                        letter-spacing:2px; margin-bottom:4px;">CLAIM VERDICT</div>
            <div style="font-size:28px; font-weight:700; color:{color};">
                {icon} {verdict}{source_badge}
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_agent_steps(steps):
    """Render all 7 agent steps with results."""
    tag_styles = {
        "PASS": "background:#052e16; color:#10b981; border:1px solid #10b981;",
        "FAIL": "background:#2d0a0a; color:#ef4444; border:1px solid #ef4444;",
        "WARN": "background:#2d1a00; color:#f59e0b; border:1px solid #f59e0b;",
        "INFO": "background:#0c1a3a; color:#3b82f6; border:1px solid #3b82f6;",
    }

    for step in steps:
        tag = step.get("tag", "INFO")
        style = tag_styles.get(tag, tag_styles["INFO"])
        num = str(step["step_num"]).zfill(2)
        name = step["name"]
        detail = step.get("detail", "")

        # Extra info per step
        extra = ""
        if step["step_num"] == 1:
            score = step.get("score", 0)
            extra = f'<div style="font-size:11px; color:#64748b; margin-top:4px;">Completeness Score: <b style="color:#e2e8f0;">{score}%</b></div>'
        elif step["step_num"] == 2:
            icds = step.get("icd_codes", [])
            cpts = step.get("cpt_codes", [])
            chips = " ".join([f'<code style="background:#1e293b; color:#a5f3fc; padding:1px 6px; border-radius:4px; font-size:11px;">{c["code"]}</code>' for c in icds + cpts])
            extra = f'<div style="margin-top:6px;">{chips}</div>'
        elif step["step_num"] == 3:
            result = step.get("result", {})
            invalid = result.get("invalid_count", 0)
            corrected = result.get("corrected_codes", [])
            if invalid > 0:
                extra = f'<div style="font-size:11px; color:#f59e0b; margin-top:4px;">⚠️ {invalid} invalid code(s) detected.'
                for c in corrected:
                    extra += f' Suggested: <code style="color:#a5f3fc;">{c["suggested"]}</code> ({c["suggested_desc"][:40]}...)'
                extra += '</div>'
            else:
                extra = '<div style="font-size:11px; color:#10b981; margin-top:4px;">✅ All codes verified against real ICD-10/CPT database.</div>'
        elif step["step_num"] == 4:
            score = step.get("score", 0)
            extra = f'<div style="font-size:11px; color:#64748b; margin-top:4px;">Necessity Score: <b style="color:#e2e8f0;">{score}%</b></div>'

        st.markdown(f"""
            <div style="display:flex; gap:14px; padding:12px 0; border-bottom:1px solid #1e293b;">
                <div style="width:28px; height:28px; border-radius:50%;
                            background:#1e293b; border:1px solid #334155;
                            display:flex; align-items:center; justify-content:center;
                            font-family:monospace; font-size:11px; color:#64748b;
                            flex-shrink:0; margin-top:2px;">{num}</div>
                <div style="flex:1;">
                    <div style="font-size:13px; font-weight:600; color:#e2e8f0; margin-bottom:4px;">
                        {name}
                        <span style="{style} border-radius:4px; padding:1px 8px;
                                      font-size:10px; font-family:monospace; margin-left:8px;">{tag}</span>
                    </div>
                    <div style="font-size:12px; color:#64748b; line-height:1.5;">{detail}</div>
                    {extra}
                </div>
            </div>
        """, unsafe_allow_html=True)


def render_validation_report(validation):
    """Render ICD/CPT validation results."""
    st.markdown("**🔬 Code Validation Report:**")

    from icd_cpt_validator import get_code_stats
    stats = get_code_stats()
    st.markdown(
        f'<div style="font-size:11px; color:#64748b; margin-bottom:10px;">'
        f'Validated against {stats["total_icd"]} ICD-10 + {stats["total_cpt"]} CPT codes in local database</div>',
        unsafe_allow_html=True
    )

    col_icd, col_cpt = st.columns(2)

    with col_icd:
        st.markdown("**ICD-10 Codes:**")
        for r in validation.get("icd_results", []):
            if r["valid"]:
                st.markdown(f"""
                    <div style="background:#1e293b; border:1px solid #10b981;
                                border-radius:8px; padding:10px 14px; margin-bottom:8px;">
                        <code style="color:#a5f3fc;">{r['code']}</code>
                        <span style="color:#10b981; font-size:10px; margin-left:6px;">✓ VALID</span>
                        <div style="font-size:12px; color:#94a3b8; margin-top:4px;">{r['real_description']}</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                suggestion = r.get("suggestion", {})
                sugg_text = f'Suggested: <code style="color:#fcd34d;">{suggestion.get("code","")}</code>' if suggestion else "No suggestion found"
                st.markdown(f"""
                    <div style="background:#1e293b; border:1px solid #ef4444;
                                border-radius:8px; padding:10px 14px; margin-bottom:8px;">
                        <code style="color:#fca5a5;">{r['code']}</code>
                        <span style="color:#ef4444; font-size:10px; margin-left:6px;">✗ INVALID</span>
                        <div style="font-size:12px; color:#94a3b8; margin-top:4px;">{sugg_text}</div>
                    </div>
                """, unsafe_allow_html=True)

    with col_cpt:
        st.markdown("**CPT Codes:**")
        for r in validation.get("cpt_results", []):
            if r["valid"]:
                st.markdown(f"""
                    <div style="background:#1e293b; border:1px solid #10b981;
                                border-radius:8px; padding:10px 14px; margin-bottom:8px;">
                        <code style="color:#a5f3fc;">{r['code']}</code>
                        <span style="color:#10b981; font-size:10px; margin-left:6px;">✓ VALID</span>
                        <div style="font-size:12px; color:#94a3b8; margin-top:4px;">{r['real_description']}</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                suggestion = r.get("suggestion", {})
                sugg_text = f'Suggested: <code style="color:#fcd34d;">{suggestion.get("code","")}</code>' if suggestion else "No suggestion found"
                st.markdown(f"""
                    <div style="background:#1e293b; border:1px solid #ef4444;
                                border-radius:8px; padding:10px 14px; margin-bottom:8px;">
                        <code style="color:#fca5a5;">{r['code']}</code>
                        <span style="color:#ef4444; font-size:10px; margin-left:6px;">✗ INVALID</span>
                        <div style="font-size:12px; color:#94a3b8; margin-top:4px;">{sugg_text}</div>
                    </div>
                """, unsafe_allow_html=True)


def render_guardrail_flags(flags):
    if not flags:
        st.markdown("""
            <div style="background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.2);
                        border-radius:8px; padding:12px 16px; margin-bottom:12px;
                        font-size:13px; color:#6ee7b7;">
                🛡️ All compliance guardrails passed. No flags raised.
            </div>
        """, unsafe_allow_html=True)
        return
    severity_colors = {"HIGH": "#ef4444", "MEDIUM": "#f59e0b", "LOW": "#3b82f6"}
    for flag in flags:
        color = severity_colors.get(flag["severity"], "#6b7280")
        st.markdown(f"""
            <div style="background:rgba(0,0,0,0.2); border:1px solid {color};
                        border-left:4px solid {color}; border-radius:8px;
                        padding:12px 16px; margin-bottom:8px;">
                <div style="font-size:13px; color:#e2e8f0;">{flag['message']}</div>
                <div style="font-size:10px; color:#64748b; font-family:monospace; margin-top:4px;">
                    {flag['type']} · {flag['severity']}
                </div>
            </div>
        """, unsafe_allow_html=True)


# ============================================================
# MAIN PIPELINE RUNNER
# ============================================================

def run_full_agent(age, gender, plan, diagnosis, treatment):
    """Runs the complete agentic pipeline."""

    with st.status("🤖 Autonomous Agent Pipeline Running...", expanded=True) as status:
        st.write("🔍 Step 1: Checking claim completeness...")
        st.write("🏷️ Step 2: Assigning ICD-10 & CPT codes...")
        st.write("✅ Step 3: Validating codes against real database...")
        st.write("🩺 Step 4: Checking medical necessity...")
        st.write("📋 Step 5: Verifying payer policy coverage...")
        st.write("🛡️ Step 6: Running compliance guardrail engine...")
        st.write("⚖️ Step 7: Autonomous final adjudication...")

        # Run guardrails first (needed by agent)
        guardrail_result = run_guardrails(plan, diagnosis, treatment, int(age))

        # Run full agent
        result = run_claim_agent(age, gender, plan, diagnosis, treatment, guardrail_result)
        status.update(label="✅ Agent pipeline complete!", state="complete", expanded=False)

    # Handle incomplete claims
    if result.get("status") == "INCOMPLETE":
        st.warning("⚠️ **Agent detected incomplete claim information!**")
        st.markdown("**Please provide answers to these questions:**")
        for i, q in enumerate(result.get("clarification_questions", []), 1):
            st.markdown(f"**Q{i}:** {q}")
        st.info("Fill in the missing details and resubmit.")
        return

    # Store results
    st.session_state['agent_result'] = result
    st.session_state['claim_data'] = {
        "age": age, "gender": gender, "plan": plan,
        "diagnosis": diagnosis, "treatment": treatment,
        "icd_codes": result.get("icd_codes", []),
        "cpt_codes": result.get("cpt_codes", []),
    }
    st.rerun()


# ============================================================
# MAIN UI SECTION
# ============================================================

def claim_assistant_section():
    st.markdown("""
        <div style="margin-bottom:8px;">
            <span style="background:rgba(0,229,195,0.1); color:#00e5c3;
                         border:1px solid rgba(0,229,195,0.2); border-radius:20px;
                         padding:3px 12px; font-size:11px; font-family:monospace;
                         letter-spacing:1px;">🤖 AUTONOMOUS AGENT v3.0</span>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("🏥 AI Health Insurance Claim Agent")
    st.markdown(
        "Submit claim details — autonomous agent **7-step pipeline** execute karega: "
        "completeness check → ICD/CPT coding → **real code validation** → "
        "medical necessity → policy check → guardrails → final verdict."
    )

    tab1, tab2 = st.tabs(["📋 Claim Submission", "🧪 Edge Case Stress Test"])

    with tab1:
        _claim_submission_tab()

    with tab2:
        def load_edge_case(age, gender, plan, diagnosis, treatment):
            st.session_state['claim_age'] = age
            st.session_state['claim_gender'] = gender
            st.session_state['claim_plan'] = plan
            st.session_state['claim_diagnosis'] = diagnosis
            st.session_state['claim_treatment'] = treatment
            st.session_state['agent_result'] = None
            st.info("✅ Case loaded! 'Claim Submission' tab pe jao aur Analyze button dabao.")
        edge_cases_section(load_edge_case)


def _claim_submission_tab():
    # Init session state
    defaults = {
        'claim_age': 30, 'claim_gender': 'Male',
        'claim_plan': 'Ayushman Bharat (PMJAY)',
        'claim_diagnosis': '', 'claim_treatment': '',
        'agent_result': None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # Presets
    st.markdown("**⚡ Quick Presets:**")
    presets = {
        "🩺 Diabetes":      {"age":52,"gender":"Male","plan":"Ayushman Bharat (PMJAY)","diagnosis":"Type 2 Diabetes Mellitus with peripheral neuropathy, uncontrolled. HbA1c 11.2%.","treatment":"Hospitalization for intensive insulin titration, nerve conduction study, HbA1c test."},
        "❤️ Cardiac Stent": {"age":58,"gender":"Male","plan":"Private PPO","diagnosis":"Acute STEMI anterior wall. Troponin I elevated. ECG ST elevation V1-V4.","treatment":"Emergency PCI, drug-eluting stent in LAD, ICU 48 hours, dual antiplatelet therapy."},
        "🦴 Hip Fracture":  {"age":68,"gender":"Female","plan":"CGHS","diagnosis":"Closed fracture neck of femur right hip, displaced. Garden Type III.","treatment":"Total Hip Replacement surgery, post-op physiotherapy, 7-day hospitalization."},
        "🔪 Appendectomy":  {"age":24,"gender":"Male","plan":"ESIC","diagnosis":"Acute appendicitis uncomplicated. Alvarado 7. CT confirmed no perforation.","treatment":"Laparoscopic appendectomy, general anaesthesia, 2-day hospitalization."},
        "🤱 Delivery":      {"age":27,"gender":"Female","plan":"BSKY (Odisha)","diagnosis":"Full-term pregnancy 39 weeks, uncomplicated. G1P0.","treatment":"Normal vaginal delivery, post-natal care, newborn screening."},
    }
    cols = st.columns(len(presets))
    for col, (label, data) in zip(cols, presets.items()):
        if col.button(label, use_container_width=True):
            for k, v in data.items():
                st.session_state[f'claim_{k}'] = v
            st.session_state['agent_result'] = None
            st.rerun()

    st.markdown("---")

    plans = ["Ayushman Bharat (PMJAY)", "BSKY (Odisha)", "ESIC", "CGHS", "Private PPO"]
    genders = ["Male", "Female", "Other"]

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        age = st.number_input(
            "Patient Age", min_value=0, max_value=120,
            value=int(st.session_state.get('claim_age') or 30)
        )
    with col2:
        saved_gender = st.session_state.get('claim_gender', 'Male')
        gender = st.selectbox("Gender", genders,
            index=genders.index(saved_gender) if saved_gender in genders else 0)
    with col3:
        saved_plan = st.session_state.get('claim_plan', plans[0])
        plan = st.selectbox("Insurance Plan", plans,
            index=plans.index(saved_plan) if saved_plan in plans else 0)

    diagnosis = st.text_area(
        "📋 Diagnosis / Clinical Condition",
        value=st.session_state.get('claim_diagnosis', ''),
        placeholder="e.g. Type 2 Diabetes with HbA1c 11.2% and peripheral neuropathy...",
        height=100
    )
    treatment = st.text_area(
        "💉 Treatment / Procedure Requested",
        value=st.session_state.get('claim_treatment', ''),
        placeholder="e.g. Hospitalization for insulin titration, nerve conduction study...",
        height=100
    )

    st.markdown("")
    if st.button("🤖 Run Autonomous Agent Pipeline", use_container_width=True, type="primary"):
        if not diagnosis.strip() or not treatment.strip():
            st.warning("⚠️ Diagnosis aur Treatment dono fields bharein.")
            return
        st.session_state.update({
            'claim_age': age, 'claim_gender': gender,
            'claim_plan': plan, 'claim_diagnosis': diagnosis,
            'claim_treatment': treatment,
        })
        run_full_agent(age, gender, plan, diagnosis, treatment)

    # --- RESULTS ---
    result = st.session_state.get('agent_result')
    if not result:
        return

    claim_data = st.session_state.get('claim_data', {})
    st.markdown("---")

    # Verdict
    render_verdict_badge(
        result["verdict"],
        source=result.get("verdict_source", "AI_AGENT"),
        forced=result.get("guardrail_override", False)
    )

    # Summary + Confidence
    st.markdown(f"""
        <div style="background:#1e293b; border:1px solid #334155; border-radius:8px;
                    padding:14px; margin-bottom:16px;">
            <span style="font-size:11px; color:#64748b; font-family:monospace;">
                CONFIDENCE: {result.get('confidence','N/A')} &nbsp;|&nbsp;
                SOURCE: {result.get('verdict_source','AI_AGENT')}
                {'&nbsp;|&nbsp;<b style="color:#ef4444;">⚠️ GUARDRAIL OVERRIDE</b>' if result.get('guardrail_override') else ''}
            </span><br>
            <span style="font-size:13px; color:#cbd5e1; line-height:1.7;">{result.get('summary','')}</span>
        </div>
    """, unsafe_allow_html=True)

    # Recommendation
    if result.get("recommendation"):
        st.markdown(f"""
            <div style="background:rgba(59,130,246,0.08); border:1px solid rgba(59,130,246,0.2);
                        border-radius:8px; padding:10px 14px; margin-bottom:16px;
                        font-size:13px; color:#93c5fd;">
                💡 <b>Next Step:</b> {result['recommendation']}
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Agent Steps
    st.markdown("**🤖 Autonomous Agent — 7-Step Pipeline:**")
    render_agent_steps(result.get("steps", []))

    st.markdown("---")

    # Code Validation Report
    if result.get("validation"):
        render_validation_report(result["validation"])
        st.markdown("---")

    # Guardrail Flags
    st.markdown("**🛡️ Compliance Guardrail Flags:**")
    render_guardrail_flags(result.get("guardrail_flags", []))

    # Coverage Info
    cov = result.get("coverage_info", {})
    if cov:
        limit = f"₹{cov['annual_limit']:,}" if cov.get('annual_limit') else "No fixed cap"
        st.markdown(f"""
            <div style="background:rgba(59,130,246,0.08); border:1px solid rgba(59,130,246,0.2);
                        border-radius:8px; padding:10px 14px; margin-bottom:12px;
                        font-size:12px; color:#93c5fd;">
                💳 <b>Coverage ({claim_data.get('plan','')}):</b> {limit} | {cov.get('note','')}
            </div>
        """, unsafe_allow_html=True)

    # Decision Reasons
    st.markdown("**📌 Decision Reasons:**")
    for r in result.get("reasons", []):
        st.markdown(f"{r['icon']} {r['text']}")

    # Prior Auth
    if result.get("prior_auth_required"):
        prior_auth_section(claim_data)

    st.markdown("---")
    if st.button("🔄 New Claim"):
        st.session_state['agent_result'] = None
        st.session_state['claim_diagnosis'] = ''
        st.session_state['claim_treatment'] = ''
        st.rerun()

    st.info("⚠️ Disclaimer: AI-generated adjudication sirf informational hai. Final decision insurance provider ka hoga.")