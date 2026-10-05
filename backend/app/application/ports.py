"""Ports (interfaces) que a aplicação usa. Os adaptadores ficam em `infrastructure/`.

Ports pequenos e separados (segregação de interfaces): leitura e escrita de decisões são ports
diferentes, e o registro de auditoria só tem `append` e `recent`.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Protocol

from app.domain.model import AllocationPlan, AuditEvent, Decision, WeekData

Role = Literal["system", "user", "assistant"]


@dataclass(frozen=True, slots=True)
class Message:
    """Mensagem de uma conversa com o LLM."""

    role: Role
    content: str


class SeedSource(Protocol):
    """Fonte dos dados de entrada da semana (seed JSON hoje, ERP amanhã)."""

    def load(self) -> WeekData: ...


class PlanReader(Protocol):
    """Lê o plano corrente calculado pelo motor."""

    def current(self) -> AllocationPlan: ...


class PlanWriter(Protocol):
    """Guarda o plano recém-calculado."""

    def save(self, plan: AllocationPlan) -> None: ...


class DecisionReader(Protocol):
    """Lê as decisões humanas sobre exceções."""

    def get(self, exception_id: str) -> Decision | None: ...

    def all(self) -> Mapping[str, Decision]: ...


class DecisionWriter(Protocol):
    """Grava e remove (desfazer) decisões humanas."""

    def save(self, exception_id: str, decision: Decision) -> None: ...

    def delete(self, exception_id: str) -> None: ...


class AuditLog(Protocol):
    """Registro append-only de auditoria."""

    def append(self, event: AuditEvent) -> None: ...

    def recent(self, limit: int) -> list[AuditEvent]: ...


class LLMClient(Protocol):
    """Modelo de linguagem. Só interpreta e explica; nunca é fonte de número."""

    def complete(self, messages: Sequence[Message], *, max_tokens: int) -> str: ...


class Clock(Protocol):
    """Relógio injetável (o domínio nunca chama `datetime.now()`)."""

    def now(self) -> datetime: ...
