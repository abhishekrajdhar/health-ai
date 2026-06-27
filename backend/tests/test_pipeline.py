"""Smoke tests for the agentic pipeline. Run with: pytest -q  (from backend/).

These exercise DEMO MODE only (no network), so they pass in CI with zero config.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.graph import run_pipeline  # noqa: E402


CARDIAC_CASE = {
    "age": 62,
    "sex": "Male",
    "history": ["Hypertension", "Diabetes", "Smoking"],
    "symptoms": ["Chest pain", "Shortness of breath", "Sweating"],
    "medications": [],
    "allergies": [],
    "note": "",
}


def test_pipeline_runs_all_six_agents():
    result = run_pipeline(CARDIAC_CASE)
    agents = [s["agent"] for s in result["reasoning_trace"]]
    assert agents == [
        "Clinical Note Parser",
        "Medical Knowledge Retrieval",
        "Diagnostic Reasoning",
        "Risk Prediction",
        "Clinical Recommendation",
        "Explanation",
    ]


def test_cardiac_case_ranks_acs_first_and_high_risk():
    result = run_pipeline(CARDIAC_CASE)
    assert result["diagnoses"], "expected differential diagnoses"
    top = result["diagnoses"][0]
    assert "Coronary" in top["name"] or "Myocardial" in top["name"]
    assert top["confidence"] >= 0.7
    assert result["risk"]["level"] == "High"
    # differential should surface PE / GERD / dissection as alternatives
    names = " ".join(d["name"] for d in result["diagnoses"])
    assert "Pulmonary Embolism" in names


def test_recommendations_and_codes_present():
    result = run_pipeline(CARDIAC_CASE)
    recs = result["recommendations"]
    assert any("Troponin" in l for l in recs["labs"])
    assert recs["cpt_codes"], "expected CPT codes"
    assert result["evidence"], "expected retrieved evidence"
    assert result["explanation"]
    assert result["summary"]
    assert result["knowledge_graph"]["nodes"]


def test_freetext_only_extraction():
    case = {"note": "71 yo male with COPD, productive cough, fever and shortness of breath."}
    result = run_pipeline(case)
    syms = [s.lower() for s in result["extracted"]["symptoms"]]
    assert any("cough" in s for s in syms)
    assert result["diagnoses"]


if __name__ == "__main__":
    for fn in [
        test_pipeline_runs_all_six_agents,
        test_cardiac_case_ranks_acs_first_and_high_risk,
        test_recommendations_and_codes_present,
        test_freetext_only_extraction,
    ]:
        fn()
        print(f"PASS  {fn.__name__}")
    print("\nAll smoke tests passed.")
