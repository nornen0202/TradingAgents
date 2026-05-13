from __future__ import annotations

import csv
import json
import re
from datetime import date
from pathlib import Path
from typing import Any, Mapping

from tradingagents.portfolio.account_models import PortfolioProfile
from tradingagents.portfolio.kis import KisClient

from .broker_models import BrokerBenchmarkReturn, BrokerPerformanceSummary


def fetch_kis_domestic_broker_performance(
    *,
    profile: PortfolioProfile,
    period_start: date,
    period_end: date,
    benchmark_prices: Mapping[str, list[dict[str, Any]]] | None = None,
    warnings: list[str] | None = None,
) -> BrokerPerformanceSummary | None:
    if profile.broker != "kis":
        return None
    market_scope = str(getattr(profile, "market_scope", "kr") or "kr").strip().lower()
    if market_scope in {"us", "overseas"}:
        return None
    if not profile.account_no or not profile.product_code:
        if warnings is not None:
            warnings.append("broker_performance_kis_skipped:missing_account")
        return None
    try:
        client = KisClient.from_api_keys(environment=profile.broker_environment)
        _rows, summary = client.fetch_domestic_period_profit(
            account_no=profile.account_no,
            product_code=profile.product_code,
            start_date=period_start,
            end_date=period_end,
        )
        try:
            _trade_rows, trade_summary = client.fetch_domestic_period_trade_profit(
                account_no=profile.account_no,
                product_code=profile.product_code,
                start_date=period_start,
                end_date=period_end,
            )
        except Exception as exc:
            trade_summary = {}
            if warnings is not None:
                warnings.append(f"broker_performance_kis_trade_profit_failed:{_short_error(exc)}")
    except Exception as exc:
        if warnings is not None:
            warnings.append(f"broker_performance_kis_period_profit_failed:{_short_error(exc)}")
        return None

    raw_summary = _merge_raw_summaries(summary, trade_summary)
    if not raw_summary:
        if warnings is not None:
            warnings.append("broker_performance_kis_empty_summary")
        return None
    return normalize_kis_broker_summary(
        raw_summary,
        period_start=period_start,
        period_end=period_end,
        benchmark_prices=benchmark_prices,
    )


def load_broker_performance_baseline(
    path: str | Path | None,
    *,
    period_start: date | None = None,
    period_end: date | None = None,
    benchmark_prices: Mapping[str, list[dict[str, Any]]] | None = None,
    warnings: list[str] | None = None,
) -> BrokerPerformanceSummary | None:
    if not path:
        return None
    source = Path(path).expanduser()
    if not source.exists():
        if warnings is not None:
            warnings.append(f"broker_performance_baseline_missing:{source}")
        return None
    try:
        if source.suffix.lower() == ".csv":
            with source.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                raw = next(reader, None) or {}
        else:
            raw_payload = json.loads(source.read_text(encoding="utf-8"))
            if isinstance(raw_payload, list):
                raw = next((item for item in raw_payload if isinstance(item, dict)), {})
            elif isinstance(raw_payload, dict):
                raw = raw_payload
            else:
                raw = {}
    except Exception as exc:
        if warnings is not None:
            warnings.append(f"broker_performance_baseline_invalid:{_short_error(exc)}")
        return None

    start = _date_or_none(raw.get("period_start") or raw.get("start_date")) or period_start
    end = _date_or_none(raw.get("period_end") or raw.get("end_date")) or period_end
    if start is None or end is None:
        if warnings is not None:
            warnings.append("broker_performance_baseline_missing_period")
        return None
    return normalize_kis_broker_summary(
        raw,
        period_start=start,
        period_end=end,
        benchmark_prices=benchmark_prices,
    )


def normalize_kis_broker_summary(
    raw_summary: Mapping[str, Any],
    *,
    period_start: date,
    period_end: date,
    benchmark_prices: Mapping[str, list[dict[str, Any]]] | None = None,
) -> BrokerPerformanceSummary:
    raw = dict(raw_summary)
    warnings: list[str] = []

    start_asset = _first_int(
        raw,
        (
            "start_asset_krw",
            "base_asset_krw",
            "begin_asset_krw",
            "bgn_asst_amt",
            "bfdy_tot_asst_evlu_amt",
            "pchs_amt_smtl_amt",
            "기초자산",
        ),
    )
    end_asset = _first_int(
        raw,
        (
            "end_asset_krw",
            "nass_amt",
            "tot_asst_amt",
            "evlu_amt_smtl_amt",
            "tot_evlu_amt",
            "asst_icdc_after_amt",
            "기말자산",
        ),
    )
    deposit = _first_int(raw, ("deposit_amount_krw", "tot_dpst_amt", "dpst_amt", "in_amt", "입금고", "입금액")) or 0
    withdrawal = (
        _first_int(raw, ("withdrawal_amount_krw", "tot_wthdr_amt", "wthdr_amt", "out_amt", "출금고", "출금액")) or 0
    )
    investment_pnl = _first_int(
        raw,
        (
            "investment_pnl_krw",
            "asst_icdc_amt",
            "evlu_pfls_smtl_amt",
            "tot_evlu_pfls_amt",
            "evlu_pfls_amt",
            "투자손익",
        ),
    )
    if investment_pnl is None and start_asset is not None and end_asset is not None:
        investment_pnl = int(end_asset - start_asset - deposit + withdrawal)

    principal = _first_int(raw, ("investment_principal_krw", "inv_principal_krw", "투자원금"))
    if principal is None and start_asset is not None:
        principal = int(start_asset + deposit - withdrawal)

    balance_return = _first_float(
        raw,
        (
            "balance_return_pct",
            "net_asset_return_pct",
            "asst_icdc_erng_rt",
            "erng_rt",
            "evlu_pfls_rt",
            "잔액기준 수익률",
            "순자산 수익률",
        ),
    )
    if balance_return is None and investment_pnl is not None and principal and principal > 0:
        balance_return = investment_pnl / principal * 100.0

    total_deposit_return = _first_float(raw, ("total_deposit_return_pct", "tot_dpst_erng_rt", "총입금액 수익률"))
    total_deposit_base = start_asset + deposit if start_asset is not None else None
    if total_deposit_return is None and investment_pnl is not None and total_deposit_base and total_deposit_base > 0:
        total_deposit_return = investment_pnl / total_deposit_base * 100.0

    net_asset_return = _first_float(raw, ("net_asset_return_pct", "nass_erng_rt", "순자산 수익률"))
    if net_asset_return is None:
        net_asset_return = balance_return

    if end_asset is None:
        warnings.append("broker_performance_missing_end_asset")
    if investment_pnl is None:
        warnings.append("broker_performance_missing_investment_pnl")
    if balance_return is None:
        warnings.append("broker_performance_missing_balance_return")

    benchmark_returns = _benchmark_returns(
        benchmark_prices or {},
        period_start=period_start,
        period_end=period_end,
        broker_return_pct=balance_return,
    )
    excess = {
        item.benchmark: item.excess_return_pct
        for item in benchmark_returns
        if item.excess_return_pct is not None
    }

    return BrokerPerformanceSummary(
        broker=str(raw.get("broker") or "kis"),
        account_scope=str(raw.get("account_scope") or "KR domestic"),
        period_start=period_start.isoformat(),
        period_end=period_end.isoformat(),
        investment_pnl_krw=investment_pnl,
        balance_return_pct=_round_or_none(balance_return),
        average_balance_return_pct=_round_or_none(
            _first_float(raw, ("average_balance_return_pct", "avg_blce_erng_rt", "평잔 수익률"))
        ),
        net_asset_return_pct=_round_or_none(net_asset_return),
        total_deposit_return_pct=_round_or_none(total_deposit_return),
        investment_principal_krw=principal,
        start_asset_krw=start_asset,
        end_asset_krw=end_asset,
        deposit_amount_krw=deposit,
        withdrawal_amount_krw=withdrawal,
        dividend_krw=_first_int(raw, ("dividend_krw", "dvdn_amt", "배당금")) or 0,
        interest_krw=_first_int(raw, ("interest_krw", "int_amt", "예탁금이자", "상환이자")) or 0,
        fees_krw=_first_int(raw, ("fees_krw", "fee_amt", "smtl_fee", "수수료")) or 0,
        taxes_krw=_first_int(raw, ("taxes_krw", "tax_amt", "tr_tax", "세금")) or 0,
        benchmark_returns=benchmark_returns,
        benchmark_excess_returns=excess,
        raw_summary=raw,
        warnings=warnings,
    )


def _merge_raw_summaries(primary: Any, secondary: Any) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    if isinstance(secondary, Mapping):
        merged.update({f"trade_{key}": value for key, value in secondary.items()})
    if isinstance(primary, Mapping):
        merged.update(primary)
    return merged


def _benchmark_returns(
    benchmark_prices: Mapping[str, list[dict[str, Any]]],
    *,
    period_start: date,
    period_end: date,
    broker_return_pct: float | None,
) -> list[BrokerBenchmarkReturn]:
    rows: list[BrokerBenchmarkReturn] = []
    for name, series in benchmark_prices.items():
        start_price = _price_on_or_after(series, period_start)
        end_price = _price_on_or_before(series, period_end)
        benchmark_pct = (
            (end_price - start_price) / start_price * 100.0
            if start_price is not None and end_price is not None and start_price > 0
            else None
        )
        excess = broker_return_pct - benchmark_pct if broker_return_pct is not None and benchmark_pct is not None else None
        rows.append(
            BrokerBenchmarkReturn(
                benchmark=str(name),
                benchmark_return_pct=_round_or_none(benchmark_pct),
                excess_return_pct=_round_or_none(excess),
            )
        )
    return rows


def _price_on_or_after(rows: list[dict[str, Any]], target: date) -> float | None:
    for row in sorted(rows, key=lambda item: str(item.get("date") or "")):
        row_date = _date_or_none(row.get("date"))
        price = _first_float(row, ("close", "price", "last"))
        if row_date is not None and row_date >= target and price is not None:
            return price
    return None


def _price_on_or_before(rows: list[dict[str, Any]], target: date) -> float | None:
    candidate: float | None = None
    for row in sorted(rows, key=lambda item: str(item.get("date") or "")):
        row_date = _date_or_none(row.get("date"))
        price = _first_float(row, ("close", "price", "last"))
        if row_date is not None and row_date <= target and price is not None:
            candidate = price
    return candidate


def _first_int(payload: Mapping[str, Any], keys: tuple[str, ...]) -> int | None:
    value = _first_float(payload, keys)
    if value is None:
        return None
    return int(round(value))


def _first_float(payload: Mapping[str, Any], keys: tuple[str, ...]) -> float | None:
    for key in keys:
        value = payload.get(key)
        if value in (None, ""):
            continue
        try:
            text = str(value).strip().replace(",", "").replace("%", "")
            return float(text)
        except (TypeError, ValueError):
            continue
    return None


def _date_or_none(value: Any) -> date | None:
    if isinstance(value, date):
        return value
    text = str(value or "").strip()
    if len(text) >= 10 and text[4] == "-" and text[7] == "-":
        try:
            return date(int(text[:4]), int(text[5:7]), int(text[8:10]))
        except ValueError:
            return None
    digits = re.sub(r"\D", "", text)
    if len(digits) >= 8:
        try:
            return date(int(digits[:4]), int(digits[4:6]), int(digits[6:8]))
        except ValueError:
            return None
    return None


def _round_or_none(value: float | None, digits: int = 6) -> float | None:
    if value is None:
        return None
    return round(float(value), digits)


def _short_error(exc: Exception) -> str:
    text = str(exc).strip().replace("\n", " ") or exc.__class__.__name__
    text = re.sub(r"(CANO=)[^&\s]+", r"\1***MASKED***", text)
    text = re.sub(r"(ACNT_PRDT_CD=)[^&\s]+", r"\1***MASKED***", text)
    text = re.sub(r"\b\d{8}-\d{2}\b", "***MASKED***", text)
    return text[:240]
