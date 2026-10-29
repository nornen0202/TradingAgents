from __future__ import annotations

import json
import math
import sqlite3
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Mapping

from tradingagents.external.prism_normalize import normalize_market
from tradingagents.performance.models import OUTCOME_CALCULATION_VERSION
from tradingagents.performance.lifecycle import timestamp


BENCHMARK_KEY = "__BENCHMARK__"


@dataclass(frozen=True)
class PriceHistoryLoadResult:
    price_history: dict[str, Any] = field(default_factory=dict)
    provider: str = "none"
    warnings: list[str] = field(default_factory=list)
    due_recommendation_ids: tuple[int, ...] = ()
    required_tickers: tuple[str, ...] = ()

    @property
    def has_prices(self) -> bool:
        return any(key != BENCHMARK_KEY and values for key, values in self.price_history.items())

    @property
    def missing_price_tickers(self) -> tuple[str, ...]:
        return tuple(ticker for ticker in self.required_tickers if not self.price_history.get(ticker))

    @property
    def price_coverage_complete(self) -> bool:
        return (not self.due_recommendation_ids or bool(self.required_tickers)) and not self.missing_price_tickers

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
    lower, cutoff = _history_window(asof_date, lookback_days)
    provider = str(provider or "none").strip().lower()
    warnings: list[str] = []
    history: dict[str, Any] = {}

    if price_history_path:
        local_payload = _load_price_history_json(Path(price_history_path), benchmark_ticker=benchmark_ticker)
        history.update(_bounded_history(local_payload.price_history, lower=lower, cutoff=cutoff))
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
            required_tickers=tuple(tickers),
        )

    if provider == "local_json":
        if not history:
            warnings.append("performance_price_history_path_missing")
        return PriceHistoryLoadResult(
            price_history=history,
            provider=provider,
            warnings=warnings,
            due_recommendation_ids=due_recommendation_ids,
            required_tickers=tuple(tickers),
        )

    if provider != "yfinance":
        warnings.append(f"performance_price_provider_unsupported:{provider}")
        return PriceHistoryLoadResult(
            price_history=history,
            provider=provider,
            warnings=warnings,
            due_recommendation_ids=due_recommendation_ids,
            required_tickers=tuple(tickers),
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
        required_tickers=tuple(tickers),
    )


def _history_window(asof_date: str | None, lookback_days: int) -> tuple[date, date]:
    text = str(asof_date or "").strip()
    try:
        cutoff = date.fromisoformat(text)
    except ValueError:
        raise ValueError("An explicit ISO analysis date is required for performance prices") from None
    if cutoff.isoformat() != text:
        raise ValueError("An explicit ISO analysis date is required for performance prices")
    return cutoff - timedelta(days=max(1, int(lookback_days))), cutoff


def _bounded_history(payload: Mapping[str, Any], *, lower: date, cutoff: date) -> dict[str, Any]:
    # Reuse the outcome validator, including availability clocks and conflicting
    # duplicate dates. Import lazily because outcomes imports BENCHMARK_KEY.
    from tradingagents.performance.action_outcomes import _normalize_price_history

    normalized = _normalize_price_history(payload, asof_date=cutoff.isoformat())
    history: dict[str, Any] = {}
    for ticker, raw in payload.items():
        key = str(ticker).upper()
        allowed = {day: value for day, value in normalized.get(key, [])
                   if lower.isoformat() <= day <= cutoff.isoformat()}
        values = raw.get("prices") if isinstance(raw, Mapping) else raw
        if not allowed or not isinstance(values, list):
            continue
        rows = {}
        for item in values:
            validated = _normalize_price_history({key: [item]}, asof_date=cutoff.isoformat()).get(key, [])
            for day, value in validated:
                if allowed.get(day) == value and day not in rows:
                    # Keep original observation/settlement clocks for any later
                    # consumer applying an earlier cutoff to this same payload.
                    row = dict(item) if isinstance(item, Mapping) else {}
                    rows[day] = {**row, "date": day, "close": value}
        if rows:
            history[key] = [rows[day] for day in sorted(rows)]
    return history


def load_price_history_json(
    path: str | Path,
    *,
    benchmark_ticker: str | None = None,
    asof_date: str | None = None,
    lookback_days: int = 120,
) -> PriceHistoryLoadResult:
    lower, cutoff = _history_window(asof_date, lookback_days)
    raw = _load_price_history_json(Path(path), benchmark_ticker=benchmark_ticker)
    return PriceHistoryLoadResult(price_history=_bounded_history(raw.price_history, lower=lower, cutoff=cutoff),
                                  provider=raw.provider, warnings=raw.warnings)


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
    _, analysis_date = _history_window(asof_date, refresh_window_days)
    target_market = _normalize_target_market(market)
    cutoff_date = _refresh_cutoff_date(asof_date, refresh_window_days)
    with sqlite3.connect(db_path) as conn:
        columns = _table_columns(conn, "action_recommendations")
        if cutoff_date:
            market_column = "r.market" if "market" in columns else "NULL"
            rows = conn.execute(
                f"""
                SELECT r.id, r.ticker, {market_column}, r.created_at
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
    tickers: list[str] = []
    seen_tickers: set[str] = set()
    due_recommendation_ids: list[int] = []
    seen_recommendation_ids: set[int] = set()
    skipped = 0
    invalid_clock = 0
    upper = timestamp(analysis_date.isoformat() + "T23:59:59.999999+00:00")
    for row in rows:
        created_at = str(row[3] or "")
        try:
            known = timestamp(created_at if "T" in created_at else created_at + "T23:59:59.999999+00:00")
            if known > upper or not cutoff_date <= known.date().isoformat() <= analysis_date.isoformat():
                invalid_clock += 1
                continue
        except ValueError:
            invalid_clock += 1
            continue
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
    if invalid_clock:
        warnings.append(f"performance_price_history_excluded_recommendation_clock:{invalid_clock}")
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
    lower, cutoff = _history_window(asof_date, lookback_days)
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
            start=lower.isoformat(),
            end=(cutoff + timedelta(days=1)).isoformat(),
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

    for ticker in unique_tickers:
        close = _extract_close_series(
            data,
            ticker,
            allow_single_column_fallback=False,
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
            try:
                date_text = str(getattr(index, "date", lambda: index)())
                day = date.fromisoformat(date_text)
                if day.isoformat() != date_text or not lower <= day <= cutoff:
                    continue
            except (ValueError, TypeError, OverflowError):
                continue
            rows.append({"date": day.isoformat(), "close": close_value})
        if rows:
            history[ticker.upper()] = rows
            if ticker == benchmark:
                history[BENCHMARK_KEY] = rows
        else:
            warnings.append(f"performance_yfinance_empty_close:{ticker}")
    history = _bounded_history(history, lower=lower, cutoff=cutoff)
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
    if value in (None, "") or isinstance(value, bool):
        return None
    if hasattr(value, "item"):
        try:
            value = value.item()
        except Exception:
            return None
    try:
        if isinstance(value, bool):
            return None
        number = float(value)
        return number if math.isfinite(number) and number > 0 else None
    except (TypeError, ValueError):
        return None
