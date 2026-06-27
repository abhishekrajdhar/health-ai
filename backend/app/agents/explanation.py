"""Agent 6 — Explanation Agent.

Produces a concise, clinician-facing explanation, explicit uncertainty flags and
a structured handoff summary. Also assembles the knowledge-graph view.

Note on Chain-of-Thought: reasoning is performed INTERNALLY (in the LLM or the
deterministic engine). Only the clinical bottom line is surfaced — hidden
step-by-step deliberation is never exposed to end users.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List

from .. import mock_engine
from ..prompts import EXPLANATION_PROMPT, SAFETY_PREAMBLE
from .base import llm_or_none, timed_step


def run(state: Dict[str, Any]) -> Dict[str, Any]:
    ex = state["extracted"]
    diagnoses = state.get("diagnoses", [])
    risk = state.get("risk", {})
    recs = state.get("recommendations", {})

    with timed_step(state, "Explanation") as step:
        explanation = _mock_explanation(ex, diagnoses, risk, recs)
        flags = mock_engine.build_uncertainty_flags(
            state.get("_ranked", []), ex.get("symptoms", [])
        )
        summary = _structured_summary(ex, diagnoses, risk, recs, flags)

        llm_out = llm_or_none(
            SAFETY_PREAMBLE,
            EXPLANATION_PROMPT.format(
                safety=SAFETY_PREAMBLE,
                case=json.dumps(
                    {
                        "entities": ex,
                        "diagnoses": diagnoses,
                        "risk": risk,
                        "recommendations": recs,
                    }
                ),
            ),
        )
        if llm_out:
            explanation = llm_out.get("explanation", explanation) or explanation
            if llm_out.get("uncertainty_flags"):
                flags = llm_out["uncertainty_flags"]
            summary = llm_out.get("summary", summary) or summary

        state["explanation"] = explanation
        state["uncertainty_flags"] = flags
        state["summary"] = summary
        state["knowledge_graph"] = _build_graph(ex, diagnoses, risk)
        step["detail"] = f"Generated explanation + {len(flags)} uncertainty flag(s)"
    return state


def _mock_explanation(ex, diagnoses, risk, recs) -> str:
    if not diagnoses:
        return "Insufficient structured data to form a differential. Recommend a complete history and examination."
    top = diagnoses[0]
    demo = ex.get("demographics", {})
    age = demo.get("age")
    sex = (demo.get("sex") or "").lower()
    who = f"{age}-year-old {sex}".strip() or "patient"
    syms = ", ".join(ex.get("symptoms", [])) or "the presenting complaint"
    hx = ", ".join(ex.get("history", [])) or "no significant history reported"
    labs = ", ".join(recs.get("labs", [])[:4]) or "targeted laboratory testing"
    imaging = ", ".join(recs.get("imaging", [])[:3]) or "appropriate imaging"
    return (
        f"This {who} presents with {syms} on a background of {hx}. The constellation "
        f"of findings, weighted against cardiac and other risk factors, makes "
        f"{top['name']} the leading consideration (~{int(top['confidence'] * 100)}% "
        f"relative confidence). The case is stratified as {risk.get('level', 'Unknown')} "
        f"acuity because of {', '.join(risk.get('factors', [])[:3]) or 'the overall clinical picture'}. "
        f"Recommended next steps include {labs} and {imaging}, with "
        f"{', '.join(recs.get('referral', [])[:2]) or 'appropriate specialty input'} to "
        f"confirm or exclude the leading diagnosis and the higher-risk alternatives. "
        f"This is decision support only and does not replace clinician judgment."
    )


def _structured_summary(ex, diagnoses, risk, recs, flags) -> str:
    demo = ex.get("demographics", {})
    lines: List[str] = []
    lines.append("STRUCTURED CLINICAL SUMMARY")
    lines.append("=" * 30)
    lines.append(
        f"Patient: {demo.get('age', '—')} y/o {demo.get('sex', '—')}"
    )
    lines.append(f"Symptoms: {', '.join(ex.get('symptoms', [])) or '—'}")
    lines.append(f"History: {', '.join(ex.get('history', [])) or '—'}")
    lines.append(f"Medications: {', '.join(ex.get('medications', [])) or '—'}")
    lines.append(f"Allergies: {', '.join(ex.get('allergies', [])) or 'NKDA'}")
    lines.append("")
    lines.append("ASSESSMENT")
    for i, d in enumerate(diagnoses, 1):
        lines.append(
            f"  {i}. {d['name']} [{d.get('icd10', '')}] — {int(d['confidence'] * 100)}% confidence"
        )
    lines.append(f"  Risk level: {risk.get('level', '—')} (score {risk.get('score', '—')})")
    lines.append("")
    lines.append("PLAN")
    if recs.get("labs"):
        lines.append(f"  Labs: {', '.join(recs['labs'])}")
    if recs.get("imaging"):
        lines.append(f"  Imaging: {', '.join(recs['imaging'])}")
    if recs.get("referral"):
        lines.append(f"  Referral: {', '.join(recs['referral'])}")
    if recs.get("followup"):
        lines.append(f"  Follow-up: {', '.join(recs['followup'])}")
    if recs.get("cpt_codes"):
        lines.append(f"  Suggested CPT: {', '.join(recs['cpt_codes'])}")
    if flags:
        lines.append("")
        lines.append("UNCERTAINTY / SAFETY FLAGS")
        for f in flags:
            lines.append(f"  ⚠ {f}")
    return "\n".join(lines)


def _build_graph(ex, diagnoses, risk) -> Dict[str, Any]:
    """Assemble a small knowledge graph linking the leading dx to symptoms,
    risk factors and codes for the UI visualization."""
    nodes: List[Dict[str, str]] = []
    edges: List[Dict[str, str]] = []
    if not diagnoses:
        return {"nodes": nodes, "edges": edges}
    top = diagnoses[0]
    center = "dx:" + top["name"]
    nodes.append({"id": center, "label": top["name"], "type": "diagnosis"})

    for s in ex.get("symptoms", [])[:6]:
        nid = "sym:" + s
        nodes.append({"id": nid, "label": s, "type": "symptom"})
        edges.append({"source": center, "target": nid, "label": "presents_with"})
    for h in ex.get("history", [])[:5]:
        nid = "hx:" + h
        nodes.append({"id": nid, "label": h, "type": "history"})
        edges.append({"source": center, "target": nid, "label": "risk_factor"})
    if top.get("icd10"):
        nid = "icd:" + top["icd10"]
        nodes.append({"id": nid, "label": top["icd10"], "type": "code"})
        edges.append({"source": center, "target": nid, "label": "coded_as"})
    # link alternative differentials
    for d in diagnoses[1:4]:
        nid = "dx:" + d["name"]
        nodes.append({"id": nid, "label": d["name"], "type": "diagnosis"})
        edges.append({"source": center, "target": nid, "label": "differential"})
    return {"nodes": nodes, "edges": edges}
