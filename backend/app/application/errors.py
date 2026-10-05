"""Erros da camada de aplicação ligados ao LLM. Mapeados para HTTP em `api/errors.py`."""
from __future__ import annotations

from app.domain.errors import DomainError


class LlmUnavailable(DomainError):
    """O provedor de LLM não respondeu (timeout, rede ou erro do servidor)."""

    code = "llm_unavailable"


class SignalUnparseable(DomainError):
    """O agente de sinais não devolveu um JSON válido mesmo depois de uma nova tentativa."""

    code = "unparseable"
