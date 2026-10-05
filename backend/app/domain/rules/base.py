"""Contrato das regras de exceção e o contexto que o motor entrega a elas.

Uma regra nova é um arquivo novo que implementa `ExceptionRule` e uma linha em `default_rules()`.
O motor nunca pergunta "que regra é esta?" (aberto/fechado).
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol

from app.domain.explain import Explanation
from app.domain.forecasting import SalesIndex
from app.domain.model import (
    AllocationException,
    AllocationLine,
    LineKey,
    Policies,
    Severity,
    Sku,
    Store,
    Transfer,
    WeekData,
    exception_id,
)


@dataclass(frozen=True, slots=True)
class RuleContext:
    """Tudo que uma regra pode consultar: dados da semana, linhas calculadas e transferências."""

    data: WeekData
    lines: tuple[AllocationLine, ...]
    transfers: tuple[Transfer, ...]
    sales: SalesIndex

    @property
    def policies(self) -> Policies:
        return self.data.policies

    @property
    def current_week(self) -> int:
        return self.data.week.iso_week

    def lines_for(self, store: str | None = None, sku: str | None = None,
                  size: str | None = None) -> list[AllocationLine]:
        return [line for line in self.lines
                if (store is None or line.store == store) and (sku is None or line.sku == sku)
                and (size is None or line.size == size)]

    def stores_by_id(self) -> list[Store]:
        return sorted(self.data.stores, key=lambda s: s.id)

    def skus_by_id(self) -> list[Sku]:
        return sorted(self.data.skus, key=lambda k: k.id)

    def store(self, store_id: str) -> Store:
        found = self.data.store(store_id)
        if found is None:
            raise KeyError(f"loja desconhecida: {store_id}")
        return found

    def sku(self, sku_id: str) -> Sku:
        found = self.data.sku(sku_id)
        if found is None:
            raise KeyError(f"produto desconhecido: {sku_id}")
        return found


class ExceptionRule(Protocol):
    """Regra que transforma o resultado do motor em exceções para o planejador."""

    rule: str
    severity: Severity

    def evaluate(self, ctx: RuleContext) -> list[AllocationException]: ...


def requires_launch_approval(sku: Sku, current_week: int, policies: Policies) -> bool:
    """Lançamentos dentro da janela de aprovação passam pelo planejador (regras.md §8.1)."""
    return sku.launch_week is not None and current_week - sku.launch_week < policies.launch_approval_weeks


def build_exception(rule: ExceptionRule, key: Iterable[str], text: Explanation,
                    lines: Iterable[AllocationLine]) -> AllocationException:
    """Monta a exceção com id determinístico e as linhas que ela referencia."""
    keys: frozenset[LineKey] = frozenset(line.key for line in lines)
    return AllocationException(
        id=exception_id(rule.rule, *key), rule=rule.rule, severity=rule.severity, title=text.title,
        recommendation=text.recommendation, explanation=text.explanation, facts=text.facts, line_keys=keys,
    )
