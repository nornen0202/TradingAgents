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
    checkpoint_id: str | None = None,
) -> IntradayMarketSnapshot:
    """Fetch a classified intraday snapshot through the configured provider chain.

    Default US and KR chains prefer KIS and allow a delayed Yahoo reference.
    Fallback provenance is retained; obtaining a price does not make delayed
    data execution-ready. An explicit provider selection remains authoritative.
    """

    from datetime import datetime, timezone
    from .config import get_config
    from .integrity import parse_analysis_cutoff
    from .intraday.providers import require_live_intraday_clock
    from .market_policy import aware_datetime
    from .vendor_exceptions import VendorUnavailableError

    market_tz = market_timezone or _default_market_timezone(ticker)
    requested_as_of = get_config().get("analysis_as_of")
    requested_cutoff = parse_analysis_cutoff(requested_as_of, market_tz) if requested_as_of else None
    live_only_providers = {"kis", "kis_quote", "kis_microstructure", "kis_us_microstructure"}
    provider_chain = _provider_chain(ticker=ticker, provider=provider)
    last_exc: Exception | None = None
    failures: dict[str, str] = {}
    for provider_name in provider_chain:
        is_kis = provider_name.strip().lower() in live_only_providers
        try:
            if requested_as_of and is_kis:
                require_live_intraday_clock(market_tz, provider_name=provider_name)
            snapshot = get_intraday_provider(provider_name).fetch(
                ticker,
                interval=interval,
                market_timezone=market_tz,
                checkpoint_id=checkpoint_id,
            )
            # A live event may occur during the request. Its receipt time bounds
            # it unless the caller supplied an earlier analysis cutoff.
            received_at = datetime.now(timezone.utc)
            cutoff = min(received_at, requested_cutoff) if requested_cutoff is not None else received_at
            snapshot_asof = aware_datetime(snapshot.asof)
            if snapshot_asof is None:
                raise VendorUnavailableError(f"Intraday provider '{provider_name}' omitted snapshot asof or supplied an invalid clock.")
            if snapshot_asof > cutoff:
                raise VendorUnavailableError(f"Intraday provider '{provider_name}' snapshot asof exceeds analysis_as_of.")
            return replace(
                snapshot,
                snapshot_received_at=received_at.isoformat() if is_kis else None,
                missing_reason={**snapshot.missing_reason, **failures},
                execution_data_quality=classify_execution_market_data(
                    snapshot,
                ),
            )
        except Exception as exc:
            last_exc = exc
            # Retain degraded-path provenance without logging provider messages
            # that may contain credentials, account identifiers or request URLs.
            failures[f"provider:{provider_name}"] = f"unavailable:{type(exc).__name__}"
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
        return ["kis_microstructure", "kis", "yfinance"]
    return ["kis_microstructure", "yfinance"]


def _default_market_timezone(ticker: str) -> str:
    return "Asia/Seoul" if _looks_like_kr_symbol(ticker) else "America/New_York"


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

    if not realtime:
        return DELAYED_ANALYSIS_ONLY
    if delay is not None and (delay < 0 or delay > max_delay):
        return STALE_INVALID_FOR_EXECUTION
    if regular_session and delay is not None:
        return REALTIME_EXECUTION_READY
    return DELAYED_ANALYSIS_ONLY


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
