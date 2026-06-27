"""Shared helpers for agents: timing, trace recording, and LLM-with-fallback."""
from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Any, Callable, Dict

from ..llm import get_llm


@contextmanager
def timed_step(state: Dict[str, Any], agent_name: str):
    """Context manager that appends a reasoning-trace entry with a duration.

    Usage:
        with timed_step(state, "Risk Prediction") as step:
            ... do work ...
            step["detail"] = "Classified as High"
    """
    start = time.perf_counter()
    step: Dict[str, Any] = {"agent": agent_name, "status": "complete", "detail": "", "duration_ms": 0}
    try:
        yield step
    except Exception as exc:  # pragma: no cover - defensive
        step["status"] = "error"
        step["detail"] = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        step["duration_ms"] = int((time.perf_counter() - start) * 1000)
        state.setdefault("reasoning_trace", []).append(step)


def llm_or_none(system: str, user: str) -> Dict[str, Any] | None:
    """Call the LLM in live mode; return None to signal 'use the mock path'.

    Any error degrades gracefully to the deterministic engine so a single flaky
    model call never breaks the pipeline.
    """
    llm = get_llm()
    if not llm.is_live:
        return None
    try:
        return llm.complete_json(system, user)
    except Exception:
        return None
