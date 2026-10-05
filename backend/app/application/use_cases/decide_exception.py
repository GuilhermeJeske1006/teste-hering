"""Caso de uso: aprovar, rejeitar (com motivo) ou desfazer a decisão sobre uma exceção (regras.md §9)."""
from __future__ import annotations

from app.application.ports import AuditLog, Clock, DecisionReader, DecisionWriter, PlanReader
from app.domain.errors import AlreadyDecided, ExceptionNotFound, NotDecided, ReasonRequired
from app.domain.model import (
    REJECTION_REASONS,
    AllocationException,
    AuditEvent,
    Decision,
    DecisionAction,
)

PLANNER_ACTOR = "planejador"


class DecideException:
    """Registra a decisão humana e grava o evento na auditoria. Nada é executado (modo sombra)."""

    def __init__(self, plan: PlanReader, reader: DecisionReader, writer: DecisionWriter, audit: AuditLog,
                 clock: Clock) -> None:
        self._plan, self._reader, self._writer, self._audit, self._clock = plan, reader, writer, audit, clock

    def execute(self, exception_id: str, action: DecisionAction, reason: str | None = None,
                actor: str = PLANNER_ACTOR) -> AllocationException:
        exc = self._find(exception_id)
        current = self._reader.get(exception_id)
        if action is DecisionAction.UNDO:
            if current is None:
                raise NotDecided("Esta exceção ainda não foi decidida, então não há o que desfazer.")
            self._writer.delete(exception_id)
            self._record(exc, action, actor, f"Reabriu a exceção ({current.status.value})")
            return exc.with_decision(None)
        if current is not None:
            raise AlreadyDecided("Esta exceção já foi decidida. Desfaça a decisão antes de decidir de novo.")
        if action is DecisionAction.REJECT and reason not in REJECTION_REASONS:
            raise ReasonRequired("Escolha um motivo para rejeitar: " + "; ".join(REJECTION_REASONS) + ".")
        decision = Decision(action, actor, self._clock.now(),
                            reason if action is DecisionAction.REJECT else None)
        self._writer.save(exception_id, decision)
        self._record(exc, action, actor, decision.reason)
        return exc.with_decision(decision)

    def _find(self, exception_id: str) -> AllocationException:
        for exc in self._plan.current().exceptions:
            if exc.id == exception_id:
                return exc
        raise ExceptionNotFound("Exceção não encontrada.")

    def _record(self, exc: AllocationException, action: DecisionAction, actor: str, detail: str | None) -> None:
        self._audit.append(AuditEvent(timestamp=self._clock.now(), actor=actor, action=action.value,
                                      subject=exc.title, detail=detail, exception_id=exc.id))
