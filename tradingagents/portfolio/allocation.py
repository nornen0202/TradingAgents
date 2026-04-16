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

_IMMEDIATE_ACTIONS = {"ADD_NOW", "STARTER_NOW", "REDUCE_NOW", "TRIM_NOW", "EXIT_NOW"}
_TRIGGER_BUY_ACTIONS = {"ADD_IF_TRIGGERED", "STARTER_IF_TRIGGERED"}
_TRIGGER_SELL_ACTIONS = {"REDUCE_IF_TRIGGERED", "EXIT_IF_TRIGGERED"}
_STRATEGIC_TRIGGER_ACTIONS = _TRIGGER_BUY_ACTIONS | _TRIGGER_SELL_ACTIONS


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
    trigger_budget_krw = min(profile.trigger_budget_krw or investable_cash_now, investable_cash_now)

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
                    "strict_cash_available_for_new_buys_krw": investable_cash_now,
                },
                strategy_state=candidate.strategy_state,
                execution_feasibility_now=candidate.execution_feasibility_now,
                stale_but_triggerable=candidate.stale_but_triggerable,
                funding_source_score=round(candidate.funding_source_score, 4),
                capital_reallocation_rank=candidate.capital_reallocation_rank,
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
    prioritized = _annotate_reallocation_ranks(prioritized, snapshot)

    cash_after_now = snapshot.available_cash_krw - sum(max(action.delta_krw_now, 0) for action in prioritized)
    cash_after_triggered = cash_after_now - sum(max(action.delta_krw_if_triggered, 0) for action in prioritized)

    risks = _infer_portfolio_risks(prioritized, warnings, batch_metrics)
    candidate_counts = _build_candidate_counts(prioritized, snapshot)
    funding_plan = _build_funding_plan(prioritized, snapshot)
    scenario_plan = _build_scenario_plan(
        actions=prioritized,
        snapshot=snapshot,
        funding_plan=funding_plan,
        candidate_counts=candidate_counts,
        profile=profile,
    )
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
            "actionable_now_count": sum(
                1 for action in prioritized if action.action_now in _IMMEDIATE_ACTIONS
            ),
            "triggerable_candidates_count": sum(
                1 for action in prioritized if action.action_if_triggered in _TRIGGER_BUY_ACTIONS
            ),
            **candidate_counts,
            "watch_candidates_count": sum(1 for action in prioritized if action.action_now == "WATCH"),
            "held_watch_count": sum(
                1 for action in prioritized if action.action_now == "HOLD" and action.action_if_triggered == "ADD_IF_TRIGGERED"
            ),
            "review_required_count": sum(1 for action in prioritized if action.review_required),
            "rule_only_fallback_count": sum(
                1 for action in prioritized if str(action.decision_source).upper() == "RULE_ONLY_FALLBACK"
            ),
            "funding_plan_available": bool(
                funding_plan.get("top_add_if_funded") and funding_plan.get("top_trim_if_funding_needed")
            ),
        },
        candidate_counts=candidate_counts,
        funding_plan=funding_plan,
        scenario_plan=scenario_plan,
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
    funding_source_score = _candidate_funding_source_score(
        candidate=candidate,
        coverage_score=coverage_score,
        timing_readiness=timing_readiness,
    )

    return PortfolioCandidate(
        **{
            **candidate.__dict__,
            "score_now": score_now,
            "score_triggered": score_triggered,
            "funding_source_score": funding_source_score,
            "data_health": {
                **candidate.data_health,
                "coverage_score": coverage_score,
                "thesis_multiplier": round(thesis_multiplier, 4),
                "timing_now": round(timing_now, 4),
                "timing_triggered": round(timing_triggered, 4),
                "funding_source_score": round(funding_source_score, 4),
            },
        }
    )


def _candidate_funding_source_score(
    *,
    candidate: PortfolioCandidate,
    coverage_score: float,
    timing_readiness: float,
) -> float:
    if not candidate.is_held or candidate.market_value_krw <= 0:
        return 0.0
    stance_penalty = {"BEARISH": 0.35, "NEUTRAL": 0.22, "BULLISH": 0.04}.get(candidate.stance, 0.18)
    setup_penalty = {"WEAK": 0.22, "DEVELOPING": 0.10, "COMPELLING": 0.0}.get(candidate.setup_quality, 0.08)
    no_add_penalty = 0.12 if candidate.suggested_action_if_triggered in {"NONE", "WATCH_TRIGGER"} else 0.0
    quality_penalty = (1.0 - max(min(coverage_score, 1.0), 0.0)) * 0.18
    timing_penalty = (1.0 - max(min(timing_readiness, 1.0), 0.0)) * 0.14
    confidence_penalty = (1.0 - max(min(candidate.confidence, 1.0), 0.0)) * 0.12
    return round(
        max(0.0, min(1.0, stance_penalty + setup_penalty + no_add_penalty + quality_penalty + timing_penalty + confidence_penalty)),
        4,
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
    return candidate.suggested_action_if_triggered


def _build_candidate_counts(
    actions: tuple[PortfolioAction, ...],
    snapshot: AccountSnapshot,
) -> dict[str, int]:
    strategic_trigger_candidates = [
        action for action in actions if action.action_if_triggered in _STRATEGIC_TRIGGER_ACTIONS
    ]
    budgeted_trigger_candidates = [
        action for action in strategic_trigger_candidates if int(action.delta_krw_if_triggered) != 0
    ]
    top_add_if_funded = [
        action
        for action in strategic_trigger_candidates
        if action.action_if_triggered in _TRIGGER_BUY_ACTIONS and int(action.delta_krw_if_triggered) <= 0
    ]
    top_trim_if_needed = [
        action
        for action in actions
        if snapshot.find_position(action.canonical_ticker) is not None and action.funding_source_score > 0
    ]
    return {
        "strategic_trigger_candidates_count": len(strategic_trigger_candidates),
        "budgeted_trigger_candidates_count": len(budgeted_trigger_candidates),
        "immediate_candidates_count": sum(1 for action in actions if action.action_now in _IMMEDIATE_ACTIONS and action.delta_krw_now != 0),
        "funding_candidates_count": len(top_add_if_funded) if top_trim_if_needed else 0,
        "held_add_if_triggered_count": sum(
            1
            for action in actions
            if snapshot.find_position(action.canonical_ticker) is not None
            and action.action_if_triggered in _TRIGGER_BUY_ACTIONS
        ),
        "watch_if_triggered_count": sum(
            1
            for action in actions
            if snapshot.find_position(action.canonical_ticker) is None
            and action.action_if_triggered in (_TRIGGER_BUY_ACTIONS | {"WATCH_TRIGGER"})
        ),
    }


def _annotate_reallocation_ranks(
    actions: tuple[PortfolioAction, ...],
    snapshot: AccountSnapshot,
) -> tuple[PortfolioAction, ...]:
    trim_rank_by_ticker = {
        action.canonical_ticker: index
        for index, action in enumerate(
            sorted(
                (
                    action
                    for action in actions
                    if snapshot.find_position(action.canonical_ticker) is not None and action.funding_source_score > 0
                ),
                key=lambda action: (action.funding_source_score, action.market_value_krw if hasattr(action, "market_value_krw") else 0),
                reverse=True,
            ),
            start=1,
        )
    }
    add_rank_by_ticker = {
        action.canonical_ticker: index
        for index, action in enumerate(
            sorted(
                (action for action in actions if action.action_if_triggered in _TRIGGER_BUY_ACTIONS),
                key=_add_if_funded_score,
                reverse=True,
            ),
            start=1,
        )
    }
    annotated: list[PortfolioAction] = []
    for action in actions:
        rank = trim_rank_by_ticker.get(action.canonical_ticker) or add_rank_by_ticker.get(action.canonical_ticker)
        annotated.append(
            PortfolioAction(
                **{
                    **action.__dict__,
                    "capital_reallocation_rank": rank,
                }
            )
        )
    return tuple(annotated)


def _build_funding_plan(
    actions: tuple[PortfolioAction, ...],
    snapshot: AccountSnapshot,
) -> dict[str, Any]:
    add_candidates = sorted(
        (action for action in actions if action.action_if_triggered in _TRIGGER_BUY_ACTIONS),
        key=_add_if_funded_score,
        reverse=True,
    )
    trim_candidates = sorted(
        (
            action
            for action in actions
            if snapshot.find_position(action.canonical_ticker) is not None and action.funding_source_score > 0
        ),
        key=lambda action: action.funding_source_score,
        reverse=True,
    )
    cash_gap = max(snapshot.constraints.min_cash_buffer_krw - snapshot.available_cash_krw, 0)
    return {
        "cash_gap_to_strict_buffer_krw": cash_gap,
        "top_add_if_funded": [_funding_add_item(action) for action in add_candidates[:5]],
        "top_trim_if_funding_needed": [_funding_trim_item(action, snapshot) for action in trim_candidates[:5]],
    }


def _build_scenario_plan(
    *,
    actions: tuple[PortfolioAction, ...],
    snapshot: AccountSnapshot,
    funding_plan: dict[str, Any],
    candidate_counts: dict[str, int],
    profile: PortfolioProfile,
) -> dict[str, Any]:
    immediate_orders = [action for action in actions if action.delta_krw_now != 0]
    budgeted_triggers = [action for action in actions if action.delta_krw_if_triggered != 0]
    switch_orders = _build_switch_scenario_orders(actions=actions, snapshot=snapshot)
    aggressive_orders = _build_aggressive_scenario_orders(actions=actions, snapshot=snapshot, profile=profile)
    add_if_funded = list(funding_plan.get("top_add_if_funded") or [])
    trim_sources = list(funding_plan.get("top_trim_if_funding_needed") or [])
    return {
        "strict": {
            "label": "Strict",
            "cash_buffer_respected": snapshot.available_cash_krw >= snapshot.constraints.min_cash_buffer_krw,
            "immediate_order_count": len(immediate_orders),
            "budgeted_trigger_count": len(budgeted_triggers),
            "strategic_trigger_count": candidate_counts.get("strategic_trigger_candidates_count", 0),
            "orders_now": [_scenario_order_from_action(action, scenario="strict_now", amount=action.delta_krw_now) for action in immediate_orders],
            "orders_if_triggered": [
                _scenario_order_from_action(action, scenario="strict_if_triggered", amount=action.delta_krw_if_triggered)
                for action in budgeted_triggers
            ],
        },
        "switch": {
            "label": "Switch",
            "enabled": bool(switch_orders),
            "would_buy_if_funded": add_if_funded[:3],
            "would_trim_first": trim_sources[:3],
            "orders_if_triggered": switch_orders,
            "gross_buy_krw": sum(max(int(order.get("amount_krw", 0)), 0) for order in switch_orders if order.get("side") == "buy"),
            "gross_sell_krw": sum(max(int(order.get("amount_krw", 0)), 0) for order in switch_orders if order.get("side") == "sell"),
        },
        "aggressive": {
            "label": "Aggressive",
            "enabled": bool(aggressive_orders),
            "requires_buffer_sacrifice": snapshot.available_cash_krw < snapshot.constraints.min_cash_buffer_krw,
            "would_buy_if_buffer_relaxed": add_if_funded[:3],
            "orders_if_triggered": aggressive_orders,
            "gross_buy_krw": sum(max(int(order.get("amount_krw", 0)), 0) for order in aggressive_orders if order.get("side") == "buy"),
        },
    }


def _build_switch_scenario_orders(
    *,
    actions: tuple[PortfolioAction, ...],
    snapshot: AccountSnapshot,
) -> list[dict[str, Any]]:
    min_trade = max(int(snapshot.constraints.min_trade_krw), 1)
    trim_actions = sorted(
        (
            action
            for action in actions
            if snapshot.find_position(action.canonical_ticker) is not None and action.funding_source_score > 0
        ),
        key=lambda action: action.funding_source_score,
        reverse=True,
    )
    add_actions = sorted(
        (action for action in actions if action.action_if_triggered in _TRIGGER_BUY_ACTIONS),
        key=_add_if_funded_score,
        reverse=True,
    )
    if not trim_actions or not add_actions:
        return []

    sell_orders: list[dict[str, Any]] = []
    sell_budget = 0
    turnover_limit = int(max(snapshot.account_value_krw, 1) * snapshot.constraints.max_daily_turnover_ratio)
    for action in trim_actions:
        position = snapshot.find_position(action.canonical_ticker)
        if position is None:
            continue
        ratio = min(0.35, max(0.15, float(action.funding_source_score) * 0.55))
        amount = int(position.market_value_krw * ratio)
        remaining_turnover = max(turnover_limit - sell_budget, 0) if turnover_limit > 0 else amount
        amount = min(amount, remaining_turnover)
        if amount < min_trade:
            continue
        sell_budget += amount
        sell_orders.append(
            _scenario_order_from_action(
                action,
                scenario="switch_trim_source",
                amount=-amount,
                note="자금 조달을 위한 조건부 축소",
            )
        )
        if sell_budget >= min_trade * 3:
            break

    if sell_budget < min_trade:
        return []

    buy_orders = _allocate_buy_scenario_orders(
        actions=add_actions,
        snapshot=snapshot,
        budget_krw=sell_budget,
        scenario="switch_buy_if_funded",
        note="축소 자금 확보 시 조건부 매수",
    )
    if not buy_orders:
        return []
    return sell_orders + buy_orders


def _build_aggressive_scenario_orders(
    *,
    actions: tuple[PortfolioAction, ...],
    snapshot: AccountSnapshot,
    profile: PortfolioProfile,
) -> list[dict[str, Any]]:
    add_actions = sorted(
        (action for action in actions if action.action_if_triggered in _TRIGGER_BUY_ACTIONS),
        key=_add_if_funded_score,
        reverse=True,
    )
    if not add_actions:
        return []
    investable_cash = max(snapshot.available_cash_krw - snapshot.constraints.min_cash_buffer_krw, 0)
    if investable_cash <= 0:
        budget = min(max(int(profile.trigger_budget_krw or 0), snapshot.constraints.min_trade_krw), max(snapshot.available_cash_krw, 0))
    else:
        budget = min(int(profile.trigger_budget_krw or investable_cash), investable_cash)
    if budget < snapshot.constraints.min_trade_krw:
        return []
    return _allocate_buy_scenario_orders(
        actions=add_actions,
        snapshot=snapshot,
        budget_krw=budget,
        scenario="aggressive_buy_if_triggered",
        note="버퍼 일부 희생을 허용하는 조건부 매수",
    )


def _allocate_buy_scenario_orders(
    *,
    actions: list[PortfolioAction],
    snapshot: AccountSnapshot,
    budget_krw: int,
    scenario: str,
    note: str,
) -> list[dict[str, Any]]:
    min_trade = max(int(snapshot.constraints.min_trade_krw), 1)
    account_value = max(snapshot.account_value_krw, 1)
    total_score = sum(max(_add_if_funded_score(action), 0.01) for action in actions)
    remaining_budget = int(budget_krw)
    orders: list[dict[str, Any]] = []
    for index, action in enumerate(actions):
        if remaining_budget < min_trade:
            break
        score = max(_add_if_funded_score(action), 0.01)
        if index == len(actions) - 1:
            raw_amount = remaining_budget
        else:
            raw_amount = int(budget_krw * score / max(total_score, 0.01))
        current_position = snapshot.find_position(action.canonical_ticker)
        current_value = int(current_position.market_value_krw if current_position else 0)
        max_name_value = int(snapshot.constraints.max_single_name_weight * account_value)
        remaining_name_capacity = max(max_name_value - current_value, 0)
        amount = min(raw_amount, remaining_budget, remaining_name_capacity)
        if amount < min_trade:
            continue
        remaining_budget -= amount
        orders.append(_scenario_order_from_action(action, scenario=scenario, amount=amount, note=note))
    return orders


def _scenario_order_from_action(
    action: PortfolioAction,
    *,
    scenario: str,
    amount: int,
    note: str | None = None,
) -> dict[str, Any]:
    amount_int = int(amount)
    return {
        "scenario": scenario,
        "canonical_ticker": action.canonical_ticker,
        "display_name": action.display_name,
        "side": "buy" if amount_int > 0 else "sell",
        "amount_krw": abs(amount_int),
        "signed_delta_krw": amount_int,
        "action_now": action.action_now,
        "action_if_triggered": action.action_if_triggered,
        "trigger_conditions": list(action.trigger_conditions),
        "rank": action.capital_reallocation_rank,
        "note": note,
    }


def _add_if_funded_score(action: PortfolioAction) -> float:
    return (
        max(float(action.data_health.get("score_triggered") or 0.0), 0.0)
        + max(min(float(action.confidence or 0.0), 1.0), 0.0) * 0.30
        + max(min(float(action.timing_readiness or 0.0), 1.0), 0.0) * 0.20
        + max(min(float(action.data_health.get("trigger_quality") or 0.0), 1.0), 0.0) * 0.20
    )


def _funding_add_item(action: PortfolioAction) -> dict[str, Any]:
    return {
        "canonical_ticker": action.canonical_ticker,
        "display_name": action.display_name,
        "action_if_triggered": action.action_if_triggered,
        "delta_krw_if_triggered": action.delta_krw_if_triggered,
        "rank": action.capital_reallocation_rank,
        "score": round(_add_if_funded_score(action), 4),
        "trigger_conditions": list(action.trigger_conditions),
        "rationale": action.rationale,
    }


def _funding_trim_item(action: PortfolioAction, snapshot: AccountSnapshot) -> dict[str, Any]:
    position = snapshot.find_position(action.canonical_ticker)
    return {
        "canonical_ticker": action.canonical_ticker,
        "display_name": action.display_name,
        "rank": action.capital_reallocation_rank,
        "funding_source_score": round(action.funding_source_score, 4),
        "market_value_krw": int(position.market_value_krw if position else 0),
        "action_now": action.action_now,
        "action_if_triggered": action.action_if_triggered,
        "rationale": action.rationale,
    }


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
