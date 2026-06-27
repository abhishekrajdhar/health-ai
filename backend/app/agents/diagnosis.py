"""Agent 3 — Diagnostic Reasoning Agent.

Produces up to 5 ranked differential diagnoses with confidence scores. In LIVE
mode the LLM reasons over entities + retrieved evidence; the deterministic
engine provides a structured prior and the offline fallback.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List

from .. import mock_engine
from ..prompts import DIAGNOSIS_PROMPT, SAFETY_PREAMBLE
from .base import llm_or_none, timed_step


def run(state: Dict[str, Any]) -> Dict[str, Any]:
    ex = state["extracted"]
    with timed_step(state, "Diagnostic Reasoning") as step:
        ranked = mock_engine.score_conditions(
            ex.get("symptoms", []),
            ex.get("history", []),
            ex["demographics"].get("age"),
            ex["demographics"].get("sex"),
        )[:5]
        confidences = mock_engine.softmaxish([s for _, s in ranked])
        diagnoses: List[Dict[str, Any]] = []
        for (cond, _), conf in zip(ranked, confidences):
            diagnoses.append(
                {
                    "name": cond["name"],
                    "confidence": round(conf, 2),
                    "icd10": cond["icd10"],
                    "rationale": cond["rationale"],
                }
            )

        # LIVE: let the LLM refine ordering/confidence using retrieved evidence.
        llm_out = llm_or_none(
            SAFETY_PREAMBLE,
            DIAGNOSIS_PROMPT.format(
                safety=SAFETY_PREAMBLE,
                entities=json.dumps(ex),
                evidence=json.dumps(state.get("evidence", [])),
            ),
        )
        if llm_out and isinstance(llm_out.get("diagnoses"), list) and llm_out["diagnoses"]:
            refined = []
            for d in llm_out["diagnoses"][:5]:
                try:
                    refined.append(
                        {
                            "name": str(d["name"]),
                            "confidence": round(float(d.get("confidence", 0.5)), 2),
                            "icd10": d.get("icd10", ""),
                            "rationale": d.get("rationale", ""),
                        }
                    )
                except Exception:
                    continue
            if refined:
                diagnoses = refined

        state["diagnoses"] = diagnoses
        state["_ranked"] = ranked  # cached for risk/recommendation/uncertainty
        top = diagnoses[0]["name"] if diagnoses else "n/a"
        step["detail"] = f"Top differential: {top} ({len(diagnoses)} considered)"
    return state
