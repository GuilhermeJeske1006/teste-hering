"""Caso de uso: fila de exceções em ordem de severidade."""
from __future__ import annotations

from app.application.exception_state import exceptions_with_decisions
from app.application.ports import DecisionReader, PlanReader
from app.domain.model import AllocationException, ExceptionStatus


class ListExceptions:
    """Lista as exceções com o status atual, filtrando por status quando pedido."""

    def __init__(self, plan: PlanReader, decisions: DecisionReader) -> None:
        self._plan, self._decisions = plan, decisions

    def execute(self, status: ExceptionStatus | None = None) -> list[AllocationException]:
        items = exceptions_with_decisions(self._plan, self._decisions)
        if status is not None:
            items = [e for e in items if e.status is status]
        return sorted(items, key=lambda e: e.severity.rank)
