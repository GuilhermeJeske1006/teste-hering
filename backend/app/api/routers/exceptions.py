"""Rotas da fila de exceções, das decisões e do registro de auditoria."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_container
from app.api.schemas import MAX_AUDIT_LIMIT, AuditOut, DecisionIn, DecisionOut, ExceptionOut
from app.application.use_cases.get_audit_log import DEFAULT_AUDIT_LIMIT
from app.container import Container
from app.domain.model import AllocationException, DecisionAction, ExceptionStatus

router = APIRouter()
Deps = Annotated[Container, Depends(get_container)]


def to_out(e: AllocationException) -> ExceptionOut:
    d = e.decision
    decision = (DecisionOut(action=d.action.value, actor=d.actor, decided_at=d.decided_at, reason=d.reason)
                if d else None)
    return ExceptionOut(id=e.id, rule=e.rule, severity=e.severity.value, title=e.title,
                        recommendation=e.recommendation, explanation=e.explanation, facts=list(e.facts),
                        status=e.status.value, decision=decision)


@router.get("/exceptions", response_model=list[ExceptionOut])
def list_exceptions(c: Deps, status: ExceptionStatus | None = None) -> list[ExceptionOut]:
    return [to_out(e) for e in c.list_exceptions.execute(status)]


@router.post("/exceptions/{exception_id}/decision", response_model=ExceptionOut)
def decide(c: Deps, exception_id: str, body: DecisionIn) -> ExceptionOut:
    return to_out(c.decide_exception.execute(exception_id, DecisionAction(body.action), body.reason))


@router.get("/audit-log", response_model=list[AuditOut])
def audit_log(c: Deps, limit: Annotated[int, Query(ge=0, le=MAX_AUDIT_LIMIT)] = DEFAULT_AUDIT_LIMIT) -> list[AuditOut]:
    return [AuditOut(timestamp=e.timestamp, actor=e.actor, action=e.action, subject=e.subject, detail=e.detail,
                     exception_id=e.exception_id) for e in c.get_audit_log.execute(limit)]
