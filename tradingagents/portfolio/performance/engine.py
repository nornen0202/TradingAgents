from __future__ import annotations

import json
import math
import re
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

from tradingagents.agents.utils.instrument_resolver import resolve_instrument
from tradingagents.portfolio.account_models import AccountSnapshot, PortfolioProfile
from tradingagents.portfolio.benchmarks.dca_engine import build_etf_dca_comparison
from tradingagents.portfolio.performance.broker_kis import (
    fetch_kis_domestic_broker_performance,
    fetch_kis_domestic_broker_performance_periods,
    load_broker_performance_baseline,
    load_broker_performance_baseline_periods,
)
from tradingagents.portfolio.performance.broker_models import (
    BrokerPerformanceComparison,
    BrokerPerformanceSummary,
)


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
    broker_period_start, broker_period_end = _broker_period_window(
        settings=settings,
        snapshot_rows=snapshot_rows,
        end_date=end_date,
    )
    broker_performance = _load_broker_performance(
        profile=profile,
        settings=settings,
        market_scope=market_scope,
        period_start=broker_period_start,
        period_end=broker_period_end,
        benchmark_prices=benchmark_prices,
        warnings=warnings,
    )
    cashflow_events = _cashflow_events_from_ledger(ledger_events)
    broker_external_capital_flow_count = broker_performance.external_capital_flow_count if broker_performance else 0
    snapshot_external_capital_flow_count = len([event for event in cashflow_events if event.capital_flow])
    if broker_external_capital_flow_count and not snapshot_external_capital_flow_count:
        warnings.append("account_performance_broker_external_flows_not_in_snapshot_ledger")
    min_coverage_ratio = _settings_ratio(getattr(settings, "min_coverage_ratio", None), default=0.8)
    periods = _compute_periods(
        snapshot_rows=snapshot_rows,
        ledger_events=ledger_events,
        cashflow_events=cashflow_events,
        broker_performance=broker_performance,
        benchmark_prices=benchmark_prices,
        period_names=tuple(getattr(settings, "periods", ("1M", "3M", "6M", "YTD", "1Y", "ALL"))),
        end_date=end_date,
        min_coverage_ratio=min_coverage_ratio,
        warnings=warnings,
    )
    contribution = _contribution_by_ticker(
        snapshot=snapshot,
        snapshot_rows=snapshot_rows,
        ledger_events=ledger_events,
        warnings=warnings,
    )
    reconciliation = reconcile_account_performance(
        snapshot_rows=snapshot_rows,
        ledger_events=ledger_events,
        contribution_rows=contribution,
        warnings=warnings,
    )
    reconciliation = _reconciliation_with_guidance(
        reconciliation,
        profile=profile,
        broker_performance=broker_performance,
        settings=settings,
        warnings=warnings,
    )
    costs = _cost_summary(ledger_events)
    summary = _summary(periods)
    summary = _summary_with_performance_confidence(summary, reconciliation)
    summary = _summary_with_snapshot_display_policy(summary, settings=settings)
    broker_comparison = _broker_performance_comparison(
        broker_performance=broker_performance,
        snapshot=snapshot,
        summary=summary,
        market_scope=market_scope,
        warnings=warnings,
    )
    summary = _summary_with_broker_comparison(summary, broker_comparison)
    periods = _periods_with_display_policy(periods, summary=summary)
    chart_data = _build_chart_data(
        snapshot_rows=snapshot_rows,
        benchmark_prices=benchmark_prices,
        cashflow_events=cashflow_events,
        summary=summary,
        warnings=warnings,
    )
    profit_calendar = _build_profit_calendar(
        settings=settings,
        profile=profile,
        snapshot_rows=snapshot_rows,
        ledger_events=ledger_events,
        cashflow_events=cashflow_events,
        broker_performance=broker_performance,
        benchmark_prices=benchmark_prices,
        end_date=end_date,
        reconciliation=reconciliation,
        warnings=warnings,
    )
    etf_dca_comparison = build_etf_dca_comparison(
        snapshot=snapshot,
        settings=settings,
        summary=summary,
        periods=periods,
        broker_performance=broker_performance,
        reconciliation=reconciliation,
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
        "profit_calendar": profit_calendar,
        "broker_performance": broker_performance.to_dict() if broker_performance else {},
        "broker_performance_comparison": broker_comparison.to_dict() if broker_comparison else {},
        "etf_alternative_comparison": etf_dca_comparison.to_public_dict() if etf_dca_comparison else {},
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
            "external_capital_flow_count": max(
                snapshot_external_capital_flow_count,
                broker_external_capital_flow_count,
            ),
            "snapshot_external_capital_flow_count": snapshot_external_capital_flow_count,
            "broker_external_capital_flow_count": broker_external_capital_flow_count,
            "broker_performance_available": bool(broker_performance),
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
    broker_raw_json = private_dir / "broker_performance_raw.json"
    broker_normalized_json = private_dir / "broker_performance_normalized.json"
    broker_comparison_json = private_dir / "broker_performance_comparison.json"
    etf_alt_raw_json = private_dir / "etf_alternative_portfolios_raw.json"
    etf_alt_public_json = private_dir / "etf_alternative_portfolios_public.json"
    etf_alt_policy_json = private_dir / "etf_alternative_policy.json"
    etf_dca_cashflows_json = private_dir / "etf_dca_cashflows.json"
    cashflows_json = private_dir / "cashflows.json"
    cashflows_audit_json = private_dir / "cashflows_audit.json"
    etf_dca_transactions_json = private_dir / "etf_dca_benchmark_transactions.json"
    etf_dca_results_json = private_dir / "etf_dca_benchmark_results.json"
    etf_dca_equity_curves_json = private_dir / "etf_dca_equity_curves.json"
    etf_dca_comparison_json = private_dir / "etf_dca_comparison.json"
    etf_dca_policy_json = private_dir / "etf_dca_policy_recommendation.json"

    _write_json(report_json, payload)
    _write_json(public_json, public_payload)
    _write_json(chart_json, public_payload.get("chart_data") or {})
    if broker_performance:
        _write_json(broker_raw_json, broker_performance.raw_summary)
        _write_json(broker_normalized_json, broker_performance.to_dict())
    if broker_comparison:
        _write_json(broker_comparison_json, broker_comparison.to_dict())
    if etf_dca_comparison:
        etf_public = etf_dca_comparison.to_public_dict()
        etf_raw = etf_dca_comparison.to_raw_dict()
        _write_json(etf_alt_raw_json, etf_raw)
        _write_json(etf_alt_public_json, etf_public)
        _write_json(etf_alt_policy_json, etf_public.get("policy") or {})
        _write_json(etf_dca_cashflows_json, [item.to_dict(include_raw=True) for item in etf_dca_comparison.raw_cashflows])
        _write_json(cashflows_json, [item.to_dict(include_raw=False) for item in etf_dca_comparison.raw_cashflows])
        _write_json(
            cashflows_audit_json,
            {
                "exact_dated_cashflows_available": etf_public.get("status") == "OK",
                "cashflow_count": (etf_public.get("cashflows") or {}).get("dated_flow_count", 0),
                "deposit_count": len([item for item in etf_dca_comparison.raw_cashflows if item.flow_type == "deposit"]),
                "withdrawal_count": len([item for item in etf_dca_comparison.raw_cashflows if item.flow_type == "withdrawal"]),
                "sources": sorted({item.source for item in etf_dca_comparison.raw_cashflows}),
                "warnings": etf_public.get("warnings") or [],
            },
        )
        raw_alternatives = etf_raw.get("alternatives") if isinstance(etf_raw, Mapping) else []
        transactions = []
        equity_curves = []
        if isinstance(raw_alternatives, list):
            for alternative in raw_alternatives:
                if not isinstance(alternative, Mapping):
                    continue
                for transaction in alternative.get("transactions") or []:
                    if isinstance(transaction, Mapping):
                        transactions.append(dict(transaction))
                curve = alternative.get("equity_curve") or []
                if isinstance(curve, list):
                    equity_curves.append(
                        {
                            "benchmark_id": alternative.get("key"),
                            "display_name": alternative.get("label"),
                            "points": [dict(point) for point in curve if isinstance(point, Mapping)],
                        }
                    )
        _write_json(etf_dca_transactions_json, {"transactions": transactions})
        _write_json(etf_dca_results_json, {"benchmarks": etf_public.get("alternatives") or []})
        _write_json(etf_dca_equity_curves_json, {"equity_curves": equity_curves})
        _write_json(etf_dca_comparison_json, etf_public)
        _write_json(etf_dca_policy_json, etf_public.get("policy") or {})
    report_md.write_text(markdown, encoding="utf-8")

    artifacts = {
        "account_performance_report_json": report_json.as_posix(),
        "account_performance_public_json": public_json.as_posix(),
        "account_performance_chart_data_json": chart_json.as_posix(),
        "account_performance_report_md": report_md.as_posix(),
    }
    if broker_performance:
        artifacts.update(
            {
                "broker_performance_raw_json": broker_raw_json.as_posix(),
                "broker_performance_normalized_json": broker_normalized_json.as_posix(),
            }
        )
    if broker_comparison:
        artifacts["broker_performance_comparison_json"] = broker_comparison_json.as_posix()
    if etf_dca_comparison:
        artifacts.update(
            {
                "etf_alternative_portfolios_public_json": etf_alt_public_json.as_posix(),
                "etf_alternative_policy_json": etf_alt_policy_json.as_posix(),
                "etf_dca_benchmark_results_json": etf_dca_results_json.as_posix(),
                "etf_dca_comparison_json": etf_dca_comparison_json.as_posix(),
                "etf_dca_policy_recommendation_json": etf_dca_policy_json.as_posix(),
            }
        )
    return artifacts


def render_account_performance_markdown(payload: Mapping[str, Any]) -> str:
    summary = payload.get("summary") if isinstance(payload.get("summary"), Mapping) else {}
    periods = payload.get("periods") if isinstance(payload.get("periods"), list) else []
    costs = payload.get("costs") if isinstance(payload.get("costs"), Mapping) else {}
    contribution = payload.get("contribution_by_ticker") if isinstance(payload.get("contribution_by_ticker"), list) else []
    reconciliation = payload.get("reconciliation") if isinstance(payload.get("reconciliation"), Mapping) else {}
    quality = payload.get("data_quality") if isinstance(payload.get("data_quality"), Mapping) else {}
    broker = payload.get("broker_performance") if isinstance(payload.get("broker_performance"), Mapping) else {}
    broker_comparison = (
        payload.get("broker_performance_comparison")
        if isinstance(payload.get("broker_performance_comparison"), Mapping)
        else {}
    )
    etf_comparison = (
        payload.get("etf_alternative_comparison")
        if isinstance(payload.get("etf_alternative_comparison"), Mapping)
        else {}
    )
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
        if period.get("display_eligible") is False or period.get("trust_state") == "unreconciled_reference":
            rows.append(
                "| "
                f"{period_label} | "
                "검증 전 참고 불가 | "
                "정합성 실패 | "
                "정합성 검증 후 해석 | "
                "- | "
                f"{', '.join(str(item.get('benchmark')) for item in period.get('simple_benchmarks', []) if isinstance(item, Mapping)) or '-'} |"
            )
            continue
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
        ticker = str(item.get("ticker") or "-")
        display_name = str(item.get("display_name") or "").strip()
        label = display_name if display_name and display_name != ticker else ticker
        display_label = f"{label} ({ticker})" if label != ticker else label
        contribution_rows.append(
            f"- {display_label}: 기여도 {_krw(item.get('total_contribution_krw'))} "
            f"(실현 {_krw(item.get('realized_pnl_krw'))}, 미실현 변화 {_krw(item.get('unrealized_pnl_krw'))})"
        )

    warnings = quality.get("warnings") if isinstance(quality.get("warnings"), list) else []
    warning_lines = [f"- {_friendly_data_quality_warning(item)}" for item in warnings[:8]] or ["- 특이사항 없음"]
    action_lines = _resolution_action_lines(reconciliation.get("resolution_actions"))
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
    contribution_status = _reconciliation_status_label(reconciliation.get("reconciliation_status"))
    broker_lines = []
    if broker:
        broker_lines = [
            "",
            "### 한국투자증권 앱 기준 성과",
            "",
            f"- 기간: `{broker.get('period_start') or '-'} ~ {broker.get('period_end') or '-'}`",
            f"- 브로커 수익률: `{_pct_points(broker.get('balance_return_pct'))}`",
            f"- 투자손익: `{_krw(broker.get('investment_pnl_krw'))}`",
            f"- 매매손익: `{_krw(broker.get('realized_trade_pnl_krw'))}` "
            f"(`{_pct_points(broker.get('realized_trade_return_pct'))}`)",
            f"- 기초/기말자산: `{_krw(broker.get('start_asset_krw'))} -> {_krw(broker.get('end_asset_krw'))}`",
            f"- 입금/출금: `{_krw(broker.get('deposit_amount_krw'))} / {_krw(broker.get('withdrawal_amount_krw'))}`",
            f"- 브로커-내부 비교: `{broker_comparison.get('comparison_status') or '-'}`",
        ]
    etf_lines = []
    if etf_comparison:
        etf_status = str(etf_comparison.get("status") or "-")
        etf_status_label = _etf_status_label(etf_status)
        etf_actual_source = _actual_source_label(etf_comparison.get("actual_source"))
        etf_cashflows = etf_comparison.get("cashflows") if isinstance(etf_comparison.get("cashflows"), Mapping) else {}
        alternatives = [
            item
            for item in etf_comparison.get("alternatives", [])
            if isinstance(item, Mapping) and item.get("status") == "OK"
        ]
        best_etf = max(
            alternatives,
            key=lambda item: _float_or_none(item.get("balance_return_pct")) if _float_or_none(item.get("balance_return_pct")) is not None else -10**9,
        ) if alternatives else {}
        blended = next((item for item in alternatives if str(item.get("key") or "").upper() == "BLENDED"), {})
        etf_lines = [
            "",
            "### 동일 입금일 ETF 대체 포트폴리오 비교",
            "",
            f"- 상태: `{etf_status_label}`",
            f"- 실제 성과 기준: `{etf_actual_source}` "
            f"({_pct_points((etf_comparison.get('actual') or {}).get('balance_return_pct'))})",
            f"- 날짜별 현금흐름: `{etf_cashflows.get('dated_flow_count') or 0}건` "
            f"(입금 {_krw(etf_cashflows.get('deposit_amount_krw'))}, 출금 {_krw(etf_cashflows.get('withdrawal_amount_krw'))})",
            f"- ETF 최고 수익률: `{best_etf.get('label') or '-'}` "
            f"({_pct_points(best_etf.get('balance_return_pct'))})",
            f"- 혼합 벤치마크: `{_pct_points(blended.get('balance_return_pct'))}` / "
            f"실제 대비 `{_pct_points(blended.get('excess_return_pct'))}`",
        ]
        if etf_status == "actual_performance_unavailable":
            etf_lines.extend(
                [
                    "- 사유: `실제 계좌 성과가 검증되지 않아 ETF 대체 비교를 계산하지 않았습니다.`",
                    "- 필요한 실제 성과: `브로커 계좌 수익률` 또는 `정합성 OK/WARNING 내부 스냅샷`",
                    "- KIS 자동화 상태: `체결/손익/권리 이벤트는 자동 조회, 일반 계좌 외부 입출금 일자 원장은 API 미확인`",
                    "- 선택적 fallback: `config/account_cashflows.csv` 또는 "
                    "`etf_dca_benchmarks.manual_cashflow_csv_path/manual_cashflow_json_path`",
                ]
            )
    hide_snapshot = (
        str(reconciliation.get("reconciliation_status") or "").upper() == "FAILED"
        and not bool(summary.get("show_snapshot_performance_when_unreconciled"))
    )
    snapshot_summary_return = "검증 전 참고 불가" if hide_snapshot else _pct(summary.get("actual_return"))
    return "\n".join(
        [
            "## 계좌 성과 vs 지수/ETF",
            *broker_lines,
            *etf_lines,
            "",
            f"- 성과 기준 기간: `{summary.get('start_date') or '-'} ~ {summary.get('end_date') or '-'}` "
            f"(`{summary.get('default_period_label') or summary.get('default_period') or '-'}`)",
            f"- 내부 스냅샷 수익률: `{snapshot_summary_return}` "
            f"({_return_method_label(summary.get('primary_return_method'), summary.get('return_method_warning'))})",
            f"- 최고 초과 기준: `{((summary.get('best_excess') or {}).get('benchmark')) or '-'}` "
            f"({'정합성 검증 후 해석' if hide_snapshot else _pct((summary.get('best_excess') or {}).get('excess_return'))})",
            f"- 최저 초과 기준: `{((summary.get('worst_excess') or {}).get('benchmark')) or '-'}` "
            f"({'정합성 검증 후 해석' if hide_snapshot else _pct((summary.get('worst_excess') or {}).get('excess_return'))})",
            f"- 참고용 초과손익: `{'정합성 검증 후 해석' if hide_snapshot else _krw((summary.get('best_excess') or {}).get('excess_krw'))}`",
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
            "### 정합성 해결 입력",
            "",
            *action_lines,
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
        "settled_cash_krw": _float_or_none(getattr(snapshot, "settled_cash_krw", None)),
        "available_cash_krw": _float_or_none(getattr(snapshot, "available_cash_krw", None)),
        "buying_power_krw": _float_or_none(getattr(snapshot, "buying_power_krw", None)),
        "position_market_value_krw": float(
            sum(_float_or_none(getattr(position, "market_value_krw", None)) or 0.0 for position in snapshot.positions)
        ),
        "snapshot_health": str(getattr(snapshot, "snapshot_health", "") or ""),
        "positions_count": len(getattr(snapshot, "positions", ()) or ()),
        "positions": _snapshot_position_rows(getattr(snapshot, "positions", ()) or ()),
        "broker": str(getattr(snapshot, "broker", "") or ""),
    }


def _snapshot_payload_row(payload: Mapping[str, Any], *, profile_name: str) -> dict[str, Any]:
    value = _float_or_none(payload.get("account_value_krw"))
    if value is None:
        value = _float_or_none(payload.get("total_equity_krw")) or 0.0
    positions = payload.get("positions")
    positions_count = len(positions) if isinstance(positions, list) else _int_or_none(payload.get("positions_count"))
    position_rows = _payload_position_rows(positions if isinstance(positions, list) else [])
    position_market_value = _float_or_none(payload.get("position_market_value_krw"))
    if position_market_value is None:
        position_market_value = sum(_float_or_none(item.get("market_value_krw")) or 0.0 for item in position_rows)
    as_of = str(payload.get("as_of") or payload.get("generated_at") or payload.get("date") or "")
    return {
        "snapshot_id": str(payload.get("snapshot_id") or ""),
        "profile": profile_name,
        "date": as_of[:10],
        "as_of": as_of,
        "account_value_krw": float(value),
        "settled_cash_krw": _float_or_none(payload.get("settled_cash_krw")),
        "available_cash_krw": _float_or_none(payload.get("available_cash_krw")),
        "buying_power_krw": _float_or_none(payload.get("buying_power_krw")),
        "position_market_value_krw": float(position_market_value or 0.0),
        "snapshot_health": str(payload.get("snapshot_health") or ""),
        "positions_count": positions_count,
        "positions": position_rows,
        "broker": str(payload.get("broker") or ""),
    }


def _snapshot_position_rows(positions: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for position in positions or ():
        canonical = str(getattr(position, "canonical_ticker", "") or "").strip().upper()
        if not canonical:
            continue
        rows.append(
            {
                "broker_symbol": str(getattr(position, "broker_symbol", "") or "").strip().upper(),
                "canonical_ticker": canonical,
                "display_name": str(getattr(position, "display_name", "") or canonical),
                "market_value_krw": _float_or_none(getattr(position, "market_value_krw", None)) or 0.0,
                "unrealized_pnl_krw": _float_or_none(getattr(position, "unrealized_pnl_krw", None)) or 0.0,
            }
        )
    return rows


def _payload_position_rows(positions: list[Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for position in positions:
        if not isinstance(position, Mapping):
            continue
        canonical = str(position.get("canonical_ticker") or position.get("ticker") or "").strip().upper()
        if not canonical:
            continue
        broker_symbol = str(position.get("broker_symbol") or position.get("pdno") or canonical).strip().upper()
        rows.append(
            {
                "broker_symbol": broker_symbol,
                "canonical_ticker": canonical,
                "display_name": str(position.get("display_name") or position.get("name") or canonical),
                "market_value_krw": _float_or_none(position.get("market_value_krw")) or 0.0,
                "unrealized_pnl_krw": _float_or_none(position.get("unrealized_pnl_krw")) or 0.0,
            }
        )
    return rows


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
            _extend_kis_ledger_rows(
                raw_rows,
                warnings=warnings,
                endpoint="domestic_period_rights",
                fetch=lambda query_start=query_start, query_end=query_end: client.fetch_domestic_period_rights(
                    account_no=profile.account_no,
                    product_code=profile.product_code,
                    start_date=query_start,
                    end_date=query_end,
                ),
            )
            _extend_kis_ledger_rows(
                raw_rows,
                warnings=warnings,
                endpoint="domestic_cashflow_ledger",
                fetch=lambda query_start=query_start, query_end=query_end: client.fetch_domestic_cashflow_ledger(
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
            "cash_dfrm_dt",
            "rfnd_dt",
            "rqst_dt",
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
    ticker = _first_text(row, ("pdno", "shtn_pdno", "rptt_pdno", "ovrs_pdno", "std_pdno", "prdt_code", "symbol", "ticker"))
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
            "last_alct_amt",
            "last_ftsk_chgs",
            "rdpt_prca",
            "dlay_int_amt",
            "rfnd_amt",
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
    realized = _realized_pnl_krw(row, fx_rate=fx_rate)
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
    broker_performance: BrokerPerformanceSummary | None,
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
            broker_performance=broker_performance,
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
        period_profit = _internal_profit_for_window(
            cashflow_events=cashflow_events,
            start_date=start,
            end_date=end,
            start_value=start_value,
            end_value=end_value,
        )
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
                "investment_pnl_krw": period_profit["investment_pnl_krw"],
                "return_pct": period_profit["return_pct"],
                "deposit_amount_krw": period_profit["deposit_amount_krw"],
                "withdrawal_amount_krw": period_profit["withdrawal_amount_krw"],
                "profit_source": "internal_snapshot",
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


def _build_profit_calendar(
    *,
    settings: Any,
    profile: PortfolioProfile,
    snapshot_rows: list[dict[str, Any]],
    ledger_events: list[LedgerEvent],
    cashflow_events: list[CashflowEvent],
    broker_performance: BrokerPerformanceSummary | None,
    benchmark_prices: Mapping[str, list[dict[str, Any]]],
    end_date: date,
    reconciliation: Mapping[str, Any],
    warnings: list[str],
) -> dict[str, Any]:
    if not bool(getattr(settings, "profit_calendar_enabled", True)):
        return {}
    specs = _profit_calendar_specs(
        settings=settings,
        snapshot_rows=snapshot_rows,
        end_date=end_date,
    )
    all_specs = specs["weekly"] + specs["monthly"] + specs["rolling"]
    period_pairs = [(spec["period_start"], spec["period_end"]) for spec in all_specs]
    broker_by_period = _profit_calendar_broker_summaries(
        settings=settings,
        profile=profile,
        broker_performance=broker_performance,
        periods=period_pairs,
        benchmark_prices=benchmark_prices,
        warnings=warnings,
    )
    reconciliation_failed = str(reconciliation.get("reconciliation_status") or "").upper() == "FAILED"
    weekly = [
        _profit_calendar_bucket(
            spec,
            snapshot_rows=snapshot_rows,
            ledger_events=ledger_events,
            cashflow_events=cashflow_events,
            broker_by_period=broker_by_period,
            reconciliation_failed=reconciliation_failed,
        )
        for spec in specs["weekly"]
    ]
    monthly = [
        _profit_calendar_bucket(
            spec,
            snapshot_rows=snapshot_rows,
            ledger_events=ledger_events,
            cashflow_events=cashflow_events,
            broker_by_period=broker_by_period,
            reconciliation_failed=reconciliation_failed,
        )
        for spec in specs["monthly"]
    ]
    rolling = [
        _profit_calendar_bucket(
            spec,
            snapshot_rows=snapshot_rows,
            ledger_events=ledger_events,
            cashflow_events=cashflow_events,
            broker_by_period=broker_by_period,
            reconciliation_failed=reconciliation_failed,
        )
        for spec in specs["rolling"]
    ]
    return {
        "weekly": weekly,
        "monthly": monthly,
        "rolling": rolling,
        "summary": {
            "current_week": weekly[0] if weekly else {},
            "current_month": monthly[0] if monthly else {},
            "rolling_1w": _first_profit_bucket(rolling, "ROLLING_1W"),
            "rolling_1m": _first_profit_bucket(rolling, "ROLLING_1M"),
        },
    }


def _profit_calendar_specs(
    *,
    settings: Any,
    snapshot_rows: list[dict[str, Any]],
    end_date: date,
) -> dict[str, list[dict[str, Any]]]:
    weekly: list[dict[str, Any]] = []
    monthly: list[dict[str, Any]] = []
    rolling: list[dict[str, Any]] = []
    week_start = end_date - timedelta(days=end_date.weekday())
    week_count = max(1, int(getattr(settings, "profit_calendar_weeks", 8) or 8))
    for offset in range(week_count):
        start = week_start - timedelta(days=7 * offset)
        full_end = start + timedelta(days=6)
        end = min(full_end, end_date)
        weekly.append(
            {
                "period_key": f"WEEK_{start.strftime('%Y%m%d')}",
                "label": "이번 주" if offset == 0 else f"{start.isoformat()} 주",
                "period_start": start,
                "period_end": end,
                "partial": end < full_end,
            }
        )

    month_count = max(1, int(getattr(settings, "profit_calendar_months", 6) or 6))
    current_month = date(end_date.year, end_date.month, 1)
    for offset in range(month_count):
        start = _month_start_offset(current_month, -offset)
        full_end = _month_end(start)
        end = min(full_end, end_date)
        monthly.append(
            {
                "period_key": f"MONTH_{start.strftime('%Y%m')}",
                "label": "이번 달" if offset == 0 else start.strftime("%Y-%m"),
                "period_start": start,
                "period_end": end,
                "partial": end < full_end,
            }
        )

    rolling_periods = tuple(
        getattr(settings, "profit_calendar_rolling_periods", ("1W", "1M", "3M", "6M", "YTD", "1Y", "ALL"))
        or ("1W", "1M", "3M", "6M", "YTD", "1Y", "ALL")
    )
    for raw_name in rolling_periods:
        name = str(raw_name or "").strip().upper()
        if not name:
            continue
        start = _period_start(name, end_date=end_date, snapshot_rows=snapshot_rows)
        rolling.append(
            {
                "period_key": f"ROLLING_{name}",
                "label": _rolling_profit_label(name),
                "period_start": start,
                "period_end": end_date,
                "partial": False,
            }
        )
    return {"weekly": weekly, "monthly": monthly, "rolling": rolling}


def _profit_calendar_broker_summaries(
    *,
    settings: Any,
    profile: PortfolioProfile,
    broker_performance: BrokerPerformanceSummary | None,
    periods: list[tuple[date, date]],
    benchmark_prices: Mapping[str, list[dict[str, Any]]],
    warnings: list[str],
) -> dict[tuple[str, str], BrokerPerformanceSummary]:
    unique_periods = list(dict.fromkeys(periods))
    results = load_broker_performance_baseline_periods(
        getattr(settings, "broker_return_baseline_path", None),
        periods=unique_periods,
        benchmark_prices=benchmark_prices,
        warnings=warnings,
    )
    if broker_performance is not None:
        results[(broker_performance.period_start, broker_performance.period_end)] = broker_performance
    missing_periods = [
        period
        for period in unique_periods
        if (period[0].isoformat(), period[1].isoformat()) not in results
    ]
    if (
        missing_periods
        and bool(getattr(settings, "prefer_broker_reported_performance", True))
        and profile.broker == "kis"
        and str(getattr(profile, "market_scope", "kr") or "kr").strip().lower() != "us"
    ):
        results.update(
            fetch_kis_domestic_broker_performance_periods(
                profile=profile,
                periods=missing_periods,
                benchmark_prices=benchmark_prices,
                warnings=warnings,
            )
        )
    return results


def _profit_calendar_bucket(
    spec: Mapping[str, Any],
    *,
    snapshot_rows: list[dict[str, Any]],
    ledger_events: list[LedgerEvent],
    cashflow_events: list[CashflowEvent],
    broker_by_period: Mapping[tuple[str, str], BrokerPerformanceSummary],
    reconciliation_failed: bool,
) -> dict[str, Any]:
    requested_start = spec["period_start"]
    requested_end = spec["period_end"]
    key = (requested_start.isoformat(), requested_end.isoformat())
    broker = broker_by_period.get(key)
    if broker is not None and broker.investment_pnl_krw is not None:
        warnings = list(broker.warnings)
        return {
            "period_key": spec.get("period_key"),
            "label": spec.get("label"),
            "period_start": requested_start.isoformat(),
            "period_end": requested_end.isoformat(),
            "investment_pnl_krw": broker.investment_pnl_krw,
            "return_pct": broker.balance_return_pct,
            "start_asset_krw": broker.start_asset_krw,
            "end_asset_krw": broker.end_asset_krw,
            "deposit_amount_krw": broker.deposit_amount_krw,
            "withdrawal_amount_krw": broker.withdrawal_amount_krw,
            "source": "broker_reported",
            "trust_state": "trusted" if not warnings else "broker_reported_with_warning",
            "display_eligible": True,
            "partial": bool(spec.get("partial")),
            "warnings": warnings,
        }

    start_snapshot = _first_snapshot_on_or_after(snapshot_rows, requested_start)
    end_snapshot = _last_snapshot_on_or_before(snapshot_rows, requested_end)
    if not start_snapshot or not end_snapshot or str(start_snapshot.get("date") or "") >= str(end_snapshot.get("date") or ""):
        return _unavailable_profit_bucket(spec, warning="snapshot_history_insufficient")
    start_date = _parse_date(str(start_snapshot.get("date") or "")) or requested_start
    end_date = _parse_date(str(end_snapshot.get("date") or "")) or requested_end
    start_value = _float_or_none(start_snapshot.get("account_value_krw"))
    end_value = _float_or_none(end_snapshot.get("account_value_krw"))
    if start_value is None or end_value is None or start_value <= 0:
        return _unavailable_profit_bucket(spec, warning="invalid_snapshot_value")

    profit = _internal_profit_for_window(
        cashflow_events=cashflow_events,
        start_date=start_date,
        end_date=end_date,
        start_value=start_value,
        end_value=end_value,
    )
    bucket_warnings: list[str] = []
    if broker is None:
        bucket_warnings.append("broker_reported_unavailable")
    else:
        bucket_warnings.extend(broker.warnings or ["broker_reported_investment_pnl_unavailable"])
    if start_date > requested_start or end_date < requested_end or bool(spec.get("partial")):
        bucket_warnings.append("partial_snapshot_coverage")
    if _has_unknown_material_ledger_events(ledger_events, start_date=start_date, end_date=end_date):
        bucket_warnings.append("cashflow_adjustment_unavailable")
    trust_state = "trusted"
    display_eligible = True
    if reconciliation_failed:
        trust_state = "unreconciled_reference"
        display_eligible = False
        bucket_warnings.append("snapshot_reconciliation_failed")
    elif "cashflow_adjustment_unavailable" in bucket_warnings:
        trust_state = "cashflow_unadjusted_reference"
        display_eligible = False
    elif "partial_snapshot_coverage" in bucket_warnings:
        trust_state = "partial_reference"
    return {
        "period_key": spec.get("period_key"),
        "label": spec.get("label"),
        "period_start": requested_start.isoformat(),
        "period_end": requested_end.isoformat(),
        "actual_start_date": start_date.isoformat(),
        "actual_end_date": end_date.isoformat(),
        "investment_pnl_krw": profit["investment_pnl_krw"],
        "return_pct": profit["return_pct"],
        "start_asset_krw": int(round(start_value)),
        "end_asset_krw": int(round(end_value)),
        "deposit_amount_krw": profit["deposit_amount_krw"],
        "withdrawal_amount_krw": profit["withdrawal_amount_krw"],
        "source": "internal_snapshot",
        "trust_state": trust_state,
        "display_eligible": display_eligible,
        "partial": bool(spec.get("partial")) or start_date > requested_start or end_date < requested_end,
        "warnings": list(dict.fromkeys(bucket_warnings)),
    }


def _internal_profit_for_window(
    *,
    cashflow_events: list[CashflowEvent],
    start_date: date,
    end_date: date,
    start_value: float,
    end_value: float,
) -> dict[str, Any]:
    capital_flows = _cashflows_between(
        cashflow_events,
        start_date=start_date,
        end_date=end_date,
        capital_only=True,
    )
    deposits = sum(max(float(event.amount_krw), 0.0) for event in capital_flows)
    withdrawals = sum(abs(min(float(event.amount_krw), 0.0)) for event in capital_flows)
    investment_pnl = float(end_value) - float(start_value) - deposits + withdrawals
    principal = float(start_value) + deposits - withdrawals
    return {
        "investment_pnl_krw": int(round(investment_pnl)),
        "return_pct": _round_or_none(investment_pnl / principal * 100.0 if principal > 0 else None),
        "deposit_amount_krw": int(round(deposits)),
        "withdrawal_amount_krw": int(round(withdrawals)),
        "investment_principal_krw": int(round(principal)) if principal > 0 else None,
    }


def _unavailable_profit_bucket(spec: Mapping[str, Any], *, warning: str) -> dict[str, Any]:
    return {
        "period_key": spec.get("period_key"),
        "label": spec.get("label"),
        "period_start": spec["period_start"].isoformat(),
        "period_end": spec["period_end"].isoformat(),
        "investment_pnl_krw": None,
        "return_pct": None,
        "start_asset_krw": None,
        "end_asset_krw": None,
        "deposit_amount_krw": None,
        "withdrawal_amount_krw": None,
        "source": "unavailable",
        "trust_state": "unavailable",
        "display_eligible": False,
        "partial": bool(spec.get("partial")),
        "warnings": [warning],
    }


def _first_profit_bucket(buckets: list[dict[str, Any]], period_key: str) -> dict[str, Any]:
    return next((bucket for bucket in buckets if bucket.get("period_key") == period_key), {})


def _month_start_offset(month_start: date, offset_months: int) -> date:
    month_index = month_start.year * 12 + month_start.month - 1 + offset_months
    year = month_index // 12
    month = month_index % 12 + 1
    return date(year, month, 1)


def _month_end(month_start: date) -> date:
    return _month_start_offset(month_start, 1) - timedelta(days=1)


def _rolling_profit_label(period_name: str) -> str:
    labels = {
        "1W": "최근 1주",
        "1M": "최근 1개월",
        "3M": "최근 3개월",
        "6M": "최근 6개월",
        "YTD": "연초 이후",
        "1Y": "최근 1년",
        "ALL": "사용 가능 전체 기간",
    }
    return labels.get(period_name, period_name)


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
    if warning_text in {"cashflow_adjustment_unavailable", "broker_external_cashflow_unmodeled"} or method_text == "simple_nav_unadjusted":
        return "현금흐름 미보정 단순 NAV 기준"
    if method_text == "available_history_simple_nav":
        return "사용 가능 기간 단순 NAV 기준"
    if method_text == "insufficient_history":
        return "기간 데이터 부족"
    return "단순 NAV 기준"


def _reconciliation_status_label(value: Any) -> str:
    status = str(value or "UNAVAILABLE").strip().upper()
    return {
        "OK": "정합성 확인",
        "WARNING": "정합성 경고",
        "FAILED": "정합성 실패",
        "UNAVAILABLE": "정합성 미확인",
    }.get(status, "정합성 미확인")


def _etf_status_label(value: Any) -> str:
    status = str(value or "").strip().lower()
    if status == "ok":
        return "계산 완료"
    if status == "actual_performance_unavailable":
        return "실제 성과 검증 전"
    if status == "cashflow_dates_required":
        return "입금일 원장 필요"
    if status == "no_alternatives":
        return "대체 포트폴리오 없음"
    return str(value or "-")


def _actual_source_label(value: Any) -> str:
    source = str(value or "").strip()
    if source == "broker_reported":
        return "한국투자증권 앱 기준"
    if source == "internal_reconciled_snapshot":
        return "내부 스냅샷 정합 기준"
    if source == "unavailable":
        return "검증 전 참고 불가"
    return source or "-"


def _friendly_data_quality_warning(value: Any) -> str:
    text = str(value or "")
    if "etf_alternative_actual_performance_unavailable" in text:
        return "실제 계좌 성과가 검증되지 않아 ETF 대체 비교를 계산하지 않았습니다."
    if "etf_alternative_yfinance_empty" in text or "etf_alternative_price_missing" in text:
        code = text.rsplit(":", 1)[-1] if ":" in text else "ETF"
        return f"{code} 가격 데이터가 비어 해당 ETF 대체 포트폴리오를 계산하지 않았습니다."
    if "account_performance_snapshot_history_insufficient" in text:
        return "계좌 스냅샷 이력이 부족해 기간별 성과를 계산하지 못했습니다."
    if "account_performance_snapshot_excluded:under_min_trade_no_positions" in text:
        return "최소 거래금액 미만이거나 보유가 없는 초기 스냅샷은 성과 기준에서 제외했습니다."
    if "account_performance_snapshot_excluded:watchlist_only" in text:
        return "워치리스트 전용 스냅샷은 계좌 성과 기준에서 제외했습니다."
    if "account_performance_resolution_actions_required" in text:
        return "성과 정합성을 풀기 위한 추가 입력이 필요합니다."
    if "broker_performance_missing_balance_return" in text:
        return "브로커 계좌 전체 수익률 데이터가 없어 앱 기준 NAV 성과는 표시하지 않았습니다."
    if "broker_performance_missing_end_asset" in text:
        return "브로커 기말자산 데이터가 없어 내부 계좌 평가액과 직접 비교하지 못했습니다."
    if "broker_performance_missing_investment_pnl" in text:
        return "브로커 투자손익 데이터가 없어 계좌 전체 손익으로 표시하지 않았습니다."
    if "broker_performance_comparison:broker_period_mismatch" in text:
        return "브로커 성과 기간과 내부 계좌 스냅샷 기간이 달라 비교 해석에 주의가 필요합니다."
    if "account_performance_unreconciled_pnl" in text:
        return "NAV 변화와 보유/실현 손익 기여도 합계가 맞지 않아 수동 정합성 확인이 필요합니다."
    if "account_performance_contribution_not_total_return" in text:
        return "보유/실현 손익 기여도는 총 NAV 수익률 전체를 대체하지 않습니다."
    if "account_performance_contribution_unresolved_ticker" in text:
        code = text.rsplit(":", 1)[-1]
        return f"{code} 종목명을 해석하지 못해 코드로 표시했습니다."
    if "account_performance_duplicate_actual_windows" in text:
        return "일부 요청 기간은 실제 사용 가능 기간이 같아 중복 기간으로 묶었습니다."
    if "account_performance_period_insufficient_history" in text:
        return "요청 기간 시작일의 계좌 스냅샷이 부족해 해당 기간 성과를 별도로 표시하지 않았습니다."
    if "account_performance_period_partial" in text:
        return "요청 기간 전체를 덮지 못하는 부분 기간 산출이 감지됐습니다."
    if "account_performance_cashflow" in text:
        return "입출금 원장이 부족해 현금흐름 보정 성과가 제한됩니다."
    return text


def _contribution_by_ticker(
    *,
    snapshot: AccountSnapshot,
    snapshot_rows: list[dict[str, Any]],
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
    start_positions_by_canonical = _positions_by_canonical_from_snapshot_row(snapshot_rows[0] if snapshot_rows else {})
    for canonical, row in start_positions_by_canonical.items():
        positions_by_canonical.setdefault(canonical, row)
        for candidate in (row.get("canonical_ticker"), row.get("broker_symbol")):
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
    current_positions = {str(position.canonical_ticker or "").strip().upper(): position for position in snapshot.positions if str(position.canonical_ticker or "").strip()}
    tickers = set(current_positions) | set(start_positions_by_canonical) | set(realized)
    rows = []
    for ticker in sorted(tickers):
        position = current_positions.get(ticker)
        start_position = start_positions_by_canonical.get(ticker)
        ending_unrealized = _position_unrealized_pnl(position)
        starting_unrealized = _position_unrealized_pnl(start_position)
        unrealized_change = ending_unrealized - starting_unrealized
        realized_value = float(realized.get(ticker, 0.0))
        display_name = (
            str(getattr(position, "display_name", "") or "").strip()
            or str((start_position or {}).get("display_name") or "").strip()
            or _resolved_display_name(ticker)
        )
        rows.append(
            {
                "ticker": ticker,
                "display_name": display_name,
                "realized_pnl_krw": int(round(realized_value)),
                "starting_unrealized_pnl_krw": int(round(starting_unrealized)),
                "ending_unrealized_pnl_krw": int(round(ending_unrealized)),
                "unrealized_pnl_change_krw": int(round(unrealized_change)),
                "unrealized_pnl_krw": int(round(unrealized_change)),
                "total_contribution_krw": int(round(realized_value + unrealized_change)),
            }
        )
    rows.sort(key=lambda item: abs(int(item["total_contribution_krw"])), reverse=True)
    return rows


def _resolved_display_name(ticker: Any) -> str:
    normalized = str(ticker or "").strip()
    if not normalized:
        return "-"
    try:
        return resolve_instrument(normalized).display_name or normalized
    except Exception:
        return normalized


def _positions_by_canonical_from_snapshot_row(row: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    positions = row.get("positions") if isinstance(row, Mapping) else []
    result: dict[str, dict[str, Any]] = {}
    if not isinstance(positions, list):
        return result
    for position in positions:
        if not isinstance(position, Mapping):
            continue
        canonical = str(position.get("canonical_ticker") or position.get("ticker") or "").strip().upper()
        if not canonical:
            continue
        result[canonical] = dict(position)
    return result


def _position_unrealized_pnl(position: Any) -> float:
    if position is None:
        return 0.0
    if isinstance(position, Mapping):
        return float(_float_or_none(position.get("unrealized_pnl_krw")) or 0.0)
    return float(_float_or_none(getattr(position, "unrealized_pnl_krw", None)) or 0.0)


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
        try:
            resolved = resolve_instrument(normalized)
            if resolved.display_name and resolved.display_name != normalized:
                return str(resolved.primary_symbol or normalized).strip().upper()
        except Exception:
            pass
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
    broker_performance: BrokerPerformanceSummary | None,
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
    broker_external_flows = _broker_external_flows_overlap(
        broker_performance,
        start_date=start_date,
        end_date=end_date,
    )
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
    if broker_external_flows and not capital_flows:
        return {
            "simple_nav_return": simple_nav_return,
            "twr_return": None,
            "twr_unavailable_reason": "broker_external_cashflow_unmodeled",
            "mwr_return": None,
            "mwr_unavailable_reason": "dated_external_cashflows_incomplete",
            "primary_return": simple_nav_return,
            "primary_return_method": "simple_nav_unadjusted",
            "return_method_warning": "broker_external_cashflow_unmodeled",
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
            "cash_delta_krw": None,
            "position_market_value_delta_krw": None,
            "sum_position_contribution_krw": None,
            "external_cashflow_net_krw": None,
            "fees_taxes_krw": None,
            "explained_change_krw": None,
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
            "cash_delta_krw": None,
            "position_market_value_delta_krw": None,
            "sum_position_contribution_krw": None,
            "external_cashflow_net_krw": None,
            "fees_taxes_krw": None,
            "explained_change_krw": None,
            "unexplained_difference_krw": None,
            "unexplained_difference_pct_of_nav": None,
            "reconciliation_status": "UNAVAILABLE",
            "reconciliation_severity": "unavailable",
        }

    cashflow_events = _cashflow_events_from_ledger(ledger_events)
    start_cash = _cash_value(snapshot_rows[0])
    end_cash = _cash_value(snapshot_rows[-1])
    cash_delta = end_cash - start_cash if start_cash is not None and end_cash is not None else None
    start_position_value = _float_or_none(snapshot_rows[0].get("position_market_value_krw"))
    end_position_value = _float_or_none(snapshot_rows[-1].get("position_market_value_krw"))
    position_market_value_delta = (
        end_position_value - start_position_value
        if start_position_value is not None and end_position_value is not None
        else None
    )
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
    explained_change = None if external_cashflow_net is None else contribution_sum + external_cashflow_net
    unexplained = None if explained_change is None else simple_nav_pnl - explained_change
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
        "cash_delta_krw": int(round(cash_delta)) if cash_delta is not None else None,
        "position_market_value_delta_krw": (
            int(round(position_market_value_delta)) if position_market_value_delta is not None else None
        ),
        "sum_position_contribution_krw": int(round(contribution_sum)),
        "external_cashflow_net_krw": int(round(external_cashflow_net)) if external_cashflow_net is not None else None,
        "fees_taxes_krw": int(round(fees_taxes)),
        "explained_change_krw": int(round(explained_change)) if explained_change is not None else None,
        "unexplained_difference_krw": int(round(unexplained)) if unexplained is not None else None,
        "unexplained_difference_pct_of_nav": round(unexplained_pct, 6) if unexplained_pct is not None else None,
        "reconciliation_status": status,
        "reconciliation_severity": severity,
    }


def _resolution_action_lines(actions: Any) -> list[str]:
    if not isinstance(actions, list) or not actions:
        return ["- 추가 입력 요청 없음"]
    lines: list[str] = []
    for item in actions[:5]:
        if not isinstance(item, Mapping):
            continue
        title = str(item.get("title") or "정합성 보완").strip()
        evidence = str(item.get("evidence") or "").strip()
        required = str(item.get("required_input") or "").strip()
        suggested = str(item.get("suggested_file") or "").strip()
        parts = [title]
        if evidence:
            parts.append(evidence)
        if required:
            parts.append(f"필요 입력: {required}")
        if suggested:
            parts.append(f"권장 위치: {suggested}")
        lines.append("- " + " / ".join(parts))
    return lines or ["- 추가 입력 요청 없음"]


def _cash_value(row: Mapping[str, Any]) -> float | None:
    for key in ("settled_cash_krw", "available_cash_krw", "cash_krw"):
        value = _float_or_none(row.get(key))
        if value is not None:
            return value
    return None


def _reconciliation_with_guidance(
    reconciliation: dict[str, Any],
    *,
    profile: PortfolioProfile,
    broker_performance: BrokerPerformanceSummary | None,
    settings: Any,
    warnings: list[str],
) -> dict[str, Any]:
    result = dict(reconciliation)
    actions: list[dict[str, Any]] = []
    status = str(result.get("reconciliation_status") or "").upper()
    needs_guidance = status in {"FAILED", "WARNING", "UNAVAILABLE"}
    unexplained = _float_or_none(result.get("unexplained_difference_krw"))
    if status in {"FAILED", "WARNING"} and unexplained is not None:
        actions.append(
            {
                "code": "explain_nav_residual",
                "title": "NAV 미해명 차이 분해",
                "evidence": (
                    f"NAV 변화 {_krw(result.get('simple_nav_pnl_krw'))} 중 "
                    f"{_krw(result.get('explained_change_krw'))}만 종목 기여도와 외부 현금흐름으로 설명됩니다. "
                    f"잔차는 {_krw(result.get('unexplained_difference_krw'))}입니다."
                ),
                "required_input": "일자별 계좌 평가액, 현금 잔고, 보유 평가액, 입출금/배당/이자/수수료 원장",
                "suggested_file": "KIS 자동 수집 원장 및 내부 스냅샷",
            }
        )
        if result.get("cash_delta_krw") is not None or result.get("position_market_value_delta_krw") is not None:
            actions.append(
                {
                    "code": "check_cash_and_position_delta",
                    "title": "현금/보유 평가액 변화 확인",
                    "evidence": (
                        f"현금 변화 {_krw(result.get('cash_delta_krw'))}, "
                        f"보유 평가액 변화 {_krw(result.get('position_market_value_delta_krw'))}입니다. "
                        "이 값은 진단용이며 수익률로 바로 승격하지 않습니다."
                    ),
                    "required_input": "시작/종료 스냅샷의 현금 잔고와 보유 평가액을 같은 기준으로 보존",
                    "suggested_file": "portfolio-private/account_snapshot.json",
                }
            )
    if needs_guidance and (broker_performance is None or broker_performance.balance_return_pct is None):
        actions.append(
            {
                "code": "provide_broker_nav_performance",
                "title": "브로커 NAV 성과 확보",
                "evidence": "KIS 기간매매손익은 매매손익 진단으로만 사용되며 계좌 전체 NAV 수익률이 아닙니다.",
                "required_input": "period_start, period_end, start_asset_krw, end_asset_krw, deposit_amount_krw, withdrawal_amount_krw, balance_return_pct",
                "suggested_file": "broker_return_baseline_path",
            }
        )
    cashflow_path = getattr(settings, "cashflow_baseline_path", None)
    if needs_guidance and not cashflow_path:
        evidence = "ETF DCA 비교는 입금일/출금일을 임의 합성하지 않습니다."
        required = "date,type,amount_krw 형식의 외부 입출금 원장"
        suggested = "config/account_cashflows.csv"
        if str(getattr(profile, "broker", "") or "").lower() == "kis":
            evidence = (
                "KIS 국내주식 공식 주문/계좌 샘플에서 잔고, 체결, 기간손익, 기간별 계좌권리는 자동 조회할 수 있지만 "
                "일반 계좌의 날짜별 외부 입금/출금 원장 조회 엔드포인트는 확인되지 않습니다."
            )
            required = "브로커가 제공하는 날짜별 외부 입출금 API 또는 내보내기 원장"
            suggested = "KIS API 원천 미제공: CSV/JSON은 선택적 fallback"
        actions.append(
            {
                "code": (
                    "kis_cashflow_api_gap"
                    if str(getattr(profile, "broker", "") or "").lower() == "kis"
                    else "provide_dated_cashflows"
                ),
                "title": "날짜별 입출금 원장 자동화 상태",
                "evidence": evidence,
                "required_input": required,
                "suggested_file": suggested,
            }
        )
    result["resolution_actions"] = actions
    if actions and "account_performance_resolution_actions_required" not in warnings:
        warnings.append("account_performance_resolution_actions_required")
    return result


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


def _summary_with_snapshot_display_policy(summary: dict[str, Any], *, settings: Any) -> dict[str, Any]:
    if not summary:
        return summary
    result = dict(summary)
    result["show_snapshot_performance_when_unreconciled"] = bool(
        getattr(settings, "show_snapshot_performance_when_unreconciled", False)
    )
    return result


def _summary_with_broker_comparison(
    summary: dict[str, Any],
    comparison: BrokerPerformanceComparison | None,
) -> dict[str, Any]:
    if not summary or comparison is None:
        return summary
    if comparison.comparison_status != "FAILED":
        return summary
    result = dict(summary)
    result.update(
        {
            "performance_confidence": "low",
            "performance_confidence_reason": "broker_reported_performance_mismatch",
            "hide_excess_headline": True,
            "requires_manual_reconciliation": True,
            "broker_comparison_status": comparison.comparison_status,
        }
    )
    return result


def _periods_with_display_policy(periods: list[dict[str, Any]], *, summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    hide_unreconciled_snapshot = bool(summary.get("hide_excess_headline")) and not bool(
        summary.get("show_snapshot_performance_when_unreconciled")
    )
    result: list[dict[str, Any]] = []
    for period in periods:
        if not isinstance(period, dict):
            result.append(period)
            continue
        row = dict(period)
        if _float_or_none(row.get("actual_return")) is None:
            row.setdefault("display_eligible", False)
            row.setdefault("trust_state", str(row.get("status") or row.get("primary_return_method") or "unavailable"))
        elif hide_unreconciled_snapshot:
            row["display_eligible"] = False
            row["trust_state"] = "unreconciled_reference"
            row["display_reason"] = "snapshot_reconciliation_failed"
        else:
            row.setdefault("display_eligible", True)
            row.setdefault("trust_state", "trusted")
        result.append(row)
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
    if normalized == "1W":
        return end_date - timedelta(days=7)
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


def _broker_period_window(
    *,
    settings: Any,
    snapshot_rows: list[dict[str, Any]],
    end_date: date,
) -> tuple[date, date]:
    configured_end = _parse_date(str(getattr(settings, "broker_period_end", "") or "")) or end_date
    configured_start = _parse_date(str(getattr(settings, "broker_period_start", "") or ""))
    if configured_start is None:
        configured_start = _period_start("1M", end_date=configured_end, snapshot_rows=snapshot_rows)
    if configured_start > configured_end:
        configured_start = configured_end
    return configured_start, configured_end


def _load_broker_performance(
    *,
    profile: PortfolioProfile,
    settings: Any,
    market_scope: str,
    period_start: date,
    period_end: date,
    benchmark_prices: Mapping[str, list[dict[str, Any]]],
    warnings: list[str],
) -> BrokerPerformanceSummary | None:
    baseline = load_broker_performance_baseline(
        getattr(settings, "broker_return_baseline_path", None),
        period_start=period_start,
        period_end=period_end,
        benchmark_prices=benchmark_prices,
        warnings=warnings,
    )
    if baseline is not None:
        warnings.extend(f"broker_performance:{item}" for item in baseline.warnings)
        return baseline
    if not bool(getattr(settings, "prefer_broker_reported_performance", True)):
        return None
    if profile.broker != "kis" or market_scope != "kr":
        return None
    broker = fetch_kis_domestic_broker_performance(
        profile=profile,
        period_start=period_start,
        period_end=period_end,
        benchmark_prices=benchmark_prices,
        warnings=warnings,
    )
    if broker is not None:
        warnings.extend(f"broker_performance:{item}" for item in broker.warnings)
    return broker


def _broker_performance_comparison(
    *,
    broker_performance: BrokerPerformanceSummary | None,
    snapshot: AccountSnapshot,
    summary: Mapping[str, Any],
    market_scope: str,
    warnings: list[str],
) -> BrokerPerformanceComparison | None:
    if broker_performance is None:
        return None
    broker_end = broker_performance.end_asset_krw
    ta_value = int(snapshot.account_value_krw)
    end_delta = ta_value - broker_end if broker_end is not None else None
    end_delta_pct = (end_delta / broker_end * 100.0) if end_delta is not None and broker_end else None
    ta_return_pct = (
        float(summary.get("simple_nav_return")) * 100.0
        if _float_or_none(summary.get("simple_nav_return")) is not None
        else (
            float(summary.get("actual_return")) * 100.0
            if _float_or_none(summary.get("actual_return")) is not None
            else None
        )
    )
    broker_return_pct = broker_performance.balance_return_pct
    return_delta = ta_return_pct - broker_return_pct if ta_return_pct is not None and broker_return_pct is not None else None

    summary_start = str(summary.get("start_date") or "")
    summary_end = str(summary.get("end_date") or "")
    period_match = (
        "MATCH"
        if summary_start == broker_performance.period_start and summary_end == broker_performance.period_end
        else "MISMATCH"
    )
    scope_text = broker_performance.account_scope.upper()
    scope_match = "MATCH" if market_scope.upper() in scope_text or ("KR" in scope_text and market_scope == "kr") else "UNKNOWN"

    comparison_warnings: list[str] = []
    status = "OK"
    if end_delta_pct is not None and abs(end_delta_pct) > 5.0:
        comparison_warnings.append("broker_end_asset_differs_from_tradingagents_account_value")
        status = "FAILED"
    elif end_delta_pct is not None and abs(end_delta_pct) > 2.0:
        comparison_warnings.append("broker_end_asset_warning")
        status = "WARNING"
    if return_delta is not None and abs(return_delta) > 5.0:
        comparison_warnings.append("broker_return_differs_from_snapshot_return")
        status = "FAILED"
    elif status == "OK" and return_delta is not None and abs(return_delta) > 1.0:
        comparison_warnings.append("broker_return_warning")
        status = "WARNING"
    if period_match != "MATCH":
        comparison_warnings.append("broker_period_mismatch")
        if status == "OK":
            status = "WARNING"
    warnings.extend(f"broker_performance_comparison:{item}" for item in comparison_warnings)
    return BrokerPerformanceComparison(
        broker_end_asset_krw=broker_end,
        tradingagents_account_value_krw=ta_value,
        end_asset_delta_krw=int(round(end_delta)) if end_delta is not None else None,
        end_asset_delta_pct=_round_or_none(end_delta_pct),
        broker_balance_return_pct=_round_or_none(broker_return_pct),
        tradingagents_simple_nav_return_pct=_round_or_none(ta_return_pct),
        return_delta_pct=_round_or_none(return_delta),
        period_match_status=period_match,
        scope_match_status=scope_match,
        comparison_status=status,
        warnings=comparison_warnings,
    )


def _broker_external_flows_overlap(
    broker_performance: BrokerPerformanceSummary | None,
    *,
    start_date: date,
    end_date: date,
) -> bool:
    if broker_performance is None or broker_performance.external_capital_flow_count <= 0:
        return False
    broker_start = _parse_date(broker_performance.period_start)
    broker_end = _parse_date(broker_performance.period_end)
    if broker_start is None or broker_end is None:
        return True
    return broker_start <= end_date and broker_end >= start_date


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
        "profit_calendar",
        "broker_performance",
        "broker_performance_comparison",
        "etf_alternative_comparison",
        "costs",
        "contribution_by_ticker",
        "reconciliation",
        "data_quality",
        "public_sanitization",
    }
    public = {key: value for key, value in payload.items() if key in allowed}
    broker = public.get("broker_performance")
    if isinstance(broker, Mapping):
        public["broker_performance"] = {
            key: value
            for key, value in broker.items()
            if key != "raw_summary"
        }
    return public


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
    if _first_float(row, ("dlay_int_amt",)) not in (None, 0):
        return LedgerEventType.INTEREST
    if _first_float(row, ("last_alct_amt", "last_ftsk_chgs", "rdpt_prca")) not in (None, 0) and _first_text(
        row, ("cash_dfrm_dt", "rght_type_cd", "rght_cblc_type_cd")
    ):
        return LedgerEventType.DIVIDEND
    if _first_float(row, ("interest_krw", "int_amt", "interest_amount")) is not None:
        return LedgerEventType.INTEREST
    if _first_float(row, ("tax_amt", "tax", "transaction_tax")) not in (None, 0):
        return LedgerEventType.TAX
    if _first_float(row, ("fee_amt", "fee", "cmsn_amt", "commission")) not in (None, 0):
        return LedgerEventType.FEE
    return LedgerEventType.UNKNOWN


def _realized_pnl_krw(row: Mapping[str, Any], *, fx_rate: float | None) -> float | None:
    key, value = _first_float_with_key(
        row,
        (
            "rlzt_pfls",
            "rlzt_pfls_amt",
            "trad_pfls_amt",
            "evlu_pfls_smtl_amt",
            "ovrs_rlzt_pfls_amt",
            "realized_pnl",
            "realized_pnl_krw",
            "frcr_rlzt_pfls_amt",
            "frcr_realized_pnl",
            "realized_pnl_usd",
        ),
    )
    if value is None:
        return None
    normalized_key = str(key or "").lower()
    if "frcr" in normalized_key or normalized_key.endswith("_usd"):
        return _to_krw(value, fx_rate=fx_rate)
    return float(value)


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


def _first_float_with_key(payload: Mapping[str, Any], keys: tuple[str, ...]) -> tuple[str | None, float | None]:
    for key in keys:
        value = _float_or_none(payload.get(key))
        if value is not None:
            return key, value
    return None, None


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


def _pct_points(value: Any) -> str:
    number = _float_or_none(value)
    if number is None:
        return "-"
    return f"{number:.2f}%"


def _krw(value: Any) -> str:
    number = _float_or_none(value)
    if number is None:
        return "-"
    return f"{int(round(number)):,} KRW"
