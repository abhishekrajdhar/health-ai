"""Seed clinical knowledge corpus for RAG.

A compact set of guideline-style passages, each tagged with ICD-10 and CPT codes.
In a production deployment this would be replaced by a curated, versioned vector
store of payer medical policies, ACC/AHA/IDSA guidelines, LCD/NCD coverage
determinations and CMS coding references.
"""
from __future__ import annotations

from typing import Dict, List

CLINICAL_CORPUS: List[Dict] = [
    {
        "source": "ACC/AHA Chest Pain Evaluation Guideline (2021)",
        "snippet": "Acute chest pain with diaphoresis, dyspnea and cardiac risk factors "
                    "should be triaged as possible acute coronary syndrome. Obtain a 12-lead "
                    "ECG within 10 minutes and high-sensitivity troponin; risk-stratify with "
                    "HEART score before disposition.",
        "icd_codes": ["I24.9", "I20.0", "I21.9"],
        "cpt_codes": ["93000", "84484"],
        "keywords": ["chest pain", "acs", "troponin", "ecg", "diaphoresis",
                      "sweating", "shortness of breath", "cardiac", "heart"],
    },
    {
        "source": "Wells Criteria & PE Diagnostic Pathway (ESC 2019)",
        "snippet": "For suspected pulmonary embolism, apply the Wells score and PERC rule. "
                    "Low probability with negative D-dimer excludes PE; otherwise proceed to "
                    "CT pulmonary angiography. Pleuritic chest pain, unexplained dyspnea, "
                    "tachycardia and unilateral leg swelling raise pretest probability.",
        "icd_codes": ["I26.99"],
        "cpt_codes": ["71275", "85379"],
        "keywords": ["pulmonary embolism", "pe", "d-dimer", "ct angiography",
                      "dyspnea", "shortness of breath", "leg swelling", "wells"],
    },
    {
        "source": "Aortic Dissection Detection (AHA Scientific Statement)",
        "snippet": "Acute aortic dissection presents with sudden severe tearing chest or back "
                    "pain, often in hypertensive patients. Check for pulse/BP differential and "
                    "obtain CT angiography. High mortality mandates rapid surgical consult.",
        "icd_codes": ["I71.00"],
        "cpt_codes": ["71275"],
        "keywords": ["aortic dissection", "tearing", "back pain", "chest pain",
                      "hypertension", "ct angiography"],
    },
    {
        "source": "IDSA/ATS Community-Acquired Pneumonia Guideline (2019)",
        "snippet": "Productive cough, fever and focal dyspnea suggest community-acquired "
                    "pneumonia. Confirm with chest radiograph; use CURB-65 or PSI for severity "
                    "and select empiric antibiotics accordingly.",
        "icd_codes": ["J18.9"],
        "cpt_codes": ["71046", "85025"],
        "keywords": ["pneumonia", "cough", "fever", "sputum", "chest x-ray",
                      "curb-65", "shortness of breath"],
    },
    {
        "source": "Surviving Sepsis Campaign Bundle (2021)",
        "snippet": "Suspected sepsis with fever, tachycardia, hypotension or altered mentation "
                    "requires the 1-hour bundle: measure lactate, draw blood cultures, give "
                    "broad-spectrum antibiotics and 30 mL/kg crystalloid for hypoperfusion.",
        "icd_codes": ["A41.9"],
        "cpt_codes": ["83605", "85025", "87040"],
        "keywords": ["sepsis", "fever", "lactate", "blood cultures", "hypotension",
                      "confusion", "infection"],
    },
    {
        "source": "AHA/ASA Acute Ischemic Stroke Guideline (2019)",
        "snippet": "Sudden focal neurologic deficit (facial droop, arm weakness, speech "
                    "difficulty) should activate a stroke code. Obtain non-contrast CT head "
                    "immediately and assess eligibility for IV thrombolysis within the time "
                    "window; compute the NIH Stroke Scale.",
        "icd_codes": ["I63.9"],
        "cpt_codes": ["70450", "70496"],
        "keywords": ["stroke", "facial droop", "weakness", "slurred speech",
                      "ct head", "tpa", "neurologic"],
    },
    {
        "source": "ACC/AHA Heart Failure Guideline (2022)",
        "snippet": "Decompensated heart failure presents with progressive dyspnea, orthopnea "
                    "and peripheral edema. Obtain BNP/NT-proBNP, chest radiograph and "
                    "echocardiography; initiate diuresis and optimise guideline-directed "
                    "medical therapy.",
        "icd_codes": ["I50.9"],
        "cpt_codes": ["83880", "93306"],
        "keywords": ["heart failure", "orthopnea", "edema", "leg swelling", "bnp",
                      "shortness of breath", "echocardiogram"],
    },
    {
        "source": "ACG GERD Clinical Guideline (2022)",
        "snippet": "Non-cardiac chest pain with heartburn and regurgitation related to meals "
                    "or position suggests gastroesophageal reflux disease. Exclude cardiac "
                    "causes first, then trial empiric proton-pump inhibitor therapy.",
        "icd_codes": ["K21.9"],
        "cpt_codes": ["91010"],
        "keywords": ["gerd", "heartburn", "regurgitation", "chest pain", "reflux",
                      "ppi"],
    },
    {
        "source": "CMS Risk Adjustment / HCC Coding Reference",
        "snippet": "Accurate ICD-10-CM capture of chronic conditions (diabetes, CHF, vascular "
                    "disease) drives HCC risk-adjustment factors. Documentation must support "
                    "MEAT criteria (Monitored, Evaluated, Assessed, Treated) for each condition.",
        "icd_codes": ["E11.9", "I50.9", "I25.10"],
        "cpt_codes": [],
        "keywords": ["risk adjustment", "hcc", "diabetes", "documentation", "coding",
                      "chronic"],
    },
    {
        "source": "Cotiviti Payment Integrity — Medical Necessity Policy (illustrative)",
        "snippet": "High-cost imaging and admissions require documented medical necessity "
                    "aligned to guideline criteria. Claims lacking guideline-concordant "
                    "indications are routed to clinical review for prepay validation.",
        "icd_codes": [],
        "cpt_codes": ["71275", "70496", "93306"],
        "keywords": ["medical necessity", "prior authorization", "utilization review",
                      "payment integrity", "claim", "imaging"],
    },
]
