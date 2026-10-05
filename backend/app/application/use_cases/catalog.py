"""Casos de uso de leitura: produtos, lojas, transferências, sinais e políticas."""
from __future__ import annotations

from dataclasses import dataclass

from app.application.ports import PlanReader
from app.domain.model import Signal, Sku, Store, Transfer
from app.domain.policy_catalog import POLICY_CATALOG

PolicyValue = float | int | list[float]


@dataclass(frozen=True, slots=True)
class PolicyView:
    """Política com rótulo e unidade para a tela."""

    key: str
    label: str
    description: str
    value: PolicyValue
    unit: str


class ListSkus:
    """Produtos da semana."""

    def __init__(self, plan: PlanReader) -> None:
        self._plan = plan

    def execute(self) -> list[Sku]:
        return list(self._plan.current().data.skus)


class ListStores:
    """Lojas da rede com o modo de execução."""

    def __init__(self, plan: PlanReader) -> None:
        self._plan = plan

    def execute(self) -> list[Store]:
        return list(self._plan.current().data.stores)


class ListTransfers:
    """Transferências propostas pelo motor."""

    def __init__(self, plan: PlanReader) -> None:
        self._plan = plan

    def execute(self) -> list[Transfer]:
        return list(self._plan.current().transfers)


class ListSignals:
    """Sinais recebidos das lojas, já estruturados."""

    def __init__(self, plan: PlanReader) -> None:
        self._plan = plan

    def execute(self) -> list[Signal]:
        return list(self._plan.current().data.signals)


class ListPolicies:
    """Políticas em vigor, com rótulos em pt-BR."""

    def __init__(self, plan: PlanReader) -> None:
        self._plan = plan

    def execute(self) -> list[PolicyView]:
        policies = self._plan.current().data.policies
        views = []
        for meta in POLICY_CATALOG:
            raw = getattr(policies, meta.key)
            value: PolicyValue = list(raw) if isinstance(raw, tuple) else raw
            views.append(PolicyView(meta.key, meta.label, meta.description, value, meta.unit))
        return views
