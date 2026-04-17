from __future__ import annotations

from datetime import datetime, time
from typing import Protocol
from zoneinfo import ZoneInfo

import yfinance as yf

from tradingagents.schemas import IntradayMarketSnapshot

from ..stockstats_utils import yf_retry


class IntradaySnapshotProvider(Protocol):
    name: str
    realtime_capable: bool

    def fetch(self, ticker: str, *, interval: str = "5m", market_timezone: str = "US/Eastern") -> IntradayMarketSnapshot:
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
    ) -> IntradayMarketSnapshot:
        ticker_obj = yf.Ticker(ticker)
        history = yf_retry(lambda: ticker_obj.history(period="1d", interval=interval, auto_adjust=False))
        if history.empty:
            raise RuntimeError(f"No intraday data available for ticker '{ticker}'.")

        history = history.dropna(subset=["Close"])
        if history.empty:
            raise RuntimeError(f"Intraday dataset for '{ticker}' is empty after cleanup.")

        closes = history["Close"]
        highs = history["High"]
        lows = history["Low"]
        volumes = history["Volume"]

        last_ts = history.index[-1].to_pydatetime()
        if last_ts.tzinfo is None:
            last_ts = last_ts.replace(tzinfo=ZoneInfo(market_timezone))

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
            avg20_volume = float(daily["Volume"].tail(20).mean())

        intraday_volume = int(volumes.sum())
        relative_volume = None
        if avg20_volume and avg20_volume > 0:
            progress = _session_progress_fraction(last_ts, market_timezone=market_timezone)
            adjusted_baseline = max(avg20_volume * progress, avg20_volume * 0.05)
            relative_volume = float(intraday_volume / adjusted_baseline)

        provider_timestamp = datetime.now(last_ts.tzinfo).isoformat()
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
            bar_timestamp=last_ts.isoformat(),
            provider_timestamp=provider_timestamp,
            quote_delay_seconds=_delay_seconds(provider_timestamp, last_ts.isoformat()),
            provider_realtime_capable=self.realtime_capable,
            market_session=_market_session(last_ts, market_timezone=market_timezone),
        )


def get_intraday_provider(name: str | None) -> IntradaySnapshotProvider:
    normalized = str(name or "yfinance").strip().lower()
    if normalized in {"yfinance", "yfinance_intraday"}:
        return YFinanceIntradayProvider()
    if normalized in {"kis", "kis_quote", "kis_quotes"}:
        from .kis_quotes import KISQuoteProvider

        return KISQuoteProvider()
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

