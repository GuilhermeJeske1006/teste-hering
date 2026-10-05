"""Fonte de dados da semana a partir do seed JSON (ADR 0008)."""
from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

from app.domain.model import (
    DcStock,
    Event,
    Ownership,
    PastDecision,
    Policies,
    ReferenceSale,
    SalesRecord,
    Signal,
    SignalAdjustment,
    SignalType,
    Sku,
    StockRecord,
    Store,
    Week,
    WeekData,
)


class SeedFormatError(ValueError):
    """O seed não tem o formato esperado ou referencia algo que não existe."""


class JsonSeedSource:
    """Lê o `seed.json` e devolve a fotografia da semana em objetos de domínio."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def load(self) -> WeekData:
        raw: dict[str, Any] = json.loads(self._path.read_text(encoding="utf-8"))
        try:
            data = _parse(raw)
        except (KeyError, TypeError, ValueError) as err:
            raise SeedFormatError(f"seed inválido em {self._path}: {err}") from err
        _check_references(data)
        return data


def _parse(raw: dict[str, Any]) -> WeekData:
    grids = {k: tuple(v) for k, v in raw["size_grids"].items()}
    cw = raw["current_week"]
    skus = []
    for k in raw["skus"]:
        if k["size_grid"] not in grids:
            raise SeedFormatError(f"produto {k['id']} usa a grade inexistente {k['size_grid']}")
        skus.append(Sku(k["id"], k["name"], k["category"], k["size_grid"], grids[k["size_grid"]], float(k["price"]),
                        bool(k["is_basic"]), k.get("launch_week"), tuple(k.get("similar_skus", ()))))
    return WeekData(
        week=Week(cw["year"], cw["iso_week"], date.fromisoformat(cw["start"]), date.fromisoformat(cw["end"])),
        size_grids=grids,
        standard_size_curves={k: tuple(v) for k, v in raw["standard_size_curves"].items()},
        stores=tuple(Store(s["id"], s["name"], Ownership(s["ownership"]), s["region"]) for s in raw["stores"]),
        skus=tuple(skus),
        sales=tuple(SalesRecord(r["store"], r["sku"], r["size"], r["week"], r["qty"]) for r in raw["sales_history"]),
        reference_sales=tuple(ReferenceSale(r["reference_sku"], r["store"], r["size"], r["qty_first_2_weeks"])
                              for r in raw["reference_sales"]),
        stock=tuple(StockRecord(r["store"], r["sku"], r["size"], r["qty"]) for r in raw["stock"]),
        dc_stock=tuple(DcStock(r["sku"], r["size"], r["qty"]) for r in raw["dc_stock"]),
        events=tuple(Event(e["id"], e["name"], tuple(e["stores"]), e["start_week"], e["end_week"],
                           dict(e["uplift_by_category"])) for e in raw["events"]),
        signals=tuple(_signal(s) for s in raw["signals"]),
        decision_history=tuple(PastDecision(d["week"], d["store"], d["sku"], d["action"], d["actor"], d.get("reason"))
                               for d in raw["decision_history"]),
        policies=Policies(**{**raw["policies"], "forecast_weights": tuple(raw["policies"]["forecast_weights"])}),
    )


def _signal(s: dict[str, Any]) -> Signal:
    it = s["interpreted"]
    return Signal(s["id"], s["store"], s["author_role"], datetime.fromisoformat(s["received_at"]), s["text"],
                  SignalType(it["type"]), it.get("event"),
                  tuple(SignalAdjustment(a["scope"], float(a["pct"])) for a in it["adjustments"]),
                  float(it["confidence"]))


def _check_references(data: WeekData) -> None:
    stores = {s.id for s in data.stores}
    sizes = {k.id: set(k.sizes) for k in data.skus}
    for r in data.stock:
        if r.store not in stores:
            raise SeedFormatError(f"estoque cita a loja inexistente {r.store}")
        if r.size not in sizes.get(r.sku, set()):
            raise SeedFormatError(f"estoque cita o produto/tamanho inexistente {r.sku} {r.size}")
    for s in data.signals:
        if s.store not in stores:
            raise SeedFormatError(f"sinal {s.id} cita a loja inexistente {s.store}")
