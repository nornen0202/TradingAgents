from datetime import timedelta
import json
import sqlite3

import pytest

from tradingagents.atomic_io import atomic_write_json
from tradingagents.execution import demo_roundtrip as rt
from tests.execution.test_demo_runtime import Harness


@pytest.fixture(params=['KR', 'US'])
def h(tmp_path, request, monkeypatch):
    harness = Harness(tmp_path, request.param)
    monkeypatch.setitem(rt.dv.MARKETS, 'KR', {**rt.dv.MARKETS['KR'], 'ticker': '005930'})
    atomic_write_json(harness.validation / 'roundtrip-enabled.json', {
        'enabled': True, 'mode': rt.MODE, 'real_orders_enabled': False, 'campaign_id': 'fixture-roundtrip',
        'authorized_at': harness.now.isoformat(), 'expires_at': (harness.now+timedelta(days=1)).isoformat()})
    return harness


def run(h, **kwargs):
    def session(market, now_local):
        return {'source': 'exchange_calendars', 'is_open': market == h.market, 'phase': 'regular',
                'session_open': (h.now-timedelta(minutes=20)).isoformat(),
                'session_close': (h.now+timedelta(hours=3)).isoformat()}
    return rt.run_roundtrip(h.archive, h.validation, clock=lambda: h.now,
        broker_factory=lambda market, path, clock: h.factory(market, path, clock, (h.ticker,), h.credentials.scope()),
        quote_loader=lambda market, clock: {**h.quote(market, h.ticker, clock), 'bid': h.price, 'ask': h.price}, account_loader=kwargs.pop('account_loader', h.account),
        session_resolver=kwargs.pop('session_resolver', session), **kwargs)['markets'][h.market]


def test_real_guarded_brokers_buy_fill_sell_fill_without_duplicate_or_strategy_result(h):
    assert run(h)['submitted_side'] == 'BUY'
    assert run(h)['legs'][0]['status'] == 'OPEN'
    assert len(h.orders) == 1
    h.fill()
    h.now += timedelta(seconds=5)
    result = run(h)
    assert result['submitted_side'] == 'SELL'
    assert result['legs'][0]['filled_quantity'] == 1
    h.fill('2')
    h.now += timedelta(seconds=5)
    result = run(h)
    assert result['status'] == 'VERIFIED'
    assert result['strategy_performance'] is False
    assert [leg['side'] for leg in result['legs']] == ['BUY', 'SELL']
    assert all(leg['source'] == 'KIS_DEMO_BROKER_REPORT' for leg in result['legs'])
    assert run(h)['status'] == 'VERIFIED'
    assert len(h.orders) == 2


def test_unknown_ack_is_not_retried_and_never_becomes_fill(h):
    h.lost = True
    run(h)
    assert run(h)['status'] == 'ATTENTION'
    assert len(h.orders) == 1


def test_sell_requires_current_sellable_holdings_even_after_campaign_fill(h):
    run(h); h.fill()
    def account(*args):
        result = h.account(*args)
        result['positions'][0]['sellable_quantity'] = 0
        return result
    result = run(h, account_loader=account)
    assert result['status'] == 'BLOCKED'
    assert len(h.orders) == 1
    assert run(h)['status'] == 'ATTENTION'  # no replay of a prepared submission


def test_closed_session_has_no_network_and_authorization_is_explicit(h):
    result = run(h, session_resolver=lambda **kw: {'source':'exchange_calendars','is_open':False,'phase':'closed'})
    assert result['status'] == 'WAITING_SESSION' and h.calls == []
    p=h.validation/'roundtrip-enabled.json'; config=json.loads(p.read_text());config['real_orders_enabled']=True
    atomic_write_json(p,config)
    assert rt.run_roundtrip(h.archive,h.validation,clock=lambda:h.now)['status']=='DISABLED'


def test_completion_after_close_uses_durable_fill_proof_and_rejects_tampering(h):
    run(h); h.fill(); run(h); h.fill('2')
    assert run(h)['status'] == 'VERIFIED'
    calls = list(h.calls)
    closed = lambda **kw: {'source': 'exchange_calendars', 'is_open': False, 'phase': 'closed'}
    assert run(h, session_resolver=closed)['status'] == 'VERIFIED'
    assert h.calls == calls
    path = h.validation / 'roundtrips/fixture-roundtrip' / f'{h.market.lower()}.sqlite'
    with sqlite3.connect(path) as db:
        db.execute('DELETE FROM paper_observations')
    assert run(h, session_resolver=closed)['status'] == 'BLOCKED'
    assert h.calls == calls


def test_forged_status_json_cannot_create_fill(h):
    atomic_write_json(h.validation / 'roundtrip-status.json', {
        'campaign_id': 'fixture-roundtrip', 'markets': {h.market: {'status': 'VERIFIED'}}})
    assert run(h)['submitted_side'] == 'BUY'
    assert len(h.orders) == 1


def test_expired_authorization_never_submits_and_completed_proof_remains_visible(h):
    h.now += timedelta(days=2)
    assert run(h)['blocker'] == 'AUTHORIZATION_EXPIRED'
    assert not h.calls
    h.now -= timedelta(days=2)
    run(h); h.fill(); run(h); h.fill('2')
    assert run(h)['status'] == 'VERIFIED'
    h.now += timedelta(days=2)
    calls = list(h.calls)
    assert run(h)['status'] == 'VERIFIED'
    assert h.calls == calls
