"""Report projection preserves source clocks and producer validity limits."""
from datetime import datetime, timedelta, timezone
import json

import pytest

from tradingagents.work import freshness, packet
from tests.test_chatgpt_work import _write_market_run


AT = datetime(2026, 7, 14, 14, 0, tzinfo=timezone.utc)


@pytest.mark.parametrize("value,seconds", [(120, 120), (180, 180), (900, 600),
    (None, 0), (True, 0), (0, 0), (-1, 0), ("bad", 0), ("NaN", 0), ("inf", 0)])
def test_source_age_cannot_be_extended_or_invalid(value, seconds):
    assert freshness.source_execution_max_age({'settings': {
        'execution_max_data_age_seconds': value}}).total_seconds() == seconds
    assert freshness.source_execution_max_age({}).total_seconds() == 600


@pytest.mark.parametrize("public", [False, True])
@pytest.mark.parametrize("elapsed,expired", [(119, False), (120, True), (180, True)])
def test_real_packet_preserves_producer_120_second_expiry(tmp_path, public, elapsed, expired):
    run = _write_market_run(tmp_path, run_id='source', market='us',
        started_at=AT.isoformat(), row_mode='IMMEDIATE')
    manifest_path = run / 'run.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    manifest['status'] = 'success'
    manifest['active_universe'] = {'expected_watchlist_tickers': ['NVDA'], 'scanner_candidates': []}
    manifest['settings']['execution_max_data_age_seconds'] = 120
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
    before = (run / 'decision_bundle_v2.json').read_bytes()
    body = packet.build_surface_packet('us', archive_dir=tmp_path,
        now=AT + timedelta(seconds=elapsed), public=public)['body']
    receipt = body['current']['freshness_receipt']
    assert receipt['execution_max_age_seconds'] == 120
    assert receipt['market_data_status'] == ('STALE' if expired else 'FRESH')
    assert body['guardrails']['valid_until'] == (AT + timedelta(seconds=120)).isoformat()
    assert body['guardrails']['expired_at_build'] is expired
    assert (run / 'decision_bundle_v2.json').read_bytes() == before
    if not public:
        row = body['current']['bundle']['strategy_table'][0]
        assert row['execution']['valid_until'] == (AT + timedelta(seconds=120)).isoformat()
        if expired:
            assert row['execution']['action_now'] is None
            assert row['quality']['execution_ready'] is False


@pytest.mark.parametrize("field", ['quality', 'execution'])
@pytest.mark.parametrize("value", [(AT + timedelta(seconds=60)).isoformat(), 'bad', None])
def test_explicit_row_validity_is_not_replaced_with_longer_window(field, value):
    row = {'market_data_asof': AT.isoformat(), 'quality': {'row_mode': 'IMMEDIATE', 'execution_ready': True}}
    row.setdefault(field, {})['row_valid_until' if field == 'quality' else 'valid_until'] = value
    bundle = {'strategy_table': [row]}
    packet._apply_market_row_validity(bundle, now=AT + timedelta(seconds=70), max_age=timedelta(seconds=120))
    packet._apply_market_row_validity(bundle, now=AT + timedelta(seconds=70), max_age=timedelta(seconds=120))
    assert row['execution']['valid_until'] == (value if value not in ['bad', None] else None)
    assert row['execution']['action_now'] is None
    assert row['quality']['execution_ready'] is False
