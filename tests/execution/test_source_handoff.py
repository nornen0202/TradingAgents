from datetime import timedelta
import json
import sqlite3

import pytest

from tradingagents.atomic_io import atomic_write_json
from tradingagents.execution import paper_runtime, demo_runtime
from tradingagents.execution.source_handoff import await_completed_source
from tests.execution.test_paper_runtime import AT, Quotes, account, source
from tests.execution.test_demo_runtime import Harness
from tests.execution.test_demo_strategy_plan import native_source


def pending(root, old, market='kr', started=AT, **changes):
    value = {'market': market, 'status': 'STARTED', 'real_orders_enabled': False,
             'previous_source_run_id': old.name, 'started_at': started.isoformat()}
    atomic_write_json(root / 'execution-refresh' / f'{market}.json', {**value, **changes})


@pytest.mark.parametrize('publication', ['complete', 'absent', 'future', 'incomplete', 'wrong_market'])
def test_wait_is_bounded_and_only_selects_completed_current_market_source(tmp_path, publication):
    archive = tmp_path / 'archive'
    old = source(archive, AT - timedelta(seconds=125))
    original = {p: p.read_bytes() for p in old.rglob('*.json')}
    pending(tmp_path, old)
    elapsed = [0]
    def sleep(seconds):
        elapsed[0] += seconds
        if elapsed[0] == 5 and publication != 'absent':
            new = source(archive, AT + timedelta(seconds=60 if publication == 'future' else 5), name='zz-new')
            if publication == 'incomplete':
                (new / 'decision_bundle_v2.json').unlink()
            if publication == 'wrong_market':
                p = new / 'run.json'; d = json.loads(p.read_text()); d['settings']['market'] = 'US'
                atomic_write_json(p, d)
    selected, receipt = await_completed_source(archive, tmp_path, 'kr', old,
        clock=lambda: AT + timedelta(seconds=elapsed[0]), selector=paper_runtime._latest_source,
        sleep=sleep, monotonic=lambda: elapsed[0])
    assert selected.name == ('zz-new' if publication == 'complete' else old.name)
    assert elapsed[0] == (5 if publication == 'complete' else 15)
    assert receipt['prior_fresh_rows'] == 0
    assert receipt['outcome'] == ('NEW_COMPLETED_SOURCE' if publication == 'complete' else 'NO_NEW_COMPLETED_SOURCE')
    assert all(p.read_bytes() == data for p, data in original.items())


@pytest.mark.parametrize('change', [{'status': 'COMPLETED'}, {'real_orders_enabled': True},
    {'started_at': None}, {'started_at': 'bad'}, {'started_at': AT.replace(tzinfo=None).isoformat()},
    {'started_at': (AT + timedelta(seconds=1)).isoformat()},
    {'started_at': (AT - timedelta(seconds=120)).isoformat()}, {'previous_source_run_id': 'another'}, {'market': 'us'}])
def test_no_wait_without_matching_current_simulation_producer(tmp_path, change):
    old = source(tmp_path / 'archive', AT - timedelta(seconds=125))
    pending(tmp_path, old, **change)
    selected, receipt = await_completed_source(tmp_path / 'archive', tmp_path, 'kr', old,
        clock=lambda: AT, selector=lambda *a: pytest.fail('must not poll'), sleep=lambda *a: pytest.fail('must not wait'))
    assert selected == old and receipt is None


@pytest.mark.parametrize('stop', ['none', 'wrong_account', 'session', 'account'])
def test_paper_rebuilds_after_wait_and_rechecks_account_and_close(tmp_path, monkeypatch, stop):
    archive, state = tmp_path / 'archive', tmp_path / 'paper'
    old = source(archive, AT - timedelta(seconds=125)); pending(tmp_path, old)
    now, elapsed = [AT], [0]
    def sleep(seconds):
        elapsed[0] += seconds; now[0] += timedelta(seconds=seconds)
        if elapsed[0] == 5:
            new = source(archive, now[0], name='zz-new')
            if stop == 'wrong_account':
                p = new / 'portfolio-private/account_snapshot.json'; d = json.loads(p.read_text())
                d['account_id'] = 'another'; atomic_write_json(p, d)
    monkeypatch.setattr(paper_runtime, 'await_completed_source',
        lambda *a, **k: await_completed_source(*a, **k, sleep=sleep, monotonic=lambda: elapsed[0]))
    result = paper_runtime.advance_market(archive, state, 'kr', now=AT, clock=lambda: now[0],
        account_loader=lambda _: account(AT - timedelta(seconds=119) if stop == 'account' else AT),
        quote_factory=lambda: Quotes(lambda: now[0]),
        session_resolver=lambda **k: {'is_open': True, 'session_close': (AT + timedelta(seconds=3 if stop == 'session' else 600)).isoformat()})
    assert result['source_refresh_handoff']['waited_seconds'] == 5
    with sqlite3.connect(archive / 'paper/kr.sqlite') as db:
        assert db.execute("select count(*) from orders where status='PENDING'").fetchone()[0] == (1 if stop == 'none' else 0)
    if stop == 'none':
        assert result['source_run_id'] == 'zz-new'
        assert result['source_diagnostics']['fresh_rows'] == 1
    else:
        assert result['status'] in {'BLOCKED', 'MARKET_CLOSED'}


@pytest.mark.parametrize('market', ['KR', 'US'])
@pytest.mark.parametrize('stop', ['none', 'session', 'gate', 'scope'])
@pytest.mark.parametrize('native', [False, True])
def test_demo_wait_revalidates_session_and_scope_before_real_guarded_mock_broker(tmp_path, monkeypatch, market, stop, native):
    h = Harness(tmp_path, market); original_now = h.now
    h.now -= timedelta(seconds=125)
    old = native_source(h)[0] if native else h.source()
    h.now = original_now
    pending(h.root.parent, old, market.lower(), h.now)
    elapsed = [0]
    def sleep(seconds):
        h.now += timedelta(seconds=seconds); elapsed[0] += seconds
        if elapsed[0] == 5:
            native_source(h, 'zz-new') if native else h.source('zz-new')
            if stop == 'gate': h.gate_open = False
    monkeypatch.setattr(demo_runtime, 'await_completed_source',
        lambda *a, **k: await_completed_source(*a, **k, sleep=sleep, monotonic=lambda: elapsed[0]))
    def session(**kwargs):
        return {'source': 'exchange_calendars', 'phase': 'regular', 'is_open': True,
            'session_open': (original_now - timedelta(minutes=30)).isoformat(),
            'session_close': (original_now + timedelta(seconds=3 if stop == 'session' and elapsed[0] else 3600)).isoformat()}
    def gate(root, current_market, now):
        scope = h.gate(root, current_market, now)
        return 'changed-owner' if stop == 'scope' and elapsed[0] else scope
    result = h.tick(session_resolver=session, gate=gate)
    assert result['source_refresh_handoff']['waited_seconds'] == 5
    assert len(h.orders) == (1 if stop == 'none' else 0)
    if stop == 'none':
        assert result['source_run_id'] == 'zz-new'
        assert result['source_diagnostics']['fresh_rows'] == 1
    else:
        assert result['blockers']


@pytest.mark.parametrize('market', ['KR', 'US'])
@pytest.mark.parametrize('phase', ['entry', 'exit', 'pending'])
def test_existing_order_reconciliation_and_valid_entry_exit_never_wait(tmp_path, monkeypatch, market, phase):
    h = Harness(tmp_path, market)
    monkeypatch.setattr(demo_runtime, 'await_completed_source', lambda *a, **k: pytest.fail('valid action/reconciliation must not wait'))
    h.tick()
    assert len(h.orders) == 1
    if phase == 'pending':
        h.now += timedelta(seconds=125)
        h.tick()
        assert len(h.orders) == 1
    elif phase == 'exit':
        h.fill(); h.now += timedelta(seconds=1)
        h.tick()
        h.source('zz-exit', action='EXIT_NOW')
        h.tick()
        assert len(h.orders) == 2 and h.orders['2']['side'] == 'SELL'


def test_clock_regression_during_wait_fails_closed(tmp_path):
    old = source(tmp_path / 'archive', AT - timedelta(seconds=125))
    pending(tmp_path, old)
    moments = iter([AT, AT - timedelta(seconds=1)])
    with pytest.raises(ValueError, match='SOURCE_HANDOFF_CLOCK_REGRESSED'):
        await_completed_source(tmp_path / 'archive', tmp_path, 'kr', old,
            clock=lambda: next(moments), selector=lambda *a: pytest.fail('must not select'),
            sleep=lambda *a: pytest.fail('must not wait'))
