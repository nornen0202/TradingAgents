from __future__ import annotations

import json
import math
import re
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

from tradingagents.portfolio.account_models import AccountSnapshot, PortfolioProfile


_KR_BENCHMARK_SYMBOLS = {
    "KOSPI": {"kis_code": "0001", "yfinance": "^KS11", "label": "KOSPI"},
    "KOSDAQ": {"kis_code": "1001", "yfinance": "^KQ11", "label": "KOSDAQ"},
}
_US_BENCHMARK_SYMBOLS = {
    "SPY": {"exchange": "AMS", "yfinance": "SPY", "label": "SPY"},
    "QQQ": {"exchange": "NAS", "yfinance": "QQQ", "label": "QQQ"},
}


class LedgerEventType(str, Enum):
    TRADE = "trade"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    DIVIDEND = "dividend"
    FEE = "fee"
    TAX = "tax"
    INTEREST = "interest"
    FX_CONVERSION = "fx_conversion"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class LedgerEvent:
    date: str
    market: str
    ticker: str
    side: str
    quantity: float
    price: float | None
    gross_amount_krw: float
    fee_krw: float
    tax_krw: float
    currency: str
    fx_rate: float | None
    realized_pnl_krw: float | None
    event_type: str
    source: str

    def to_public_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CashflowEvent:
    date: str
    event_type: str
    amount_krw: float
    capital_flow: bool
    performance_flow: bool
    source: str

    def to_public_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PeriodCoverage:
    period: str
    requested_start_date: date
    actual_start_date: date | None
    end_date: date | None
    requested_days: int | None
    actual_days: int | None
    coverage_ratio: float | None
    is_partial: bool
    same_actual_window_as: str | None
    is_summary_eligible: bool
    insufficient_reason: str | None

    def to_public_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        for key in ("requested_start_date", "actual_start_date", "end_date"):
            value = payload.get(key)
            if isinstance(value, date):
                payload[key] = value.isoformat()
        if isinstance(payload.get("coverage_ratio"), float):
            payload["coverage_ratio"] = round(float(payload["coverage_ratio"]), 6)
        return payload


@dataclass(frozen=True)
class SnapshotSelection:
    rows: list[dict[str, Any]]
    raw_count: int
    excluded_count: int
    excluded_reasons: dict[str, int]
    min_snapshot_value_krw: int | None
    current_excluded_reason: str | None


def build_account_performance_outputs(
    *,
    private_dir: Path,
    run_dir: Path,
    snapshot: AccountSnapshot,
    profile: PortfolioProfile,
    settings: Any,
) -> dict[str, str]:
    if not bool(getattr(settings, "enabled", True)):
        return {}

    private_dir.mkdir(parents=True, exist_ok=True)
    warnings: list[str] = []
    market_scope = _market_scope(profile)
    benchmark_names = _benchmark_names(settings, market_scope)
    current_snapshot = _snapshot_row(snapshot, profile_name=profile.name)
    raw_snapshot_rows = _load_snapshot_history(run_dir=run_dir, profile_name=profile.name)
    raw_snapshot_rows.append(current_snapshot)
    snapshot_selection = _select_performance_snapshots(
        raw_snapshot_rows,
        profile=profile,
        current_snapshot=current_snapshot,
        warnings=warnings,
    )
    snapshot_rows = snapshot_selection.rows

    end_date = _parse_date(current_snapshot["date"]) or date.today()
    start_date = _default_start_date(snapshot_rows, lookback_days=int(getattr(settings, "lookback_days", 800)))
    if not snapshot_rows:
        start_date = end_date
    ledger_events = _load_ledger_events(
        profile=profile,
        market_scope=market_scope,
        settings=settings,
        start_date=start_date,
        end_date=end_date,
        warnings=warnings,
    )

    if len(snapshot_rows) < 2:
        warnings.append("account_performance_snapshot_history_insufficient")

    benchmark_provider_status = _initial_benchmark_provider_status(
        profile=profile,
        settings=settings,
        benchmarks=benchmark_names,
    )
    benchmark_prices = _load_benchmark_prices(
        profile=profile,
        settings=settings,
        market_scope=market_scope,
        benchmarks=benchmark_names,
        start_date=start_date,
        end_date=end_date,
        warnings=warnings,
        provider_status=benchmark_provider_status,
    )
    cashflow_events = _cashflow_events_from_ledger(ledger_events)
    min_coverage_ratio = _settings_ratio(getattr(settings, "min_coverage_ratio", None), default=0.8)
    periods = _compute_periods(
        snapshot_rows=snapshot_rows,
        ledger_events=ledger_events,
        cashflow_events=cashflow_events,
        benchmark_prices=benchmark_prices,
        period_names=tuple(getattr(settings, "periods", ("1M", "3M", "6M", "YTD", "1Y", "ALL"))),
        end_date=end_date,
        min_coverage_ratio=min_coverage_ratio,
        warnings=warnings,
    )
    contribution = _contribution_by_ticker(snapshot=snapshot, ledger_events=ledger_events, warnings=warnings)
    reconciliation = reconcile_account_performance(
        snapshot_rows=snapshot_rows,
        ledger_events=ledger_events,
        contribution_rows=contribution,
        warnings=warnings,
    )
    costs = _cost_summary(ledger_events)
    summary = _summary(periods)
    summary = _summary_with_performance_confidence(summary, reconciliation)
    chart_data = _build_chart_data(
        snapshot_rows=snapshot_rows,
        benchmark_prices=benchmark_prices,
        cashflow_events=cashflow_events,
        summary=summary,
        warnings=warnings,
    )

    payload = {
        "status": "ok" if periods else "partial",
        "generated_at": datetime.now().astimezone().isoformat(),
        "market_scope": market_scope.upper(),
        "benchmarks": benchmark_names,
        "summary": summary,
        "periods": periods,
        "chart_data": chart_data,
        "costs": costs,
        "contribution_by_ticker": contribution,
        "reconciliation": reconciliation,
        "data_quality": {
            "raw_snapshot_count": snapshot_selection.raw_count,
            "snapshot_count": len(snapshot_rows),
            "excluded_snapshot_count": snapshot_selection.excluded_count,
            "excluded_snapshot_reasons": snapshot_selection.excluded_reasons,
            "min_snapshot_value_krw": snapshot_selection.min_snapshot_value_krw,
            "ledger_event_count": len(ledger_events),
            "cashflow_event_count": len(cashflow_events),
            "external_capital_flow_count": len([event for event in cashflow_events if event.capital_flow]),
            "benchmark_provider": _provider_label(settings),
            "benchmark_provider_status": benchmark_provider_status,
            "min_coverage_ratio": min_coverage_ratio,
            "warnings": list(dict.fromkeys(warnings)),
        },
        "public_sanitization": str(getattr(settings, "public_sanitization", "mask_identifiers") or "mask_identifiers"),
    }
    public_payload = _public_payload(payload)
    markdown = render_account_performance_markdown(public_payload)

    report_json = private_dir / "account_performance_report.json"
    public_json = private_dir / "account_performance_public.json"
    chart_json = private_dir / "account_performance_chart_data.json"
    report_md = private_dir / "account_performance_report.md"

    _write_json(report_json, payload)
    _write_json(public_json, public_payload)
    _write_json(chart_json, public_payload.get("chart_data") or {})
    report_md.write_text(markdown, encoding="utf-8")

    return {
        "account_performance_report_json": report_json.as_posix(),
        "account_performance_public_json": public_json.as_posix(),
        "account_performance_chart_data_json": chart_json.as_posix(),
        "account_performance_report_md": report_md.as_posix(),
    }


def render_account_performance_markdown(payload: Mapping[str, Any]) -> str:
    summary = payload.get("summary") if isinstance(payload.get("summary"), Mapping) else {}
    periods = payload.get("periods") if isinstance(payload.get("periods"), list) else []
    costs = payload.get("costs") if isinstance(payload.get("costs"), Mapping) else {}
    contribution = payload.get("contribution_by_ticker") if isinstance(payload.get("contribution_by_ticker"), list) else []
    reconciliation = payload.get("reconciliation") if isinstance(payload.get("reconciliation"), Mapping) else {}
    quality = payload.get("data_quality") if isinstance(payload.get("data_quality"), Mapping) else {}
    display_periods = [
        period
        for period in periods
        if isinstance(period, Mapping)
        and _float_or_none(period.get("actual_return")) is not None
        and period.get("status") not in {"insufficient_history", "duplicate_actual_window"}
        and not period.get("same_actual_window_as")
    ] or [
        period
        for period in periods
        if isinstance(period, Mapping) and _float_or_none(period.get("actual_return")) is not None
    ]
    rows = [
        "| 기간 | 계좌 수익률 | 산출 기준 | 최고 초과 | 초과손익 | 비교 기준 |",
        "|---|---:|---|---:|---:|---|",
    ]
    for period in display_periods:
        if not isinstance(period, Mapping):
            continue
        period_label = "사용 가능 전체 기간" if str(period.get("period") or "").upper() == "ALL" else str(period.get("period") or "-")
        if period.get("partial"):
            period_label = f"{period_label} (부분)"
        rows.append(
            "| "
            f"{period_label} | "
            f"{_pct(period.get('actual_return'))} | "
            f"{_return_method_label(period.get('primary_return_method'), period.get('return_method_warning'))} | "
            f"{_pct((period.get('best_excess') or {}).get('excess_return'))} | "
            f"{_krw((period.get('best_excess') or {}).get('excess_krw'))} | "
            f"{', '.join(str(item.get('benchmark')) for item in period.get('simple_benchmarks', []) if isinstance(item, Mapping)) or '-'} |"
        )

    contribution_rows = []
    for item in contribution[:8]:
        if not isinstance(item, Mapping):
            continue
        contribution_rows.append(
            f"- {item.get('ticker')}: 기여도 {_krw(item.get('total_contribution_krw'))} "
            f"(실현 {_krw(item.get('realized_pnl_krw'))}, 미실현 {_krw(item.get('unrealized_pnl_krw'))})"
        )

    warnings = quality.get("warnings") if isinstance(quality.get("warnings"), list) else []
    warning_lines = [f"- {item}" for item in warnings[:8]] or ["- 특이사항 없음"]
    hidden_periods = [
        str(period.get("period") or "-")
        for period in periods
        if isinstance(period, Mapping)
        and (
            period.get("status") in {"insufficient_history", "duplicate_actual_window"}
            or period.get("same_actual_window_as")
        )
    ]
    hidden_note = (
        f"- 별도 표시하지 않은 요청 기간: `{'/'.join(dict.fromkeys(hidden_periods))}` "
        "(기록 부족 또는 동일 실제 기간)"
        if hidden_periods
        else "- 별도 숨긴 요청 기간 없음"
    )
    contribution_status = str(reconciliation.get("reconciliation_status") or "UNAVAILABLE")
    return "\n".join(
        [
            "## 계좌 성과 vs 지수/ETF",
            "",
            f"- 성과 기준 기간: `{summary.get('start_date') or '-'} ~ {summary.get('end_date') or '-'}` "
            f"(`{summary.get('default_period_label') or summary.get('default_period') or '-'}`)",
            f"- 계좌 수익률: `{_pct(summary.get('actual_return'))}` "
            f"({_return_method_label(summary.get('primary_return_method'), summary.get('return_method_warning'))})",
            f"- 최고 초과 기준: `{((summary.get('best_excess') or {}).get('benchmark')) or '-'}` "
            f"({_pct((summary.get('best_excess') or {}).get('excess_return'))})",
            f"- 최저 초과 기준: `{((summary.get('worst_excess') or {}).get('benchmark')) or '-'}` "
            f"({_pct((summary.get('worst_excess') or {}).get('excess_return'))})",
            f"- 참고용 초과손익: `{_krw((summary.get('best_excess') or {}).get('excess_krw'))}`",
            hidden_note,
            "",
            "### 기간별 비교",
            "",
            *rows,
            "",
            "### 매매 비용",
            "",
            f"- 수수료: `{_krw(costs.get('fees_krw'))}`",
            f"- 세금: `{_krw(costs.get('taxes_krw'))}`",
            f"- 총 비용: `{_krw(costs.get('total_cost_krw'))}`",
            "",
            "### 보유/실현 손익 기여도",
            "",
            f"- 정합성 상태: `{contribution_status}`",
            "",
            *(contribution_rows or ["- 산출 가능한 기여도 데이터가 없습니다."]),
            "",
            "### 데이터 품질",
            "",
            *warning_lines,
            "",
        ]
    )


def _load_snapshot_history(*, run_dir: Path, profile_name: str) -> list[dict[str, Any]]:
    runs_root = _find_runs_root(run_dir)
    if runs_root is None:
        return []
    rows: list[dict[str, Any]] = []
    for snapshot_path in runs_root.rglob("portfolio-private/account_snapshot.json"):
        private_dir = snapshot_path.parent
        status_path = private_dir / "status.json"
        status: dict[str, Any] = {}
        if status_path.exists():
            try:
                status = json.loads(status_path.read_text(encoding="utf-8"))
                if str(status.get("profile") or "") != profile_name:
                    continue
            except Exception:
                continue
        try:
            payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
            if isinstance(payload, dict) and not payload.get("snapshot_health") and status.get("snapshot_health"):
                payload = {**payload, "snapshot_health": status.get("snapshot_health")}
            rows.append(_snapshot_payload_row(payload, profile_name=profile_name))
        except Exception:
            continue
    return rows


def _snapshot_row(snapshot: AccountSnapshot, *, profile_name: str) -> dict[str, Any]:
    return {
        "snapshot_id": snapshot.snapshot_id,
        "profile": profile_name,
        "date": str(snapshot.as_of)[:10],
        "as_of": snapshot.as_of,
        "account_value_krw": float(snapshot.account_value_krw),
        "snapshot_health": str(getattr(snapshot, "snapshot_health", "") or ""),
        "positions_count": len(getattr(snapshot, "positions", ()) or ()),
        "broker": str(getattr(snapshot, "broker", "") or ""),
    }


def _snapshot_payload_row(payload: Mapping[str, Any], *, profile_name: str) -> dict[str, Any]:
    value = _float_or_none(payload.get("account_value_krw"))
    if value is None:
        value = _float_or_none(payload.get("total_equity_krw")) or 0.0
    positions = payload.get("positions")
    positions_count = len(positions) if isinstance(positions, list) else _int_or_none(payload.get("positions_count"))
    as_of = str(payload.get("as_of") or payload.get("generated_at") or payload.get("date") or "")
    return {
        "snapshot_id": str(payload.get("snapshot_id") or ""),
        "profile": profile_name,
        "date": as_of[:10],
        "as_of": as_of,
        "account_value_krw": float(value),
        "snapshot_health": str(payload.get("snapshot_health") or ""),
        "positions_count": positions_count,
        "broker": str(payload.get("broker") or ""),
    }


def _select_performance_snapshots(
    rows: list[dict[str, Any]],
    *,
    profile: PortfolioProfile,
    current_snapshot: dict[str, Any],
    warnings: list[str],
) -> SnapshotSelection:
    valid_rows: list[dict[str, Any]] = []
    reasons: dict[str, int] = {}
    min_value: float | None = None
    current_excluded_reason = _snapshot_exclusion_reason(current_snapshot, profile=profile)
    for row in rows:
        reason = _snapshot_exclusion_reason(row, profile=profile)
        if reason:
            reasons[reason] = reasons.get(reason, 0) + 1
            continue
        value = _float_or_none(row.get("account_value_krw"))
        if value is not None:
            min_value = value if min_value is None else min(min_value, value)
        valid_rows.append(row)

    if current_excluded_reason:
        warnings.append(f"account_performance_current_snapshot_excluded:{current_excluded_reason}")
        valid_rows = []
        min_value = None

    for reason, count in sorted(reasons.items()):
        warnings.append(f"account_performance_snapshot_excluded:{reason}:{count}")

    selected = _dedupe_snapshot_rows(valid_rows)
    return SnapshotSelection(
        rows=selected,
        raw_count=len(rows),
        excluded_count=sum(reasons.values()),
        excluded_reasons=dict(sorted(reasons.items())),
        min_snapshot_value_krw=int(round(min_value)) if min_value is not None else None,
        current_excluded_reason=current_excluded_reason,
    )


def _snapshot_exclusion_reason(row: Mapping[str, Any], *, profile: PortfolioProfile) -> str | None:
    if _parse_date(str(row.get("date") or "")) is None:
        return "invalid_date"
    value = _float_or_none(row.get("account_value_krw"))
    if value is None:
        return "missing_account_value"
    if not math.isfinite(value):
        return "non_finite_account_value"
    if value <= 0:
        return "non_positive_account_value"
    health = str(row.get("snapshot_health") or "").strip().upper()
    if health == "WATCHLIST_ONLY":
        return "watchlist_only"
    if health == "INVALID_SNAPSHOT":
        return "invalid_snapshot"
    positions_count = _int_or_none(row.get("positions_count"))
    min_trade_krw = max(0, int(getattr(getattr(profile, "constraints", None), "min_trade_krw", 0) or 0))
    if min_trade_krw > 0 and value < min_trade_krw and (positions_count is None or positions_count <= 0):
        return "under_min_trade_no_positions"
    return None


def _dedupe_snapshot_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: dict[str, dict[str, Any]] = {}
    for row in rows:
        row_date = str(row.get("date") or "")
        if not row_date:
            continue
        current = deduped.get(row_date)
        if current is None or str(row.get("as_of") or "") >= str(current.get("as_of") or ""):
            deduped[row_date] = row
    return sorted(deduped.values(), key=lambda item: str(item.get("date") or ""))


def _find_runs_root(run_dir: Path) -> Path | None:
    run_dir = Path(run_dir)
    for parent in (run_dir, *run_dir.parents):
        if parent.name == "runs":
            return parent
    return None


def _load_ledger_events(
    *,
    profile: PortfolioProfile,
    market_scope: str,
    settings: Any,
    start_date: date,
    end_date: date,
    warnings: list[str],
) -> list[LedgerEvent]:
    if profile.broker != "kis" or not bool(getattr(settings, "fetch_kis_ledger", True)):
        return []
    if not profile.account_no or not profile.product_code:
        warnings.append("account_performance_kis_ledger_skipped:missing_account")
        return []
    try:
        from tradingagents.portfolio.kis import KisClient

        client = KisClient.from_api_keys(environment=profile.broker_environment)
        query_ranges = _kis_ledger_query_ranges(start_date=start_date, end_date=end_date)
        if len(query_ranges) > 1:
            warnings.append(f"account_performance_kis_ledger_chunked:{len(query_ranges)}")
        if market_scope == "us":
            raw_rows = []
            for query_start, query_end in query_ranges:
                _extend_kis_ledger_rows(
                    raw_rows,
                    warnings=warnings,
                    endpoint="overseas_order_fills",
                    fetch=lambda query_start=query_start, query_end=query_end: client.fetch_overseas_order_fills(
                        account_no=profile.account_no,
                        product_code=profile.product_code,
                        start_date=query_start,
                        end_date=query_end,
                    ),
                )
                _extend_kis_ledger_rows(
                    raw_rows,
                    warnings=warnings,
                    endpoint="overseas_period_transactions",
                    fetch=lambda query_start=query_start, query_end=query_end: client.fetch_overseas_period_transactions(
                        account_no=profile.account_no,
                        product_code=profile.product_code,
                        start_date=query_start,
                        end_date=query_end,
                    ),
                )
                _extend_kis_ledger_rows(
                    raw_rows,
                    warnings=warnings,
                    endpoint="overseas_period_profit",
                    fetch=lambda query_start=query_start, query_end=query_end: client.fetch_overseas_period_profit(
                        account_no=profile.account_no,
                        product_code=profile.product_code,
                        start_date=query_start,
                        end_date=query_end,
                    ),
                )
            return [_normalize_ledger_event(row, market="US", source="kis_overseas") for row in raw_rows]

        raw_rows = []
        for query_start, query_end in query_ranges:
            _extend_kis_ledger_rows(
                raw_rows,
                warnings=warnings,
                endpoint="domestic_order_fills",
                fetch=lambda query_start=query_start, query_end=query_end: client.fetch_domestic_order_fills(
                    account_no=profile.account_no,
                    product_code=profile.product_code,
                    start_date=query_start,
                    end_date=query_end,
                ),
            )
            _extend_kis_ledger_rows(
                raw_rows,
                warnings=warnings,
                endpoint="domestic_period_profit",
                fetch=lambda query_start=query_start, query_end=query_end: client.fetch_domestic_period_profit(
                    account_no=profile.account_no,
                    product_code=profile.product_code,
                    start_date=query_start,
                    end_date=query_end,
                ),
            )
            _extend_kis_ledger_rows(
                raw_rows,
                warnings=warnings,
                endpoint="domestic_period_trade_profit",
                fetch=lambda query_start=query_start, query_end=query_end: client.fetch_domestic_period_trade_profit(
                    account_no=profile.account_no,
                    product_code=profile.product_code,
                    start_date=query_start,
                    end_date=query_end,
                ),
            )
        return [_normalize_ledger_event(row, market="KR", source="kis_domestic") for row in raw_rows]
    except Exception as exc:
        warnings.append(f"account_performance_kis_ledger_failed:{_short_error(exc)}")
        return []


def _extend_kis_ledger_rows(
    rows: list[dict[str, Any]],
    *,
    warnings: list[str],
    endpoint: str,
    fetch: Any,
) -> None:
    try:
        result = fetch()
    except Exception as exc:
        warnings.append(f"account_performance_kis_ledger_endpoint_failed:{endpoint}:{_short_error(exc)}")
        return
    if isinstance(result, tuple):
        result = result[0]
    if isinstance(result, list):
        rows.extend(item for item in result if isinstance(item, dict))


def _kis_ledger_query_ranges(*, start_date: date, end_date: date) -> list[tuple[date, date]]:
    if start_date > end_date:
        return []
    ranges: list[tuple[date, date]] = []
    current = start_date
    max_span = timedelta(days=360)
    while current <= end_date:
        chunk_end = min(end_date, current + max_span)
        ranges.append((current, chunk_end))
        current = chunk_end + timedelta(days=1)
    return ranges


def _normalize_ledger_event(row: Mapping[str, Any], *, market: str, source: str) -> LedgerEvent:
    date_text = _first_text(
        row,
        (
            "ord_dt",
            "trad_dt",
            "bass_dt",
            "sttl_dt",
            "erlm_dt",
            "tr_dt",
            "dt",
            "date",
        ),
    )[:10]
    if len(date_text) == 8 and date_text.isdigit():
        date_text = f"{date_text[:4]}-{date_text[4:6]}-{date_text[6:8]}"
    ticker = _first_text(row, ("pdno", "ovrs_pdno", "std_pdno", "prdt_code", "symbol", "ticker"))
    side = _side_from_row(row)
    qty = _first_float(row, ("tot_ccld_qty", "ccld_qty", "ord_qty", "sll_qty", "buy_qty", "qty")) or 0.0
    price = _first_float(row, ("avg_prvs", "avg_unpr", "ccld_unpr", "ord_unpr", "tr_pric", "price"))
    fx_rate = _first_float(row, ("bass_exrt", "frst_bltn_exrt", "aply_exrt", "exrt"))
    gross = _first_float(
        row,
        (
            "tot_ccld_amt",
            "ccld_amt",
            "ord_amt",
            "sll_amt",
            "buy_amt",
            "frcr_ccld_amt",
            "ovrs_stck_sll_amt",
            "ovrs_stck_buy_amt",
            "dpst_amt",
            "wthdr_amt",
            "tr_amt",
            "trns_amt",
            "cashflow_amount",
            "dividend_krw",
            "interest_krw",
            "gross_amount",
        ),
    )
    if gross is None and price is not None and qty:
        gross = price * qty
    gross_krw = _to_krw(gross or 0.0, fx_rate=fx_rate)
    fee = _to_krw(
        _first_float(row, ("fee", "fee_amt", "smtl_fee", "exec_fee", "ovrs_fee", "cmsn_amt")) or 0.0,
        fx_rate=fx_rate,
    )
    tax = _to_krw(
        _first_float(row, ("tax", "tax_amt", "tr_tax", "sll_tax", "sttx", "transaction_tax")) or 0.0,
        fx_rate=fx_rate,
    )
    realized = _first_float(
        row,
        (
            "rlzt_pfls",
            "rlzt_pfls_amt",
            "trad_pfls_amt",
            "evlu_pfls_smtl_amt",
            "ovrs_rlzt_pfls_amt",
            "realized_pnl",
        ),
    )
    if realized is not None:
        realized = _to_krw(realized, fx_rate=fx_rate)
    currency = _first_text(row, ("crcy_cd", "tr_crcy_cd", "currency")) or ("USD" if market == "US" else "KRW")
    event_type = _classify_ledger_event_type(row, side=side)
    return LedgerEvent(
        date=date_text,
        market=market,
        ticker=ticker.upper(),
        side=side,
        quantity=float(qty),
        price=price,
        gross_amount_krw=float(gross_krw),
        fee_krw=float(fee),
        tax_krw=float(tax),
        currency=currency,
        fx_rate=fx_rate,
        realized_pnl_krw=realized,
        event_type=event_type.value,
        source=source,
    )


def _load_benchmark_prices(
    *,
    profile: PortfolioProfile,
    settings: Any,
    market_scope: str,
    benchmarks: tuple[str, ...],
    start_date: date,
    end_date: date,
    warnings: list[str],
    provider_status: dict[str, dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    prices: dict[str, list[dict[str, Any]]] = {}
    prices.update(_load_local_benchmark_prices(getattr(settings, "price_history_path", None), benchmarks=benchmarks, warnings=warnings))
    for benchmark in prices:
        _mark_benchmark_provider_status(
            provider_status,
            benchmark,
            used_provider="local_json",
            status="ok",
        )
    missing = [name for name in benchmarks if name not in prices]

    if profile.broker == "kis" and missing:
        prices.update(
            _fetch_kis_benchmark_prices(
                profile=profile,
                market_scope=market_scope,
                benchmarks=tuple(missing),
                start_date=start_date,
                end_date=end_date,
                warnings=warnings,
                provider_status=provider_status,
            )
        )
        missing = [name for name in benchmarks if name not in prices]

    provider = str(getattr(settings, "price_provider", "yfinance") or "yfinance").strip().lower()
    if provider == "local_json":
        for benchmark in missing:
            _mark_benchmark_provider_status(provider_status, benchmark, status="missing")
        return prices
    if provider in {"", "none", "disabled"}:
        if missing:
            warnings.append(f"account_performance_benchmark_missing:{','.join(missing)}")
        for benchmark in missing:
            _mark_benchmark_provider_status(provider_status, benchmark, status="missing")
        return prices
    if provider != "yfinance":
        warnings.append(f"account_performance_price_provider_unsupported:{provider}")
        for benchmark in missing:
            _mark_benchmark_provider_status(
                provider_status,
                benchmark,
                status="missing",
                warning=f"unsupported_provider:{provider}",
            )
        return prices

    if missing:
        prices.update(
            _fetch_yfinance_benchmark_prices(
                market_scope=market_scope,
                benchmarks=tuple(missing),
                start_date=start_date,
                end_date=end_date,
                warnings=warnings,
                provider_status=provider_status,
            )
        )
    for benchmark in benchmarks:
        if benchmark not in prices:
            _mark_benchmark_provider_status(provider_status, benchmark, status="missing")
    return prices


def _initial_benchmark_provider_status(
    *,
    profile: PortfolioProfile,
    settings: Any,
    benchmarks: tuple[str, ...],
) -> dict[str, dict[str, Any]]:
    configured = str(getattr(settings, "price_provider", "yfinance") or "yfinance").strip().lower()
    if getattr(settings, "price_history_path", None):
        preferred = "local_json"
    elif profile.broker == "kis":
        preferred = "kis"
    else:
        preferred = configured
    return {
        benchmark: {
            "preferred_provider": preferred,
            "used_provider": None,
            "status": "pending",
            "warnings": [],
        }
        for benchmark in benchmarks
    }


def _mark_benchmark_provider_status(
    provider_status: dict[str, dict[str, Any]],
    benchmark: str,
    *,
    used_provider: str | None = None,
    status: str | None = None,
    warning: str | None = None,
) -> None:
    item = provider_status.setdefault(
        benchmark,
        {"preferred_provider": None, "used_provider": None, "status": "pending", "warnings": []},
    )
    if used_provider:
        item["used_provider"] = used_provider
    if status:
        if status == "ok" and item.get("warnings") and item.get("preferred_provider") != used_provider:
            item["status"] = "fallback"
        else:
            item["status"] = status
    if warning:
        warnings = list(item.get("warnings")) if isinstance(item.get("warnings"), list) else []
        warnings.append(_short_error(warning))
        item["warnings"] = list(dict.fromkeys(warnings))


def _load_local_benchmark_prices(
    path: Any,
    *,
    benchmarks: tuple[str, ...],
    warnings: list[str],
) -> dict[str, list[dict[str, Any]]]:
    if not path:
        return {}
    candidate = Path(path)
    if not candidate.exists():
        warnings.append(f"account_performance_price_history_missing:{candidate}")
        return {}
    try:
        payload = json.loads(candidate.read_text(encoding="utf-8"))
    except Exception as exc:
        warnings.append(f"account_performance_price_history_invalid:{_short_error(exc)}")
        return {}
    if not isinstance(payload, Mapping):
        warnings.append("account_performance_price_history_not_object")
        return {}
    prices: dict[str, list[dict[str, Any]]] = {}
    aliases = _benchmark_aliases()
    for benchmark in benchmarks:
        for key in (benchmark, benchmark.upper(), aliases.get(benchmark, "")):
            if key and key in payload:
                rows = _normalize_price_rows(payload[key])
                if rows:
                    prices[benchmark] = rows
                    break
    return prices


def _fetch_kis_benchmark_prices(
    *,
    profile: PortfolioProfile,
    market_scope: str,
    benchmarks: tuple[str, ...],
    start_date: date,
    end_date: date,
    warnings: list[str],
    provider_status: dict[str, dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    try:
        from tradingagents.portfolio.kis import KisClient

        client = KisClient.from_api_keys(environment=profile.broker_environment)
    except Exception as exc:
        warnings.append(f"account_performance_kis_benchmark_unavailable:{_short_error(exc)}")
        for benchmark in benchmarks:
            _mark_benchmark_provider_status(
                provider_status,
                benchmark,
                status="unavailable",
                warning=f"kis_unavailable:{_short_error(exc)}",
            )
        return {}

    result: dict[str, list[dict[str, Any]]] = {}
    for benchmark in benchmarks:
        try:
            if market_scope == "kr":
                code = _KR_BENCHMARK_SYMBOLS.get(benchmark, {}).get("kis_code")
                if not code:
                    continue
                rows = client.fetch_domestic_index_price_history(
                    index_code=str(code),
                    start_date=start_date,
                    end_date=end_date,
                )
            else:
                meta = _US_BENCHMARK_SYMBOLS.get(benchmark, {})
                rows = client.fetch_overseas_daily_price_history(
                    symbol=benchmark,
                    exchange_code=str(meta.get("exchange") or "NAS"),
                    start_date=start_date,
                    end_date=end_date,
                )
            normalized = _normalize_price_rows(rows)
            if normalized:
                result[benchmark] = normalized
                _mark_benchmark_provider_status(
                    provider_status,
                    benchmark,
                    used_provider="kis",
                    status="ok",
                )
        except Exception as exc:
            warnings.append(f"account_performance_kis_benchmark_failed:{benchmark}:{_short_error(exc)}")
            _mark_benchmark_provider_status(
                provider_status,
                benchmark,
                status="failed",
                warning=f"kis_failed:{_short_error(exc)}",
            )
    return result


def _fetch_yfinance_benchmark_prices(
    *,
    market_scope: str,
    benchmarks: tuple[str, ...],
    start_date: date,
    end_date: date,
    warnings: list[str],
    provider_status: dict[str, dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    try:
        import yfinance as yf
    except Exception as exc:
        warnings.append(f"account_performance_yfinance_unavailable:{_short_error(exc)}")
        for benchmark in benchmarks:
            _mark_benchmark_provider_status(
                provider_status,
                benchmark,
                status="unavailable",
                warning=f"yfinance_unavailable:{_short_error(exc)}",
            )
        return {}
    result: dict[str, list[dict[str, Any]]] = {}
    for benchmark in benchmarks:
        symbol = _benchmark_yfinance_symbol(market_scope, benchmark)
        if not symbol:
            continue
        try:
            data = yf.download(
                symbol,
                start=start_date.isoformat(),
                end=(end_date + timedelta(days=1)).isoformat(),
                progress=False,
                auto_adjust=True,
                threads=False,
            )
        except Exception as exc:
            warnings.append(f"account_performance_yfinance_failed:{benchmark}:{_short_error(exc)}")
            _mark_benchmark_provider_status(
                provider_status,
                benchmark,
                status="failed",
                warning=f"yfinance_failed:{_short_error(exc)}",
            )
            continue
        if data is None or getattr(data, "empty", True):
            warnings.append(f"account_performance_yfinance_empty:{benchmark}")
            _mark_benchmark_provider_status(
                provider_status,
                benchmark,
                status="empty",
                warning="yfinance_empty",
            )
            continue
        close = data.get("Close")
        if close is None:
            warnings.append(f"account_performance_yfinance_no_close:{benchmark}")
            _mark_benchmark_provider_status(
                provider_status,
                benchmark,
                status="failed",
                warning="yfinance_no_close",
            )
            continue
        if hasattr(close, "columns"):
            close = close.iloc[:, 0]
        rows = []
        for index, value in close.dropna().items():
            numeric = _float_or_none(value)
            if numeric is None:
                continue
            rows.append({"date": str(getattr(index, "date", lambda: index)())[:10], "close": numeric})
        if rows:
            result[benchmark] = rows
            previous = provider_status.get(benchmark) or {}
            status = "fallback" if previous.get("warnings") else "ok"
            _mark_benchmark_provider_status(
                provider_status,
                benchmark,
                used_provider="yfinance",
                status=status,
            )
    return result


def _compute_periods(
    *,
    snapshot_rows: list[dict[str, Any]],
    ledger_events: list[LedgerEvent],
    cashflow_events: list[CashflowEvent],
    benchmark_prices: dict[str, list[dict[str, Any]]],
    period_names: tuple[str, ...],
    end_date: date,
    min_coverage_ratio: float,
    warnings: list[str],
) -> list[dict[str, Any]]:
    periods: list[dict[str, Any]] = []
    if len(snapshot_rows) < 2:
        return periods
    first_available_start = _parse_date(str(snapshot_rows[0].get("date") or ""))
    end_snapshot = _last_snapshot_on_or_before(snapshot_rows, end_date)
    actual_end_date = _parse_date(str(end_snapshot.get("date"))) if end_snapshot else None
    if end_snapshot is None or actual_end_date is None:
        return periods
    for period_name in period_names:
        start_boundary = _period_start(period_name, end_date=end_date, snapshot_rows=snapshot_rows)
        start_snapshot = _first_snapshot_on_or_after(snapshot_rows, start_boundary)
        if not start_snapshot or start_snapshot["date"] >= end_snapshot["date"]:
            warnings.append(f"account_performance_period_partial:{period_name}")
            continue
        start_value = float(start_snapshot["account_value_krw"])
        end_value = float(end_snapshot["account_value_krw"])
        if start_value <= 0:
            warnings.append(f"account_performance_period_invalid_start_value:{period_name}")
            continue
        start = _parse_date(str(start_snapshot["date"])) or start_boundary
        end = actual_end_date
        coverage = _build_period_coverage(
            period_name=period_name,
            requested_start=start_boundary,
            actual_start=start,
            end=end,
            requested_end=end_date,
            min_coverage_ratio=min_coverage_ratio,
        )
        partial_reasons = []
        if start > start_boundary:
            partial_reasons.append(f"requested_start={start_boundary.isoformat()}:actual_start={start.isoformat()}")
        if end < end_date:
            partial_reasons.append(f"requested_end={end_date.isoformat()}:actual_end={end.isoformat()}")
        if partial_reasons:
            warnings.append(f"account_performance_period_partial:{period_name}:{';'.join(partial_reasons)}")
        insufficient_reason = _period_insufficient_reason(
            period_name=period_name,
            requested_start=start_boundary,
            actual_start=start,
            coverage=coverage,
            min_coverage_ratio=min_coverage_ratio,
            first_available_start=first_available_start,
        )
        if insufficient_reason:
            reason = (
                f"requested_start={start_boundary.isoformat()}:"
                f"available_start={start.isoformat()}:"
                f"coverage_ratio={_coverage_ratio_text(coverage.coverage_ratio)}:"
                f"reason={insufficient_reason}"
            )
            warnings.append(f"account_performance_period_insufficient_history:{period_name}:{reason}")
            periods.append(
                _insufficient_history_period(
                    period_name=period_name,
                    requested_start=start_boundary,
                    available_start=start,
                    end_date=end,
                    reason=reason,
                    coverage=coverage,
                )
            )
            continue
        return_profile = _period_return_profile(
            period_name=period_name,
            snapshot_rows=snapshot_rows,
            ledger_events=ledger_events,
            cashflow_events=cashflow_events,
            start_date=start,
            end_date=end,
            start_value=start_value,
            end_value=end_value,
        )
        primary_return = _float_or_none(return_profile.get("primary_return"))
        if primary_return is None:
            warnings.append(f"account_performance_period_return_unavailable:{period_name}")
            continue
        if return_profile.get("return_method_warning"):
            warnings.append(f"account_performance_{return_profile['return_method_warning']}:{period_name}")
        simple_rows: list[dict[str, Any]] = []
        cashflow_rows: list[dict[str, Any]] = []
        benchmark_cashflow_available = not _has_unknown_material_ledger_events(
            ledger_events,
            start_date=start,
            end_date=end,
        )
        if not benchmark_cashflow_available:
            warnings.append(f"account_performance_benchmark_cashflow_unavailable:{period_name}:unknown_ledger_events")
        for benchmark, series in benchmark_prices.items():
            simple = _benchmark_simple_return(series, start_date=start, end_date=end)
            if simple is None:
                warnings.append(f"account_performance_benchmark_period_missing:{period_name}:{benchmark}")
                continue
            excess = primary_return - simple
            simple_rows.append(
                {
                    "benchmark": benchmark,
                    "benchmark_return": round(simple, 6),
                    "excess_return": round(excess, 6),
                    "excess_krw": int(round(excess * start_value)),
                    "comparison_basis": "simple_period_return",
                }
            )
            if benchmark_cashflow_available:
                simulated = benchmark_same_cashflow_return(
                    series,
                    external_cashflows=cashflow_events,
                    start_date=start,
                    end_date=end,
                    start_value=start_value,
                )
                if simulated is not None:
                    cf_excess = primary_return - simulated
                    capital_flow_count = len(
                        [
                            event
                            for event in cashflow_events
                            if event.capital_flow
                            and (event_date := _parse_date(event.date)) is not None
                            and start <= event_date <= end
                        ]
                    )
                    basis = "external_cashflows" if capital_flow_count else "no_external_cashflows"
                    reliability = "reference" if return_profile.get("return_method_warning") else "reliable"
                    cashflow_rows.append(
                        {
                            "benchmark": benchmark,
                            "benchmark_return": round(simulated, 6),
                            "excess_return": round(cf_excess, 6),
                            "excess_krw": int(round(cf_excess * start_value)),
                            "cashflow_event_count": capital_flow_count,
                            "comparison_basis": basis,
                            "reliability": reliability,
                        }
                    )
        all_rows = simple_rows or cashflow_rows
        best = max(all_rows, key=lambda item: float(item["excess_return"])) if all_rows else None
        worst = min(all_rows, key=lambda item: float(item["excess_return"])) if all_rows else None
        period_values = _snapshot_values_between(snapshot_rows, start, end)
        summary_eligible = coverage.is_summary_eligible and (not partial_reasons or min_coverage_ratio <= 0.0)
        coverage_payload = _replace_period_coverage(
            coverage,
            is_partial=bool(partial_reasons),
            is_summary_eligible=summary_eligible,
            insufficient_reason=None,
        ).to_public_dict()
        periods.append(
            {
                "period": period_name,
                "requested_start_date": start_boundary.isoformat(),
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "partial": bool(partial_reasons),
                "partial_reasons": partial_reasons,
                "actual_start_value_krw": int(round(start_value)),
                "actual_end_value_krw": int(round(end_value)),
                "simple_nav_return": _round_or_none(return_profile.get("simple_nav_return")),
                "twr_return": _round_or_none(return_profile.get("twr_return")),
                "twr_unavailable_reason": return_profile.get("twr_unavailable_reason"),
                "mwr_return": _round_or_none(return_profile.get("mwr_return")),
                "mwr_unavailable_reason": return_profile.get("mwr_unavailable_reason") or "mwr_not_implemented",
                "primary_return": _round_or_none(return_profile.get("primary_return")),
                "primary_return_method": return_profile.get("primary_return_method"),
                "return_method_warning": return_profile.get("return_method_warning"),
                "actual_return": _round_or_none(return_profile.get("primary_return")),
                "mdd": _max_drawdown(period_values),
                "volatility": _volatility(period_values),
                "period_coverage": coverage_payload,
                "simple_benchmarks": simple_rows,
                "cashflow_benchmarks": cashflow_rows,
                "best_excess": best or {},
                "worst_excess": worst or {},
            }
        )
    _mark_duplicate_actual_windows(periods, warnings=warnings)
    return periods


def _build_period_coverage(
    *,
    period_name: str,
    requested_start: date,
    actual_start: date | None,
    end: date | None,
    requested_end: date,
    min_coverage_ratio: float,
) -> PeriodCoverage:
    requested_days = max(0, (requested_end - requested_start).days) if requested_end >= requested_start else None
    actual_days = (
        max(0, (end - actual_start).days)
        if actual_start is not None and end is not None and end >= actual_start
        else None
    )
    if str(period_name or "").strip().upper() == "ALL":
        requested_days = actual_days
    coverage_ratio = (
        float(actual_days) / float(requested_days)
        if actual_days is not None and requested_days not in (None, 0)
        else None
    )
    is_partial = bool(
        actual_start is None
        or end is None
        or actual_start > requested_start
        or end < requested_end
        or (coverage_ratio is not None and coverage_ratio < 1.0)
    )
    insufficient_reason = None
    is_summary_eligible = True
    if coverage_ratio is not None and coverage_ratio < min_coverage_ratio:
        insufficient_reason = "coverage below minimum threshold"
        is_summary_eligible = False
    if str(period_name or "").strip().upper() == "ALL":
        is_partial = False
        insufficient_reason = None
        is_summary_eligible = actual_days is not None and actual_days > 0
    return PeriodCoverage(
        period=str(period_name),
        requested_start_date=requested_start,
        actual_start_date=actual_start,
        end_date=end,
        requested_days=requested_days,
        actual_days=actual_days,
        coverage_ratio=coverage_ratio,
        is_partial=is_partial,
        same_actual_window_as=None,
        is_summary_eligible=is_summary_eligible,
        insufficient_reason=insufficient_reason,
    )


def _replace_period_coverage(
    coverage: PeriodCoverage,
    *,
    is_partial: bool | None = None,
    same_actual_window_as: str | None = None,
    is_summary_eligible: bool | None = None,
    insufficient_reason: str | None = None,
) -> PeriodCoverage:
    return PeriodCoverage(
        period=coverage.period,
        requested_start_date=coverage.requested_start_date,
        actual_start_date=coverage.actual_start_date,
        end_date=coverage.end_date,
        requested_days=coverage.requested_days,
        actual_days=coverage.actual_days,
        coverage_ratio=coverage.coverage_ratio,
        is_partial=coverage.is_partial if is_partial is None else is_partial,
        same_actual_window_as=same_actual_window_as,
        is_summary_eligible=coverage.is_summary_eligible if is_summary_eligible is None else is_summary_eligible,
        insufficient_reason=insufficient_reason,
    )


def _period_insufficient_reason(
    *,
    period_name: str,
    requested_start: date,
    actual_start: date,
    coverage: PeriodCoverage,
    min_coverage_ratio: float,
    first_available_start: date | None,
) -> str | None:
    if str(period_name or "").strip().upper() == "ALL":
        return None
    if min_coverage_ratio <= 0.0:
        return None
    if first_available_start is not None and requested_start < first_available_start:
        return "account history starts after requested period start"
    if actual_start > requested_start and coverage.coverage_ratio is not None and coverage.coverage_ratio < min_coverage_ratio:
        return "nearest usable snapshot is after requested period start"
    if coverage.coverage_ratio is not None and coverage.coverage_ratio < min_coverage_ratio:
        return "coverage below minimum threshold"
    return None


def _coverage_ratio_text(value: float | None) -> str:
    return "-" if value is None else f"{value:.6f}"


def _round_or_none(value: Any, digits: int = 6) -> float | None:
    number = _float_or_none(value)
    return round(number, digits) if number is not None else None


def _mark_duplicate_actual_windows(periods: list[dict[str, Any]], *, warnings: list[str]) -> None:
    by_window: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for period in periods:
        start = str(period.get("start_date") or "")
        end = str(period.get("end_date") or "")
        if start and end:
            by_window.setdefault((start, end), []).append(period)

    for grouped in by_window.values():
        if len(grouped) < 2:
            continue
        canonical = _duplicate_window_canonical_period(grouped)
        canonical_label = _period_summary_label(canonical)
        duplicates: list[str] = []
        for period in grouped:
            if period is canonical:
                coverage = _period_coverage_from_payload(period.get("period_coverage"))
                if coverage:
                    period["period_coverage"] = _replace_period_coverage(
                        coverage,
                        same_actual_window_as=None,
                        is_summary_eligible=bool(period.get("actual_return") is not None),
                    ).to_public_dict()
                continue
            duplicates.append(str(period.get("period") or "-"))
            coverage = _period_coverage_from_payload(period.get("period_coverage"))
            if coverage:
                period["period_coverage"] = _replace_period_coverage(
                    coverage,
                    same_actual_window_as=canonical_label,
                    is_summary_eligible=False,
                    insufficient_reason=f"same actual window as {canonical_label}",
                    is_partial=True,
                ).to_public_dict()
            period["same_actual_window_as"] = canonical_label
            had_return = _float_or_none(period.get("actual_return")) is not None
            if had_return:
                period["raw_duplicate_result"] = {
                    "actual_return": period.get("actual_return"),
                    "simple_nav_return": period.get("simple_nav_return"),
                    "twr_return": period.get("twr_return"),
                    "primary_return": period.get("primary_return"),
                    "primary_return_method": period.get("primary_return_method"),
                    "mdd": period.get("mdd"),
                    "volatility": period.get("volatility"),
                    "simple_benchmarks": period.get("simple_benchmarks") or [],
                    "cashflow_benchmarks": period.get("cashflow_benchmarks") or [],
                    "best_excess": period.get("best_excess") or {},
                    "worst_excess": period.get("worst_excess") or {},
                }
            period.update(
                {
                    "status": "duplicate_actual_window" if had_return else period.get("status", "duplicate_actual_window"),
                    "partial": True,
                    "actual_return": None,
                    "primary_return": None,
                    "mdd": None,
                    "volatility": None,
                    "simple_benchmarks": [],
                    "cashflow_benchmarks": [],
                    "best_excess": {},
                    "worst_excess": {},
                }
            )
            reason = f"same_actual_window_as={canonical_label}"
            partial_reasons = list(period.get("partial_reasons")) if isinstance(period.get("partial_reasons"), list) else []
            if reason not in {str(item) for item in partial_reasons}:
                partial_reasons.append(reason)
            period["partial_reasons"] = partial_reasons
        if duplicates:
            warnings.append(
                "account_performance_duplicate_actual_windows:"
                f"{canonical_label}:{','.join(sorted(dict.fromkeys(duplicates)))}"
            )


def _duplicate_window_canonical_period(periods: list[dict[str, Any]]) -> dict[str, Any]:
    for period in periods:
        if str(period.get("period") or "").strip().upper() == "ALL":
            return period
    eligible = [
        period
        for period in periods
        if _float_or_none(period.get("actual_return")) is not None
        and ((period.get("period_coverage") or {}).get("is_summary_eligible") if isinstance(period.get("period_coverage"), dict) else True)
    ]
    candidates = eligible or periods
    return max(candidates, key=lambda item: int(((item.get("period_coverage") or {}).get("actual_days") or 0) if isinstance(item.get("period_coverage"), dict) else 0))


def _period_summary_label(period: Mapping[str, Any]) -> str:
    return "ALL_AVAILABLE" if str(period.get("period") or "").strip().upper() == "ALL" else str(period.get("period") or "-")


def _period_coverage_from_payload(value: Any) -> PeriodCoverage | None:
    if not isinstance(value, Mapping):
        return None
    requested = _parse_date(str(value.get("requested_start_date") or ""))
    if requested is None:
        return None
    return PeriodCoverage(
        period=str(value.get("period") or ""),
        requested_start_date=requested,
        actual_start_date=_parse_date(str(value.get("actual_start_date") or "")),
        end_date=_parse_date(str(value.get("end_date") or "")),
        requested_days=_int_or_none(value.get("requested_days")),
        actual_days=_int_or_none(value.get("actual_days")),
        coverage_ratio=_float_or_none(value.get("coverage_ratio")),
        is_partial=bool(value.get("is_partial")),
        same_actual_window_as=str(value.get("same_actual_window_as") or "") or None,
        is_summary_eligible=bool(value.get("is_summary_eligible")),
        insufficient_reason=str(value.get("insufficient_reason") or "") or None,
    )


def _insufficient_history_period(
    *,
    period_name: str,
    requested_start: date,
    available_start: date,
    end_date: date,
    reason: str,
    coverage: PeriodCoverage | None = None,
) -> dict[str, Any]:
    coverage_payload = (
        _replace_period_coverage(
            coverage,
            is_partial=True,
            is_summary_eligible=False,
            insufficient_reason=coverage.insufficient_reason or "account history starts after requested period start",
        ).to_public_dict()
        if coverage
        else PeriodCoverage(
            period=period_name,
            requested_start_date=requested_start,
            actual_start_date=available_start,
            end_date=end_date,
            requested_days=max(0, (end_date - requested_start).days),
            actual_days=max(0, (end_date - available_start).days),
            coverage_ratio=None,
            is_partial=True,
            same_actual_window_as=None,
            is_summary_eligible=False,
            insufficient_reason="account history starts after requested period start",
        ).to_public_dict()
    )
    return {
        "period": period_name,
        "requested_start_date": requested_start.isoformat(),
        "start_date": available_start.isoformat(),
        "end_date": end_date.isoformat(),
        "partial": True,
        "partial_reasons": [reason],
        "status": "insufficient_history",
        "actual_start_value_krw": None,
        "actual_end_value_krw": None,
        "simple_nav_return": None,
        "twr_return": None,
        "twr_unavailable_reason": "insufficient_history",
        "mwr_return": None,
        "mwr_unavailable_reason": "insufficient_history",
        "primary_return": None,
        "primary_return_method": "insufficient_history",
        "return_method_warning": "insufficient_history",
        "actual_return": None,
        "mdd": None,
        "volatility": None,
        "period_coverage": coverage_payload,
        "simple_benchmarks": [],
        "cashflow_benchmarks": [],
        "best_excess": {},
        "worst_excess": {},
    }


def _build_chart_data(
    *,
    snapshot_rows: list[dict[str, Any]],
    benchmark_prices: dict[str, list[dict[str, Any]]],
    cashflow_events: list[CashflowEvent],
    summary: Mapping[str, Any],
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    if not snapshot_rows:
        return {"series": []}
    summary_start = _parse_date(str(summary.get("start_date") or "")) or _parse_date(str(snapshot_rows[0].get("date") or ""))
    summary_end = _parse_date(str(summary.get("end_date") or "")) or _parse_date(str(snapshot_rows[-1].get("date") or ""))
    rows = [
        row
        for row in snapshot_rows
        if (row_date := _parse_date(str(row.get("date") or ""))) is not None
        and (summary_start is None or row_date >= summary_start)
        and (summary_end is None or row_date <= summary_end)
    ]
    if len(rows) < 2:
        return {
            "series": [],
            "benchmarks": list(benchmark_prices),
            "return_method": str(summary.get("primary_return_method") or "simple_nav"),
            "coverage": summary.get("period_coverage") or {},
            "title": _chart_title(summary),
        }
    start_value = float(rows[0].get("account_value_krw") or 0.0)
    return_method = str(summary.get("primary_return_method") or "simple_nav")
    use_twr = return_method == "twr"
    start_date = _parse_date(str(rows[0].get("date"))) or date.today()
    benchmark_start = {
        name: _price_on_or_after(price_rows, start_date)
        for name, price_rows in benchmark_prices.items()
    }
    series = []
    cumulative_twr = 0.0
    previous_row: dict[str, Any] | None = None
    for row in rows:
        row_date = _parse_date(str(row.get("date"))) or date.today()
        item: dict[str, Any] = {"date": row_date.isoformat()}
        value = float(row.get("account_value_krw") or 0.0)
        if use_twr and previous_row is not None:
            previous_date = _parse_date(str(previous_row.get("date") or ""))
            previous_value = _float_or_none(previous_row.get("account_value_krw"))
            if previous_date is not None and previous_value and previous_value > 0:
                flow_sum = sum(
                    event.amount_krw
                    for event in cashflow_events
                    if event.capital_flow
                    and (event_date := _parse_date(event.date)) is not None
                    and previous_date < event_date <= row_date
                )
                interval_return = (value - flow_sum - previous_value) / previous_value
                cumulative_twr = (1.0 + cumulative_twr) * (1.0 + interval_return) - 1.0
            item["account_return"] = round(cumulative_twr, 6)
        else:
            item["account_return"] = round((value - start_value) / start_value, 6) if start_value > 0 else None
        for name, rows in benchmark_prices.items():
            start_price = benchmark_start.get(name)
            current_price = _price_on_or_before(rows, row_date)
            item[name] = (
                round((current_price - start_price) / start_price, 6)
                if start_price and current_price and start_price > 0
                else None
            )
        series.append(item)
        previous_row = row
    account_returns = [
        float(row["account_return"])
        for row in series
        if isinstance(row, dict) and row.get("account_return") is not None
    ]
    final_return = account_returns[-1] if account_returns else None
    summary_return = _float_or_none(summary.get("actual_return"))
    consistency_status = "unchecked"
    consistency_warning = None
    if final_return is not None and summary_return is not None:
        if abs(final_return - summary_return) <= 0.0001:
            consistency_status = "ok"
        else:
            consistency_status = "warning"
            consistency_warning = "chart_final_return_differs_from_summary"
            if warnings is not None:
                warnings.append("account_performance_chart_summary_mismatch")
    return {
        "series": series,
        "benchmarks": list(benchmark_prices),
        "return_method": return_method,
        "coverage": summary.get("period_coverage") or {},
        "summary_return": _round_or_none(summary_return),
        "final_return": _round_or_none(final_return),
        "peak_return": _round_or_none(max(account_returns) if account_returns else None),
        "trough_return": _round_or_none(min(account_returns) if account_returns else None),
        "max_drawdown": _round_or_none(_max_drawdown([1.0 + value for value in account_returns])) if account_returns else None,
        "consistency_status": consistency_status,
        "consistency_warning": consistency_warning,
        "title": _chart_title(summary),
    }


def _chart_title(summary: Mapping[str, Any]) -> str:
    method_label = _return_method_label(summary.get("primary_return_method"), summary.get("return_method_warning"))
    is_available_history = str(summary.get("default_period") or "") == "ALL_AVAILABLE"
    period_label = "사용 가능 기간" if is_available_history else str(summary.get("default_period_label") or summary.get("default_period") or "기간")
    return f"{period_label} 수익률 ({method_label})"


def _return_method_label(method: Any, warning: Any = None) -> str:
    method_text = str(method or "").strip().lower()
    warning_text = str(warning or "").strip().lower()
    if method_text == "twr":
        return "현금흐름 보정 TWR"
    if method_text in {"twr_equivalent", "available_history_twr_equivalent"}:
        return "외부 현금흐름 없음 - TWR 상당 단순 NAV"
    if method_text == "mwr":
        return "현금흐름 보정 MWR"
    if warning_text == "cashflow_adjustment_unavailable" or method_text == "simple_nav_unadjusted":
        return "현금흐름 미보정 단순 NAV 기준"
    if method_text == "available_history_simple_nav":
        return "사용 가능 기간 단순 NAV 기준"
    if method_text == "insufficient_history":
        return "기간 데이터 부족"
    return "단순 NAV 기준"


def _contribution_by_ticker(
    *,
    snapshot: AccountSnapshot,
    ledger_events: list[LedgerEvent],
    warnings: list[str] | None = None,
) -> list[dict[str, Any]]:
    positions_by_canonical: dict[str, Any] = {}
    positions_by_base_code: dict[str, str] = {}
    for position in snapshot.positions:
        canonical = str(position.canonical_ticker or "").strip().upper()
        if not canonical:
            continue
        positions_by_canonical[canonical] = position
        for candidate in (position.canonical_ticker, position.broker_symbol):
            base_code = _kr_base_code(candidate)
            if base_code:
                positions_by_base_code.setdefault(base_code, canonical)

    realized: dict[str, float] = {}
    for event in ledger_events:
        if event.realized_pnl_krw is None or not event.ticker:
            continue
        ticker = _canonical_contribution_ticker(
            event.ticker,
            positions_by_canonical=positions_by_canonical,
            positions_by_base_code=positions_by_base_code,
            warnings=warnings,
        )
        realized[ticker] = realized.get(ticker, 0.0) + float(event.realized_pnl_krw)
    tickers = set(positions_by_canonical) | set(realized)
    rows = []
    for ticker in sorted(tickers):
        position = positions_by_canonical.get(ticker)
        unrealized = float(position.unrealized_pnl_krw if position else 0.0)
        realized_value = float(realized.get(ticker, 0.0))
        rows.append(
            {
                "ticker": ticker,
                "display_name": position.display_name if position else ticker,
                "realized_pnl_krw": int(round(realized_value)),
                "unrealized_pnl_krw": int(round(unrealized)),
                "total_contribution_krw": int(round(realized_value + unrealized)),
            }
        )
    rows.sort(key=lambda item: abs(int(item["total_contribution_krw"])), reverse=True)
    return rows


def _canonical_contribution_ticker(
    ticker: Any,
    *,
    positions_by_canonical: Mapping[str, Any],
    positions_by_base_code: Mapping[str, str],
    warnings: list[str] | None = None,
) -> str:
    normalized = str(ticker or "").strip().upper()
    if not normalized:
        return "-"
    if normalized in positions_by_canonical:
        return normalized
    base_code = _kr_base_code(normalized)
    if base_code and base_code in positions_by_base_code:
        return positions_by_base_code[base_code]
    if base_code and normalized == base_code and warnings is not None:
        warnings.append(f"account_performance_contribution_unresolved_ticker:{normalized}")
    return normalized


def _kr_base_code(ticker: Any) -> str | None:
    normalized = str(ticker or "").strip().upper()
    if normalized.endswith(".KS") or normalized.endswith(".KQ"):
        normalized = normalized[:-3]
    if len(normalized) == 6 and normalized.isdigit():
        return normalized
    return None


def _cost_summary(ledger_events: list[LedgerEvent]) -> dict[str, int]:
    fees = sum(event.fee_krw for event in ledger_events)
    taxes = sum(event.tax_krw for event in ledger_events)
    return {
        "fees_krw": int(round(fees)),
        "taxes_krw": int(round(taxes)),
        "total_cost_krw": int(round(fees + taxes)),
    }


def _cashflow_events_from_ledger(ledger_events: list[LedgerEvent]) -> list[CashflowEvent]:
    events: list[CashflowEvent] = []
    for event in ledger_events:
        try:
            event_type = LedgerEventType(str(event.event_type or LedgerEventType.UNKNOWN.value))
        except ValueError:
            event_type = LedgerEventType.UNKNOWN
        amount = _cashflow_amount_krw(event, event_type)
        if amount is None:
            continue
        events.append(
            CashflowEvent(
                date=event.date,
                event_type=event_type.value,
                amount_krw=float(amount),
                capital_flow=event_type in {LedgerEventType.DEPOSIT, LedgerEventType.WITHDRAWAL},
                performance_flow=event_type
                in {
                    LedgerEventType.DEPOSIT,
                    LedgerEventType.WITHDRAWAL,
                    LedgerEventType.DIVIDEND,
                    LedgerEventType.INTEREST,
                    LedgerEventType.FEE,
                    LedgerEventType.TAX,
                },
                source=event.source,
            )
        )
    return sorted(events, key=lambda item: item.date)


def _cashflow_amount_krw(event: LedgerEvent, event_type: LedgerEventType) -> float | None:
    if event_type == LedgerEventType.DEPOSIT:
        return abs(float(event.gross_amount_krw))
    if event_type == LedgerEventType.WITHDRAWAL:
        return -abs(float(event.gross_amount_krw))
    if event_type in {LedgerEventType.DIVIDEND, LedgerEventType.INTEREST}:
        amount = event.gross_amount_krw if event.gross_amount_krw else event.realized_pnl_krw
        return abs(float(amount or 0.0))
    if event_type == LedgerEventType.FEE:
        amount = event.fee_krw if event.fee_krw else event.gross_amount_krw
        return -abs(float(amount or 0.0))
    if event_type == LedgerEventType.TAX:
        amount = event.tax_krw if event.tax_krw else event.gross_amount_krw
        return -abs(float(amount or 0.0))
    if event_type == LedgerEventType.UNKNOWN and abs(float(event.gross_amount_krw or 0.0)) > 0:
        return float(event.gross_amount_krw)
    return None


def _period_return_profile(
    *,
    period_name: str,
    snapshot_rows: list[dict[str, Any]],
    ledger_events: list[LedgerEvent],
    cashflow_events: list[CashflowEvent],
    start_date: date,
    end_date: date,
    start_value: float,
    end_value: float,
) -> dict[str, Any]:
    simple_nav_return = (end_value - start_value) / start_value if start_value > 0 else None
    if simple_nav_return is None:
        return {
            "simple_nav_return": None,
            "twr_return": None,
            "primary_return": None,
            "primary_return_method": "unavailable",
            "return_method_warning": "invalid_start_nav",
        }

    unknown_material = _has_unknown_material_ledger_events(ledger_events, start_date=start_date, end_date=end_date)
    capital_flows = _cashflows_between(cashflow_events, start_date=start_date, end_date=end_date, capital_only=True)
    if unknown_material:
        return {
            "simple_nav_return": simple_nav_return,
            "twr_return": None,
            "twr_unavailable_reason": "cashflow_adjustment_unavailable",
            "mwr_return": None,
            "mwr_unavailable_reason": "dated_external_cashflows_incomplete",
            "primary_return": simple_nav_return,
            "primary_return_method": "simple_nav_unadjusted",
            "return_method_warning": "cashflow_adjustment_unavailable",
        }
    if capital_flows:
        twr_return = _cashflow_adjusted_twr_return(
            snapshot_rows=snapshot_rows,
            cashflow_events=capital_flows,
            start_date=start_date,
            end_date=end_date,
        )
        if twr_return is not None:
            return {
                "simple_nav_return": simple_nav_return,
                "twr_return": twr_return,
                "twr_unavailable_reason": None,
                "mwr_return": None,
                "mwr_unavailable_reason": "mwr_not_implemented",
                "primary_return": twr_return,
                "primary_return_method": "twr",
                "return_method_warning": None,
            }
        return {
            "simple_nav_return": simple_nav_return,
            "twr_return": None,
            "twr_unavailable_reason": "cashflow_dates_or_nav_snapshots_incomplete",
            "mwr_return": None,
            "mwr_unavailable_reason": "dated_external_cashflows_incomplete",
            "primary_return": simple_nav_return,
            "primary_return_method": "simple_nav_unadjusted",
            "return_method_warning": "cashflow_adjustment_unavailable",
        }

    method = "available_history_twr_equivalent" if str(period_name or "").strip().upper() == "ALL" else "twr_equivalent"
    return {
        "simple_nav_return": simple_nav_return,
        "twr_return": simple_nav_return,
        "twr_unavailable_reason": None,
        "mwr_return": None,
        "mwr_unavailable_reason": "no_external_capital_flows_for_irr",
        "primary_return": simple_nav_return,
        "primary_return_method": method,
        "return_method_warning": None,
    }


def _cashflow_adjusted_twr_return(
    *,
    snapshot_rows: list[dict[str, Any]],
    cashflow_events: list[CashflowEvent],
    start_date: date,
    end_date: date,
) -> float | None:
    rows = [
        row
        for row in snapshot_rows
        if (row_date := _parse_date(str(row.get("date") or ""))) is not None and start_date <= row_date <= end_date
    ]
    if len(rows) < 2:
        return None
    cumulative = 1.0
    for previous, current in zip(rows, rows[1:]):
        previous_date = _parse_date(str(previous.get("date") or ""))
        current_date = _parse_date(str(current.get("date") or ""))
        previous_value = _float_or_none(previous.get("account_value_krw"))
        current_value = _float_or_none(current.get("account_value_krw"))
        if previous_date is None or current_date is None or previous_value is None or current_value is None or previous_value <= 0:
            return None
        flow_sum = sum(
            event.amount_krw
            for event in cashflow_events
            if (event_date := _parse_date(event.date)) is not None and previous_date < event_date <= current_date
        )
        interval_return = (current_value - flow_sum - previous_value) / previous_value
        cumulative *= 1.0 + interval_return
    return cumulative - 1.0


def _cashflows_between(
    cashflow_events: list[CashflowEvent],
    *,
    start_date: date,
    end_date: date,
    capital_only: bool = False,
) -> list[CashflowEvent]:
    rows = []
    for event in cashflow_events:
        event_date = _parse_date(event.date)
        if event_date is None or event_date < start_date or event_date > end_date:
            continue
        if capital_only and not event.capital_flow:
            continue
        rows.append(event)
    return rows


def _has_unknown_material_ledger_events(
    ledger_events: list[LedgerEvent],
    *,
    start_date: date,
    end_date: date,
) -> bool:
    for event in ledger_events:
        event_date = _parse_date(event.date)
        if event_date is None or event_date < start_date or event_date > end_date:
            continue
        if str(event.event_type or "").lower() != LedgerEventType.UNKNOWN.value:
            continue
        if abs(float(event.gross_amount_krw or 0.0)) > 0:
            return True
    return False


def reconcile_account_performance(
    *,
    snapshot_rows: list[dict[str, Any]],
    ledger_events: list[LedgerEvent],
    contribution_rows: list[dict[str, Any]],
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    if len(snapshot_rows) < 2:
        return {
            "start_nav_krw": None,
            "end_nav_krw": None,
            "simple_nav_pnl_krw": None,
            "sum_position_contribution_krw": None,
            "external_cashflow_net_krw": None,
            "fees_taxes_krw": None,
            "unexplained_difference_krw": None,
            "unexplained_difference_pct_of_nav": None,
            "reconciliation_status": "UNAVAILABLE",
            "reconciliation_severity": "unavailable",
        }
    start_nav = _float_or_none(snapshot_rows[0].get("account_value_krw"))
    end_nav = _float_or_none(snapshot_rows[-1].get("account_value_krw"))
    if start_nav is None or end_nav is None:
        return {
            "start_nav_krw": None,
            "end_nav_krw": None,
            "simple_nav_pnl_krw": None,
            "sum_position_contribution_krw": None,
            "external_cashflow_net_krw": None,
            "fees_taxes_krw": None,
            "unexplained_difference_krw": None,
            "unexplained_difference_pct_of_nav": None,
            "reconciliation_status": "UNAVAILABLE",
            "reconciliation_severity": "unavailable",
        }

    cashflow_events = _cashflow_events_from_ledger(ledger_events)
    unknown_material = any(
        str(event.event_type or "").lower() == LedgerEventType.UNKNOWN.value
        and abs(float(event.gross_amount_krw or 0.0)) > 0
        for event in ledger_events
    )
    external_cashflow_net = (
        None
        if unknown_material
        else sum(
            event.amount_krw
            for event in cashflow_events
            if event.event_type
            in {
                LedgerEventType.DEPOSIT.value,
                LedgerEventType.WITHDRAWAL.value,
                LedgerEventType.DIVIDEND.value,
                LedgerEventType.INTEREST.value,
            }
        )
    )
    simple_nav_pnl = end_nav - start_nav
    contribution_sum = sum(
        float(item.get("total_contribution_krw") or 0.0)
        for item in contribution_rows
        if isinstance(item, Mapping)
    )
    fees_taxes = sum(float(event.fee_krw or 0.0) + float(event.tax_krw or 0.0) for event in ledger_events)
    unexplained = None if external_cashflow_net is None else simple_nav_pnl - contribution_sum - external_cashflow_net
    unexplained_pct = unexplained / end_nav if unexplained is not None and end_nav else None
    materiality_pct = abs(unexplained_pct) if unexplained_pct is not None else None
    if unexplained is None:
        status = "UNAVAILABLE"
        severity = "unavailable"
        if warnings is not None and unknown_material:
            warnings.append("account_performance_cashflow_unadjusted")
    elif materiality_pct is not None and materiality_pct <= 0.02:
        status = "OK"
        severity = "ok"
    elif materiality_pct is not None and materiality_pct <= 0.05:
        status = "WARNING"
        severity = "warning"
    else:
        status = "FAILED"
        severity = "critical" if materiality_pct is not None and materiality_pct > 0.20 else "failed"
    if warnings is not None and status in {"WARNING", "FAILED"}:
        warnings.append("account_performance_unreconciled_pnl")
        warnings.append("account_performance_contribution_not_total_return")

    return {
        "start_nav_krw": int(round(start_nav)),
        "end_nav_krw": int(round(end_nav)),
        "simple_nav_pnl_krw": int(round(simple_nav_pnl)),
        "sum_position_contribution_krw": int(round(contribution_sum)),
        "external_cashflow_net_krw": int(round(external_cashflow_net)) if external_cashflow_net is not None else None,
        "fees_taxes_krw": int(round(fees_taxes)),
        "unexplained_difference_krw": int(round(unexplained)) if unexplained is not None else None,
        "unexplained_difference_pct_of_nav": round(unexplained_pct, 6) if unexplained_pct is not None else None,
        "reconciliation_status": status,
        "reconciliation_severity": severity,
    }


def _summary(periods: list[dict[str, Any]]) -> dict[str, Any]:
    default = _default_period(periods)
    if not default:
        return {}
    default_label = _period_summary_label(default)
    return {
        "default_period": default_label,
        "source_period": default.get("period"),
        "default_period_label": _period_display_label(default),
        "requested_start_date": default.get("requested_start_date"),
        "start_date": default.get("start_date"),
        "end_date": default.get("end_date"),
        "partial": bool(default.get("partial")),
        "simple_nav_return": default.get("simple_nav_return"),
        "twr_return": default.get("twr_return"),
        "twr_unavailable_reason": default.get("twr_unavailable_reason"),
        "mwr_return": default.get("mwr_return"),
        "mwr_unavailable_reason": default.get("mwr_unavailable_reason"),
        "primary_return": default.get("primary_return"),
        "primary_return_method": default.get("primary_return_method"),
        "return_method_warning": default.get("return_method_warning"),
        "actual_return": default.get("actual_return"),
        "period_coverage": default.get("period_coverage") or {},
        "best_excess": default.get("best_excess") or {},
        "worst_excess": default.get("worst_excess") or {},
    }


def _summary_with_performance_confidence(
    summary: dict[str, Any],
    reconciliation: Mapping[str, Any],
) -> dict[str, Any]:
    if not summary:
        return summary
    result = dict(summary)
    status = str(reconciliation.get("reconciliation_status") or "").upper()
    severity = str(reconciliation.get("reconciliation_severity") or "").lower()
    if status == "FAILED":
        result.update(
            {
                "performance_confidence": "low",
                "performance_confidence_reason": "unreconciled_nav_vs_position_pnl",
                "hide_excess_headline": True,
                "requires_manual_reconciliation": True,
                "reconciliation_severity": severity or "failed",
            }
        )
    elif status in {"WARNING", "UNAVAILABLE"}:
        result.update(
            {
                "performance_confidence": "medium",
                "performance_confidence_reason": (
                    "cashflow_or_reconciliation_incomplete"
                    if status == "UNAVAILABLE"
                    else "reconciliation_warning"
                ),
                "hide_excess_headline": False,
                "requires_manual_reconciliation": status == "UNAVAILABLE",
                "reconciliation_severity": severity or status.lower(),
            }
        )
    else:
        result.update(
            {
                "performance_confidence": "high",
                "performance_confidence_reason": "reconciled_or_no_material_difference",
                "hide_excess_headline": False,
                "requires_manual_reconciliation": False,
                "reconciliation_severity": severity or "ok",
            }
        )
    return result


def _default_period(periods: list[dict[str, Any]]) -> dict[str, Any] | None:
    eligible = [
        period
        for period in periods
        if _float_or_none(period.get("actual_return")) is not None
        and _period_summary_eligible(period)
        and not bool(period.get("same_actual_window_as"))
    ]
    non_all_eligible = [period for period in eligible if str(period.get("period") or "").upper() != "ALL"]
    if non_all_eligible:
        return max(
            non_all_eligible,
            key=lambda item: int(
                ((item.get("period_coverage") or {}).get("requested_days") or 0)
                if isinstance(item.get("period_coverage"), Mapping)
                else 0
            ),
        )
    all_period = next((period for period in periods if str(period.get("period") or "").upper() == "ALL"), None)
    if all_period and _float_or_none(all_period.get("actual_return")) is not None:
        return all_period
    for preferred in ("YTD", "1Y", "6M", "3M", "1M", "ALL"):
        for period in periods:
            if period.get("period") == preferred and _float_or_none(period.get("actual_return")) is not None:
                return period
    for period in periods:
        if _float_or_none(period.get("actual_return")) is not None:
            return period
    return periods[-1] if periods else None


def _period_summary_eligible(period: Mapping[str, Any]) -> bool:
    coverage = period.get("period_coverage")
    if isinstance(coverage, Mapping):
        return bool(coverage.get("is_summary_eligible"))
    return _float_or_none(period.get("actual_return")) is not None and period.get("status") not in {
        "insufficient_history",
        "duplicate_actual_window",
    }


def _period_display_label(period: Mapping[str, Any]) -> str:
    if str(period.get("period") or "").strip().upper() == "ALL":
        return "사용 가능 전체 기간"
    return str(period.get("period") or "-")


def _benchmark_simple_return(rows: list[dict[str, Any]], *, start_date: date, end_date: date) -> float | None:
    start = _price_on_or_after(rows, start_date)
    end = _price_on_or_before(rows, end_date)
    if start is None or end is None or start <= 0:
        return None
    return (end - start) / start


def benchmark_same_cashflow_return(
    rows: list[dict[str, Any]],
    *,
    external_cashflows: list[CashflowEvent],
    start_date: date,
    end_date: date,
    start_value: float,
) -> float | None:
    start = _price_on_or_after(rows, start_date)
    end = _price_on_or_before(rows, end_date)
    if start is None or end is None or start <= 0 or start_value <= 0:
        return None
    shares = start_value / start
    for event in external_cashflows:
        if not event.capital_flow:
            continue
        event_date = _parse_date(event.date)
        if event_date is None or event_date < start_date or event_date > end_date:
            continue
        price = _price_on_or_before(rows, event_date) or start
        if price <= 0:
            continue
        shares += float(event.amount_krw) / price
    final_value = shares * end
    return (final_value - start_value) / start_value


def _benchmark_cashflow_return(
    rows: list[dict[str, Any]],
    *,
    ledger_events: list[LedgerEvent],
    start_date: date,
    end_date: date,
    start_value: float,
) -> float | None:
    return benchmark_same_cashflow_return(
        rows,
        external_cashflows=_cashflow_events_from_ledger(ledger_events),
        start_date=start_date,
        end_date=end_date,
        start_value=start_value,
    )


def _snapshot_values_between(rows: list[dict[str, Any]], start_date: date, end_date: date) -> list[float]:
    values = []
    for row in rows:
        row_date = _parse_date(str(row.get("date")))
        if row_date is None or row_date < start_date or row_date > end_date:
            continue
        value = _float_or_none(row.get("account_value_krw"))
        if value is not None:
            values.append(value)
    return values


def _max_drawdown(values: list[float]) -> float | None:
    if not values:
        return None
    peak = values[0]
    drawdown = 0.0
    for value in values:
        peak = max(peak, value)
        if peak > 0:
            drawdown = min(drawdown, (value - peak) / peak)
    return round(drawdown, 6)


def _volatility(values: list[float]) -> float | None:
    if len(values) < 3:
        return None
    returns = []
    for before, after in zip(values, values[1:]):
        if before > 0:
            returns.append((after - before) / before)
    if len(returns) < 2:
        return None
    mean = sum(returns) / len(returns)
    variance = sum((item - mean) ** 2 for item in returns) / (len(returns) - 1)
    return round(math.sqrt(variance), 6)


def _first_snapshot_on_or_after(rows: list[dict[str, Any]], target: date) -> dict[str, Any] | None:
    for row in rows:
        row_date = _parse_date(str(row.get("date")))
        if row_date and row_date >= target:
            return row
    return None


def _last_snapshot_on_or_before(rows: list[dict[str, Any]], target: date) -> dict[str, Any] | None:
    candidate = None
    for row in rows:
        row_date = _parse_date(str(row.get("date")))
        if row_date and row_date <= target:
            candidate = row
    return candidate


def _period_start(period_name: str, *, end_date: date, snapshot_rows: list[dict[str, Any]]) -> date:
    normalized = str(period_name or "").strip().upper()
    if normalized == "1M":
        return end_date - timedelta(days=30)
    if normalized == "3M":
        return end_date - timedelta(days=90)
    if normalized == "6M":
        return end_date - timedelta(days=180)
    if normalized == "1Y":
        return end_date - timedelta(days=365)
    if normalized == "YTD":
        return date(end_date.year, 1, 1)
    first = _parse_date(str(snapshot_rows[0].get("date"))) if snapshot_rows else None
    return first or end_date


def _default_start_date(snapshot_rows: list[dict[str, Any]], *, lookback_days: int) -> date:
    first = _parse_date(str(snapshot_rows[0].get("date"))) if snapshot_rows else None
    fallback = date.today() - timedelta(days=max(30, int(lookback_days)))
    return max(first, fallback) if first else fallback


def _normalize_price_rows(raw: Any) -> list[dict[str, Any]]:
    values = raw.get("prices") if isinstance(raw, Mapping) else raw
    if not isinstance(values, list):
        return []
    rows = []
    for item in values:
        if isinstance(item, Mapping):
            date_text = _first_text(
                item,
                ("date", "asof", "timestamp", "stck_bsop_date", "xymd", "bsop_date", "trd_dd"),
            )
            close = _first_float(
                item,
                (
                    "close",
                    "price",
                    "last",
                    "stck_clpr",
                    "bstp_nmix_prpr",
                    "ovrs_nmix_prpr",
                    "clos",
                    "last_price",
                ),
            )
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            date_text = str(item[0])
            close = _float_or_none(item[1])
        else:
            continue
        parsed = _parse_date(date_text)
        if parsed and close is not None:
            rows.append({"date": parsed.isoformat(), "close": float(close)})
    return sorted(rows, key=lambda item: item["date"])


def _price_on_or_after(rows: list[dict[str, Any]], target: date) -> float | None:
    for row in rows:
        row_date = _parse_date(str(row.get("date")))
        if row_date and row_date >= target:
            return _float_or_none(row.get("close"))
    return None


def _price_on_or_before(rows: list[dict[str, Any]], target: date) -> float | None:
    value = None
    for row in rows:
        row_date = _parse_date(str(row.get("date")))
        if row_date and row_date <= target:
            value = _float_or_none(row.get("close"))
    return value


def _benchmark_names(settings: Any, market_scope: str) -> tuple[str, ...]:
    if market_scope == "us":
        return tuple(getattr(settings, "us_benchmarks", ("SPY", "QQQ")) or ("SPY", "QQQ"))
    return tuple(getattr(settings, "kr_benchmarks", ("KOSPI", "KOSDAQ")) or ("KOSPI", "KOSDAQ"))


def _benchmark_yfinance_symbol(market_scope: str, benchmark: str) -> str | None:
    if market_scope == "us":
        return str(_US_BENCHMARK_SYMBOLS.get(benchmark, {}).get("yfinance") or benchmark)
    return str(_KR_BENCHMARK_SYMBOLS.get(benchmark, {}).get("yfinance") or benchmark)


def _benchmark_aliases() -> dict[str, str]:
    aliases: dict[str, str] = {}
    for name, meta in {**_KR_BENCHMARK_SYMBOLS, **_US_BENCHMARK_SYMBOLS}.items():
        aliases[name] = str(meta.get("yfinance") or name)
    return aliases


def _public_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    allowed = {
        "status",
        "generated_at",
        "market_scope",
        "benchmarks",
        "summary",
        "periods",
        "chart_data",
        "costs",
        "contribution_by_ticker",
        "reconciliation",
        "data_quality",
        "public_sanitization",
    }
    return {key: value for key, value in payload.items() if key in allowed}


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _market_scope(profile: PortfolioProfile) -> str:
    scope = str(getattr(profile, "market_scope", "kr") or "kr").strip().lower()
    return "us" if scope in {"us", "overseas"} else "kr"


def _provider_label(settings: Any) -> str:
    provider = str(getattr(settings, "price_provider", "yfinance") or "yfinance").strip().lower()
    if getattr(settings, "price_history_path", None):
        return f"local_json+{provider}" if provider not in {"local_json", "none"} else "local_json"
    return provider


def _settings_ratio(value: Any, *, default: float) -> float:
    if value is None:
        return float(default)
    try:
        number = float(value)
    except (TypeError, ValueError):
        return float(default)
    return max(0.0, min(1.0, number))


def _side_from_row(row: Mapping[str, Any]) -> str:
    code = _first_text(row, ("sll_buy_dvsn_cd", "sll_buy_dvsn", "trad_dvsn", "tr_dvsn_cd"))
    name = _first_text(row, ("sll_buy_dvsn_name", "trad_dvsn_name", "tr_dvsn_name", "rmks_name")).lower()
    if code in {"02", "2", "BUY"} or "buy" in name or "매수" in name:
        return "BUY"
    if code in {"01", "1", "SELL"} or "sell" in name or "매도" in name:
        return "SELL"
    return "UNKNOWN"


def _classify_ledger_event_type(row: Mapping[str, Any], *, side: str) -> LedgerEventType:
    if side in {"BUY", "SELL"}:
        return LedgerEventType.TRADE
    explicit = _first_text(
        row,
        (
            "event_type",
            "ledger_event_type",
            "transaction_type",
            "transaction_kind",
            "cashflow_type",
            "tr_dvsn",
            "tr_dvsn_name",
            "rmks",
            "rmks_name",
            "memo",
            "description",
        ),
    ).strip()
    normalized = re.sub(r"[\s_\-]+", "", explicit).lower()
    if normalized:
        if normalized in {"deposit", "cashdeposit", "dpst", "입금"} or "deposit" in normalized or "입금" in normalized:
            return LedgerEventType.DEPOSIT
        if (
            normalized in {"withdrawal", "withdraw", "cashwithdrawal", "wthdr", "출금"}
            or "withdraw" in normalized
            or "출금" in normalized
        ):
            return LedgerEventType.WITHDRAWAL
        if normalized in {"dividend", "div"} or "dividend" in normalized or "배당" in normalized:
            return LedgerEventType.DIVIDEND
        if normalized in {"interest", "int"} or "interest" in normalized or "이자" in normalized:
            return LedgerEventType.INTEREST
        if normalized in {"fee", "commission", "cmsn"} or "fee" in normalized or "commission" in normalized or "수수료" in normalized:
            return LedgerEventType.FEE
        if normalized == "tax" or "tax" in normalized or "세금" in normalized or "제세" in normalized:
            return LedgerEventType.TAX
        if "fx" in normalized or "exchange" in normalized or "환전" in normalized:
            return LedgerEventType.FX_CONVERSION
        if normalized in {"trade", "fill", "execution", "체결"}:
            return LedgerEventType.TRADE

    if _first_float(row, ("dpst_amt", "deposit_amount", "cash_deposit_krw")) is not None:
        return LedgerEventType.DEPOSIT
    if _first_float(row, ("wthdr_amt", "withdrawal_amount", "cash_withdrawal_krw")) is not None:
        return LedgerEventType.WITHDRAWAL
    if _first_float(row, ("dividend_krw", "dvdn_amt", "dividend_amount")) is not None:
        return LedgerEventType.DIVIDEND
    if _first_float(row, ("interest_krw", "int_amt", "interest_amount")) is not None:
        return LedgerEventType.INTEREST
    if _first_float(row, ("tax_amt", "tax", "transaction_tax")) not in (None, 0):
        return LedgerEventType.TAX
    if _first_float(row, ("fee_amt", "fee", "cmsn_amt", "commission")) not in (None, 0):
        return LedgerEventType.FEE
    return LedgerEventType.UNKNOWN


def _to_krw(value: float, *, fx_rate: float | None) -> float:
    if fx_rate and fx_rate > 0:
        return float(value) * float(fx_rate)
    return float(value)


def _first_text(payload: Mapping[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = payload.get(key)
        if value in (None, ""):
            continue
        return str(value).strip()
    return ""


def _first_float(payload: Mapping[str, Any], keys: tuple[str, ...]) -> float | None:
    for key in keys:
        value = _float_or_none(payload.get(key))
        if value is not None:
            return value
    return None


def _float_or_none(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        if isinstance(value, str):
            value = value.replace(",", "")
        return float(value)
    except (TypeError, ValueError):
        return None


def _int_or_none(value: Any) -> int | None:
    number = _float_or_none(value)
    if number is None:
        return None
    return int(round(number))


def _parse_date(value: str) -> date | None:
    text = str(value or "").strip()[:10]
    if len(text) == 8 and text.isdigit():
        text = f"{text[:4]}-{text[4:6]}-{text[6:8]}"
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def _date_text(value: date) -> str:
    return value.strftime("%Y%m%d")


def _short_error(exc: Exception) -> str:
    text = str(exc).strip().replace("\n", " ") or exc.__class__.__name__
    text = re.sub(r"(CANO=)[^&\s]+", r"\1***MASKED***", text)
    text = re.sub(r"(ACNT_PRDT_CD=)[^&\s]+", r"\1***MASKED***", text)
    text = re.sub(r"\b\d{8}-\d{2}\b", "***MASKED***", text)
    return text[:180]


def _pct(value: Any) -> str:
    number = _float_or_none(value)
    if number is None:
        return "-"
    return f"{number * 100:.2f}%"


def _krw(value: Any) -> str:
    number = _float_or_none(value)
    if number is None:
        return "-"
    return f"{int(round(number)):,} KRW"
