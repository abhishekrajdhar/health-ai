"""LLM provider abstraction.

A single `LLMClient` exposes `complete_json()` which returns a parsed dict. It
transparently supports:
  * OpenAI   (gpt-4o / gpt-4.1)  — JSON mode
  * Anthropic (Claude)          — JSON via tool-free prompting
  * DEMO     — no network; callers fall back to the deterministic mock engine.

Importing the heavy SDKs is deferred and guarded so the package imports cleanly
in a minimal (core-only) install.
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional

from .config import get_settings


class LLMClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.provider = self.settings.active_provider
        self._client = None

    # ------------------------------------------------------------------ #
    @property
    def is_live(self) -> bool:
        return self.provider in ("openai", "anthropic")

    def _ensure_client(self) -> None:
        if self._client is not None:
            return
        if self.provider == "openai":
            from openai import OpenAI  # type: ignore

            self._client = OpenAI(api_key=self.settings.OPENAI_API_KEY)
        elif self.provider == "anthropic":
            import anthropic  # type: ignore

            self._client = anthropic.Anthropic(api_key=self.settings.ANTHROPIC_API_KEY)

    # ------------------------------------------------------------------ #
    def complete_json(self, system: str, user: str) -> Dict[str, Any]:
        """Return a parsed JSON object from the model. Raises on hard failure so
        the caller can fall back to the deterministic engine."""
        if not self.is_live:
            raise RuntimeError("LLM not in live mode")
        self._ensure_client()
        if self.provider == "openai":
            return self._openai_json(system, user)
        return self._anthropic_json(system, user)

    # ------------------------------------------------------------------ #
    def _openai_json(self, system: str, user: str) -> Dict[str, Any]:
        resp = self._client.chat.completions.create(  # type: ignore[union-attr]
            model=self.settings.OPENAI_MODEL,
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user + "\n\nReturn ONLY valid JSON."},
            ],
        )
        return _safe_json(resp.choices[0].message.content or "{}")

    def _anthropic_json(self, system: str, user: str) -> Dict[str, Any]:
        resp = self._client.messages.create(  # type: ignore[union-attr]
            model=self.settings.ANTHROPIC_MODEL,
            max_tokens=1500,
            temperature=0.2,
            system=system + "\nRespond with ONLY a single valid JSON object.",
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(getattr(b, "text", "") for b in resp.content)
        return _safe_json(text)


def _safe_json(text: str) -> Dict[str, Any]:
    """Best-effort extraction of a JSON object from a model response."""
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    # strip ```json fences
    text = re.sub(r"^```[a-zA-Z]*", "", text).strip().strip("`").strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    # grab the outermost {...}
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass
    raise ValueError("Could not parse JSON from LLM response")


_singleton: Optional[LLMClient] = None


def get_llm() -> LLMClient:
    global _singleton
    if _singleton is None:
        _singleton = LLMClient()
    return _singleton
