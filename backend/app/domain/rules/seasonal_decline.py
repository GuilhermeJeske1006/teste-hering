"""Regra 4: queda sazonal de vendas com cobertura alta em várias lojas."""
from __future__ import annotations

from app.domain import explain
from app.domain.model import AllocationException, Severity, Sku
from app.domain.rules.base import RuleContext, build_exception


class SeasonalDeclineRule:
    """Uma exceção por produto quando lojas suficientes mostram fim de estação."""

    rule = "seasonal_decline"
    severity = Severity.MEDIUM

    def evaluate(self, ctx: RuleContext) -> list[AllocationException]:
        p = ctx.policies
        out: list[AllocationException] = []
        for sku in ctx.skus_by_id():
            if sku.is_launch:
                continue
            hits = [hit for store in ctx.stores_by_id() if (hit := self._store_hit(ctx, sku, store.id))]
            if len(hits) < p.seasonal_min_stores:
                continue
            text = explain.seasonal_decline(sku, hits, window_weeks=p.seasonal_window_weeks,
                                            min_decline_pct=p.seasonal_decline_pct,
                                            min_cover_weeks=p.seasonal_min_cover_weeks)
            stores = {store_id for store_id, _, _ in hits}
            lines = [line for line in ctx.lines_for(sku=sku.id) if line.store in stores]
            out.append(build_exception(self, (sku.id,), text, lines))
        return out

    @staticmethod
    def _store_hit(ctx: RuleContext, sku: Sku, store: str) -> tuple[str, float, float] | None:
        p, cur, window = ctx.policies, ctx.current_week, ctx.policies.seasonal_window_weeks
        previous = ctx.sales.total(store, sku.id, sku.sizes, range(cur - 2 * window, cur - window))
        last = ctx.sales.total(store, sku.id, sku.sizes, range(cur - window, cur))
        lines = ctx.lines_for(store=store, sku=sku.id)
        stock = sum(line.stock for line in lines)
        weekly = sum(line.weekly_forecast for line in lines)
        if not previous or not weekly:
            return None
        decline = (previous - last) / previous * 100
        cover = stock / weekly
        if decline >= p.seasonal_decline_pct and cover >= p.seasonal_min_cover_weeks:
            return (store, decline, cover)
        return None
