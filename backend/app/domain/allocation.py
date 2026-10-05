"""Cálculo das linhas, rateio do CD e transferências (regras.md §4–6).

Cada classe tem uma responsabilidade: `LineCalculator` calcula alvo, necessidade e excesso;
`DcRationer` divide o estoque do CD; `TransferPlanner` cobre o que o CD não cobre.
"""
from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from dataclasses import replace

from app.domain.forecasting import Forecast
from app.domain.model import AllocationLine, LineStatus, Policies, Sku, Transfer


def cover_weeks(units: float, weekly_forecast: float) -> float:
    """Semanas de cobertura; sem previsão, a cobertura é infinita."""
    return units / weekly_forecast if weekly_forecast else math.inf


class LineCalculator:
    """Calcula alvo, necessidade e excesso de uma linha a partir do estoque e da previsão."""

    def __init__(self, policies: Policies) -> None:
        self._p = policies

    def calculate(self, store: str, sku: Sku, size: str, stock: int, forecast: Forecast) -> AllocationLine:
        base = AllocationLine(store, sku.id, size, stock=stock, weekly_forecast=forecast.weekly,
                              forecast_horizon=forecast.horizon)
        if stock < 0:
            return replace(base, status=LineStatus.BLOCKED)
        min_display = self._p.min_display_basic if sku.is_basic else self._p.min_display_other
        target = max(min_display, math.ceil(forecast.horizon * self._p.cover_factor))
        need = target - stock
        if need > 0:
            return replace(base, target=target, need=need)
        excess = 0
        if stock > forecast.horizon * self._p.excess_trigger_factor:
            excess = math.floor(stock - forecast.horizon * self._p.excess_keep_factor)
        return replace(base, target=target, excess=excess)


class DcRationer:
    """Divide o estoque do CD entre as linhas de um produto × tamanho."""

    def ration(self, lines: Sequence[AllocationLine], available: int) -> list[AllocationLine]:
        needing = [line for line in lines if line.need > 0]
        total = sum(line.need for line in needing)
        if total <= available:
            allocated = {line.store: line.need for line in needing}
        else:
            allocated = {line.store: math.floor(line.need * available / total) for line in needing}
            remainder = available - sum(allocated.values())
            by_shortfall = sorted(needing, key=lambda line: (-(line.need - allocated[line.store]), line.store))
            for line in by_shortfall[:remainder]:
                allocated[line.store] += 1
        return [replace(line, dc_allocated=allocated[line.store]) if line.store in allocated else line
                for line in lines]


class TransferPlanner:
    """Propõe transferências de lojas com excesso para lojas em risco de ruptura."""

    def __init__(self, policies: Policies) -> None:
        self._horizon = policies.horizon_weeks
        self._min_source_cover = policies.transfer_min_source_cover_weeks

    def plan(self, lines: Sequence[AllocationLine]) -> tuple[list[AllocationLine], list[Transfer]]:
        current = {line.store: line for line in lines}
        transfers: list[Transfer] = []
        for candidate in self._by_lost_sales(lines):
            dest = current[candidate.store]
            short = dest.short
            if short <= 0 or cover_weeks(dest.stock + dest.dc_allocated, dest.weekly_forecast) >= self._horizon:
                continue
            for src in self._sources(current.values()):
                qty = min(src.available_excess, short)
                current[src.store] = replace(src, transfer_out=src.transfer_out + qty)
                dest = current[dest.store] = replace(dest, transfer_in=dest.transfer_in + qty)
                transfers.append(Transfer(dest.sku, dest.size, src.store, dest.store, qty))
                short -= qty
                if short <= 0:
                    break
        return [current[line.store] for line in lines], transfers

    @staticmethod
    def _by_lost_sales(lines: Iterable[AllocationLine]) -> list[AllocationLine]:
        needing = [line for line in lines if line.need > 0]
        return sorted(needing, key=lambda l: (-(l.forecast_horizon - l.stock - l.dc_allocated), l.store))

    def _sources(self, lines: Iterable[AllocationLine]) -> list[AllocationLine]:
        eligible = [line for line in lines
                    if line.available_excess > 0 and line.weekly_forecast
                    and line.stock / line.weekly_forecast > self._min_source_cover]
        return sorted(eligible, key=lambda line: (-line.available_excess, line.store))
