"""Groq LLM client wrapper.

Uses the `groq` SDK directly (OpenAI-compatible, free tier). When no API key is
configured the client reports `available == False` and callers fall back to
deterministic templates, so the whole investigation pipeline still works end to
end without a key.
"""

from __future__ import annotations

import json
from typing import Any

import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class LLMClient:
    def __init__(self) -> None:
        self._client: Any | None = None
        self.model = settings.GROQ_MODEL
        self.fast_model = settings.GROQ_MODEL_FAST

    @property
    def available(self) -> bool:
        return bool(settings.GROQ_API_KEY)

    def _get(self):
        if self._client is None:
            from groq import AsyncGroq

            self._client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        return self._client

    async def complete(
        self,
        prompt: str,
        system: str = "You are an expert SOC security analyst.",
        *,
        fast: bool = False,
        max_tokens: int = 900,
        temperature: float = 0.2,
    ) -> str | None:
        """Return the model's text, or None if unavailable/errored."""
        if not self.available:
            return None
        try:
            client = self._get()
            resp = await client.chat.completions.create(
                model=self.fast_model if fast else self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return resp.choices[0].message.content
        except Exception as exc:
            logger.warning("llm_completion_failed", error=str(exc))
            return None

    async def complete_json(
        self,
        prompt: str,
        system: str = "You are an expert SOC security analyst. Respond with valid JSON only.",
        *,
        max_tokens: int = 1200,
    ) -> dict | None:
        """Return parsed JSON from the model, or None if unavailable/invalid."""
        if not self.available:
            return None
        try:
            client = self._get()
            resp = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            return json.loads(resp.choices[0].message.content or "{}")
        except Exception as exc:
            logger.warning("llm_json_failed", error=str(exc))
            return None


llm = LLMClient()
