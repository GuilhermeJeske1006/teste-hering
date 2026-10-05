"""Caso de uso: copiloto que explica as decisões da semana (regras.md §12)."""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from app.application.context_builder import ContextBuilder
from app.application.errors import LlmUnavailable
from app.application.ports import LLMClient, Message
from app.application.prompts import COPILOT_SYSTEM

MAX_HISTORY_TURNS = 8
COPILOT_MAX_TOKENS = 600


@dataclass(frozen=True, slots=True)
class CopilotAnswer:
    """Resposta do copiloto e as exceções citadas que existem de fato."""

    answer: str
    sources: tuple[str, ...]


class AskCopilot:
    """Responde perguntas com base só no contexto da mesa; nunca executa nada."""

    def __init__(self, llm: LLMClient, context: ContextBuilder) -> None:
        self._llm, self._context = llm, context

    def execute(self, question: str, history: Sequence[Message], focus_sku: str | None = None) -> CopilotAnswer:
        ctx = self._context.build(focus_sku)
        turns = [m for m in history if m.role in ("user", "assistant")][-MAX_HISTORY_TURNS:]
        messages = [Message("system", COPILOT_SYSTEM + ctx.text), *turns, Message("user", question)]
        answer = self._llm.complete(messages, max_tokens=COPILOT_MAX_TOKENS).strip()
        if not answer:
            raise LlmUnavailable("O copiloto não respondeu. Tente de novo em instantes.")
        return CopilotAnswer(answer, tuple(i for i in ctx.exception_ids if f"[{i}]" in answer or i in answer))
