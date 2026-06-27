"""Deterministic clinical reasoning engine (DEMO MODE).

This is a transparent, rule-based knowledge model that lets the entire agentic
pipeline run fully offline with no API keys — critical for a reliable demo. It is
NOT a medical device and is for demonstration only.

The engine encodes a small curated knowledge base of acute presentations with:
  * associated symptoms and risk factors (weighted)
  * ICD-10 codes
  * guideline-aligned work-up (labs / imaging / referral / follow-up + CPT)

Diagnoses are scored by weighted symptom + risk-factor overlap against a base
prior, then normalised into calibrated-looking confidences. The same scoring is
reused as a structured prior even in LIVE mode (the LLM can override it), which
keeps outputs stable and auditable — a property payers value.
"""
from __future__ import annotations

import re
from typing import Dict, List, Tuple

# --------------------------------------------------------------------------- #
# Knowledge base                                                              #
# --------------------------------------------------------------------------- #
# weight: 2 = strongly suggestive, 1 = supportive
CONDITIONS: List[Dict] = [
    {
        "name": "Acute Coronary Syndrome",
        "icd10": "I24.9",
        "prior": 0.18,
        "symptoms": {"chest pain": 2, "shortness of breath": 1, "sweating": 2,
                      "diaphoresis": 2, "left arm pain": 2, "jaw pain": 1, "nausea": 1},
        "risk": {"hypertension": 1, "diabetes": 1, "smoking": 1,
                  "hyperlipidemia": 1, "age>55": 1, "male": 1, "family history": 1},
        "labs": ["Troponin (high-sensitivity)", "CBC", "Basic Metabolic Panel", "Lipid panel"],
        "imaging": ["12-lead ECG", "Chest X-Ray"],
        "referral": ["Cardiology", "Emergency Department"],
        "followup": ["Admit to telemetry / chest-pain pathway", "Serial troponin in 3h"],
        "cpt": ["93000", "80053", "84484", "71046"],
        "rationale": "Exertional/at-rest chest pain with diaphoresis and dyspnea in a "
                      "patient with cardiac risk factors is ACS until proven otherwise.",
    },
    {
        "name": "Acute Myocardial Infarction",
        "icd10": "I21.9",
        "prior": 0.12,
        "symptoms": {"chest pain": 2, "sweating": 2, "diaphoresis": 2,
                      "shortness of breath": 1, "left arm pain": 2, "nausea": 1},
        "risk": {"hypertension": 1, "diabetes": 1, "smoking": 1, "age>55": 1, "male": 1},
        "labs": ["Troponin (high-sensitivity)", "CBC", "BMP"],
        "imaging": ["12-lead ECG", "Chest X-Ray"],
        "referral": ["Cardiology / Cath lab", "Emergency Department"],
        "followup": ["Activate ACS pathway", "Continuous cardiac monitoring"],
        "cpt": ["93000", "84484", "80053"],
        "rationale": "ST-segment changes plus elevated troponin would confirm infarction; "
                      "presentation overlaps with ACS and must be excluded urgently.",
    },
    {
        "name": "Pulmonary Embolism",
        "icd10": "I26.99",
        "prior": 0.1,
        "symptoms": {"shortness of breath": 2, "chest pain": 1, "sweating": 1,
                      "leg swelling": 2, "cough": 1, "hemoptysis": 2, "tachycardia": 1,
                      "syncope": 1},
        "risk": {"smoking": 1, "immobility": 2, "cancer": 2, "recent surgery": 2,
                  "age>55": 1},
        "labs": ["D-dimer", "CBC", "BMP"],
        "imaging": ["CT Pulmonary Angiography", "12-lead ECG"],
        "referral": ["Emergency Department"],
        "followup": ["Risk-stratify (Wells/PERC)", "Anticoagulation if confirmed"],
        "cpt": ["71275", "85379", "93000"],
        "rationale": "Acute dyspnea with pleuritic chest pain warrants PE work-up; "
                      "cannot be excluded without D-dimer or CT angiography.",
    },
    {
        "name": "Stable / Unstable Angina",
        "icd10": "I20.0",
        "prior": 0.1,
        "symptoms": {"chest pain": 2, "shortness of breath": 1, "sweating": 1,
                      "exertional pain": 2},
        "risk": {"hypertension": 1, "diabetes": 1, "smoking": 1, "hyperlipidemia": 1,
                  "age>55": 1, "male": 1},
        "labs": ["Troponin (high-sensitivity)", "Lipid panel"],
        "imaging": ["12-lead ECG", "Stress test / coronary CTA"],
        "referral": ["Cardiology"],
        "followup": ["Antianginal therapy", "Outpatient ischemia evaluation"],
        "cpt": ["93000", "93017", "75574"],
        "rationale": "Predictable exertional chest pain relieved by rest suggests angina; "
                      "unstable features escalate urgency toward ACS.",
    },
    {
        "name": "Aortic Dissection",
        "icd10": "I71.00",
        "prior": 0.05,
        "symptoms": {"chest pain": 2, "back pain": 2, "tearing pain": 2,
                      "sweating": 1, "syncope": 1},
        "risk": {"hypertension": 2, "age>55": 1, "male": 1, "connective tissue disease": 2},
        "labs": ["CBC", "Type & crossmatch", "D-dimer"],
        "imaging": ["CT Angiography chest", "12-lead ECG"],
        "referral": ["Cardiothoracic surgery", "Emergency Department"],
        "followup": ["Strict blood-pressure control", "Urgent surgical evaluation"],
        "cpt": ["71275", "93000"],
        "rationale": "Sudden tearing chest/back pain with hypertension raises concern for "
                      "dissection — a can't-miss, high-mortality alternative.",
    },
    {
        "name": "GERD / Non-cardiac chest pain",
        "icd10": "K21.9",
        "prior": 0.08,
        "symptoms": {"chest pain": 1, "heartburn": 2, "regurgitation": 2,
                      "cough": 1, "sour taste": 1},
        "risk": {"obesity": 1},
        "labs": ["CBC"],
        "imaging": ["12-lead ECG (to exclude cardiac cause)"],
        "referral": ["Primary care", "Gastroenterology"],
        "followup": ["Empiric PPI trial", "Lifestyle modification"],
        "cpt": ["93000", "91010"],
        "rationale": "Burning retrosternal discomfort related to meals/position suggests "
                      "reflux, but is a diagnosis of exclusion after cardiac causes.",
    },
    {
        "name": "Community-Acquired Pneumonia",
        "icd10": "J18.9",
        "prior": 0.09,
        "symptoms": {"cough": 2, "fever": 2, "shortness of breath": 1,
                      "chest pain": 1, "sputum": 2, "chills": 1},
        "risk": {"smoking": 1, "copd": 1, "age>55": 1, "immunocompromised": 1},
        "labs": ["CBC with differential", "CRP / procalcitonin", "Blood cultures"],
        "imaging": ["Chest X-Ray"],
        "referral": ["Primary care / Hospital medicine"],
        "followup": ["CURB-65 risk score", "Empiric antibiotics per guideline"],
        "cpt": ["71046", "85025", "87040"],
        "rationale": "Productive cough with fever and focal dyspnea points to pneumonia; "
                      "confirm with chest radiograph and inflammatory markers.",
    },
    {
        "name": "Congestive Heart Failure Exacerbation",
        "icd10": "I50.9",
        "prior": 0.08,
        "symptoms": {"shortness of breath": 2, "leg swelling": 2, "orthopnea": 2,
                      "fatigue": 1, "weight gain": 1, "chest pain": 1},
        "risk": {"hypertension": 1, "diabetes": 1, "age>55": 1, "prior mi": 2},
        "labs": ["BNP / NT-proBNP", "BMP", "Troponin"],
        "imaging": ["Chest X-Ray", "Echocardiogram"],
        "referral": ["Cardiology"],
        "followup": ["Diuresis", "Daily weights and fluid restriction"],
        "cpt": ["83880", "71046", "93306"],
        "rationale": "Progressive dyspnea with orthopnea and edema suggests volume overload "
                      "from decompensated heart failure.",
    },
    {
        "name": "Sepsis / Systemic Infection",
        "icd10": "A41.9",
        "prior": 0.06,
        "symptoms": {"fever": 2, "tachycardia": 1, "confusion": 2, "shortness of breath": 1,
                      "chills": 1, "low blood pressure": 2},
        "risk": {"immunocompromised": 2, "age>55": 1, "diabetes": 1, "recent surgery": 1},
        "labs": ["CBC with differential", "Lactate", "Blood cultures x2", "BMP"],
        "imaging": ["Chest X-Ray"],
        "referral": ["Emergency Department"],
        "followup": ["Sepsis bundle (fluids, antibiotics within 1h)", "Source control"],
        "cpt": ["85025", "83605", "87040"],
        "rationale": "Fever with end-organ signs (confusion, hypotension) meets sepsis "
                      "screening — initiate time-critical bundle.",
    },
    {
        "name": "Acute Ischemic Stroke / TIA",
        "icd10": "I63.9",
        "prior": 0.06,
        "symptoms": {"weakness": 2, "facial droop": 2, "slurred speech": 2,
                      "confusion": 1, "vision loss": 2, "numbness": 1, "headache": 1},
        "risk": {"hypertension": 2, "diabetes": 1, "smoking": 1, "atrial fibrillation": 2,
                  "age>55": 1},
        "labs": ["Glucose", "CBC", "Coagulation panel"],
        "imaging": ["Non-contrast CT head", "CT angiography head/neck"],
        "referral": ["Stroke neurology", "Emergency Department"],
        "followup": ["Activate stroke code / assess tPA window", "NIH Stroke Scale"],
        "cpt": ["70450", "70496", "85025"],
        "rationale": "Sudden focal neurologic deficit is a stroke until imaging proves "
                      "otherwise — time-to-treatment is outcome-critical.",
    },
]

# Synonyms normalise free-text into the canonical tokens used above.
SYMPTOM_SYNONYMS = {
    "sob": "shortness of breath", "dyspnea": "shortness of breath",
    "breathlessness": "shortness of breath", "short of breath": "shortness of breath",
    "diaphoresis": "sweating", "sweats": "sweating", "perspiration": "sweating",
    "chest discomfort": "chest pain", "chest tightness": "chest pain",
    "palpitations": "tachycardia", "fast heart rate": "tachycardia",
    "coughing": "cough", "leg edema": "leg swelling", "swollen legs": "leg swelling",
    "passing out": "syncope", "fainting": "syncope", "acid reflux": "heartburn",
}
HISTORY_SYNONYMS = {
    "htn": "hypertension", "high blood pressure": "hypertension",
    "dm": "diabetes", "diabetes mellitus": "diabetes", "t2dm": "diabetes",
    "smoker": "smoking", "tobacco": "smoking", "tobacco use": "smoking",
    "high cholesterol": "hyperlipidemia", "dyslipidemia": "hyperlipidemia",
    "cad": "prior mi", "afib": "atrial fibrillation",
}


def _normalize(items: List[str], synonyms: Dict[str, str]) -> List[str]:
    out: List[str] = []
    for raw in items:
        t = raw.strip().lower()
        t = synonyms.get(t, t)
        if t and t not in out:
            out.append(t)
    return out


def parse_note(note: str) -> Dict[str, List[str]]:
    """Lightweight entity extraction from free text (demo Parser agent)."""
    text = (note or "").lower()
    symptoms, history, meds, allergies = [], [], [], []
    sym_vocab = {s for c in CONDITIONS for s in c["symptoms"]}
    sym_vocab |= set(SYMPTOM_SYNONYMS.keys())
    his_vocab = {r for c in CONDITIONS for r in c["risk"]}
    his_vocab |= set(HISTORY_SYNONYMS.keys())
    for term in sorted(sym_vocab, key=len, reverse=True):
        if term in text and term not in symptoms:
            symptoms.append(term)
    for term in sorted(his_vocab, key=len, reverse=True):
        if term in {"male", "age>55"}:
            continue
        if re.search(r"\b" + re.escape(term) + r"\b", text):
            history.append(term)
    m = re.search(r"\b(\d{1,3})\s*(?:y/?o|yo|year|years|yrs)\b", text)
    age = int(m.group(1)) if m else None
    sex = None
    if re.search(r"\b(male|man|m)\b", text):
        sex = "Male"
    if re.search(r"\b(female|woman|f)\b", text):
        sex = "Female"
    return {
        "symptoms": _normalize(symptoms, SYMPTOM_SYNONYMS),
        "history": _normalize(history, HISTORY_SYNONYMS),
        "medications": meds,
        "allergies": allergies,
        "age": age,
        "sex": sex,
    }


def _risk_tokens(age, sex, history: List[str]) -> List[str]:
    tokens = list(history)
    if age is not None and age >= 55:
        tokens.append("age>55")
    if sex and sex.lower().startswith("m"):
        tokens.append("male")
    return tokens


def score_conditions(symptoms: List[str], history: List[str], age, sex) -> List[Tuple[Dict, float]]:
    syms = _normalize(symptoms, SYMPTOM_SYNONYMS)
    risk_tokens = _normalize(_risk_tokens(age, sex, history), HISTORY_SYNONYMS)
    scored: List[Tuple[Dict, float]] = []
    for cond in CONDITIONS:
        s = cond["prior"]
        sym_hits = sum(w for k, w in cond["symptoms"].items() if k in syms)
        risk_hits = sum(w for k, w in cond["risk"].items() if k in risk_tokens)
        # symptoms dominate; risk factors modulate pre-test probability
        s += 0.16 * sym_hits + 0.06 * risk_hits
        # small penalty if zero symptom overlap (avoids spurious matches)
        if sym_hits == 0:
            s *= 0.25
        scored.append((cond, s))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored


def softmaxish(scores: List[float]) -> List[float]:
    """Squash raw scores into [0,1] confidences that look calibrated."""
    if not scores:
        return []
    top = max(scores)
    vals = [min(0.97, max(0.05, v / (top + 1e-6) * 0.92)) for v in scores]
    return vals


def assess_risk(top_cond: Dict, symptoms: List[str], history: List[str], age, sex) -> Dict:
    syms = _normalize(symptoms, SYMPTOM_SYNONYMS)
    risk_tokens = _normalize(_risk_tokens(age, sex, history), HISTORY_SYNONYMS)
    redflag_dx = {"Acute Coronary Syndrome", "Acute Myocardial Infarction",
                  "Pulmonary Embolism", "Aortic Dissection", "Sepsis / Systemic Infection",
                  "Acute Ischemic Stroke / TIA"}
    score = 0.15
    score += 0.18 if top_cond["name"] in redflag_dx else 0.0
    redflag_syms = {"chest pain", "shortness of breath", "sweating", "syncope",
                    "confusion", "low blood pressure", "facial droop", "slurred speech",
                    "tearing pain", "hemoptysis"}
    score += 0.08 * len(set(syms) & redflag_syms)
    score += 0.05 * len([r for r in risk_tokens if r in
                          {"hypertension", "diabetes", "smoking", "age>55",
                           "cancer", "immunocompromised", "prior mi"}])
    score = min(0.97, score)
    if score >= 0.6:
        level = "High"
    elif score >= 0.35:
        level = "Medium"
    else:
        level = "Low"
    factors = []
    if age is not None and age >= 55:
        factors.append(f"Age {age} (>55)")
    if sex:
        factors.append(sex)
    factors += [h.title() for h in history]
    flagged = sorted(set(syms) & redflag_syms)
    factors += [f"Red-flag symptom: {s}" for s in flagged]
    return {"level": level, "score": round(score, 2), "factors": factors[:8]}


def build_uncertainty_flags(ranked: List[Tuple[Dict, float]], symptoms: List[str]) -> List[str]:
    flags: List[str] = []
    syms = _normalize(symptoms, SYMPTOM_SYNONYMS)
    names = [c["name"] for c, _ in ranked[:5]]
    if "Pulmonary Embolism" in names and "leg swelling" not in syms:
        flags.append("Pulmonary embolism cannot be excluded without D-dimer / CT angiography.")
    if "Aortic Dissection" in names:
        flags.append("Aortic dissection is low-probability but high-mortality - confirm BP symmetry and imaging.")
    if len(ranked) >= 2 and abs(ranked[0][1] - ranked[1][1]) < 0.06:
        flags.append(
            f"Top two differentials ('{ranked[0][0]['name']}' vs "
            f"'{ranked[1][0]['name']}') are closely ranked - confirmatory testing advised."
        )
    if not syms:
        flags.append("Sparse symptom data — recommend a complete history and exam before acting.")
    return flags
