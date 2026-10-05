"""Motor de alocação: orquestra previsão, cálculo das linhas, rateio, transferências e regras.

O motor não conhece nenhuma regra específica: recebe a lista de `ExceptionRule` pronta.
"""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Sequence

from app.domain.allocation import DcRationer, LineCalculator, TransferPlanner
from app.domain.forecasting import DemandForecaster, SalesIndex, default_forecaster
from app.domain.model import AllocationLine, AllocationPlan, Transfer, WeekData
from app.domain.rules.base import ExceptionRule, RuleContext

ForecasterFactory = Callable[[WeekData], DemandForecaster]


class AllocationEngine:
    """Calcula o plano da semana de forma determinística a partir dos dados de entrada."""

    def __init__(self, rules: Sequence[ExceptionRule],
                 forecaster_factory: ForecasterFactory = default_forecaster) -> None:
        self._rules = tuple(rules)
        self._forecaster_factory = forecaster_factory

    def run(self, data: WeekData) -> AllocationPlan:
        lines = self._calculate_lines(data)
        lines, transfers = self._distribute(data, lines)
        ctx = RuleContext(data=data, lines=tuple(lines), transfers=tuple(transfers), sales=SalesIndex(data.sales))
        exceptions = tuple(exc for rule in self._rules for exc in rule.evaluate(ctx))
        return AllocationPlan(data=data, lines=ctx.lines, transfers=ctx.transfers, exceptions=exceptions)

    def _calculate_lines(self, data: WeekData) -> list[AllocationLine]:
        forecaster = self._forecaster_factory(data)
        calculator = LineCalculator(data.policies)
        skus = {k.id: k for k in data.skus}
        records = sorted(data.stock, key=lambda r: (r.store, r.sku, r.size))
        return [calculator.calculate(r.store, skus[r.sku], r.size, r.qty,
                                     forecaster.forecast(r.store, skus[r.sku], r.size))
                for r in records]

    @staticmethod
    def _distribute(data: WeekData, lines: list[AllocationLine]) -> tuple[list[AllocationLine], list[Transfer]]:
        dc = {(d.sku, d.size): d.qty for d in data.dc_stock}
        groups: dict[tuple[str, str], list[AllocationLine]] = defaultdict(list)
        for line in lines:
            groups[(line.sku, line.size)].append(line)
        rationer, planner = DcRationer(), TransferPlanner(data.policies)
        updated: dict[tuple[str, str, str], AllocationLine] = {}
        transfers: list[Transfer] = []
        for key in sorted(groups):
            rationed = rationer.ration(groups[key], dc.get(key, 0))
            planned, group_transfers = planner.plan(rationed)
            updated.update((line.key, line) for line in planned)
            transfers.extend(group_transfers)
        return [updated[line.key] for line in lines], transfers
