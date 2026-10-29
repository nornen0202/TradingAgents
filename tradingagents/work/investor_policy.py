"""Dated investment plans are readable independently of an order's quote TTL.

This projection never fetches prices, renews observations, or enables orders.
Review windows are editorial checkpoints, not claims that a thesis stays true.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime, timedelta
import math
from zoneinfo import ZoneInfo

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
    try:
        return (float(value) if isinstance(value, (int, float)) and not isinstance(value, bool)
                and math.isfinite(value) and value > 0 else None)
    except OverflowError:
        return None


def _transport_value(value, exclusions: list[str], path=""):
    """Keep partial source responses usable by JSON.parse, without NaN tokens."""
    if isinstance(value, float) and not math.isfinite(value):
        exclusions.append(path)
        return None
    if isinstance(value, dict):
        return {key: _transport_value(item, exclusions, f"{path}/{key}") for key, item in value.items()}
    if isinstance(value, list):
        return [_transport_value(item, exclusions, f"{path}/{index}") for index, item in enumerate(value)]
    return value


def _research_clock_errors(thesis: dict, *, market: str, now: datetime) -> list[str]:
    errors = []
    available = aware_datetime(thesis.get("analysis_asof"))
    if available is None or available > now:
        errors.append("ANALYSIS_ASOF_INVALID_OR_FUTURE")
    local_date = now.astimezone(ZoneInfo("America/New_York" if market.upper() == "US" else "Asia/Seoul")).date()
    # Availability, decision date and referenced price date are different. A
    # valid availability timestamp must not legitimize future dated evidence.
    # Optional absent legacy date labels do not override the required clock.
    for field in ("decision_asof", "price_reference_date", "analysis_trade_date"):
        raw = thesis.get(field)
        if raw in (None, ""):
            continue
        try:
            if isinstance(raw, str) and len(raw) == 10:
                valid = date.fromisoformat(raw) <= local_date
            else:
                clock = aware_datetime(raw)
                valid = clock is not None and clock <= now
        except (ValueError, TypeError):
            valid = False
        if not valid:
            errors.append(field.upper() + "_INVALID_OR_FUTURE")
    return errors


def _normalize_thesis(thesis: dict, exclusions: list[str]) -> None:
    from .runtime import WorkRuntimeError, _validate_condition_list, _has_meaningful_contract_value
    for field in ("entry_conditions", "invalidation_conditions"):
        values = thesis.get(field)
        if not isinstance(values, list):
            values = []
            exclusions.append(field + ":MISSING_CONDITIONS")
        accepted = []
        for index, value in enumerate(values):
            try:
                _validate_condition_list([value], ticker="source", field=field, require_anchor=False)
            except WorkRuntimeError:
                exclusions.append(f"{field}/{index}:UNUSABLE_CONDITION")
            else:
                accepted.append(value)
        thesis[field] = accepted
    for field, fallback in (
        ("invalidation_action", "무효화·축소 조건을 먼저 확인하고 계획을 재평가"),
        ("position_sizing", "수량 산출 없음; 현재 보유·현금·위험 한도로 결정"),
        ("horizon", "원분석 기간 미지정; 표시된 검토일까지 재평가"),
    ):
        if not _has_meaningful_contract_value(thesis.get(field)):
            thesis[field] = fallback
            exclusions.append(field + ":SOURCE_VALUE_UNAVAILABLE")
    confidence = thesis.get("confidence")
    if (isinstance(confidence, bool) or not isinstance(confidence, (int, float))
            or not 0 <= confidence <= 1):
        thesis["confidence"] = 0.0
        thesis["confidence_note"] = "원분석 신뢰도 미제공 또는 형식 오류; 0은 미확인 표시"
        exclusions.append("confidence:SOURCE_VALUE_UNAVAILABLE")
    if not thesis["entry_conditions"] or not thesis["invalidation_conditions"]:
        thesis["data_needed_reason"] = "원분석의 사용 가능한 진입 또는 무효화 조건이 없어 임의 보충하지 않음"


def price_zones(thesis: dict) -> tuple[list[dict], list[str]]:
    """Keep sourced ranges; label any policy tolerance, never widen a stop.

    A support can describe either an entry or an exit. Its original rule and
    stance remain binding; being inside a zone alone does not mean buy.
    """
    zones, excluded = [], []
    execution_levels = thesis.get("execution_levels")
    if execution_levels is not None and not isinstance(execution_levels, dict):
        return [], ["INVALID_EXECUTION_LEVELS"]
    levels = (execution_levels or {}).get("levels") or []
    if not isinstance(levels, list):
        return [], ["INVALID_PRICE_LEVELS"]
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
        "status": "DATA_NEEDED" if not dated else "REVIEW_REQUIRED" if now >= review or exclusions or row.get("investor_exclusions") else "CONDITIONAL_PLAN",
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
        "source_exclusions": list(row.get("investor_exclusions") or []),
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
    transport_exclusions = []
    result = _transport_value(result, transport_exclusions)
    current = result.get("current") or {}
    current["transport_exclusions"] = transport_exclusions
    rows = (current.get("bundle") or {}).get("strategy_table") or []
    for index, row in enumerate(rows):
        thesis = row.get("thesis") or {}
        clock_errors = _research_clock_errors(thesis, market=str(result.get("market") or ""), now=now)
        quote = aware_datetime(row.get("market_data_asof"))
        exclusions = ["NON_FINITE_SOURCE_VALUE:" + path for path in transport_exclusions
                      if path.startswith(f"/current/bundle/strategy_table/{index}/")]
        if clock_errors:
            # Excluded source text must not leak into the composition as evidence.
            keep = {k: row[k] for k in ("ticker", "display_name", "portfolio_role", "is_held",
                                       "display_priority", "quality", "execution") if k in row}
            row.clear()
            row.update(keep)
            row["thesis"] = {"stance": "RESEARCH", "confidence": 0.0, "analysis_asof": None,
                             "entry_conditions": [], "invalidation_conditions": [],
                             "invalidation_action": "분석 기준시각 확인 후 계획 재작성",
                             "data_needed_reason": "원분석·의사결정·가격 기준시각이 없거나 잘못됐거나 미래여서 근거에서 제외"}
            exclusions.extend(clock_errors)
        elif quote is None or quote > now:
            for field in ("last_price", "session_vwap", "relative_volume", "day_high", "day_low",
                          "price_change_pct", "vwap_distance_pct", "spread_bps", "trading_value",
                          "execution_condition_ko", "risk_condition_ko", "reason_codes_ko",
                          "sync_summary_ko", "vwap_position_ko"):
                row.pop(field, None)
            row["data_status_ko"] = "시각 미검증 시세 제외; 별도 날짜가 검증된 분석만 사용"
        row["investor_exclusions"] = exclusions
        _normalize_thesis(row["thesis"], exclusions)
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
        for field in ("stance", "risk_action", "risk_action_level", "risk_action_reason", "risk_limits",
                      "conditional_entry_valid_until", "entry_conditions", "invalidation_conditions",
                      "execution_levels", "invalidation_action", "position_sizing", "profit_taking_plan", "horizon"):
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
    coverage_label = {"COMPLETE": "전체 종목 수신", "INCOMPLETE": "일부 누락", "UNVERIFIED": "범위 미확인"}.get(coverage.get("status"), "범위 미확인")
    rows = (current.get("bundle") or {}).get("strategy_table") or []
    excluded = sum((row.get("investment_plan") or {}).get("status") == "DATA_NEEDED" for row in rows)
    if excluded:
        coverage_label += f" · 날짜 검증 불가 {excluded}종목 근거 제외"
    return (f"**원분석 기준 {receipt.get('analysis_trade_date_latest') or '확인 불가'} · {coverage_label}**\n\n"
            "지연 시세로 읽는 조건부 계획입니다. 거래 전 현재 가격·무효화 조건을 확인하세요.\n\n")
