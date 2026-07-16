from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Mapping

from tradingagents.external.prism_normalize import normalize_market
from tradingagents.performance.models import OUTCOME_CALCULATION_VERSION


BENCHMARK_KEY = "__BENCHMARK__"


@dataclass(frozen=True)
class PriceHistoryLoadResult:
    price_history: dict[str, Any] = field(default_factory=dict)
    provider: str = "none"
    warnings: list[str] = field(default_factory=list)
    due_recommendation_ids: tuple[int, ...] = ()

    @property
    def has_prices(self) -> bool:
        return any(key != BENCHMARK_KEY for key in self.price_history)

    @property
    def due_recommendation_count(self) -> int:
        return len(self.due_recommendation_ids)


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

    tickers, due_recommendation_ids, market_filter_warnings = _recommendations_due_for_refresh(
        db_path,
        market=market,
        asof_date=asof_date,
        refresh_window_days=lookback_days,
    )
    warnings.extend(market_filter_warnings)

    if provider in {"", "none", "disabled"}:
        if not history:
            warnings.append("performance_outcome_update_skipped:no_price_history_or_provider")
        return PriceHistoryLoadResult(
            price_history=history,
            provider="local_json" if history else "none",
            warnings=warnings,
            due_recommendation_ids=due_recommendation_ids,
        )

    if provider == "local_json":
        if not history:
            warnings.append("performance_price_history_path_missing")
        return PriceHistoryLoadResult(
            price_history=history,
            provider=provider,
            warnings=warnings,
            due_recommendation_ids=due_recommendation_ids,
        )

    if provider != "yfinance":
        warnings.append(f"performance_price_provider_unsupported:{provider}")
        return PriceHistoryLoadResult(
            price_history=history,
            provider=provider,
            warnings=warnings,
            due_recommendation_ids=due_recommendation_ids,
        )

    missing = [ticker for ticker in tickers if ticker not in {key.upper() for key in history}]
    if tickers and benchmark_ticker and BENCHMARK_KEY not in history:
        missing.append(str(benchmark_ticker).strip().upper())

    fetched, fetch_warnings = _fetch_yfinance_price_history(
        missing,
        benchmark_ticker=benchmark_ticker,
        lookback_days=lookback_days,
        asof_date=asof_date,
    )
    history.update(fetched)
    warnings.extend(fetch_warnings)
    return PriceHistoryLoadResult(
        price_history=history,
        provider=provider,
        warnings=warnings,
        due_recommendation_ids=due_recommendation_ids,
    )


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


def _recommendations_due_for_refresh(
    db_path: Path,
    *,
    market: str | None = None,
    asof_date: str | None = None,
    refresh_window_days: int = 120,
) -> tuple[list[str], tuple[int, ...], list[str]]:
    if not Path(db_path).exists():
        return [], (), []
    target_market = _normalize_target_market(market)
    cutoff_date = _refresh_cutoff_date(asof_date, refresh_window_days)
    with sqlite3.connect(db_path) as conn:
        columns = _table_columns(conn, "action_recommendations")
        if cutoff_date:
            market_column = ", r.market" if "market" in columns else ""
            rows = conn.execute(
                f"""
                SELECT r.id, r.ticker{market_column}
                FROM action_recommendations r
                LEFT JOIN action_outcomes o ON o.recommendation_id = r.id
                WHERE substr(r.created_at, 1, 10) >= ?
                  AND (
                    o.recommendation_id IS NULL
                    OR COALESCE(o.calculation_version, 1) < ?
                    OR (
                      o.return_60d IS NULL
                      AND substr(COALESCE(o.updated_at, ''), 1, 10) < ?
                    )
                  )
                ORDER BY r.ticker
                """,
                (cutoff_date, OUTCOME_CALCULATION_VERSION, str(asof_date)[:10]),
            ).fetchall()
        elif "market" in columns:
            rows = conn.execute("SELECT id, ticker, market FROM action_recommendations ORDER BY ticker").fetchall()
        else:
            rows = conn.execute("SELECT id, ticker FROM action_recommendations ORDER BY ticker").fetchall()
    tickers: list[str] = []
    seen_tickers: set[str] = set()
    due_recommendation_ids: list[int] = []
    seen_recommendation_ids: set[int] = set()
    skipped = 0
    for row in rows:
        recommendation_id = int(row[0])
        ticker = str(row[1]).strip().upper()
        if not ticker:
            continue
        row_market = str(row[2]).strip().upper() if len(row) > 2 and row[2] else None
        inferred_market = normalize_market(row_market, ticker=ticker)
        if target_market and inferred_market != target_market:
            skipped += 1
            continue
        if recommendation_id not in seen_recommendation_ids:
            due_recommendation_ids.append(recommendation_id)
            seen_recommendation_ids.add(recommendation_id)
        if ticker not in seen_tickers:
            tickers.append(ticker)
            seen_tickers.add(ticker)
    warnings = (
        [f"performance_price_history_market_filter:{target_market}:skipped={skipped}"]
        if target_market and skipped
        else []
    )
    return tickers, tuple(due_recommendation_ids), warnings


def _refresh_cutoff_date(asof_date: str | None, refresh_window_days: int) -> str | None:
    text = str(asof_date or "").strip()[:10]
    if not text:
        return None
    try:
        parsed = date.fromisoformat(text)
    except ValueError:
        return None
    return (parsed - timedelta(days=max(1, int(refresh_window_days or 1)))).isoformat()


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
    request_tickers: str | list[str] = unique_tickers[0] if len(unique_tickers) == 1 else unique_tickers
    try:
        data = yf.download(
            request_tickers,
            period=f"{max(1, int(lookback_days))}d",
            progress=False,
            auto_adjust=False,
            threads=True,
            timeout=10,
            group_by="column",
            multi_level_index=True,
        )
    except Exception as exc:  # pragma: no cover - network/provider dependent
        return {}, [f"performance_yfinance_batch_fetch_failed:{exc}"]
    if data is None or getattr(data, "empty", True):
        return {}, [f"performance_yfinance_no_data:{ticker}" for ticker in unique_tickers]

    strict_ticker_match = len(unique_tickers) > 1
    for ticker in unique_tickers:
        close = _extract_close_series(
            data,
            ticker,
            allow_single_column_fallback=not strict_ticker_match,
        )
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


def _extract_close_series(
    data: Any,
    ticker: str,
    *,
    allow_single_column_fallback: bool = True,
) -> Any | None:
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
        if allow_single_column_fallback and len(non_empty_columns) == 1:
            return non_empty[non_empty_columns[0]]
        if allow_single_column_fallback and len(columns) == 1:
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
