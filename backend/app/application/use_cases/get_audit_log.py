"""Caso de uso: registro de auditoria do mais novo para o mais antigo."""
from __future__ import annotations

from app.application.ports import AuditLog
from app.domain.model import AuditEvent

DEFAULT_AUDIT_LIMIT = 50


class GetAuditLog:
    """Lê os eventos mais recentes do registro append-only."""

    def __init__(self, audit: AuditLog) -> None:
        self._audit = audit

    def execute(self, limit: int = DEFAULT_AUDIT_LIMIT) -> list[AuditEvent]:
        return self._audit.recent(max(limit, 0))
