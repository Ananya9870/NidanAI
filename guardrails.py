# ============================================================
# guardrails.py — Dynamic Compliance Rule Engine
# Ab hardcoded nahi — DB se rules load hoti hain!
# ============================================================

from guardrails_db import (
    get_exclusions, get_age_restrictions,
    get_prior_auth_triggers, get_fraud_signals
)


def run_guardrails(plan: str, diagnosis: str, treatment: str, age: int) -> dict:
    combined_text = f"{diagnosis} {treatment}".lower()
    flags = []
    override = False
    forced_verdict = None
    prior_auth = False

    # CHECK 1: Plan Exclusions (from DB)
    exclusions = get_exclusions(plan=plan, active_only=True)
    for rule in exclusions:
        rid, rule_plan, keyword, active = rule
        if keyword.lower() in combined_text:
            flags.append({
                "type": "EXCLUSION",
                "severity": "HIGH",
                "message": f"❌ '{keyword.title()}' is explicitly excluded under {plan}. Claim must be REJECTED."
            })
            override = True
            forced_verdict = "REJECTED"

    # CHECK 2: Age Restrictions (from DB)
    age_rules = get_age_restrictions(active_only=True)
    for rule in age_rules:
        rid, cname, keywords_str, min_age, max_age, message, active = rule
        keywords = [kw.strip() for kw in keywords_str.split(",")]
        for kw in keywords:
            if kw and kw in combined_text:
                if not (min_age <= age <= max_age):
                    flags.append({
                        "type": "AGE_RESTRICTION",
                        "severity": "HIGH",
                        "message": f"❌ Age Restriction ({cname}): {message} Patient age: {age}."
                    })
                    override = True
                    forced_verdict = "REJECTED"
                break

    # CHECK 3: Prior Authorization (from DB)
    pa_triggers = get_prior_auth_triggers(active_only=True)
    for rule in pa_triggers:
        rid, keyword, active = rule
        if keyword.lower() in combined_text:
            prior_auth = True
            flags.append({
                "type": "PRIOR_AUTH",
                "severity": "MEDIUM",
                "message": f"⚠️ Prior Authorization required for '{keyword}' under {plan}."
            })
            if forced_verdict != "REJECTED":
                override = True
                forced_verdict = "PENDING REVIEW"
            break

    # CHECK 4: Fraud Signals (from DB)
    fraud_rules = get_fraud_signals(active_only=True)
    for rule in fraud_rules:
        rid, sname, keywords_str, message, active = rule
        keywords = [kw.strip() for kw in keywords_str.split(",")]
        if any(kw and kw in combined_text for kw in keywords):
            flags.append({
                "type": "FRAUD_FLAG",
                "severity": "MEDIUM",
                "message": f"⚠️ {message}"
            })

    # CHECK 5: Duplicate Claim (hardcoded - rarely changes)
    for dup in ["second opinion", "same procedure", "already done", "previously treated", "readmission"]:
        if dup in combined_text:
            flags.append({
                "type": "DUPLICATE_SIGNAL",
                "severity": "HIGH",
                "message": f"🔁 Possible duplicate claim: '{dup}' found in submission."
            })
            override = True
            forced_verdict = "PENDING REVIEW"
            break

    coverage_limits = {
        "Ayushman Bharat (PMJAY)": {"annual_limit": 500000,  "note": "₹5 lakh per family per year."},
        "BSKY (Odisha)":           {"annual_limit": 500000,  "note": "₹5L general / ₹10L women per family."},
        "ESIC":                    {"annual_limit": None,    "note": "Full care for insured persons. No cap."},
        "CGHS":                    {"annual_limit": None,    "note": "Cashless at empanelled hospitals. No cap."},
        "Private PPO":             {"annual_limit": 1000000, "note": "Up to ₹10 lakh. Depends on policy."},
    }

    return {
        "override": override,
        "forced_verdict": forced_verdict,
        "flags": flags,
        "prior_auth_required": prior_auth,
        "coverage_info": coverage_limits.get(plan, {}),
        "guardrail_passed": len([f for f in flags if f["severity"] == "HIGH"]) == 0,
    }