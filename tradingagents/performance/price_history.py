from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from tradingagents.external.prism_normalize import normalize_market


BENCHMARK_KEY = "__BENCHMARK__"


@dataclass(frozen=True)
class PriceHistoryLoadResult:
    price_history: dict[str, Any] = field(default_factory=dict)
    provider: str = "none"
    warnings: list[str] = field(default_factory=list)

    @property
    def has_prices(self) -> bool:
        return any(key != BENCHMARK_KEY for key in self.price_history)


def load_price_history_for_recommendations(
    db_path: Path,
    *,
    provider: str = "none",
    price_history_path: str | Path | None = None,
    benchmark_ticker: str | None = None,
    market: str | None = None,
    lookback_days: int = 120,
    asof_date: str | None = None,
) -> PriceHistoryLoadResult:
    provider = str(provider or "none").strip().lower()
    warnings: list[str] = []
    history: dict[str, Any] = {}

    if price_history_path:
        local_payload = _load_price_history_json(Path(price_history_path), benchmark_ticker=benchmark_ticker)
        history.update(local_payload.price_history)
        warnings.extend(local_payload.warnings)

    if provider in {"", "none", "disabled"}:
        if not history:
            warnings.append("performance_outcome_update_skipped:no_price_history_or_provider")
        return PriceHistoryLoadResult(price_history=history, provider="local_json" if history else "none", warnings=warnings)

    if provider == "local_json":
        if not history:
            warnings.append("performance_price_history_path_missing")
        return PriceHistoryLoadResult(price_history=history, provider=provider, warnings=warnings)

    if provider != "yfinance":
        warnings.append(f"performance_price_provider_unsupported:{provider}")
        return PriceHistoryLoadResult(price_history=history, provider=provider, warnings=warnings)

    tickers, market_filter_warnings = _recommendation_tickers(db_path, market=market)
    warnings.extend(market_filter_warnings)
    missing = [ticker for ticker in tickers if ticker not in {key.upper() for key in history}]
    if benchmark_ticker and BENCHMARK_KEY not in history:
        missing.append(str(benchmark_ticker).strip().upper())

    fetched, fetch_warnings = _fetch_yfinance_price_history(
        missing,
        benchmark_ticker=benchmark_ticker,
        lookback_days=lookback_days,
        asof_date=asof_date,
    )
    history.update(fetched)
    warnings.extend(fetch_warnings)
    return PriceHistoryLoadResult(price_history=history, provider=provider, warnings=warnings)


def load_price_history_json(
    path: str | Path,
    *,
    benchmark_ticker: str | None = None,
) -> PriceHistoryLoadResult:
    return _load_price_history_json(Path(path), benchmark_ticker=benchmark_ticker)


def _load_price_history_json(path: Path, *, benchmark_ticker: str | None = None) -> PriceHistoryLoadResult:
    path = Path(path)
    if not path.exists():
        return PriceHistoryLoadResult(provider="local_json", warnings=[f"performance_price_history_missing:{path}"])
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return PriceHistoryLoadResult(provider="local_json", warnings=[f"performance_price_history_invalid:{path}:{exc}"])
    if not isinstance(payload, Mapping):
        return PriceHistoryLoadResult(provider="local_json", warnings=[f"performance_price_history_not_object:{path}"])

    history = dict(payload)
    benchmark_key = str(benchmark_ticker or "").strip().upper()
    for key in ("benchmark", "BENCHMARK", benchmark_key):
        if key and key in history:
            history.setdefault(BENCHMARK_KEY, history[key])
            break
    return PriceHistoryLoadResult(price_history=history, provider="local_json")


def _recommendation_tickers(db_path: Path, *, market: str | None = None) -> tuple[list[str], list[str]]:
    if not Path(db_path).exists():
        return [], []
    target_market = _normalize_target_market(market)
    with sqlite3.connect(db_path) as conn:
        columns = _table_columns(conn, "action_recommendations")
        if "market" in columns:
            rows = conn.execute("SELECT DISTINCT ticker, market FROM action_recommendations ORDER BY ticker").fetchall()
        else:
            rows = conn.execute("SELECT DISTINCT ticker FROM action_recommendations ORDER BY ticker").fetchall()
    tickers: list[str] = []
    skipped = 0
    for row in rows:
        ticker = str(row[0]).strip().upper()
        if not ticker:
            continue
        row_market = str(row[1]).strip().upper() if len(row) > 1 and row[1] else None
        inferred_market = normalize_market(row_market, ticker=ticker)
        if target_market and inferred_market != target_market:
            skipped += 1
            continue
        tickers.append(ticker)
    warnings = (
        [f"performance_price_history_market_filter:{target_market}:skipped={skipped}"]
        if target_market and skipped
        else []
    )
    return tickers, warnings


def _normalize_target_market(value: str | None) -> str | None:
    normalized = normalize_market(value)
    return normalized if normalized in {"KR", "US"} else None


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    try:
        return {str(row[1]) for row in conn.execute(f"PRAGMA table_info({table})")}
    except sqlite3.Error:
        return set()


def _fetch_yfinance_price_history(
    tickers: list[str],
    *,
    benchmark_ticker: str | None,
    lookback_days: int,
    asof_date: str | None,
) -> tuple[dict[str, Any], list[str]]:
    if not tickers:
        return {}, []
    try:
        import yfinance as yf
    except Exception as exc:  # pragma: no cover - depends on optional runtime package
        return {}, [f"performance_yfinance_unavailable:{exc}"]

    warnings: list[str] = []
    history: dict[str, Any] = {}
    benchmark = str(benchmark_ticker or "").strip().upper()
    unique_tickers = list(dict.fromkeys(ticker for ticker in tickers if ticker))
    for ticker in unique_tickers:
        try:
            data = yf.download(
                ticker,
                period=f"{max(1, int(lookback_days))}d",
                progress=False,
                auto_adjust=False,
                threads=False,
            )
        except Exception as exc:  # pragma: no cover - network/provider dependent
            warnings.append(f"performance_yfinance_fetch_failed:{ticker}:{exc}")
            continue
        if data is None or getattr(data, "empty", True):
            warnings.append(f"performance_yfinance_no_data:{ticker}")
            continue
        close = _extract_close_series(data, ticker)
        if close is None:
            warnings.append(f"performance_yfinance_no_close:{ticker}")
            continue
        rows: list[dict[str, Any]] = []
        for index, value in close.dropna().items():
            close_value = _scalar_float(value)
            if close_value is None:
                warnings.append(f"performance_yfinance_non_scalar_close:{ticker}")
                continue
            date_text = getattr(index, "date", lambda: index)()
            rows.append({"date": str(date_text)[:10], "close": close_value})
        if rows:
            history[ticker.upper()] = rows
            if ticker == benchmark:
                history[BENCHMARK_KEY] = rows
        else:
            warnings.append(f"performance_yfinance_empty_close:{ticker}")
    if asof_date and history:
        warnings.append(f"performance_price_history_loaded_asof:{asof_date}")
    return history, warnings


def _extract_close_series(data: Any, ticker: str) -> Any | None:
    close = data.get("Close") if hasattr(data, "get") else None
    if close is None and hasattr(data, "xs"):
        try:
            close = data.xs("Close", level=0, axis=1, drop_level=True)
        except Exception:
            close = None
    if close is None:
        return None
    if hasattr(close, "columns"):
        columns = list(getattr(close, "columns", []))
        if not columns:
            return None
        ticker_text = str(ticker or "").strip().upper()
        for column in columns:
            if _column_matches_ticker(column, ticker_text):
                return close[column]
        non_empty = close.dropna(axis=1, how="all") if hasattr(close, "dropna") else close
        non_empty_columns = list(getattr(non_empty, "columns", []))
        if len(non_empty_columns) == 1:
            return non_empty[non_empty_columns[0]]
        if len(columns) == 1:
            return close[columns[0]]
        return None
    return close


def _column_matches_ticker(column: Any, ticker: str) -> bool:
    if not ticker:
        return False
    if isinstance(column, tuple):
        return any(str(part).strip().upper() == ticker for part in column)
    return str(column).strip().upper() == ticker


def _scalar_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    if hasattr(value, "item"):
        try:
            value = value.item()
        except Exception:
            return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
