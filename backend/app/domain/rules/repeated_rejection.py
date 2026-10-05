"""Regra 7: a mesma loja × produto foi rejeitada várias vezes."""
from __future__ import annotations

from collections import defaultdict

from app.domain import explain
from app.domain.model import AllocationException, DecisionAction, PastDecision, Severity
from app.domain.rules.base import RuleContext, build_exception


class RepeatedRejectionRule:
    """Uma exceção por loja × produto com rejeições acima do limite no histórico."""

    rule = "repeated_rejection"
    severity = Severity.LOW

    def evaluate(self, ctx: RuleContext) -> list[AllocationException]:
        rejections: dict[tuple[str, str], list[PastDecision]] = defaultdict(list)
        for d in ctx.data.decision_history:
            if d.action == DecisionAction.REJECT:
                rejections[(d.store, d.sku)].append(d)
        out: list[AllocationException] = []
        for (store_id, sku_id), decisions in sorted(rejections.items()):
            if len(decisions) < ctx.policies.repeated_rejection_count:
                continue
            text = explain.repeated_rejection(
                ctx.sku(sku_id), ctx.store(store_id), len(decisions),
                weeks=sorted({d.week for d in decisions}),
                reasons=[d.reason for d in decisions if d.reason],
            )
            out.append(build_exception(self, (store_id, sku_id), text, ctx.lines_for(store=store_id, sku=sku_id)))
        return out
