from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
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
    snapshot_rows = _load_snapshot_history(run_dir=run_dir, profile_name=profile.name)
    snapshot_rows.append(current_snapshot)
    snapshot_rows = _dedupe_snapshot_rows(snapshot_rows)

    start_date = _default_start_date(snapshot_rows, lookback_days=int(getattr(settings, "lookback_days", 800)))
    end_date = _parse_date(current_snapshot["date"]) or date.today()
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

    benchmark_prices = _load_benchmark_prices(
        profile=profile,
        settings=settings,
        market_scope=market_scope,
        benchmarks=benchmark_names,
        start_date=start_date,
        end_date=end_date,
        warnings=warnings,
    )
    periods = _compute_periods(
        snapshot_rows=snapshot_rows,
        ledger_events=ledger_events,
        benchmark_prices=benchmark_prices,
        period_names=tuple(getattr(settings, "periods", ("1M", "3M", "6M", "YTD", "1Y", "ALL"))),
        end_date=end_date,
        warnings=warnings,
    )
    chart_data = _build_chart_data(snapshot_rows=snapshot_rows, benchmark_prices=benchmark_prices)
    contribution = _contribution_by_ticker(snapshot=snapshot, ledger_events=ledger_events)
    costs = _cost_summary(ledger_events)
    summary = _summary(periods)

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
        "data_quality": {
            "snapshot_count": len(snapshot_rows),
            "ledger_event_count": len(ledger_events),
            "benchmark_provider": _provider_label(settings),
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
    quality = payload.get("data_quality") if isinstance(payload.get("data_quality"), Mapping) else {}
    rows = [
        "| 기간 | 실제 수익률 | 최고 초과 | 최저 초과 | 초과손익 | 비교 기준 |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for period in periods:
        if not isinstance(period, Mapping):
            continue
        rows.append(
            "| "
            f"{period.get('period', '-')} | "
            f"{_pct(period.get('actual_return'))} | "
            f"{_pct((period.get('best_excess') or {}).get('excess_return'))} | "
            f"{_pct((period.get('worst_excess') or {}).get('excess_return'))} | "
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
    return "\n".join(
        [
            "## 계좌 성과 vs 지수/ETF",
            "",
            f"- 기본 기간: `{summary.get('default_period') or '-'}`",
            f"- 실제 계좌 수익률: `{_pct(summary.get('actual_return'))}`",
            f"- 최고 초과 기준: `{((summary.get('best_excess') or {}).get('benchmark')) or '-'}` "
            f"({_pct((summary.get('best_excess') or {}).get('excess_return'))})",
            f"- 최저 초과 기준: `{((summary.get('worst_excess') or {}).get('benchmark')) or '-'}` "
            f"({_pct((summary.get('worst_excess') or {}).get('excess_return'))})",
            f"- 복잡한 운용 프리미엄: `{_krw((summary.get('best_excess') or {}).get('excess_krw'))}`",
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
            "### 종목별 기여도",
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
        if status_path.exists():
            try:
                status = json.loads(status_path.read_text(encoding="utf-8"))
                if str(status.get("profile") or "") != profile_name:
                    continue
            except Exception:
                continue
        try:
            payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
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
    }


def _snapshot_payload_row(payload: Mapping[str, Any], *, profile_name: str) -> dict[str, Any]:
    value = _float_or_none(payload.get("account_value_krw"))
    if value is None:
        value = _float_or_none(payload.get("total_equity_krw")) or 0.0
    return {
        "snapshot_id": str(payload.get("snapshot_id") or ""),
        "profile": profile_name,
        "date": str(payload.get("as_of") or "")[:10],
        "as_of": str(payload.get("as_of") or ""),
        "account_value_krw": float(value),
    }


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
        if market_scope == "us":
            raw_rows = []
            raw_rows.extend(
                client.fetch_overseas_order_fills(
                    account_no=profile.account_no,
                    product_code=profile.product_code,
                    start_date=start_date,
                    end_date=end_date,
                )
            )
            raw_rows.extend(
                client.fetch_overseas_period_transactions(
                    account_no=profile.account_no,
                    product_code=profile.product_code,
                    start_date=start_date,
                    end_date=end_date,
                )
            )
            profits, _summary = client.fetch_overseas_period_profit(
                account_no=profile.account_no,
                product_code=profile.product_code,
                start_date=start_date,
                end_date=end_date,
            )
            raw_rows.extend(profits)
            return [_normalize_ledger_event(row, market="US", source="kis_overseas") for row in raw_rows]

        raw_rows = []
        raw_rows.extend(
            client.fetch_domestic_order_fills(
                account_no=profile.account_no,
                product_code=profile.product_code,
                start_date=start_date,
                end_date=end_date,
            )
        )
        daily_profit, _daily_summary = client.fetch_domestic_period_profit(
            account_no=profile.account_no,
            product_code=profile.product_code,
            start_date=start_date,
            end_date=end_date,
        )
        trade_profit, _trade_summary = client.fetch_domestic_period_trade_profit(
            account_no=profile.account_no,
            product_code=profile.product_code,
            start_date=start_date,
            end_date=end_date,
        )
        raw_rows.extend(daily_profit)
        raw_rows.extend(trade_profit)
        return [_normalize_ledger_event(row, market="KR", source="kis_domestic") for row in raw_rows]
    except Exception as exc:
        warnings.append(f"account_performance_kis_ledger_failed:{_short_error(exc)}")
        return []


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
        event_type="trade" if side in {"BUY", "SELL"} else "cash_or_profit",
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
) -> dict[str, list[dict[str, Any]]]:
    prices: dict[str, list[dict[str, Any]]] = {}
    prices.update(_load_local_benchmark_prices(getattr(settings, "price_history_path", None), benchmarks=benchmarks, warnings=warnings))
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
            )
        )
        missing = [name for name in benchmarks if name not in prices]

    provider = str(getattr(settings, "price_provider", "yfinance") or "yfinance").strip().lower()
    if provider == "local_json":
        return prices
    if provider in {"", "none", "disabled"}:
        if missing:
            warnings.append(f"account_performance_benchmark_missing:{','.join(missing)}")
        return prices
    if provider != "yfinance":
        warnings.append(f"account_performance_price_provider_unsupported:{provider}")
        return prices

    if missing:
        prices.update(
            _fetch_yfinance_benchmark_prices(
                market_scope=market_scope,
                benchmarks=tuple(missing),
                start_date=start_date,
                end_date=end_date,
                warnings=warnings,
            )
        )
    return prices


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
) -> dict[str, list[dict[str, Any]]]:
    try:
        from tradingagents.portfolio.kis import KisClient

        client = KisClient.from_api_keys(environment=profile.broker_environment)
    except Exception as exc:
        warnings.append(f"account_performance_kis_benchmark_unavailable:{_short_error(exc)}")
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
        except Exception as exc:
            warnings.append(f"account_performance_kis_benchmark_failed:{benchmark}:{_short_error(exc)}")
    return result


def _fetch_yfinance_benchmark_prices(
    *,
    market_scope: str,
    benchmarks: tuple[str, ...],
    start_date: date,
    end_date: date,
    warnings: list[str],
) -> dict[str, list[dict[str, Any]]]:
    try:
        import yfinance as yf
    except Exception as exc:
        warnings.append(f"account_performance_yfinance_unavailable:{_short_error(exc)}")
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
            continue
        if data is None or getattr(data, "empty", True):
            warnings.append(f"account_performance_yfinance_empty:{benchmark}")
            continue
        close = data.get("Close")
        if close is None:
            warnings.append(f"account_performance_yfinance_no_close:{benchmark}")
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
    return result


def _compute_periods(
    *,
    snapshot_rows: list[dict[str, Any]],
    ledger_events: list[LedgerEvent],
    benchmark_prices: dict[str, list[dict[str, Any]]],
    period_names: tuple[str, ...],
    end_date: date,
    warnings: list[str],
) -> list[dict[str, Any]]:
    periods: list[dict[str, Any]] = []
    if len(snapshot_rows) < 2:
        return periods
    for period_name in period_names:
        start_boundary = _period_start(period_name, end_date=end_date, snapshot_rows=snapshot_rows)
        start_snapshot = _first_snapshot_on_or_after(snapshot_rows, start_boundary)
        end_snapshot = _last_snapshot_on_or_before(snapshot_rows, end_date)
        if not start_snapshot or not end_snapshot or start_snapshot["date"] >= end_snapshot["date"]:
            warnings.append(f"account_performance_period_partial:{period_name}")
            continue
        start_value = float(start_snapshot["account_value_krw"])
        end_value = float(end_snapshot["account_value_krw"])
        if start_value <= 0:
            warnings.append(f"account_performance_period_invalid_start_value:{period_name}")
            continue
        actual_return = (end_value - start_value) / start_value
        start = _parse_date(str(start_snapshot["date"])) or start_boundary
        end = _parse_date(str(end_snapshot["date"])) or end_date
        simple_rows: list[dict[str, Any]] = []
        cashflow_rows: list[dict[str, Any]] = []
        for benchmark, series in benchmark_prices.items():
            simple = _benchmark_simple_return(series, start_date=start, end_date=end)
            if simple is None:
                warnings.append(f"account_performance_benchmark_period_missing:{period_name}:{benchmark}")
                continue
            excess = actual_return - simple
            simple_rows.append(
                {
                    "benchmark": benchmark,
                    "benchmark_return": round(simple, 6),
                    "excess_return": round(excess, 6),
                    "excess_krw": int(round(excess * start_value)),
                }
            )
            simulated = _benchmark_cashflow_return(
                series,
                ledger_events=ledger_events,
                start_date=start,
                end_date=end,
                start_value=start_value,
            )
            if simulated is not None:
                cf_excess = actual_return - simulated
                cashflow_rows.append(
                    {
                        "benchmark": benchmark,
                        "benchmark_return": round(simulated, 6),
                        "excess_return": round(cf_excess, 6),
                        "excess_krw": int(round(cf_excess * start_value)),
                    }
                )
        all_rows = simple_rows or cashflow_rows
        best = max(all_rows, key=lambda item: float(item["excess_return"])) if all_rows else None
        worst = min(all_rows, key=lambda item: float(item["excess_return"])) if all_rows else None
        period_values = _snapshot_values_between(snapshot_rows, start, end)
        periods.append(
            {
                "period": period_name,
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "actual_start_value_krw": int(round(start_value)),
                "actual_end_value_krw": int(round(end_value)),
                "actual_return": round(actual_return, 6),
                "mdd": _max_drawdown(period_values),
                "volatility": _volatility(period_values),
                "simple_benchmarks": simple_rows,
                "cashflow_benchmarks": cashflow_rows,
                "best_excess": best or {},
                "worst_excess": worst or {},
            }
        )
    return periods


def _build_chart_data(
    *,
    snapshot_rows: list[dict[str, Any]],
    benchmark_prices: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    if not snapshot_rows:
        return {"series": []}
    start_value = float(snapshot_rows[0].get("account_value_krw") or 0.0)
    benchmark_start = {
        name: _price_on_or_after(rows, _parse_date(str(snapshot_rows[0].get("date"))) or date.today())
        for name, rows in benchmark_prices.items()
    }
    series = []
    for row in snapshot_rows:
        row_date = _parse_date(str(row.get("date"))) or date.today()
        item: dict[str, Any] = {"date": row_date.isoformat()}
        value = float(row.get("account_value_krw") or 0.0)
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
    return {"series": series, "benchmarks": list(benchmark_prices)}


def _contribution_by_ticker(*, snapshot: AccountSnapshot, ledger_events: list[LedgerEvent]) -> list[dict[str, Any]]:
    realized: dict[str, float] = {}
    for event in ledger_events:
        if event.realized_pnl_krw is None or not event.ticker:
            continue
        realized[event.ticker] = realized.get(event.ticker, 0.0) + float(event.realized_pnl_krw)
    tickers = {position.canonical_ticker for position in snapshot.positions} | set(realized)
    rows = []
    for ticker in sorted(tickers):
        position = snapshot.find_position(ticker)
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


def _cost_summary(ledger_events: list[LedgerEvent]) -> dict[str, int]:
    fees = sum(event.fee_krw for event in ledger_events)
    taxes = sum(event.tax_krw for event in ledger_events)
    return {
        "fees_krw": int(round(fees)),
        "taxes_krw": int(round(taxes)),
        "total_cost_krw": int(round(fees + taxes)),
    }


def _summary(periods: list[dict[str, Any]]) -> dict[str, Any]:
    default = _default_period(periods)
    if not default:
        return {}
    return {
        "default_period": default.get("period"),
        "actual_return": default.get("actual_return"),
        "best_excess": default.get("best_excess") or {},
        "worst_excess": default.get("worst_excess") or {},
    }


def _default_period(periods: list[dict[str, Any]]) -> dict[str, Any] | None:
    for preferred in ("YTD", "1Y", "6M", "3M", "1M", "ALL"):
        for period in periods:
            if period.get("period") == preferred:
                return period
    return periods[-1] if periods else None


def _benchmark_simple_return(rows: list[dict[str, Any]], *, start_date: date, end_date: date) -> float | None:
    start = _price_on_or_after(rows, start_date)
    end = _price_on_or_before(rows, end_date)
    if start is None or end is None or start <= 0:
        return None
    return (end - start) / start


def _benchmark_cashflow_return(
    rows: list[dict[str, Any]],
    *,
    ledger_events: list[LedgerEvent],
    start_date: date,
    end_date: date,
    start_value: float,
) -> float | None:
    start = _price_on_or_after(rows, start_date)
    end = _price_on_or_before(rows, end_date)
    if start is None or end is None or start <= 0 or start_value <= 0:
        return None
    shares = start_value / start
    cash = 0.0
    for event in ledger_events:
        event_date = _parse_date(event.date)
        if event_date is None or event_date < start_date or event_date > end_date:
            continue
        price = _price_on_or_before(rows, event_date) or start
        if price <= 0 or event.gross_amount_krw <= 0:
            continue
        if event.side == "BUY":
            shares += event.gross_amount_krw / price
            cash -= event.gross_amount_krw
        elif event.side == "SELL":
            shares -= event.gross_amount_krw / price
            cash += event.gross_amount_krw
    final_value = shares * end + cash
    return (final_value - start_value) / start_value


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
    return rows[0] if rows else None


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
    return min(first, fallback) if first else fallback


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


def _side_from_row(row: Mapping[str, Any]) -> str:
    code = _first_text(row, ("sll_buy_dvsn_cd", "sll_buy_dvsn", "trad_dvsn", "tr_dvsn_cd"))
    name = _first_text(row, ("sll_buy_dvsn_name", "trad_dvsn_name", "tr_dvsn_name", "rmks_name")).lower()
    if code in {"02", "2", "BUY"} or "buy" in name or "매수" in name:
        return "BUY"
    if code in {"01", "1", "SELL"} or "sell" in name or "매도" in name:
        return "SELL"
    return "UNKNOWN"


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
    return str(exc).strip().replace("\n", " ")[:180] or exc.__class__.__name__


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
