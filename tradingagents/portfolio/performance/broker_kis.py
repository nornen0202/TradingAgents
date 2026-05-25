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


_US_PERIOD_PROFIT_EXCHANGES = ("NASD", "NYSE", "AMEX")


def fetch_kis_broker_performance(
    *,
    profile: PortfolioProfile,
    period_start: date,
    period_end: date,
    benchmark_prices: Mapping[str, list[dict[str, Any]]] | None = None,
    warnings: list[str] | None = None,
) -> BrokerPerformanceSummary | None:
    market_scope = str(getattr(profile, "market_scope", "kr") or "kr").strip().lower()
    if market_scope in {"us", "overseas"}:
        return fetch_kis_overseas_broker_performance(
            profile=profile,
            period_start=period_start,
            period_end=period_end,
            benchmark_prices=benchmark_prices,
            warnings=warnings,
        )
    return fetch_kis_domestic_broker_performance(
        profile=profile,
        period_start=period_start,
        period_end=period_end,
        benchmark_prices=benchmark_prices,
        warnings=warnings,
    )


def fetch_kis_broker_performance_periods(
    *,
    profile: PortfolioProfile,
    periods: list[tuple[date, date]],
    benchmark_prices: Mapping[str, list[dict[str, Any]]] | None = None,
    warnings: list[str] | None = None,
) -> dict[tuple[str, str], BrokerPerformanceSummary]:
    results: dict[tuple[str, str], BrokerPerformanceSummary] = {}
    cache: dict[tuple[date, date], BrokerPerformanceSummary | None] = {}
    for period_start, period_end in periods:
        if period_start > period_end:
            continue
        key = (period_start, period_end)
        if key not in cache:
            cache[key] = fetch_kis_broker_performance(
                profile=profile,
                period_start=period_start,
                period_end=period_end,
                benchmark_prices=benchmark_prices,
                warnings=warnings,
            )
        summary = cache[key]
        if summary is not None:
            results[(period_start.isoformat(), period_end.isoformat())] = summary
    return results


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


def fetch_kis_overseas_broker_performance(
    *,
    profile: PortfolioProfile,
    period_start: date,
    period_end: date,
    benchmark_prices: Mapping[str, list[dict[str, Any]]] | None = None,
    warnings: list[str] | None = None,
) -> BrokerPerformanceSummary | None:
    if profile.broker != "kis":
        return None
    if not profile.account_no or not profile.product_code:
        if warnings is not None:
            warnings.append("broker_performance_kis_overseas_skipped:missing_account")
        return None
    try:
        client = KisClient.from_api_keys(environment=profile.broker_environment)
    except Exception as exc:
        if warnings is not None:
            warnings.append(f"broker_performance_kis_overseas_client_failed:{_short_error(exc)}")
        return None

    rows: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    failed = 0
    for exchange_code in _US_PERIOD_PROFIT_EXCHANGES:
        try:
            fetched_rows, summary = client.fetch_overseas_period_profit(
                account_no=profile.account_no,
                product_code=profile.product_code,
                start_date=period_start,
                end_date=period_end,
                exchange_code=exchange_code,
            )
        except Exception as exc:
            failed += 1
            if warnings is not None:
                warnings.append(
                    f"broker_performance_kis_overseas_period_profit_failed:{exchange_code}:{_short_error(exc)}"
                )
            continue
        rows.extend(item for item in fetched_rows if isinstance(item, Mapping))
        if isinstance(summary, Mapping) and summary:
            item = dict(summary)
            item.setdefault("exchange_code", exchange_code)
            summaries.append(item)

    rows = _dedupe_rows(rows)
    if not rows and not summaries:
        if warnings is not None:
            if failed:
                warnings.append("broker_performance_kis_overseas_period_profit_all_failed")
            else:
                warnings.append("broker_performance_kis_overseas_period_profit_empty")
        return None

    raw_summary = _combine_overseas_period_profit(
        rows,
        summaries,
        period_start=period_start,
        period_end=period_end,
    )
    return normalize_kis_broker_summary(
        raw_summary,
        period_start=period_start,
        period_end=period_end,
        benchmark_prices=benchmark_prices,
    )


def fetch_kis_domestic_broker_performance_periods(
    *,
    profile: PortfolioProfile,
    periods: list[tuple[date, date]],
    benchmark_prices: Mapping[str, list[dict[str, Any]]] | None = None,
    warnings: list[str] | None = None,
) -> dict[tuple[str, str], BrokerPerformanceSummary]:
    results: dict[tuple[str, str], BrokerPerformanceSummary] = {}
    cache: dict[tuple[date, date], BrokerPerformanceSummary | None] = {}
    for period_start, period_end in periods:
        if period_start > period_end:
            continue
        key = (period_start, period_end)
        if key not in cache:
            cache[key] = fetch_kis_domestic_broker_performance(
                profile=profile,
                period_start=period_start,
                period_end=period_end,
                benchmark_prices=benchmark_prices,
                warnings=warnings,
            )
        summary = cache[key]
        if summary is not None:
            results[(period_start.isoformat(), period_end.isoformat())] = summary
    return results


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
    raw_rows = _load_baseline_rows(source, warnings=warnings)
    if not raw_rows:
        return None

    raw = _select_baseline_row(
        raw_rows,
        period_start=period_start,
        period_end=period_end,
        allow_single_fallback=True,
    )
    if not raw:
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


def load_broker_performance_baseline_periods(
    path: str | Path | None,
    *,
    periods: list[tuple[date, date]],
    benchmark_prices: Mapping[str, list[dict[str, Any]]] | None = None,
    warnings: list[str] | None = None,
) -> dict[tuple[str, str], BrokerPerformanceSummary]:
    if not path:
        return {}
    source = Path(path).expanduser()
    if not source.exists():
        if warnings is not None:
            warnings.append(f"broker_performance_baseline_missing:{source}")
        return {}
    raw_rows = _load_baseline_rows(source, warnings=warnings)
    if not raw_rows:
        return {}
    results: dict[tuple[str, str], BrokerPerformanceSummary] = {}
    for period_start, period_end in dict.fromkeys(periods):
        raw = _select_baseline_row(
            raw_rows,
            period_start=period_start,
            period_end=period_end,
            allow_single_fallback=False,
        )
        if not raw:
            continue
        start = _date_or_none(raw.get("period_start") or raw.get("start_date")) or period_start
        end = _date_or_none(raw.get("period_end") or raw.get("end_date")) or period_end
        if start is None or end is None:
            continue
        results[(period_start.isoformat(), period_end.isoformat())] = normalize_kis_broker_summary(
            raw,
            period_start=start,
            period_end=end,
            benchmark_prices=benchmark_prices,
        )
    return results


def _load_baseline_rows(source: Path, *, warnings: list[str] | None = None) -> list[dict[str, Any]]:
    try:
        if source.suffix.lower() == ".csv":
            with source.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                return [dict(row) for row in reader if isinstance(row, Mapping)]
        raw_payload = json.loads(source.read_text(encoding="utf-8"))
        if isinstance(raw_payload, list):
            return [dict(item) for item in raw_payload if isinstance(item, Mapping)]
        if isinstance(raw_payload, Mapping):
            rows = raw_payload.get("periods") or raw_payload.get("rows") or raw_payload.get("broker_performance")
            if isinstance(rows, list):
                return [dict(item) for item in rows if isinstance(item, Mapping)]
            return [dict(raw_payload)]
        return []
    except Exception as exc:
        if warnings is not None:
            warnings.append(f"broker_performance_baseline_invalid:{_short_error(exc)}")
        return []


def _select_baseline_row(
    rows: list[dict[str, Any]],
    *,
    period_start: date | None,
    period_end: date | None,
    allow_single_fallback: bool,
) -> dict[str, Any]:
    if allow_single_fallback and len(rows) == 1:
        return rows[0]
    if period_start is None or period_end is None:
        return rows[0] if allow_single_fallback and rows else {}
    for row in rows:
        start = _date_or_none(row.get("period_start") or row.get("start_date"))
        end = _date_or_none(row.get("period_end") or row.get("end_date"))
        if start == period_start and end == period_end:
            return row
    return {}


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
    realized_trade_pnl = _first_int(
        raw,
        (
            "realized_trade_pnl_krw",
            "trade_tot_rlzt_pfls",
            "tot_rlzt_pfls",
            "rlzt_pfls",
            "rlzt_pfls_amt",
            "ovrs_rlzt_pfls_amt",
            "frcr_rlzt_pfls_amt",
            "realized_pnl_krw",
            "realized_pnl",
            "총실현손익",
            "매매손익",
        ),
    )
    realized_trade_return = _first_float(
        raw,
        (
            "realized_trade_return_pct",
            "trade_tot_pftrt",
            "tot_pftrt",
            "pftrt",
            "rlzt_erng_rt",
            "ovrs_rlzt_erng_rt",
            "frcr_rlzt_erng_rt",
            "realized_trade_profit_rate",
            "realized_return_pct",
            "총수익률",
            "매매수익률",
        ),
    )
    trade_fees = _first_int(raw, ("trade_tot_fee", "tot_fee", "trade_smtl_fee", "ovrs_fee", "frcr_fee", "매매수수료"))
    trade_taxes = _first_int(raw, ("trade_tot_tltx", "tot_tltx", "trade_tot_tax", "ovrs_tax", "frcr_tax", "매매세금"))
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
        realized_trade_pnl_krw=realized_trade_pnl,
        realized_trade_return_pct=_round_or_none(realized_trade_return),
        trade_fees_krw=trade_fees,
        trade_taxes_krw=trade_taxes,
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


def _combine_overseas_period_profit(
    rows: list[dict[str, Any]],
    summaries: list[dict[str, Any]],
    *,
    period_start: date,
    period_end: date,
) -> dict[str, Any]:
    raw: dict[str, Any] = {
        "broker": "kis",
        "account_scope": "US overseas",
        "period_start": period_start.isoformat(),
        "period_end": period_end.isoformat(),
    }
    if len(summaries) == 1:
        raw.update(summaries[0])
    elif summaries:
        raw["exchange_summaries"] = summaries
        for target, keys in {
            "realized_trade_pnl_krw": (
                "realized_trade_pnl_krw",
                "ovrs_rlzt_pfls_amt",
                "frcr_rlzt_pfls_amt",
                "rlzt_pfls_amt",
                "rlzt_pfls",
            ),
            "trade_fees_krw": ("trade_tot_fee", "tot_fee", "ovrs_fee", "frcr_fee", "smtl_fee"),
            "trade_taxes_krw": ("trade_tot_tltx", "tot_tltx", "ovrs_tax", "frcr_tax", "tax_amt"),
        }.items():
            values = [_first_int(summary, keys) for summary in summaries]
            numeric = [value for value in values if value is not None]
            if numeric:
                raw[target] = sum(numeric)
        for target, keys in {
            "realized_trade_return_pct": (
                "realized_trade_return_pct",
                "rlzt_erng_rt",
                "ovrs_rlzt_erng_rt",
                "frcr_rlzt_erng_rt",
                "pftrt",
            ),
        }.items():
            values = [_first_float(summary, keys) for summary in summaries]
            numeric = [value for value in values if value is not None]
            if len(numeric) == 1:
                raw[target] = numeric[0]

    realized_from_rows = sum(
        value
        for row in rows
        if (value := _first_int(
            row,
            (
                "realized_pnl_krw",
                "realized_pnl",
                "ovrs_rlzt_pfls_amt",
                "frcr_rlzt_pfls_amt",
                "rlzt_pfls_amt",
                "rlzt_pfls",
            ),
        ))
        is not None
    )
    if rows:
        raw["realized_trade_pnl_krw"] = realized_from_rows
        raw["realized_trade_row_count"] = len(rows)
    return raw


def _dedupe_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        key = json.dumps(row, sort_keys=True, ensure_ascii=False, default=str)
        if key in seen:
            continue
        seen.add(key)
        result.append(dict(row))
    return result


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
