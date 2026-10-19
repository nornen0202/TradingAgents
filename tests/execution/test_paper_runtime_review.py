"""Independent offline regression evidence for forward paper execution review.

Fixtures intentionally use their own source/quote builders, rather than the
runtime's main test helpers. None of these tests contacts KIS or sends orders.
"""

from copy import deepcopy
from datetime import datetime, timedelta
import hashlib
import json

import pytest

from tradingagents.execution.paper import PaperBroker
from tradingagents.execution.paper_quotes import normalize_quote
from tradingagents.execution.paper_runtime import advance_market, tick
from tradingagents.charting.operations import paper_health


AT = datetime.fromisoformat("2026-10-19T10:00:00+09:00")
TICKER = "005930.KS"
OTHER = "000660.KS"
ACCOUNT = "independent-fixture-account"
SCOPE = hashlib.sha256(ACCOUNT.encode()).hexdigest()


def _account(at=AT, *, account_id=ACCOUNT, positions=()):
    positions = list(positions)
    return {
        "account_id": account_id, "as_of": at.isoformat(), "snapshot_health": "VALID",
        "available_cash_krw": 10_000_000, "buying_power_krw": 10_000_000,
        "account_value_krw": 10_000_000 + sum(p["quantity"] * p["market_price_krw"] for p in positions),
        "positions": positions, "pending_orders": [], "warnings": [],
    }


def _position(ticker=TICKER, quantity=5, price=20_000):
    return {"canonical_ticker": ticker, "quantity": quantity, "market_price_krw": price,
            "available_qty": quantity}


def _quote(at, price=20_000):
    return {"as_of": at.isoformat(), "price_krw": price, "session": "regular",
            "executable": True, "spread_bps": 5}


def _signal(at=AT):
    return {"signal_id": "independent-initial-intent", "ticker": TICKER, "action": "BUY",
            "quantity": 4, "execution_ready": True, "available_at": at.isoformat(),
            "valid_until": (at + timedelta(minutes=2)).isoformat()}


def _source(archive, *, source_account=ACCOUNT, at=AT):
    run = archive / "runs" / "20261019" / "independent-run"
    records = {
        "run.json": {"run_id": run.name, "status": "success", "started_at": (at - timedelta(minutes=5)).isoformat(), "finished_at": at.isoformat(),
                     "settings": {"market": "KR"}},
        "portfolio-private/account_snapshot.json": _account(at, account_id=source_account),
        "portfolio-private/proposed_orders.json": {"orders": [
            {"canonical_ticker": TICKER, "side": "BUY", "estimated_qty": 4, "delta_krw_now": 90_000}]},
        "decision_bundle_v2.json": {
            "market": "kr", "generated_at": at.isoformat(), "analysis_source_run_id": run.name,
            "strategy_table": [{"ticker": TICKER, "last_price": 20_000, "spread_bps": 5,
                                "market_data_asof": at.isoformat(), "market_session": "regular",
                                "quality": {"execution_ready": True, "generated_in_current_run": True},
                                "raw_codes": {"decision_now": "STARTER_NOW"}}],
        },
    }
    for filename, record in records.items():
        path = run / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record), encoding="utf-8")
    return run


class _Quotes:
    def __init__(self, at, calls):
        self.at, self.calls = at, calls

    def fetch(self, tickers, **kwargs):
        self.calls.append(set(tickers))
        return {ticker: _quote(self.at) for ticker in tickers}, {}

    def close(self):
        pass


def test_existing_ledger_keeps_observing_and_fills_existing_intent_without_new_source(tmp_path):
    archive, state = tmp_path / "archive", tmp_path / "state"
    ledger = archive / "paper" / "kr.sqlite"
    broker = PaperBroker(ledger)
    try:
        broker.seed(_account(positions=[_position()]), account_scope=SCOPE)
        broker.step(now=AT.isoformat(), quotes={TICKER: _quote(AT)}, signals=[_signal()])
    finally:
        broker.close()
    at = AT + timedelta(seconds=30)
    calls = []
    result = advance_market(
        archive, state, "kr", now=at, clock=lambda: at,
        account_loader=lambda _: _account(at, positions=[_position()]),
        quote_factory=lambda: _Quotes(at, calls),
        session_resolver=lambda **_: {"is_open": True, "phase": "regular"},
    )
    assert result["status"] == "VALUATION_ONLY"
    assert "NO_RECENT_COMPLETED_SOURCE" in result["blockers"]
    assert result["order_counts"] == {"PENDING": 0, "FILLED": 1, "REJECTED": 0, "CANCELLED": 0}
    assert result["last_observation_at"] == at.isoformat()
    assert calls == [{TICKER}]
    assert result["broker_orders_sent"] == 0 and result["real_orders_enabled"] is False
    broker = PaperBroker(ledger)
    try:
        # The refreshed real snapshot still has five shares. It must not reset
        # the independent paper holding of nine after the pending buy fills.
        assert broker.db.execute("SELECT qty FROM positions WHERE ticker=?", (TICKER,)).fetchone()[0] == 9
        assert broker._get("seed_asof") == AT.isoformat()
        assert broker._get("account_scope") == SCOPE
        assert broker.db.execute("SELECT COUNT(*) FROM observations").fetchone()[0] == 2
    finally:
        broker.close()


def test_status_counts_are_available_only_after_reads_and_both_markets_complete(tmp_path, monkeypatch):
    archive, state = tmp_path / "archive", tmp_path / "state"
    ledger = archive / "paper" / "kr.sqlite"
    broker = PaperBroker(ledger)
    try:
        broker.seed(_account(positions=[_position()]), account_scope=SCOPE)
        broker.step(now=AT.isoformat(), quotes={TICKER: _quote(AT)}, signals=[_signal()])
    finally:
        broker.close()
    state.mkdir()
    (state / "enabled.json").write_text(json.dumps({"mode": "LOCAL_PAPER_ONLY", "enabled": True}))
    moment = [AT + timedelta(seconds=30)]
    started = moment[0]

    def account_loader(_):
        moment[0] += timedelta(seconds=5)
        return _account(moment[0], positions=[_position()])

    class DelayedQuotes:
        def fetch(self, tickers, **_):
            moment[0] += timedelta(seconds=5)
            return {ticker: _quote(moment[0]) for ticker in tickers}, {}

        def close(self):
            moment[0] += timedelta(seconds=1)

    original_step = PaperBroker.step

    def delayed_step(self, **kwargs):
        result = original_step(self, **kwargs)
        moment[0] += timedelta(seconds=2)
        return result

    def session_resolver(*, market, **_):
        if market == "us":
            moment[0] += timedelta(seconds=3)
            return {"is_open": False, "phase": "closed"}
        return {"is_open": True, "phase": "regular"}

    monkeypatch.setattr(PaperBroker, "step", delayed_step)
    receipt = tick(archive, state, now=started, clock=lambda: moment[0], account_loader=account_loader,
                   quote_factory=DelayedQuotes, session_resolver=session_resolver)
    kr = receipt["markets"]["kr"]
    assert kr["order_counts"]["FILLED"] == 1
    assert datetime.fromisoformat(kr["last_fill_at"]) == AT + timedelta(seconds=41)
    assert datetime.fromisoformat(kr["checked_at"]) == AT + timedelta(seconds=43)
    assert datetime.fromisoformat(receipt["markets"]["us"]["checked_at"]) == AT + timedelta(seconds=46)
    assert datetime.fromisoformat(receipt["checked_at"]) == moment[0] == AT + timedelta(seconds=46)
    status_path = archive / "paper" / "status.json"
    for before in (started, AT + timedelta(seconds=39), AT + timedelta(seconds=41), moment[0] - timedelta(microseconds=1)):
        hidden = paper_health(status_path, analysis_as_of=before)
        assert hidden["status"] == "UNAVAILABLE" and hidden["markets"] == {}
    visible = paper_health(status_path, analysis_as_of=moment[0])
    assert visible["markets"]["kr"]["order_counts"]["FILLED"] == 1
    assert visible["markets"]["kr"]["last_fill_at"] == kr["last_fill_at"]


def test_explicit_now_without_advancing_clock_keeps_receipts_deterministic(tmp_path):
    archive, state = tmp_path / "archive", tmp_path / "state"
    state.mkdir()
    (state / "enabled.json").write_text(json.dumps({"mode": "LOCAL_PAPER_ONLY", "enabled": True}))
    receipt = tick(archive, state, now=AT,
                   session_resolver=lambda **_: {"is_open": False, "phase": "closed"})
    assert datetime.fromisoformat(receipt["checked_at"]) == AT
    assert all(datetime.fromisoformat(market["checked_at"]) == AT for market in receipt["markets"].values())


def test_same_market_different_account_source_cannot_create_any_intent(tmp_path):
    archive, state = tmp_path / "archive", tmp_path / "state"
    _source(archive, source_account="some-other-portfolio")
    result = advance_market(
        archive, state, "kr", now=AT, clock=lambda: AT,
        account_loader=lambda _: _account(),
        quote_factory=lambda: pytest.fail("cross-account source must fail before market reads"),
        session_resolver=lambda **_: {"is_open": True, "phase": "regular"},
    )
    assert result["status"] == "BLOCKED"
    assert result["blockers"] == ["SOURCE_ACCOUNT_IDENTITY_MISMATCH"]
    broker = PaperBroker(archive / "paper" / "kr.sqlite")
    try:
        assert broker.db.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 0
        assert broker.db.execute("SELECT COUNT(*) FROM observations").fetchone()[0] == 0
    finally:
        broker.close()
    public_status = (state / "kr-status.json").read_text("utf-8")
    assert ACCOUNT not in public_status
    assert "some-other-portfolio" not in public_status


@pytest.mark.parametrize("record", ["market_data", "source_account"])
@pytest.mark.parametrize("invalid", ["future", None, "bad", "2026-10-19T10:00:00"])
def test_unknown_or_future_archived_evidence_cannot_be_laundered_by_a_new_live_quote(tmp_path, record, invalid):
    archive, state = tmp_path / "archive", tmp_path / "state"
    source = _source(archive)
    filename = "decision_bundle_v2.json" if record == "market_data" else "portfolio-private/account_snapshot.json"
    path = source / filename
    payload = json.loads(path.read_text("utf-8"))
    invalid = (AT + timedelta(minutes=1)).isoformat() if invalid == "future" else invalid
    if record == "market_data":
        payload["strategy_table"][0]["market_data_asof"] = invalid
    else:
        payload["as_of"] = invalid
    path.write_text(json.dumps(payload), encoding="utf-8")
    calls = []
    result = advance_market(
        archive, state, "kr", now=AT, clock=lambda: AT,
        account_loader=lambda _: _account(),
        quote_factory=lambda: _Quotes(AT, calls),
        session_resolver=lambda **_: {"is_open": True, "phase": "regular"},
    )
    broker = PaperBroker(archive / "paper" / "kr.sqlite")
    try:
        assert broker.db.execute("SELECT COUNT(*) FROM orders WHERE status IN ('PENDING','FILLED')").fetchone()[0] == 0
    finally:
        broker.close()
    assert result["broker_orders_sent"] == 0


def test_incomplete_new_day_marks_defer_daily_baseline_then_repair_with_complete_marks(tmp_path):
    broker = PaperBroker(tmp_path / "baseline.sqlite")
    initial = _account(positions=[_position(quantity=100), _position(OTHER, quantity=100)])
    initial.update(available_cash_krw=6_000_000, buying_power_krw=6_000_000, account_value_krw=10_000_000)
    try:
        broker.seed(initial)
        broker.step(now=AT.isoformat(), quotes={TICKER: _quote(AT), OTHER: _quote(AT)}, signals=[])
        assert broker._get("day_start_nav") == 10_000_000
        tomorrow = AT + timedelta(days=1)
        first = broker.step(now=tomorrow.isoformat(), quotes={TICKER: _quote(tomorrow, 15_000)}, signals=[])
        assert first["marks_complete"] is False
        assert broker._get("day_start_nav") is None
        assert broker._get("day_baseline_pending") is True
        assert broker._get("daily_stopped") is True
        repaired_at = tomorrow + timedelta(seconds=30)
        repaired = broker.step(now=repaired_at.isoformat(), quotes={
            TICKER: _quote(repaired_at, 15_000), OTHER: _quote(repaired_at, 10_000)}, signals=[])
        assert repaired["marks_complete"] is True
        assert broker._get("day_baseline_pending") is False
        assert broker._get("day_start_nav") == 8_500_000
        assert broker._get("daily_stopped") is False
        # The complete baseline is then held fixed, so a later 500,000 loss
        # triggers the existing 2% reduce-only guard instead of resetting NAV.
        loss_at = repaired_at + timedelta(seconds=30)
        loss = broker.step(now=loss_at.isoformat(), quotes={
            TICKER: _quote(loss_at, 10_000), OTHER: _quote(loss_at, 10_000)}, signals=[])
        assert broker._get("day_start_nav") == 8_500_000
        assert broker._get("daily_stopped") is True
        assert loss["trading_state"] == "REDUCING"
    finally:
        broker.close()


def test_expiry_rejects_backward_clock_without_cancelling_or_rewriting_observations(tmp_path):
    broker = PaperBroker(tmp_path / "expiry.sqlite")
    try:
        broker.seed(_account())
        with pytest.raises(ValueError, match="before"):
            broker.expire_pending(now=(AT - timedelta(seconds=1)).isoformat(), halted=True)
        at = AT + timedelta(seconds=30)
        broker.step(now=at.isoformat(), quotes={TICKER: _quote(at)}, signals=[_signal()])
        with pytest.raises(ValueError, match="before"):
            broker.expire_pending(now=(at - timedelta(seconds=1)).isoformat(), halted=True)
        assert broker.db.execute("SELECT status FROM orders").fetchone()[0] == "PENDING"
        assert broker.db.execute("SELECT COUNT(*) FROM observations").fetchone()[0] == 1
        assert broker._get("last_step") == at.isoformat()
        broker.expire_pending(now=(AT + timedelta(minutes=2)).isoformat())
        assert broker.db.execute("SELECT status FROM orders").fetchone()[0] == "CANCELLED"
        assert broker._get("last_step") == at.isoformat()
        assert broker.db.execute("SELECT COUNT(*) FROM observations").fetchone()[0] == 1
    finally:
        broker.close()


def _us_observation():
    at = datetime.fromisoformat("2026-10-19T10:00:00-04:00")
    chart = {"rt_cd": "0", "output2": [{
        "xymd": "20261019", "xhms": "095900", "open": "100", "high": "101",
        "low": "99", "last": "100", "evol": "1000"}]}
    book = {"rt_cd": "0", "output1": {"pbid1": 99.99, "pask1": 100.01,
            "dymd": "20261019", "dhms": "230000", "vbid1": 7000, "vask1": 7000}}
    fx = {"observed_at": at.isoformat(), "base_currency": "USD", "quote_currency": "KRW", "rate": 1400,
          "source": "kis.inquire_present_balance.output2.frst_bltn_exrt", "kind": "BROKER_REFERENCE_RATE"}
    return {"ticker": "AAPL", "market": "us", "chart": chart, "orderbook": book, "observed_at": at, "fx_quote": fx}


def _split_us_observation():
    values = _us_observation()
    book = values["orderbook"]
    combined = book["output1"]
    book["output1"] = {"code": "AAPL", "curr": "USD", "dymd": combined["dymd"], "dhms": combined["dhms"]}
    book["output2"] = {key: combined[key] for key in ("pbid1", "pask1", "vbid1", "vask1")}
    book["output3"] = {"iep": "0"}
    return values


def test_actual_us_response_separates_header_and_price_fields():
    result = normalize_quote(**_split_us_observation())
    assert result["price_usd"] == 100
    assert result["spread_bps"] == pytest.approx(2)
    assert result["orderbook_date_basis"] == "EXPLICIT"


@pytest.mark.parametrize("change", ["missing_date", "future", "invalid_date", "empty_prices", "wrong_symbol", "conflict", "wrong_currency", "malformed_part"])
def test_split_us_response_cannot_hide_bad_identity_or_clock(change):
    values = _split_us_observation()
    header, prices = values["orderbook"]["output1"], values["orderbook"]["output2"]
    if change == "missing_date": header.pop("dymd")
    elif change == "future": header["dymd"] = "20261020"
    elif change == "invalid_date": header["dymd"] = "20260230"
    elif change == "empty_prices": prices.clear()
    elif change == "wrong_symbol": header["code"] = "MSFT"
    elif change == "conflict": prices["code"] = "MSFT"
    elif change == "wrong_currency": header["curr"] = "HKD"
    else: values["orderbook"]["output2"] = []
    with pytest.raises(ValueError):
        normalize_quote(**values)


@pytest.mark.parametrize("changed", [
    {"dymd": "20261020"}, {"dhms": "230001"}, {"dymd": "20261018"}, {"dhms": "225700"},
    {"dymd": "not-a-date"}, {"dymd": "20260230"}, {"dhms": "250001"},
    {"dymd": None}, {"dhms": None}, {"dymd": ""}, {"dhms": ""},
])
def test_us_orderbook_future_missing_malformed_and_stale_source_clocks_fail_closed(changed):
    kwargs = _us_observation()
    kwargs["orderbook"]["output1"].update(changed)
    with pytest.raises(ValueError, match="ORDERBOOK_CLOCK"):
        normalize_quote(**kwargs)


def test_orderbook_quantities_never_substitute_for_bid_ask_prices():
    kwargs = _us_observation()
    kwargs["orderbook"]["output1"].pop("pbid1")
    kwargs["orderbook"]["output1"].pop("pask1")
    with pytest.raises(ValueError, match="INVALID_PRICE"):
        normalize_quote(**kwargs)
    good = _us_observation()
    changed_volumes = deepcopy(good)
    changed_volumes["orderbook"]["output1"].update(vbid1=1e18, vask1=1)
    first, second = normalize_quote(**good), normalize_quote(**changed_volumes)
    assert first["spread_bps"] == second["spread_bps"] == pytest.approx(2)
    assert datetime.fromisoformat(first["orderbook_event_at"]) == datetime.fromisoformat(first["observed_at"])
    assert first["price_usd"] == 100 and first["price_krw"] == 140_000
