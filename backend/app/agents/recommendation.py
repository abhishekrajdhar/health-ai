"""Agent 5 — Clinical Recommendation Agent.

Recommends the next clinical actions (labs, imaging, referral, follow-up) and
attaches realistic CPT codes, aligned to the leading differential and risk.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List

from .. import mock_engine
from ..prompts import RECOMMENDATION_PROMPT, SAFETY_PREAMBLE
from .base import llm_or_none, timed_step


def _dedupe(seq: List[str]) -> List[str]:
    out, seen = [], set()
    for x in seq:
        key = (x or "").strip().lower()
        if key and key not in seen:
            out.append(x.strip())
            seen.add(key)
    return out


def run(state: Dict[str, Any]) -> Dict[str, Any]:
    with timed_step(state, "Clinical Recommendation") as step:
        ranked = state.get("_ranked") or []
        # Merge work-ups from the top 2 differentials so we cover can't-miss dx.
        labs, imaging, referral, followup, cpt = [], [], [], [], []
        for cond, _ in ranked[:2]:
            labs += cond.get("labs", [])
            imaging += cond.get("imaging", [])
            referral += cond.get("referral", [])
            followup += cond.get("followup", [])
            cpt += cond.get("cpt", [])
        recs = {
            "labs": _dedupe(labs),
            "imaging": _dedupe(imaging),
            "referral": _dedupe(referral),
            "followup": _dedupe(followup),
            "cpt_codes": _dedupe(cpt),
        }

        llm_out = llm_or_none(
            SAFETY_PREAMBLE,
            RECOMMENDATION_PROMPT.format(
                safety=SAFETY_PREAMBLE,
                entities=json.dumps(state["extracted"]),
                diagnoses=json.dumps(state.get("diagnoses", [])),
                risk=json.dumps(state.get("risk", {})),
            ),
        )
        if llm_out:
            recs = {
                "labs": _dedupe(llm_out.get("labs", recs["labs"])),
                "imaging": _dedupe(llm_out.get("imaging", recs["imaging"])),
                "referral": _dedupe(llm_out.get("referral", recs["referral"])),
                "followup": _dedupe(llm_out.get("followup", recs["followup"])),
                "cpt_codes": _dedupe(llm_out.get("cpt_codes", recs["cpt_codes"])),
            }

        state["recommendations"] = recs
        step["detail"] = (
            f"{len(recs['labs'])} lab(s), {len(recs['imaging'])} imaging, "
            f"{len(recs['referral'])} referral(s)"
        )
    return state
