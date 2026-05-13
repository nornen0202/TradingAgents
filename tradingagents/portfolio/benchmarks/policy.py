from __future__ import annotations

from datetime import date
from typing import Any

from tradingagents.portfolio.performance.etf_alternatives import EtfAlternativePortfolioResult, evaluate_alpha_policy


def evaluate_individual_stock_policy(
    *,
    alternatives: list[EtfAlternativePortfolioResult],
    settings: Any,
    period_start: date,
    period_end: date,
    policy_inputs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return evaluate_alpha_policy(
        alternatives=alternatives,
        settings=settings,
        period_start=period_start,
        period_end=period_end,
        policy_inputs=policy_inputs,
    )
