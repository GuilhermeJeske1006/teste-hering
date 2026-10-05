"""Rotas do agente de sinais e do copiloto (as únicas que usam LLM)."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_container
from app.api.schemas import (
    AdjustmentOut,
    CopilotIn,
    CopilotOut,
    InterpretedOut,
    InterpretIn,
    InterpretOut,
    SignalOut,
)
from app.application.ports import Message
from app.container import Container

router = APIRouter()
Deps = Annotated[Container, Depends(get_container)]


@router.get("/signals", response_model=list[SignalOut])
def signals(c: Deps) -> list[SignalOut]:
    return [SignalOut(id=s.id, store=s.store, author_role=s.author_role, received_at=s.received_at, text=s.text,
                      interpreted=InterpretedOut(
                          type=s.type.value, event=s.event, confidence=s.confidence,
                          adjustments=[AdjustmentOut(scope=a.scope, pct=a.pct) for a in s.adjustments]))
            for s in c.list_signals.execute()]


@router.post("/signals/interpret", response_model=InterpretOut)
def interpret(c: Deps, body: InterpretIn) -> InterpretOut:
    r = c.interpret_signal.execute(body.text, body.store)
    return InterpretOut(store=r.store, type=r.type.value, event=r.event, confidence=r.confidence,
                        requires_human=r.requires_human, reason=r.reason,
                        adjustments=[AdjustmentOut(scope=a.scope, pct=a.pct) for a in r.adjustments])


@router.post("/copilot/ask", response_model=CopilotOut)
def ask(c: Deps, body: CopilotIn) -> CopilotOut:
    history = [Message(m.role, m.content) for m in body.history]
    answer = c.ask_copilot.execute(body.question, history, body.focus_sku)
    return CopilotOut(answer=answer.answer, sources=list(answer.sources))
