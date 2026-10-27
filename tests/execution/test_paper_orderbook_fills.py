"""Independent clocked books bridge the minute-bar/short-lived intent gap."""
from datetime import timedelta
import json
import sqlite3

import pytest

from tradingagents.execution.paper import PaperBroker, PaperLimits
from tradingagents.execution.paper_runtime import tick
from tests.execution.test_paper_runtime import AT, TICKER, account, source, Quotes, is_open


def quote(at, *, bid=19995, ask=20005, book_at=None):
    return {"as_of": AT.isoformat(), "price_krw": 20000, "session": "regular",
            "executable": True, "spread_bps": 5, "price_basis": "COMPLETED_MINUTE_CLOSE",
            "execution_quote": {"basis": "KIS_ORDERBOOK", "as_of": (book_at or at).isoformat(),
                                "observed_at": at.isoformat(), "bid_krw": bid, "ask_krw": ask}}


@pytest.mark.parametrize("side", ["BUY", "SELL"])
@pytest.mark.parametrize("price_case", ["inside", "at_limit", "outside"])
def test_subminute_book_fills_only_marketable_limits(tmp_path, side, price_case):
    broker = PaperBroker(tmp_path / "paper.sqlite")
    snapshot = account()
    snapshot["positions"] = [{"canonical_ticker": TICKER, "quantity": 3, "market_price_krw": 20000}]
    snapshot["account_value_krw"] += 60000
    broker.seed(snapshot)
    at = AT + timedelta(seconds=40)
    signal = {"signal_id": "subminute", "ticker": TICKER, "action": side, "quantity": 1,
              "execution_ready": True, "available_at": AT.isoformat(),
              "valid_until": (AT + timedelta(seconds=59)).isoformat()}
    try:
        first = broker.step(now=at.isoformat(), quotes={TICKER: quote(at)}, signals=[signal])
        assert first["orders"][0]["status"] == "PENDING"  # never same snapshot
        limit = first["orders"][0]["limit_price"]
        raw = limit + ({"inside": -1, "at_limit": 0, "outside": 1}[price_case]) * (1 if side == "BUY" else -1)
        later = at + timedelta(seconds=2)
        q = quote(later, bid=raw - 10 if side == "BUY" else raw,
                  ask=raw if side == "BUY" else raw + 10)
        done = broker.step(now=later.isoformat(), quotes={TICKER: q}, signals=[])
        order = done["orders"][0]
        assert order["status"] == ("PENDING" if price_case == "outside" else "FILLED")
        if price_case != "outside":
            assert order["fill_price"] == pytest.approx(limit)
            assert order["cost"] > 0
            event = json.loads(broker.db.execute("SELECT payload_json FROM lifecycle_events WHERE kind='FILL'").fetchone()[0])
            assert event["fill_basis"] == "KIS_ORDERBOOK"
            assert event["quote_event_at"] == later.isoformat()
        assert done["broker_orders_sent"] == 0
    finally:
        broker.close()


@pytest.mark.parametrize("invalid", ["same", "future", "stale", "naive", "missing", "crossed", "nan", "wide", "observed_future"])
def test_invalid_or_replayed_book_never_fills(tmp_path, invalid):
    broker = PaperBroker(tmp_path / "paper.sqlite")
    broker.seed(account())
    at = AT + timedelta(seconds=40)
    signal = {"signal_id": "guard", "ticker": TICKER, "action": "BUY", "quantity": 1,
              "execution_ready": True, "available_at": AT.isoformat(),
              "valid_until": (AT + timedelta(seconds=59)).isoformat()}
    try:
        broker.step(now=at.isoformat(), quotes={TICKER: quote(at)}, signals=[signal])
        later = at + timedelta(seconds=2)
        q = quote(later); book = q["execution_quote"]
        if invalid == "same": book["as_of"] = at.isoformat()
        if invalid == "future": book["as_of"] = (later + timedelta(seconds=1)).isoformat()
        if invalid == "stale": book["as_of"] = (later - timedelta(seconds=121)).isoformat()
        if invalid == "naive": book["as_of"] = later.replace(tzinfo=None).isoformat()
        if invalid == "missing": book.pop("as_of")
        if invalid == "crossed": book["bid_krw"] = 21000
        if invalid == "nan": book["ask_krw"] = float("nan")
        if invalid == "wide": book["ask_krw"] = 21000
        if invalid == "observed_future": book["observed_at"] = (later + timedelta(seconds=1)).isoformat()
        done = broker.step(now=later.isoformat(), quotes={TICKER: q}, signals=[])
        assert done["orders"][0]["status"] == "PENDING"
    finally:
        broker.close()


@pytest.mark.parametrize("stop", [None, "halt", "expired", "session", "frozen_book", "account"])
def test_worker_follow_up_rechecks_guards_and_is_bounded(tmp_path, stop):
    archive, state = tmp_path / "archive", tmp_path / "state"
    source(archive)
    state.mkdir()
    (state / "enabled.json").write_text(json.dumps({"mode": "LOCAL_PAPER_ONLY", "enabled": True}))
    now, sleeps, reads = [AT + timedelta(seconds=40)], [], []
    def sleep(seconds):
        sleeps.append(seconds)
        now[0] += timedelta(seconds=121 if stop == "expired" else 2)
        if stop == "halt": (state / "HALT").touch()
    class Books(Quotes):
        def fetch(self, tickers, **kwargs):
            reads.append(now[0])
            return {t: quote(now[0], book_at=AT + timedelta(seconds=40) if stop == "frozen_book" else now[0]) for t in tickers}, {}
    def session(**kwargs):
        return {"is_open": kwargs["market"] == "kr" and not (sleeps and stop == "session"), "phase": "closed"}
    def load(_):
        value = account(now[0])
        if sleeps and stop == "account": value["account_id"] = "different-account"
        return value
    result = tick(archive, state, clock=lambda: now[0], sleep=sleep, follow_up_pending=True,
                  account_loader=load, quote_factory=lambda: Books(lambda: now[0]), session_resolver=session)
    assert sleeps == [1]
    assert len(reads) <= 2
    with sqlite3.connect(archive / "paper/kr.sqlite") as db:
        orders = db.execute("SELECT status,expires_at FROM orders").fetchall()
        assert len(orders) == 1
        assert orders[0][0] == ("FILLED" if stop is None else "CANCELLED" if stop in {"halt", "expired"} else "PENDING")
        assert orders[0][1] == (AT + timedelta(seconds=120)).isoformat()
    assert result["markets"]["kr"]["pending_follow_up_attempted"] is True
    assert result["broker_orders_sent"] == 0


def test_wait_source_does_not_trigger_follow_up_or_synthetic_order(tmp_path):
    archive, state = tmp_path / "archive", tmp_path / "state"
    source(archive, action="WAIT")
    state.mkdir()
    (state / "enabled.json").write_text(json.dumps({"mode": "LOCAL_PAPER_ONLY", "enabled": True}))
    result = tick(archive, state, now=AT, follow_up_pending=True,
                  sleep=lambda _: pytest.fail("No pending order"), account_loader=lambda _: account(),
                  quote_factory=lambda: Quotes(lambda: AT),
                  session_resolver=lambda **kw: is_open() if kw["market"] == "kr" else {"is_open": False, "phase": "closed"})
    assert result["markets"]["kr"]["order_counts"] == {"PENDING": 0, "FILLED": 0, "REJECTED": 0, "CANCELLED": 0}
