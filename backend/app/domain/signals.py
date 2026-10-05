"""Regras de política sobre sinais interpretados (regras.md §11)."""
from __future__ import annotations

from collections.abc import Sequence

from app.domain.model import Policies, SignalAdjustment, SignalType


def signal_requires_human(signal_type: SignalType, adjustments: Sequence[SignalAdjustment],
                          policies: Policies) -> bool:
    """Recalcula `requires_human` pela política; o valor vindo do LLM é ignorado."""
    above_limit = any(adj.pct > policies.signal_max_auto_adjust_pct for adj in adjustments)
    return above_limit or signal_type is SignalType.SIZE_CURVE
