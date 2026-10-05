"""Regra 2: transferência proposta entre lojas para evitar ruptura."""
from __future__ import annotations

from collections import defaultdict

from app.domain import explain
from app.domain.allocation import cover_weeks
from app.domain.model import AllocationException, Ownership, Severity
from app.domain.rules.base import RuleContext, build_exception


class StockoutTransferRule:
    """Uma exceção por produto × tamanho × origem, com a lista de destinos."""

    rule = "stockout_transfer"
    severity = Severity.HIGH

    def evaluate(self, ctx: RuleContext) -> list[AllocationException]:
        groups: dict[tuple[str, str, str], list[tuple[str, int]]] = defaultdict(list)
        for t in ctx.transfers:
            groups[(t.sku, t.size, t.source)].append((t.destination, t.qty))
        dc = {(d.sku, d.size): d.qty for d in ctx.data.dc_stock}
        out: list[AllocationException] = []
        for (sku_id, size, source_id), destinations in sorted(groups.items()):
            group = ctx.lines_for(sku=sku_id, size=size)
            source_line = next(line for line in group if line.store == source_id)
            source = ctx.store(source_id)
            text = explain.stockout_transfer(
                ctx.sku(sku_id), size, source, destinations,
                dc_available=dc.get((sku_id, size), 0),
                total_need=sum(line.need for line in group),
                source_cover=cover_weeks(source_line.stock, source_line.weekly_forecast),
                freight_brl=ctx.policies.transfer_freight_brl,
                source_is_franchise=source.ownership is Ownership.FRANCHISE,
            )
            involved = {source_id, *(d for d, _ in destinations)}
            out.append(build_exception(self, (sku_id, size, source_id), text,
                                       [line for line in group if line.store in involved]))
        return out
