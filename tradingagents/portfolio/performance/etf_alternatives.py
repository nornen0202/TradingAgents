from __future__ import annotations

import csv
import json
import math
from dataclasses import asdict, dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Mapping

from tradingagents.portfolio.account_models import AccountSnapshot, Position
from tradingagents.portfolio.performance.broker_models import BrokerPerformanceSummary


_DEFAULT_INSTRUMENTS: dict[str, dict[str, str]] = {
    "KOSPI200": {"symbol": "069500.KS", "currency": "KRW", "label": "KOSPI200 ETF"},
    "KOSDAQ150": {"symbol": "229200.KS", "currency": "KRW", "label": "KOSDAQ150 ETF"},
    "SP500_KRW": {"symbol": "360750.KS", "currency": "KRW", "label": "S&P500 KRW ETF"},
    "NASDAQ100_KRW": {"symbol": "133690.KS", "currency": "KRW", "label": "Nasdaq100 KRW ETF"},
    "SP500": {"symbol": "SPY", "currency": "USD", "label": "S&P500 US ETF"},
    "NASDAQ100": {"symbol": "QQQ", "currency": "USD", "label": "Nasdaq100 US ETF"},
}
_DEFAULT_PORTFOLIOS: dict[str, dict[str, float]] = {
    "KOSPI200_100": {"KOSPI200": 1.0},
    "KOSDAQ150_100": {"KOSDAQ150": 1.0},
    "SP500_100": {"SP500_KRW": 1.0},
    "NASDAQ100_100": {"NASDAQ100_KRW": 1.0},
    "BLENDED": {"KOSPI200": 0.35, "KOSDAQ150": 0.15, "SP500_KRW": 0.30, "NASDAQ100_KRW": 0.20},
}
_BUY_ACTIONS = {"ADD_NOW", "ADD_IF_TRIGGERED", "STARTER_NOW", "STARTER_IF_TRIGGERED"}


@dataclass(frozen=True)
class ExternalCapitalFlow:
    date: str
    amount_krw: int
    flow_type: str
    source: str = "baseline"
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def signed_amount_krw(self) -> int:
        flow = self.flow_type.lower()
        if flow in {"withdrawal", "fee", "tax", "fx_conversion_out"}:
            return -abs(int(self.amount_krw))
        return abs(int(self.amount_krw))

    def to_dict(self, *, include_raw: bool = True) -> dict[str, Any]:
        payload = asdict(self)
        if not include_raw:
            payload.pop("raw", None)
        return payload


@dataclass(frozen=True)
class EtfAlternativeInstrument:
    key: str
    symbol: str
    currency: str
    label: str
    price_series_status: str = "missing"
    price_basis: str = "unknown"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EtfAlternativePortfolioResult:
    key: str
    label: str
    weights: dict[str, float]
    status: str
    end_value_krw: int | None = None
    investment_pnl_krw: int | None = None
    balance_return_pct: float | None = None
    total_deposit_return_pct: float | None = None
    mdd_pct: float | None = None
    excess_return_pct: float | None = None
    excess_pnl_krw: int | None = None
    transactions: list[dict[str, Any]] = field(default_factory=list)
    equity_curve: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_public_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload.pop("transactions", None)
        return payload


@dataclass(frozen=True)
class EtfAlternativeComparisonSummary:
    status: str
    period_start: str | None
    period_end: str | None
    actual_source: str
    actual: dict[str, Any]
    cashflows: dict[str, Any]
    instruments: list[EtfAlternativeInstrument] = field(default_factory=list)
    alternatives: list[EtfAlternativePortfolioResult] = field(default_factory=list)
    policy: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    raw_cashflows: list[ExternalCapitalFlow] = field(default_factory=list)
    price_diagnostics: dict[str, Any] = field(default_factory=dict)

    def to_public_dict(self) -> dict[str, Any]:
        alternatives = [item.to_public_dict() for item in self.alternatives]
        actual_return_pct = _float_or_none(self.actual.get("balance_return_pct"))
        actual_pnl_krw = _int_or_none(self.actual.get("investment_pnl_krw"))
        actual_final_value_krw = _int_or_none(self.actual.get("end_asset_krw"))
        actual_vs_benchmark = _actual_vs_benchmark_payload(self.alternatives)
        best = _best_result(self.alternatives)
        blended = _result_by_key(self.alternatives, "BLENDED")
        exact_available = self.status == "OK" and str(self.cashflows.get("status") or "").upper() == "OK"
        reason = _comparison_reason(self.status)
        return {
            "status": self.status,
            "reason": reason,
            "message": _comparison_message(self.status),
            "exact_dated_cashflows_available": exact_available,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "actual_source": self.actual_source,
            "period_match_status": self.actual.get("period_match_status"),
            "actual_final_value_krw": actual_final_value_krw,
            "actual_return_pct": actual_return_pct,
            "actual_pnl_krw": actual_pnl_krw,
            "actual": self.actual,
            "cashflows": self.cashflows,
            "cashflow_markers": [
                {"date": item.date, "flow_type": item.flow_type, "source": item.source}
                for item in self.raw_cashflows
            ],
            "instruments": [item.to_dict() for item in self.instruments],
            "alternatives": alternatives,
            "benchmarks": alternatives,
            "best_benchmark_id": best.key if best else None,
            "blended_benchmark_id": blended.key if blended else None,
            "actual_vs_benchmark": actual_vs_benchmark,
            "policy": self.policy,
            "warnings": list(self.warnings),
        }

    def to_raw_dict(self) -> dict[str, Any]:
        payload = self.to_public_dict()
        payload["alternatives"] = [item.to_dict() for item in self.alternatives]
        payload["raw_cashflows"] = [item.to_dict(include_raw=True) for item in self.raw_cashflows]
        payload["price_diagnostics"] = self.price_diagnostics
        return payload


def build_etf_alternative_comparison(
    *,
    snapshot: AccountSnapshot,
    settings: Any,
    summary: Mapping[str, Any],
    periods: list[dict[str, Any]],
    broker_performance: BrokerPerformanceSummary | None,
    reconciliation: Mapping[str, Any],
    warnings: list[str] | None = None,
) -> EtfAlternativeComparisonSummary | None:
    if not bool(getattr(settings, "etf_alternative_enabled", True)):
        return None

    local_warnings: list[str] = []
    actual = _actual_performance(
        summary=summary,
        periods=periods,
        broker_performance=broker_performance,
        reconciliation=reconciliation,
    )
    if not actual:
        local_warnings.append("etf_alternative_actual_performance_unavailable")
        result = EtfAlternativeComparisonSummary(
            status="actual_performance_unavailable",
            period_start=None,
            period_end=None,
            actual_source="unavailable",
            actual={},
            cashflows=_empty_cashflow_summary(source="unavailable"),
            warnings=local_warnings,
            policy=_alpha_policy_unavailable(settings=settings, reason="actual_performance_unavailable"),
        )
        _extend_warnings(warnings, local_warnings)
        return result

    actual_period_start = _parse_date(str(actual.get("period_start") or ""))
    actual_period_end = _parse_date(str(actual.get("period_end") or ""))
    period_start = actual_period_start
    period_end = actual_period_end
    configured_start = _parse_date(str(getattr(settings, "etf_dca_period_start", "") or ""))
    configured_end = _parse_date(str(getattr(settings, "etf_dca_period_end", "") or ""))
    period_match_status = "MATCHED"
    if configured_start and configured_start != actual_period_start:
        local_warnings.append("etf_alternative_period_start_mismatch")
        period_match_status = "MISMATCH"
    if configured_end and configured_end != actual_period_end:
        local_warnings.append("etf_alternative_period_end_mismatch")
        period_match_status = "MISMATCH"
    if configured_start and configured_end and configured_start <= configured_end:
        period_start = configured_start
        period_end = configured_end
    actual["benchmark_period_start"] = period_start.isoformat() if period_start else None
    actual["benchmark_period_end"] = period_end.isoformat() if period_end else None
    actual["period_match_status"] = period_match_status
    if period_start is None or period_end is None or period_start > period_end:
        local_warnings.append("etf_alternative_invalid_period")
        result = EtfAlternativeComparisonSummary(
            status="actual_performance_unavailable",
            period_start=str(actual.get("period_start") or "") or None,
            period_end=str(actual.get("period_end") or "") or None,
            actual_source=str(actual.get("source") or "unavailable"),
            actual=actual,
            cashflows=_empty_cashflow_summary(source="unavailable"),
            warnings=local_warnings,
            policy=_alpha_policy_unavailable(settings=settings, reason="invalid_period"),
        )
        _extend_warnings(warnings, local_warnings)
        return result

    flow_load_warnings: list[str] = []
    all_flows = load_external_capital_flows(
        getattr(settings, "cashflow_baseline_path", None),
        warnings=flow_load_warnings,
    )
    local_warnings.extend(flow_load_warnings)
    flows = [
        flow
        for flow in all_flows
        if (flow_date := _parse_date(flow.date)) is not None and period_start <= flow_date <= period_end
    ]
    broker_deposit = _int_or_none(actual.get("deposit_amount_krw"))
    broker_withdrawal = _int_or_none(actual.get("withdrawal_amount_krw"))
    cashflow_summary, cashflow_status_warnings = _cashflow_summary(
        flows=flows,
        all_flows=all_flows,
        source_path=getattr(settings, "cashflow_baseline_path", None),
        broker_deposit_krw=broker_deposit,
        broker_withdrawal_krw=broker_withdrawal,
    )
    local_warnings.extend(cashflow_status_warnings)
    if cashflow_summary["status"] == "cashflow_dates_required":
        policy = _alpha_policy_unavailable(settings=settings, reason="cashflow_dates_required")
        result = EtfAlternativeComparisonSummary(
            status="cashflow_dates_required",
            period_start=period_start.isoformat(),
            period_end=period_end.isoformat(),
            actual_source=str(actual.get("source") or "unavailable"),
            actual=actual,
            cashflows=cashflow_summary,
            warnings=list(dict.fromkeys(local_warnings)),
            raw_cashflows=flows,
            policy=policy,
        )
        _extend_warnings(warnings, local_warnings)
        return result

    instruments = _instrument_config(settings)
    price_history_path = getattr(settings, "etf_price_history_path", None) or getattr(settings, "price_history_path", None)
    fx_history_path = getattr(settings, "etf_fx_history_path", None)
    price_provider = str(getattr(settings, "price_provider", "yfinance") or "yfinance").strip().lower()
    price_map, price_diagnostics, price_warnings = _load_price_series_for_instruments(
        instruments,
        path=price_history_path,
        provider=price_provider,
        start_date=period_start,
        end_date=period_end,
    )
    fx_map, fx_warnings = _load_fx_series(fx_history_path)
    local_warnings.extend(price_warnings)
    local_warnings.extend(fx_warnings)
    instruments_with_status = [
        EtfAlternativeInstrument(
            key=item.key,
            symbol=item.symbol,
            currency=item.currency,
            label=item.label,
            price_series_status="ok" if item.key in price_map else "missing",
            price_basis=str(price_diagnostics.get(item.key, {}).get("price_basis") or "unknown"),
        )
        for item in instruments
    ]

    portfolios = _portfolio_configs(settings, snapshot=snapshot)
    actual_pnl = _int_or_none(actual.get("investment_pnl_krw")) if period_match_status == "MATCHED" else None
    actual_return_pct = _float_or_none(actual.get("balance_return_pct")) if period_match_status == "MATCHED" else None
    start_asset = float(_int_or_none(actual.get("start_asset_krw")) or 0)
    alternatives = [
        _simulate_portfolio(
            key=key,
            weights=weights,
            instruments={item.key: item for item in instruments_with_status},
            price_map=price_map,
            fx_map=fx_map,
            start_date=period_start,
            end_date=period_end,
            start_asset_krw=start_asset,
            flows=flows,
            include_start_asset=bool(getattr(settings, "etf_alternative_include_start_asset", True)),
            transaction_cost_bps=float(getattr(settings, "etf_alternative_transaction_cost_bps", 0.0) or 0.0),
            min_initial_seed_krw=float(
                getattr(
                    settings,
                    "etf_dca_min_initial_seed_krw",
                    getattr(settings, "min_initial_seed_krw", 10_000),
                )
                or 0.0
            ),
            reinvest_dividends=bool(getattr(settings, "etf_dca_reinvest_dividends", True)),
            actual_investment_pnl_krw=actual_pnl,
            actual_balance_return_pct=actual_return_pct,
        )
        for key, weights in portfolios.items()
    ]
    status = "OK" if any(item.status == "OK" for item in alternatives) else "price_or_fx_unavailable"
    if not alternatives:
        status = "portfolio_config_unavailable"
        local_warnings.append("etf_alternative_portfolio_config_unavailable")

    policy = evaluate_alpha_policy(
        alternatives=alternatives,
        settings=settings,
        period_start=period_start,
        period_end=period_end,
        policy_inputs=getattr(settings, "alpha_policy_inputs", None),
    )
    result = EtfAlternativeComparisonSummary(
        status=status,
        period_start=period_start.isoformat(),
        period_end=period_end.isoformat(),
        actual_source=str(actual.get("source") or "unavailable"),
        actual=actual,
        cashflows=cashflow_summary,
        instruments=instruments_with_status,
        alternatives=alternatives,
        policy=policy,
        warnings=list(dict.fromkeys(local_warnings)),
        raw_cashflows=flows,
        price_diagnostics=price_diagnostics,
    )
    _extend_warnings(warnings, local_warnings)
    return result


def load_external_capital_flows(path: Any, *, warnings: list[str] | None = None) -> list[ExternalCapitalFlow]:
    if not path:
        return []
    candidate = Path(path)
    if not candidate.exists():
        if warnings is not None:
            warnings.append(f"etf_alternative_cashflow_baseline_missing:{candidate}")
        return []
    try:
        if candidate.suffix.lower() == ".csv":
            rows = list(csv.DictReader(candidate.read_text(encoding="utf-8-sig").splitlines()))
        else:
            payload = json.loads(candidate.read_text(encoding="utf-8"))
            if isinstance(payload, Mapping):
                values = (
                    payload.get("cashflows")
                    or payload.get("external_capital_flows")
                    or payload.get("capital_flows")
                    or payload.get("rows")
                    or []
                )
            else:
                values = payload
            rows = values if isinstance(values, list) else []
    except Exception as exc:
        if warnings is not None:
            warnings.append(f"etf_alternative_cashflow_baseline_invalid:{_short_error(exc)}")
        return []

    flows: list[ExternalCapitalFlow] = []
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        flow = _external_flow_from_row(row)
        if flow is not None:
            flows.append(flow)
    return sorted(flows, key=lambda item: item.date)


def evaluate_alpha_policy(
    *,
    alternatives: list[EtfAlternativePortfolioResult],
    settings: Any,
    period_start: date,
    period_end: date,
    policy_inputs: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    policy_inputs = policy_inputs if isinstance(policy_inputs, Mapping) else {}
    decisions: list[str] = []
    checks: dict[str, Any] = {}
    reduce_target = float(getattr(settings, "alpha_policy_reduce_target_pct", 15.0) or 15.0)
    min_samples = int(getattr(settings, "alpha_policy_min_action_samples", 5) or 5)

    monthly = [_float_or_none(item) for item in policy_inputs.get("monthly_blended_excess_return_pct", [])]
    monthly = [item for item in monthly if item is not None]
    last_three = monthly[-3:]
    if len(last_three) == 3:
        passed = all(item < 0 for item in last_three)
        checks["three_month_consecutive_underperformance"] = {
            "status": "FAILED" if passed else "OK",
            "values": [round(item, 6) for item in last_three],
        }
        if passed:
            decisions.append("FREEZE_NEW_INDIVIDUAL_BUYS")
    else:
        checks["three_month_consecutive_underperformance"] = {"status": "INSUFFICIENT_DATA"}

    six_month_excess = _float_or_none(policy_inputs.get("six_month_blended_excess_return_pct"))
    if six_month_excess is None:
        blended = _result_by_key(alternatives, "BLENDED")
        days = (period_end - period_start).days
        if blended and blended.excess_return_pct is not None and 150 <= days <= 220:
            six_month_excess = blended.excess_return_pct
    if six_month_excess is not None:
        checks["six_month_cumulative_excess"] = {
            "status": "FAILED" if six_month_excess < 0 else "OK",
            "excess_return_pct": round(float(six_month_excess), 6),
        }
        if six_month_excess < 0:
            decisions.append(f"REDUCE_INDIVIDUAL_STOCK_TARGET_TO_{int(round(reduce_target))}PCT")
    else:
        checks["six_month_cumulative_excess"] = {"status": "INSUFFICIENT_DATA"}

    twelve = _twelve_month_policy_check(policy_inputs)
    checks["twelve_month_return_mdd_turnover"] = twelve
    if twelve.get("status") == "FAILED":
        decisions.append("ETF_CORE_REQUIRED")

    action_check = _action_policy_check(policy_inputs, min_samples=min_samples)
    checks["action_add_starter_vs_etf"] = action_check
    if action_check.get("status") == "FAILED":
        decisions.append("ACTION_SIGNALS_OBSERVATION_ONLY")

    status = "ACTION_REQUIRED" if decisions else (
        "INSUFFICIENT_DATA" if any(item.get("status") == "INSUFFICIENT_DATA" for item in checks.values()) else "OK"
    )
    core_satellite = _core_satellite_recommendation_payload(
        decisions=list(dict.fromkeys(decisions)),
        status=status,
        reduce_target=reduce_target,
    )
    return {
        "mode": str(getattr(settings, "alpha_policy_mode", "report_only") or "report_only"),
        "status": status,
        "decisions": list(dict.fromkeys(decisions)),
        "checks": checks,
        "core_satellite_recommendation": core_satellite,
    }


def _actual_performance(
    *,
    summary: Mapping[str, Any],
    periods: list[dict[str, Any]],
    broker_performance: BrokerPerformanceSummary | None,
    reconciliation: Mapping[str, Any],
) -> dict[str, Any]:
    if broker_performance and broker_performance.balance_return_pct is not None:
        return {
            "source": "broker_reported",
            "period_start": broker_performance.period_start,
            "period_end": broker_performance.period_end,
            "investment_pnl_krw": broker_performance.investment_pnl_krw,
            "balance_return_pct": broker_performance.balance_return_pct,
            "end_asset_krw": broker_performance.end_asset_krw,
            "start_asset_krw": broker_performance.start_asset_krw,
            "deposit_amount_krw": broker_performance.deposit_amount_krw,
            "withdrawal_amount_krw": broker_performance.withdrawal_amount_krw,
        }
    if str(reconciliation.get("reconciliation_status") or "").upper() == "FAILED":
        return {}
    default = str(summary.get("source_period") or summary.get("default_period") or "")
    period = next((item for item in periods if str(item.get("period") or "") == default), None)
    if period is None and str(summary.get("default_period") or "") == "ALL_AVAILABLE":
        period = next((item for item in periods if str(item.get("period") or "").upper() == "ALL"), None)
    if not isinstance(period, Mapping):
        return {}
    start_value = _int_or_none(period.get("actual_start_value_krw"))
    end_value = _int_or_none(period.get("actual_end_value_krw"))
    actual_return = _float_or_none(period.get("actual_return"))
    if start_value is None or end_value is None or actual_return is None:
        return {}
    investment_pnl = end_value - start_value
    return {
        "source": "internal_reconciled_snapshot",
        "period_start": period.get("start_date"),
        "period_end": period.get("end_date"),
        "investment_pnl_krw": int(investment_pnl),
        "balance_return_pct": round(actual_return * 100.0, 6),
        "end_asset_krw": end_value,
        "start_asset_krw": start_value,
        "deposit_amount_krw": 0,
        "withdrawal_amount_krw": 0,
    }


def _core_satellite_recommendation_payload(
    *,
    decisions: list[str],
    status: str,
    reduce_target: float,
) -> dict[str, Any]:
    confidence = "low" if status == "INSUFFICIENT_DATA" else "medium"
    core_weight = 0.50
    individual_weight = 0.50
    reasons: list[str] = []
    if "ETF_CORE_REQUIRED" in decisions:
        core_weight = 0.90
        individual_weight = 0.10
        confidence = "high"
        reasons.append("12개월 수익률, MDD, 회전율 기준이 모두 혼합 ETF 벤치마크보다 불리합니다.")
    elif any(item.startswith("REDUCE_INDIVIDUAL_STOCK_TARGET_TO_") for item in decisions):
        individual_weight = max(0.0, min(1.0, reduce_target / 100.0))
        core_weight = 1.0 - individual_weight
        reasons.append("6개월 누적 초과수익이 음수입니다.")
    elif "FREEZE_NEW_INDIVIDUAL_BUYS" in decisions:
        core_weight = 0.70
        individual_weight = 0.30
        reasons.append("최근 3개월 연속 혼합 벤치마크를 언더퍼폼했습니다.")
    else:
        reasons.append("정책 전환 판단을 위한 충분한 ETF 우위 신호가 아직 없습니다.")
    if "ACTION_SIGNALS_OBSERVATION_ONLY" in decisions:
        reasons.append("ADD/STARTER 액션 성과가 ETF 대체 계좌 대비 낮습니다.")
    return {
        "recommended_core_etf_weight": round(core_weight, 4),
        "recommended_individual_stock_weight": round(individual_weight, 4),
        "confidence": confidence,
        "reasons": reasons,
        "rules_triggered": decisions,
        "next_review_date": None,
    }


def _external_flow_from_row(row: Mapping[str, Any]) -> ExternalCapitalFlow | None:
    parsed = _parse_date(
        str(
            row.get("date")
            or row.get("event_date")
            or row.get("trade_date")
            or row.get("as_of")
            or row.get("asof")
            or row.get("timestamp")
            or ""
        )
    )
    if parsed is None:
        return None
    flow_type = str(row.get("type") or row.get("cashflow_type") or row.get("flow_type") or row.get("event_type") or "").strip().lower()
    amount = _first_number(row, ("amount_krw", "amount", "amount_local", "cashflow_amount", "amt"))
    if flow_type in {"buy", "sell", "매수", "매도", "trade"}:
        return None
    if not flow_type:
        if _first_number(row, ("deposit_amount_krw", "deposit_krw")):
            flow_type = "deposit"
            amount = _first_number(row, ("deposit_amount_krw", "deposit_krw"))
        elif _first_number(row, ("withdrawal_amount_krw", "withdrawal_krw")):
            flow_type = "withdrawal"
            amount = _first_number(row, ("withdrawal_amount_krw", "withdrawal_krw"))
        else:
            return None
    if amount is None:
        return None
    aliases = {
        "deposit": "deposit",
        "입금": "deposit",
        "in": "deposit",
        "withdrawal": "withdrawal",
        "withdraw": "withdrawal",
        "출금": "withdrawal",
        "out": "withdrawal",
        "dividend": "dividend",
        "배당": "dividend",
        "interest": "interest",
        "이자": "interest",
        "fee": "fee",
        "수수료": "fee",
        "tax": "tax",
        "세금": "tax",
        "fx_conversion_in": "fx_conversion_in",
        "fx_conversion_out": "fx_conversion_out",
    }
    normalized = aliases.get(flow_type.lower())
    if normalized is None:
        return None
    if amount < 0:
        normalized = "withdrawal" if normalized == "deposit" else normalized
    return ExternalCapitalFlow(
        date=parsed.isoformat(),
        amount_krw=int(round(abs(amount))),
        flow_type=normalized,
        source=str(row.get("source") or "baseline"),
        raw={str(key): value for key, value in row.items()},
    )


def _cashflow_summary(
    *,
    flows: list[ExternalCapitalFlow],
    all_flows: list[ExternalCapitalFlow],
    source_path: Any,
    broker_deposit_krw: int | None,
    broker_withdrawal_krw: int | None,
) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    deposit_total = sum(flow.amount_krw for flow in flows if flow.flow_type == "deposit")
    withdrawal_total = sum(flow.amount_krw for flow in flows if flow.flow_type == "withdrawal")
    performance_flow_count = len([flow for flow in flows if flow.flow_type in {"dividend", "interest", "fee", "tax"}])
    source = "baseline" if source_path else "none"
    dated_count = len(flows)
    broker_has_flow = bool((broker_deposit_krw or 0) > 0 or (broker_withdrawal_krw or 0) > 0)
    if broker_has_flow and not dated_count:
        warnings.append("etf_alternative_cashflow_dates_required")
        return (
            {
                "status": "cashflow_dates_required",
                "source": source,
                "dated_flow_count": 0,
                "available_flow_count": len(all_flows),
                "deposit_amount_krw": 0,
                "withdrawal_amount_krw": 0,
                "performance_flow_count": 0,
                "broker_deposit_amount_krw": broker_deposit_krw,
                "broker_withdrawal_amount_krw": broker_withdrawal_krw,
                "missing_reason": "dated_external_capital_flows_required",
            },
            warnings,
        )
    if broker_deposit_krw is not None and abs(deposit_total - broker_deposit_krw) > 1:
        warnings.append("etf_alternative_cashflow_deposit_total_mismatch")
    if broker_withdrawal_krw is not None and abs(withdrawal_total - broker_withdrawal_krw) > 1:
        warnings.append("etf_alternative_cashflow_withdrawal_total_mismatch")
    return (
        {
            "status": "OK",
            "source": source,
            "dated_flow_count": dated_count,
            "available_flow_count": len(all_flows),
            "deposit_amount_krw": int(deposit_total),
            "withdrawal_amount_krw": int(withdrawal_total),
            "performance_flow_count": performance_flow_count,
            "broker_deposit_amount_krw": broker_deposit_krw,
            "broker_withdrawal_amount_krw": broker_withdrawal_krw,
            "missing_reason": None,
        },
        warnings,
    )


def _instrument_config(settings: Any) -> list[EtfAlternativeInstrument]:
    raw = getattr(settings, "etf_alternative_symbols", None)
    symbols = _string_mapping(raw)
    currencies = _string_mapping(getattr(settings, "etf_alternative_currencies", None))
    labels = _string_mapping(getattr(settings, "etf_alternative_labels", None))
    keys = list(_DEFAULT_INSTRUMENTS)
    for key in symbols:
        if key not in keys:
            keys.append(key)
    instruments: list[EtfAlternativeInstrument] = []
    for key in keys:
        default = _DEFAULT_INSTRUMENTS.get(key, {"symbol": "", "currency": "KRW", "label": key})
        instruments.append(
            EtfAlternativeInstrument(
                key=key,
                symbol=str(symbols.get(key, default["symbol"]) or "").strip(),
                currency=str(currencies.get(key, default["currency"]) or "KRW").strip().upper(),
                label=str(labels.get(key, default["label"]) or key).strip(),
            )
        )
    return instruments


def _portfolio_configs(settings: Any, *, snapshot: AccountSnapshot) -> dict[str, dict[str, float]]:
    configured = _nested_float_mapping(getattr(settings, "etf_alternative_portfolios", None))
    portfolios = dict(_DEFAULT_PORTFOLIOS)
    portfolios.update(configured)
    blended = _float_mapping(getattr(settings, "etf_alternative_blended_weights", None))
    if not blended:
        blended = _infer_blended_weights(snapshot)
    if blended:
        portfolios["BLENDED"] = blended
    return {key: _normalize_weights(weights) for key, weights in portfolios.items() if _normalize_weights(weights)}


def _infer_blended_weights(snapshot: AccountSnapshot) -> dict[str, float]:
    bucket_values: dict[str, float] = {}
    positions = tuple(getattr(snapshot, "positions", ()) or ())
    total = sum(max(0.0, float(getattr(position, "market_value_krw", 0) or 0)) for position in positions)
    if total <= 0:
        return {}
    for position in positions:
        value = max(0.0, float(getattr(position, "market_value_krw", 0) or 0))
        if value <= 0:
            continue
        bucket = _position_benchmark_bucket(position)
        bucket_values[bucket] = bucket_values.get(bucket, 0.0) + value
    return _normalize_weights(bucket_values)


def _position_benchmark_bucket(position: Position) -> str:
    ticker = str(getattr(position, "canonical_ticker", "") or getattr(position, "broker_symbol", "") or "").strip().upper()
    sector = str(getattr(position, "sector", "") or "").strip().lower()
    if ticker.endswith(".KQ"):
        return "KOSDAQ150"
    if ticker.endswith(".KS") or (len(ticker) == 6 and ticker.isdigit()):
        return "KOSPI200"
    if any(word in sector for word in ("semi", "software", "tech", "internet", "ai", "반도체", "소프트웨어")):
        return "NASDAQ100"
    if ticker in {"AAPL", "MSFT", "NVDA", "GOOGL", "GOOG", "META", "AMZN", "TSLA", "AVGO"}:
        return "NASDAQ100"
    return "SP500"


def _benchmark_flow_action(flow: ExternalCapitalFlow, *, reinvest_dividends: bool) -> str:
    flow_type = str(flow.flow_type or "").strip().lower()
    if flow_type == "deposit":
        return "buy"
    if flow_type == "withdrawal":
        return "sell"
    if flow_type in {"dividend", "interest", "fx_conversion_in"}:
        return "buy" if reinvest_dividends else "ignore"
    if flow_type in {"fee", "tax", "fx_conversion_out"}:
        return "sell"
    return "ignore"


def _cashflow_id(flow: ExternalCapitalFlow) -> str:
    raw_id = ""
    if isinstance(flow.raw, Mapping):
        raw_id = str(flow.raw.get("event_id") or flow.raw.get("id") or flow.raw.get("transaction_id") or "")
    if raw_id:
        return raw_id
    return f"{flow.date}:{flow.flow_type}:{flow.amount_krw}:{flow.source}"


def _actual_vs_benchmark_payload(alternatives: list[EtfAlternativePortfolioResult]) -> dict[str, dict[str, Any]]:
    payload: dict[str, dict[str, Any]] = {}
    for item in alternatives:
        if item.status != "OK":
            payload[item.key] = {"status": item.status, "warnings": list(item.warnings)}
            continue
        excess = _float_or_none(item.excess_return_pct)
        payload[item.key] = {
            "status": item.status,
            "benchmark_final_value_krw": item.end_value_krw,
            "benchmark_return_pct": item.balance_return_pct,
            "actual_excess_return_pct": item.excess_return_pct,
            "actual_excess_pnl_krw": item.excess_pnl_krw,
            "winner": "actual" if excess is not None and excess >= 0 else "benchmark",
        }
    return payload


def _best_result(alternatives: list[EtfAlternativePortfolioResult]) -> EtfAlternativePortfolioResult | None:
    ok_items = [item for item in alternatives if item.status == "OK" and item.balance_return_pct is not None]
    if not ok_items:
        return None
    return max(ok_items, key=lambda item: float(item.balance_return_pct or -10**9))


def _comparison_reason(status: str) -> str | None:
    normalized = str(status or "").strip()
    if normalized == "cashflow_dates_required":
        return "dated_cashflows_missing"
    if normalized == "actual_performance_unavailable":
        return "actual_performance_unavailable"
    if normalized == "price_or_fx_unavailable":
        return "price_or_fx_unavailable"
    if normalized == "portfolio_config_unavailable":
        return "portfolio_config_unavailable"
    return None


def _comparison_message(status: str) -> str | None:
    normalized = str(status or "").strip()
    if normalized == "cashflow_dates_required":
        return (
            "KIS period summary only provides aggregate deposits. Exact same-deposit-date ETF benchmark "
            "requires dated cashflows. Provide manual cashflow CSV/JSON or enable broker cashflow ledger."
        )
    if normalized == "actual_performance_unavailable":
        return "Actual account performance is unavailable because broker performance is missing and snapshot reconciliation is not trusted."
    if normalized == "price_or_fx_unavailable":
        return "One or more ETF alternatives could not be calculated because price or FX data is missing."
    if normalized == "portfolio_config_unavailable":
        return "No ETF benchmark portfolio definition is available."
    return None


def _simulate_portfolio(
    *,
    key: str,
    weights: dict[str, float],
    instruments: Mapping[str, EtfAlternativeInstrument],
    price_map: Mapping[str, list[dict[str, Any]]],
    fx_map: Mapping[str, list[dict[str, Any]]],
    start_date: date,
    end_date: date,
    start_asset_krw: float,
    flows: list[ExternalCapitalFlow],
    include_start_asset: bool,
    transaction_cost_bps: float,
    min_initial_seed_krw: float,
    reinvest_dividends: bool,
    actual_investment_pnl_krw: int | None,
    actual_balance_return_pct: float | None,
) -> EtfAlternativePortfolioResult:
    warnings: list[str] = []
    label = _portfolio_label(key)
    for instrument_key in weights:
        if instrument_key not in instruments:
            warnings.append(f"etf_alternative_unknown_instrument:{instrument_key}")
        if instrument_key not in price_map:
            warnings.append(f"etf_alternative_price_missing:{instrument_key}")
    if warnings:
        return EtfAlternativePortfolioResult(key=key, label=label, weights=weights, status="price_missing", warnings=warnings)

    cost_factor = max(0.0, 1.0 - max(0.0, transaction_cost_bps) / 10_000.0)
    holdings: dict[str, float] = {instrument_key: 0.0 for instrument_key in weights}
    transactions: list[dict[str, Any]] = []

    seed_invested = bool(include_start_asset and start_asset_krw >= max(0.0, min_initial_seed_krw))
    if include_start_asset and start_asset_krw > 0 and not seed_invested:
        warnings.append("etf_alternative_seed_ignored_below_minimum")
    if seed_invested:
        ok = _buy_weighted(
            holdings=holdings,
            amount_krw=start_asset_krw,
            weights=weights,
            instruments=instruments,
            price_map=price_map,
            fx_map=fx_map,
            trade_date=start_date,
            cost_factor=cost_factor,
            warnings=warnings,
            transactions=transactions,
            portfolio_key=key,
            source_cashflow_id="initial_seed",
            source_flow_type="seed",
        )
        if not ok:
            return _failed_simulation(key=key, label=label, weights=weights, status=_simulation_status_from_warnings(warnings), warnings=warnings)

    for flow in flows:
        flow_date = _parse_date(flow.date)
        if flow_date is None or flow_date < start_date or flow_date > end_date:
            continue
        flow_action = _benchmark_flow_action(flow, reinvest_dividends=reinvest_dividends)
        if flow_action == "buy":
            ok = _buy_weighted(
                holdings=holdings,
                amount_krw=float(flow.amount_krw),
                weights=weights,
                instruments=instruments,
                price_map=price_map,
                fx_map=fx_map,
                trade_date=flow_date,
                cost_factor=cost_factor,
                warnings=warnings,
                transactions=transactions,
                portfolio_key=key,
                source_cashflow_id=_cashflow_id(flow),
                source_flow_type=flow.flow_type,
            )
        elif flow_action == "sell":
            ok = _sell_pro_rata(
                holdings=holdings,
                amount_krw=float(flow.amount_krw),
                instruments=instruments,
                price_map=price_map,
                fx_map=fx_map,
                trade_date=flow_date,
                cost_factor=cost_factor,
                warnings=warnings,
                transactions=transactions,
                portfolio_key=key,
                source_cashflow_id=_cashflow_id(flow),
                source_flow_type=flow.flow_type,
            )
        else:
            ok = True
        if not ok:
            return _failed_simulation(key=key, label=label, weights=weights, status=_simulation_status_from_warnings(warnings), warnings=warnings)

    end_value = _holdings_value_krw(
        holdings=holdings,
        instruments=instruments,
        price_map=price_map,
        fx_map=fx_map,
        valuation_date=end_date,
        price_lookup="before",
        warnings=warnings,
    )
    if end_value is None:
        return _failed_simulation(key=key, label=label, weights=weights, status=_simulation_status_from_warnings(warnings), warnings=warnings)

    equity_curve = _build_equity_curve_from_transactions(
        transactions=transactions,
        instruments=instruments,
        price_map=price_map,
        fx_map=fx_map,
        start_date=start_date,
        end_date=end_date,
    )
    value_curve = [
        float(item["value_krw"])
        for item in equity_curve
        if _float_or_none(item.get("value_krw")) is not None
    ]

    deposit_total = sum(flow.amount_krw for flow in flows if flow.flow_type == "deposit")
    withdrawal_total = sum(flow.amount_krw for flow in flows if flow.flow_type == "withdrawal")
    initial = start_asset_krw if seed_invested else 0.0
    investment_pnl = end_value - initial - float(deposit_total) + float(withdrawal_total)
    principal = initial + float(deposit_total) - float(withdrawal_total)
    deposit_basis = initial + float(deposit_total)
    balance_return_pct = investment_pnl / principal * 100.0 if principal > 0 else None
    total_deposit_return_pct = investment_pnl / deposit_basis * 100.0 if deposit_basis > 0 else None
    excess_return_pct = (
        actual_balance_return_pct - balance_return_pct
        if actual_balance_return_pct is not None and balance_return_pct is not None
        else None
    )
    excess_pnl = actual_investment_pnl_krw - investment_pnl if actual_investment_pnl_krw is not None else None
    return EtfAlternativePortfolioResult(
        key=key,
        label=label,
        weights=weights,
        status="OK",
        end_value_krw=int(round(end_value)),
        investment_pnl_krw=int(round(investment_pnl)),
        balance_return_pct=_round_or_none(balance_return_pct),
        total_deposit_return_pct=_round_or_none(total_deposit_return_pct),
        mdd_pct=_round_or_none((_max_drawdown(value_curve) or 0.0) * 100.0 if value_curve else None),
        excess_return_pct=_round_or_none(excess_return_pct),
        excess_pnl_krw=int(round(excess_pnl)) if excess_pnl is not None else None,
        transactions=transactions,
        equity_curve=equity_curve,
        warnings=list(dict.fromkeys(warnings)),
    )


def _buy_weighted(
    *,
    holdings: dict[str, float],
    amount_krw: float,
    weights: Mapping[str, float],
    instruments: Mapping[str, EtfAlternativeInstrument],
    price_map: Mapping[str, list[dict[str, Any]]],
    fx_map: Mapping[str, list[dict[str, Any]]],
    trade_date: date,
    cost_factor: float,
    warnings: list[str],
    transactions: list[dict[str, Any]] | None = None,
    portfolio_key: str | None = None,
    source_cashflow_id: str | None = None,
    source_flow_type: str | None = None,
) -> bool:
    if amount_krw <= 0:
        return True
    for key, weight in weights.items():
        instrument = instruments.get(key)
        rows = price_map.get(key)
        if instrument is None or not rows:
            warnings.append(f"etf_alternative_price_missing:{key}")
            return False
        price_row = _price_row_on_or_after(rows, trade_date)
        actual_trade_date = _parse_date(str(price_row.get("date") or "")) if price_row else None
        price = _float_or_none(price_row.get("close")) if price_row else None
        fx = _fx_rate_for_currency(instrument.currency, fx_map, actual_trade_date or trade_date, lookup="after")
        if price is None or price <= 0:
            warnings.append(f"etf_alternative_trade_price_missing:{key}:{trade_date.isoformat()}")
            return False
        if fx is None or fx <= 0:
            warnings.append(f"etf_alternative_fx_missing:{instrument.currency}:{trade_date.isoformat()}")
            return False
        allocation_krw = amount_krw * float(weight) * cost_factor
        local_amount = allocation_krw / fx
        shares = local_amount / price
        holdings[key] = holdings.get(key, 0.0) + shares
        if transactions is not None:
            transactions.append(
                {
                    "portfolio_key": portfolio_key,
                    "instrument_key": key,
                    "symbol": instrument.symbol,
                    "trade_date": (actual_trade_date or trade_date).isoformat(),
                    "requested_date": trade_date.isoformat(),
                    "side": "BUY",
                    "amount_krw": int(round(allocation_krw)),
                    "price": round(float(price), 8),
                    "fx_rate": round(float(fx), 8),
                    "shares": round(float(shares), 12),
                    "source_cashflow_id": source_cashflow_id,
                    "source_flow_type": source_flow_type,
                }
            )
    return True


def _sell_pro_rata(
    *,
    holdings: dict[str, float],
    amount_krw: float,
    instruments: Mapping[str, EtfAlternativeInstrument],
    price_map: Mapping[str, list[dict[str, Any]]],
    fx_map: Mapping[str, list[dict[str, Any]]],
    trade_date: date,
    cost_factor: float,
    warnings: list[str],
    transactions: list[dict[str, Any]] | None = None,
    portfolio_key: str | None = None,
    source_cashflow_id: str | None = None,
    source_flow_type: str | None = None,
) -> bool:
    if amount_krw <= 0:
        return True
    current_value = _holdings_value_krw(
        holdings=holdings,
        instruments=instruments,
        price_map=price_map,
        fx_map=fx_map,
        valuation_date=trade_date,
        price_lookup="after",
        warnings=warnings,
    )
    if current_value is None:
        return False
    effective_value = current_value * max(cost_factor, 0.000001)
    if effective_value <= 0:
        warnings.append("etf_alternative_withdrawal_no_holdings")
        return False
    sell_ratio = min(1.0, amount_krw / effective_value)
    if sell_ratio >= 1.0 and amount_krw > effective_value:
        warnings.append("etf_alternative_withdrawal_exceeds_portfolio_value")
    for key in list(holdings):
        shares_before = holdings.get(key, 0.0)
        shares_sold = shares_before * sell_ratio
        holdings[key] = max(0.0, shares_before - shares_sold)
        if transactions is not None and shares_sold > 0:
            instrument = instruments.get(key)
            rows = price_map.get(key) or []
            price_row = _price_row_on_or_after(rows, trade_date)
            actual_trade_date = _parse_date(str(price_row.get("date") or "")) if price_row else None
            price = _float_or_none(price_row.get("close")) if price_row else None
            fx = _fx_rate_for_currency(
                instrument.currency if instrument else "KRW",
                fx_map,
                actual_trade_date or trade_date,
                lookup="after",
            )
            if instrument is not None and price is not None and fx is not None:
                transactions.append(
                    {
                        "portfolio_key": portfolio_key,
                        "instrument_key": key,
                        "symbol": instrument.symbol,
                        "trade_date": (actual_trade_date or trade_date).isoformat(),
                        "requested_date": trade_date.isoformat(),
                        "side": "SELL",
                        "amount_krw": int(round(shares_sold * price * fx * cost_factor)),
                        "price": round(float(price), 8),
                        "fx_rate": round(float(fx), 8),
                        "shares": round(float(shares_sold), 12),
                        "source_cashflow_id": source_cashflow_id,
                        "source_flow_type": source_flow_type,
                    }
                )
    return True


def _build_equity_curve_from_transactions(
    *,
    transactions: list[dict[str, Any]],
    instruments: Mapping[str, EtfAlternativeInstrument],
    price_map: Mapping[str, list[dict[str, Any]]],
    fx_map: Mapping[str, list[dict[str, Any]]],
    start_date: date,
    end_date: date,
) -> list[dict[str, Any]]:
    holdings: dict[str, float] = {key: 0.0 for key in instruments}
    pending = sorted(
        transactions,
        key=lambda item: (
            str(item.get("trade_date") or ""),
            0 if str(item.get("side") or "").upper() == "BUY" else 1,
        ),
    )
    dates = set(_valuation_dates(price_map, start_date=start_date, end_date=end_date))
    for transaction in pending:
        parsed = _parse_date(str(transaction.get("trade_date") or ""))
        if parsed and start_date <= parsed <= end_date:
            dates.add(parsed)
    curve: list[dict[str, Any]] = []
    index = 0
    for curve_date in sorted(dates):
        while index < len(pending):
            trade_date = _parse_date(str(pending[index].get("trade_date") or ""))
            if trade_date is None or trade_date > curve_date:
                break
            instrument_key = str(pending[index].get("instrument_key") or "")
            shares = _float_or_none(pending[index].get("shares")) or 0.0
            side = str(pending[index].get("side") or "").upper()
            if side == "BUY":
                holdings[instrument_key] = holdings.get(instrument_key, 0.0) + shares
            elif side == "SELL":
                holdings[instrument_key] = max(0.0, holdings.get(instrument_key, 0.0) - shares)
            index += 1
        value = _holdings_value_krw(
            holdings=holdings,
            instruments=instruments,
            price_map=price_map,
            fx_map=fx_map,
            valuation_date=curve_date,
            price_lookup="before",
            warnings=[],
        )
        if value is not None:
            curve.append({"date": curve_date.isoformat(), "value_krw": int(round(value))})
    return curve


def _holdings_value_krw(
    *,
    holdings: Mapping[str, float],
    instruments: Mapping[str, EtfAlternativeInstrument],
    price_map: Mapping[str, list[dict[str, Any]]],
    fx_map: Mapping[str, list[dict[str, Any]]],
    valuation_date: date,
    price_lookup: str,
    warnings: list[str],
) -> float | None:
    total = 0.0
    for key, units in holdings.items():
        if abs(float(units or 0.0)) <= 0.0:
            continue
        instrument = instruments.get(key)
        rows = price_map.get(key)
        if instrument is None or not rows:
            warnings.append(f"etf_alternative_price_missing:{key}")
            return None
        price = _price_on_or_after(rows, valuation_date) if price_lookup == "after" else _price_on_or_before(rows, valuation_date)
        fx = _fx_rate_for_currency(instrument.currency, fx_map, valuation_date, lookup=price_lookup)
        if price is None or price <= 0:
            warnings.append(f"etf_alternative_valuation_price_missing:{key}:{valuation_date.isoformat()}")
            return None
        if fx is None or fx <= 0:
            warnings.append(f"etf_alternative_fx_missing:{instrument.currency}:{valuation_date.isoformat()}")
            return None
        total += float(units) * price * fx
    return total


def _load_price_series_for_instruments(
    instruments: list[EtfAlternativeInstrument],
    *,
    path: Any,
    provider: str,
    start_date: date,
    end_date: date,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any], list[str]]:
    warnings: list[str] = []
    local = _load_local_price_payload(path, warnings=warnings)
    result: dict[str, list[dict[str, Any]]] = {}
    diagnostics: dict[str, Any] = {}
    for instrument in instruments:
        rows, basis = _price_rows_from_payload(local, instrument)
        if rows:
            result[instrument.key] = rows
            diagnostics[instrument.key] = {"provider": "local_json", "price_basis": basis, "rows": len(rows)}
    missing = [item for item in instruments if item.key not in result and item.symbol]
    if str(provider or "").lower() == "yfinance" and missing:
        fetched = _fetch_yfinance_prices(missing, start_date=start_date, end_date=end_date, warnings=warnings)
        for key, rows in fetched.items():
            if rows:
                result[key] = rows
                diagnostics[key] = {"provider": "yfinance", "price_basis": "adjusted_close", "rows": len(rows)}
    return result, diagnostics, warnings


def _load_local_price_payload(path: Any, *, warnings: list[str]) -> Mapping[str, Any]:
    if not path:
        return {}
    candidate = Path(path)
    if not candidate.exists():
        warnings.append(f"etf_alternative_price_history_missing:{candidate}")
        return {}
    try:
        payload = json.loads(candidate.read_text(encoding="utf-8"))
    except Exception as exc:
        warnings.append(f"etf_alternative_price_history_invalid:{_short_error(exc)}")
        return {}
    if not isinstance(payload, Mapping):
        warnings.append("etf_alternative_price_history_not_object")
        return {}
    return payload


def _price_rows_from_payload(
    payload: Mapping[str, Any],
    instrument: EtfAlternativeInstrument,
) -> tuple[list[dict[str, Any]], str]:
    keys = [instrument.key, instrument.key.upper(), instrument.symbol, instrument.symbol.upper()]
    for key in keys:
        if key and key in payload:
            rows, basis = _normalize_price_rows(payload[key])
            if rows:
                return rows, basis
    return [], "unknown"


def _fetch_yfinance_prices(
    instruments: list[EtfAlternativeInstrument],
    *,
    start_date: date,
    end_date: date,
    warnings: list[str],
) -> dict[str, list[dict[str, Any]]]:
    try:
        import yfinance as yf
    except Exception as exc:
        warnings.append(f"etf_alternative_yfinance_unavailable:{_short_error(exc)}")
        return {}
    result: dict[str, list[dict[str, Any]]] = {}
    for instrument in instruments:
        try:
            data = yf.download(
                instrument.symbol,
                start=start_date.isoformat(),
                end=(end_date + timedelta(days=1)).isoformat(),
                progress=False,
                auto_adjust=True,
                threads=False,
            )
        except Exception as exc:
            warnings.append(f"etf_alternative_yfinance_failed:{instrument.key}:{_short_error(exc)}")
            continue
        rows: list[dict[str, Any]] = []
        try:
            close = data["Close"]
        except Exception:
            close = None
        if close is None:
            warnings.append(f"etf_alternative_yfinance_no_close:{instrument.key}")
            continue
        for index, value in close.dropna().items():
            if hasattr(value, "iloc"):
                try:
                    value = value.iloc[0]
                except Exception:
                    pass
            parsed = _parse_date(str(index)[:10])
            number = _float_or_none(value)
            if parsed and number is not None:
                rows.append({"date": parsed.isoformat(), "close": number})
        if rows:
            result[instrument.key] = sorted(rows, key=lambda item: item["date"])
        else:
            warnings.append(f"etf_alternative_yfinance_empty:{instrument.key}")
    return result


def _load_fx_series(path: Any) -> tuple[dict[str, list[dict[str, Any]]], list[str]]:
    warnings: list[str] = []
    if not path:
        return {}, warnings
    payload = _load_local_price_payload(path, warnings=warnings)
    result: dict[str, list[dict[str, Any]]] = {}
    for key, raw in payload.items():
        rows, _basis = _normalize_price_rows(raw)
        if rows:
            result[str(key).strip().upper()] = rows
    return result, warnings


def _fx_rate_for_currency(
    currency: str,
    fx_map: Mapping[str, list[dict[str, Any]]],
    target: date,
    *,
    lookup: str,
) -> float | None:
    normalized = str(currency or "KRW").strip().upper()
    if normalized in {"", "KRW"}:
        return 1.0
    rows = fx_map.get(normalized) or fx_map.get(f"{normalized}KRW") or fx_map.get(f"{normalized}/KRW")
    if not rows:
        return None
    return _price_on_or_after(rows, target) if lookup == "after" else _price_on_or_before(rows, target)


def _normalize_price_rows(raw: Any) -> tuple[list[dict[str, Any]], str]:
    values = raw.get("prices") if isinstance(raw, Mapping) else raw
    if not isinstance(values, list):
        return [], "unknown"
    rows: list[dict[str, Any]] = []
    basis = "close"
    for item in values:
        if isinstance(item, Mapping):
            parsed = _parse_date(str(item.get("date") or item.get("asof") or item.get("timestamp") or "")[:10])
            close = _first_number(item, ("adj_close", "adjusted_close", "auto_adjusted_close"))
            if close is not None:
                basis = "adjusted_close"
            else:
                close = _first_number(item, ("close", "price", "last", "stck_clpr", "last_price"))
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            parsed = _parse_date(str(item[0])[:10])
            close = _float_or_none(item[1])
        else:
            continue
        if parsed and close is not None:
            rows.append({"date": parsed.isoformat(), "close": float(close)})
    return sorted(rows, key=lambda item: item["date"]), basis


def _valuation_dates(
    price_map: Mapping[str, list[dict[str, Any]]],
    *,
    start_date: date,
    end_date: date,
) -> list[date]:
    values: set[date] = {start_date, end_date}
    for rows in price_map.values():
        for row in rows:
            parsed = _parse_date(str(row.get("date") or ""))
            if parsed and start_date <= parsed <= end_date:
                values.add(parsed)
    return sorted(values)


def _price_on_or_after(rows: list[dict[str, Any]], target: date) -> float | None:
    row = _price_row_on_or_after(rows, target)
    return _float_or_none(row.get("close")) if row else None


def _price_row_on_or_after(rows: list[dict[str, Any]], target: date) -> dict[str, Any] | None:
    for row in rows:
        row_date = _parse_date(str(row.get("date") or ""))
        if row_date and row_date >= target:
            return row
    return None


def _price_on_or_before(rows: list[dict[str, Any]], target: date) -> float | None:
    value = None
    for row in rows:
        row_date = _parse_date(str(row.get("date") or ""))
        if row_date and row_date <= target:
            value = _float_or_none(row.get("close"))
    return value


def _twelve_month_policy_check(policy_inputs: Mapping[str, Any]) -> dict[str, Any]:
    actual_return = _float_or_none(policy_inputs.get("twelve_month_actual_return_pct"))
    blended_return = _float_or_none(policy_inputs.get("twelve_month_blended_return_pct"))
    actual_mdd = _float_or_none(policy_inputs.get("twelve_month_actual_mdd_pct"))
    blended_mdd = _float_or_none(policy_inputs.get("twelve_month_blended_mdd_pct"))
    actual_turnover = _float_or_none(policy_inputs.get("twelve_month_actual_turnover_pct"))
    blended_turnover = _float_or_none(policy_inputs.get("twelve_month_blended_turnover_pct"))
    if None in {actual_return, blended_return, actual_mdd, blended_mdd, actual_turnover, blended_turnover}:
        return {"status": "INSUFFICIENT_DATA"}
    failed = bool(
        actual_return < blended_return
        and actual_mdd < blended_mdd
        and actual_turnover > blended_turnover
    )
    return {
        "status": "FAILED" if failed else "OK",
        "actual_return_pct": actual_return,
        "blended_return_pct": blended_return,
        "actual_mdd_pct": actual_mdd,
        "blended_mdd_pct": blended_mdd,
        "actual_turnover_pct": actual_turnover,
        "blended_turnover_pct": blended_turnover,
    }


def _action_policy_check(policy_inputs: Mapping[str, Any], *, min_samples: int) -> dict[str, Any]:
    raw = policy_inputs.get("action_add_starter_vs_etf")
    if not isinstance(raw, Mapping):
        raw = policy_inputs.get("action_benchmark_excess")
    if not isinstance(raw, Mapping):
        return {"status": "INSUFFICIENT_DATA"}
    sample_count = int(_float_or_none(raw.get("sample_count")) or 0)
    avg_excess = _float_or_none(raw.get("avg_excess_return_pct"))
    actions = raw.get("actions")
    if sample_count < min_samples or avg_excess is None:
        return {"status": "INSUFFICIENT_DATA", "sample_count": sample_count, "min_samples": min_samples}
    failed = avg_excess < 0
    return {
        "status": "FAILED" if failed else "OK",
        "sample_count": sample_count,
        "min_samples": min_samples,
        "avg_excess_return_pct": round(avg_excess, 6),
        "actions": actions if isinstance(actions, list) else sorted(_BUY_ACTIONS),
    }


def _alpha_policy_unavailable(*, settings: Any, reason: str) -> dict[str, Any]:
    return {
        "mode": str(getattr(settings, "alpha_policy_mode", "report_only") or "report_only"),
        "status": "INSUFFICIENT_DATA",
        "decisions": [],
        "checks": {
            "three_month_consecutive_underperformance": {"status": "INSUFFICIENT_DATA", "reason": reason},
            "six_month_cumulative_excess": {"status": "INSUFFICIENT_DATA", "reason": reason},
            "twelve_month_return_mdd_turnover": {"status": "INSUFFICIENT_DATA", "reason": reason},
            "action_add_starter_vs_etf": {"status": "INSUFFICIENT_DATA", "reason": reason},
        },
    }


def _failed_simulation(
    *,
    key: str,
    label: str,
    weights: dict[str, float],
    status: str,
    warnings: list[str],
) -> EtfAlternativePortfolioResult:
    return EtfAlternativePortfolioResult(
        key=key,
        label=label,
        weights=weights,
        status=status,
        warnings=list(dict.fromkeys(warnings)),
    )


def _simulation_status_from_warnings(warnings: list[str]) -> str:
    if any("fx_missing" in item for item in warnings):
        return "fx_missing"
    if any("price_missing" in item for item in warnings):
        return "price_missing"
    return "calculation_unavailable"


def _portfolio_label(key: str) -> str:
    labels = {
        "KOSPI200": "KOSPI200 ETF 100%",
        "KOSPI200_100": "KOSPI200 ETF 100%",
        "KOSDAQ150": "KOSDAQ150 ETF 100%",
        "KOSDAQ150_100": "KOSDAQ150 ETF 100%",
        "SP500": "S&P500 ETF 100%",
        "SP500_100": "S&P500 ETF 100%",
        "NASDAQ100": "Nasdaq100 ETF 100%",
        "NASDAQ100_100": "Nasdaq100 ETF 100%",
        "BLENDED": "혼합 벤치마크",
    }
    return labels.get(str(key), str(key))


def _empty_cashflow_summary(*, source: str) -> dict[str, Any]:
    return {
        "status": "unavailable",
        "source": source,
        "dated_flow_count": 0,
        "available_flow_count": 0,
        "deposit_amount_krw": 0,
        "withdrawal_amount_krw": 0,
        "broker_deposit_amount_krw": None,
        "broker_withdrawal_amount_krw": None,
        "missing_reason": None,
    }


def _normalize_weights(weights: Mapping[str, Any]) -> dict[str, float]:
    parsed = _float_mapping(weights)
    total = sum(value for value in parsed.values() if value > 0)
    if total <= 0:
        return {}
    return {key: round(value / total, 6) for key, value in parsed.items() if value > 0}


def _string_mapping(value: Any) -> dict[str, str]:
    if not isinstance(value, Mapping):
        return {}
    return {str(key).strip().upper(): str(item).strip() for key, item in value.items() if str(key).strip()}


def _float_mapping(value: Any) -> dict[str, float]:
    if not isinstance(value, Mapping):
        return {}
    result: dict[str, float] = {}
    for key, item in value.items():
        number = _float_or_none(item)
        if number is not None:
            result[str(key).strip().upper()] = number
    return result


def _nested_float_mapping(value: Any) -> dict[str, dict[str, float]]:
    if not isinstance(value, Mapping):
        return {}
    result: dict[str, dict[str, float]] = {}
    for key, item in value.items():
        weights = _float_mapping(item)
        if weights:
            result[str(key).strip().upper()] = weights
    return result


def _result_by_key(
    alternatives: list[EtfAlternativePortfolioResult],
    key: str,
) -> EtfAlternativePortfolioResult | None:
    normalized = str(key).strip().upper()
    for item in alternatives:
        if item.key.upper() == normalized and item.status == "OK":
            return item
    return None


def _max_drawdown(values: list[float]) -> float | None:
    if not values:
        return None
    peak = values[0]
    drawdown = 0.0
    for value in values:
        peak = max(peak, value)
        if peak > 0:
            drawdown = min(drawdown, (value - peak) / peak)
    return drawdown


def _parse_date(value: Any) -> date | None:
    text = str(value or "").strip()
    if not text:
        return None
    text = text[:10]
    for fmt in ("%Y-%m-%d", "%Y%m%d"):
        try:
            return date.fromisoformat(text) if fmt == "%Y-%m-%d" else date(int(text[:4]), int(text[4:6]), int(text[6:8]))
        except Exception:
            continue
    return None


def _first_number(row: Mapping[str, Any], keys: tuple[str, ...]) -> float | None:
    for key in keys:
        if key in row:
            value = _float_or_none(row.get(key))
            if value is not None:
                return value
    return None


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, str):
        value = value.replace(",", "").replace("%", "").strip()
        if not value:
            return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


def _int_or_none(value: Any) -> int | None:
    number = _float_or_none(value)
    return int(round(number)) if number is not None else None


def _round_or_none(value: Any, digits: int = 6) -> float | None:
    number = _float_or_none(value)
    return round(number, digits) if number is not None else None


def _short_error(exc: Any) -> str:
    text = str(exc).replace("\n", " ").strip()
    return text[:180]


def _extend_warnings(target: list[str] | None, values: list[str]) -> None:
    if target is None:
        return
    for value in values:
        if value not in target:
            target.append(value)
