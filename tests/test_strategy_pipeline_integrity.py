from __future__ import annotations

import copy
import json
from datetime import datetime, timedelta, timezone

import pytest

from tradingagents.work import packet
from tradingagents.work.runtime import WorkRuntimeError, _validate_report_thesis_direction
from tradingagents.scheduled.mobile_site import (
    _sanitize_work_report_value, _strip_strategy_identifiers,
    _work_report_lineage, assert_strategy_payload_safe,
)
from tradingagents.execution.risk_trigger import risk_condition_text, risk_trigger
from tradingagents.scheduled.attempts import RunAttempt, latest_full_attempt


@pytest.mark.parametrize("text,old_action,expected", [
    ("📈 신규 매수: RF머트리얼즈(327260)\n손절가: 48,750원", "STOP_LOSS", "BUY"),
    ("📊 실시간 포트폴리오\nRF머트리얼즈(327260)\n손절가: 48,750원", "STOP_LOSS", "HOLD"),
    ("⚠️ [KR] 매수 후보 분석 실패\n대상: 한온시스템(018880): 실패 / RF머트리얼즈(327260): 실패", "BUY", "UNKNOWN"),
])
def test_archived_prism_actions_rechecked_without_mutating_history(tmp_path, text, old_action, expected):
    signals_path = tmp_path / "signals.json"
    historical = json.dumps({"signals": [{"canonical_ticker": "327260", "market": "KR",
                                         "signal_action": old_action, "confidence": .7}]})
    signals_path.write_text(historical, encoding="utf-8")
    (tmp_path / "metadata.json").write_text(json.dumps({"text": text}), encoding="utf-8")
    event = packet._prism_event("channel", {"message_id": "42", "signals_path": "signals.json",
                                          "metadata_path": "metadata.json"}, tmp_path)
    summary = event["summary"]
    assert summary["signals"][0]["signal_action"] == expected
    assert summary["signals"][0]["confidence"] == .7
    assert summary["normalization"]["action_changes"] == [
        {"ticker": "327260", "before": old_action, "after": expected}
    ]
    if expected == "UNKNOWN":
        assert set(event["relevance"]["tickers"]) == {"327260", "018880.KS"}
        assert summary["normalization"]["recovered_tickers"] == ["018880.KS"]
    assert signals_path.read_text(encoding="utf-8") == historical


def test_archived_prism_missing_text_keeps_normalized_signals(tmp_path):
    (tmp_path / "signals.json").write_text(json.dumps({"signals": [
        {"canonical_ticker": "ABC", "signal_action": "WATCH"}
    ]}), encoding="utf-8")
    event = packet._prism_event("channel", {"message_id": "42", "signals_path": "signals.json",
                                          "metadata_path": "../private.json"}, tmp_path)
    assert event["summary"]["signals"][0]["signal_action"] == "WATCH"
    assert event["summary"]["normalization"]["status"] == "NO_ARCHIVED_TEXT"


def test_present_hold_does_not_mean_hold_after_support_failure():
    text = risk_condition_text('HOLD', {'price': 70700, 'level_type': 'SUPPORT', 'confirmation': 'close'}, '보유 유지')
    assert '70,700 이하 하락' in text
    assert '보유 유지' not in text
    assert '위험 대응 계획 재확인' in text


def test_changed_strategy_assets_get_new_urls_for_cached_browsers(monkeypatch):
    import re
    from tradingagents.scheduled import mobile_site
    def assets(desktop=False):
        html = mobile_site._private_html(desktop=desktop)
        return re.findall(r'(?:src|href)="([^"]+\.(?:js|css)\?v=[^"]+)"', html)
    original = assets()
    assert len(original) == 2
    assert assets() == original
    monkeypatch.setattr(mobile_site, '_PRIVATE_JS', mobile_site._PRIVATE_JS + '\n// changed')
    assert assets()[0] == original[0]
    assert assets()[1] != original[1]
    monkeypatch.setattr(mobile_site, '_MOBILE_CSS', mobile_site._MOBILE_CSS + '\n/* changed */')
    assert assets()[0] != original[0]
    assert assets(desktop=True) == ['mobile/' + url for url in assets()]


def _run(root, run_id, when, *, parent=None, calls=0):
    directory = root / 'runs/2026' / run_id
    directory.mkdir(parents=True)
    decision = {'rating': 'HOLD', 'portfolio_stance': 'BULLISH', 'entry_action': 'WAIT',
                'conditional_entry_action': 'STARTER', 'risk_action': 'REDUCE_RISK',
                'risk_action_level': {'price': 90, 'level_type': 'SUPPORT', 'confirmation': 'close'},
                'watchlist_triggers': ['Close above 100 with volume confirmation'],
                'invalidators': ['Close below 90'], 'confidence': .7}
    manifest = {'run_id': run_id, 'started_at': when, 'finished_at': when, 'status': 'success',
                'settings': {'market': 'us', 'run_mode': 'overlay_only' if parent else 'full'},
                'tickers': [{'ticker': 'ABC', 'trade_date': '2026-09-28', 'analysis_date': '2026-09-29',
                             'finished_at': '2026-09-29T12:00:00+00:00', 'decision': decision}],
                'llm_usage': {'calls': calls, 'by_model': {'model': {'calls': calls}}}}
    if parent:
        manifest['overlay_source_run_id'] = parent
    (directory / 'run.json').write_text(json.dumps(manifest), encoding='utf-8')
    bundle = {'run_id': run_id, 'analysis_source_run_id': parent or run_id,
              'quality': {}, 'strategy_table': [{'ticker': 'ABC', 'is_held': True,
              'strategy_code': 'DATA_CHECK', 'market_data_asof': when,
              'quality': {'row_mode': 'BLOCKED_STALE'}}]}
    (directory / 'decision_bundle_v2.json').write_text(json.dumps(bundle), encoding='utf-8')
    return manifest, bundle


def test_fresh_stale_fresh_keeps_all_analysis_axes(tmp_path):
    manifest, bundle = _run(tmp_path, 'full', '2026-09-29T12:00:00+00:00')
    theses = []
    for code, mode in [('BUY_ON_CONFIRMATION', 'CONDITIONAL'), ('DATA_CHECK', 'BLOCKED_STALE'), ('BUY_NOW', 'IMMEDIATE')]:
        current = copy.deepcopy(bundle)
        current['strategy_table'][0].update(strategy_code=code, quality={'row_mode': mode})
        packet._attach_analysis_theses(current, manifest, manifest)
        row = packet._compact_market_row(current['strategy_table'][0], 1)
        theses.append(row['thesis'])
        assert row['execution']['readiness'] == {'CONDITIONAL': 'WAIT_FOR_TRIGGER', 'BLOCKED_STALE': 'NEEDS_LIVE_RECHECK', 'IMMEDIATE': 'READY_NOW'}[mode]
    assert theses[0] == theses[1] == theses[2]
    assert theses[0]['stance'] == 'BUY'
    assert theses[0]['rating'] == 'HOLD'
    assert theses[0]['entry_action'] == 'WAIT'
    assert theses[0]['risk_action'] == 'REDUCE_RISK'
    assert theses[0]['risk_action_level']['price'] == 90


def test_downside_watchlist_trigger_is_not_a_buy_entry_condition(tmp_path):
    manifest, bundle = _run(tmp_path, 'full', '2026-09-29T12:00:00+00:00')
    decision = manifest['tickers'][0]['decision']
    decision['entry_logic'] = 'Buy only after close above 100 and relative volume at least 1.2.'
    decision['watchlist_triggers'].append('Close below 90 means reduce the existing position.')
    packet._attach_analysis_theses(bundle, manifest, manifest)
    thesis = bundle['strategy_table'][0]['thesis']
    assert thesis['entry_conditions'] == [decision['entry_logic']]
    assert thesis['observation_conditions'] == decision['watchlist_triggers']
    assert thesis['invalidation_conditions'] == ['Close below 90']


@pytest.mark.parametrize(('rating', 'expected'), [('OVERWEIGHT', 'BUY'), ('UNDERWEIGHT', 'REDUCE'), ('NO_TRADE', 'AVOID')])
def test_legacy_ratings_are_explicitly_mapped(tmp_path, rating, expected):
    manifest, bundle = _run(tmp_path, 'full', '2026-09-29T12:00:00+00:00')
    manifest['tickers'][0]['decision'].update(rating=rating, conditional_entry_action='NONE')
    packet._attach_analysis_theses(bundle, manifest, manifest)
    assert bundle['strategy_table'][0]['thesis']['stance'] == expected


def test_us_bulk_hold_overwrite_is_rejected_but_bound_revision_is_allowed():
    source = {'thesis': {'stance': 'BUY'}}
    strategy = {'thesis': {'stance': 'HOLD'}}
    with pytest.raises(WorkRuntimeError, match='stance_change'):
        _validate_report_thesis_direction(strategy, source, ticker='ABC')
    strategy['thesis']['stance_change'] = {'from': 'BUY', 'to': 'HOLD', 'reason': 'New disclosed demand risk',
                                          'evidence': [{'source': 'prism', 'event_key': 'e1', 'finding': 'Demand outlook reduced'}]}
    with pytest.raises(WorkRuntimeError, match='stance_change'):
        _validate_report_thesis_direction(strategy, source, ticker='ABC')
    strategy['source_contributions'] = [{'source': 'prism', 'event_key': 'e1'}]
    _validate_report_thesis_direction(strategy, source, ticker='ABC')
    strategy['source_contributions'] = [{'source': 'tradingagents', 'event_key': 'e1'}]
    strategy['thesis']['stance_change']['evidence'][0]['source'] = 'tradingagents'
    with pytest.raises(WorkRuntimeError, match='stance_change'):
        _validate_report_thesis_direction(strategy, source, ticker='ABC')


def test_multi_hop_analysis_receipt_and_model_usage(tmp_path):
    _run(tmp_path, 'full', '2026-09-29T12:00:00+00:00', calls=1510)
    _run(tmp_path, 'overlay1', '2026-09-29T13:00:00+00:00', parent='full', calls=2)
    _run(tmp_path, 'overlay2', '2026-09-29T14:00:00+00:00', parent='overlay1', calls=3)
    current = packet.build_surface_packet('us', archive_dir=tmp_path, now=datetime(2026, 9, 29, 14, 5, tzinfo=timezone.utc))
    body = current['body']
    assert body['model_provenance']['market_analysis']['source_run_id'] == 'full'
    assert body['model_provenance']['market_analysis']['observed_calls'] == 1510
    assert body['model_provenance']['overlay']['observed_calls'] == 3
    assert body['model_provenance']['work_synthesis']['verification_status'] == 'CONFIGURED_NOT_RUNTIME_VERIFIED'
    report = {'workflow_contract_sha256': current['workflow_contract_sha256'],
              'structured_report': {'coverage_receipt': {'source_run_id': 'overlay0'},
              'source_summary': {'analysis_receipt': body['current']['analysis_receipt']},
              'strategies': [{'ticker': 'ABC'}]}}
    assert _work_report_lineage(report, current)['status'] == 'CURRENT_ANALYSIS_LINEAGE'
    changed = copy.deepcopy(report)
    changed['structured_report']['source_summary']['analysis_receipt']['decisions']['ABC'] = 'different'
    assert _work_report_lineage(changed, current)['status'] == 'PAST_REFERENCE'
    changed = copy.deepcopy(report)
    changed['structured_report']['strategies'] = [{'ticker': 'NEW'}]
    assert _work_report_lineage(changed, current)['status'] == 'PAST_REFERENCE'
    changed = copy.deepcopy(report)
    changed['workflow_contract_sha256'] = 'old'
    assert _work_report_lineage(changed, current)['status'] == 'PAST_REFERENCE'


def test_discovery_membership_is_producer_owned():
    bundle = {'strategy_table': [{'ticker': 'HELD', 'is_held': True}, {'ticker': 'WATCH'}, {'ticker': 'NEW'}]}
    rows = packet.compact_decision_bundle(bundle, required_watchlist_tickers=['WATCH'])['strategy_table']
    assert {row['ticker']: row['portfolio_role'] for row in rows} == {'HELD': 'holding', 'WATCH': 'watchlist', 'NEW': 'discovery'}


def test_sanitizer_preserves_urls_and_machine_values_and_redacts_private_paths():
    value = {'stance': 'HOLD', 'readiness': 'NEEDS_LIVE_RECHECK', 'affected_field': 'confidence',
             'url': 'https://www.youtube.com/watch?v=123&한글=기업',
             'source_url': 'https://example.com/home/research?q=yes',
             'note': 'Saved at C:\\Users\\private\\file.txt', 'secret': 'api_key=secret123'}
    clean = _sanitize_work_report_value(_strip_strategy_identifiers(value))
    for key in ('stance', 'readiness', 'affected_field', 'url', 'source_url'):
        assert clean[key] == value[key]
    assert 'private' not in clean['note'] and 'secret123' not in clean.get('secret', '')
    assert_strategy_payload_safe(clean)


@pytest.mark.parametrize(('action', 'kind', 'price', 'operator', 'word'), [
    ('TAKE_PROFIT', 'RESISTANCE', 130300, '>=', '이상 도달'),
    ('STOP_LOSS', 'SUPPORT', 90, '<=', '이하 하락'),
    ('REDUCE_RISK', 'RESISTANCE', 110, '>=', '이상 도달'),
])
@pytest.mark.parametrize('confirmation', ['intraday', 'close', 'two_bar', 'next_day'])
def test_risk_wording_matches_shared_evaluator(action, kind, price, operator, word, confirmation):
    level = {'price': price, 'level_type': kind, 'confirmation': confirmation}
    assert risk_trigger(action, level)['comparator'] == operator
    text = risk_condition_text(action, level, '축소')
    assert word in text
    if confirmation == 'close':
        assert '종가 확인 후' in text


def test_failed_and_interrupted_attempt_do_not_replace_completed_cohort(tmp_path):
    now = datetime.now(timezone.utc)
    _run(tmp_path, 'full', (now - timedelta(hours=2)).isoformat())
    path = tmp_path / 'runs/2026/failing'
    path.mkdir()
    with pytest.raises(RuntimeError):
        with RunAttempt(path, market='us', run_mode='full', started_at=now):
            assert latest_full_attempt(tmp_path, 'us', now=now + timedelta(seconds=1))['status'] == 'RUNNING'
            raise RuntimeError('runner lost')
    assert not (path / 'run.json').exists()
    assert latest_full_attempt(tmp_path, 'us', now=now)['status'] == 'FAILED'
    current = packet.build_surface_packet('us', archive_dir=tmp_path, now=now)['body']['current']
    assert current['run_id'] == 'full'
    assert current['latest_attempt']['run_id'] == 'failing'
    assert current['latest_completed_analysis']['run_id'] == 'full'
    state = json.loads((path / 'attempt.json').read_text())
    state.update(status='RUNNING', heartbeat_at=(now - timedelta(minutes=6)).isoformat())
    (path / 'attempt.json').write_text(json.dumps(state))
    assert latest_full_attempt(tmp_path, 'us', now=now)['status'] == 'INTERRUPTED'


def test_sec_filings_preserve_publication_and_retrieval_times(monkeypatch):
    from tradingagents.dataflows import sec_edgar as sec
    monkeypatch.setattr(sec, '_ticker_map', lambda day: {'ABC': '0000000001'})
    monkeypatch.setattr(sec, '_submissions', lambda cik, hour: {'entityType': 'operating', 'filings': {'recent': {
        'accessionNumber': ['0000000001-26-000001', '0000000001-26-000002'],
        'filingDate': ['2026-09-20', '2026-10-10'], 'acceptanceDateTime': ['2026-09-20T12:00:00Z', '2026-10-10T12:00:00Z'],
        'form': ['8-K', '10-Q'], 'primaryDocDescription': ['Current report', 'Quarterly report']}}})
    report = sec.get_disclosures_sec_edgar('ABC', '2026-09-01', '2026-09-30')
    assert 'observed=1' in report and 'CORPORATE_FILINGS' in report
    assert 'accepted 2026-09-20' in report and 'retrieved' in report
    assert 'https://www.sec.gov/Archives/edgar/data/1/' in report
    assert '10-Q' not in report
    assert 'VERIFIED_ZERO' in sec.get_disclosures_sec_edgar('ABC', '2026-09-21', '2026-09-22')


def test_sec_fund_and_unmapped_are_not_corporate_zero(monkeypatch):
    from tradingagents.dataflows import sec_edgar as sec
    monkeypatch.setattr(sec, '_ticker_map', lambda day: {})
    monkeypatch.setattr(sec, '_fund_map', lambda day: {'FUND': '0000000002'})
    monkeypatch.setattr(sec, '_submissions', lambda cik, hour: {'entityType': 'investment', 'filings': {'recent': {'accessionNumber': [], 'filingDate': []}}})
    assert 'FUND_FILINGS' in sec.get_disclosures_sec_edgar('FUND', '2026-09-01', '2026-09-30')
    assert 'UNMAPPED_INSTRUMENT' in sec.get_disclosures_sec_edgar('UNKNOWN', '2026-09-01', '2026-09-30')


def test_source_coverage_does_not_hide_missing_fred_behind_model_success():
    result = packet._source_coverage({'status': 'success', 'tool_telemetry': {'events': [
        {'method': 'get_macro_indicators', 'vendor': 'fred', 'status': 'fallback', 'fallback': True, 'note': 'FRED_API_KEY not set'},
        {'method': 'get_disclosures', 'vendor': 'sec_edgar', 'status': 'verified_zero'},
        {'method': 'get_social_sentiment', 'vendor': 'yfinance', 'status': 'success'},
    ]}})
    assert result['get_macro_indicators']['status'] == 'UNAVAILABLE'
    assert result['get_macro_indicators']['missing_configuration']
    assert result['get_disclosures']['status'] == 'VERIFIED_ZERO'
    assert result['get_social_sentiment']['source_type'] == 'NEWS_DERIVED'


def test_deploy_guard_rejects_corrupted_enums_and_false_reference_enrichment():
    from tradingagents.scheduled.mobile_site import assert_strategy_semantics
    with pytest.raises(ValueError, match='canonical enum'):
        assert_strategy_semantics({'markets': {'us': {'rows': [{'ticker': 'ABC', 'thesis': {'stance': '보유'}}]}}})
    with pytest.raises(ValueError, match='reference'):
        assert_strategy_semantics({'markets': {'us': {'integrated_report': {'lineage': {'current_action_cards_enriched': False}}}}})


def test_archive_display_reclassifies_loss_and_keeps_upside_risk_trigger():
    from tradingagents.scheduled.mobile_site import _normalize_private_action_semantics
    row = _normalize_private_action_semantics({'risk_action': 'TAKE_PROFIT', 'action_if_triggered': 'TAKE_PROFIT_IF_TRIGGERED',
          'position_metrics': {'unrealized_return_pct': -22}, 'risk_action_level': {'price': 130300, 'level_type': 'TAKE_PROFIT'}})
    assert row['risk_action'] == 'REDUCE_RISK'
    assert row['action_if_triggered'] == 'REDUCE_IF_TRIGGERED'
    assert risk_trigger(row['risk_action'], row['risk_action_level'])['comparator'] == '>='
