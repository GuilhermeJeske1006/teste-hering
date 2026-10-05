"""Fixtures compartilhadas dos testes de regras de exceção."""
from __future__ import annotations

from collections.abc import Sequence

from app.domain.forecasting import SalesIndex
from app.domain.model import AllocationLine, Transfer, WeekData
from app.domain.rules.base import RuleContext


def make_context(data: WeekData, lines: Sequence[AllocationLine] = (),
                 transfers: Sequence[Transfer] = ()) -> RuleContext:
    return RuleContext(data=data, lines=tuple(lines), transfers=tuple(transfers), sales=SalesIndex(data.sales))
