from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .account_models import AccountSnapshot, PortfolioAction, PortfolioCandidate, PortfolioProfile, PortfolioRecommendation
from .opportunity_sleeve import compute_opportunity_pilot_budget


_NOW_BUY_ACTIONS = {"ADD_NOW", "STARTER_NOW"}
_TRIGGER_BUY_ACTIONS = {
    "ADD_IF_TRIGGERED",
    "STARTER_IF_TRIGGERED",
    "STARTER_ON_PULLBACK",
    "CLOSE_CONFIRMED_STARTER_NEXT_DAY",
}
_CONDITIONAL_BUY_ACTIONS = _TRIGGER_BUY_ACTIONS | {"FULL_SIZE_BLOCKED_PILOT_ALLOWED"}
_SELL_SIDE_ACTIONS = {"TRIM_TO_FUND", "REDUCE_RISK", "TAKE_PROFIT", "STOP_LOSS", "EXIT"}
_BLOCK_CATEGORY_TOKENS = {
    "disclosure_hard_block": {
        "audit_opinion",
        "going_concern",
        "delisting_review",
        "disclosure_hard_risk",
        "unfaithful_disclosure",
        "embezzlement",
        "breach_of_trust",
        "rehabilitation_proceeding",
        "감사의견",
        "계속기업",
        "상장폐지",
        "불성실공시",
        "횡령",
        "배임",
        "회생절차",
    },
    "market_warning_block": {
        "trading_halt",
        "management_issue",
        "investment_warning",
        "investment_risk",
        "거래정지",
        "관리종목",
        "투자경고",
        "투자위험",
    },
    "data_quality_block": {
        "identity_integrity_failed",
        "ticker_identity_mismatch",
        "price_unavailable",
        "data_missing_blocked_pilot",
        "blocked_new_entries_no_tool_calls",
        "blocked_new_entries_company_news_zero",
        "high_fallback_count",
        "execution_data_quality_failed",
    },
    "account_concentration_block": {
        "max_single_name_weight_reached",
        "max_sector_weight_reached",
        "account_concentration",
        "single_name_weight",
        "sector_weight",
        "concentration",
    },
    "stop_distance_block": {
        "stop_distance_block",
        "pilot_blocked_by_stop_distance",
        "stop_distance_too_wide",
        "too_wide_stop",
    },
    "budget_block": {
        "budget_or_cash_buffer_blocked",
        "cash_buffer_block",
        "pilot_allowed_below_min_trade",
        "opportunity_capture_sleeve_cap",
        "opportunity_capture_per_pilot_cap",
        "pilot_budget_zero",
        "min_trade",
        "budget_block",
    },
}
_PILOT_HARD_BLOCK_CATEGORIES = {
    "disclosure_hard_block",
    "market_warning_block",
    "data_quality_block",
    "account_concentration_block",
    "stop_distance_block",
}
_WARNING_STATUSES = {
    "ACTION_LIFT_FAILURE",
    "BUY_SIGNAL_RELABELED_AS_SELL_SIDE",
    "BUDGET_BLOCKED",
    "PILOT_VISIBLE_NO_ORDER",
    "PRISM_SOFT_BLOCK_PILOT_ALLOWED",
    "HARD_BLOCKED",
}


@dataclass(frozen=True)
class ActionLiftAuditEntry:
    ticker: str
    display_name: str
    stock_thesis: str
    stock_entry_state: str
    stock_execution_timing: str
    account_position_state: str
    account_action_now: str
    account_action_if_triggered: str
    proposed_now_exists: bool
    conditional_order_exists: bool
    proposed_order_exists: bool
    block_reasons: list[str]
    block_categories: list[str]
    pilot_allowed: bool
    full_size_allowed: bool
    opportunity_cost_score: float
    opportunity_capture_score: float
    opportunity_capture_components: dict[str, float]
    lift_status: str
    lift_failure: bool
    next_valid_action: str
    pilot_budget_krw: int | None = None
    max_loss_krw: int | None = None
    sleeve_total_krw: int | None = None
    stop_distance_pct: float | None = None
    sizing_blocked: bool | None = None
    sizing_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def attach_action_lift_audit(
    *,
    recommendation: PortfolioRecommendation,
    candidates: list[PortfolioCandidate],
    snapshot: AccountSnapshot,
    profile: PortfolioProfile,
) -> PortfolioRecommendation:
    audit = build_action_lift_audit(
        recommendation=recommendation,
        candidates=candidates,
        snapshot=snapshot,
        profile=profile,
    )
    entry_by_ticker = {entry["ticker"]: entry for entry in audit.get("entries", []) if isinstance(entry, dict)}
    annotated_actions: list[PortfolioAction] = []
    for action in recommendation.actions:
        entry = entry_by_ticker.get(action.canonical_ticker)
        if not entry:
            annotated_actions.append(action)
            continue
        annotated_actions.append(
            PortfolioAction(
                **{
                    **action.__dict__,
                    "data_health": {
                        **action.data_health,
                        "action_lift": entry,
                        "lift_status": entry.get("lift_status"),
                        "opportunity_cost_score": entry.get("opportunity_cost_score"),
                        "opportunity_capture_score": entry.get("opportunity_capture_score"),
                        "pilot_allowed": entry.get("pilot_allowed"),
                        "full_size_allowed": entry.get("full_size_allowed"),
                    },
                }
            )
        )
    return PortfolioRecommendation(
        **{
            **recommendation.__dict__,
            "actions": tuple(annotated_actions),
            "action_lift_audit": audit,
            "data_health_summary": {
                **recommendation.data_health_summary,
                "action_lift_audit": _summary_without_entries(audit),
            },
        }
    )


def build_action_lift_audit(
    *,
    recommendation: PortfolioRecommendation,
    candidates: list[PortfolioCandidate],
    snapshot: AccountSnapshot,
    profile: PortfolioProfile,
) -> dict[str, Any]:
    candidate_by_ticker = {candidate.instrument.canonical_ticker: candidate for candidate in candidates}
    action_by_ticker = {action.canonical_ticker: action for action in recommendation.actions}
    ordered_tickers: list[str] = []
    for action in recommendation.actions:
        if action.canonical_ticker not in ordered_tickers:
            ordered_tickers.append(action.canonical_ticker)
    for candidate in candidates:
        ticker = candidate.instrument.canonical_ticker
        if ticker not in ordered_tickers:
            ordered_tickers.append(ticker)
    entries = []
    for ticker in ordered_tickers:
        candidate = candidate_by_ticker.get(ticker)
        action = action_by_ticker.get(ticker)
        if action is None and candidate is None:
            continue
        entries.append(
            _entry_for_action(
                action=action or _synthetic_action_for_candidate(candidate),
                candidate=candidate,
                snapshot=snapshot,
                profile=profile,
                candidate_only=action is None,
            )
        )
    payload_entries = [entry.to_dict() for entry in entries]
    status_counts: dict[str, int] = {}
    for entry in entries:
        status_counts[entry.lift_status] = status_counts.get(entry.lift_status, 0) + 1
    warning_entries = [entry for entry in entries if entry.lift_status in _WARNING_STATUSES]
    actionable_not_ordered = [
        entry
        for entry in entries
        if entry.stock_entry_state == "ACTIONABLE_NOW"
        and entry.stock_thesis in {"BULLISH", "ADD", "STARTER", "EXPAND"}
        and not entry.proposed_order_exists
    ]
    return {
        "summary": {
            "total": len(entries),
            "status_counts": dict(sorted(status_counts.items())),
            "warning_count": len(warning_entries),
            "actionable_not_ordered_count": len(actionable_not_ordered),
            "opportunity_capture_enabled": bool(getattr(profile, "opportunity_capture_enabled", False)),
            "opportunity_capture_sleeve_nav_pct": float(getattr(profile, "opportunity_capture_sleeve_nav_pct", 0.0) or 0.0),
            "opportunity_capture_per_pilot_nav_pct": float(getattr(profile, "opportunity_capture_per_pilot_nav_pct", 0.0) or 0.0),
        },
        "entries": payload_entries,
        "warnings": [
            _warning_text(entry)
            for entry in warning_entries
            if entry.lift_status in {"ACTION_LIFT_FAILURE", "BUY_SIGNAL_RELABELED_AS_SELL_SIDE"}
        ],
    }


def _entry_for_action(
    *,
    action: PortfolioAction,
    candidate: PortfolioCandidate | None,
    snapshot: AccountSnapshot,
    profile: PortfolioProfile,
    candidate_only: bool = False,
) -> ActionLiftAuditEntry:
    health = dict(action.data_health or {})
    if candidate is not None:
        health = {**candidate.data_health, **health}
    thesis = _stock_thesis(candidate, action)
    entry_state = _stock_entry_state(health)
    timing = str(health.get("execution_timing_state") or "").strip().upper()
    position_state = _position_state(snapshot.find_position(action.canonical_ticker))
    proposed_now_exists = int(action.delta_krw_now or 0) != 0
    conditional_order_exists = _conditional_order_exists(action)
    proposed_order_exists = proposed_now_exists or conditional_order_exists
    reasons = _block_reasons(action, candidate, snapshot=snapshot, profile=profile)
    if candidate_only:
        reasons.append("CANDIDATE_ACTIONABLE_NOT_LIFTED")
    buy_now_visible = action.action_now in _NOW_BUY_ACTIONS
    buy_trigger_visible = action.action_if_triggered in _TRIGGER_BUY_ACTIONS or action.action_now in _CONDITIONAL_BUY_ACTIONS
    buy_visible = buy_now_visible or buy_trigger_visible
    actionable = entry_state == "ACTIONABLE_NOW" or timing == "PILOT_READY"
    constructive = thesis in {"BULLISH", "ADD", "STARTER", "EXPAND"} or str(action.portfolio_relative_action).upper() == "ADD"
    sell_side_only = _sell_side_intent(action) in _SELL_SIDE_ACTIONS and not buy_visible
    stop_distance_pct = _stop_distance_pct(action, candidate, health)
    pilot_budget = compute_opportunity_pilot_budget(
        nav_krw=snapshot.account_value_krw,
        available_cash_krw=snapshot.available_cash_krw,
        min_cash_buffer_krw=snapshot.constraints.min_cash_buffer_krw,
        stop_distance_pct=stop_distance_pct,
        profile=profile,
    )
    for reason in pilot_budget.get("block_reasons") or []:
        reason_text = str(reason).strip()
        if reason_text and reason_text != "opportunity_capture_disabled":
            reasons.append(reason_text)
    reasons = list(dict.fromkeys(reasons))
    block_categories = _block_categories(reasons)
    hard_blocked = bool(set(block_categories) & _PILOT_HARD_BLOCK_CATEGORIES)
    prism_soft = (
        str(action.prism_agreement or health.get("prism_agreement") or "").startswith("conflict_prism_sell_ta_buy")
        and bool(action.review_required)
        and buy_visible
        and not hard_blocked
    )

    if proposed_now_exists and buy_now_visible:
        lift_status = "PRISM_SOFT_BLOCK_PILOT_ALLOWED" if prism_soft else "ORDER_PROPOSED"
    elif buy_now_visible and action.budget_blocked_actionable:
        lift_status = "BUDGET_BLOCKED"
    elif prism_soft:
        lift_status = "PRISM_SOFT_BLOCK_PILOT_ALLOWED"
    elif buy_now_visible or buy_trigger_visible or conditional_order_exists:
        lift_status = "PILOT_VISIBLE_NO_ORDER" if actionable or constructive else "NOT_ACTIONABLE"
    elif actionable and constructive and sell_side_only:
        lift_status = "BUY_SIGNAL_RELABELED_AS_SELL_SIDE"
    elif actionable and constructive and not buy_visible:
        lift_status = "HARD_BLOCKED" if hard_blocked else "ACTION_LIFT_FAILURE"
    elif hard_blocked:
        lift_status = "HARD_BLOCKED"
    else:
        lift_status = "NOT_ACTIONABLE"

    pilot_allowed = _pilot_allowed(
        lift_status,
        buy_visible=buy_visible,
        hard_blocked=hard_blocked,
        actionable=actionable,
        constructive=constructive,
    )
    full_size_allowed = bool(action.action_now == "ADD_NOW" and proposed_now_exists and not prism_soft and not hard_blocked)
    opportunity_cost = _opportunity_cost_score(
        action=action,
        thesis=thesis,
        entry_state=entry_state,
        timing=timing,
        hard_blocked=hard_blocked,
        position_state=position_state,
    )
    capture = _opportunity_capture_score(
        action=action,
        candidate=candidate,
        health=health,
        thesis=thesis,
        entry_state=entry_state,
        timing=timing,
        position_state=position_state,
        block_categories=block_categories,
        opportunity_cost_score=opportunity_cost,
    )
    return ActionLiftAuditEntry(
        ticker=action.canonical_ticker,
        display_name=action.display_name,
        stock_thesis=thesis,
        stock_entry_state=entry_state,
        stock_execution_timing=timing or "UNKNOWN",
        account_position_state=position_state,
        account_action_now=action.action_now,
        account_action_if_triggered=action.action_if_triggered,
        proposed_now_exists=proposed_now_exists,
        conditional_order_exists=conditional_order_exists,
        proposed_order_exists=proposed_order_exists,
        block_reasons=reasons,
        block_categories=block_categories,
        pilot_allowed=pilot_allowed,
        full_size_allowed=full_size_allowed,
        opportunity_cost_score=opportunity_cost,
        opportunity_capture_score=capture["score"],
        opportunity_capture_components=capture["components"],
        lift_status=lift_status,
        lift_failure=lift_status == "ACTION_LIFT_FAILURE",
        next_valid_action=_next_valid_action(action, health, lift_status=lift_status),
        pilot_budget_krw=pilot_budget.get("pilot_budget_krw"),
        max_loss_krw=pilot_budget.get("max_loss_krw"),
        sleeve_total_krw=pilot_budget.get("sleeve_total_krw"),
        stop_distance_pct=stop_distance_pct,
        sizing_blocked=bool(pilot_budget.get("sizing_blocked")),
        sizing_reason=str(pilot_budget.get("budget_reason") or ""),
    )


def _synthetic_action_for_candidate(candidate: PortfolioCandidate | None) -> PortfolioAction:
    if candidate is None:
        raise ValueError("candidate is required for a synthetic action lift audit row")
    return PortfolioAction(
        canonical_ticker=candidate.instrument.canonical_ticker,
        display_name=candidate.instrument.display_name,
        priority=999,
        confidence=candidate.confidence,
        action_now="NO_ACCOUNT_ACTION",
        delta_krw_now=0,
        target_weight_now=0.0,
        action_if_triggered="WATCH",
        delta_krw_if_triggered=0,
        target_weight_if_triggered=0.0,
        trigger_conditions=candidate.trigger_conditions,
        rationale=candidate.rationale,
        data_health=dict(candidate.data_health or {}),
        strategy_state=candidate.strategy_state,
        execution_feasibility_now=candidate.execution_feasibility_now,
        portfolio_relative_action="WATCH",
        relative_action_reason=candidate.relative_action_reason,
        relative_action_reason_codes=candidate.relative_action_reason_codes,
        risk_action=candidate.risk_action,
        risk_action_reason_codes=candidate.risk_action_reason_codes,
        risk_action_level=candidate.risk_action_level,
        sell_side_category=candidate.sell_side_category,
        sell_intent=candidate.sell_intent,
        sell_trigger_status=candidate.sell_trigger_status,
        sell_size_plan=candidate.sell_size_plan,
        thesis_after_sell=candidate.thesis_after_sell,
        position_metrics=candidate.position_metrics,
        profit_taking_plan=candidate.profit_taking_plan,
        budget_blocked_actionable=candidate.budget_blocked_actionable,
        stale_but_triggerable=candidate.stale_but_triggerable,
        funding_source_score=candidate.funding_source_score,
        capital_reallocation_rank=candidate.capital_reallocation_rank,
        decision_source=candidate.decision_source,
        timing_readiness=candidate.timing_readiness,
        reason_codes=candidate.reason_codes,
        review_required=candidate.review_required,
        trigger_type=None,
        gate_reasons=candidate.gate_reasons,
        sector=candidate.sector,
        external_signals=candidate.external_signals,
        prism_agreement=candidate.prism_agreement,
        external_signal_score_delta=candidate.external_signal_score_delta,
        external_signal_notes=candidate.external_signal_notes,
        buy_matrix=candidate.buy_matrix,
    )


def _conditional_order_exists(action: PortfolioAction) -> bool:
    if int(action.delta_krw_if_triggered or 0) != 0:
        return True
    now = str(action.action_now or "").strip().upper()
    triggered = str(action.action_if_triggered or "").strip().upper()
    return now in _CONDITIONAL_BUY_ACTIONS or triggered in _CONDITIONAL_BUY_ACTIONS


def _stock_thesis(candidate: PortfolioCandidate | None, action: PortfolioAction) -> str:
    if candidate is not None:
        stance = str(candidate.stance or "").strip().upper()
        if stance:
            return stance
        entry = str(candidate.entry_action or "").strip().upper()
        if entry:
            return entry
    relative = str(action.portfolio_relative_action or "").strip().upper()
    if relative == "ADD":
        return "BULLISH"
    return relative or "UNKNOWN"


def _stock_entry_state(health: dict[str, Any]) -> str:
    state = str(health.get("execution_decision_state") or health.get("decision_state") or "").strip().upper()
    timing = str(health.get("execution_timing_state") or "").strip().upper()
    if state:
        return state
    if timing == "PILOT_READY":
        return "ACTIONABLE_NOW"
    if timing in {"CLOSE_CONFIRM_PENDING", "CLOSE_CONFIRMED", "NEXT_DAY_FOLLOWTHROUGH_PENDING"}:
        return "TRIGGERED_PENDING_CLOSE"
    return "WAIT"


def _position_state(position: Any | None) -> str:
    if position is None:
        return "NOT_HELD"
    quantity = float(getattr(position, "quantity", 0.0) or 0.0)
    available = float(getattr(position, "available_qty", 0.0) or 0.0)
    if quantity > 0 and available < quantity:
        return "PARTIAL"
    return "HELD"


def _block_reasons(
    action: PortfolioAction,
    candidate: PortfolioCandidate | None,
    *,
    snapshot: AccountSnapshot,
    profile: PortfolioProfile,
) -> list[str]:
    reasons: list[str] = []
    for values in (
        action.gate_reasons,
        action.reason_codes,
        action.relative_action_reason_codes,
        action.risk_action_reason_codes,
        candidate.gate_reasons if candidate else tuple(),
        candidate.reason_codes if candidate else tuple(),
    ):
        reasons.extend(str(item).strip() for item in values or [] if str(item).strip())
    if action.budget_blocked_actionable:
        reasons.append("budget_or_cash_buffer_blocked")
    if action.action_now == "STARTER_NOW" and int(action.delta_krw_now or 0) <= 0:
        account_value = max(snapshot.account_value_krw, 1)
        if bool(getattr(profile, "opportunity_capture_enabled", False)):
            per_pilot_cap = int(account_value * float(getattr(profile, "opportunity_capture_per_pilot_nav_pct", 0.0) or 0.0) / 100.0)
            if per_pilot_cap < snapshot.constraints.min_trade_krw:
                reasons.append("pilot_allowed_below_min_trade")
    if str(action.prism_agreement or "").startswith("conflict_"):
        reasons.append("prism_conflict_review_required")
    return list(dict.fromkeys(reasons))


def _block_categories(reasons: list[str]) -> list[str]:
    categories: list[str] = []
    reason_text = " ".join(str(reason or "") for reason in reasons)
    reason_lower = reason_text.lower()
    for category, tokens in _BLOCK_CATEGORY_TOKENS.items():
        for token in tokens:
            token_text = str(token)
            if (token_text.isascii() and token_text.lower() in reason_lower) or (
                not token_text.isascii() and token_text in reason_text
            ):
                categories.append(category)
                break
    return list(dict.fromkeys(categories))


def _sell_side_intent(action: PortfolioAction) -> str:
    intent = str(action.sell_intent or "").strip().upper()
    if intent:
        return intent
    return str(action.portfolio_relative_action or "").strip().upper()


def _pilot_allowed(
    lift_status: str,
    *,
    buy_visible: bool,
    hard_blocked: bool,
    actionable: bool,
    constructive: bool,
) -> bool:
    if hard_blocked:
        return False
    if lift_status in {"ORDER_PROPOSED", "BUDGET_BLOCKED", "PILOT_VISIBLE_NO_ORDER", "PRISM_SOFT_BLOCK_PILOT_ALLOWED"}:
        return True
    if lift_status == "ACTION_LIFT_FAILURE":
        return bool(actionable and constructive)
    return bool(actionable and constructive and buy_visible)


def _opportunity_cost_score(
    *,
    action: PortfolioAction,
    thesis: str,
    entry_state: str,
    timing: str,
    hard_blocked: bool,
    position_state: str,
) -> float:
    score = 0.0
    if thesis in {"BULLISH", "ADD", "STARTER", "EXPAND"}:
        score += 0.25
    if entry_state == "ACTIONABLE_NOW":
        score += 0.25
    if timing == "PILOT_READY":
        score += 0.15
    if position_state == "NOT_HELD":
        score += 0.10
    score += max(0.0, min(float(action.confidence or 0.0), 1.0)) * 0.15
    if action.data_health.get("session_vwap_ok") is True:
        score += 0.05
    if action.data_health.get("relative_volume_ok") is True:
        score += 0.05
    if str(action.prism_agreement or "").startswith("conflict_"):
        score -= 0.05
    if hard_blocked:
        score -= 0.20
    return round(max(0.0, min(score, 1.0)), 4)


def _opportunity_capture_score(
    *,
    action: PortfolioAction,
    candidate: PortfolioCandidate | None,
    health: dict[str, Any],
    thesis: str,
    entry_state: str,
    timing: str,
    position_state: str,
    block_categories: list[str],
    opportunity_cost_score: float,
) -> dict[str, Any]:
    text = " ".join(
        str(value or "")
        for value in (
            action.rationale,
            action.relative_action_reason,
            candidate.rationale if candidate else "",
            candidate.setup_quality if candidate else "",
            " ".join(action.trigger_conditions or ()),
            " ".join(action.reason_codes or ()),
            " ".join(candidate.reason_codes if candidate else ()),
        )
    ).lower()
    data_coverage = candidate.data_coverage if candidate else {}
    news_count = _int_or_zero(data_coverage.get("company_news_count"))
    disclosure_count = _int_or_zero(data_coverage.get("disclosures_count"))
    components = {
        "fundamental_catalyst_score": _component_score(
            85.0 if any(token in text for token in ("실적", "공급계약", "계약", "earnings", "contract", "guidance", "report")) else 0.0,
            15.0 * min(news_count, 3),
            20.0 if disclosure_count > 0 else 0.0,
        ),
        "breakout_score": _component_score(
            55.0 if entry_state == "ACTIONABLE_NOW" else 0.0,
            25.0 if timing == "PILOT_READY" else 0.0,
            20.0 if any(token in text for token in ("breakout", "돌파", "신고가", "52w", "52주")) else 0.0,
        ),
        "volume_value_score": _component_score(
            45.0 if health.get("relative_volume_ok") is True else 0.0,
            35.0 if health.get("session_vwap_ok") is True else 0.0,
            20.0 if any(token in text for token in ("거래대금", "volume", "rvol", "vwap")) else 0.0,
        ),
        "sector_leadership_score": _component_score(
            50.0 if any(token in text for token in ("leader", "주도", "sector", "테마")) else 0.0,
            20.0 if action.sector or (candidate and candidate.sector) else 0.0,
        ),
        "liquidity_score": _component_score(
            45.0 if _float_or_none(health.get("last_price")) is not None else 0.0,
            30.0 if str(health.get("execution_data_quality") or "").upper() == "REALTIME_EXECUTION_READY" else 0.0,
            25.0 if "data_quality_block" not in block_categories else -25.0,
        ),
        "source_confirmation_score": _component_score(
            30.0 if data_coverage.get("social_source") == "dedicated" else 0.0,
            20.0 * min(news_count, 2),
            30.0 if disclosure_count > 0 else 0.0,
            20.0 if candidate and candidate.structured_decision else 0.0,
        ),
        "missed_upside_risk_score": _component_score(
            opportunity_cost_score * 100.0,
            15.0 if position_state == "NOT_HELD" and thesis in {"BULLISH", "ADD", "STARTER", "EXPAND"} else 0.0,
        ),
        "valuation_risk_penalty": _component_score(35.0 if any(token in text for token in ("valuation", "밸류", "per", "pbr", "고평가")) else 0.0),
        "account_concentration_penalty": _component_score(70.0 if "account_concentration_block" in block_categories else 0.0),
        "disclosure_risk_penalty": _component_score(
            90.0 if {"disclosure_hard_block", "market_warning_block"} & set(block_categories) else 0.0
        ),
    }
    score = (
        0.20 * components["fundamental_catalyst_score"]
        + 0.20 * components["breakout_score"]
        + 0.15 * components["volume_value_score"]
        + 0.15 * components["sector_leadership_score"]
        + 0.10 * components["liquidity_score"]
        + 0.10 * components["source_confirmation_score"]
        + 0.10 * components["missed_upside_risk_score"]
        - 0.15 * components["valuation_risk_penalty"]
        - 0.15 * components["account_concentration_penalty"]
        - 0.20 * components["disclosure_risk_penalty"]
    )
    return {
        "score": round(max(0.0, min(score, 100.0)), 2),
        "components": {key: round(value, 2) for key, value in components.items()},
    }


def _component_score(*values: float) -> float:
    return max(0.0, min(sum(float(value or 0.0) for value in values), 100.0))


def _stop_distance_pct(
    action: PortfolioAction,
    candidate: PortfolioCandidate | None,
    health: dict[str, Any],
) -> float | None:
    for container in (health, action.position_metrics, candidate.position_metrics if candidate else {}):
        if not isinstance(container, dict):
            continue
        for key in ("pilot_stop_distance_pct", "stop_distance_pct", "stop_distance_percent"):
            value = _float_or_none(container.get(key))
            if value is not None and value >= 0:
                return round(value, 4)
    last_price = _float_or_none(health.get("last_price") or health.get("current_price"))
    risk_level = action.risk_action_level or (candidate.risk_action_level if candidate else None)
    if last_price and isinstance(risk_level, dict):
        stop_price = _float_or_none(risk_level.get("price") or risk_level.get("low") or risk_level.get("high"))
        if stop_price and stop_price > 0:
            return round(abs(last_price - stop_price) / last_price * 100.0, 4)
    return None


def _float_or_none(value: Any) -> float | None:
    if value in (None, "") or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int_or_zero(value: Any) -> int:
    number = _float_or_none(value)
    return int(number) if number is not None else 0


def _next_valid_action(action: PortfolioAction, health: dict[str, Any], *, lift_status: str) -> str:
    invalidation = str(health.get("pilot_invalidation_text") or "").strip()
    conditions = "; ".join(str(item).strip() for item in action.trigger_conditions if str(item).strip())
    if lift_status == "PRISM_SOFT_BLOCK_PILOT_ALLOWED":
        return "full-size 금지, PRISM 충돌 수동 확인 후 pilot만 검토"
    if action.action_now in _NOW_BUY_ACTIONS:
        return invalidation or conditions or "pilot sizing and cash buffer 확인"
    if action.action_if_triggered in _TRIGGER_BUY_ACTIONS:
        return conditions or "종가/다음 거래일 조건 확인 후 starter 검토"
    if lift_status == "BUY_SIGNAL_RELABELED_AS_SELL_SIDE":
        return conditions or invalidation or "sell-side 분류와 pilot 가능 여부 재검토"
    if lift_status == "ACTION_LIFT_FAILURE":
        return conditions or invalidation or "block_reason 확인 후 starter/pilot 전환 여부 결정"
    return conditions or invalidation or "추가 조건 없음"


def _warning_text(entry: ActionLiftAuditEntry) -> str:
    return (
        f"{entry.ticker} {entry.display_name}: {entry.stock_entry_state}/{entry.stock_execution_timing} "
        f"신호가 계좌 액션 {entry.account_action_now}/{entry.account_action_if_triggered}로 처리됨 "
        f"({entry.lift_status})."
    )


def _summary_without_entries(audit: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary": audit.get("summary") or {},
        "warnings": audit.get("warnings") or [],
    }
