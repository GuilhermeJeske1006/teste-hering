"""Adaptadores em memória: plano corrente (sempre) e repositórios para testes."""
from __future__ import annotations

from collections.abc import Mapping

from app.domain.model import AllocationPlan, AuditEvent, Decision


class InMemoryPlanStore:
    """Guarda o plano recalculado na inicialização; ele é derivado do seed, então não precisa de disco."""

    def __init__(self) -> None:
        self._plan: AllocationPlan | None = None

    def current(self) -> AllocationPlan:
        if self._plan is None:
            raise RuntimeError("O plano ainda não foi calculado.")
        return self._plan

    def save(self, plan: AllocationPlan) -> None:
        self._plan = plan


class InMemoryDecisionRepository:
    """Decisões em memória, para testes e demonstração."""

    def __init__(self) -> None:
        self._items: dict[str, Decision] = {}

    def get(self, exception_id: str) -> Decision | None:
        return self._items.get(exception_id)

    def all(self) -> Mapping[str, Decision]:
        return dict(self._items)

    def save(self, exception_id: str, decision: Decision) -> None:
        self._items[exception_id] = decision

    def delete(self, exception_id: str) -> None:
        self._items.pop(exception_id, None)


class InMemoryAuditLog:
    """Registro de auditoria append-only em memória."""

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    def append(self, event: AuditEvent) -> None:
        self._events.append(event)

    def recent(self, limit: int) -> list[AuditEvent]:
        return list(reversed(self._events))[:max(limit, 0)]
