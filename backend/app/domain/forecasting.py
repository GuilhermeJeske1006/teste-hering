"""Previsão de demanda (regras.md §2–3).

Cada previsor implementa `DemandForecaster`. Os uplifts (eventos e sinais) entram por um decorator,
então uma fonte nova de uplift é uma classe nova, sem mexer nos previsores.
"""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Protocol

from app.domain.model import Event, Policies, ReferenceSale, SalesRecord, Signal, Sku, WeekData

REFERENCE_WINDOW_WEEKS = 2
"""`qty_first_2_weeks` cobre duas semanas; dividir por isso dá a média semanal (regras.md §2)."""


@dataclass(frozen=True, slots=True)
class Forecast:
    """Previsão semanal e previsão do horizonte de uma linha."""

    weekly: float
    horizon: float


class DemandForecaster(Protocol):
    """Prevê a demanda de uma loja × produto × tamanho."""

    def forecast(self, store: str, sku: Sku, size: str) -> Forecast: ...


class UpliftSource(Protocol):
    """Fonte de ajuste percentual da previsão do horizonte (0.1 = +10%)."""

    def uplift(self, store: str, sku: Sku, size: str) -> float: ...


class SalesIndex:
    """Índice de vendas por loja × produto × tamanho × semana, para leituras rápidas."""

    def __init__(self, records: Iterable[SalesRecord]) -> None:
        self._by_line: dict[tuple[str, str, str], dict[int, int]] = defaultdict(dict)
        for r in records:
            self._by_line[(r.store, r.sku, r.size)][r.week] = r.qty

    def qty(self, store: str, sku: str, size: str, week: int) -> int:
        return self._by_line.get((store, sku, size), {}).get(week, 0)

    def total(self, store: str, sku: str, sizes: Iterable[str], weeks: Iterable[int]) -> int:
        week_list = list(weeks)
        return sum(self.qty(store, sku, size, w) for size in sizes for w in week_list)


class WeightedMovingAverageForecaster:
    """Média ponderada das últimas semanas, com o primeiro peso na semana mais recente."""

    def __init__(self, sales: SalesIndex, current_week: int, policies: Policies) -> None:
        self._sales = sales
        self._current_week = current_week
        self._weights = policies.forecast_weights
        self._horizon = policies.horizon_weeks

    def forecast(self, store: str, sku: Sku, size: str) -> Forecast:
        weekly = sum(w * self._sales.qty(store, sku.id, size, self._current_week - 1 - i)
                     for i, w in enumerate(self._weights))
        return Forecast(weekly, weekly * self._horizon)


class SimilarityLaunchForecaster:
    """Lançamentos: média das 2 primeiras semanas dos similares na mesma loja e tamanho."""

    def __init__(self, reference_sales: Sequence[ReferenceSale], policies: Policies) -> None:
        self._refs = reference_sales
        self._horizon = policies.horizon_weeks

    def forecast(self, store: str, sku: Sku, size: str) -> Forecast:
        refs = [r.qty_first_2_weeks for r in self._refs
                if r.store == store and r.size == size and r.reference_sku in sku.similar_skus]
        weekly = (sum(refs) / len(refs)) / REFERENCE_WINDOW_WEEKS if refs else 0.0
        return Forecast(weekly, weekly * self._horizon)


class LaunchAwareForecaster:
    """Escolhe o previsor de lançamento ou o de histórico conforme o produto."""

    def __init__(self, history: DemandForecaster, launch: DemandForecaster) -> None:
        self._history = history
        self._launch = launch

    def forecast(self, store: str, sku: Sku, size: str) -> Forecast:
        return (self._launch if sku.is_launch else self._history).forecast(store, sku, size)


class EventUplift:
    """Soma o uplift da categoria dos eventos da loja que se sobrepõem ao horizonte."""

    def __init__(self, events: Sequence[Event], current_week: int, policies: Policies) -> None:
        self._events = events
        self._first = current_week
        self._last = current_week + policies.horizon_weeks - 1

    def uplift(self, store: str, sku: Sku, size: str) -> float:
        total = 0.0
        for e in self._events:
            if store in e.stores and e.overlaps(self._first, self._last):
                total += e.uplift_by_category.get(sku.category, 0.0)
        return total


class SignalUplift:
    """Soma os ajustes de sinais da loja dentro do limite automático; os acima viram exceção."""

    def __init__(self, signals: Sequence[Signal], policies: Policies) -> None:
        self._signals = signals
        self._max_pct = policies.signal_max_auto_adjust_pct

    def uplift(self, store: str, sku: Sku, size: str) -> float:
        total = 0.0
        for signal in self._signals:
            if signal.store != store:
                continue
            for adj in signal.adjustments:
                if adj.pct <= self._max_pct and adj.applies_to(sku.id, size):
                    total += adj.pct / 100
        return total


class UpliftDecorator:
    """Aplica `(1 + Σ uplifts)` à previsão do horizonte de outro previsor."""

    def __init__(self, inner: DemandForecaster, sources: Sequence[UpliftSource]) -> None:
        self._inner = inner
        self._sources = sources

    def forecast(self, store: str, sku: Sku, size: str) -> Forecast:
        base = self._inner.forecast(store, sku, size)
        factor = 1.0
        for source in self._sources:
            factor += source.uplift(store, sku, size)
        return Forecast(base.weekly, base.horizon * factor)


def default_forecaster(data: WeekData) -> DemandForecaster:
    """Composição padrão: histórico ou lançamento, com uplift de eventos e de sinais."""
    cur, policies = data.week.iso_week, data.policies
    base = LaunchAwareForecaster(
        history=WeightedMovingAverageForecaster(SalesIndex(data.sales), cur, policies),
        launch=SimilarityLaunchForecaster(data.reference_sales, policies),
    )
    return UpliftDecorator(base, (EventUplift(data.events, cur, policies), SignalUplift(data.signals, policies)))
