"""Rotas de catálogo: produtos, lojas, políticas, plano por produto e transferências."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_container
from app.api.schemas import PlanCellOut, PlanOut, PlanRowOut, PolicyOut, SkuOut, StoreOut, TransferOut
from app.container import Container

router = APIRouter()
Deps = Annotated[Container, Depends(get_container)]
FORECAST_DECIMALS = 2


@router.get("/skus", response_model=list[SkuOut])
def skus(c: Deps) -> list[SkuOut]:
    return [SkuOut(id=k.id, name=k.name, category=k.category, size_grid=k.size_grid, sizes=list(k.sizes),
                   price=k.price, is_basic=k.is_basic, is_launch=k.is_launch) for k in c.list_skus.execute()]


@router.get("/stores", response_model=list[StoreOut])
def stores(c: Deps) -> list[StoreOut]:
    return [StoreOut(id=s.id, name=s.name, ownership=s.ownership.value, execution_mode=s.execution_mode.value)
            for s in c.list_stores.execute()]


@router.get("/policies", response_model=list[PolicyOut])
def policies(c: Deps) -> list[PolicyOut]:
    return [PolicyOut(key=p.key, label=p.label, description=p.description, value=p.value, unit=p.unit)
            for p in c.list_policies.execute()]


@router.get("/transfers", response_model=list[TransferOut])
def transfers(c: Deps) -> list[TransferOut]:
    return [TransferOut(sku=t.sku, size=t.size, source=t.source, destination=t.destination, qty=t.qty)
            for t in c.list_transfers.execute()]


@router.get("/plan", response_model=PlanOut)
def plan(c: Deps, sku: Annotated[str, Query(min_length=1)]) -> PlanOut:
    p = c.get_plan_for_sku.execute(sku)
    rows = [PlanRowOut(
        store_id=r.store_id, store_name=r.store_name, execution_mode=r.execution_mode.value,
        total_movement=r.total_movement,
        cells=[PlanCellOut(size=x.size, stock=x.stock, forecast_horizon=round(x.forecast_horizon, FORECAST_DECIMALS),
                           target=x.target, dc_allocated=x.dc_allocated, transfer_in=x.transfer_in,
                           transfer_out=x.transfer_out, excess=x.excess, status=x.status.value) for x in r.cells],
    ) for r in p.rows]
    return PlanOut(sku=p.sku, sizes=list(p.sizes), rows=rows)
