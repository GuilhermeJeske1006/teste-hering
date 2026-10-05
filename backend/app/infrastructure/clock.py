"""Relógio do sistema (adaptador do port `Clock`)."""
from __future__ import annotations

from datetime import UTC, datetime


class SystemClock:
    """Hora atual em UTC; o domínio nunca chama `datetime.now()` diretamente."""

    def now(self) -> datetime:
        return datetime.now(UTC)
