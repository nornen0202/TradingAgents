from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import yfinance as yf

from tradingagents.schemas import IntradayMarketSnapshot


def fetch_intraday_market_snapshot(
    ticker: str,
    *,
    interval: str = "5m",
    market_timezone: str = "US/Eastern",
) -> IntradayMarketSnapshot:
    history = yf.Ticker(ticker).history(period="1d", interval=interval, auto_adjust=False)
    if history.empty:
        raise RuntimeError(f"No intraday data available for ticker '{ticker}'.")

    history = history.dropna(subset=["Close"])  # defensive
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
    daily = yf.Ticker(ticker).history(period="3mo", interval="1d", auto_adjust=False)
    if not daily.empty and "Volume" in daily:
        avg20_volume = float(daily["Volume"].tail(20).mean())

    intraday_volume = int(volumes.sum())
    relative_volume = None
    if avg20_volume and avg20_volume > 0:
        relative_volume = float(intraday_volume / avg20_volume)

    return IntradayMarketSnapshot(
        ticker=ticker,
        asof=last_ts.isoformat(),
        provider="yfinance_intraday",
        interval=interval,
        last_price=float(closes.iloc[-1]),
        session_vwap=session_vwap,
        day_high=float(highs.max()),
        day_low=float(lows.min()),
        volume=intraday_volume,
        avg20_daily_volume=avg20_volume,
        relative_volume=relative_volume,
    )
