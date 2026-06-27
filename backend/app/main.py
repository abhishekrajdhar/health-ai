"""FastAPI application — the Agentic Clinical Decision Support API.

Routes
------
GET  /api/health              service + engine status
GET  /api/samples             demo patient cases for the UI dropdown
POST /api/analyze             run the 6-agent pipeline, return structured result
GET  /api/analyses            recent analyses (audit trail)
GET  /api/report/{id}/pdf     download a PDF clinical report
GET  /api/graph/{id}          knowledge-graph payload for a prior analysis
"""
from __future__ import annotations

import json
import os
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from . import db
from .config import get_settings
from .graph import orchestrator_name, run_pipeline
from .rag.retriever import active_backend
from .report import build_pdf
from .schemas import AnalyzeRequest, AnalyzeResponse

settings = get_settings()
app = FastAPI(
    title="Agentic Clinical Decision Support System",
    description="Multi-agent clinical reasoning over patient notes — built for the "
    "Cotiviti Healthcare AI Hackathon. Decision support only; not a medical device.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",")] if settings.CORS_ORIGINS != "*" else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


@app.on_event("startup")
def _startup() -> None:
    db.init_db()
    # warm the orchestrator + retriever so the first request is fast
    orchestrator_name()
    active_backend()


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "mode": settings.mode,
        "provider": settings.active_provider,
        "orchestrator": orchestrator_name(),
        "rag_backend": active_backend(),
        "version": app.version,
    }


@app.get("/api/samples")
def samples() -> List[dict]:
    path = os.path.join(_DATA_DIR, "samples.json")
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    payload = req.model_dump()
    if not (payload.get("symptoms") or payload.get("note") or payload.get("history")):
        raise HTTPException(
            status_code=422,
            detail="Provide at least symptoms, history, or a free-text clinical note.",
        )
    result = run_pipeline(payload)
    try:
        db.save_analysis(result)
    except Exception:
        pass  # persistence is best-effort; never block a result
    return result


@app.get("/api/analyses")
def analyses(limit: int = 25):
    return db.list_analyses(limit=limit)


@app.get("/api/graph/{request_id}")
def graph(request_id: str):
    data = db.get_analysis(request_id)
    if not data:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return data.get("knowledge_graph", {"nodes": [], "edges": []})


@app.get("/api/report/{request_id}/pdf")
def report_pdf(request_id: str):
    data = db.get_analysis(request_id)
    if not data:
        raise HTTPException(status_code=404, detail="Analysis not found")
    pdf_bytes = build_pdf(data)
    filename = f"cds_report_{request_id[:8]}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@app.get("/")
def root():
    return {
        "name": "Agentic Clinical Decision Support System",
        "docs": "/docs",
        "health": "/api/health",
    }
