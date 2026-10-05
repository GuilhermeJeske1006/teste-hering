"""Regra 3: sinal pede ajuste acima do limite automático."""
from __future__ import annotations

from app.domain import explain
from app.domain.model import AllocationException, Severity
from app.domain.rules.base import RuleContext, build_exception


class SignalDivergenceRule:
    """Uma exceção por ajuste de sinal acima de `signal_max_auto_adjust_pct`."""

    rule = "signal_divergence"
    severity = Severity.HIGH

    def evaluate(self, ctx: RuleContext) -> list[AllocationException]:
        out: list[AllocationException] = []
        limit = ctx.policies.signal_max_auto_adjust_pct
        for signal in sorted(ctx.data.signals, key=lambda s: s.id):
            for adj in signal.adjustments:
                if adj.pct <= limit:
                    continue
                text = explain.signal_divergence(signal, ctx.store(signal.store), adj, limit)
                lines = [line for line in ctx.lines_for(store=signal.store) if adj.applies_to(line.sku, line.size)]
                out.append(build_exception(self, (signal.id, adj.scope), text, lines))
        return out
