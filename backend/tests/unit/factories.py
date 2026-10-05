"""Fábricas de objetos de domínio para testes unitários (sem I/O)."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from app.domain.model import (
    AllocationLine,
    DcStock,
    Event,
    LineStatus,
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

TOPS = ("PP", "P", "M", "G", "GG")


def make_policies(**overrides: object) -> Policies:
    base: dict[str, object] = dict(
        forecast_weights=(0.4, 0.3, 0.2, 0.1),
        horizon_weeks=2,
        cover_factor=1.25,
        min_display_basic=3,
        min_display_other=1,
        excess_trigger_factor=2.4,
        excess_keep_factor=1.5,
        auto_execution_max_value_brl=8000.0,
        launch_approval_weeks=2,
        stockout_alert_cover_weeks=1.0,
        transfer_min_source_cover_weeks=6.0,
        transfer_freight_brl=38.0,
        signal_max_auto_adjust_pct=20.0,
        seasonal_decline_pct=30.0,
        seasonal_min_cover_weeks=6.0,
        seasonal_min_stores=3,
        size_curve_deviation_pp=12.0,
        size_curve_min_units=30,
        size_curve_min_sizes=2,
        size_curve_weeks=8,
        repeated_rejection_count=2,
    )
    base.update(overrides)
    return Policies(**base)  # type: ignore[arg-type]


def make_store(store_id: str = "JOI", ownership: Ownership = Ownership.OWN, name: str | None = None) -> Store:
    return Store(store_id, name or f"Loja {store_id}", ownership, "Vale do Itajaí")


def make_sku(sku_id: str = "CB-PT", *, is_basic: bool = True, category: str = "tees", price: float = 59.9,
             launch_week: int | None = None, similar: tuple[str, ...] = (), sizes: tuple[str, ...] = TOPS) -> Sku:
    return Sku(sku_id, f"Produto {sku_id}", category, "tops", sizes, price, is_basic, launch_week, similar)


def make_line(store: str = "JOI", sku: str = "CB-PT", size: str = "M", *, stock: int = 0,
              weekly: float = 1.0, horizon: float = 2.0, **kw: object) -> AllocationLine:
    return AllocationLine(store, sku, size, stock=stock, weekly_forecast=weekly, forecast_horizon=horizon,
                          **kw)  # type: ignore[arg-type]


def make_signal(signal_id: str = "sig-1", store: str = "JOI", adjustments: tuple[SignalAdjustment, ...] = (),
                signal_type: SignalType = SignalType.LOCAL_EVENT, text: str = "texto") -> Signal:
    return Signal(signal_id, store, "franchisee", datetime(2026, 10, 3, 10, 0, tzinfo=timezone(timedelta(hours=-3))),
                  text, signal_type, None, adjustments, 0.8)


def make_week_data(*, stores: tuple[Store, ...] | None = None, skus: tuple[Sku, ...] | None = None,
                   sales: tuple[SalesRecord, ...] = (), reference_sales: tuple[ReferenceSale, ...] = (),
                   stock: tuple[StockRecord, ...] = (), dc_stock: tuple[DcStock, ...] = (),
                   events: tuple[Event, ...] = (), signals: tuple[Signal, ...] = (),
                   decision_history: tuple[PastDecision, ...] = (), policies: Policies | None = None,
                   iso_week: int = 41) -> WeekData:
    return WeekData(
        week=Week(2026, iso_week, date(2026, 10, 5), date(2026, 10, 11)),
        size_grids={"tops": TOPS},
        standard_size_curves={"tops": (0.08, 0.22, 0.33, 0.24, 0.13)},
        stores=stores if stores is not None else (make_store(),),
        skus=skus if skus is not None else (make_sku(),),
        sales=sales,
        reference_sales=reference_sales,
        stock=stock,
        dc_stock=dc_stock,
        events=events,
        signals=signals,
        decision_history=decision_history,
        policies=policies or make_policies(),
    )


__all__ = ["LineStatus", "make_line", "make_policies", "make_signal", "make_sku", "make_store", "make_week_data"]
