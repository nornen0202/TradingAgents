import json
import sqlite3
import sys
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pandas as pd
import pytest

from tradingagents.performance import price_history as prices
from tradingagents.performance.action_outcomes import initialize_action_tracker, _normalize_price_history
from tradingagents.scheduled import runner
from tradingagents.scheduled.config import load_scheduled_config


@pytest.mark.parametrize('cutoff', [None, '', '2026-02-30', '20260402', '2026-04-02junk'])
def test_price_requests_require_explicit_valid_analysis_date(monkeypatch, cutoff):
    download = Mock(side_effect=AssertionError('network must not run'))
    monkeypatch.setitem(sys.modules, 'yfinance', SimpleNamespace(download=download))
    with pytest.raises(ValueError, match='explicit ISO'):
        prices._fetch_yfinance_price_history(['AAPL'], benchmark_ticker=None, lookback_days=5, asof_date=cutoff)
    download.assert_not_called()


def test_provider_request_and_return_both_obey_date_window(monkeypatch):
    frame = pd.DataFrame({('Close', 'AAPL'): [90, 100, 101, 102, 103, 104]},
                         index=['2026-03-27', '2026-03-28', '2026-04-02', '2026-04-03', None, '2026-04-02junk'])
    download = Mock(return_value=frame)
    monkeypatch.setitem(sys.modules, 'yfinance', SimpleNamespace(download=download))
    history, _ = prices._fetch_yfinance_price_history(['AAPL'], benchmark_ticker=None, lookback_days=5, asof_date='2026-04-02')
    assert history == {'AAPL': [{'date': '2026-03-28', 'close': 100.0}, {'date': '2026-04-02', 'close': 101.0}]}
    assert download.call_args.kwargs['start'] == '2026-03-28'
    assert download.call_args.kwargs['end'] == '2026-04-03'
    assert 'period' not in download.call_args.kwargs


@pytest.mark.parametrize('value', [float('inf'), float('-inf'), -1, 0, True, 'bad'])
def test_invalid_prices_are_excluded(monkeypatch, value):
    frame = pd.DataFrame({('Close', 'AAPL'): [value]}, index=pd.to_datetime(['2026-04-02']))
    monkeypatch.setitem(sys.modules, 'yfinance', SimpleNamespace(download=Mock(return_value=frame)))
    history, _ = prices._fetch_yfinance_price_history(['AAPL'], benchmark_ticker=None, lookback_days=5, asof_date='2026-04-02')
    assert history == {}


def test_single_requested_symbol_cannot_borrow_another_symbol(monkeypatch):
    frame = pd.DataFrame({('Close', 'MSFT'): [100]}, index=pd.to_datetime(['2026-04-02']))
    monkeypatch.setitem(sys.modules, 'yfinance', SimpleNamespace(download=Mock(return_value=frame)))
    history, warnings = prices._fetch_yfinance_price_history(['AAPL'], benchmark_ticker=None, lookback_days=5, asof_date='2026-04-02')
    assert history == {} and 'performance_yfinance_no_close:AAPL' in warnings


def test_empty_response_remains_missing(monkeypatch):
    monkeypatch.setitem(sys.modules, 'yfinance', SimpleNamespace(download=Mock(return_value=pd.DataFrame())))
    history, warnings = prices._fetch_yfinance_price_history(['AAPL'], benchmark_ticker=None, lookback_days=5, asof_date='2026-04-02')
    assert not history and 'performance_yfinance_no_data:AAPL' in warnings


def test_unrelated_or_benchmark_prices_do_not_count_as_due_security_prices():
    result = prices.PriceHistoryLoadResult(price_history={'MSFT': [{'date': '2026-04-02', 'close': 100}]},
        due_recommendation_ids=(1,), required_tickers=('AAPL',))
    assert not result.has_prices and not result.price_coverage_complete
    assert not prices.PriceHistoryLoadResult(price_history={'BENCHMARK': [1], '__BENCHMARK__': [1]}).has_prices


def test_local_prices_preserve_availability_clocks_and_exclude_conflicts(tmp_path):
    path = tmp_path / 'prices.json'
    path.write_text(json.dumps({'AAPL': [
        {'date': '2026-04-01', 'close': 100, 'available_at': '2026-04-02T12:00:00Z'},
        {'date': '2026-04-02', 'close': 101, 'observed_at': '2026-04-03T00:00:00Z'},
        {'date': '2026-04-03', 'close': 102}, {'close': 103}, {'date': 'bad', 'close': 104},
        {'date': '2026-03-31', 'close': 90}, {'date': '2026-03-31', 'close': 91},
        {'date': '2026-03-01', 'close': 80}]}), encoding='utf-8')
    result = prices.load_price_history_for_recommendations(tmp_path / 'absent.sqlite', provider='local_json',
        price_history_path=path, asof_date='2026-04-02', lookback_days=5)
    assert result.price_history == {'AAPL': [{'date': '2026-04-01', 'close': 100.0, 'available_at': '2026-04-02T12:00:00Z'}]}
    assert _normalize_price_history(result.price_history, asof_date='2026-04-01') == {}
    assert prices.load_price_history_json(path, asof_date='2026-04-02', lookback_days=5).price_history == result.price_history
    with pytest.raises(ValueError):
        prices.load_price_history_json(path)


def test_future_and_unverifiable_recommendations_do_not_request_prices(tmp_path, monkeypatch):
    db = tmp_path / 'perf.sqlite'
    initialize_action_tracker(db)
    with sqlite3.connect(db) as conn:
        for ticker, clock in [('AAPL', '2026-04-01T09:00:00Z'), ('MSFT', '2026-04-03T09:00:00Z'),
                              ('NVDA', '2026-04-02Tbad'), ('TSLA', '2026-04-02T09:00:00')]:
            conn.execute('INSERT INTO action_recommendations(run_id,ticker,action,created_at) VALUES (?,?,?,?)',
                         ('run', ticker, 'WATCH', clock))
    download = Mock(return_value=pd.DataFrame())
    monkeypatch.setitem(sys.modules, 'yfinance', SimpleNamespace(download=download))
    result = prices.load_price_history_for_recommendations(db, provider='yfinance', asof_date='2026-04-02')
    assert download.call_args.args == ('AAPL',)
    assert result.required_tickers == ('AAPL',) and result.missing_price_tickers == ('AAPL',)
    assert not result.price_coverage_complete


@pytest.mark.parametrize('complete', [True, False])
def test_runner_distinguishes_complete_and_partial_price_updates(tmp_path, monkeypatch, complete):
    config_path = tmp_path / 'config.toml'
    config_path.write_text('[run]\ntickers=["AAPL"]\n[storage]\narchive_dir="./archive"\nsite_dir="./site"\n'
                           '[performance]\nenabled=true\nupdate_outcomes_on_run=true\nprice_provider="yfinance"\n')
    config = load_scheduled_config(config_path)
    run_dir = tmp_path / 'run'
    run_dir.mkdir()
    history = {'AAPL': [{'date': '2026-04-01', 'close': 100}]}
    if complete:
        history['MSFT'] = [{'date': '2026-04-01', 'close': 200}]
    monkeypatch.setattr(runner, 'record_run_recommendations', Mock(return_value=2))
    monkeypatch.setattr(runner, 'summarize_action_performance', Mock(return_value={'recommendations': 2}))
    monkeypatch.setattr(runner, 'load_price_history_for_recommendations', Mock(return_value=prices.PriceHistoryLoadResult(
        price_history=history, provider='yfinance', due_recommendation_ids=(1, 2), required_tickers=('AAPL', 'MSFT'))))
    update = Mock()
    monkeypatch.setattr(runner, 'update_action_outcomes', update)
    result = runner._run_performance_tracking(config=config, run_dir=run_dir, started_at=datetime(2026, 4, 2, tzinfo=timezone.utc))
    update.assert_called_once()
    assert result['outcome_update']['updated'] is complete
    assert result['status'] == ('ok' if complete else 'recorded_pending_outcomes')
    assert result['outcome_update']['missing_price_tickers'] == ([] if complete else ['MSFT'])


@pytest.mark.parametrize('market,started,expected', [
    ('US', '2026-10-30T02:00:00+09:00', '2026-10-29'),
    ('US', '2026-10-29T17:00:00+00:00', '2026-10-29'),
    ('US', '2026-10-30T14:00:00+09:00', '2026-10-30'),
    ('KR', '2026-10-29T17:00:00+00:00', '2026-10-30'),
])
@pytest.mark.parametrize('empty', [False, True])
def test_runner_prices_and_outcomes_share_market_date_at_midnight(tmp_path, monkeypatch, market, started, expected, empty):
    config_path = tmp_path / 'config.toml'
    config_path.write_text(f'[run]\ntickers=["AAPL"]\nmarket="{market}"\n'
        '[storage]\narchive_dir="./archive"\nsite_dir="./site"\n'
        '[performance]\nenabled=true\nupdate_outcomes_on_run=true\nprice_provider="yfinance"\n')
    config = load_scheduled_config(config_path)
    run_dir = tmp_path / 'run'
    run_dir.mkdir()
    monkeypatch.setattr(runner, 'record_run_recommendations', Mock(return_value=1))
    monkeypatch.setattr(runner, 'summarize_action_performance', Mock(return_value={'recommendations': 1}))
    frame = pd.DataFrame() if empty else pd.DataFrame({('Close', 'AAPL'): [100, 101, 102, 103]},
        index=['2026-10-29', '2026-10-30', None, 'not-a-date'])
    download = Mock(return_value=frame)
    monkeypatch.setitem(sys.modules, 'yfinance', SimpleNamespace(download=download))
    seen = {}

    def load(*args, **kwargs):
        seen['price_date'] = kwargs['asof_date']
        history, _ = prices._fetch_yfinance_price_history(['AAPL'], benchmark_ticker=None,
            lookback_days=5, asof_date=kwargs['asof_date'])
        seen['history'] = history
        return prices.PriceHistoryLoadResult(price_history=history, provider='yfinance',
            due_recommendation_ids=(1,), required_tickers=('AAPL',))

    monkeypatch.setattr(runner, 'load_price_history_for_recommendations', load)
    update = Mock()
    monkeypatch.setattr(runner, 'update_action_outcomes', update)
    result = runner._run_performance_tracking(config=config, run_dir=run_dir,
        started_at=datetime.fromisoformat(started))
    assert seen['price_date'] == expected
    if empty:
        update.assert_not_called()
        assert result['status'] == 'recorded_pending_outcomes'
    else:
        assert all(row['date'] <= expected for row in seen['history']['AAPL'])
        assert update.call_args.kwargs['asof_date'] == expected
        assert len(seen['history']['AAPL']) == (1 if expected == '2026-10-29' else 2)


def test_performance_runner_rejects_naive_clock_before_recording_or_price_requests(tmp_path, monkeypatch):
    config_path = tmp_path / 'config.toml'
    config_path.write_text('[run]\ntickers=["AAPL"]\nmarket="US"\n'
        '[storage]\narchive_dir="./archive"\nsite_dir="./site"\n')
    config = load_scheduled_config(config_path)
    record = Mock(side_effect=AssertionError('unverifiable clock must not record'))
    fetch = Mock(side_effect=AssertionError('unverifiable clock must not fetch'))
    monkeypatch.setattr(runner, 'record_run_recommendations', record)
    monkeypatch.setattr(runner, 'load_price_history_for_recommendations', fetch)
    result = runner._run_performance_tracking(config=config, run_dir=tmp_path,
        started_at=datetime(2026, 10, 30, 2))
    assert result['status'] == 'failed'
    record.assert_not_called()
    fetch.assert_not_called()
