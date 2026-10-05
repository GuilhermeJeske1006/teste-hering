"""Regra 6: estoque negativo bloqueia a linha e pede correção do dado."""
from __future__ import annotations

from app.domain import explain
from app.domain.model import AllocationException, LineStatus, Severity
from app.domain.rules.base import RuleContext, build_exception


class NegativeStockRule:
    """Uma exceção por linha bloqueada: dado inconsistente bloqueia, não adivinha."""

    rule = "negative_stock"
    severity = Severity.MEDIUM

    def evaluate(self, ctx: RuleContext) -> list[AllocationException]:
        blocked = sorted((line for line in ctx.lines if line.status is LineStatus.BLOCKED), key=lambda l: l.key)
        return [
            build_exception(self, line.key,
                            explain.negative_stock(ctx.sku(line.sku), line.size, ctx.store(line.store), line.stock),
                            [line])
            for line in blocked
        ]
