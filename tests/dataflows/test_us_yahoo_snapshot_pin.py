"""A research scope retains its first native Yahoo input, including cache churn."""
from concurrent.futures import ThreadPoolExecutor
from contextvars import copy_context
from threading import Barrier
from unittest.mock import Mock

import pandas as pd
import pytest

from tradingagents.calendar_access import get_exchange_calendar
from tradingagents.dataflows import stockstats_utils as stats, us_daily_history as us
from tradingagents.dataflows.config import run_config
from tradingagents.dataflows.daily_history_evidence import DailyHistoryEvidenceRecorder
from tradingagents.dataflows.daily_history_selection import get_selected_daily_history
from tradingagents.dataflows.vendor_exceptions import VendorMalformedResponseError

START, END = '2021-10-21', '2026-10-21'


@pytest.fixture
def native(monkeypatch, tmp_path):
    monkeypatch.setenv('TRADINGAGENTS_KIS_RESEARCH_FALLBACK_ENABLED', '1')
    monkeypatch.setattr('requests.Session.request', Mock(side_effect=AssertionError('network forbidden')))
    days = get_exchange_calendar('XNYS').sessions_in_range(START, END).tz_localize(None)
    close = pd.Series([100.12345678901234 + i * .02 for i in range(len(days))], index=days)
    frame = pd.DataFrame({'Open':close-1, 'High':close+2, 'Low':close-2,
                          'Close':close, 'Volume':1000.}, index=days)
    frame.index.name = 'Date'
    download = Mock(return_value=frame)
    monkeypatch.setattr(stats.yf, 'download', download)
    return frame, download, {'data_cache_dir':str(tmp_path), 'analysis_as_of':END}, tmp_path


def test_active_snapshot_survives_cache_invalidation_without_refreshing_cache(native, monkeypatch):
    frame, download, config, path = native
    with run_config(config):
        first = stats.load_ohlcv('AAPL', END)
        cache = next(path.glob('*.csv'))
        before = cache.read_bytes(), cache.stat().st_mtime_ns
        download.return_value = frame * 2
        exists = stats.os.path.exists
        monkeypatch.setattr(stats.os.path, 'exists', lambda p: False if str(p) == str(cache) else exists(p))
        again = stats.load_ohlcv('AAPL', END)
        pd.testing.assert_frame_equal(first, again)
        download.assert_called_once()
        assert (cache.read_bytes(), cache.stat().st_mtime_ns) == before
    with run_config(config):
        fresh = stats.load_ohlcv('AAPL', END)
        assert fresh['Close'].iloc[-1] == first['Close'].iloc[-1] * 2
        assert download.call_count == 2


def test_independent_cache_read_preserves_exact_floats(native):
    _, download, config, _ = native
    with run_config(config):
        first = stats.load_ohlcv('AAPL', END)
    with run_config(config):
        again = stats.load_ohlcv('AAPL', END)
        # CSV dates may use a different datetime resolution; values stay exact.
        pd.testing.assert_frame_equal(first, again, check_exact=True, check_dtype=False)
    download.assert_called_once()


def test_pin_isolated_windows_and_unverified_provenance(native):
    _, _, config, _ = native
    recorder = DailyHistoryEvidenceRecorder('AAPL')
    token = recorder.activate()
    try:
        with run_config(config):
            first = stats.load_ohlcv('AAPL', END)
            selected = get_selected_daily_history('AAPL', END)
            assert selected['frame'] is not None
            original = first['Close'].iloc[-1]
            first.loc[first.index[-1], 'Close'] = 1.
            first.attrs['requested_start'] = '1900-01-01'
            assert stats.load_ohlcv('AAPL', END)['Close'].iloc[-1] == original
            narrow = us.selected_history('AAPL', '2026-10-01', END)
            assert narrow['Date'].min() >= pd.Timestamp('2026-10-01')
            with pytest.raises(VendorMalformedResponseError, match='exceeds the pinned'):
                us.selected_history('AAPL', '2020-01-01', END)
        receipt = recorder.receipt()
        assert receipt['entries'][0]['status'] != 'VERIFIED_RETRIEVED_SERIES'
        assert receipt['historical_vintage_verified'] is False
    finally:
        recorder.reset(token)


def test_concurrent_native_tools_return_the_winning_snapshot(native, monkeypatch):
    frame, _, config, _ = native
    from tradingagents.dataflows import daily_history_selection as selection
    original = selection.select_daily_history
    barrier = Barrier(2)

    def choose(*args, **kwargs):
        barrier.wait(timeout=10)
        return original(*args, **kwargs)

    monkeypatch.setattr(selection, 'select_daily_history', choose)
    with run_config(config), ThreadPoolExecutor(2) as pool:
        contexts = [copy_context(), copy_context()]
        frames = [frame.reset_index(), (frame * 2).reset_index()]
        futures = [pool.submit(context.run, us.validate_with_us_fallback, data, 'AAPL', START, END)
                   for context, data in zip(contexts, frames)]
        results = [future.result(timeout=20) for future in futures]
        pd.testing.assert_frame_equal(results[0], results[1], check_exact=True)


def test_optout_does_not_pin_short_native_window(native, monkeypatch):
    frame, _, config, _ = native
    monkeypatch.delenv('TRADINGAGENTS_KIS_RESEARCH_FALLBACK_ENABLED')
    with run_config(config):
        us.validate_with_us_fallback(frame.reset_index(), 'AAPL', START, END)
        assert get_selected_daily_history('AAPL', END)['frame'] is None
