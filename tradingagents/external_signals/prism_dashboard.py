from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import requests

from .models import ExternalSignal, ExternalSignalIngestion, ExternalSignalSource
from .validation import (
    canonicalize_ticker,
    coerce_confidence,
    coerce_float,
    coerce_score,
    first_non_empty,
    normalize_external_action,
)


DEFAULT_DASHBOARD_URLS = (
    "https://analysis.stocksimulation.kr/dashboard_data.json",
    "https://analysis.stocksimulation.kr/data/dashboard_data.json",
)

_SECTION_KEYS = {
    "holdings",
    "stock_holdings",
    "portfolio",
    "positions",
    "trading_history",
    "trades",
    "watchlist",
    "watchlist_history",
    "holding_decisions",
    "decisions",
    "signals",
    "recommendations",
    "buy_candidates",
    "sell_candidates",
    "trigger_performance",
    "missed_opportunities",
    "avoided_losses",
    "trading_principles",
    "trading_intuitions",
    "action_performance_leaderboard",
    "action_leaderboard",
}

_TICKER_KEYS = (
    "ticker",
    "symbol",
    "canonical_ticker",
    "stock_code",
    "stockCode",
    "code",
    "종목코드",
)
_NAME_KEYS = ("display_name", "name", "stock_name", "stockName", "company_name", "종목명")
_ACTION_KEYS = ("action", "decision", "signal", "recommendation", "trade_type", "side", "status")
_CONFIDENCE_KEYS = ("confidence", "confidence_score", "probability", "conviction")
_SCORE_KEYS = ("score", "final_score", "buy_score", "rank_score", "performance_score")
_TRIGGER_KEYS = ("trigger_type", "trigger", "strategy", "category", "signal_type")
_STOP_KEYS = ("stop_loss_price", "stop_loss", "stopLoss", "stopLossPrice", "cut_loss_price")
_TARGET_KEYS = ("target_price", "target", "take_profit_price", "profit_target")
_PRICE_KEYS = ("current_price", "price", "market_price", "close", "last_price")
_REASON_KEYS = ("reason", "rationale", "summary", "comment", "note", "one_line_summary")
_ASOF_KEYS = ("asof", "as_of", "updated_at", "created_at", "date", "timestamp")


def load_prism_dashboard_signals(
    *,
    dashboard_url: str | None = None,
    local_json_path: str | None = None,
    sqlite_path: str | None = None,
    market: str | None = None,
) -> list[ExternalSignal]:
    return list(
        load_prism_dashboard_signals_with_status(
            dashboard_url=dashboard_url,
            local_json_path=local_json_path,
            sqlite_path=sqlite_path,
            market=market,
        ).signals
    )


def load_prism_dashboard_signals_with_status(
    *,
    dashboard_url: str | None = None,
    local_json_path: str | None = None,
    sqlite_path: str | None = None,
    market: str | None = None,
) -> ExternalSignalIngestion:
    warnings: list[str] = []
    attempted: list[str] = []
    asof = datetime.now().astimezone().isoformat()

    url_candidates = _url_candidates(dashboard_url, local_json_path=local_json_path, sqlite_path=sqlite_path)
    for url in url_candidates:
        attempted.append(f"url:{url}")
        try:
            payload = _fetch_json_url(url)
            signals, parse_warnings = parse_prism_dashboard_payload(
                payload,
                source=ExternalSignalSource.PRISM_DASHBOARD,
                market=market,
            )
            warnings.extend(parse_warnings)
            return ExternalSignalIngestion(
                source=ExternalSignalSource.PRISM_DASHBOARD,
                status="ok",
                asof=asof,
                signals=tuple(signals),
                warnings=tuple(warnings),
                attempted_sources=tuple(attempted),
                selected_source=url,
            )
        except Exception as exc:
            warnings.append(f"dashboard_url_unavailable:{url}:{exc}")

    if local_json_path:
        path = Path(local_json_path).expanduser()
        attempted.append(f"local_json:{path}")
        if path.exists():
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
                signals, parse_warnings = parse_prism_dashboard_payload(
                    payload,
                    source=ExternalSignalSource.PRISM_LOCAL_JSON,
                    market=market,
                )
                warnings.extend(parse_warnings)
                return ExternalSignalIngestion(
                    source=ExternalSignalSource.PRISM_LOCAL_JSON,
                    status="ok",
                    asof=asof,
                    signals=tuple(signals),
                    warnings=tuple(warnings),
                    attempted_sources=tuple(attempted),
                    selected_source=path.as_posix(),
                )
            except Exception as exc:
                warnings.append(f"local_json_parse_failed:{path}:{exc}")
        else:
            warnings.append(f"local_json_missing:{path}")

    if sqlite_path:
        path = Path(sqlite_path).expanduser()
        attempted.append(f"sqlite:{path}")
        if path.exists():
            try:
                payload = _load_sqlite_payload(path)
                signals, parse_warnings = parse_prism_dashboard_payload(
                    payload,
                    source=ExternalSignalSource.PRISM_SQLITE,
                    market=market,
                )
                warnings.extend(parse_warnings)
                return ExternalSignalIngestion(
                    source=ExternalSignalSource.PRISM_SQLITE,
                    status="ok",
                    asof=asof,
                    signals=tuple(signals),
                    warnings=tuple(warnings),
                    attempted_sources=tuple(attempted),
                    selected_source=path.as_posix(),
                )
            except Exception as exc:
                warnings.append(f"sqlite_parse_failed:{path}:{exc}")
        else:
            warnings.append(f"sqlite_missing:{path}")

    return ExternalSignalIngestion(
        source=None,
        status="unavailable",
        asof=asof,
        signals=tuple(),
        warnings=tuple(warnings or ["no_external_signal_source_available"]),
        attempted_sources=tuple(attempted),
        selected_source=None,
    )


def load_manual_json_signals(path: str | Path, *, market: str | None = None) -> list[ExternalSignal]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    signals, _warnings = parse_prism_dashboard_payload(
        payload,
        source=ExternalSignalSource.MANUAL_JSON,
        market=market,
    )
    return signals


def parse_prism_dashboard_payload(
    payload: Any,
    *,
    source: ExternalSignalSource,
    market: str | None = None,
) -> tuple[list[ExternalSignal], list[str]]:
    warnings: list[str] = []
    signals: list[ExternalSignal] = []
    seen: set[tuple[str, str, str | None]] = set()

    for section, item in _iter_signal_records(payload):
        signal = _build_signal(item, section=section, source=source, market=market, warnings=warnings)
        if signal is None:
            continue
        key = (signal.ticker, signal.action.value, signal.trigger_type)
        if key in seen:
            continue
        seen.add(key)
        signals.append(signal)

    if not signals:
        warnings.append("no_ticker_level_external_signals_found")
    return signals, warnings


def _url_candidates(
    dashboard_url: str | None,
    *,
    local_json_path: str | None,
    sqlite_path: str | None,
) -> tuple[str, ...]:
    if dashboard_url is not None:
        text = str(dashboard_url).strip()
        return (text,) if text else tuple()
    return tuple()


def _fetch_json_url(url: str) -> Any:
    response = requests.get(url, timeout=8)
    response.raise_for_status()
    return response.json()


def _load_sqlite_payload(path: Path) -> dict[str, Any]:
    wanted = {
        "stock_holdings",
        "trading_history",
        "watchlist_history",
        "holding_decisions",
        "trigger_performance",
        "missed_opportunities",
        "avoided_losses",
        "trading_principles",
        "trading_intuitions",
        "action_performance_leaderboard",
    }
    payload: dict[str, Any] = {}
    with sqlite3.connect(path) as conn:
        conn.row_factory = sqlite3.Row
        tables = {
            str(row["name"])
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            if row["name"]
        }
        for table in sorted(tables & wanted):
            payload[table] = [dict(row) for row in conn.execute(f'SELECT * FROM "{table}"')]
    return payload


def _iter_signal_records(payload: Any, *, section: str = "root", depth: int = 0) -> Iterable[tuple[str, dict[str, Any]]]:
    if depth > 4:
        return
    if isinstance(payload, list):
        for item in payload:
            yield from _iter_signal_records(item, section=section, depth=depth + 1)
        return
    if not isinstance(payload, dict):
        return

    if _looks_like_signal_record(payload):
        yield section, payload

    for key, value in payload.items():
        key_text = str(key)
        key_lower = key_text.lower()
        should_descend = key_lower in _SECTION_KEYS or depth < 2
        if should_descend and isinstance(value, (dict, list)):
            yield from _iter_signal_records(value, section=key_text, depth=depth + 1)


def _looks_like_signal_record(item: dict[str, Any]) -> bool:
    if any(key in item for key in _TICKER_KEYS):
        return True
    stock = item.get("stock") or item.get("instrument") or item.get("company")
    return isinstance(stock, dict) and any(key in stock for key in _TICKER_KEYS)


def _build_signal(
    item: dict[str, Any],
    *,
    section: str,
    source: ExternalSignalSource,
    market: str | None,
    warnings: list[str],
) -> ExternalSignal | None:
    stock = item.get("stock") or item.get("instrument") or item.get("company")
    merged = dict(item)
    if isinstance(stock, dict):
        for key, value in stock.items():
            merged.setdefault(str(key), value)

    display_name = _optional_text(first_non_empty(merged, _NAME_KEYS))
    raw_ticker = first_non_empty(merged, _TICKER_KEYS)
    ticker = canonicalize_ticker(raw_ticker, display_name=display_name, market=market)
    if not ticker:
        warnings.append(f"{section}:missing_ticker")
        return None

    action = normalize_external_action(first_non_empty(merged, _ACTION_KEYS), section=section)
    trigger_type = _optional_text(first_non_empty(merged, _TRIGGER_KEYS))
    asof = _optional_text(first_non_empty(merged, _ASOF_KEYS)) or datetime.now().astimezone().isoformat()
    tags = _tags(section, trigger_type, merged)
    return ExternalSignal(
        source=source,
        ticker=ticker,
        display_name=display_name,
        market=_optional_text(merged.get("market")) or market,
        action=action,
        confidence=coerce_confidence(first_non_empty(merged, _CONFIDENCE_KEYS)),
        trigger_type=trigger_type,
        score=coerce_score(first_non_empty(merged, _SCORE_KEYS)),
        stop_loss_price=coerce_float(first_non_empty(merged, _STOP_KEYS)),
        target_price=coerce_float(first_non_empty(merged, _TARGET_KEYS)),
        current_price=coerce_float(first_non_empty(merged, _PRICE_KEYS)),
        reason=_optional_text(first_non_empty(merged, _REASON_KEYS)),
        tags=tags,
        asof=asof,
        raw=_json_safe({"section": section, "payload": item}),
    )


def _optional_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _tags(section: str, trigger_type: str | None, item: dict[str, Any]) -> tuple[str, ...]:
    values = [section]
    if trigger_type:
        values.append(trigger_type)
    for key in ("sector", "theme", "market_regime", "trigger_group"):
        value = _optional_text(item.get(key))
        if value:
            values.append(value)
    return tuple(dict.fromkeys(str(value) for value in values if value))


def _json_safe(value: Any) -> Any:
    try:
        json.dumps(value, ensure_ascii=False)
        return value
    except TypeError:
        if isinstance(value, dict):
            return {str(key): _json_safe(item) for key, item in value.items()}
        if isinstance(value, list):
            return [_json_safe(item) for item in value]
        if isinstance(value, tuple):
            return [_json_safe(item) for item in value]
        return str(value)
