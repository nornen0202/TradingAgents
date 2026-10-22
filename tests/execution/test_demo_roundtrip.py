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
        quote_loader=kwargs.pop('quote_loader', lambda market, clock: {**h.quote(market, h.ticker, clock), 'bid': h.price, 'ask': h.price}), account_loader=kwargs.pop('account_loader', h.account),
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
    run(h)
    h.fill()
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
    p=h.validation/'roundtrip-enabled.json'
    config=json.loads(p.read_text())
    config['real_orders_enabled']=True
    atomic_write_json(p,config)
    assert rt.run_roundtrip(h.archive,h.validation,clock=lambda:h.now)['status']=='DISABLED'


def test_completion_after_close_uses_durable_fill_proof_and_rejects_tampering(h):
    run(h)
    h.fill()
    run(h)
    h.fill('2')
    assert run(h)['status'] == 'VERIFIED'
    calls = list(h.calls)
    def closed(**kw):
        return {'source': 'exchange_calendars', 'is_open': False, 'phase': 'closed'}
    assert run(h, session_resolver=closed)['status'] == 'VERIFIED'
    assert h.calls == calls
    path = h.validation / 'roundtrips/fixture-roundtrip' / f'{h.market.lower()}.sqlite'
    with sqlite3.connect(path) as db:
        db.execute('DELETE FROM paper_observations')
    assert run(h, session_resolver=closed)['status'] == 'BLOCKED'
    assert h.calls == calls


@pytest.mark.parametrize('damage', [
    'wrong_broker', 'missing_broker', 'future_ingestion', 'missing_ingestion',
    'bad_ingestion', 'ingestion_before_observation', 'different_observation',
    'missing_observation', 'invalid_amount', 'nonfinite_amount', 'request_after_expiry',
])
def test_completed_roundtrip_requires_matching_broker_and_available_report(h, damage):
    run(h)
    h.fill()
    h.now += timedelta(seconds=5)
    run(h)
    h.fill('2')
    h.now += timedelta(seconds=5)
    assert run(h)['status'] == 'VERIFIED'
    with sqlite3.connect(journal(h)) as db:
        if damage == 'request_after_expiry':
            config = json.loads(db.execute("SELECT value FROM roundtrip_control WHERE key='authorization'").fetchone()[0])
            db.execute('UPDATE requests SET created_at=?', (config['expires_at'],))
            h.now += timedelta(days=2)
        else:
            for identity, observed, raw in db.execute('SELECT id,observed_at,evidence FROM paper_observations').fetchall():
                evidence = json.loads(raw)
                if evidence['status'] != 'FILLED':
                    continue
                if damage == 'wrong_broker':
                    evidence['broker_order_id'] = 'unrelated'
                elif damage == 'missing_broker':
                    evidence.pop('broker_order_id')
                elif damage == 'future_ingestion':
                    evidence['ingested_at'] = (h.now + timedelta(seconds=1)).isoformat()
                elif damage == 'missing_ingestion':
                    evidence.pop('ingested_at')
                elif damage == 'bad_ingestion':
                    evidence['ingested_at'] = 'invalid'
                elif damage == 'ingestion_before_observation':
                    evidence['ingested_at'] = (rt.dv._at(observed) - timedelta(seconds=1)).isoformat()
                elif damage == 'different_observation':
                    evidence['observed_at'] = (rt.dv._at(observed) - timedelta(seconds=1)).isoformat()
                elif damage == 'missing_observation':
                    evidence.pop('observed_at')
                else:
                    evidence['fill_notional'] = -1 if damage == 'invalid_amount' else float('nan')
                db.execute('UPDATE paper_observations SET evidence=? WHERE id=? AND observed_at=?',
                           (json.dumps(evidence), identity, observed))
    calls = list(h.calls)
    assert run(h, session_resolver=lambda **kw: {'source': 'exchange_calendars', 'is_open': False, 'phase': 'closed'})['status'] == 'BLOCKED'
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
    run(h)
    h.fill()
    run(h)
    h.fill('2')
    assert run(h)['status'] == 'VERIFIED'
    h.now += timedelta(days=2)
    calls = list(h.calls)
    assert run(h)['status'] == 'VERIFIED'
    assert h.calls == calls


def journal(h):
    return h.validation / 'roundtrips/fixture-roundtrip' / f'{h.market.lower()}.sqlite'


def cancel_open_leg(h):
    h.now += timedelta(minutes=5)
    assert run(h)['legs'][-1]['status'] == 'OPEN'  # cancel acknowledgement only
    h.now += timedelta(seconds=5)
    assert run(h)['legs'][-1]['status'] == 'CANCELLED'


def test_confirmed_cancel_recovers_in_same_ledger_without_changing_prior_terms(h):
    run(h)
    with sqlite3.connect(journal(h)) as db:
        original = db.execute('SELECT * FROM paper_intents').fetchall()
        policy = db.execute('SELECT * FROM paper_policy').fetchall()
    cancel_open_leg(h)
    assert len(h.orders) == 1
    assert run(h)['submitted_side'] == 'BUY'
    with sqlite3.connect(journal(h)) as db:
        assert db.execute('SELECT * FROM paper_intents ORDER BY created_at LIMIT 1').fetchall() == original
        assert db.execute('SELECT * FROM paper_policy').fetchall() == policy
        assert db.execute('SELECT id FROM paper_intents ORDER BY created_at DESC LIMIT 1').fetchone()[0].endswith(':BUY:attempt-2')
    h.fill('2')
    h.now += timedelta(seconds=5)
    result = run(h)
    assert result.get('submitted_side') == 'SELL', result
    h.fill('3')
    h.now += timedelta(seconds=5)
    assert run(h)['status'] == 'VERIFIED'
    assert run(h)['status'] == 'VERIFIED' and len(h.orders) == 3


def test_two_order_policy_reserves_exit_and_waits_until_next_trading_day(h, monkeypatch):
    from tradingagents.execution.kis_paper import PaperOrderPolicy
    from tradingagents.execution.kis_paper_us import USPaperOrderPolicy
    import tests.execution.test_demo_runtime as harness_module
    policy = PaperOrderPolicy if h.market == 'KR' else USPaperOrderPolicy
    monkeypatch.setattr(harness_module, policy.__name__, lambda *a, **kw: policy(*a, **{**kw, 'max_daily_orders': 2}))
    original_request = h.request
    def dated_reports(method, url, **kwargs):
        response = original_request(method, url, **kwargs)
        if url.endswith('inquire-ccnl'):
            requested = kwargs['params']['ORD_STRT_DT']
            response.payload['output'] = [row for row in response.payload['output'] if row['ord_dt'] == requested]
        return response
    monkeypatch.setattr(h, 'request', dated_reports)
    run(h)
    cancel_open_leg(h)
    assert run(h)['status'] == 'WAITING_POLICY_CAPACITY'
    assert len(h.orders) == 1
    with sqlite3.connect(journal(h)) as db:
        assert db.execute("SELECT count(*) FROM roundtrip_control WHERE key LIKE '%attempt-%'").fetchone()[0] == 0
    # Still within the original 24-hour authorization (fixture starts at 10:00).
    h.now += timedelta(days=1, minutes=-10)
    assert run(h)['submitted_side'] == 'BUY'
    h.fill('2')
    h.now += timedelta(seconds=5)
    assert run(h)['submitted_side'] == 'SELL'
    h.fill('3')
    h.now += timedelta(seconds=5)
    assert run(h)['status'] == 'VERIFIED'


@pytest.mark.parametrize('damage', ['no_observation', 'wrong_broker', 'future', 'missing_clock', 'bad_clock',
                                  'partial_fill', 'unknown_cancel', 'no_cancel', 'terms', 'unresolved'])
def test_cancel_cannot_authorize_successor_without_exact_durable_evidence(h, damage):
    run(h)
    cancel_open_leg(h)
    identity = f'fixture-roundtrip:{h.market}:BUY'
    with sqlite3.connect(journal(h)) as db:
        if damage == 'no_observation':
            db.execute('DELETE FROM paper_observations')
        elif damage in {'wrong_broker', 'future', 'missing_clock', 'bad_clock'}:
            rows = db.execute('SELECT observed_at,evidence FROM paper_observations').fetchall()
            for at, raw in rows:
                value = json.loads(raw)
                if value['status'] != 'CANCELLED':
                    continue
                if damage == 'wrong_broker':
                    value['broker_order_id'] = 'unrelated'
                elif damage == 'future':
                    value['ingested_at'] = (h.now+timedelta(seconds=1)).isoformat()
                elif damage == 'missing_clock':
                    value.pop('ingested_at')
                else:
                    value['ingested_at'] = 'not-a-date'
                db.execute('UPDATE paper_observations SET evidence=? WHERE observed_at=?', (json.dumps(value), at))
        elif damage == 'partial_fill':
            db.execute('UPDATE order_state SET filled=1')
        elif damage == 'unknown_cancel':
            db.execute("UPDATE requests SET status='UNKNOWN' WHERE id=?", ('cancel:'+identity,))
        elif damage == 'no_cancel':
            db.execute('DELETE FROM requests WHERE id=?', ('cancel:'+identity,))
        elif damage == 'terms':
            preparation = json.loads(db.execute('SELECT value FROM roundtrip_control WHERE key=?', (identity,)).fetchone()[0])
            preparation['terms']['quantity'] = 2
            db.execute('UPDATE roundtrip_control SET value=? WHERE key=?', (json.dumps(preparation), identity))
        else:
            db.execute('INSERT INTO reconciliation_issues VALUES (?,?)', (identity, 'fixture_unresolved'))
    calls = list(h.calls)
    assert run(h)['status'] == 'BLOCKED'
    assert h.calls == calls and len(h.orders) == 1


def test_sell_successor_requires_original_buy_fill_and_stays_one_share(h):
    run(h)
    h.fill()
    h.now += timedelta(seconds=5)
    assert run(h)['submitted_side'] == 'SELL'
    cancel_open_leg(h)
    assert run(h)['submitted_side'] == 'SELL'
    h.fill('3')
    h.now += timedelta(seconds=5)
    result = run(h)
    assert result['status'] == 'VERIFIED' and result['strategy_performance'] is False
    assert len(h.orders) == 3
    assert [leg['filled_quantity'] for leg in result['legs']] == [1, 1]


def test_prepared_successor_crash_is_never_retried(h):
    run(h)
    cancel_open_leg(h)
    def unavailable(*args):
        result = h.account(*args)
        result['cash_only_buying_quantity'] = 0
        return result
    assert run(h, account_loader=unavailable)['status'] == 'BLOCKED'
    assert run(h)['blocker'] == 'PREPARED_WITHOUT_BROKER_REQUEST'
    assert len(h.orders) == 1


def test_orphan_successor_preparation_cannot_skip_open_predecessor(h):
    run(h)
    with sqlite3.connect(journal(h)) as db:
        db.execute('INSERT INTO roundtrip_control VALUES (?,?)',
                   (f'fixture-roundtrip:{h.market}:BUY:attempt-2', '{}'))
    calls = list(h.calls)
    assert run(h)['status'] == 'BLOCKED'
    assert h.calls == calls and len(h.orders) == 1


def test_new_quote_cannot_mutate_cancelled_order_or_reprice_an_open_successor(h):
    run(h)
    cancel_open_leg(h)
    h.price += 100 if h.market == 'KR' else 1
    assert run(h)['submitted_side'] == 'BUY'
    with sqlite3.connect(journal(h)) as db:
        before = db.execute('SELECT * FROM paper_intents ORDER BY created_at').fetchall()
    h.price += 100 if h.market == 'KR' else 1
    assert run(h)['legs'][0]['status'] == 'OPEN'
    with sqlite3.connect(journal(h)) as db:
        assert db.execute('SELECT * FROM paper_intents ORDER BY created_at').fetchall() == before
    assert len(h.orders) == 2


def test_bar_only_price_is_bounded_without_fabricating_bid_ask():
    from decimal import Decimal
    for last in (100, 89195, 89750, 99600, 100000):
        quote = {'last_price': last, 'quote_basis': 'BAR_ONLY'}
        buy = rt._limit_price('KR', 'BUY', quote)
        sell = rt._limit_price('KR', 'SELL', quote)
        assert Decimal(last) <= buy <= Decimal(last)*Decimal('1.005')
        assert Decimal(last)*Decimal('0.995') <= sell <= Decimal(last)
        assert buy % 5 == sell % 5 == 0
        assert buy <= rt.dv.MARKETS['KR']['cap']
        assert 'bid' not in quote and 'ask' not in quote
    assert rt._limit_price('KR', 'BUY', {'last_price': 89195, 'ask': 89200}) == 89200
    assert rt._limit_price('US', 'BUY', {'last_price': 200, 'ask': 200.01}) == Decimal('200.01')


def test_cancel_ack_with_still_open_broker_report_never_creates_successor(h):
    run(h)
    h.now += timedelta(minutes=5)
    assert run(h)['legs'][0]['status'] == 'OPEN'
    h.orders['1']['cancelled'] = False
    h.now += timedelta(seconds=5)
    assert run(h)['legs'][0]['status'] == 'OPEN'
    assert len(h.orders) == 1


@pytest.mark.parametrize('stop', ['halt', 'expired', 'stale_quote'])
def test_successor_retains_halt_authorization_and_quote_guards(h, stop):
    run(h)
    cancel_open_leg(h)
    kwargs = {}
    if stop == 'halt':
        (h.validation/'HALT').touch()
    elif stop == 'expired':
        h.now += timedelta(days=1)
    else:
        def stale(market, clock):
            return {**h.quote(market, h.ticker, clock), 'bid': h.price, 'ask': h.price,
                    'observed_at': (h.now-timedelta(seconds=121)).isoformat()}
        kwargs['quote_loader'] = stale
    assert run(h, **kwargs)['status'] in {'BLOCKED', 'ATTENTION'}
    assert len(h.orders) == 1


def test_attempt_limit_is_finite_and_keeps_all_cancel_evidence(h):
    path = h.validation/'roundtrip-enabled.json'
    config = json.loads(path.read_text())
    config['expires_at'] = (h.now+timedelta(days=3)).isoformat()
    atomic_write_json(path, config)
    # No date transition needed to exercise the campaign bound with a larger
    # fixture policy; production keeps its persisted two-order daily limit.
    import tests.execution.test_demo_runtime as harness_module
    from unittest.mock import patch
    policy_name = 'PaperOrderPolicy' if h.market == 'KR' else 'USPaperOrderPolicy'
    policy = getattr(harness_module, policy_name)
    with patch.object(harness_module, policy_name, lambda *a, **kw: policy(*a, **{**kw, 'max_daily_orders': 5})):
        for _ in range(rt.MAX_LEG_ATTEMPTS):
            assert run(h)['submitted_side'] == 'BUY'
            cancel_open_leg(h)
        assert run(h)['status'] == 'BLOCKED'
        assert len(h.orders) == rt.MAX_LEG_ATTEMPTS
        with sqlite3.connect(journal(h)) as db:
            assert db.execute("SELECT count(*) FROM order_state WHERE status='CANCELLED'").fetchone()[0] == rt.MAX_LEG_ATTEMPTS
