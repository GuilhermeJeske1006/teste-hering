"""Schemas pydantic da API (snake_case, datas ISO 8601), espelhando o contrato de api.md."""
from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.application.use_cases.catalog import PolicyValue

MAX_SIGNAL_CHARS = 2000
MAX_QUESTION_CHARS = 1000
MAX_HISTORY_ITEMS = 50
MAX_AUDIT_LIMIT = 500


class HealthOut(BaseModel):
    status: Literal["ok"] = "ok"
    llm: Literal["anthropic", "deterministic"]


class WeekOut(BaseModel):
    year: int
    iso_week: int
    start: date
    end: date


class SummaryOut(BaseModel):
    week: WeekOut
    total_lines: int
    within_policy: int
    open_exceptions: int
    transfers: int
    shadow_mode: bool


class SkuOut(BaseModel):
    id: str
    name: str
    category: str
    size_grid: str
    sizes: list[str]
    price: float
    is_basic: bool
    is_launch: bool


class StoreOut(BaseModel):
    id: str
    name: str
    ownership: str
    execution_mode: str


class PlanCellOut(BaseModel):
    size: str
    stock: int
    forecast_horizon: float
    target: int
    dc_allocated: int
    transfer_in: int
    transfer_out: int
    excess: int
    status: str


class PlanRowOut(BaseModel):
    store_id: str
    store_name: str
    execution_mode: str
    cells: list[PlanCellOut]
    total_movement: int


class PlanOut(BaseModel):
    sku: str
    sizes: list[str]
    rows: list[PlanRowOut]


class TransferOut(BaseModel):
    sku: str
    size: str
    source: str
    destination: str
    qty: int


class DecisionOut(BaseModel):
    action: str
    actor: str
    decided_at: datetime
    reason: str | None


class ExceptionOut(BaseModel):
    id: str
    rule: str
    severity: str
    title: str
    recommendation: str
    explanation: str
    facts: list[str]
    status: str
    decision: DecisionOut | None


class DecisionIn(BaseModel):
    action: Literal["approve", "reject", "undo"]
    reason: str | None = None


class AdjustmentOut(BaseModel):
    scope: str
    pct: float


class InterpretedOut(BaseModel):
    type: str
    event: str | None
    adjustments: list[AdjustmentOut]
    confidence: float


class SignalOut(BaseModel):
    id: str
    store: str
    author_role: str
    received_at: datetime
    text: str
    interpreted: InterpretedOut


class InterpretIn(BaseModel):
    text: str = Field(min_length=1, max_length=MAX_SIGNAL_CHARS)
    store: str | None = None


class InterpretOut(BaseModel):
    store: str | None
    type: str
    event: str | None
    adjustments: list[AdjustmentOut]
    confidence: float
    requires_human: bool
    reason: str


class ChatMessageIn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=MAX_SIGNAL_CHARS * 2)


class CopilotIn(BaseModel):
    question: str = Field(min_length=1, max_length=MAX_QUESTION_CHARS)
    history: list[ChatMessageIn] = Field(default_factory=list, max_length=MAX_HISTORY_ITEMS)
    focus_sku: str | None = None


class CopilotOut(BaseModel):
    answer: str
    sources: list[str]


class PolicyOut(BaseModel):
    key: str
    label: str
    description: str
    value: PolicyValue
    unit: str


class AuditOut(BaseModel):
    timestamp: datetime
    actor: str
    action: str
    subject: str
    detail: str | None
    exception_id: str | None
