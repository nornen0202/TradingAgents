from __future__ import annotations

from datetime import date
from typing import Any

from tradingagents.portfolio.performance.etf_alternatives import EtfAlternativePortfolioResult, evaluate_alpha_policy

from .models import CoreSatelliteRecommendation


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


def core_satellite_recommendation(policy: dict[str, Any]) -> CoreSatelliteRecommendation:
    decisions = [str(item) for item in policy.get("decisions", [])] if isinstance(policy, dict) else []
    confidence = "low" if str(policy.get("status") if isinstance(policy, dict) else "").upper() == "INSUFFICIENT_DATA" else "medium"
    core_weight = 0.5
    individual_weight = 0.5
    reasons: list[str] = []
    if "ETF_CORE_REQUIRED" in decisions:
        core_weight = 0.9
        individual_weight = 0.1
        confidence = "high"
        reasons.append("12M return/MDD/turnover rule favored ETF core allocation.")
    elif any(item.startswith("REDUCE_INDIVIDUAL_STOCK_TARGET_TO_") for item in decisions):
        target = next((item for item in decisions if item.startswith("REDUCE_INDIVIDUAL_STOCK_TARGET_TO_")), "")
        try:
            individual_weight = float(target.removeprefix("REDUCE_INDIVIDUAL_STOCK_TARGET_TO_").removesuffix("PCT")) / 100.0
        except ValueError:
            individual_weight = 0.15
        core_weight = max(0.0, 1.0 - individual_weight)
        confidence = "medium"
        reasons.append("6M blended benchmark excess return was negative.")
    elif "FREEZE_NEW_INDIVIDUAL_BUYS" in decisions:
        core_weight = 0.7
        individual_weight = 0.3
        confidence = "medium"
        reasons.append("3M consecutive blended benchmark underperformance was detected.")
    else:
        reasons.append("No hard ETF core rule was triggered.")
    return CoreSatelliteRecommendation(
        recommended_core_etf_weight=round(core_weight, 4),
        recommended_individual_stock_weight=round(individual_weight, 4),
        confidence=confidence,
        reasons=reasons,
        rules_triggered=decisions,
    )
