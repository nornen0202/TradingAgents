"""Whole KR research inputs: no network, row splicing or clock fabrication."""
from datetime import date
import hashlib
from unittest.mock import Mock

import pandas as pd
import pytest
from stockstats import wrap

from tradingagents.calendar_access import get_exchange_calendar
from tradingagents.dataflows import kr_daily_history as kr, stockstats_utils as stats, y_finance
from tradingagents.dataflows.config import run_config
from tradingagents.dataflows.daily_history_evidence import DailyHistoryEvidenceRecorder
from tradingagents.dataflows.daily_history_selection import get_selected_daily_history, select_daily_history
from tradingagents.dataflows.vendor_exceptions import VendorMalformedResponseError
from tradingagents.scheduled.market_calendar import is_supplemental_market_holiday


SYMBOL, END = '267260.KS', '2026-10-21'


def frame(days):
    return pd.DataFrame({'Date': pd.to_datetime(days), 'Open': 100., 'High': 110.,
                         'Low': 90., 'Close': 105., 'Volume': 200.})


def stamped(data, start, end):
    result = data.copy(deep=True)
    result.attrs.update(source=kr.SOURCE, provider='kis', exchange='KRX', adjustment='FID_ORG_ADJ_PRC=0',
                        requested_start=start, requested_end=end, observed_at='2026-10-22T00:00:00+00:00',
                        complete=True, session_count=len(result),
                        series_sha256=hashlib.sha256(result.to_csv(index=False).encode()).hexdigest())
    return result


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setenv('TRADINGAGENTS_KIS_RESEARCH_FALLBACK_ENABLED', '1')
    monkeypatch.setattr(stats.yf, 'download', Mock(side_effect=AssertionError('network forbidden')))
    ticker = Mock()
    ticker.history.side_effect = AssertionError('short-range Yahoo history must not replace the full input')
    monkeypatch.setattr(y_finance.yf, 'Ticker', Mock(return_value=ticker))
    monkeypatch.setattr(kr, 'load_kr_daily_bars', Mock(side_effect=AssertionError('unexpected KIS request')))


@pytest.mark.parametrize('middle', [None, 'bad-date', '2026-10-22'])
def test_missing_future_or_unknown_middle_date_requires_whole_replacement(monkeypatch, middle):
    original = frame(['2026-10-19', '2026-10-20', END])
    original['Date'] = original['Date'].astype(object)
    original.loc[1, 'Date'] = middle
    before = original.copy(deep=True)
    replacement = stamped(frame(['2026-10-19', '2026-10-20', END]), '2026-10-19', END)
    loader = Mock(return_value=replacement)
    monkeypatch.setattr(kr, 'load_kr_daily_bars', loader)
    with run_config({}):
        result = kr.validate_with_kr_fallback(original, SYMBOL, '2026-10-19', END)
        assert result['Date'].dt.strftime('%Y-%m-%d').tolist() == ['2026-10-19','2026-10-20',END]
        assert get_selected_daily_history(SYMBOL, END)['source'] == kr.SOURCE
    loader.assert_called_once_with(SYMBOL, '2026-10-19', END, require_complete=True)
    pd.testing.assert_frame_equal(original, before)


def test_no_replacement_or_shorter_replacement_cannot_hide_a_missing_session(monkeypatch):
    original = frame(['2026-10-19', END])
    for replacement in (None, stamped(frame(['2026-10-20', END]), '2026-10-20', END)):
        monkeypatch.setattr(kr, 'load_kr_daily_bars', Mock(return_value=replacement))
        with run_config({}):
            with pytest.raises(VendorMalformedResponseError, match='missing required sessions'):
                kr.validate_with_kr_fallback(original, SYMBOL, '2026-10-19', END)
            assert get_selected_daily_history(SYMBOL, END) is None


@pytest.mark.parametrize('gap', [False, True])
def test_first_price_and_later_indicators_share_full_five_year_snapshot(monkeypatch, tmp_path, gap):
    start = '2021-10-21'
    days = get_exchange_calendar('XKRX', start=start, end=END).sessions
    days = [day for day in days if not is_supplemental_market_holiday(market='KR', session_date=day.date())]
    whole = frame(days)
    yahoo = whole.drop(index=len(whole)-3) if gap else whole.copy(deep=True)
    broker_whole = whole.copy(deep=True)
    broker_whole['Close'] = 106.
    download = Mock(return_value=yahoo.set_index('Date'))
    monkeypatch.setattr(stats.yf, 'download', download)
    loader = Mock(return_value=stamped(broker_whole, start, END))
    monkeypatch.setattr(kr, 'load_kr_daily_bars', loader)
    recorder = DailyHistoryEvidenceRecorder(SYMBOL)
    token = recorder.activate()
    try:
        with run_config({'data_cache_dir': str(tmp_path)}):
            price = y_finance.get_YFin_data_online(SYMBOL, '2026-09-01', END)
            selected = get_selected_daily_history(SYMBOL, END)
            assert len(selected['frame']) == len(whole)
            assert selected['source'] == (kr.SOURCE if gap else 'yfinance')
            assert (selected['frame']['Close'] == (106. if gap else 105.)).all()
            # Even a later cache expiry cannot silently replace this run's input.
            monkeypatch.setattr(stats.time, 'time', lambda: 9999999999.)
            value = stats.StockstatsUtils.get_stock_stats(SYMBOL, 'close_200_sma', END)
            expected = broker_whole if gap else whole
            assert value == float(wrap(expected.copy())['close_200_sma'].iloc[-1])
            assert price.count('\n') < len(whole)
            y_finance.yf.Ticker.return_value.history.assert_not_called()
            download.assert_called_once()
            assert download.call_args.kwargs['start'] == start
            if gap:
                loader.assert_called_once_with(SYMBOL, start, END, require_complete=True)
                assert recorder.receipt()['entries'][0]['status'] == 'VERIFIED_RETRIEVED_SERIES'
                assert recorder.receipt()['entries'][0]['exchange'] == 'KRX'
                assert not list(tmp_path.glob('*.csv'))
            else:
                loader.assert_not_called()
    finally:
        recorder.reset(token)


@pytest.mark.parametrize('market,day,expected', [
    ('KR', date(2026,6,3), True), ('KR', date(2026,6,2), False),
    ('KR', date(2026,6,4), False), ('US', date(2026,6,3), False),
    ('KR', date(2030,6,3), False),
])
def test_only_verified_specific_election_day_is_added(market, day, expected):
    assert is_supplemental_market_holiday(market=market, session_date=day) is expected


@pytest.mark.parametrize('field,value', [
    ('exchange','NAS'), ('adjustment','FID_ORG_ADJ_PRC=1'), ('provider','yfinance'),
    ('observed_at','2099-01-01T00:00:00+00:00'), ('observed_at',None),
    ('series_sha256','wrong'), ('complete',False), ('requested_start',None), ('session_count',4),
])
def test_kr_receipt_does_not_promote_missing_future_or_wrong_metadata(field, value):
    data = stamped(frame(['2026-10-19','2026-10-20',END]), '2026-10-19', END)
    data.attrs[field] = value
    recorder = DailyHistoryEvidenceRecorder(SYMBOL)
    token = recorder.activate()
    try:
        with run_config({}):
            select_daily_history(SYMBOL, END, kr.SOURCE, data)
        entry = recorder.receipt()['entries'][0]
        assert entry['status'] == 'UNVERIFIED'
        assert entry['historical_vintage_verified'] is False
    finally:
        recorder.reset(token)
