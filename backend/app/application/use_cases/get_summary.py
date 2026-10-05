"""Caso de uso: KPIs do resumo da semana (regras.md §10)."""
from __future__ import annotations

from dataclasses import dataclass

from app.application.exception_state import exceptions_with_decisions
from app.application.ports import DecisionReader, PlanReader
from app.domain.model import ExceptionStatus, LineKey, LineStatus, Week


@dataclass(frozen=True, slots=True)
class Summary:
    """Resumo da semana mostrado no topo da mesa."""

    week: Week
    total_lines: int
    within_policy: int
    open_exceptions: int
    transfers: int
    shadow_mode: bool = True


class GetSummary:
    """Conta linhas, linhas dentro da política, exceções abertas e transferências."""

    def __init__(self, plan: PlanReader, decisions: DecisionReader) -> None:
        self._plan, self._decisions = plan, decisions

    def execute(self) -> Summary:
        plan = self._plan.current()
        open_exceptions = [e for e in exceptions_with_decisions(self._plan, self._decisions)
                           if e.status is ExceptionStatus.OPEN]
        flagged: set[LineKey] = set().union(*(e.line_keys for e in open_exceptions))
        within = sum(1 for line in plan.lines if line.status is not LineStatus.BLOCKED and line.key not in flagged)
        return Summary(week=plan.data.week, total_lines=len(plan.lines), within_policy=within,
                       open_exceptions=len(open_exceptions), transfers=len(plan.transfers))
