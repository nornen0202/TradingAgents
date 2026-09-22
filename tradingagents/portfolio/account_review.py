"""Local account decision support. No broker dependency or order transport.

Values describe one archived market view, not a reconciled multi-currency ledger.
Never interpret an empty pending-order list as proof of query completeness.
"""

from __future__ import annotations

from datetime import datetime, timezone
import math
from typing import Any


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) else None


def _timestamp(value: Any) -> datetime | None:
    try:
        result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
    return result if result.tzinfo is not None else None


def review_account(
    snapshot: dict[str, Any], *, now: datetime, max_age_seconds: float = 900
) -> dict[str, Any]:
    """Review a snapshot without treating it as authority to allocate or trade."""
    if now.tzinfo is None or not math.isfinite(max_age_seconds) or max_age_seconds <= 0:
        raise ValueError("Timezone-aware now and positive finite age limit required")
    issues: list[str] = []
    as_of = _timestamp(snapshot.get("as_of"))
    age = (now - as_of).total_seconds() if as_of else None
    if age is None:
        issues.append("SNAPSHOT_TIME_UNKNOWN")
    elif age < 0:
        issues.append("SNAPSHOT_FROM_FUTURE")
    elif age > max_age_seconds:
        issues.append("SNAPSHOT_STALE")
    if snapshot.get("snapshot_health") != "VALID":
        issues.append("SNAPSHOT_HEALTH_NOT_VALID")
    krw_confirmed = snapshot.get("currency") == "KRW"
    if not krw_confirmed:
        issues.append("VALUATION_CURRENCY_UNCONFIRMED")
    nav = _number(snapshot.get("total_equity_krw"))
    nav_source = "total_equity_krw"
    if nav is None:
        nav = _number(snapshot.get("account_value_krw"))
        nav_source = "account_value_krw_fallback"
        issues.append("REPORTED_NAV_MISSING")
    if nav is None or nav <= 0:
        issues.append("NAV_NOT_POSITIVE")
        nav = None
    if not krw_confirmed:
        nav = None
    positions, total, sectors = [], 0.0, {}
    position_rows = snapshot.get("positions")
    values_complete = krw_confirmed
    if not isinstance(position_rows, (list, tuple)):
        issues.append("POSITIONS_MISSING")
        position_rows = []
        values_complete = False
    identities = set()
    for p in position_rows:
        if not isinstance(p, dict):
            issues.append("POSITION_VALUE_INVALID")
            values_complete = False
            continue
        ticker = str(p.get("canonical_ticker") or "UNKNOWN")
        value = _number(p.get("market_value_krw")) if krw_confirmed else None
        qty = _number(p.get("quantity"))
        price = _number(p.get("market_price_krw")) if krw_confirmed else None
        available = _number(p.get("available_qty"))
        if ticker in identities:
            issues.append("DUPLICATE_POSITION")
            values_complete = False
        identities.add(ticker)
        if value is None or value < 0 or qty is None or qty < 0:
            issues.append("POSITION_VALUE_INVALID")
            values_complete = False
        if available is None or qty is None or available < 0 or available > qty:
            issues.append("AVAILABLE_QUANTITY_UNCONFIRMED")
        if qty is not None and qty != int(qty):
            issues.append("FRACTIONAL_POSITION_REQUIRES_SEPARATE_REVIEW")
        if value is not None and value >= 0:
            total += value
            sector = str(p.get("sector") or "UNKNOWN")
            sectors[sector] = sectors.get(sector, 0) + value
        positions.append(
            {
                "ticker": ticker,
                "quantity": qty,
                "available_quantity": available,
                "market_value_krw": value,
                "weight_pct_of_market_view": value / nav * 100
                if nav and value is not None
                else None,
                "one_share_pct_of_market_view": price / nav * 100
                if nav and price and price > 0
                else None,
            }
        )
    if not values_complete:
        total = None
    if sectors.get("UNKNOWN", 0) > 0:
        issues.append("SECTOR_COVERAGE_INCOMPLETE")
    cash = {
        key: _number(snapshot.get(key)) if krw_confirmed else None
        for key in ("settled_cash_krw", "available_cash_krw", "buying_power_krw")
    }
    if any(value is None or value < 0 for value in cash.values()):
        issues.append("CASH_VALUES_INCOMPLETE_OR_NEGATIVE")
    diagnostics = snapshot.get("cash_diagnostics")
    if not isinstance(diagnostics, dict):
        diagnostics = {}
    selected = diagnostics.get("selected_fields")
    if not isinstance(selected, dict):
        selected = {}
    # These labels can describe deposits or withdrawal capacity, not a
    # symbol-specific non-margin buy inquiry. Preserve them without promotion.
    issues.append("NON_MARGIN_SYMBOL_BUYING_POWER_NOT_VERIFIED")
    coverage = diagnostics.get("query_coverage")
    if not isinstance(coverage, dict):
        coverage = {}
    holdings_complete = coverage.get("holdings_complete") is True
    pending_known = coverage.get("pending_orders_known") is True
    if not holdings_complete:
        issues.append("HOLDINGS_QUERY_COMPLETENESS_UNKNOWN")
    if not pending_known:
        issues.append("PENDING_ORDERS_UNKNOWN")
    pending = snapshot.get("pending_orders")
    pending_count = len(pending) if isinstance(pending, (list, tuple)) else None
    if pending_count:
        issues.append("PENDING_ORDERS_REQUIRE_RECONCILIATION")
    if snapshot.get("warnings"):
        issues.append("SOURCE_HAS_WARNINGS")
    constraints = snapshot.get("constraints")
    if not isinstance(constraints, dict):
        constraints = {}
    floor = _number(constraints.get("min_cash_buffer_krw"))
    max_single = _number(constraints.get("max_single_name_weight"))
    breaches = [
        p["ticker"]
        for p in positions
        if p["weight_pct_of_market_view"] is not None
        and max_single is not None
        and p["weight_pct_of_market_view"] > max_single * 100
    ]
    if breaches:
        issues.append("REPORTED_SINGLE_NAME_LIMIT_EXCEEDED")
    stress = []
    if nav and total is not None:
        for shock in (-0.30, -0.20, -0.10, 0.10):
            stress.append(
                {
                    "uniform_equity_move_pct": shock * 100,
                    "pnl_krw": total * shock,
                    "market_view_return_pct": total * shock / nav * 100,
                }
            )
    return {
        "mode": "ACCOUNT_REVIEW_ONLY",
        "source_broker": snapshot.get("broker"),
        "source_environment": "UNVERIFIED_IN_ARCHIVE_SCHEMA",
        "order_authorized": False,
        "as_of": snapshot.get("as_of"),
        "generated_at": now.astimezone(timezone.utc).isoformat(),
        "age_seconds": age,
        "status": "REVIEW_REQUIRED",
        "issues": list(dict.fromkeys(issues)),
        "market_view_nav_krw": nav,
        "nav_source": nav_source,
        "holdings_value_krw": total,
        "equity_exposure_pct": total / nav * 100 if nav and total is not None else None,
        "cash": cash,
        "cash_source_fields": {
            key: selected.get(key)
            for key in (
                "settled_cash",
                "available_cash",
                "buying_power",
                "total_equity",
            )
        },
        "holdings_complete": holdings_complete,
        "pending_orders_known": pending_known,
        "reported_pending_order_count": pending_count,
        "positions": sorted(
            positions, key=lambda p: p["market_value_krw"] or 0, reverse=True
        ),
        "sector_values_krw": sectors,
        "reported_limits": {
            "cash_floor_krw": floor,
            "cash_floor_pct_of_market_view": floor / nav * 100
            if nav and floor is not None
            else None,
            "single_name_limit_pct": max_single * 100
            if max_single is not None
            else None,
            "single_name_breaches": breaches,
        },
        "no_trade_stress_scenarios": stress,
        "notes": [
            "WAIT retains current positions and their market exposure.",
            "Stress is a simultaneous equity price shock, with FX, cash and liabilities held fixed; not a forecast or loss bound.",
            "Market-view NAVs and cash may overlap; do not sum them.",
            "Reported zero cash remains zero; none of these balances authorizes a new buy.",
            "No fee, tax, FX, calendar, quote or execution readiness is certified by this review.",
        ],
    }


def review_market_views(
    snapshots: dict[str, dict[str, Any]], *, now: datetime
) -> dict[str, Any]:
    """Keep market balances separate until a canonical currency ledger exists."""
    reviews = {
        market: review_account(snapshot, now=now)
        for market, snapshot in snapshots.items()
    }
    duplicate_cash = []
    names = list(snapshots)
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            a = _number(snapshots[left].get("available_cash_krw"))
            b = _number(snapshots[right].get("available_cash_krw"))
            if a is not None and a > 0 and a == b:
                duplicate_cash.append([left, right])
    return {
        "mode": "ACCOUNT_REVIEW_ONLY",
        "order_authorized": False,
        "markets": reviews,
        "combined_nav_krw": None,
        "combined_buying_power_krw": None,
        "matching_cash_views": duplicate_cash,
        "consolidation_status": "CURRENCY_LEDGER_RECONCILIATION_REQUIRED",
        "consolidation_note": "Matching cash is an overlap warning, not proof that accounts or all balances are identical. No account identifiers are exported.",
    }


def render_account_review(report: dict[str, Any]) -> str:
    lines = [
        "# 계좌 보유·현금 검토",
        "",
        "기존 계좌의 자료를 읽어 작성한 검토표입니다. 주문을 생성하거나 전송하지 않습니다.",
        "",
        "국내·미국 평가자산 및 매수가능금액은 합산하지 않았습니다. 통화별 원장을 대사해야 통합 자산을 확정할 수 있습니다.",
        "",
    ]

    def fmt(value):
        return "미확인" if value is None else f"{value:,.2f}"

    for market, r in report["markets"].items():
        lines += [
            f"## {market}",
            "",
            f"조회 기준: {r['as_of']} / 검토 생성: {r['generated_at']}",
            "",
            f"시장 조회 화면 기준 자산 {fmt(r['market_view_nav_krw'])}원, 보유 주식 {fmt(r['holdings_value_krw'])}원, 주식 노출 {fmt(r['equity_exposure_pct'])}%.",
            "",
            f"예수금 {fmt(r['cash']['settled_cash_krw'])}원 / 가용현금 표시 {fmt(r['cash']['available_cash_krw'])}원 / 매수가능 표시 {fmt(r['cash']['buying_power_krw'])}원. 같은 돈일 수 있으며 서로 더하지 않습니다.",
            "",
            f"기존 현금 하한은 시장 조회 자산의 {fmt(r['reported_limits']['cash_floor_pct_of_market_view'])}%입니다. 미체결 표시 {r['reported_pending_order_count']}건, 조회 완전성 확인: {r['pending_orders_known']}.",
            "",
            "| 종목 | 보유 수량 | 조회 자산 대비 비중 | 1주 비중 |",
            "|---|---:|---:|---:|",
        ]
        for p in r["positions"]:
            lines.append(
                f"| {p['ticker']} | {fmt(p['quantity'])} | {fmt(p['weight_pct_of_market_view'])}% | {fmt(p['one_share_pct_of_market_view'])}% |"
            )
        lines += [
            "",
            "보유를 유지하고 주식만 동시에 움직이는 단순 민감도입니다. 환율은 고정하며 예상수익·최대손실 한도가 아닙니다.",
            "",
            "| 주식 가격 변화 | 평가손익 | 조회 자산 대비 변화 |",
            "|---|---:|---:|",
        ]
        for s in r["no_trade_stress_scenarios"]:
            lines.append(
                f"| {s['uniform_equity_move_pct']:+.0f}% | {s['pnl_krw']:+,.0f}원 | {s['market_view_return_pct']:+.2f}% |"
            )
        descriptions = {
            "NON_MARGIN_SYMBOL_BUYING_POWER_NOT_VERIFIED": "종목별 미수 없는 매수가능액 미확인",
            "HOLDINGS_QUERY_COMPLETENESS_UNKNOWN": "잔고 전체 페이지 조회 완료 여부 미확인",
            "PENDING_ORDERS_UNKNOWN": "미체결 전체 시장 조회 완료 여부 미확인",
            "PENDING_ORDERS_REQUIRE_RECONCILIATION": "기존 미체결 주문 대사 필요",
            "SECTOR_COVERAGE_INCOMPLETE": "업종 자료 누락: 업종 분산 판단 불가",
            "SNAPSHOT_STALE": "자료가 15분 이상 경과함: 현재 주문 검토에 재사용 불가",
            "SNAPSHOT_FROM_FUTURE": "자료 시각이 검토 시각보다 미래임",
            "SNAPSHOT_TIME_UNKNOWN": "자료 시각 확인 불가",
            "SNAPSHOT_HEALTH_NOT_VALID": "자료 건강도 확인 필요",
            "VALUATION_CURRENCY_UNCONFIRMED": "원화 평가 기준 미확인",
            "NAV_NOT_POSITIVE": "유효한 순자산 확인 불가",
            "REPORTED_NAV_MISSING": "증권사 직접 보고 순자산 누락",
            "POSITIONS_MISSING": "보유종목 자료 누락",
            "POSITION_VALUE_INVALID": "보유종목 수량 또는 평가액 오류",
            "DUPLICATE_POSITION": "보유종목 중복 기록",
            "AVAILABLE_QUANTITY_UNCONFIRMED": "매도가능 수량 미확인",
            "FRACTIONAL_POSITION_REQUIRES_SEPARATE_REVIEW": "소수점 보유분 별도 검토 필요",
            "CASH_VALUES_INCOMPLETE_OR_NEGATIVE": "현금 필드 누락 또는 음수",
            "SOURCE_HAS_WARNINGS": "원본 자료에 경고가 있음",
            "REPORTED_SINGLE_NAME_LIMIT_EXCEEDED": "기존 종목 비중 한도 초과",
        }
        lines += ["", "확인이 필요한 항목:", ""]
        lines += ["- " + descriptions.get(code, code) for code in r["issues"]]
        lines.append("")
    return "\n".join(lines) + "\n"
