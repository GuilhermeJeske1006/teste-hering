"""Regra 8: envio automático de loja própria acima do limite de valor."""
from __future__ import annotations

from app.domain import explain
from app.domain.model import AllocationException, Ownership, Severity
from app.domain.rules.base import RuleContext, build_exception, requires_launch_approval


class AutoExecutionLimitRule:
    """Uma exceção por loja própria cujo envio (fora de lançamentos em aprovação) passa do limite."""

    rule = "auto_execution_limit"
    severity = Severity.MEDIUM

    def evaluate(self, ctx: RuleContext) -> list[AllocationException]:
        p = ctx.policies
        launch_skus = {k.id for k in ctx.data.skus if requires_launch_approval(k, ctx.current_week, p)}
        prices = {k.id: k.price for k in ctx.data.skus}
        out: list[AllocationException] = []
        for store in ctx.stores_by_id():
            if store.ownership is not Ownership.OWN:
                continue
            lines = [line for line in ctx.lines_for(store=store.id)
                     if line.sku not in launch_skus and line.dc_allocated > 0]
            value = round(sum(line.dc_allocated * prices[line.sku] for line in lines), 2)
            if value > p.auto_execution_max_value_brl:
                text = explain.auto_execution_limit(store, value, p.auto_execution_max_value_brl)
                out.append(build_exception(self, (store.id,), text, lines))
        return out
