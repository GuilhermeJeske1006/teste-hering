"""Adaptador do LLM da Anthropic via HTTP (httpx), sem SDK obrigatório (ADR 0006)."""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import httpx

from app.application.errors import LlmUnavailable
from app.application.ports import Message

API_URL = "https://api.anthropic.com"
API_VERSION = "2023-06-01"
DEFAULT_MODEL = "claude-haiku-4-5"
TIMEOUT_SECONDS = 30.0
RETRIES = 1
RETRYABLE_STATUS = {408, 409, 429, 500, 502, 503, 504, 529}


class AnthropicLLMClient:
    """Chama a Messages API com timeout de 30 s e uma nova tentativa; falhas viram `LlmUnavailable` (503)."""

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL, *, base_url: str = API_URL,
                 timeout: float = TIMEOUT_SECONDS, retries: int = RETRIES,
                 transport: httpx.BaseTransport | None = None) -> None:
        self._headers = {"x-api-key": api_key, "anthropic-version": API_VERSION, "content-type": "application/json"}
        self._model, self._base_url, self._timeout = model, base_url, timeout
        self._retries, self._transport = retries, transport

    def complete(self, messages: Sequence[Message], *, max_tokens: int) -> str:
        if not messages:
            raise ValueError("a conversa precisa de pelo menos uma mensagem")
        body: dict[str, Any] = {
            "model": self._model,
            "max_tokens": max_tokens,
            "messages": [{"role": m.role, "content": m.content} for m in messages if m.role != "system"],
        }
        system = "\n\n".join(m.content for m in messages if m.role == "system")
        if system:
            body["system"] = system
        with httpx.Client(base_url=self._base_url, timeout=self._timeout, transport=self._transport) as http:
            for _ in range(self._retries + 1):
                try:
                    response = http.post("/v1/messages", json=body, headers=self._headers)
                except httpx.HTTPError:
                    continue
                if response.status_code in RETRYABLE_STATUS:
                    continue
                if response.is_error:
                    break
                return _text_of(response.json())
        raise LlmUnavailable("O serviço de IA não respondeu agora. Tente de novo em instantes.")


def _text_of(payload: dict[str, Any]) -> str:
    blocks = payload.get("content") or []
    return "".join(b.get("text", "") for b in blocks if isinstance(b, dict) and b.get("type") == "text")
