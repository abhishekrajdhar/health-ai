"""Runtime configuration. Reads from environment / .env file.

The system is designed to run with ZERO configuration (DEMO MODE). Supplying an
OpenAI or Anthropic key flips it into LIVE MODE where the agents call a real LLM.
"""
from __future__ import annotations

import os
from functools import lru_cache

try:  # optional, only needed to load a .env file during local dev
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - dotenv is optional
    pass


class Settings:
    # --- LLM providers -----------------------------------------------------
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "").strip()
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "").strip()
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    # "auto" | "openai" | "anthropic" | "demo"
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "auto").lower().strip()

    # --- RAG / embeddings --------------------------------------------------
    # "auto" tries ChromaDB, then gracefully falls back to the keyword retriever.
    RAG_BACKEND: str = os.getenv("RAG_BACKEND", "auto").lower().strip()
    CHROMA_DIR: str = os.getenv("CHROMA_DIR", os.path.join(os.getcwd(), ".chroma"))
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "default").lower().strip()

    # --- persistence -------------------------------------------------------
    SQLITE_PATH: str = os.getenv("SQLITE_PATH", os.path.join(os.getcwd(), "cds.db"))

    # --- server ------------------------------------------------------------
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")

    @property
    def active_provider(self) -> str:
        """Resolve which engine will actually be used at request time."""
        if self.LLM_PROVIDER == "demo":
            return "demo"
        if self.LLM_PROVIDER == "openai" and self.OPENAI_API_KEY:
            return "openai"
        if self.LLM_PROVIDER == "anthropic" and self.ANTHROPIC_API_KEY:
            return "anthropic"
        if self.LLM_PROVIDER == "auto":
            if self.OPENAI_API_KEY:
                return "openai"
            if self.ANTHROPIC_API_KEY:
                return "anthropic"
        return "demo"

    @property
    def mode(self) -> str:
        return "demo" if self.active_provider == "demo" else "live"


@lru_cache
def get_settings() -> "Settings":
    return Settings()
