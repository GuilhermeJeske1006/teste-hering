"""Adaptadores SQLite (stdlib) para decisões e auditoria (ADR 0008).

Cada operação abre a própria conexão: simples e seguro com o threadpool do FastAPI.
O registro de auditoria é append-only: não existe update nem delete.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from app.domain.model import AuditEvent, Decision, DecisionAction

SCHEMA = """
CREATE TABLE IF NOT EXISTS decisions (
    exception_id TEXT PRIMARY KEY,
    action TEXT NOT NULL,
    actor TEXT NOT NULL,
    decided_at TEXT NOT NULL,
    reason TEXT
);
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    actor TEXT NOT NULL,
    action TEXT NOT NULL,
    subject TEXT NOT NULL,
    detail TEXT,
    exception_id TEXT
);
"""


class _SqliteDatabase:
    """Abre conexões para um arquivo e garante o schema."""

    def __init__(self, path: Path) -> None:
        self._path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as conn:
            conn.executescript(SCHEMA)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self._path)
        try:
            with conn:
                yield conn
        finally:
            conn.close()


class SqliteDecisionRepository:
    """Decisões humanas persistidas em SQLite, uma por exceção."""

    def __init__(self, path: Path) -> None:
        self._db = _SqliteDatabase(path)

    def get(self, exception_id: str) -> Decision | None:
        with self._db.connect() as conn:
            row = conn.execute("SELECT action, actor, decided_at, reason FROM decisions WHERE exception_id = ?",
                               (exception_id,)).fetchone()
        return _decision(row) if row else None

    def all(self) -> Mapping[str, Decision]:
        with self._db.connect() as conn:
            rows = conn.execute("SELECT exception_id, action, actor, decided_at, reason FROM decisions").fetchall()
        return {row[0]: _decision(row[1:]) for row in rows}

    def save(self, exception_id: str, decision: Decision) -> None:
        with self._db.connect() as conn:
            conn.execute(
                "INSERT INTO decisions (exception_id, action, actor, decided_at, reason) VALUES (?, ?, ?, ?, ?) "
                "ON CONFLICT(exception_id) DO UPDATE SET action = excluded.action, actor = excluded.actor, "
                "decided_at = excluded.decided_at, reason = excluded.reason",
                (exception_id, decision.action.value, decision.actor, decision.decided_at.isoformat(),
                 decision.reason))

    def delete(self, exception_id: str) -> None:
        with self._db.connect() as conn:
            conn.execute("DELETE FROM decisions WHERE exception_id = ?", (exception_id,))


class SqliteAuditLog:
    """Registro de auditoria append-only em SQLite."""

    def __init__(self, path: Path) -> None:
        self._db = _SqliteDatabase(path)

    def append(self, event: AuditEvent) -> None:
        with self._db.connect() as conn:
            conn.execute(
                "INSERT INTO audit_log (timestamp, actor, action, subject, detail, exception_id) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (event.timestamp.isoformat(), event.actor, event.action, event.subject, event.detail,
                 event.exception_id))

    def recent(self, limit: int) -> list[AuditEvent]:
        with self._db.connect() as conn:
            rows = conn.execute(
                "SELECT timestamp, actor, action, subject, detail, exception_id FROM audit_log "
                "ORDER BY id DESC LIMIT ?", (max(limit, 0),)).fetchall()
        return [AuditEvent(datetime.fromisoformat(r[0]), r[1], r[2], r[3], r[4], r[5]) for r in rows]


def _decision(row: tuple[str, str, str, str | None]) -> Decision:
    action, actor, decided_at, reason = row
    return Decision(DecisionAction(action), actor, datetime.fromisoformat(decided_at), reason)
