"""The six clinical agents that make up the agentic workflow.

Each agent is a pure function `run(state) -> state` that reads and augments a
shared state dict. They run identically whether orchestrated by LangGraph
(LIVE/full install) or the built-in sequential fallback.
"""
from .parser import run as parser_agent
from .retrieval import run as retrieval_agent
from .diagnosis import run as diagnosis_agent
from .risk import run as risk_agent
from .recommendation import run as recommendation_agent
from .explanation import run as explanation_agent

AGENT_SEQUENCE = [
    ("Clinical Note Parser", parser_agent),
    ("Medical Knowledge Retrieval", retrieval_agent),
    ("Diagnostic Reasoning", diagnosis_agent),
    ("Risk Prediction", risk_agent),
    ("Clinical Recommendation", recommendation_agent),
    ("Explanation", explanation_agent),
]

__all__ = [
    "parser_agent",
    "retrieval_agent",
    "diagnosis_agent",
    "risk_agent",
    "recommendation_agent",
    "explanation_agent",
    "AGENT_SEQUENCE",
]
