"""Combina as exceções do plano com as decisões humanas gravadas."""
from __future__ import annotations

from app.application.ports import DecisionReader, PlanReader
from app.domain.model import AllocationException


def exceptions_with_decisions(plan: PlanReader, decisions: DecisionReader) -> list[AllocationException]:
    """Exceções do plano corrente, cada uma com o status vindo da decisão gravada."""
    decided = decisions.all()
    return [exc.with_decision(decided.get(exc.id)) for exc in plan.current().exceptions]
