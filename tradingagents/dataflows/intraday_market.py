from __future__ import annotations

from dataclasses import replace
import os
from typing import Any

from tradingagents.schemas import IntradayMarketSnapshot

from .intraday.providers import get_intraday_provider


REALTIME_EXECUTION_READY = "REALTIME_EXECUTION_READY"
DELAYED_ANALYSIS_ONLY = "DELAYED_ANALYSIS_ONLY"
STALE_INVALID_FOR_EXECUTION = "STALE_INVALID_FOR_EXECUTION"


def fetch_intraday_market_snapshot(
    ticker: str,
    *,
    interval: str = "5m",
    market_timezone: str | None = None,
    provider: str | None = None,
) -> IntradayMarketSnapshot:
    """Fetch an execution-grade intraday snapshot through the configured provider.

    KR symbols prefer KIS quotes when credentials and provider configuration are
    available, then fall back to yfinance so scheduled runs still produce an
    explicit degraded/freshness signal instead of failing silently.
    """

    market_tz = market_timezone or _default_market_timezone(ticker)
    provider_chain = _provider_chain(ticker=ticker, provider=provider)
    last_exc: Exception | None = None
    for provider_name in provider_chain:
        try:
            snapshot = get_intraday_provider(provider_name).fetch(
                ticker,
                interval=interval,
                market_timezone=market_tz,
            )
            return replace(
                snapshot,
                execution_data_quality=classify_execution_market_data(
                    snapshot,
                ),
            )
        except Exception as exc:
            last_exc = exc
            if provider_name == provider_chain[-1]:
                break
            continue
    if last_exc is not None:
        raise last_exc
    raise RuntimeError(f"No intraday provider was configured for {ticker}.")


def _provider_chain(*, ticker: str, provider: str | None) -> list[str]:
    configured = provider or os.getenv("TRADINGAGENTS_INTRADAY_PROVIDER") or ""
    if configured:
        values = [item.strip() for item in configured.split(",") if item.strip()]
        if values:
            return values
    if _looks_like_kr_symbol(ticker):
        return ["kis", "yfinance"]
    return ["yfinance"]


def _default_market_timezone(ticker: str) -> str:
    return "Asia/Seoul" if _looks_like_kr_symbol(ticker) else "US/Eastern"


def _looks_like_kr_symbol(ticker: str) -> bool:
    normalized = str(ticker or "").strip().upper()
    return normalized.endswith((".KS", ".KQ")) or (len(normalized) == 6 and normalized.isdigit())


def classify_execution_market_data(
    source: IntradayMarketSnapshot | dict[str, Any] | None = None,
    *,
    provider_realtime_capable: bool | None = None,
    quote_delay_seconds: int | None = None,
    market_session: str | None = None,
    data_health: str | None = None,
    max_quote_delay_seconds: int = 180,
) -> str:
    """Classify whether an intraday snapshot can be used for execution."""

    if isinstance(source, IntradayMarketSnapshot):
        explicit = str(source.execution_data_quality or "").strip().upper()
        if explicit in {REALTIME_EXECUTION_READY, DELAYED_ANALYSIS_ONLY, STALE_INVALID_FOR_EXECUTION}:
            return explicit
        provider_realtime_capable = source.provider_realtime_capable
        quote_delay_seconds = source.quote_delay_seconds
        market_session = source.market_session
    elif isinstance(source, dict):
        explicit = str(source.get("execution_data_quality") or "").strip().upper()
        if explicit in {REALTIME_EXECUTION_READY, DELAYED_ANALYSIS_ONLY, STALE_INVALID_FOR_EXECUTION}:
            return explicit
        provider_realtime_capable = _coerce_bool(source.get("provider_realtime_capable"))
        quote_delay_seconds = _coerce_int(source.get("quote_delay_seconds"))
        market_session = str(source.get("market_session") or "")
        data_health = data_health or str(source.get("data_health") or source.get("execution_data_quality") or "")

    health = str(data_health or "").strip().upper()
    if health in {"STALE", "UNAVAILABLE", "FAILED"}:
        return STALE_INVALID_FOR_EXECUTION

    session = str(market_session or "").strip().lower()
    regular_session = session in {"regular", "regular_session", "in_session"}
    delay = _coerce_int(quote_delay_seconds)
    realtime = bool(provider_realtime_capable)
    max_delay = max(int(max_quote_delay_seconds or 0), 0)

    if regular_session and realtime and delay is not None and delay <= max_delay:
        return REALTIME_EXECUTION_READY
    if not realtime:
        return DELAYED_ANALYSIS_ONLY
    if delay is None:
        return DELAYED_ANALYSIS_ONLY
    if delay > max_delay:
        return STALE_INVALID_FOR_EXECUTION
    return REALTIME_EXECUTION_READY


def _coerce_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {"true", "1", "yes"}:
        return True
    if text in {"false", "0", "no"}:
        return False
    return None


def _coerce_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
