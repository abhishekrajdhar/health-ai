"""Clinical evidence retriever.

Tries a real ChromaDB vector store (LIVE/full install) and transparently falls
back to a dependency-free keyword/overlap retriever so the demo always works.
Both paths return the same EvidenceItem-shaped dicts.
"""
from __future__ import annotations

import re
from typing import Dict, List

from ..config import get_settings
from .corpus import CLINICAL_CORPUS

_TOKEN = re.compile(r"[a-z0-9\-]+")


def _tokens(text: str) -> List[str]:
    return _TOKEN.findall((text or "").lower())


class KeywordRetriever:
    """Transparent BM25-lite overlap retriever (no external deps)."""

    backend = "keyword"

    def __init__(self) -> None:
        self.docs = CLINICAL_CORPUS

    def query(self, text: str, k: int = 4) -> List[Dict]:
        q = set(_tokens(text))
        scored = []
        for doc in self.docs:
            doc_tokens = set(_tokens(doc["snippet"])) | set(
                t for kw in doc["keywords"] for t in _tokens(kw)
            )
            kw_hits = sum(1 for kw in doc["keywords"] if kw in text.lower())
            overlap = len(q & doc_tokens)
            score = 2.0 * kw_hits + overlap
            if score > 0:
                scored.append((doc, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        if not scored:
            return []
        top = scored[0][1]
        out = []
        for doc, s in scored[:k]:
            out.append(
                {
                    "source": doc["source"],
                    "snippet": doc["snippet"],
                    "score": round(min(0.97, 0.55 + 0.42 * (s / (top + 1e-6))), 2),
                    "icd_codes": doc["icd_codes"],
                    "cpt_codes": doc["cpt_codes"],
                }
            )
        return out


class ChromaRetriever:
    """ChromaDB-backed semantic retriever. Built lazily; raises if unavailable."""

    backend = "chromadb"

    def __init__(self) -> None:
        import chromadb  # type: ignore
        from chromadb.config import Settings as ChromaSettings  # type: ignore

        cfg = get_settings()
        self.client = chromadb.PersistentClient(
            path=cfg.CHROMA_DIR, settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.col = self.client.get_or_create_collection("clinical_guidelines")
        if self.col.count() == 0:
            self.col.add(
                ids=[f"doc-{i}" for i in range(len(CLINICAL_CORPUS))],
                documents=[d["snippet"] for d in CLINICAL_CORPUS],
                metadatas=[
                    {
                        "source": d["source"],
                        "icd": ",".join(d["icd_codes"]),
                        "cpt": ",".join(d["cpt_codes"]),
                    }
                    for d in CLINICAL_CORPUS
                ],
            )

    def query(self, text: str, k: int = 4) -> List[Dict]:
        res = self.col.query(query_texts=[text or " "], n_results=k)
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        dists = res.get("distances", [[None]])[0]
        out = []
        for doc, meta, dist in zip(docs, metas, dists):
            score = 0.9 if dist is None else max(0.5, min(0.97, 1.0 - float(dist)))
            out.append(
                {
                    "source": meta.get("source", "Clinical guideline"),
                    "snippet": doc,
                    "score": round(score, 2),
                    "icd_codes": [c for c in meta.get("icd", "").split(",") if c],
                    "cpt_codes": [c for c in meta.get("cpt", "").split(",") if c],
                }
            )
        return out


_retriever = None
_active_backend = "keyword"


def get_retriever():
    """Return a singleton retriever, choosing the best available backend."""
    global _retriever, _active_backend
    if _retriever is not None:
        return _retriever
    cfg = get_settings()
    if cfg.RAG_BACKEND in ("auto", "chromadb"):
        try:
            _retriever = ChromaRetriever()
            _active_backend = "chromadb"
            return _retriever
        except Exception:
            pass  # graceful fallback
    _retriever = KeywordRetriever()
    _active_backend = "keyword"
    return _retriever


def active_backend() -> str:
    get_retriever()
    return _active_backend
