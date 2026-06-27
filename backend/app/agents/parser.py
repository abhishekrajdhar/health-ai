"""Agent 1 — Clinical Note Parser.

Extracts symptoms, history, medications and allergies from structured fields
and/or a free-text clinical note.
"""
from __future__ import annotations

import json
from typing import Any, Dict

from .. import mock_engine
from ..prompts import PARSER_PROMPT, SAFETY_PREAMBLE
from .base import llm_or_none, timed_step


def run(state: Dict[str, Any]) -> Dict[str, Any]:
    req = state["request"]
    with timed_step(state, "Clinical Note Parser") as step:
        symptoms = list(req.get("symptoms") or [])
        history = list(req.get("history") or [])
        meds = list(req.get("medications") or [])
        allergies = list(req.get("allergies") or [])
        age = req.get("age")
        sex = req.get("sex")
        note = req.get("note") or ""

        # If the structured fields are thin, mine the free-text note.
        if note and (len(symptoms) + len(history) < 2):
            llm_out = llm_or_none(
                SAFETY_PREAMBLE,
                PARSER_PROMPT.format(safety=SAFETY_PREAMBLE, payload=json.dumps(req)),
            )
            parsed = None
            if llm_out:
                parsed = llm_out
                demo = parsed.get("demographics", {}) or {}
                age = age or demo.get("age")
                sex = sex or demo.get("sex")
            else:
                parsed = mock_engine.parse_note(note)
                age = age or parsed.get("age")
                sex = sex or parsed.get("sex")
            symptoms = _merge(symptoms, parsed.get("symptoms", []))
            history = _merge(history, parsed.get("history", []))
            meds = _merge(meds, parsed.get("medications", []))
            allergies = _merge(allergies, parsed.get("allergies", []))

        symptoms = [s.strip() for s in symptoms if s and s.strip()]
        history = [h.strip() for h in history if h and h.strip()]

        state["extracted"] = {
            "demographics": {"age": age, "sex": sex},
            "symptoms": symptoms,
            "history": history,
            "medications": meds,
            "allergies": allergies,
        }
        step["detail"] = (
            f"Extracted {len(symptoms)} symptom(s), {len(history)} history item(s)"
        )
    return state


def _merge(a, b):
    out = list(a)
    seen = {x.lower() for x in out}
    for item in b or []:
        if item and item.lower() not in seen:
            out.append(item)
            seen.add(item.lower())
    return out
