from datetime import datetime, timedelta
from dataclasses import replace
from types import SimpleNamespace
import json

import pytest

from tradingagents.scheduled import runner
from tradingagents.scheduled.config import load_scheduled_config
from tradingagents.execution.demo_runtime import candidates
from tests.execution.test_demo_runtime import Harness
from tests.test_scheduled_run_mode import _write_full_overlay_baseline, _fake_overlay_updates


def test_minute_source_survives_off_grid_delivery_without_retimestamping(tmp_path, monkeypatch):
    h = Harness(tmp_path, "US")
    h.now += timedelta(minutes=2, seconds=40)
    minute = h.now.replace(second=0, microsecond=0)
    config_path = tmp_path / 'config.toml'
    config_path.write_text('[run]\nmarket="US"\ntickers=["AAPL"]\n', encoding='utf-8')
    run = h.source()
    contract = run / 'contract.json'
    contract.write_text('{}')
    def fetch(ticker, **kwargs):
        # A real 1-minute source returns a distinct observation. The 5-minute
        # source would still be from 10:00; no publication clock is substituted.
        observed = minute if kwargs['interval'] == '1m' else minute.replace(minute=0)
        return SimpleNamespace(asof=observed.isoformat())
    monkeypatch.setattr(runner, 'fetch_intraday_market_snapshot', fetch)
    result = runner._fetch_overlay_market_snapshots(config=load_scheduled_config(config_path), run_dir=run,
        ticker_summaries=[{'ticker':h.ticker, 'status':'success', 'artifacts':{'execution_contract_json':'contract.json'}}], checkpoint_label='10:02')
    stamp = result[h.ticker].asof
    h.source(changes=lambda bundle: bundle['strategy_table'][0].update(market_data_asof=stamp))
    h.now += timedelta(seconds=30)
    rows = candidates(run, 'US', h.now, (h.ticker,))
    assert len(rows) == 1
    assert datetime.fromisoformat(rows[0]['signal']['valid_until']) == minute + timedelta(seconds=120)
    h.now = minute + timedelta(seconds=120)
    assert candidates(run, 'US', h.now, (h.ticker,)) == []


@pytest.mark.parametrize("lightweight", [False, True])
def test_overlay_does_not_render_identical_review_again_after_bundle(tmp_path, monkeypatch, lightweight):
    _write_full_overlay_baseline(tmp_path, tickers=['AAPL'])
    path = tmp_path / 'config.toml'
    path.write_text('[run]\nmarket="US"\ntickers=["AAPL"]\nrun_mode="overlay_only"\n'
        f'[storage]\narchive_dir="{tmp_path.as_posix()}"\nsite_dir="{(tmp_path / "site").as_posix()}"\n'
        '[execution]\nenabled=true\ncheckpoints_kst=["00:00"]\n', encoding='utf-8')
    monkeypatch.setattr(runner, 'collect_event_news', lambda **_: {})
    if lightweight:
        monkeypatch.setattr(runner, 'collect_event_news', lambda **_: pytest.fail('news belongs to scheduled research'))
        monkeypatch.setattr(runner, 'collect_event_signals', lambda **_: pytest.fail('selective rerun is disabled'))
    monkeypatch.setattr(runner, '_resolve_run_trade_date', lambda **_: '2026-10-16')
    def overlay(**kwargs):
        review = kwargs['run_dir'] / 'tickers/AAPL/investment_review.html'
        review.write_text('fresh checkpoint review', encoding='utf-8')
        kwargs['ticker_summaries'][0]['artifacts']['investment_review_html'] = 'tickers/AAPL/investment_review.html'
        return _fake_overlay_updates(**kwargs)
    monkeypatch.setattr(runner, '_run_execution_overlay_passes', overlay)
    monkeypatch.setattr(runner, '_refresh_integrated_review', lambda *a, **k: pytest.fail('duplicate review delays execution'))
    config = load_scheduled_config(path)
    config = replace(config, execution=replace(config.execution, execution_lightweight_refresh=lightweight))
    manifest = runner.execute_scheduled_run(config, skip_site_build=True)
    assert manifest['status'] == 'success'
    run = next(p.parent for p in (tmp_path / 'runs').glob('*/*/run.json') if json.loads(p.read_text(encoding='utf-8'))['run_id'] == manifest['run_id'])
    assert (run / 'tickers/AAPL/investment_review.html').read_text() == 'fresh checkpoint review'


@pytest.mark.parametrize('mode', ['full', 'overlay_only'])
def test_lightweight_cli_only_changes_explicit_overlay(tmp_path, monkeypatch, mode):
    path = tmp_path / 'config.toml'
    path.write_text('[run]\nmarket="US"\ntickers=["AAPL"]\n', encoding='utf-8')
    calls = []
    def execute(config, **kwargs):
        calls.append(config)
        return {'status':'success','run_id':'fixture','summary':{'successful_tickers':1,'failed_tickers':0}}
    monkeypatch.setattr(runner, 'execute_scheduled_run', execute)
    args = ['--config', str(path), '--run-mode', mode, '--lightweight-execution-refresh']
    if mode == 'full':
        with pytest.raises(SystemExit) as error:
            runner.main(args)
        assert error.value.code == 2 and not calls
    else:
        assert runner.main(args) == 0
        settings = calls[0].execution
        assert settings.execution_lightweight_refresh is True
        assert settings.execution_refresh_enabled is True
        assert settings.execution_selective_rerun_enabled is False
        assert settings.execution_max_data_age_seconds == 120
