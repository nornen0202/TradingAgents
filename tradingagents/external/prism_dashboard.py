from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import requests

from .prism_models import PrismExternalSignal, PrismIngestionResult, PrismSourceKind
from .prism_normalize import (
    canonicalize_ticker,
    coerce_float,
    coerce_int,
    coerce_unit_interval,
    first_non_empty,
    json_safe,
    normalize_action,
    normalize_market,
    optional_text,
    parse_datetime,
    payload_hash,
)


DASHBOARD_CANDIDATE_PATHS = (
    "/dashboard_data.json",
    "/data/dashboard_data.json",
    "/api/dashboard",
    "/api/dashboard_data",
)

_SECTION_KEYS = {
    "portfolio",
    "real_portfolio",
    "holdings",
    "stock_holdings",
    "account_summary",
    "account",
    "cash_summary",
    "trading_history",
    "trades",
    "history",
    "watchlist_history",
    "watchlist",
    "candidates",
    "holding_decisions",
    "sell_decisions",
    "decisions",
    "performance",
    "performance_analysis",
    "trigger_performance",
    "missed_opportunities",
    "avoided_losses",
    "journal_entries",
    "trading_journal",
    "principles",
    "trading_principles",
    "trading_intuitions",
    "signals",
    "recommendations",
    "buy_candidates",
    "sell_candidates",
}
_PORTFOLIO_KEYS = {"portfolio", "real_portfolio", "holdings", "stock_holdings", "account_summary", "account", "cash_summary"}
_PERFORMANCE_KEYS = {"performance", "performance_analysis", "trigger_performance", "missed_opportunities", "avoided_losses"}
_JOURNAL_KEYS = {"journal_entries", "trading_journal", "principles", "trading_principles", "trading_intuitions"}
_TICKER_KEYS = ("ticker", "symbol", "canonical_ticker", "stock_code", "stockCode", "code", "종목코드")
_NAME_KEYS = ("display_name", "name", "stock_name", "stockName", "company_name", "종목명")
_ACTION_KEYS = ("action", "decision", "signal", "recommendation", "trade_type", "side", "status")
_CONFIDENCE_KEYS = ("confidence", "confidence_score", "probability", "conviction")
_COMPOSITE_SCORE_KEYS = ("composite_score", "final_score", "buy_score", "rank_score", "performance_score", "score")
_TRIGGER_SCORE_KEYS = ("trigger_score", "score", "signal_score")
_AGENT_FIT_KEYS = ("agent_fit_score", "fit_score", "ta_fit_score")
_TRIGGER_KEYS = ("trigger_type", "trigger", "strategy", "category", "signal_type")
_STOP_KEYS = ("stop_loss_price", "stop_loss", "stopLoss", "stopLossPrice", "cut_loss_price")
_TARGET_KEYS = ("target_price", "target", "take_profit_price", "profit_target")
_PRICE_KEYS = ("current_price", "price", "market_price", "close", "last_price")
_AVG_COST_KEYS = ("avg_cost", "average_cost", "avg_buy_price", "매입단가")
_QTY_KEYS = ("quantity", "qty", "shares", "보유수량")
_VALUE_KEYS = ("position_value", "market_value", "value", "평가금액")
_PNL_KEYS = ("pnl_pct", "return_pct", "profit_rate", "unrealized_return_pct", "수익률")
_RR_KEYS = ("risk_reward_ratio", "reward_risk", "rr", "r_multiple")
_REALIZED_KEYS = ("realized_return_pct", "realized_return", "profit_pct", "closed_return_pct")
_HOLDING_DAYS_KEYS = ("holding_days", "days_held", "holding_period_days")
_WIN_RATE_KEYS = ("win_rate_30d_by_trigger", "trigger_win_rate_30d", "win_rate_30d")
_AVG_RETURN_KEYS = ("avg_30d_return_by_trigger", "trigger_avg_return_30d", "avg_return_30d")
_REASON_KEYS = ("rationale", "reason", "summary", "comment", "note", "one_line_summary")
_ASOF_KEYS = ("asof", "as_of", "updated_at", "created_at", "date", "timestamp")


def load_dashboard_json_file(
    path: str | Path,
    *,
    market: str | None = None,
    source_kind: PrismSourceKind = PrismSourceKind.DASHBOARD_JSON,
) -> PrismIngestionResult:
    ingested_at = datetime.now().astimezone()
    source = Path(path).expanduser()
    if not source.exists():
        return PrismIngestionResult(
            enabled=True,
            ok=False,
            source_kind=source_kind,
            source=source.as_posix(),
            ingested_at=ingested_at,
            warnings=[f"dashboard_json_missing:{source}"],
        )
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except Exception as exc:
        return PrismIngestionResult(
            enabled=True,
            ok=False,
            source_kind=source_kind,
            source=source.as_posix(),
            ingested_at=ingested_at,
            warnings=[f"dashboard_json_invalid:{source}:{exc}"],
        )
    return parse_dashboard_payload(
        payload,
        source_kind=source_kind,
        source=source.as_posix(),
        market=market,
        ingested_at=ingested_at,
    )


def fetch_dashboard_json_url(
    url: str,
    *,
    timeout_seconds: float = 5.0,
    max_payload_bytes: int = 5_000_000,
    market: str | None = None,
) -> PrismIngestionResult:
    ingested_at = datetime.now().astimezone()
    try:
        response = requests.get(url, timeout=timeout_seconds, stream=True)
        response.raise_for_status()
        content_type = str(response.headers.get("content-type") or "").lower()
        if content_type and "json" not in content_type and "text/plain" not in content_type:
            return PrismIngestionResult(
                enabled=True,
                ok=False,
                source_kind=PrismSourceKind.DASHBOARD_LIVE,
                source=url,
                ingested_at=ingested_at,
                warnings=[f"dashboard_http_unsupported_content_type:{content_type}"],
            )
        chunks: list[bytes] = []
        total = 0
        for chunk in response.iter_content(chunk_size=65536):
            total += len(chunk)
            if total > max_payload_bytes:
                return PrismIngestionResult(
                    enabled=True,
                    ok=False,
                    source_kind=PrismSourceKind.DASHBOARD_LIVE,
                    source=url,
                    ingested_at=ingested_at,
                    warnings=[f"dashboard_http_payload_too_large:{total}>{max_payload_bytes}"],
                )
            chunks.append(chunk)
        payload = json.loads(b"".join(chunks).decode(response.encoding or "utf-8"))
    except Exception as exc:
        return PrismIngestionResult(
            enabled=True,
            ok=False,
            source_kind=PrismSourceKind.DASHBOARD_LIVE,
            source=url,
            ingested_at=ingested_at,
            warnings=[f"dashboard_http_unavailable:{url}:{exc}"],
        )
    return parse_dashboard_payload(
        payload,
        source_kind=PrismSourceKind.DASHBOARD_LIVE,
        source=url,
        market=market,
        ingested_at=ingested_at,
    )


def candidate_dashboard_urls(base_url: str) -> tuple[str, ...]:
    base = str(base_url or "").strip().rstrip("/")
    if not base:
        return tuple()
    return tuple(f"{base}{path}" for path in DASHBOARD_CANDIDATE_PATHS)


def parse_dashboard_payload(
    payload: Any,
    *,
    source_kind: PrismSourceKind,
    source: str | None = None,
    market: str | None = None,
    ingested_at: datetime | None = None,
) -> PrismIngestionResult:
    ingested_at = ingested_at or datetime.now().astimezone()
    warnings: list[str] = []
    signals: list[PrismExternalSignal] = []
    seen: set[tuple[str, str, str | None]] = set()

    for section, item in _iter_signal_records(payload):
        signal = _build_signal(
            item,
            section=section,
            source_kind=source_kind,
            source=source,
            default_market=market,
            ingested_at=ingested_at,
            warnings=warnings,
        )
        if signal is None:
            continue
        key = (signal.canonical_ticker, signal.signal_action.value, signal.trigger_type)
        if key in seen:
            continue
        seen.add(key)
        signals.append(signal)

    if not signals:
        warnings.append("no_ticker_level_prism_signals_found")
    portfolio_snapshot = _collect_named_sections(payload, _PORTFOLIO_KEYS)
    performance_summary = _collect_named_sections(payload, _PERFORMANCE_KEYS)
    journal_lessons = _collect_journal_lessons(payload)
    return PrismIngestionResult(
        enabled=True,
        ok=True,
        source_kind=source_kind,
        source=source,
        ingested_at=ingested_at,
        signals=signals,
        portfolio_snapshot=portfolio_snapshot or None,
        performance_summary=performance_summary or None,
        journal_lessons=journal_lessons,
        warnings=warnings,
        raw_payload_hash=payload_hash(payload),
    )


def _iter_signal_records(payload: Any, *, section: str = "root", depth: int = 0) -> Iterable[tuple[str, dict[str, Any]]]:
    if depth > 5:
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
    source_kind: PrismSourceKind,
    source: str | None,
    default_market: str | None,
    ingested_at: datetime,
    warnings: list[str],
) -> PrismExternalSignal | None:
    stock = item.get("stock") or item.get("instrument") or item.get("company")
    merged = dict(item)
    if isinstance(stock, dict):
        for key, value in stock.items():
            merged.setdefault(str(key), value)

    display_name = optional_text(first_non_empty(merged, _NAME_KEYS))
    raw_ticker = first_non_empty(merged, _TICKER_KEYS)
    ticker = canonicalize_ticker(raw_ticker, display_name=display_name, market=default_market)
    if not ticker:
        warnings.append(f"{section}:missing_ticker")
        return None
    row_warnings: list[str] = []
    market = normalize_market(merged.get("market") or default_market, ticker=ticker)
    action = normalize_action(first_non_empty(merged, _ACTION_KEYS), section=section)
    source_asof = parse_datetime(first_non_empty(merged, _ASOF_KEYS))
    trigger_type = optional_text(first_non_empty(merged, _TRIGGER_KEYS))
    confidence = coerce_unit_interval(first_non_empty(merged, _CONFIDENCE_KEYS))
    composite_score = coerce_unit_interval(first_non_empty(merged, _COMPOSITE_SCORE_KEYS))
    trigger_score = coerce_unit_interval(first_non_empty(merged, _TRIGGER_SCORE_KEYS))
    if confidence is None and composite_score is not None:
        confidence = composite_score
    tags = _tags(section, trigger_type, merged)

    return PrismExternalSignal(
        canonical_ticker=ticker,
        display_name=display_name,
        market=market,  # type: ignore[arg-type]
        source_kind=source_kind,
        source_path_or_url=source,
        source_asof=source_asof,
        ingested_at=ingested_at,
        signal_action=action,
        trigger_type=trigger_type,
        trigger_score=trigger_score,
        composite_score=composite_score,
        agent_fit_score=coerce_unit_interval(first_non_empty(merged, _AGENT_FIT_KEYS)),
        risk_reward_ratio=coerce_float(first_non_empty(merged, _RR_KEYS)),
        stop_loss_price=coerce_float(first_non_empty(merged, _STOP_KEYS)),
        target_price=coerce_float(first_non_empty(merged, _TARGET_KEYS)),
        confidence=confidence,
        rationale=optional_text(first_non_empty(merged, _REASON_KEYS)),
        tags=tags,
        current_price=coerce_float(first_non_empty(merged, _PRICE_KEYS)),
        avg_cost=coerce_float(first_non_empty(merged, _AVG_COST_KEYS)),
        quantity=coerce_float(first_non_empty(merged, _QTY_KEYS)),
        position_value=coerce_float(first_non_empty(merged, _VALUE_KEYS)),
        pnl_pct=coerce_float(first_non_empty(merged, _PNL_KEYS)),
        realized_return_pct=coerce_float(first_non_empty(merged, _REALIZED_KEYS)),
        holding_days=coerce_int(first_non_empty(merged, _HOLDING_DAYS_KEYS)),
        win_rate_30d_by_trigger=coerce_unit_interval(first_non_empty(merged, _WIN_RATE_KEYS)),
        avg_30d_return_by_trigger=coerce_float(first_non_empty(merged, _AVG_RETURN_KEYS)),
        raw=json_safe({"section": section, "payload": item}),
        warnings=row_warnings,
    )


def _tags(section: str, trigger_type: str | None, item: dict[str, Any]) -> tuple[str, ...]:
    values = [section]
    if trigger_type:
        values.append(trigger_type)
    for key in ("sector", "theme", "market_regime", "trigger_group"):
        value = optional_text(item.get(key))
        if value:
            values.append(value)
    return tuple(dict.fromkeys(str(value) for value in values if value))


def _collect_named_sections(payload: Any, names: set[str]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    if not isinstance(payload, dict):
        return result
    for key, value in payload.items():
        key_text = str(key)
        if key_text.lower() in names:
            result[key_text] = json_safe(value)
    return result


def _collect_journal_lessons(payload: Any) -> list[dict[str, Any]]:
    sections = _collect_named_sections(payload, _JOURNAL_KEYS)
    lessons: list[dict[str, Any]] = []
    for section, value in sections.items():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    lessons.append({"section": section, **item})
        elif isinstance(value, dict):
            lessons.append({"section": section, **value})
    return lessons
