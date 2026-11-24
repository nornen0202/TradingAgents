from datetime import datetime, timezone
from unittest.mock import Mock

import pandas as pd
import pytest

from tradingagents.dataflows.config import run_config
from tradingagents.dataflows.intraday import providers
from tradingagents.dataflows import intraday_market


def bars(indices, prices=None):
    prices = prices or [50] * len(indices)
    return pd.DataFrame({"Close": prices, "High": prices, "Low": prices, "Volume": [10] * len(indices)}, index=indices)


def test_local_filter_excludes_future_unknown_and_invalid_dates():
    frame = bars(["2026-04-14T12:00:00Z", "2026-04-14T15:00:00Z", None, "bad", "2026-04-14T13:00:00"])
    result = providers._dated_bars(frame, datetime(2026, 4, 14, 14, tzinfo=timezone.utc))
    assert len(result) == 1 and result.iloc[0]["Close"] == 50


def test_numeric_strings_do_not_concatenate_volume_and_duplicate_times_are_excluded():
    frame = bars(["2026-04-14T12:00:00Z", "2026-04-14T12:01:00Z", "2026-04-14T12:02:00Z", "2026-04-14T12:02:00Z"]).astype(str)
    result = providers._dated_bars(frame, datetime(2026, 4, 14, 14, tzinfo=timezone.utc))
    assert len(result) == 2 and result["Volume"].sum() == 20


def test_reference_snapshot_uses_cutoff_before_aggregation(monkeypatch):
    history = bars(["2026-04-13T15:00:00Z", "2026-04-14T13:31:00Z", "2026-04-14T14:30:00Z"], [40, 50, 999])
    daily = bars(["2026-04-13T04:00:00Z", "2026-04-14T04:00:00Z", "2099-01-01T00:00:00Z"], [40, 50, 999])
    daily["Volume"] = [100, 99999, 99999]
    monkeypatch.setattr(providers.yf, "Ticker", lambda _: Mock(history=Mock(side_effect=[history, daily])))
    with run_config({"analysis_as_of": "2026-04-14T14:00:00Z"}):
        snapshot = providers.YFinanceIntradayProvider().fetch("TCEHY", interval="1m")
    assert snapshot.last_price == snapshot.day_high == snapshot.day_low == 50
    assert snapshot.volume == 10 and snapshot.avg20_daily_volume == 100
    assert snapshot.provider_realtime_capable is False
    assert snapshot.halt_status["is_clear"] is False
    assert intraday_market.classify_execution_market_data(snapshot) == "DELAYED_ANALYSIS_ONLY"
    assert snapshot.asof == "2026-04-14T13:31:00+00:00"


@pytest.mark.parametrize("frame", [bars([]), bars([None]), bars(["bad"]), bars(["2099-01-01T00:00:00Z"]),
                                  bars(["2026-04-14T13:00:00Z"], [float("inf")])])
def test_no_verifiable_quote_fails_closed(monkeypatch, frame):
    monkeypatch.setattr(providers.yf, "Ticker", lambda _: Mock(history=lambda **_: frame))
    with run_config({"analysis_as_of": "2026-04-14T14:00:00Z"}):
        with pytest.raises(RuntimeError):
            providers.YFinanceIntradayProvider().fetch("TCEHY")


def test_fallback_keeps_provider_failure_without_leaking_details(monkeypatch):
    from tradingagents.schemas import IntradayMarketSnapshot
    snapshot = IntradayMarketSnapshot(ticker="TCEHY", asof="2026-04-14T13:31:00Z", provider="yfinance_intraday",
                                     session_vwap=None, day_high=50, day_low=50, volume=10, avg20_daily_volume=None, relative_volume=None,
                                     interval="1m", last_price=50, provider_realtime_capable=False,
                                     missing_reason={"orderbook": "not_provided"})
    monkeypatch.setattr(intraday_market, "get_intraday_provider", lambda name: Mock(
        fetch=Mock(side_effect=RuntimeError("secret=must-not-leak"))) if name == "kis_microstructure" else Mock(fetch=lambda *a, **k: snapshot))
    result = intraday_market.fetch_intraday_market_snapshot("TCEHY", provider="kis_microstructure,yfinance")
    assert result.missing_reason["provider:kis_microstructure"] == "unavailable:RuntimeError"
    assert result.missing_reason["orderbook"] == "not_provided"
    assert "secret" not in str(result.to_dict())
    assert result.execution_data_quality == "DELAYED_ANALYSIS_ONLY"
