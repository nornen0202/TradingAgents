from __future__ import annotations

from datetime import datetime, time, timedelta, timezone
import math
from typing import Protocol
from zoneinfo import ZoneInfo

import yfinance as yf
import pandas as pd

from tradingagents.schemas import IntradayMarketSnapshot

from ..stockstats_utils import yf_retry
from ..config import get_config


def _dated_bars(frame, cutoff, *, before_date=None, market_timezone="US/Eastern"):
    """Exclude unverifiable/future rows before any price or volume aggregate."""
    valid = []
    stamps = []
    for position, (index, row) in enumerate(frame.iterrows()):
        try:
            stamp = pd.Timestamp(index)
            if pd.isna(stamp) or stamp.tzinfo is None or stamp > cutoff:
                continue
            if before_date and stamp.tz_convert(market_timezone).date() >= before_date:
                continue
            values = {key: float(row[key]) for key in ("Close", "High", "Low", "Volume")}
            if (any(not math.isfinite(value) or value < 0 for value in values.values())
                    or values["Low"] <= 0 or not values["Low"] <= values["Close"] <= values["High"]):
                continue
        except (TypeError, ValueError, KeyError, OverflowError):
            continue
        valid.append(position)
        stamps.append(stamp.tz_convert("UTC"))
    result = frame.iloc[valid].copy()
    result.index = pd.DatetimeIndex(stamps)
    for column in ("Close", "High", "Low", "Volume"):
        if column in result:
            result[column] = pd.to_numeric(result[column], errors="raise")
    return result.sort_index().loc[lambda rows: ~rows.index.duplicated(keep=False)]


def _analysis_cutoff(market_timezone):
    cutoff = datetime.now(timezone.utc)
    requested = get_config().get("analysis_as_of")
    if requested:
        stamp = datetime.fromisoformat(str(requested).replace("Z", "+00:00"))
        if len(str(requested)) == 10:
            stamp = stamp.replace(tzinfo=ZoneInfo(market_timezone)) + timedelta(days=1) - timedelta(microseconds=1)
        elif stamp.tzinfo is None:
            raise ValueError("Intraday analysis cutoff requires a timezone")
        cutoff = min(cutoff, stamp)
    return cutoff


class IntradaySnapshotProvider(Protocol):
    name: str
    realtime_capable: bool

    def fetch(
        self,
        ticker: str,
        *,
        interval: str = "5m",
        market_timezone: str = "US/Eastern",
        checkpoint_id: str | None = None,
    ) -> IntradayMarketSnapshot:
        ...


class YFinanceIntradayProvider:
    name = "yfinance_intraday"
    realtime_capable = False

    def fetch(
        self,
        ticker: str,
        *,
        interval: str = "5m",
        market_timezone: str = "US/Eastern",
        checkpoint_id: str | None = None,
    ) -> IntradayMarketSnapshot:
        cutoff = _analysis_cutoff(market_timezone)
        ticker_obj = yf.Ticker(ticker)
        history = yf_retry(lambda: ticker_obj.history(period="1d", interval=interval, auto_adjust=False))
        if history.empty:
            raise RuntimeError(f"No intraday data available for ticker '{ticker}'.")

        history = _dated_bars(history, cutoff)
        if history.empty:
            raise RuntimeError(f"Intraday dataset for '{ticker}' is empty after cleanup.")

        # A reference snapshot describes one exchange-local day. Do not sum
        # previous sessions returned unexpectedly by the upstream API.
        latest_date = history.index[-1].tz_convert(market_timezone).date()
        history = history.loc[history.index.tz_convert(market_timezone).date == latest_date]
        closes = history["Close"]
        highs = history["High"]
        lows = history["Low"]
        volumes = history["Volume"]

        last_ts = history.index[-1].to_pydatetime()

        typical_price = (highs + lows + closes) / 3.0
        cumulative_volume = volumes.cumsum()
        vwap_series = ((typical_price * volumes).cumsum() / cumulative_volume).dropna()
        session_vwap = float(vwap_series.iloc[-1]) if not vwap_series.empty else None

        avg20_volume = None
        try:
            daily = yf_retry(lambda: ticker_obj.history(period="3mo", interval="1d", auto_adjust=False))
        except Exception:
            daily = None
        if daily is not None and not daily.empty and "Volume" in daily:
            daily = _dated_bars(daily, cutoff, before_date=latest_date, market_timezone=market_timezone)
            if not daily.empty:
                avg20_volume = float(daily["Volume"].tail(20).mean())

        intraday_volume = int(volumes.sum())
        intraday_trading_value = float((typical_price * volumes).sum())
        first_price = float(closes.iloc[0]) if not closes.empty else None
        price_change_pct = (
            float((float(closes.iloc[-1]) / first_price - 1.0) * 100.0)
            if first_price and first_price > 0
            else None
        )
        relative_volume = None
        if avg20_volume and avg20_volume > 0:
            progress = _session_progress_fraction(last_ts, market_timezone=market_timezone)
            adjusted_baseline = max(avg20_volume * progress, avg20_volume * 0.05)
            relative_volume = float(intraday_volume / adjusted_baseline)

        provider_timestamp = datetime.now(last_ts.tzinfo).isoformat()
        market = "KR" if market_timezone == "Asia/Seoul" else "US"
        missing_reason = {}
        halt_status = None
        investor_flow_status = None
        program_flow_status = None
        microstructure_required = False
        if market == "US":
            missing_reason = {
                "orderbook": "yfinance_does_not_provide_orderbook",
                "execution_strength": "yfinance_does_not_provide_trade_tape_strength",
                "halt_status": "yfinance_does_not_provide_halt_status",
            }
            halt_status = {"status": "unknown", "is_clear": False, "source": "not_provided"}
            investor_flow_status = "not_applicable"
            program_flow_status = "not_applicable"
            microstructure_required = True

        return IntradayMarketSnapshot(
            ticker=ticker,
            asof=last_ts.isoformat(),
            provider=self.name,
            interval=interval,
            last_price=float(closes.iloc[-1]),
            session_vwap=session_vwap,
            day_high=float(highs.max()),
            day_low=float(lows.min()),
            volume=intraday_volume,
            avg20_daily_volume=avg20_volume,
            relative_volume=relative_volume,
            trading_value=intraday_trading_value,
            price_change_pct=price_change_pct,
            bar_timestamp=last_ts.isoformat(),
            provider_timestamp=provider_timestamp,
            quote_delay_seconds=_delay_seconds(provider_timestamp, last_ts.isoformat()),
            provider_realtime_capable=self.realtime_capable,
            market_session=_market_session(last_ts, market_timezone=market_timezone),
            checkpoint_id=checkpoint_id,
            market=market,
            halt_status=halt_status,
            investor_flow_status=investor_flow_status,
            program_flow_status=program_flow_status,
            missing_reason=missing_reason,
            microstructure_required=microstructure_required,
            raw_source_names=("yfinance.history", "yfinance.daily_history"),
        )


def get_intraday_provider(name: str | None) -> IntradaySnapshotProvider:
    normalized = str(name or "yfinance").strip().lower()
    if normalized in {"yfinance", "yfinance_intraday"}:
        return YFinanceIntradayProvider()
    if normalized in {"kis", "kis_quote", "kis_quotes"}:
        from .kis_quotes import KISQuoteProvider

        return KISQuoteProvider()
    if normalized in {"kis_microstructure", "kis_micro", "kis_full"}:
        from .microstructure import KISMicrostructureProvider

        return KISMicrostructureProvider()
    raise ValueError(f"Unsupported intraday provider: {name}")


def _delay_seconds(provider_timestamp: str, bar_timestamp: str) -> int | None:
    try:
        provider_dt = datetime.fromisoformat(provider_timestamp)
        bar_dt = datetime.fromisoformat(bar_timestamp)
        return int(max(0, (provider_dt - bar_dt).total_seconds()))
    except Exception:
        return None


def _session_progress_fraction(ts: datetime, *, market_timezone: str) -> float:
    local = ts.astimezone(ZoneInfo(market_timezone))
    if market_timezone == "Asia/Seoul":
        session_open = datetime.combine(local.date(), time(hour=9, minute=0), tzinfo=local.tzinfo)
        session_close = datetime.combine(local.date(), time(hour=15, minute=30), tzinfo=local.tzinfo)
    else:
        session_open = datetime.combine(local.date(), time(hour=9, minute=30), tzinfo=local.tzinfo)
        session_close = datetime.combine(local.date(), time(hour=16, minute=0), tzinfo=local.tzinfo)
    total = max(1.0, (session_close - session_open).total_seconds())
    elapsed = min(max(0.0, (local - session_open).total_seconds()), total)
    return max(0.01, min(1.0, elapsed / total))


def _market_session(ts: datetime, *, market_timezone: str) -> str:
    local = ts.astimezone(ZoneInfo(market_timezone))
    if market_timezone == "Asia/Seoul":
        pre_open = time(hour=8, minute=0)
        open_time = time(hour=9, minute=0)
        close_time = time(hour=15, minute=30)
    else:
        pre_open = time(hour=4, minute=0)
        open_time = time(hour=9, minute=30)
        close_time = time(hour=16, minute=0)
    current = local.time()
    if current < pre_open:
        return "overnight"
    if current < open_time:
        return "pre_open"
    if current <= close_time:
        return "regular"
    return "post_close"

