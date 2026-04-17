from __future__ import annotations

import os

from tradingagents.schemas import IntradayMarketSnapshot

from .intraday.providers import get_intraday_provider


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
            return get_intraday_provider(provider_name).fetch(
                ticker,
                interval=interval,
                market_timezone=market_tz,
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
