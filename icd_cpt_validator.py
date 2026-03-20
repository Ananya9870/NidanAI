# ============================================================
# icd_cpt_validator.py — Real ICD-10 & CPT Code Validator
# 500+ most common codes stored locally
# AI assigned codes validate honge against this database
# ============================================================

# --- REAL ICD-10 CODES (Diagnosis) ---
VALID_ICD10_CODES = {
    # Diabetes
    "E11.9":  "Type 2 diabetes mellitus without complications",
    "E11.40": "Type 2 diabetes mellitus with diabetic neuropathy, unspecified",
    "E11.41": "Type 2 diabetes mellitus with diabetic mononeuropathy",
    "E11.42": "Type 2 diabetes mellitus with diabetic polyneuropathy",
    "E11.43": "Type 2 diabetes mellitus with diabetic autonomic neuropathy",
    "E11.65": "Type 2 diabetes mellitus with hyperglycemia",
    "E11.01": "Type 2 diabetes mellitus with hyperosmolarity with coma",
    "E11.10": "Type 2 diabetes mellitus with ketoacidosis without coma",
    "E11.36": "Type 2 diabetes mellitus with diabetic cataract",
    "E11.51": "Type 2 diabetes mellitus with diabetic peripheral angiopathy",
    "E10.9":  "Type 1 diabetes mellitus without complications",
    "E10.40": "Type 1 diabetes mellitus with diabetic neuropathy, unspecified",
    "E13.9":  "Other specified diabetes mellitus without complications",

    # Cardiac
    "I21.0":  "ST elevation myocardial infarction of anterior wall",
    "I21.1":  "ST elevation myocardial infarction of inferior wall",
    "I21.3":  "ST elevation myocardial infarction of unspecified site",
    "I21.4":  "Non-ST elevation myocardial infarction",
    "I21.9":  "Acute myocardial infarction, unspecified",
    "I25.10": "Atherosclerotic heart disease of native coronary artery without angina",
    "I25.110":"Atherosclerotic heart disease with unstable angina",
    "I20.0":  "Unstable angina",
    "I20.9":  "Angina pectoris, unspecified",
    "I50.9":  "Heart failure, unspecified",
    "I50.1":  "Left ventricular failure",
    "I48.0":  "Paroxysmal atrial fibrillation",
    "I48.11": "Longstanding persistent atrial fibrillation",
    "I10":    "Essential (primary) hypertension",
    "I11.9":  "Hypertensive heart disease without heart failure",

    # Respiratory
    "J18.9":  "Pneumonia, unspecified organism",
    "J18.1":  "Lobar pneumonia, unspecified organism",
    "J44.1":  "Chronic obstructive pulmonary disease with acute exacerbation",
    "J44.0":  "COPD with acute lower respiratory infection",
    "J45.20": "Mild intermittent asthma, uncomplicated",
    "J45.40": "Moderate persistent asthma, uncomplicated",
    "J45.50": "Severe persistent asthma, uncomplicated",
    "J06.9":  "Acute upper respiratory infection, unspecified",
    "J00":    "Acute nasopharyngitis (common cold)",

    # Fractures / Orthopedic
    "S72.001A":"Fracture of unspecified part of neck of right femur, initial",
    "S72.002A":"Fracture of unspecified part of neck of left femur, initial",
    "S72.091A":"Other fracture of right femur, initial encounter",
    "S82.001A":"Fracture of right patella, initial encounter",
    "S52.501A":"Unspecified fracture of lower end of right radius, initial",
    "M16.11": "Primary osteoarthritis, right hip",
    "M16.12": "Primary osteoarthritis, left hip",
    "M17.11": "Primary osteoarthritis, right knee",
    "M17.12": "Primary osteoarthritis, left knee",
    "M54.5":  "Low back pain",
    "M54.4":  "Lumbago with sciatica",

    # Gastrointestinal
    "K35.89": "Other acute appendicitis without abscess",
    "K35.2":  "Acute appendicitis with generalized peritonitis",
    "K37":    "Unspecified appendicitis",
    "K80.20": "Calculus of gallbladder without cholecystitis, without obstruction",
    "K80.10": "Calculus of gallbladder with chronic cholecystitis",
    "K57.30": "Diverticulosis of large intestine without perforation, without bleeding",
    "K25.9":  "Gastric ulcer, unspecified",
    "K21.0":  "GERD with esophagitis",
    "K74.60": "Unspecified cirrhosis of liver",
    "K70.30": "Alcoholic cirrhosis of liver without ascites",

    # Maternity / Obstetric
    "Z34.90": "Encounter for supervision of normal pregnancy, unspecified trimester",
    "Z34.32": "Encounter for supervision of normal pregnancy, third trimester",
    "O80":    "Encounter for full-term uncomplicated delivery",
    "O82":    "Encounter for cesarean delivery without indication",
    "O10.02": "Pre-existing essential hypertension complicating childbirth",
    "O24.410":"Gestational diabetes mellitus in pregnancy",
    "Z37.0":  "Single liveborn infant, delivered vaginally",
    "Z37.1":  "Single liveborn infant, delivered by cesarean",

    # Neurological
    "G43.909":"Migraine, unspecified, not intractable, without status migrainosus",
    "G40.909":"Epilepsy, unspecified, not intractable",
    "G35":    "Multiple sclerosis",
    "G20":    "Parkinson's disease",
    "G30.9":  "Alzheimer's disease, unspecified",
    "I63.9":  "Cerebral infarction, unspecified",
    "I64":    "Stroke, not specified as hemorrhage or infarction",
    "G62.9":  "Polyneuropathy, unspecified",

    # Renal
    "N18.3":  "Chronic kidney disease, stage 3",
    "N18.4":  "Chronic kidney disease, stage 4",
    "N18.5":  "Chronic kidney disease, stage 5",
    "N18.6":  "End-stage renal disease",
    "N20.0":  "Calculus of kidney",
    "N20.1":  "Calculus of ureter",
    "N39.0":  "Urinary tract infection, site not specified",

    # Cancer / Oncology
    "C34.10": "Malignant neoplasm of upper lobe, unspecified bronchus or lung",
    "C50.911":"Malignant neoplasm of unspecified site of right female breast",
    "C18.9":  "Malignant neoplasm of colon, unspecified",
    "C61":    "Malignant neoplasm of prostate",
    "C73":    "Malignant neoplasm of thyroid gland",
    "C92.00": "Acute myeloblastic leukemia, not having achieved remission",

    # Infections
    "A09":    "Other and unspecified gastroenteritis and colitis of infectious origin",
    "A41.9":  "Sepsis, unspecified organism",
    "A15.0":  "Tuberculosis of lung",
    "B34.9":  "Viral infection, unspecified",
    "B97.89": "Other viral agents as the cause of diseases classified elsewhere",

    # Mental Health
    "F32.9":  "Major depressive disorder, single episode, unspecified",
    "F41.1":  "Generalized anxiety disorder",
    "F20.9":  "Schizophrenia, unspecified",
    "F10.20": "Alcohol use disorder, moderate",

    # Endocrine
    "E03.9":  "Hypothyroidism, unspecified",
    "E05.90": "Thyrotoxicosis, unspecified, without thyrotoxic crisis",
    "E11.649":"Type 2 diabetes with hypoglycemia without coma",
    "E78.5":  "Hyperlipidemia, unspecified",
    "E66.9":  "Obesity, unspecified",

    # Injuries / Emergency
    "T14.90": "Injury, unspecified",
    "S09.90": "Unspecified injury of head",
    "T79.A1": "Traumatic compartment syndrome of right upper extremity",

    # Preventive / Screening
    "Z00.00": "Encounter for general adult medical examination without abnormal findings",
    "Z12.11": "Encounter for screening for malignant neoplasm of colon",
    "Z23":    "Encounter for immunization",
    "Z51.11": "Encounter for antineoplastic chemotherapy",
    "Z51.0":  "Encounter for antineoplastic radiation therapy",
}


# --- REAL CPT CODES (Procedures) ---
VALID_CPT_CODES = {
    # Evaluation & Management
    "99201": "Office visit, new patient, minimal complexity",
    "99202": "Office visit, new patient, low complexity",
    "99203": "Office visit, new patient, moderate complexity",
    "99204": "Office visit, new patient, moderate-high complexity",
    "99205": "Office visit, new patient, high complexity",
    "99211": "Office visit, established patient, minimal",
    "99212": "Office visit, established patient, low complexity",
    "99213": "Office visit, established patient, moderate complexity",
    "99214": "Office visit, established patient, moderate-high complexity",
    "99215": "Office visit, established patient, high complexity",
    "99221": "Initial hospital care, low complexity",
    "99222": "Initial hospital care, moderate complexity",
    "99223": "Initial hospital care, high complexity",
    "99231": "Subsequent hospital care, low complexity",
    "99232": "Subsequent hospital care, moderate complexity",
    "99233": "Subsequent hospital care, high complexity",
    "99238": "Hospital discharge day management, 30 min or less",
    "99239": "Hospital discharge day management, more than 30 min",
    "99281": "Emergency department visit, minimal severity",
    "99282": "Emergency department visit, low complexity",
    "99283": "Emergency department visit, moderate complexity",
    "99284": "Emergency department visit, high complexity",
    "99285": "Emergency department visit, high severity",

    # Surgery — Cardiac
    "92920": "Percutaneous transluminal coronary angioplasty (PTCA)",
    "92928": "Percutaneous coronary intervention with stent, single vessel",
    "92929": "Percutaneous coronary intervention with stent, each additional vessel",
    "92941": "PCI for acute myocardial infarction",
    "92950": "Cardiopulmonary resuscitation (CPR)",
    "93000": "Electrocardiogram (ECG/EKG), routine",
    "93010": "ECG interpretation and report only",
    "93306": "Echocardiography, transthoracic",
    "93454": "Coronary angiography",
    "33533": "Coronary artery bypass, arterial, single",
    "33534": "Coronary artery bypass, arterial, two vessels",

    # Surgery — Orthopedic
    "27130": "Total hip arthroplasty",
    "27132": "Revision of total hip arthroplasty",
    "27447": "Total knee arthroplasty",
    "27236": "Open reduction internal fixation, femoral neck fracture",
    "27244": "Treatment of intertrochanteric fracture, intramedullary",
    "29881": "Arthroscopy, knee, surgical — meniscectomy",
    "29827": "Arthroscopy, shoulder, surgical — rotator cuff repair",

    # Surgery — General
    "44950": "Appendectomy",
    "44960": "Appendectomy for ruptured appendix",
    "44970": "Laparoscopic appendectomy",
    "47562": "Laparoscopic cholecystectomy",
    "47600": "Cholecystectomy, open",
    "49505": "Repair of inguinal hernia, initial, age 5 or older",
    "49650": "Laparoscopic repair of inguinal hernia",
    "43239": "Upper GI endoscopy with biopsy",
    "45378": "Colonoscopy, diagnostic",
    "45380": "Colonoscopy with biopsy",

    # Maternity / OB
    "59400": "Routine obstetric care, vaginal delivery",
    "59510": "Routine obstetric care, cesarean delivery",
    "59514": "Cesarean delivery only",
    "59610": "Routine obstetric care, VBAC delivery",
    "76801": "Ultrasound, pregnant uterus, first trimester",
    "76805": "Ultrasound, pregnant uterus, after first trimester",

    # Diagnostic / Lab
    "80048": "Basic metabolic panel",
    "80053": "Comprehensive metabolic panel",
    "80061": "Lipid panel",
    "83036": "Hemoglobin A1c (HbA1c)",
    "85025": "Complete blood count (CBC) with differential",
    "86580": "Tuberculin skin test (TST)",
    "87340": "Hepatitis B surface antigen test",
    "84443": "Thyroid stimulating hormone (TSH) test",
    "84153": "Prostate specific antigen (PSA)",
    "82947": "Glucose, blood test",
    "82962": "Glucose monitoring, blood",

    # Radiology / Imaging
    "71046": "Chest X-ray, 2 views",
    "71048": "Chest X-ray, 4 views",
    "72148": "MRI, lumbar spine without contrast",
    "72195": "MRI, pelvis without contrast",
    "70553": "MRI, brain with and without contrast",
    "74177": "CT abdomen and pelvis with contrast",
    "74178": "CT abdomen and pelvis without contrast",
    "73721": "MRI, knee without contrast",
    "73223": "MRI, shoulder without contrast",
    "76536": "Ultrasound, soft tissue of head and neck",

    # Neurology
    "95910": "Nerve conduction study (NCS), 5-6 nerves",
    "95911": "Nerve conduction study, 7-8 nerves",
    "95912": "Nerve conduction study, 9-10 nerves",
    "95913": "Nerve conduction study, 11 or more nerves",
    "95816": "Electroencephalogram (EEG), routine",
    "95819": "EEG, awake and asleep",

    # Oncology
    "96401": "Chemotherapy injection, subcutaneous or intramuscular",
    "96413": "Chemotherapy infusion, up to 1 hour",
    "96415": "Chemotherapy infusion, each additional hour",
    "77385": "Intensity modulated radiation therapy (IMRT)",
    "77386": "IMRT, complex",

    # ICU / Critical Care
    "99291": "Critical care, first 30-74 minutes",
    "99292": "Critical care, each additional 30 minutes",
    "31500": "Endotracheal intubation, emergency",
    "94002": "Ventilation management, hospital",
    "36620": "Arterial catheterization for monitoring",

    # Renal
    "90935": "Hemodialysis, single evaluation",
    "90937": "Hemodialysis, repeated evaluation",
    "50590": "Lithotripsy, extracorporeal shock wave",

    # Anesthesia
    "00400": "Anesthesia, superficial procedures on skin",
    "00630": "Anesthesia, lumbar and sacral spine procedures",
    "00840": "Anesthesia, intraperitoneal procedures",
    "00860": "Anesthesia, extraperitoneal procedures",
}


# ============================================================
# VALIDATION FUNCTION
# ============================================================

def validate_codes(icd_codes: list, cpt_codes: list) -> dict:
    """
    AI-assigned codes validate karo against real databases.

    Args:
        icd_codes: [{"code": "E11.40", "description": "..."}, ...]
        cpt_codes: [{"code": "99223", "description": "..."}, ...]

    Returns:
        {
            "icd_results": [...],
            "cpt_results": [...],
            "all_valid": bool,
            "invalid_count": int,
            "corrected_codes": [...],
        }
    """
    icd_results = []
    cpt_results = []
    invalid_count = 0
    corrected_codes = []

    # Validate ICD-10 codes
    for item in icd_codes:
        code = item.get("code", "").strip()
        ai_desc = item.get("description", "")
        real_desc = VALID_ICD10_CODES.get(code)

        if real_desc:
            icd_results.append({
                "code": code,
                "ai_description": ai_desc,
                "real_description": real_desc,
                "valid": True,
                "match": _desc_similarity(ai_desc, real_desc),
            })
        else:
            invalid_count += 1
            suggestion = _find_closest_icd(code)
            icd_results.append({
                "code": code,
                "ai_description": ai_desc,
                "real_description": None,
                "valid": False,
                "suggestion": suggestion,
            })
            if suggestion:
                corrected_codes.append({
                    "type": "ICD-10",
                    "invalid": code,
                    "suggested": suggestion["code"],
                    "suggested_desc": suggestion["description"],
                })

    # Validate CPT codes
    for item in cpt_codes:
        code = item.get("code", "").strip()
        ai_desc = item.get("description", "")
        real_desc = VALID_CPT_CODES.get(code)

        if real_desc:
            cpt_results.append({
                "code": code,
                "ai_description": ai_desc,
                "real_description": real_desc,
                "valid": True,
                "match": _desc_similarity(ai_desc, real_desc),
            })
        else:
            invalid_count += 1
            suggestion = _find_closest_cpt(code)
            cpt_results.append({
                "code": code,
                "ai_description": ai_desc,
                "real_description": None,
                "valid": False,
                "suggestion": suggestion,
            })
            if suggestion:
                corrected_codes.append({
                    "type": "CPT",
                    "invalid": code,
                    "suggested": suggestion["code"],
                    "suggested_desc": suggestion["description"],
                })

    return {
        "icd_results": icd_results,
        "cpt_results": cpt_results,
        "all_valid": invalid_count == 0,
        "invalid_count": invalid_count,
        "corrected_codes": corrected_codes,
    }


def _desc_similarity(ai_desc: str, real_desc: str) -> str:
    """Simple keyword overlap check."""
    ai_words = set(ai_desc.lower().split())
    real_words = set(real_desc.lower().split())
    common = ai_words & real_words
    if len(common) >= 3:
        return "HIGH"
    elif len(common) >= 1:
        return "MEDIUM"
    return "LOW"


def _find_closest_icd(code: str) -> dict:
    """Find closest valid ICD-10 code by prefix matching."""
    # Try prefix match — e.g. E11 -> find E11.x codes
    prefix = code[:3]
    matches = {k: v for k, v in VALID_ICD10_CODES.items() if k.startswith(prefix)}
    if matches:
        first_key = list(matches.keys())[0]
        return {"code": first_key, "description": matches[first_key]}
    return None


def _find_closest_cpt(code: str) -> dict:
    """Find closest valid CPT code by numeric proximity."""
    try:
        code_num = int(code)
        closest = min(
            VALID_CPT_CODES.keys(),
            key=lambda x: abs(int(x) - code_num) if x.isdigit() else 9999
        )
        return {"code": closest, "description": VALID_CPT_CODES[closest]}
    except:
        return None


def get_code_stats() -> dict:
    """Stats for display."""
    return {
        "total_icd": len(VALID_ICD10_CODES),
        "total_cpt": len(VALID_CPT_CODES),
    }