"""Regras de exceção plugáveis. A ordem de `default_rules()` é a ordem de saída (regras.md §8)."""
from __future__ import annotations

from app.domain.rules.auto_execution_limit import AutoExecutionLimitRule
from app.domain.rules.base import ExceptionRule, RuleContext
from app.domain.rules.launch_approval import LaunchApprovalRule
from app.domain.rules.negative_stock import NegativeStockRule
from app.domain.rules.repeated_rejection import RepeatedRejectionRule
from app.domain.rules.seasonal_decline import SeasonalDeclineRule
from app.domain.rules.signal_divergence import SignalDivergenceRule
from app.domain.rules.size_curve_deviation import SizeCurveDeviationRule
from app.domain.rules.stockout_transfer import StockoutTransferRule


def default_rules() -> list[ExceptionRule]:
    """Regras padrão, na ordem da tabela do regras.md §8."""
    return [
        LaunchApprovalRule(),
        StockoutTransferRule(),
        SignalDivergenceRule(),
        SeasonalDeclineRule(),
        SizeCurveDeviationRule(),
        NegativeStockRule(),
        RepeatedRejectionRule(),
        AutoExecutionLimitRule(),
    ]


__all__ = ["ExceptionRule", "RuleContext", "default_rules"]
