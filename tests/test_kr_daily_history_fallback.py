from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from tradingagents.dataflows import kr_daily_history as kr
from tradingagents.dataflows import stockstats_utils, y_finance
from tradingagents.dataflows.vendor_exceptions import VendorMalformedResponseError
from tradingagents.scheduled import runner


def bar(day="20261012", **values):
    return {"stck_bsop_date": day, "stck_oprc": "100", "stck_hgpr": "110",
            "stck_lwpr": "90", "stck_clpr": "105", "acml_vol": "200", **values}


def yahoo(*, latest="2026-10-12", close=float("nan")):
    return pd.DataFrame({"Open": [100], "High": [110], "Low": [90],
                         "Close": [close], "Volume": [200]},
                        index=pd.DatetimeIndex([latest], name="Date"))


@pytest.fixture
def broker(monkeypatch):
    kr._CACHE.clear()
    monkeypatch.setenv("TRADINGAGENTS_KIS_RESEARCH_FALLBACK_ENABLED", "1")
    monkeypatch.setattr(kr, "get_api_key", lambda name: "test-credential")
    monkeypatch.setattr(kr.time, "sleep", lambda _: None)
    client = Mock()
    client.domestic_daily_itemchartprice.return_value = {"output2": [bar()]}
    with patch("tradingagents.portfolio.kis.KisClient.from_api_keys", return_value=client):
        yield client
    kr._CACHE.clear()


def test_bad_latest_yahoo_is_replaced_by_complete_broker_series_with_provenance(broker):
    broker.domestic_daily_itemchartprice.return_value = {
        "output2": [bar(), bar("20261008", stck_clpr="102")]}
    original = yahoo().reset_index()
    result = kr.validate_with_kr_fallback(original, "000660.KS", "2026-10-08", "2026-10-12")
    assert result["Close"].tolist() == [102, 105]
    assert pd.isna(original.iloc[-1]["Close"])
    assert result.attrs["source"] == kr.SOURCE
    assert "observed_at=" in kr.source_note(result)
    assert "requested_end=2026-10-12" in kr.source_note(result)
    assert broker.domestic_daily_itemchartprice.call_args.kwargs["adjusted_price"] == "0"


@pytest.mark.parametrize("column,value", [("stck_clpr", ""), ("stck_clpr", "NaN"),
    ("stck_clpr", "inf"), ("stck_oprc", "0"), ("stck_hgpr", "99"),
    ("stck_lwpr", "106"), ("acml_vol", "-1")])
def test_every_broker_row_is_validated_not_only_latest(broker, column, value):
    broker.domestic_daily_itemchartprice.return_value = {
        "output2": [bar(), bar("20261008", **{column: value})]}
    with pytest.raises(VendorMalformedResponseError, match="OHLCV"):
        kr.load_kr_daily_bars("000660.KS", "2026-10-08", "2026-10-12")
    assert not kr._CACHE


def test_future_bad_rows_cannot_contaminate_historical_result(broker):
    broker.domestic_daily_itemchartprice.return_value = {
        "output2": [bar("20261013", stck_clpr="bad"), bar()]}
    result = kr.load_kr_daily_bars("000660.KS", "2026-10-08", "2026-10-12", require_end=True)
    assert len(result) == 1
    assert result.iloc[0]["Date"] == pd.Timestamp("2026-10-12")


def test_conflicting_duplicate_dates_are_rejected(broker):
    broker.domestic_daily_itemchartprice.return_value = {
        "output2": [bar(), bar(stck_clpr="104")]}
    with pytest.raises(VendorMalformedResponseError, match="conflicting"):
        kr.load_kr_daily_bars("000660.KS", "2026-10-08", "2026-10-12")


def test_missing_required_session_cannot_use_older_bar(broker):
    broker.domestic_daily_itemchartprice.return_value = {"output2": [bar("20261008")]}
    with pytest.raises(VendorMalformedResponseError, match="required completed session"):
        kr.load_kr_daily_bars("000660.KS", "2026-10-08", "2026-10-12", require_end=True)
    with pytest.raises(VendorMalformedResponseError, match="Latest requested"):
        kr.validate_with_kr_fallback(yahoo().reset_index(), "000660.KS", "2026-10-08", "2026-10-12")


def test_pagination_moves_strictly_backwards_without_mixing_sources(broker):
    end = date(2026, 10, 12)
    page = [bar((end - timedelta(days=i)).strftime("%Y%m%d")) for i in range(100)]
    broker.domestic_daily_itemchartprice.side_effect = [
        {"output2": page}, {"output2": [bar("20260704")]}]
    result = kr.load_kr_daily_bars("000660.KS", "2026-07-01", "2026-10-12")
    assert len(result) == 101
    assert broker.domestic_daily_itemchartprice.call_args_list[1].kwargs["end_date"] == date(2026, 7, 4)
    assert result.iloc[0]["Date"] == pd.Timestamp("2026-07-04")


def test_nonprogressing_and_exhausted_pagination_fail_closed(broker, monkeypatch):
    broker.domestic_daily_itemchartprice.return_value = {"output2": [bar("20261013")]}
    with pytest.raises(VendorMalformedResponseError, match="no progress"):
        kr.load_kr_daily_bars("000660.KS", "2026-07-01", "2026-10-12")
    monkeypatch.setattr(kr, "_MAX_PAGES", 1)
    broker.domestic_daily_itemchartprice.return_value = {"output2": [bar()] * 100}
    with pytest.raises(VendorMalformedResponseError, match="page limit"):
        kr.load_kr_daily_bars("000660.KS", "2026-07-01", "2026-10-12")


def test_process_cache_is_date_scoped_and_never_returns_mutated_frame(broker):
    one = kr.load_kr_daily_bars("000660.KS", "2026-10-08", "2026-10-12")
    one.loc[0, "Close"] = 1
    two = kr.load_kr_daily_bars("000660.KS", "2026-10-08", "2026-10-12")
    assert two.loc[0, "Close"] == 105
    assert broker.domestic_daily_itemchartprice.call_count == 1
    broker.domestic_daily_itemchartprice.return_value = {"output2": [bar("20261013")]}
    kr.load_kr_daily_bars("000660.KS", "2026-10-08", "2026-10-13")
    assert broker.domestic_daily_itemchartprice.call_count == 2


def test_cache_expiry_refetches_and_provider_failure_never_caches(broker, monkeypatch):
    monkeypatch.setattr(kr.time, "monotonic", lambda: 100)
    kr.load_kr_daily_bars("000660.KS", "2026-10-08", "2026-10-12")
    monkeypatch.setattr(kr.time, "monotonic", lambda: 401)
    broker.domestic_daily_itemchartprice.side_effect = RuntimeError("broker unavailable")
    with pytest.raises(RuntimeError, match="broker unavailable"):
        kr.load_kr_daily_bars("000660.KS", "2026-10-08", "2026-10-12")
    assert broker.domestic_daily_itemchartprice.call_count == 2
    assert kr._CACHE[("000660.KS", "2026-10-08", "2026-10-12")][0] == 100


@pytest.mark.parametrize("payload", [{"output2": None}, {"output2": [None]},
    {"output2": [bar("not-a-date")]}, {"output2": []}])
def test_bad_broker_payloads_cannot_enter_cache(broker, payload):
    broker.domestic_daily_itemchartprice.return_value = payload
    with pytest.raises(VendorMalformedResponseError):
        kr.load_kr_daily_bars("000660.KS", "2026-10-08", "2026-10-12")
    assert not kr._CACHE


@pytest.mark.parametrize("symbol", ["AAPL", "^KS11", "000660", "../005930.KS"])
def test_no_broker_request_for_ineligible_symbols(broker, symbol):
    assert kr.load_kr_daily_bars(symbol, "2026-10-08", "2026-10-12") is None
    broker.domestic_daily_itemchartprice.assert_not_called()


def test_no_broker_request_without_optin_or_credentials(broker, monkeypatch):
    monkeypatch.delenv("TRADINGAGENTS_KIS_RESEARCH_FALLBACK_ENABLED")
    assert kr.load_kr_daily_bars("000660.KS", "2026-10-08", "2026-10-12") is None
    monkeypatch.setenv("TRADINGAGENTS_KIS_RESEARCH_FALLBACK_ENABLED", "1")
    monkeypatch.setattr(kr, "get_api_key", lambda _: None)
    assert kr.load_kr_daily_bars("000660.KS", "2026-10-08", "2026-10-12") is None
    broker.domestic_daily_itemchartprice.assert_not_called()


def test_healthy_yahoo_remains_primary(broker):
    result = kr.validate_with_kr_fallback(yahoo(close=103).reset_index(), "000660.KS", "2026-10-08", "2026-10-12")
    assert result.iloc[-1]["Close"] == 103
    assert not kr.source_note(result)
    broker.domestic_daily_itemchartprice.assert_not_called()


def test_csv_and_indicator_paths_include_broker_provenance_without_yahoo_cache_poison(broker, tmp_path):
    with patch.object(y_finance.yf, "Ticker") as ticker:
        ticker.return_value.history.return_value = yahoo()
        result = y_finance.get_YFin_data_online("000660.KS", "2026-10-08", "2026-10-12")
    assert "OHLCV source: KIS" in result
    assert "2026-10-12,100.0,110.0,90.0,105.0,200.0" in result
    with patch.object(stockstats_utils, "get_config", return_value={"data_cache_dir": str(tmp_path)}), \
         patch.object(stockstats_utils.yf, "download", return_value=yahoo()):
        result = y_finance.get_stock_stats_indicators_window("000660.KS", "close_10_ema", "2026-10-12", 0)
        repeated = y_finance.get_stock_stats_indicators_window("000660.KS", "close_10_ema", "2026-10-12", 0)
        assert repeated == result
    assert "OHLCV source: KIS" in result
    assert "2026-10-12: 105.0" in result
    assert not list(tmp_path.glob("*.csv"))


def test_repeated_indicator_read_cannot_accept_previously_rejected_older_fallback(broker, tmp_path):
    broker.domestic_daily_itemchartprice.return_value = {"output2": [bar("20261008")]}
    with patch.object(stockstats_utils, "get_config", return_value={"data_cache_dir": str(tmp_path)}), \
         patch.object(stockstats_utils.yf, "download", return_value=yahoo()):
        for _ in range(2):
            with pytest.raises(VendorMalformedResponseError, match="Latest requested"):
                stockstats_utils.load_ohlcv("000660.KS", "2026-10-12")
    # Valid historical broker rows may be cached internally, but each caller
    # must reapply its own source-selection and exact-latest-bar guard.
    assert broker.domestic_daily_itemchartprice.call_count == 1
    assert not list(tmp_path.glob("*.csv"))


def test_existing_stale_yahoo_cache_does_not_hide_missing_session(broker, tmp_path):
    today = pd.Timestamp.today()
    start = (min(today, pd.Timestamp("2026-10-12")) - pd.DateOffset(years=5)).strftime("%Y-%m-%d")
    end = (today + pd.DateOffset(days=1)).strftime("%Y-%m-%d")
    cache = tmp_path / f"000660.KS-YFin-data-{start}-{end}.csv"
    yahoo(latest="2026-10-08", close=99).reset_index().to_csv(cache, index=False)
    before = cache.read_bytes()
    with patch.object(stockstats_utils, "get_config", return_value={"data_cache_dir": str(tmp_path)}), \
         patch.object(stockstats_utils.yf, "download", side_effect=AssertionError("must reuse fresh cache")):
        result = stockstats_utils.load_ohlcv("000660.KS", "2026-10-12")
    assert result.iloc[-1]["Date"] == pd.Timestamp("2026-10-12")
    assert result.attrs["source"] == kr.SOURCE
    assert cache.read_bytes() == before


def test_stale_trade_date_resolver_uses_real_completed_broker_bar_before_wait(broker):
    config = SimpleNamespace(run=SimpleNamespace(trade_date_mode="latest_available", timezone="Asia/Seoul",
        latest_market_data_lookback_days=10, market="KR", market_declared=True,
        latest_market_data_wait_minutes=150, latest_market_data_retry_interval_seconds=600))
    with patch.object(runner, "_expected_completed_daily_trade_date", return_value=date(2026, 10, 12)), \
         patch.object(runner, "_fetch_recent_trade_date_history", return_value=yahoo(latest="2026-10-08", close=99)), \
         patch.object(runner, "sleep") as sleep:
        assert runner.resolve_trade_date("000660.KS", config) == "2026-10-12"
    sleep.assert_not_called()


def test_stale_trade_date_resolver_does_not_accept_bad_or_unavailable_broker_bar(broker):
    config = SimpleNamespace(run=SimpleNamespace(trade_date_mode="latest_available", timezone="Asia/Seoul",
        latest_market_data_lookback_days=10, market="KR", market_declared=True,
        latest_market_data_wait_minutes=0, latest_market_data_retry_interval_seconds=600))
    broker.domestic_daily_itemchartprice.return_value = {"output2": [bar(stck_clpr="NaN")]}
    with patch.object(runner, "_expected_completed_daily_trade_date", return_value=date(2026, 10, 12)), \
         patch.object(runner, "_fetch_recent_trade_date_history", return_value=yahoo(latest="2026-10-08", close=99)):
        with pytest.raises(RuntimeError, match="Refusing stale"):
            runner.resolve_trade_date("000660.KS", config)
