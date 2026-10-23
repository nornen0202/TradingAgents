"""Exercise the market analyst's actual first-price -> indicator tool order offline."""
from io import StringIO
from types import SimpleNamespace
from unittest.mock import Mock

import pandas as pd
import pytest

from tradingagents.agents.analysts.market_analyst import _initial_market_data_tool_call
from tradingagents.calendar_access import get_exchange_calendar
from tradingagents.dataflows import stockstats_utils as stats, us_daily_history as us, y_finance
from tradingagents.dataflows.config import run_config
from tradingagents.dataflows.daily_history_evidence import DailyHistoryEvidenceRecorder
from tradingagents.dataflows.daily_history_selection import get_selected_daily_history
from tradingagents.portfolio.kis import KisClient


END = '2026-10-21'
WARMUP = '2021-10-21'
ARGS = _initial_market_data_tool_call(ticker='AAPL', current_date=END).tool_calls[0]['args']


@pytest.fixture
def data(monkeypatch, tmp_path):
    us._CACHE.clear()
    monkeypatch.setenv('TRADINGAGENTS_KIS_RESEARCH_FALLBACK_ENABLED', '1')
    monkeypatch.setattr(us, 'get_api_key', lambda _: 'offline')
    monkeypatch.setattr(us, 'time', SimpleNamespace(monotonic=lambda: 100., sleep=lambda _: None))
    monkeypatch.setattr('requests.Session.request', Mock(side_effect=AssertionError('network forbidden')))
    days = get_exchange_calendar('XNYS').sessions_in_range(WARMUP, END).tz_localize(None)
    close = pd.Series([100. + index * .02 for index in range(len(days))], index=days)
    good = pd.DataFrame({'Open': close-1, 'High': close+2, 'Low': close-2,
                         'Close': close, 'Volume': 1000.}, index=days)
    good.index.name = 'Date'
    bad = good.copy(deep=True)
    bad.iloc[0, bad.columns.get_loc('Close')] = float('nan')
    recent = good.loc[good.index >= pd.Timestamp(ARGS['start_date'])].copy()
    ticker = Mock()
    ticker.history.return_value = recent
    monkeypatch.setattr(y_finance.yf, 'Ticker', Mock(return_value=ticker))
    download = Mock(return_value=bad)
    monkeypatch.setattr(stats.yf, 'download', download)
    broker_frame = good.copy()
    for column in ('Open','High','Low','Close'):
        broker_frame[column] += 200.
    mapping = {'Open':'open','High':'high','Low':'low','Close':'clos','Volume':'tvol'}
    bars = [{'xymd': day.strftime('%Y%m%d'), **{target:str(row[source]) for source,target in mapping.items()}}
            for day,row in broker_frame.iloc[::-1].iterrows()]
    client = Mock(spec=['request_json'])
    client.request_json.side_effect = lambda **kwargs: (
        {'output2':[dict(row) for row in bars if row['xymd'] <= kwargs['params']['BYMD']][:100]}, {})
    monkeypatch.setattr(KisClient, 'from_api_keys', Mock(return_value=client))
    recorder = DailyHistoryEvidenceRecorder('AAPL')
    token = recorder.activate()
    with run_config({'data_cache_dir':str(tmp_path), 'analysis_as_of':END}):
        yield SimpleNamespace(good=good, bad=bad, broker=broker_frame, client=client,
                              ticker=ticker, download=download, recorder=recorder, path=tmp_path)
    recorder.reset(token)
    us._CACHE.clear()


def test_healthy_recent_price_cannot_pin_before_older_warmup_is_checked(data):
    csv = y_finance.get_YFin_data_online(**ARGS)
    first_price_requests = data.client.request_json.call_count
    indicator = y_finance._get_stock_stats_bulk('AAPL', 'close_200_sma', END)
    assert 'OHLCV source: KIS overseas_dailyprice' in csv
    price_rows = pd.read_csv(StringIO(csv), comment='#')
    expected = data.broker.loc[data.broker.index >= pd.Timestamp(ARGS['start_date'])]
    assert price_rows['Close'].tolist() == pytest.approx(expected['Close'].tolist())
    assert float(indicator[END]) == pytest.approx(data.broker['Close'].tail(200).mean())
    assert first_price_requests > 1
    assert data.client.request_json.call_count == first_price_requests
    data.download.assert_called_once()
    data.ticker.history.assert_not_called()
    assert pd.isna(data.bad.iloc[0]['Close'])
    selected = get_selected_daily_history('AAPL', END)
    assert selected['source'] == us.SOURCE
    assert selected['frame']['Date'].min() == pd.Timestamp(WARMUP)
    assert data.recorder.receipt()['entries'][0]['status'] == 'VERIFIED_RETRIEVED_SERIES'
    assert not list(data.path.glob('*.csv'))  # KIS must not be saved as Yahoo.


def test_healthy_whole_yahoo_stays_primary_and_report_stays_in_requested_window(data):
    data.download.return_value = data.good
    csv = y_finance.get_YFin_data_online(**ARGS)
    indicator = y_finance._get_stock_stats_bulk('AAPL', 'close_200_sma', END)
    prices = pd.read_csv(StringIO(csv), comment='#')
    assert prices['Date'].min() >= ARGS['start_date']
    assert prices['Date'].max() == END
    assert float(indicator[END]) == pytest.approx(data.good['Close'].tail(200).mean())
    assert get_selected_daily_history('AAPL', END)['source'] == 'yfinance'
    data.client.request_json.assert_not_called()
    data.download.assert_called_once()
    data.ticker.history.assert_not_called()


def test_without_recovery_optin_the_existing_price_only_path_is_unchanged(data, monkeypatch):
    monkeypatch.delenv('TRADINGAGENTS_KIS_RESEARCH_FALLBACK_ENABLED')
    csv = y_finance.get_YFin_data_online(**ARGS)
    assert 'Total records' in csv
    data.ticker.history.assert_called_once()
    data.download.assert_not_called()
    data.client.request_json.assert_not_called()


@pytest.mark.parametrize('field,value', [
    ('Close',float('nan')), ('Close',float('inf')), ('Close',0.),
    ('Open',0.), ('Open',float('-inf')), ('Open',99999.),
    ('High',1.), ('Low',99999.), ('Volume',-1.), ('Volume',float('inf')),
])
def test_older_invalid_values_are_replaced_as_one_complete_provider_series(data, field, value):
    broken = data.good.copy(deep=True)
    broken.iloc[300,broken.columns.get_loc(field)] = value
    original = broken.copy(deep=True)
    data.download.return_value = broken
    csv = y_finance.get_YFin_data_online(**ARGS)
    assert 'OHLCV source: KIS overseas_dailyprice' in csv
    assert get_selected_daily_history('AAPL', END)['frame']['Date'].min() == pd.Timestamp(WARMUP)
    pd.testing.assert_frame_equal(broken, original)
    data.ticker.history.assert_not_called()


@pytest.mark.parametrize('missing', ['empty','Open','Close','Volume','Date'])
def test_empty_or_missing_full_yahoo_fields_do_not_pin_healthy_short_history(data, missing):
    if missing == 'empty':
        broken = pd.DataFrame()
    elif missing == 'Date':
        broken = data.good.rename_axis('UnverifiableDate')
    else:
        broken = data.good.drop(columns=[missing])
    data.download.return_value = broken
    csv = y_finance.get_YFin_data_online(**ARGS)
    assert 'OHLCV source: KIS overseas_dailyprice' in csv
    data.ticker.history.assert_not_called()


def test_bad_future_values_are_filtered_before_whole_history_validation(data):
    future = data.good.tail(1).copy()
    future.index = pd.DatetimeIndex(['2026-10-22'], name='Date')
    future.loc[:,'Close'] = float('inf')
    data.download.return_value = pd.concat([data.good, future])
    csv = y_finance.get_YFin_data_online(**ARGS)
    indicator = y_finance._get_stock_stats_bulk('AAPL', 'close_200_sma', END)
    assert pd.read_csv(StringIO(csv), comment='#')['Date'].max() == END
    assert float(indicator[END]) == pytest.approx(data.good['Close'].tail(200).mean())
    data.client.request_json.assert_not_called()


def test_wrong_older_date_cannot_contribute_to_history_or_hide_missing_session(data):
    broken = data.good.copy()
    index = broken.index.astype(object).tolist()
    index[300] = 'unverifiable-date'
    broken.index = pd.Index(index, name='Date')
    data.download.return_value = broken
    csv = y_finance.get_YFin_data_online(**ARGS)
    assert 'OHLCV source: KIS overseas_dailyprice' in csv
    assert get_selected_daily_history('AAPL', END)['frame']['Date'].isna().sum() == 0
