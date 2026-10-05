"""Caso de uso: plano por loja de um produto (aba Plano por loja)."""
from __future__ import annotations

from dataclasses import dataclass

from app.application.ports import PlanReader
from app.domain.errors import SkuNotFound
from app.domain.model import AllocationLine, ExecutionMode


@dataclass(frozen=True, slots=True)
class PlanRow:
    """Linha da tabela do plano: uma loja com uma célula por tamanho."""

    store_id: str
    store_name: str
    execution_mode: ExecutionMode
    cells: tuple[AllocationLine, ...]
    total_movement: int


@dataclass(frozen=True, slots=True)
class SkuPlan:
    """Plano de um produto em todas as lojas."""

    sku: str
    sizes: tuple[str, ...]
    rows: tuple[PlanRow, ...]


class GetPlanForSku:
    """Monta a grade loja × tamanho de um produto; o movimento é entradas menos saídas."""

    def __init__(self, plan: PlanReader) -> None:
        self._plan = plan

    def execute(self, sku_id: str) -> SkuPlan:
        plan = self._plan.current()
        sku = plan.data.sku(sku_id)
        if sku is None:
            raise SkuNotFound(f"Produto {sku_id} não encontrado.")
        lines = {line.key: line for line in plan.lines if line.sku == sku_id}
        rows = []
        for store in plan.data.stores:
            cells = tuple(lines[(store.id, sku_id, size)] for size in sku.sizes if (store.id, sku_id, size) in lines)
            if not cells:
                continue
            movement = sum(c.dc_allocated + c.transfer_in - c.transfer_out for c in cells)
            rows.append(PlanRow(store.id, store.name, store.execution_mode, cells, movement))
        return SkuPlan(sku=sku_id, sizes=sku.sizes, rows=tuple(rows))
