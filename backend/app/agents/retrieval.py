"""Agent 2 — Medical Knowledge Retrieval (RAG).

Builds a retrieval query from the extracted entities and pulls guideline
passages + ICD/CPT codes from the vector store (or keyword fallback).
"""
from __future__ import annotations

from typing import Any, Dict

from ..rag.retriever import active_backend, get_retriever
from .base import timed_step


def run(state: Dict[str, Any]) -> Dict[str, Any]:
    ex = state["extracted"]
    with timed_step(state, "Medical Knowledge Retrieval") as step:
        query_parts = list(ex.get("symptoms", [])) + list(ex.get("history", []))
        query = ", ".join(query_parts) or (state["request"].get("note") or "general")
        retriever = get_retriever()
        evidence = retriever.query(query, k=4)
        state["evidence"] = evidence
        step["detail"] = (
            f"Retrieved {len(evidence)} guideline passage(s) via {active_backend()} backend"
        )
    return state
