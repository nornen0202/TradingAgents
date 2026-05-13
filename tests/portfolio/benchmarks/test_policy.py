from __future__ import annotations

from datetime import date
from types import SimpleNamespace

from tradingagents.portfolio.benchmarks.policy import (
    core_satellite_recommendation,
    evaluate_individual_stock_policy,
)


def test_insufficient_history_does_not_trigger_hard_policy():
    policy = evaluate_individual_stock_policy(
        alternatives=[],
        settings=SimpleNamespace(alpha_policy_mode="report_only", alpha_policy_reduce_target_pct=15.0, alpha_policy_min_action_samples=5),
        period_start=date(2026, 4, 13),
        period_end=date(2026, 5, 12),
        policy_inputs={},
    )

    assert policy["status"] == "INSUFFICIENT_DATA"
    assert policy["decisions"] == []
    recommendation = core_satellite_recommendation(policy)
    assert recommendation.confidence == "low"


def test_three_month_and_six_month_underperformance_trigger_report_only_decisions():
    policy = evaluate_individual_stock_policy(
        alternatives=[],
        settings=SimpleNamespace(alpha_policy_mode="report_only", alpha_policy_reduce_target_pct=15.0, alpha_policy_min_action_samples=5),
        period_start=date(2025, 11, 13),
        period_end=date(2026, 5, 12),
        policy_inputs={
            "monthly_blended_excess_return_pct": [-1.0, -0.5, -0.2],
            "six_month_blended_excess_return_pct": -3.0,
        },
    )

    assert "FREEZE_NEW_INDIVIDUAL_BUYS" in policy["decisions"]
    assert "REDUCE_INDIVIDUAL_STOCK_TARGET_TO_15PCT" in policy["decisions"]
    recommendation = core_satellite_recommendation(policy)
    assert recommendation.recommended_core_etf_weight == 0.85
    assert recommendation.recommended_individual_stock_weight == 0.15
