"""Pydantic request/response models — the public API contract.

The shape here is mirrored exactly by the React frontend, so changes must stay
in sync with `frontend/src/api.js` and the component prop expectations.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------- #
# Request                                                                      #
# --------------------------------------------------------------------------- #
class AnalyzeRequest(BaseModel):
    age: Optional[int] = Field(default=None, ge=0, le=120)
    sex: Optional[str] = None
    history: List[str] = Field(default_factory=list)
    symptoms: List[str] = Field(default_factory=list)
    medications: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    note: Optional[str] = Field(
        default=None,
        description="Free-text clinical note. If structured fields are empty, "
        "the Parser agent extracts entities from this text.",
    )


# --------------------------------------------------------------------------- #
# Response sub-models                                                          #
# --------------------------------------------------------------------------- #
class Demographics(BaseModel):
    age: Optional[int] = None
    sex: Optional[str] = None


class ExtractedEntities(BaseModel):
    demographics: Demographics = Field(default_factory=Demographics)
    symptoms: List[str] = Field(default_factory=list)
    history: List[str] = Field(default_factory=list)
    medications: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)


class EvidenceItem(BaseModel):
    source: str
    snippet: str
    score: float = Field(ge=0.0, le=1.0)
    icd_codes: List[str] = Field(default_factory=list)
    cpt_codes: List[str] = Field(default_factory=list)


class Diagnosis(BaseModel):
    name: str
    confidence: float = Field(ge=0.0, le=1.0)
    icd10: Optional[str] = None
    rationale: str = ""


class RiskAssessment(BaseModel):
    level: str  # High | Medium | Low
    score: float = Field(ge=0.0, le=1.0)
    factors: List[str] = Field(default_factory=list)


class Recommendations(BaseModel):
    labs: List[str] = Field(default_factory=list)
    imaging: List[str] = Field(default_factory=list)
    referral: List[str] = Field(default_factory=list)
    followup: List[str] = Field(default_factory=list)
    cpt_codes: List[str] = Field(default_factory=list)


class AgentStep(BaseModel):
    agent: str
    status: str = "complete"
    detail: str = ""
    duration_ms: int = 0


class GraphNode(BaseModel):
    id: str
    label: str
    type: str  # diagnosis | symptom | risk | code | history


class GraphEdge(BaseModel):
    source: str
    target: str
    label: str = ""


class KnowledgeGraph(BaseModel):
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Top-level response                                                          #
# --------------------------------------------------------------------------- #
class AnalyzeResponse(BaseModel):
    request_id: str
    mode: str  # demo | live
    provider: str
    created_at: str
    extracted: ExtractedEntities
    evidence: List[EvidenceItem] = Field(default_factory=list)
    diagnoses: List[Diagnosis] = Field(default_factory=list)
    risk: RiskAssessment
    recommendations: Recommendations
    explanation: str = ""
    uncertainty_flags: List[str] = Field(default_factory=list)
    summary: str = ""
    reasoning_trace: List[AgentStep] = Field(default_factory=list)
    knowledge_graph: KnowledgeGraph = Field(default_factory=KnowledgeGraph)


class SampleCase(AnalyzeRequest):
    name: str = "Sample patient"


def empty_response_dict() -> Dict[str, Any]:
    """A minimal valid response skeleton used by agents as they fill state."""
    return {
        "extracted": ExtractedEntities().model_dump(),
        "evidence": [],
        "diagnoses": [],
        "risk": RiskAssessment(level="Low", score=0.1, factors=[]).model_dump(),
        "recommendations": Recommendations().model_dump(),
        "explanation": "",
        "uncertainty_flags": [],
        "summary": "",
        "reasoning_trace": [],
        "knowledge_graph": KnowledgeGraph().model_dump(),
    }
