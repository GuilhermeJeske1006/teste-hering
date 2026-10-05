"""Entidades e objetos de valor do domínio de alocação e reposição de lojas.

Tudo aqui é imutável: mudar de estado significa criar uma nova instância com `dataclasses.replace`.
Nenhum número de regra de negócio mora neste módulo; os limites chegam por `Policies`.
"""
from __future__ import annotations

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from datetime import date, datetime
from enum import StrEnum

LineKey = tuple[str, str, str]
"""Chave de uma linha de decisão: (loja, produto, tamanho)."""


class Ownership(StrEnum):
    """Quem é dono do estoque da loja."""

    OWN = "own"
    FRANCHISE = "franchise"


class ExecutionMode(StrEnum):
    """Como a recomendação vira ação: envio (loja própria) ou sugestão de pedido (franquia)."""

    SHIP = "ship"
    ORDER_SUGGESTION = "order_suggestion"


class LineStatus(StrEnum):
    """Estado de uma linha: `blocked` quando o dado de entrada é inconsistente."""

    OK = "ok"
    BLOCKED = "blocked"


class Severity(StrEnum):
    """Severidade de uma exceção; a ordem da declaração é a ordem de prioridade."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @property
    def rank(self) -> int:
        return list(Severity).index(self)


class ExceptionStatus(StrEnum):
    """Estado de uma exceção na fila do planejador."""

    OPEN = "open"
    APPROVED = "approved"
    REJECTED = "rejected"


class DecisionAction(StrEnum):
    """Ações que o planejador pode tomar sobre uma exceção."""

    APPROVE = "approve"
    REJECT = "reject"
    UNDO = "undo"


class SignalType(StrEnum):
    """Tipos de sinal que o agente de sinais reconhece."""

    LOCAL_EVENT = "local_event"
    LOST_SALES = "lost_sales"
    SIZE_CURVE = "size_curve"
    STOCK_MISMATCH = "stock_mismatch"
    OTHER = "other"


REJECTION_REASONS: tuple[str, ...] = (
    "Conheço um fator que o modelo não vê",
    "Restrição comercial com o franqueado",
    "Dado de entrada errado",
    "Prefiro esperar mais uma semana",
)
"""Motivos aceitos para rejeitar uma exceção (regras.md §9)."""


@dataclass(frozen=True, slots=True)
class Week:
    """Semana ISO corrente do ciclo de alocação."""

    year: int
    iso_week: int
    start: date
    end: date


@dataclass(frozen=True, slots=True)
class Store:
    """Loja da rede; o tipo de propriedade define o modo de execução."""

    id: str
    name: str
    ownership: Ownership
    region: str

    @property
    def execution_mode(self) -> ExecutionMode:
        return ExecutionMode.SHIP if self.ownership is Ownership.OWN else ExecutionMode.ORDER_SUGGESTION


@dataclass(frozen=True, slots=True)
class Sku:
    """Produto com sua grade de tamanhos; lançamentos usam produtos similares como referência."""

    id: str
    name: str
    category: str
    size_grid: str
    sizes: tuple[str, ...]
    price: float
    is_basic: bool
    launch_week: int | None = None
    similar_skus: tuple[str, ...] = ()

    @property
    def is_launch(self) -> bool:
        return self.launch_week is not None


@dataclass(frozen=True, slots=True)
class SalesRecord:
    """Venda semanal de um tamanho em uma loja."""

    store: str
    sku: str
    size: str
    week: int
    qty: int


@dataclass(frozen=True, slots=True)
class ReferenceSale:
    """Venda das 2 primeiras semanas de um produto similar, base da previsão de lançamentos."""

    reference_sku: str
    store: str
    size: str
    qty_first_2_weeks: int


@dataclass(frozen=True, slots=True)
class StockRecord:
    """Estoque de loja informado pelo ERP (pode vir negativo quando o dado está errado)."""

    store: str
    sku: str
    size: str
    qty: int


@dataclass(frozen=True, slots=True)
class DcStock:
    """Estoque disponível no centro de distribuição."""

    sku: str
    size: str
    qty: int


@dataclass(frozen=True, slots=True)
class Event:
    """Evento local que altera a demanda das lojas participantes por categoria."""

    id: str
    name: str
    stores: tuple[str, ...]
    start_week: int
    end_week: int
    uplift_by_category: Mapping[str, float]

    def overlaps(self, first_week: int, last_week: int) -> bool:
        return self.start_week <= last_week and self.end_week >= first_week


@dataclass(frozen=True, slots=True)
class SignalAdjustment:
    """Ajuste percentual pedido por um sinal, com escopo `all`, `<SKU>` ou `<SKU>:<TAM>`."""

    scope: str
    pct: float

    def applies_to(self, sku: str, size: str) -> bool:
        return self.scope in ("all", sku, f"{sku}:{size}")


@dataclass(frozen=True, slots=True)
class Signal:
    """Mensagem de loja ou franqueado já estruturada pelo agente de sinais."""

    id: str
    store: str
    author_role: str
    received_at: datetime
    text: str
    type: SignalType
    event: str | None
    adjustments: tuple[SignalAdjustment, ...]
    confidence: float


@dataclass(frozen=True, slots=True)
class PastDecision:
    """Decisão de semanas anteriores, usada para detectar rejeições repetidas."""

    week: int
    store: str
    sku: str
    action: str
    actor: str
    reason: str | None


@dataclass(frozen=True, slots=True)
class Policies:
    """Limites definidos pelo planejador. Único lugar de onde saem os números das regras."""

    forecast_weights: tuple[float, ...]
    horizon_weeks: int
    cover_factor: float
    min_display_basic: int
    min_display_other: int
    excess_trigger_factor: float
    excess_keep_factor: float
    auto_execution_max_value_brl: float
    launch_approval_weeks: int
    stockout_alert_cover_weeks: float
    transfer_min_source_cover_weeks: float
    transfer_freight_brl: float
    signal_max_auto_adjust_pct: float
    seasonal_decline_pct: float
    seasonal_min_cover_weeks: float
    seasonal_min_stores: int
    size_curve_deviation_pp: float
    size_curve_min_units: int
    size_curve_min_sizes: int
    size_curve_weeks: int
    repeated_rejection_count: int
    seasonal_window_weeks: int = 3

    def __post_init__(self) -> None:
        if not self.forecast_weights:
            raise ValueError("forecast_weights não pode ser vazio")
        if self.horizon_weeks < 1:
            raise ValueError("horizon_weeks precisa ser pelo menos 1")
        if self.cover_factor <= 0 or self.excess_keep_factor <= 0 or self.excess_trigger_factor <= 0:
            raise ValueError("fatores de cobertura e excesso precisam ser positivos")
        if self.seasonal_window_weeks < 1 or self.size_curve_weeks < 1:
            raise ValueError("janelas de semanas precisam ser pelo menos 1")


@dataclass(frozen=True, slots=True)
class AllocationLine:
    """Linha de decisão loja × produto × tamanho, com o resultado do motor."""

    store: str
    sku: str
    size: str
    stock: int
    weekly_forecast: float
    forecast_horizon: float
    target: int = 0
    need: int = 0
    excess: int = 0
    dc_allocated: int = 0
    transfer_in: int = 0
    transfer_out: int = 0
    status: LineStatus = LineStatus.OK

    def __post_init__(self) -> None:
        quantities = (self.target, self.need, self.excess, self.dc_allocated, self.transfer_in, self.transfer_out)
        if any(q < 0 for q in quantities):
            raise ValueError(f"quantidades não podem ser negativas em {self.key}")
        if self.dc_allocated > self.need:
            raise ValueError(f"envio do CD maior que a necessidade em {self.key}")
        if self.transfer_out > self.excess:
            raise ValueError(f"transferência de saída maior que o excesso em {self.key}")
        if self.status is LineStatus.BLOCKED and (self.target or self.need or self.excess):
            raise ValueError(f"linha bloqueada precisa de alvo, necessidade e excesso zerados em {self.key}")

    @property
    def key(self) -> LineKey:
        return (self.store, self.sku, self.size)

    @property
    def short(self) -> int:
        """Quanto ainda falta depois do envio do CD."""
        return self.need - self.dc_allocated

    @property
    def available_excess(self) -> int:
        """Excesso que ainda pode sair da loja."""
        return self.excess - self.transfer_out


@dataclass(frozen=True, slots=True)
class Transfer:
    """Transferência proposta entre duas lojas do mesmo produto e tamanho."""

    sku: str
    size: str
    source: str
    destination: str
    qty: int

    def __post_init__(self) -> None:
        if self.qty <= 0:
            raise ValueError("transferência precisa de quantidade positiva")


@dataclass(frozen=True, slots=True)
class Decision:
    """Decisão humana sobre uma exceção."""

    action: DecisionAction
    actor: str
    decided_at: datetime
    reason: str | None = None

    @property
    def status(self) -> ExceptionStatus:
        return ExceptionStatus.APPROVED if self.action is DecisionAction.APPROVE else ExceptionStatus.REJECTED


@dataclass(frozen=True, slots=True)
class AllocationException:
    """Decisão que precisa de humano, já explicada em pt-BR a partir dos números do motor."""

    id: str
    rule: str
    severity: Severity
    title: str
    recommendation: str
    explanation: str
    facts: tuple[str, ...]
    line_keys: frozenset[LineKey] = frozenset()
    status: ExceptionStatus = ExceptionStatus.OPEN
    decision: Decision | None = None

    def with_decision(self, decision: Decision | None) -> AllocationException:
        status = decision.status if decision else ExceptionStatus.OPEN
        return replace(self, decision=decision, status=status)


@dataclass(frozen=True, slots=True)
class AuditEvent:
    """Evento append-only do registro de auditoria."""

    timestamp: datetime
    actor: str
    action: str
    subject: str
    detail: str | None = None
    exception_id: str | None = None


@dataclass(frozen=True, slots=True)
class WeekData:
    """Fotografia dos dados de entrada da semana (vinda do seed ou, no futuro, do ERP)."""

    week: Week
    size_grids: Mapping[str, tuple[str, ...]]
    standard_size_curves: Mapping[str, tuple[float, ...]]
    stores: tuple[Store, ...]
    skus: tuple[Sku, ...]
    sales: tuple[SalesRecord, ...]
    reference_sales: tuple[ReferenceSale, ...]
    stock: tuple[StockRecord, ...]
    dc_stock: tuple[DcStock, ...]
    events: tuple[Event, ...]
    signals: tuple[Signal, ...]
    decision_history: tuple[PastDecision, ...]
    policies: Policies

    def store(self, store_id: str) -> Store | None:
        return next((s for s in self.stores if s.id == store_id), None)

    def sku(self, sku_id: str) -> Sku | None:
        return next((k for k in self.skus if k.id == sku_id), None)


@dataclass(frozen=True, slots=True)
class AllocationPlan:
    """Resultado do motor para a semana: linhas, transferências e exceções abertas."""

    data: WeekData
    lines: tuple[AllocationLine, ...]
    transfers: tuple[Transfer, ...]
    exceptions: tuple[AllocationException, ...] = field(default=())


EXCEPTION_ID_LENGTH = 10


def exception_id(rule: str, *key: str) -> str:
    """Id estável e determinístico de uma exceção: sha1(regra + chave) truncado."""
    raw = f"{rule}:{'|'.join(key)}".encode()
    return hashlib.sha1(raw, usedforsecurity=False).hexdigest()[:EXCEPTION_ID_LENGTH]
