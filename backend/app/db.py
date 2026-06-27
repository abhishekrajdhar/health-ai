"""SQLite persistence for analysis results (audit trail + PDF retrieval)."""
from __future__ import annotations

import json
import sqlite3
from typing import Any, Dict, List, Optional

from .config import get_settings

_SCHEMA = """
CREATE TABLE IF NOT EXISTS analyses (
    request_id  TEXT PRIMARY KEY,
    created_at  TEXT NOT NULL,
    mode        TEXT,
    provider    TEXT,
    payload     TEXT NOT NULL  -- full JSON response
);
"""


_initialized = False


def _connect() -> sqlite3.Connection:
    global _initialized
    conn = sqlite3.connect(get_settings().SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    if not _initialized:
        # Idempotent self-heal: guarantees the table exists even if the FastAPI
        # startup hook didn't run (e.g. embedded/test usage).
        conn.executescript(_SCHEMA)
        _initialized = True
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.executescript(_SCHEMA)


def save_analysis(response: Dict[str, Any]) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO analyses (request_id, created_at, mode, provider, payload)"
            " VALUES (?, ?, ?, ?, ?)",
            (
                response["request_id"],
                response["created_at"],
                response.get("mode"),
                response.get("provider"),
                json.dumps(response),
            ),
        )


def get_analysis(request_id: str) -> Optional[Dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT payload FROM analyses WHERE request_id = ?", (request_id,)
        ).fetchone()
    return json.loads(row["payload"]) if row else None


def list_analyses(limit: int = 25) -> List[Dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT request_id, created_at, mode, provider, payload FROM analyses"
            " ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    out = []
    for r in rows:
        payload = json.loads(r["payload"])
        top = payload.get("diagnoses", [{}])
        out.append(
            {
                "request_id": r["request_id"],
                "created_at": r["created_at"],
                "mode": r["mode"],
                "top_diagnosis": top[0]["name"] if top else None,
                "risk": payload.get("risk", {}).get("level"),
            }
        )
    return out
