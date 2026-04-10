from __future__ import annotations

from collections import defaultdict
from typing import Any

from .account_models import AccountSnapshot, PortfolioCandidate, PortfolioProfile


def apply_gates(
    *,
    candidates: list[PortfolioCandidate],
    snapshot: AccountSnapshot,
    batch_metrics: dict[str, Any],
    warnings: list[str],
    profile: PortfolioProfile,
) -> list[PortfolioCandidate]:
    account_value = max(snapshot.account_value_krw, 1)
    sector_values = defaultdict(int)
    for position in snapshot.positions:
        if position.sector:
            sector_values[position.sector] += int(position.market_value_krw)

    wait_ratio = _ratio(batch_metrics.get("entry_action_distribution"), "WAIT")
    bullish_ratio = _ratio(batch_metrics.get("stance_distribution"), "BULLISH")

    gated: list[PortfolioCandidate] = []
    for candidate in candidates:
        reasons: list[str] = list(candidate.gate_reasons)
        quality_flags = set(candidate.quality_flags)
        company_news_count = int(candidate.data_coverage.get("company_news_count", 0) or 0)
        fallback_count = int(candidate.vendor_health.get("fallback_count", 0) or 0)

        if candidate.snapshot_id != snapshot.snapshot_id:
            reasons.append("snapshot_id_mismatch")
        if not candidate.is_held and "no_tool_calls_detected" in quality_flags:
            reasons.append("blocked_new_entries_no_tool_calls")
        if not candidate.is_held and company_news_count == 0:
            reasons.append("blocked_new_entries_company_news_zero")
        if fallback_count >= 3:
            reasons.append("high_fallback_count")
        if not candidate.is_held and wait_ratio >= 0.7 and bullish_ratio >= 0.5:
            reasons.append("wait_heavy_batch_reduce_immediate_entries")

        current_weight = candidate.market_value_krw / account_value if account_value else 0.0
        if current_weight >= snapshot.constraints.max_single_name_weight and candidate.suggested_action_now in {"ADD_NOW", "STARTER_NOW"}:
            reasons.append("max_single_name_weight_reached")
        if candidate.sector:
            sector_weight = sector_values[candidate.sector] / account_value if account_value else 0.0
            if sector_weight >= snapshot.constraints.max_sector_weight and candidate.suggested_action_now in {"ADD_NOW", "STARTER_NOW"}:
                reasons.append("max_sector_weight_reached")

        if any("data" in warning.lower() or "vendor" in warning.lower() for warning in warnings):
            reasons.append("batch_warning_present")

        gated.append(
            PortfolioCandidate(
                **{
                    **candidate.__dict__,
                    "gate_reasons": tuple(dict.fromkeys(reasons)),
                }
            )
        )
    return gated


def infer_market_regime(batch_metrics: dict[str, Any]) -> str:
    wait_ratio = _ratio(batch_metrics.get("entry_action_distribution"), "WAIT")
    bullish_ratio = _ratio(batch_metrics.get("stance_distribution"), "BULLISH")
    bearish_ratio = _ratio(batch_metrics.get("stance_distribution"), "BEARISH")
    if bullish_ratio >= 0.5 and wait_ratio >= 0.5:
        return "constructive_but_selective"
    if bearish_ratio >= 0.5:
        return "defensive"
    if bullish_ratio >= 0.5:
        return "constructive"
    return "mixed"


def _ratio(distribution: dict[str, Any] | None, key: str) -> float:
    if not distribution:
        return 0.0
    total = sum(int(value or 0) for value in distribution.values())
    if total <= 0:
        return 0.0
    return int(distribution.get(key, 0) or 0) / total
