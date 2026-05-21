from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .account_models import AccountSnapshot, PortfolioAction, PortfolioCandidate, PortfolioProfile, PortfolioRecommendation


_NOW_BUY_ACTIONS = {"ADD_NOW", "STARTER_NOW"}
_TRIGGER_BUY_ACTIONS = {"ADD_IF_TRIGGERED", "STARTER_IF_TRIGGERED"}
_SELL_SIDE_ACTIONS = {"TRIM_TO_FUND", "REDUCE_RISK", "TAKE_PROFIT", "STOP_LOSS", "EXIT"}
_HARD_BLOCK_REASON_TOKENS = {
    "blocked_new_entries_no_tool_calls",
    "blocked_new_entries_company_news_zero",
    "high_fallback_count",
    "data_missing_blocked_pilot",
    "max_single_name_weight_reached",
    "max_sector_weight_reached",
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
    proposed_order_exists: bool
    block_reasons: list[str]
    pilot_allowed: bool
    full_size_allowed: bool
    opportunity_cost_score: float
    lift_status: str
    next_valid_action: str

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
    entries = [
        _entry_for_action(
            action=action,
            candidate=candidate_by_ticker.get(action.canonical_ticker),
            snapshot=snapshot,
            profile=profile,
        )
        for action in recommendation.actions
    ]
    payload_entries = [entry.to_dict() for entry in entries]
    status_counts: dict[str, int] = {}
    for entry in entries:
        status_counts[entry.lift_status] = status_counts.get(entry.lift_status, 0) + 1
    warning_statuses = {
        "ACTION_LIFT_FAILURE",
        "BUY_SIGNAL_RELABELED_AS_SELL_SIDE",
        "BUDGET_BLOCKED",
        "PILOT_VISIBLE_NO_ORDER",
        "PRISM_SOFT_BLOCK_PILOT_ALLOWED",
    }
    warning_entries = [entry for entry in entries if entry.lift_status in warning_statuses]
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
) -> ActionLiftAuditEntry:
    health = dict(action.data_health or {})
    if candidate is not None:
        health = {**candidate.data_health, **health}
    thesis = _stock_thesis(candidate, action)
    entry_state = _stock_entry_state(health)
    timing = str(health.get("execution_timing_state") or "").strip().upper()
    position_state = _position_state(snapshot.find_position(action.canonical_ticker))
    proposed_order_exists = int(action.delta_krw_now or 0) != 0
    reasons = _block_reasons(action, candidate, snapshot=snapshot, profile=profile)
    hard_blocked = bool(set(reasons) & _HARD_BLOCK_REASON_TOKENS) or any("hard_block" in reason for reason in reasons)
    buy_now_visible = action.action_now in _NOW_BUY_ACTIONS
    buy_trigger_visible = action.action_if_triggered in _TRIGGER_BUY_ACTIONS
    buy_visible = buy_now_visible or buy_trigger_visible
    actionable = entry_state == "ACTIONABLE_NOW" or timing == "PILOT_READY"
    constructive = thesis in {"BULLISH", "ADD", "STARTER", "EXPAND"} or str(action.portfolio_relative_action).upper() == "ADD"
    sell_side_only = _sell_side_intent(action) in _SELL_SIDE_ACTIONS and not buy_visible
    prism_soft = (
        str(action.prism_agreement or health.get("prism_agreement") or "").startswith("conflict_prism_sell_ta_buy")
        and bool(action.review_required)
        and buy_visible
        and not hard_blocked
    )

    if proposed_order_exists and buy_now_visible:
        lift_status = "PRISM_SOFT_BLOCK_PILOT_ALLOWED" if prism_soft else "ORDER_PROPOSED"
    elif buy_now_visible and action.budget_blocked_actionable:
        lift_status = "BUDGET_BLOCKED"
    elif prism_soft:
        lift_status = "PRISM_SOFT_BLOCK_PILOT_ALLOWED"
    elif buy_now_visible or buy_trigger_visible:
        lift_status = "PILOT_VISIBLE_NO_ORDER" if actionable or constructive else "NOT_ACTIONABLE"
    elif actionable and constructive and sell_side_only:
        lift_status = "BUY_SIGNAL_RELABELED_AS_SELL_SIDE"
    elif actionable and constructive and not buy_visible:
        lift_status = "HARD_BLOCKED" if hard_blocked else "ACTION_LIFT_FAILURE"
    elif hard_blocked:
        lift_status = "HARD_BLOCKED"
    else:
        lift_status = "NOT_ACTIONABLE"

    pilot_allowed = _pilot_allowed(lift_status, buy_visible=buy_visible, hard_blocked=hard_blocked, actionable=actionable, constructive=constructive)
    full_size_allowed = bool(action.action_now == "ADD_NOW" and proposed_order_exists and not prism_soft and not hard_blocked)
    return ActionLiftAuditEntry(
        ticker=action.canonical_ticker,
        display_name=action.display_name,
        stock_thesis=thesis,
        stock_entry_state=entry_state,
        stock_execution_timing=timing or "UNKNOWN",
        account_position_state=position_state,
        account_action_now=action.action_now,
        account_action_if_triggered=action.action_if_triggered,
        proposed_order_exists=proposed_order_exists,
        block_reasons=reasons,
        pilot_allowed=pilot_allowed,
        full_size_allowed=full_size_allowed,
        opportunity_cost_score=_opportunity_cost_score(
            action=action,
            thesis=thesis,
            entry_state=entry_state,
            timing=timing,
            hard_blocked=hard_blocked,
            position_state=position_state,
        ),
        lift_status=lift_status,
        next_valid_action=_next_valid_action(action, health, lift_status=lift_status),
    )


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
