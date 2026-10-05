"""Fakes das ports para os testes unitários da camada de aplicação."""
from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from datetime import datetime, timezone

from app.application.errors import LlmUnavailable
from app.application.ports import Message
from app.domain.engine import AllocationEngine
from app.domain.model import AllocationPlan, AuditEvent, Decision, WeekData
from app.domain.rules import default_rules


class FakeSeed:
    def __init__(self, data: WeekData) -> None:
        self.data = data

    def load(self) -> WeekData:
        return self.data


class FakePlanStore:
    def __init__(self, plan: AllocationPlan | None = None) -> None:
        self.plan = plan

    def current(self) -> AllocationPlan:
        assert self.plan is not None
        return self.plan

    def save(self, plan: AllocationPlan) -> None:
        self.plan = plan


class FakeDecisions:
    def __init__(self) -> None:
        self.items: dict[str, Decision] = {}

    def get(self, exception_id: str) -> Decision | None:
        return self.items.get(exception_id)

    def all(self) -> Mapping[str, Decision]:
        return dict(self.items)

    def save(self, exception_id: str, decision: Decision) -> None:
        self.items[exception_id] = decision

    def delete(self, exception_id: str) -> None:
        self.items.pop(exception_id, None)


class FakeAudit:
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def append(self, event: AuditEvent) -> None:
        self.events.append(event)

    def recent(self, limit: int) -> list[AuditEvent]:
        return list(reversed(self.events))[:limit]


class FixedClock:
    def __init__(self, at: datetime | None = None) -> None:
        self.at = at or datetime(2026, 10, 5, 9, 0, tzinfo=timezone.utc)

    def now(self) -> datetime:
        return self.at


class ScriptedLLM:
    """Devolve respostas pré-definidas, na ordem, e guarda as mensagens recebidas."""

    def __init__(self, *replies: str | Exception | Callable[[Sequence[Message]], str]) -> None:
        self.replies = list(replies)
        self.calls: list[list[Message]] = []

    def complete(self, messages: Sequence[Message], *, max_tokens: int) -> str:
        self.calls.append(list(messages))
        reply = self.replies.pop(0) if self.replies else LlmUnavailable("sem resposta roteirizada")
        if isinstance(reply, Exception):
            raise reply
        return reply(messages) if callable(reply) else reply


def plan_for(data: WeekData) -> FakePlanStore:
    return FakePlanStore(AllocationEngine(default_rules()).run(data))
