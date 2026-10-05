"""Regra 1: lançamento recente precisa de aprovação da grade inicial."""
from __future__ import annotations

from app.domain import explain
from app.domain.model import AllocationException, Severity
from app.domain.rules.base import RuleContext, build_exception, requires_launch_approval


class LaunchApprovalRule:
    """Lançamentos na janela de aprovação geram uma exceção crítica por produto."""

    rule = "launch_approval"
    severity = Severity.CRITICAL

    def evaluate(self, ctx: RuleContext) -> list[AllocationException]:
        out: list[AllocationException] = []
        for sku in ctx.skus_by_id():
            if not requires_launch_approval(sku, ctx.current_week, ctx.policies):
                continue
            lines = ctx.lines_for(sku=sku.id)
            need_by_store = {s.id: sum(line.need for line in lines if line.store == s.id)
                             for s in ctx.stores_by_id()}
            text = explain.launch_approval(sku, need_by_store, ctx.policies.launch_approval_weeks)
            out.append(build_exception(self, (sku.id,), text, lines))
        return out
