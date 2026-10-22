from concurrent.futures import ThreadPoolExecutor
from contextvars import copy_context
from datetime import datetime, timezone
from threading import Barrier
from types import SimpleNamespace

import pandas as pd
import pytest

from tradingagents.charting.capture import ChartCapture, capture_daily_frame
from tradingagents.dataflows.config import run_config, run_config_context
from tradingagents.dataflows.daily_history_selection import get_selected_daily_history, select_daily_history
from tradingagents.dataflows.vendor_exceptions import VendorMalformedResponseError


DAY = "2024-01-03"
KIS = "KIS overseas_dailyprice (MODP=1)"


def frame(close=105):
    data = pd.DataFrame({"Date": [pd.Timestamp(DAY)], "Open": [100], "High": [110],
                         "Low": [90], "Close": [close], "Volume": [200]})
    data.attrs = {"source": KIS, "provider": "kis", "coverage": {"complete": True}}
    return data


def test_selection_without_research_scope_has_no_global_side_effect():
    select_daily_history("AAPL", DAY, KIS, frame())
    assert get_selected_daily_history("AAPL", DAY) is None
    with run_config({}):
        assert get_selected_daily_history("AAPL", DAY) is None


def test_child_tool_selection_is_visible_to_parent_and_later_tools():
    with run_config({}):
        context = copy_context()
        with ThreadPoolExecutor(max_workers=1) as pool:
            pool.submit(context.run, select_daily_history, "AAPL", DAY, KIS, frame()).result()
        assert get_selected_daily_history("AAPL", DAY)["source"] == KIS
        later = copy_context().run(get_selected_daily_history, "AAPL", DAY)
        assert later["frame"].iloc[0]["Close"] == 105
    assert get_selected_daily_history("AAPL", DAY) is None


def test_initial_frame_is_retained_and_all_copies_are_isolated():
    source = frame()
    with run_config({}):
        select_daily_history("aapl", DAY, KIS, source)
        source.loc[0, "Close"] = 99
        source.attrs["coverage"]["complete"] = False
        first = get_selected_daily_history("AAPL", DAY)
        assert first["frame"].iloc[0]["Close"] == 105
        assert first["frame"].attrs["coverage"]["complete"] is True
        first["frame"].loc[0, "Close"] = 101
        first["frame"].attrs["coverage"]["complete"] = False
        # Refetches or cache expiry cannot revise evidence within an analysis.
        select_daily_history("AAPL", DAY, KIS, frame(102))
        second = get_selected_daily_history("AAPL", DAY)
        assert second["frame"].iloc[0]["Close"] == 105
        assert second["frame"].attrs["coverage"]["complete"] is True
        assert get_selected_daily_history("MSFT", DAY) is None
        assert get_selected_daily_history("AAPL", "2024-01-04") is None


def test_nested_and_failed_scopes_restore_prior_selection():
    with run_config({}):
        select_daily_history("AAPL", DAY, "yfinance")
        with pytest.raises(RuntimeError):
            with run_config({}):
                assert get_selected_daily_history("AAPL", DAY) is None
                select_daily_history("AAPL", DAY, KIS, frame())
                raise RuntimeError("failed research")
        assert get_selected_daily_history("AAPL", DAY) == {"source": "yfinance", "frame": None}
    with run_config({}):
        assert get_selected_daily_history("AAPL", DAY) is None


def test_stream_contexts_are_independent_and_tool_children_share_each_stream():
    with run_config({}):
        select_daily_history("AAPL", DAY, "yfinance")
        first, second = run_config_context({}), run_config_context({})
        assert first.run(get_selected_daily_history, "AAPL", DAY) is None
        child = first.run(copy_context)
        child.run(select_daily_history, "AAPL", DAY, KIS, frame())
        assert first.run(get_selected_daily_history, "AAPL", DAY)["source"] == KIS
        assert second.run(get_selected_daily_history, "AAPL", DAY) is None
        assert get_selected_daily_history("AAPL", DAY)["source"] == "yfinance"
    assert get_selected_daily_history("AAPL", DAY) is None


@pytest.mark.parametrize("first,second", [("yfinance", KIS), (KIS, "yfinance")])
def test_source_change_is_rejected_without_replacing_original(first, second):
    with run_config({}):
        select_daily_history("AAPL", DAY, first, frame() if first == KIS else None)
        with pytest.raises(VendorMalformedResponseError, match="source changed"):
            select_daily_history("AAPL", DAY, second, frame() if second == KIS else None)
        assert get_selected_daily_history("AAPL", DAY)["source"] == first


def test_concurrent_first_selection_has_one_winner_and_no_mixed_snapshot():
    barrier = Barrier(2)
    def choose(source, close):
        barrier.wait(timeout=5)
        try:
            select_daily_history("AAPL", DAY, source, frame(close))
        except VendorMalformedResponseError:
            return "rejected", source
        return "selected", source
    with run_config({}):
        contexts = [copy_context(), copy_context()]
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(ctx.run, choose, source, close)
                       for ctx, source, close in zip(contexts, ("yfinance", KIS), (101, 105))]
            results = [future.result() for future in futures]
        assert sorted(status for status, _ in results) == ["rejected", "selected"]
        winner = next(source for status, source in results if status == "selected")
        pinned = get_selected_daily_history("AAPL", DAY)
        assert pinned["source"] == winner
        assert pinned["frame"].iloc[0]["Close"] == (101 if winner == "yfinance" else 105)


@pytest.mark.parametrize("attributes,provider", [
    ({"source": KIS}, "kis"),
    ({"source": "KIS domestic_daily_itemchartprice (KRX, adjusted prices)"}, "kis"),
    ({"provider": "kis", "source": "explicit-provider-fixture"}, "kis"),
    ({}, "yfinance"),
])
def test_chart_capture_keeps_daily_provider_provenance(monkeypatch, attributes, provider):
    import exchange_calendars
    calendar = SimpleNamespace(is_session=lambda day: True,
                               session_close=lambda day: pd.Timestamp(DAY + "T21:00:00Z"))
    monkeypatch.setattr(exchange_calendars, "get_calendar", lambda name: calendar)
    data = frame()
    data.attrs = attributes
    capture = ChartCapture("AAPL")
    token = capture.activate()
    try:
        capture_daily_frame("AAPL", data, curr_date=DAY)
    finally:
        capture.reset(token)
    artifact = capture.artifact(analysis_as_of=datetime.now(timezone.utc))
    assert artifact["provider"] == provider
    assert artifact["providers"] == [provider]
