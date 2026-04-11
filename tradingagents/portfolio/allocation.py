from __future__ import annotations

from typing import Any

from .account_models import AccountSnapshot, PortfolioAction, PortfolioCandidate, PortfolioProfile, PortfolioRecommendation
from .gates import infer_market_regime


_STANCE_WEIGHTS = {
    "BULLISH": 1.0,
    "NEUTRAL": 0.55,
    "BEARISH": 0.20,
}

_SETUP_WEIGHTS = {
    "COMPELLING": 1.0,
    "DEVELOPING": 0.8,
    "WEAK": 0.55,
}

_IMMEDIACY_WEIGHTS = {
    "ADD": 1.0,
    "STARTER": 0.75,
    "WAIT": 0.10,
    "NONE": 0.0,
    "EXIT": 1.0,
}


def build_recommendation(
    *,
    candidates: list[PortfolioCandidate],
    snapshot: AccountSnapshot,
    batch_metrics: dict[str, Any],
    warnings: list[str],
    profile: PortfolioProfile,
    report_date: str,
) -> tuple[PortfolioRecommendation, list[PortfolioCandidate]]:
    scored = [_score_candidate(candidate, snapshot, batch_metrics, warnings) for candidate in candidates]
    investable_cash_now = max(snapshot.available_cash_krw - snapshot.constraints.min_cash_buffer_krw, 0)
    trigger_budget_krw = min(profile.trigger_budget_krw or investable_cash_now, snapshot.available_cash_krw)

    wait_ratio = _ratio(batch_metrics.get("entry_action_distribution"), "WAIT")
    bullish_ratio = _ratio(batch_metrics.get("stance_distribution"), "BULLISH")
    if wait_ratio >= 0.7 and bullish_ratio >= 0.4:
        investable_cash_now = int(investable_cash_now * 0.25)
        trigger_budget_krw = max(
            trigger_budget_krw,
            int(max(snapshot.available_cash_krw - snapshot.constraints.min_cash_buffer_krw, 0) * 0.50),
        )

    positive_now = sum(
        max(candidate.score_now, 0.0)
        for candidate in scored
        if candidate.suggested_action_now in {"ADD_NOW", "STARTER_NOW"}
    )
    positive_triggered = sum(
        max(candidate.score_triggered, 0.0)
        for candidate in scored
        if candidate.suggested_action_if_triggered in {"ADD_IF_TRIGGERED", "STARTER_IF_TRIGGERED"}
    )

    actions: list[PortfolioAction] = []
    for candidate in sorted(scored, key=lambda item: (item.score_now, item.score_triggered), reverse=True):
        current_position = snapshot.find_position(candidate.instrument.canonical_ticker)
        current_value = int(current_position.market_value_krw if current_position else 0)
        account_value = max(snapshot.account_value_krw, 1)

        delta_now = _allocate_now_delta(
            candidate=candidate,
            current_value=current_value,
            investable_cash_now=investable_cash_now,
            positive_now=positive_now,
            account_value=account_value,
            snapshot=snapshot,
        )
        delta_triggered = _allocate_triggered_delta(
            candidate=candidate,
            current_value=current_value,
            trigger_budget_krw=trigger_budget_krw,
            positive_triggered=positive_triggered,
            account_value=account_value,
            snapshot=snapshot,
        )

        target_now = _weight_after_delta(current_value, delta_now, account_value)
        target_triggered = _weight_after_delta(current_value, delta_triggered, account_value)
        actions.append(
            PortfolioAction(
                canonical_ticker=candidate.instrument.canonical_ticker,
                display_name=candidate.instrument.display_name,
                priority=len(actions) + 1,
                confidence=round(candidate.confidence, 2),
                action_now=_normalize_now_action(candidate, delta_now),
                delta_krw_now=delta_now,
                target_weight_now=round(target_now, 4),
                action_if_triggered=_normalize_triggered_action(candidate, delta_triggered),
                delta_krw_if_triggered=delta_triggered,
                target_weight_if_triggered=round(target_triggered, 4),
                trigger_conditions=candidate.trigger_conditions,
                rationale=candidate.rationale,
                data_health={
                    **candidate.data_health,
                    "coverage_score": round(candidate.data_health.get("coverage_score", 0.0), 4),
                    "score_now": round(candidate.score_now, 4),
                    "score_triggered": round(candidate.score_triggered, 4),
                },
                decision_source=candidate.decision_source,
                timing_readiness=round(candidate.timing_readiness, 4),
                reason_codes=candidate.reason_codes,
                review_required=candidate.review_required,
                trigger_type=str(candidate.trigger_profile.get("primary_trigger_type") or "") or None,
                gate_reasons=candidate.gate_reasons,
                sector=candidate.sector,
            )
        )

    actions.sort(
        key=lambda item: (abs(item.delta_krw_now), abs(item.delta_krw_if_triggered), -item.priority),
        reverse=True,
    )
    actions = _apply_execution_constraints(actions, snapshot)
    actions.sort(
        key=lambda item: (abs(item.delta_krw_now), abs(item.delta_krw_if_triggered), -item.priority),
        reverse=True,
    )
    prioritized = tuple(
        PortfolioAction(**{**action.__dict__, "priority": index})
        for index, action in enumerate(actions, start=1)
    )

    cash_after_now = snapshot.available_cash_krw - sum(max(action.delta_krw_now, 0) for action in prioritized)
    cash_after_triggered = cash_after_now - sum(max(action.delta_krw_if_triggered, 0) for action in prioritized)

    risks = _infer_portfolio_risks(prioritized, warnings, batch_metrics)
    recommendation = PortfolioRecommendation(
        snapshot_id=snapshot.snapshot_id,
        report_date=report_date,
        account_value_krw=snapshot.account_value_krw,
        recommended_cash_after_now_krw=max(cash_after_now, 0),
        recommended_cash_after_triggered_krw=max(cash_after_triggered, 0),
        market_regime=infer_market_regime(batch_metrics),
        actions=prioritized,
        portfolio_risks=tuple(risks),
        data_health_summary={
            "decision_distribution": batch_metrics.get("decision_distribution") or {},
            "stance_distribution": batch_metrics.get("stance_distribution") or {},
            "entry_action_distribution": batch_metrics.get("entry_action_distribution") or {},
            "avg_confidence": batch_metrics.get("avg_confidence"),
            "company_news_zero_ratio": batch_metrics.get("company_news_zero_ratio"),
            "snapshot_health": snapshot.snapshot_health,
            "warning_flags": list(warnings),
        },
    )
    return recommendation, scored


def _score_candidate(
    candidate: PortfolioCandidate,
    snapshot: AccountSnapshot,
    batch_metrics: dict[str, Any],
    warnings: list[str],
) -> PortfolioCandidate:
    conviction = (
        _STANCE_WEIGHTS.get(candidate.stance, 0.45)
        * _SETUP_WEIGHTS.get(candidate.setup_quality, 0.70)
        * max(min(candidate.confidence, 1.0), 0.05)
    )
    immediacy = _IMMEDIACY_WEIGHTS.get(candidate.entry_action, 0.0)
    thesis_multiplier = 0.70 + (max(min(candidate.thesis_strength, 1.0), 0.0) * 0.60)
    timing_readiness = max(min(candidate.timing_readiness, 1.0), 0.0)
    timing_now = max(immediacy, timing_readiness * (0.40 if candidate.entry_action == "WAIT" else 0.85))
    timing_triggered = max(timing_readiness, 0.20 if candidate.trigger_conditions else 0.0)
    coverage_score = _coverage_score(candidate, batch_metrics, warnings)
    turnover_penalty = 0.08 if not candidate.is_held else 0.02
    if snapshot.constraints.respect_existing_weights_softly:
        turnover_penalty += 0.03 if not candidate.is_held else -0.01
    current_weight = candidate.market_value_krw / max(snapshot.account_value_krw, 1)
    concentration_penalty = max(current_weight - snapshot.constraints.max_single_name_weight, 0.0) * 1.5

    score_now = (
        conviction * timing_now * coverage_score * thesis_multiplier
        - turnover_penalty
        - concentration_penalty
    )
    score_triggered = (
        conviction * timing_triggered * coverage_score * thesis_multiplier
        - concentration_penalty
    )
    if candidate.review_required and not candidate.is_held:
        score_now = min(score_now, 0.0)
        score_triggered *= 0.75

    return PortfolioCandidate(
        **{
            **candidate.__dict__,
            "score_now": score_now,
            "score_triggered": score_triggered,
            "data_health": {
                **candidate.data_health,
                "coverage_score": coverage_score,
                "thesis_multiplier": round(thesis_multiplier, 4),
                "timing_now": round(timing_now, 4),
                "timing_triggered": round(timing_triggered, 4),
            },
        }
    )


def _coverage_score(candidate: PortfolioCandidate, batch_metrics: dict[str, Any], warnings: list[str]) -> float:
    coverage = 1.0
    if int(candidate.data_coverage.get("company_news_count", 0) or 0) == 0:
        coverage -= 0.20
    if int(candidate.data_coverage.get("disclosures_count", 0) or 0) == 0 and candidate.instrument.country == "KR":
        coverage -= 0.05
    social_source = str(candidate.data_coverage.get("social_source") or "unavailable")
    if social_source == "news_derived":
        coverage -= 0.10
    elif social_source == "unavailable":
        coverage -= 0.15

    quality_flags = set(candidate.quality_flags)
    if "no_tool_calls_detected" in quality_flags:
        coverage = min(coverage, 0.20)
    if candidate.vendor_health.get("fallback_count", 0) >= 2:
        coverage -= 0.10
    if candidate.review_required:
        coverage -= 0.08

    if (batch_metrics.get("company_news_zero_ratio") or 0) >= 0.5:
        coverage -= 0.05
    if any("legacy no_trade concentration" in str(item).lower() for item in warnings):
        coverage -= 0.05

    return max(0.10, min(coverage, 1.0))


def _allocate_now_delta(
    *,
    candidate: PortfolioCandidate,
    current_value: int,
    investable_cash_now: int,
    positive_now: float,
    account_value: int,
    snapshot: AccountSnapshot,
) -> int:
    action = candidate.suggested_action_now
    if action in {"HOLD", "WATCH"}:
        return 0
    if action in {"REDUCE_NOW", "TRIM_NOW", "EXIT_NOW"}:
        base_ratio = 1.0 if action == "EXIT_NOW" else min(max(abs(candidate.score_now), 0.15), 0.5)
        return -int(current_value * base_ratio)
    if action not in {"ADD_NOW", "STARTER_NOW"} or positive_now <= 0:
        return 0

    raw_delta = int(investable_cash_now * max(candidate.score_now, 0.0) / positive_now)
    max_name_value = int(snapshot.constraints.max_single_name_weight * account_value)
    remaining_name_capacity = max(max_name_value - current_value, 0)
    allowed = min(raw_delta, remaining_name_capacity)
    if allowed < snapshot.constraints.min_trade_krw:
        return 0
    return allowed


def _allocate_triggered_delta(
    *,
    candidate: PortfolioCandidate,
    current_value: int,
    trigger_budget_krw: int,
    positive_triggered: float,
    account_value: int,
    snapshot: AccountSnapshot,
) -> int:
    action = candidate.suggested_action_if_triggered
    if action in {"NONE", "WATCH_TRIGGER"}:
        return 0
    if action in {"REDUCE_IF_TRIGGERED", "EXIT_IF_TRIGGERED"}:
        base_ratio = 1.0 if action == "EXIT_IF_TRIGGERED" else min(max(abs(candidate.score_triggered), 0.15), 0.5)
        return -int(current_value * base_ratio)
    if action not in {"ADD_IF_TRIGGERED", "STARTER_IF_TRIGGERED"} or positive_triggered <= 0:
        return 0

    raw_delta = int(trigger_budget_krw * max(candidate.score_triggered, 0.0) / positive_triggered)
    max_name_value = int(snapshot.constraints.max_single_name_weight * account_value)
    remaining_name_capacity = max(max_name_value - current_value, 0)
    allowed = min(raw_delta, remaining_name_capacity)
    if allowed < snapshot.constraints.min_trade_krw:
        return 0
    return allowed


def _normalize_now_action(candidate: PortfolioCandidate, delta_now: int) -> str:
    if candidate.suggested_action_now in {"ADD_NOW", "STARTER_NOW"} and delta_now <= 0:
        return "HOLD"
    if candidate.suggested_action_now in {"REDUCE_NOW", "TRIM_NOW", "EXIT_NOW"} and delta_now == 0:
        return "HOLD"
    return candidate.suggested_action_now


def _normalize_triggered_action(candidate: PortfolioCandidate, delta_triggered: int) -> str:
    if candidate.suggested_action_if_triggered in {"ADD_IF_TRIGGERED", "STARTER_IF_TRIGGERED"} and delta_triggered <= 0:
        return "WATCH_TRIGGER"
    if candidate.suggested_action_if_triggered in {"REDUCE_IF_TRIGGERED", "EXIT_IF_TRIGGERED"} and delta_triggered == 0:
        return "NONE"
    return candidate.suggested_action_if_triggered


def _apply_execution_constraints(
    actions: list[PortfolioAction],
    snapshot: AccountSnapshot,
) -> list[PortfolioAction]:
    account_value = max(snapshot.account_value_krw, 1)
    turnover_limit = int(snapshot.constraints.max_daily_turnover_ratio * account_value)
    order_limit = max(0, snapshot.constraints.max_order_count_per_day)
    turnover_used = 0
    orders_used = 0
    constrained: list[PortfolioAction] = []

    for action in actions:
        delta_now = int(action.delta_krw_now)
        gate_reasons = list(action.gate_reasons)
        current_position = snapshot.find_position(action.canonical_ticker)
        current_value = int(current_position.market_value_krw if current_position else 0)
        proposed_turnover = abs(delta_now)
        remaining_turnover = max(turnover_limit - turnover_used, 0)

        if delta_now != 0 and turnover_limit <= 0:
            delta_now = 0
            gate_reasons.append("max_daily_turnover_ratio_cap")
        if delta_now != 0 and turnover_limit > 0 and proposed_turnover > remaining_turnover:
            delta_now = _signed_clip(delta_now, remaining_turnover)
            gate_reasons.append("max_daily_turnover_ratio_cap")
        if delta_now != 0 and order_limit <= 0:
            delta_now = 0
            gate_reasons.append("max_order_count_per_day_cap")
        if delta_now != 0 and order_limit > 0 and orders_used >= order_limit:
            delta_now = 0
            gate_reasons.append("max_order_count_per_day_cap")
        if 0 < abs(delta_now) < snapshot.constraints.min_trade_krw:
            delta_now = 0
            gate_reasons.append("min_trade_floor_after_caps")

        if delta_now != 0:
            turnover_used += abs(delta_now)
            orders_used += 1

        constrained.append(
            PortfolioAction(
                **{
                    **action.__dict__,
                    "action_now": _normalize_action_value(action.action_now, delta_now),
                    "delta_krw_now": delta_now,
                    "target_weight_now": round(_weight_after_delta(current_value, delta_now, account_value), 4),
                    "gate_reasons": tuple(dict.fromkeys(gate_reasons)),
                }
            )
        )

    return constrained


def _normalize_action_value(action_now: str, delta_now: int) -> str:
    if action_now in {"ADD_NOW", "STARTER_NOW", "REDUCE_NOW", "TRIM_NOW", "EXIT_NOW"} and delta_now == 0:
        return "HOLD"
    return action_now


def _signed_clip(value: int, magnitude: int) -> int:
    if magnitude <= 0:
        return 0
    return magnitude if value > 0 else -magnitude


def _weight_after_delta(current_value: int, delta: int, account_value: int) -> float:
    return max(current_value + delta, 0) / max(account_value, 1)


def _infer_portfolio_risks(
    actions: tuple[PortfolioAction, ...],
    warnings: list[str],
    batch_metrics: dict[str, Any],
) -> list[str]:
    risks = list(dict.fromkeys(str(item) for item in warnings))
    sectors = [action.sector for action in actions if action.sector]
    if sectors and max(sectors.count(sector) for sector in set(sectors)) >= 2:
        risks.append("동일 섹터 편중 가능성")
    if _ratio(batch_metrics.get("entry_action_distribution"), "WAIT") >= 0.6:
        risks.append("구성적이지만 즉시 실행 가능한 후보가 적음")
    if not risks:
        risks.append("특이 리스크 없음")
    return risks


def _ratio(distribution: dict[str, Any] | None, key: str) -> float:
    if not distribution:
        return 0.0
    total = sum(int(value or 0) for value in distribution.values())
    if total <= 0:
        return 0.0
    return int(distribution.get(key, 0) or 0) / total
