# ============================================================
# claim_agent.py — Autonomous Claim Processing Agent
# Multi-step workflow jo khud decide karta hai har step pe
# ============================================================

import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ============================================================
# AGENT STEP 1: Completeness Check
# ============================================================

def agent_check_completeness(age, gender, plan, diagnosis, treatment) -> dict:
    """
    Agent khud check karta hai ki claim mein enough info hai ya nahi.
    Agar nahi hai toh clarification questions generate karta hai.
    """
    prompt = f"""
You are a medical claim intake agent. Analyze if this claim has enough information to process.

Patient Age: {age}
Gender: {gender}
Insurance Plan: {plan}
Diagnosis: {diagnosis}
Treatment: {treatment}

Check for:
1. Is diagnosis specific enough? (vague = "not feeling well", specific = "Type 2 Diabetes with HbA1c 11.2%")
2. Is treatment clearly stated?
3. Are there any obvious missing critical details?

Respond ONLY with valid JSON:
{{
  "is_complete": true or false,
  "completeness_score": 0-100,
  "missing_fields": ["list of what is missing"],
  "clarification_questions": ["question 1", "question 2"],
  "reasoning": "why complete or incomplete"
}}
"""
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
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
        return {
            "is_complete": True,
            "completeness_score": 70,
            "missing_fields": [],
            "clarification_questions": [],
            "reasoning": f"Completeness check error: {str(e)} — proceeding anyway."
        }


# ============================================================
# AGENT STEP 2: ICD-10 + CPT Assignment
# ============================================================

def agent_assign_codes(age, gender, plan, diagnosis, treatment) -> dict:
    """
    Agent assigns ICD-10 and CPT codes based on clinical info.
    """
    prompt = f"""
You are a certified medical coder. Assign ICD-10-CM and CPT codes.

Patient: {age}yr {gender}, Plan: {plan}
Diagnosis: {diagnosis}
Treatment: {treatment}

Rules:
- Use REAL, VALID ICD-10-CM codes only (e.g. E11.40, I21.0, K35.89)
- Use REAL, VALID CPT codes only (e.g. 99223, 44970, 27130)
- Assign ALL relevant codes, not just one
- Codes must match the clinical scenario

Respond ONLY with valid JSON:
{{
  "icd_codes": [
    {{"code": "E11.40", "description": "Type 2 diabetes mellitus with diabetic neuropathy, unspecified", "confidence": "HIGH"}}
  ],
  "cpt_codes": [
    {{"code": "99223", "description": "Initial hospital care, high complexity", "confidence": "HIGH"}}
  ],
  "coding_notes": "brief note on coding rationale"
}}
"""
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
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
        return {"icd_codes": [], "cpt_codes": [], "coding_notes": f"Error: {str(e)}"}


# ============================================================
# AGENT STEP 3: Medical Necessity Check
# ============================================================

def agent_check_medical_necessity(diagnosis, treatment, icd_codes, cpt_codes) -> dict:
    """
    Agent determines if treatment is medically necessary for the diagnosis.
    """
    prompt = f"""
You are a medical necessity reviewer at an insurance company.

Diagnosis: {diagnosis}
Treatment Requested: {treatment}
ICD-10 Codes: {[c['code'] for c in icd_codes]}
CPT Codes: {[c['code'] for c in cpt_codes]}

Determine:
1. Is this treatment medically necessary for this diagnosis?
2. Is the level of care appropriate? (e.g. ICU for mild fever = NOT appropriate)
3. Are there less intensive alternatives?

Respond ONLY with valid JSON:
{{
  "medically_necessary": true or false,
  "necessity_score": 0-100,
  "level_of_care_appropriate": true or false,
  "reasoning": "detailed clinical reasoning",
  "alternatives": ["alternative 1", "alternative 2"],
  "flag": "PASS" or "WARN" or "FAIL"
}}
"""
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
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
        return {
            "medically_necessary": True,
            "necessity_score": 75,
            "level_of_care_appropriate": True,
            "reasoning": f"Error in check: {str(e)}",
            "alternatives": [],
            "flag": "WARN"
        }


# ============================================================
# AGENT STEP 4: Policy Coverage Check
# ============================================================

def agent_check_policy(plan, diagnosis, treatment, icd_codes, cpt_codes) -> dict:
    """
    Agent checks payer-specific policy coverage.
    """
    prompt = f"""
You are a health insurance policy expert specializing in Indian insurance plans.

Insurance Plan: {plan}
Diagnosis: {diagnosis}
Treatment: {treatment}
ICD Codes: {[c['code'] for c in icd_codes]}
CPT Codes: {[c['code'] for c in cpt_codes]}

Check against {plan} specific rules:
- Ayushman Bharat (PMJAY): Covers secondary/tertiary care up to ₹5L. Excludes cosmetic, OPD, fertility.
- BSKY (Odisha): Covers up to ₹5L general, ₹10L women. State-specific empanelled hospitals.
- ESIC: Covers insured employees and dependents. Occupational and general illness.
- CGHS: Central govt employees. Cashless at empanelled hospitals.
- Private PPO: Depends on policy. Generally broad coverage with co-pay.

Respond ONLY with valid JSON:
{{
  "covered": true or false,
  "coverage_percentage": 0-100,
  "exclusions_triggered": ["exclusion 1"],
  "waiting_period_applicable": true or false,
  "network_hospital_required": true or false,
  "estimated_covered_amount": "₹X - ₹Y",
  "policy_notes": "specific policy details",
  "flag": "PASS" or "WARN" or "FAIL"
}}
"""
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
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
        return {
            "covered": True,
            "coverage_percentage": 80,
            "exclusions_triggered": [],
            "waiting_period_applicable": False,
            "network_hospital_required": True,
            "estimated_covered_amount": "Unable to calculate",
            "policy_notes": f"Error: {str(e)}",
            "flag": "WARN"
        }


# ============================================================
# AGENT STEP 5: Final Verdict
# ============================================================

def agent_final_verdict(
    completeness, coding, necessity,
    policy, validation, guardrail_result
) -> dict:
    """
    Agent synthesizes all previous steps and gives final verdict.
    This is the autonomous decision-making step.
    """

    # If guardrail forced a verdict — respect it
    if guardrail_result.get("override"):
        forced = guardrail_result["forced_verdict"]
        return {
            "verdict": forced,
            "confidence": "99%",
            "verdict_source": "GUARDRAIL_ENGINE",
            "summary": f"Claim {forced} by hardcoded compliance guardrail engine. AI reasoning overridden.",
            "reasons": [
                {"icon": "🛡️", "text": f"Guardrail engine override: {forced}"},
                {"icon": "❌", "text": f"{len(guardrail_result['flags'])} compliance flag(s) raised"},
            ],
            "recommendation": "Review guardrail flags before resubmission."
        }

    # Agent decides based on all steps
    factors = {
        "completeness_ok": completeness.get("is_complete", True),
        "codes_valid": validation.get("all_valid", True),
        "medically_necessary": necessity.get("medically_necessary", True),
        "care_appropriate": necessity.get("level_of_care_appropriate", True),
        "policy_covered": policy.get("covered", True),
        "no_exclusions": len(policy.get("exclusions_triggered", [])) == 0,
        "pa_required": guardrail_result.get("prior_auth_required", False),
    }

    prompt = f"""
You are the final adjudication agent. Based on ALL these factors, give the final claim verdict.

Completeness Check: {completeness}
Code Validation: {validation}
Medical Necessity: {necessity}
Policy Coverage: {policy}
Compliance Flags: {guardrail_result.get('flags', [])}

Decision factors: {factors}

Give final verdict considering ALL factors. If PA required → PENDING REVIEW.
If any exclusion or medically unnecessary → REJECTED.
If all clear → APPROVED.

Respond ONLY with valid JSON:
{{
  "verdict": "APPROVED" or "REJECTED" or "PENDING REVIEW",
  "confidence": "percentage like 92%",
  "verdict_source": "AI_AGENT",
  "summary": "2-3 sentence final summary",
  "reasons": [
    {{"icon": "✅", "text": "reason"}},
    {{"icon": "❌", "text": "reason"}},
    {{"icon": "⚠️", "text": "reason"}}
  ],
  "recommendation": "what should happen next"
}}
"""
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
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
        return {
            "verdict": "PENDING REVIEW",
            "confidence": "50%",
            "verdict_source": "AI_AGENT",
            "summary": f"Error in final verdict: {str(e)}",
            "reasons": [{"icon": "⚠️", "text": "System error — manual review required"}],
            "recommendation": "Manual review required due to system error."
        }


# ============================================================
# MASTER AGENT RUNNER
# ============================================================

def run_claim_agent(age, gender, plan, diagnosis, treatment, guardrail_result) -> dict:
    """
    Master function — runs all 5 agent steps in sequence.
    Each step informs the next — true agentic workflow.

    Returns complete agent result with all steps.
    """
    steps = []

    # STEP 1: Completeness
    completeness = agent_check_completeness(age, gender, plan, diagnosis, treatment)
    steps.append({
        "step_num": 1,
        "name": "Claim Completeness Check",
        "tag": "PASS" if completeness.get("is_complete") else "WARN",
        "result": completeness,
        "detail": completeness.get("reasoning", ""),
        "score": completeness.get("completeness_score", 0),
    })

    # If critically incomplete — stop and ask
    if not completeness.get("is_complete") and completeness.get("completeness_score", 100) < 30:
        return {
            "status": "INCOMPLETE",
            "steps": steps,
            "clarification_questions": completeness.get("clarification_questions", []),
            "missing_fields": completeness.get("missing_fields", []),
        }

    # STEP 2: Code Assignment
    coding = agent_assign_codes(age, gender, plan, diagnosis, treatment)
    steps.append({
        "step_num": 2,
        "name": "ICD-10 & CPT Code Assignment",
        "tag": "PASS" if coding.get("icd_codes") else "WARN",
        "result": coding,
        "detail": coding.get("coding_notes", ""),
        "icd_codes": coding.get("icd_codes", []),
        "cpt_codes": coding.get("cpt_codes", []),
    })

    # STEP 3: Code Validation
    from icd_cpt_validator import validate_codes
    validation = validate_codes(coding.get("icd_codes", []), coding.get("cpt_codes", []))
    steps.append({
        "step_num": 3,
        "name": "ICD/CPT Code Validation",
        "tag": "PASS" if validation["all_valid"] else "WARN",
        "result": validation,
        "detail": f"{validation['invalid_count']} invalid code(s) detected out of {len(coding.get('icd_codes',[]))+len(coding.get('cpt_codes',[]))} total.",
    })

    # STEP 4: Medical Necessity
    necessity = agent_check_medical_necessity(
        diagnosis, treatment,
        coding.get("icd_codes", []),
        coding.get("cpt_codes", [])
    )
    steps.append({
        "step_num": 4,
        "name": "Medical Necessity Validation",
        "tag": necessity.get("flag", "WARN"),
        "result": necessity,
        "detail": necessity.get("reasoning", ""),
        "score": necessity.get("necessity_score", 0),
    })

    # STEP 5: Policy Coverage
    policy = agent_check_policy(
        plan, diagnosis, treatment,
        coding.get("icd_codes", []),
        coding.get("cpt_codes", [])
    )
    steps.append({
        "step_num": 5,
        "name": "Payer Policy Coverage Check",
        "tag": policy.get("flag", "WARN"),
        "result": policy,
        "detail": policy.get("policy_notes", ""),
    })

    # STEP 6: Guardrail Engine (already run externally)
    steps.append({
        "step_num": 6,
        "name": "Hardcoded Compliance Guardrail Engine",
        "tag": "PASS" if guardrail_result["guardrail_passed"] else "FAIL",
        "result": guardrail_result,
        "detail": f"{len(guardrail_result['flags'])} flag(s). Override: {guardrail_result['override']}.",
    })

    # STEP 7: Final Verdict (Agent decides)
    verdict = agent_final_verdict(
        completeness, coding, necessity,
        policy, validation, guardrail_result
    )
    steps.append({
        "step_num": 7,
        "name": "Autonomous Final Adjudication",
        "tag": "PASS" if verdict["verdict"] == "APPROVED" else ("FAIL" if verdict["verdict"] == "REJECTED" else "WARN"),
        "result": verdict,
        "detail": verdict.get("summary", ""),
    })

    return {
        "status": "COMPLETE",
        "steps": steps,
        "icd_codes": coding.get("icd_codes", []),
        "cpt_codes": coding.get("cpt_codes", []),
        "validation": validation,
        "necessity": necessity,
        "policy": policy,
        "completeness": completeness,
        "verdict": verdict["verdict"],
        "confidence": verdict.get("confidence", "N/A"),
        "verdict_source": verdict.get("verdict_source", "AI_AGENT"),
        "summary": verdict.get("summary", ""),
        "reasons": verdict.get("reasons", []),
        "recommendation": verdict.get("recommendation", ""),
        "prior_auth_required": guardrail_result.get("prior_auth_required", False),
        "guardrail_flags": guardrail_result.get("flags", []),
        "guardrail_override": guardrail_result.get("override", False),
        "coverage_info": guardrail_result.get("coverage_info", {}),
    }