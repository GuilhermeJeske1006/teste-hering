"""Cenário pequeno e completo para os testes de aplicação: 3 lojas, 2 produtos e 3 exceções."""
from __future__ import annotations

from app.domain.model import (
    DcStock,
    Ownership,
    PastDecision,
    SalesRecord,
    SignalAdjustment,
    StockRecord,
    WeekData,
)
from tests.unit.factories import make_signal, make_sku, make_store, make_week_data


def small_week() -> WeekData:
    stores = (make_store("JOI", Ownership.OWN, "Joinville Garten"), make_store("BRQ", Ownership.FRANCHISE, "Brusque"),
              make_store("GAS", Ownership.FRANCHISE, "Gaspar"))
    skus = (make_sku("CB-PT", sizes=("M", "G")), make_sku("JJ-AZ", is_basic=False, category="jackets",
                                                         sizes=("M", "G"), price=299.9))
    sales = tuple(SalesRecord(s, "CB-PT", z, w, q) for s, q in (("JOI", 6), ("BRQ", 1), ("GAS", 2))
                  for z in ("M", "G") for w in range(33, 41))
    stock = (StockRecord("JOI", "CB-PT", "M", 1), StockRecord("JOI", "CB-PT", "G", 4),
             StockRecord("BRQ", "CB-PT", "M", 40), StockRecord("BRQ", "CB-PT", "G", 3),
             StockRecord("GAS", "CB-PT", "M", 3), StockRecord("GAS", "CB-PT", "G", -2),
             StockRecord("JOI", "JJ-AZ", "M", 2), StockRecord("BRQ", "JJ-AZ", "M", 1))
    signals = (make_signal("sig-1", "BRQ", (SignalAdjustment("all", 40),), text="Precisamos de 40% a mais de tudo"),)
    history = (PastDecision(39, "BRQ", "JJ-AZ", "reject", "franchisee", "não vende aqui"),
               PastDecision(40, "BRQ", "JJ-AZ", "reject", "franchisee", "não vende aqui"))
    return make_week_data(stores=stores, skus=skus, sales=sales, stock=stock,
                          dc_stock=(DcStock("CB-PT", "M", 2), DcStock("CB-PT", "G", 100)),
                          signals=signals, decision_history=history)
