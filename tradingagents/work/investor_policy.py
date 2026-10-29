"""Dated investment plans are readable independently of an order's quote TTL.

This projection never fetches prices, renews observations, or enables orders.
Review windows are editorial checkpoints, not claims that a thesis stays true.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta
import math

from tradingagents.dataflows.market_policy import aware_datetime
from tradingagents.schemas.decision import explicit_price_range_conflicts

SCHEMA = "tradingagents.investor-publication/v1"
POLICY = {
    "schema": SCHEMA,
    "profile": "investor",
    "publication_requires_live_quotes": False,
    "publication_requires_open_session": False,
    "partial_coverage_publishable": True,
    "execution_eligible": False,
    "review_calendar_days": {"short": 7, "medium": 30, "long": 90},
    "single_price_review_tolerance_pct": 1.0,
    "review_window_is_not_order_validity": True,
}


def _number(value):
    return (float(value) if isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and value > 0 else None)


def price_zones(thesis: dict) -> tuple[list[dict], list[str]]:
    """Keep sourced ranges; label any policy tolerance, never widen a stop.

    A support can describe either an entry or an exit. Its original rule and
    stance remain binding; being inside a zone alone does not mean buy.
    """
    zones, excluded = [], []
    levels = (thesis.get("execution_levels") or {}).get("levels") or []
    for index, level in enumerate(levels):
        if not isinstance(level, dict):
            excluded.append(f"level_{index}:INVALID_LEVEL")
            continue
        price, low, high = (_number(level.get(k)) for k in ("price", "low", "high"))
        kind = str(level.get("level_type") or "").upper()
        supplied_range = level.get("low") is not None or level.get("high") is not None
        if (supplied_range and (low is None or high is None or low > high
                or (price is not None and not low <= price <= high))
                or explicit_price_range_conflicts({"execution_levels": {"levels": [level]}})):
            excluded.append(f"level_{index}:CONFLICTING_PRICE_RANGE")
            continue
        if supplied_range:
            basis = "SOURCE_RANGE"
        elif price is not None:
            # Stops, invalidators and all sell-side thresholds stay exact.
            low = high = price
            basis = "SOURCE_LEVEL"
            if kind in {"PULLBACK", "BREAKOUT"} and thesis.get("stance") == "BUY":
                tolerance = POLICY["single_price_review_tolerance_pct"] / 100
                low = price if kind == "BREAKOUT" else round(price * (1 - tolerance), 4)
                high = round(price * (1 + tolerance), 4)
                basis = "POLICY_REVIEW_BAND_1_PERCENT"
        else:
            excluded.append(f"level_{index}:MISSING_PRICE")
            continue
        zones.append({"label": level.get("label"), "level_type": kind,
                      "low": low, "high": high, "source_price": price,
                      "currency": level.get("currency"), "basis": basis,
                      "confirmation": level.get("confirmation"),
                      "source_level_ref": f"/thesis/execution_levels/levels/{index}",
                      "zone_alone_is_not_a_trade_signal": True})
    return zones, excluded


def investment_plan(row: dict, *, now: datetime) -> dict:
    thesis = row.get("thesis") or {}
    analysis = aware_datetime(thesis.get("analysis_asof"))
    dated = analysis is not None and analysis <= now
    days = POLICY["review_calendar_days"].get(str(thesis.get("horizon") or "").lower(), 7)
    review = analysis + timedelta(days=days) if dated else None
    zones, exclusions = price_zones(thesis) if dated else ([], ["ANALYSIS_DATE_UNVERIFIED"])
    if dated and (not thesis.get("entry_conditions") or not thesis.get("invalidation_conditions")):
        exclusions.append("PLAN_CONDITIONS_INCOMPLETE")
    risk = str(thesis.get("risk_action") or "NONE").upper()
    stance = thesis.get("stance") if dated else "RESEARCH"
    reducing = stance in {"REDUCE", "SELL"} or risk in {"REDUCE_RISK", "STOP_LOSS", "EXIT", "TAKE_PROFIT"}
    return {
        "schema": "tradingagents.investment-plan/v1",
        "status": "DATA_NEEDED" if not dated else "REVIEW_REQUIRED" if now >= review or exclusions else "CONDITIONAL_PLAN",
        "stance": stance,
        "risk_action": risk if dated else "NONE",
        "purpose": "RISK_REDUCTION" if reducing else "ENTRY_REVIEW" if stance == "BUY" else "MONITOR",
        "analysis_as_of": analysis.isoformat() if dated else None,
        "review_window": {"from": analysis.isoformat() if dated else None,
                          "review_by": review.isoformat() if review else None,
                          "calendar_days": days, "basis": "EDITORIAL_REVIEW_POLICY_NOT_ORDER_EXPIRY"},
        "source_trigger_valid_until": thesis.get("conditional_entry_valid_until") if dated else None,
        "price_zones": zones,
        "excluded_levels": exclusions,
        "conditions_ref": "/thesis/entry_conditions",
        "invalidation_conditions_ref": "/thesis/invalidation_conditions",
        "invalidation_action_ref": "/thesis/invalidation_action",
        "sizing_ref": "/thesis/position_sizing",
        "execution_eligible": False,
        "before_acting": (["현재 보유 수량과 매도 가능 여부 확인", "현재 가격과 원래 축소·무효화 조건 확인"] if reducing else
                          ["현재 가격과 원래 진입·무효화 조건 확인", "가용 현금·집중도·손실 한도 확인"]),
    }


def project_investor_body(body: dict, *, now: datetime) -> dict:
    """Retain partial coverage and dated theses; isolate undated evidence by row."""
    if aware_datetime(now) is None:
        raise ValueError("Investor report cutoff must be timezone-aware")
    result = deepcopy(body)
    result["publication_policy"] = deepcopy(POLICY)
    current = result.get("current") or {}
    # The private overlay contains immediate order amounts and repeated engine
    # conditions. Dated thesis sizing and membership remain on each row; a
    # report-only consumer must not inherit a stale order ticket as advice.
    if current.pop("private_portfolio_overlay", None) is not None:
        current["private_execution_overlay_omitted"] = True
    rows = (current.get("bundle") or {}).get("strategy_table") or []
    for row in rows:
        thesis = row.get("thesis") or {}
        analysis = aware_datetime(thesis.get("analysis_asof"))
        quote = aware_datetime(row.get("market_data_asof"))
        if analysis is None or analysis > now:
            # Excluded source text must not leak into the composition as evidence.
            keep = {k: row[k] for k in ("ticker", "display_name", "portfolio_role", "is_held",
                                       "display_priority", "quality", "execution") if k in row}
            row.clear()
            row.update(keep)
            row["thesis"] = {"stance": "RESEARCH", "confidence": 0.0, "analysis_asof": None,
                             "entry_conditions": [], "invalidation_conditions": [],
                             "invalidation_action": "분석 기준시각 확인 후 계획 재작성",
                             "data_needed_reason": "원분석 기준시각이 없거나 잘못됐거나 미래여서 근거에서 제외"}
        elif quote is None or quote > now:
            for field in ("last_price", "session_vwap", "relative_volume", "day_high", "day_low",
                          "price_change_pct", "vwap_distance_pct", "spread_bps", "trading_value",
                          "execution_condition_ko", "risk_condition_ko", "reason_codes_ko",
                          "sync_summary_ko", "vwap_position_ko"):
                row.pop(field, None)
            row["data_status_ko"] = "시각 미검증 시세 제외; 별도 날짜가 검증된 분석만 사용"
        plan = investment_plan(row, now=now)
        row["investment_plan"] = plan
        execution = row.setdefault("execution", {})
        execution.update(readiness="NEEDS_LIVE_RECHECK", action_now=None, action_if_triggered=None)
        row["strategy_ko"] = {"BUY": "조건부 매수 계획", "HOLD": "보유·가격 구간 점검",
                              "REDUCE": "비중 축소 계획", "SELL": "매도 계획", "AVOID": "신규 진입 회피",
                              "RESEARCH": "추가 자료 필요"}.get(plan["stance"], "분석 참고")
    return result


def validate_investor_draft(draft: dict, packet: dict, *, now: datetime) -> None:
    policy = packet.get("body", {}).get("publication_policy")
    if not policy or policy.get("profile") != "investor":
        return
    from .runtime import WorkRuntimeError
    if draft.get("source_summary", {}).get("publication_policy") != policy:
        raise WorkRuntimeError("Investor publication policy must match the prepared packet")
    generated = aware_datetime(draft.get("generated_at"))
    if generated is None or generated > now:
        raise WorkRuntimeError("Investor report generation must have a valid, non-future clock")
    rows = {row["ticker"]: row for row in packet["body"].get("current", {}).get("bundle", {}).get("strategy_table", [])}
    for strategy in draft.get("strategies", []):
        row = rows.get(strategy.get("ticker"), {})
        if strategy.get("investment_plan") != row.get("investment_plan"):
            raise WorkRuntimeError("Investor plan must match the dated packet price zones and review window")
        for field in ("stance", "risk_action", "conditional_entry_valid_until",
                      "entry_conditions", "invalidation_conditions", "execution_levels"):
            if (strategy.get("thesis") or {}).get(field) != (row.get("thesis") or {}).get(field):
                raise WorkRuntimeError("Investor plan source conditions and levels must match the prepared packet")
        execution = strategy.get("execution") or {}
        if (execution.get("readiness") != "NEEDS_LIVE_RECHECK"
                or execution.get("action_now") or execution.get("action_if_triggered")):
            raise WorkRuntimeError("Investor reports provide plans, not executable orders")


def publication_notice(packet: dict) -> str:
    current = packet.get("body", {}).get("current", {})
    receipt = current.get("freshness_receipt") or {}
    coverage = current.get("universe_coverage") or {}
    coverage_label = {"COMPLETE": "전체 범위 확보", "INCOMPLETE": "일부 누락", "UNVERIFIED": "범위 미확인"}.get(coverage.get("status"), "범위 미확인")
    return (f"**원분석 기준 {receipt.get('analysis_trade_date_latest') or '확인 불가'} · {coverage_label}**\n\n"
            "지연 시세로 읽는 조건부 계획입니다. 거래 전 현재 가격·무효화 조건을 확인하세요.\n\n")
