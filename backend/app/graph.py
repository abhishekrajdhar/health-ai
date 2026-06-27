"""Agentic workflow orchestration.

Wires the six agents into a directed graph:

    Parser -> Retrieval -> Diagnosis -> Risk -> Recommendation -> Explanation

Uses LangGraph's StateGraph when available (full install); otherwise falls back
to an identical hand-rolled sequential runner so the pipeline always executes.
Both paths produce the same reasoning_trace.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from . import schemas
from .agents import (
    diagnosis_agent,
    explanation_agent,
    parser_agent,
    recommendation_agent,
    retrieval_agent,
    risk_agent,
)
from .config import get_settings

_USING_LANGGRAPH = False
_compiled = None


def _build_langgraph():
    """Compile a LangGraph StateGraph. Returns None if LangGraph isn't installed."""
    try:
        from langgraph.graph import END, START, StateGraph  # type: ignore
    except Exception:
        return None

    def node(fn):
        # LangGraph nodes return the (mutated) state dict.
        def _inner(state: Dict[str, Any]) -> Dict[str, Any]:
            return fn(state)

        return _inner

    graph = StateGraph(dict)
    graph.add_node("parser", node(parser_agent))
    graph.add_node("retrieval", node(retrieval_agent))
    graph.add_node("diagnosis", node(diagnosis_agent))
    graph.add_node("risk", node(risk_agent))
    graph.add_node("recommendation", node(recommendation_agent))
    graph.add_node("explanation", node(explanation_agent))

    graph.add_edge(START, "parser")
    graph.add_edge("parser", "retrieval")
    graph.add_edge("retrieval", "diagnosis")
    graph.add_edge("diagnosis", "risk")
    graph.add_edge("risk", "recommendation")
    graph.add_edge("recommendation", "explanation")
    graph.add_edge("explanation", END)
    return graph.compile()


def _sequential_run(state: Dict[str, Any]) -> Dict[str, Any]:
    for agent in (
        parser_agent,
        retrieval_agent,
        diagnosis_agent,
        risk_agent,
        recommendation_agent,
        explanation_agent,
    ):
        state = agent(state)
    return state


def _ensure_compiled():
    global _compiled, _USING_LANGGRAPH
    if _compiled is None:
        _compiled = _build_langgraph()
        _USING_LANGGRAPH = _compiled is not None
    return _compiled


def orchestrator_name() -> str:
    _ensure_compiled()
    return "langgraph" if _USING_LANGGRAPH else "sequential-fallback"


def run_pipeline(request: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the full agentic pipeline and return an API-shaped response dict."""
    settings = get_settings()
    state: Dict[str, Any] = {"request": request, "mode": settings.mode}
    state.update(schemas.empty_response_dict())

    compiled = _ensure_compiled()
    if compiled is not None:
        state = compiled.invoke(state)
    else:
        state = _sequential_run(state)

    response = {
        "request_id": str(uuid.uuid4()),
        "mode": settings.mode,
        "provider": settings.active_provider,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "extracted": state["extracted"],
        "evidence": state["evidence"],
        "diagnoses": state["diagnoses"],
        "risk": state["risk"],
        "recommendations": state["recommendations"],
        "explanation": state["explanation"],
        "uncertainty_flags": state["uncertainty_flags"],
        "summary": state["summary"],
        "reasoning_trace": state["reasoning_trace"],
        "knowledge_graph": state["knowledge_graph"],
    }
    return response
