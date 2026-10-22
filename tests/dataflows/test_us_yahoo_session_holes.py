"""Offline recovery of an interior hole; never patch or splice vendor rows."""
from datetime import date
from unittest.mock import Mock

import pandas as pd
import pytest

from tradingagents.dataflows import us_daily_history as us
from tradingagents.dataflows.config import run_config
from tradingagents.dataflows.daily_history_selection import get_selected_daily_history
from tradingagents.dataflows.vendor_exceptions import VendorMalformedResponseError


def frame(days):
    return pd.DataFrame([dict(Date=day, Open=100., High=110., Low=90., Close=105., Volume=200.) for day in days])


@pytest.fixture(autouse=True)
def isolated(monkeypatch):
    monkeypatch.setenv('TRADINGAGENTS_KIS_RESEARCH_FALLBACK_ENABLED', '1')
    monkeypatch.setattr(us, 'load_us_daily_bars', Mock(side_effect=AssertionError('Unexpected external request')))
    with run_config({}):
        yield


@pytest.mark.parametrize('bad_day', [None, 'not-a-date', '2026-10-22'])
def test_hole_with_recent_final_bar_uses_whole_replacement(monkeypatch, bad_day):
    original = frame(['2026-10-19', bad_day, '2026-10-21'])
    before = original.copy(deep=True)
    replacement = frame(['2026-10-19', '2026-10-20', '2026-10-21'])
    replacement['Date'] = pd.to_datetime(replacement['Date'])
    replacement.attrs.update(source=us.SOURCE, complete=True, requested_start='2026-10-19')
    loader = Mock(return_value=replacement)
    monkeypatch.setattr(us, 'load_us_daily_bars', loader)
    result = us.validate_with_us_fallback(original, 'ETN', '2026-10-19', '2026-10-21')
    loader.assert_called_once_with('ETN', '2026-10-19', '2026-10-21')
    assert result['Date'].dt.date.tolist() == [date(2026, 10, day) for day in (19, 20, 21)]
    assert result.attrs['source'] == us.SOURCE
    assert get_selected_daily_history('ETN', '2026-10-21')['source'] == us.SOURCE
    pd.testing.assert_frame_equal(original, before)


def test_missing_interior_session_cannot_succeed_without_replacement(monkeypatch):
    loader = Mock(return_value=None)
    monkeypatch.setattr(us, 'load_us_daily_bars', loader)
    with pytest.raises(VendorMalformedResponseError, match='interior completed session'):
        us.validate_with_us_fallback(frame(['2026-10-19','2026-10-21']), 'ETN', '2026-10-19','2026-10-21')
    assert get_selected_daily_history('ETN','2026-10-21') is None


def test_older_only_response_keeps_existing_stale_whole_recovery(monkeypatch):
    replacement = frame(['2026-10-19', '2026-10-20', '2026-10-21'])
    replacement['Date'] = pd.to_datetime(replacement['Date'])
    replacement.attrs.update(source=us.SOURCE, complete=True, requested_start='2026-10-19')
    loader = Mock(return_value=replacement)
    monkeypatch.setattr(us, 'load_us_daily_bars', loader)
    result = us.validate_with_us_fallback(frame(['2026-10-16']), 'ETN', '2026-10-19', '2026-10-21')
    loader.assert_called_once_with('ETN', '2026-10-19', '2026-10-21')
    assert result['Date'].dt.strftime('%Y-%m-%d').tolist() == ['2026-10-19','2026-10-20','2026-10-21']


@pytest.mark.parametrize('days,start', [
    (['2026-10-19','2026-10-20','2026-10-21'], '2026-10-19'),
    (['2026-10-16','2026-10-19'], '2026-10-16'),
    (['2026-10-20','2026-10-21'], '2026-10-19'),
])
def test_valid_continuous_history_preserves_values_and_no_broker_call(days, start):
    end=days[-1]
    original=frame(days)
    result=us.validate_with_us_fallback(original,'ETN',start,end)
    assert result['Close'].tolist() == original['Close'].tolist()
    assert result['Date'].dt.strftime('%Y-%m-%d').tolist() == days
    us.load_us_daily_bars.assert_not_called()
    assert get_selected_daily_history('ETN',end)['source'] == 'yfinance'
