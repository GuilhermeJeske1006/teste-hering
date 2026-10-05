"""Regra 5: curva de tamanhos vendida desvia da curva padrão."""
from __future__ import annotations

from app.domain import explain
from app.domain.model import AllocationException, Severity
from app.domain.rules.base import RuleContext, build_exception


class SizeCurveDeviationRule:
    """Uma exceção por loja × produto quando tamanhos suficientes desviam da curva padrão."""

    rule = "size_curve_deviation"
    severity = Severity.MEDIUM

    def evaluate(self, ctx: RuleContext) -> list[AllocationException]:
        p, cur = ctx.policies, ctx.current_week
        weeks = range(cur - p.size_curve_weeks, cur)
        out: list[AllocationException] = []
        for sku in ctx.skus_by_id():
            standard = ctx.data.standard_size_curves.get(sku.size_grid)
            if sku.is_launch or not standard:
                continue
            for store in ctx.stores_by_id():
                sold = [ctx.sales.total(store.id, sku.id, (size,), weeks) for size in sku.sizes]
                total = sum(sold)
                if total < p.size_curve_min_units:
                    continue
                rows = [(size, qty / total * 100, std * 100) for size, qty, std in zip(sku.sizes, sold, standard)]
                deviating = [r for r in rows if abs(r[1] - r[2]) >= p.size_curve_deviation_pp]
                if len(deviating) < p.size_curve_min_sizes:
                    continue
                text = explain.size_curve_deviation(sku, store, deviating, weeks=p.size_curve_weeks,
                                                    total_units=total, deviation_pp=p.size_curve_deviation_pp)
                out.append(build_exception(self, (store.id, sku.id), text,
                                           ctx.lines_for(store=store.id, sku=sku.id)))
        return out
