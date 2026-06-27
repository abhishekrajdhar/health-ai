"""Agent 4 — Risk Prediction Agent.

Classifies acuity as High / Medium / Low with a 0-1 score and the driving
factors, weighing red-flag symptoms, comorbidities and the leading differential.
"""
from __future__ import annotations

import json
from typing import Any, Dict

from .. import mock_engine
from ..prompts import RISK_PROMPT, SAFETY_PREAMBLE
from .base import llm_or_none, timed_step


def run(state: Dict[str, Any]) -> Dict[str, Any]:
    ex = state["extracted"]
    with timed_step(state, "Risk Prediction") as step:
        ranked = state.get("_ranked") or mock_engine.score_conditions(
            ex.get("symptoms", []),
            ex.get("history", []),
            ex["demographics"].get("age"),
            ex["demographics"].get("sex"),
        )
        top_cond = ranked[0][0] if ranked else {"name": "n/a"}
        risk = mock_engine.assess_risk(
            top_cond,
            ex.get("symptoms", []),
            ex.get("history", []),
            ex["demographics"].get("age"),
            ex["demographics"].get("sex"),
        )

        llm_out = llm_or_none(
            SAFETY_PREAMBLE,
            RISK_PROMPT.format(
                safety=SAFETY_PREAMBLE,
                entities=json.dumps(ex),
                diagnoses=json.dumps(state.get("diagnoses", [])),
            ),
        )
        if llm_out and llm_out.get("level") in ("High", "Medium", "Low"):
            risk = {
                "level": llm_out["level"],
                "score": round(float(llm_out.get("score", risk["score"])), 2),
                "factors": llm_out.get("factors", risk["factors"]) or risk["factors"],
            }

        state["risk"] = risk
        step["detail"] = f"Acuity classified as {risk['level']} (score {risk['score']})"
    return state
