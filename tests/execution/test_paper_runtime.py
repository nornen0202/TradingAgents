from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime, timedelta
import json
from threading import Event

import pytest

from tradingagents.execution.paper import PaperBroker
from tradingagents.execution.paper_quotes import normalize_quote
from tradingagents.execution.paper_runtime import advance_market, tick
from tradingagents.execution import paper_runtime
from tradingagents.atomic_io import atomic_write_json, interprocess_file_lock

AT = datetime.fromisoformat("2026-10-19T10:00:00+09:00")
TICKER = "005930.KS"


def account(at=AT):
    return {"account_id": "synthetic-private-account", "as_of": at.isoformat(), "snapshot_health": "VALID",
            "available_cash_krw": 10_000_000, "account_value_krw": 10_000_000,
            "positions": [], "pending_orders": [], "warnings": []}


def source(root, at=AT, *, action="STARTER_NOW"):
    run = root / "runs/2026/run-fixture"
    rows = {"run.json": {"run_id": run.name, "status": "success", "started_at": at.isoformat(), "finished_at": at.isoformat(),
                         "settings": {"market": "KR"}},
            "portfolio-private/account_snapshot.json": account(at),
            "portfolio-private/proposed_orders.json": {"orders": [{"canonical_ticker": TICKER, "side": "BUY", "delta_krw_now": 90000}]},
            "decision_bundle_v2.json": {"market": "kr", "generated_at": at.isoformat(), "analysis_source_run_id": "synthetic",
                "strategy_table": [{"ticker": TICKER, "last_price": 20000, "spread_bps": 5,
                    "market_data_asof": at.isoformat(), "market_session": "regular",
                    "quality": {"execution_ready": True, "generated_in_current_run": True},
                    "raw_codes": {"decision_now": action}}]},
            f"tickers/{TICKER}/execution_contract.json": {"entry_valid_until": (at + timedelta(minutes=2)).isoformat()}}
    for name, value in rows.items():
        p = run / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(value), encoding="utf-8")
    return run


def is_open(**_):
    return {"is_open": True, "phase": "regular"}


class Quotes:
    def __init__(self, clock):
        self.clock = clock

    def fetch(self, tickers, **_):
        return {ticker: {"as_of": self.clock().isoformat(), "price_krw": 20000,
                         "session": "regular", "executable": True, "spread_bps": 5} for ticker in tickers}, {}

    def close(self):
        pass


def test_real_forward_ticks_queue_fill_restart_and_no_same_signal_twice(tmp_path):
    archive, state = tmp_path / "archive", tmp_path / "state"
    source(archive)
    now = [AT]
    args = dict(clock=lambda: now[0], account_loader=lambda _: account(now[0]),
                quote_factory=lambda: Quotes(lambda: now[0]), session_resolver=is_open)
    a = advance_market(archive, state, "kr", now=now[0], **args)
    assert a["order_counts"]["PENDING"] == 1
    assert a["broker_orders_sent"] == 0
    now[0] += timedelta(seconds=30)
    b = advance_market(archive, state, "kr", now=now[0], **args)
    assert b["order_counts"]["FILLED"] == 1
    assert b["last_fill_at"] == now[0].isoformat()
    now[0] += timedelta(seconds=30)
    c = advance_market(archive, state, "kr", now=now[0], **args)
    assert c["order_counts"] == b["order_counts"]
    assert c["real_orders_enabled"] is False
    serialized = (state / "kr-status.json").read_text()
    assert "synthetic-private-account" not in serialized
    assert "cash_krw" not in serialized


@pytest.mark.parametrize("change", ["future", "missing", "naive", "stale", "pending", "incomplete"])
def test_bad_account_never_seeds_or_gets_quotes(tmp_path, change):
    archive, state = tmp_path / "archive", tmp_path / "state"
    source(archive)
    snapshot = account()
    snapshot.update({"future": {"as_of": (AT + timedelta(seconds=1)).isoformat()},
                     "missing": {"as_of": None}, "naive": {"as_of": "2026-10-19T10:00:00"},
                     "stale": {"as_of": (AT - timedelta(seconds=121)).isoformat()},
                     "pending": {"pending_orders": [{"status": "OPEN"}]},
                     "incomplete": {"warnings": ["KIS pending-order lookup failed"]}}[change])
    result = advance_market(archive, state, "kr", now=AT, clock=lambda: AT,
        account_loader=lambda _: snapshot, session_resolver=is_open,
        quote_factory=lambda: pytest.fail("must not get quotes"))
    assert result["status"] == "BLOCKED"
    assert not (archive / "paper/kr.sqlite").exists()


def test_weekend_no_broker_calls_and_expiry_does_not_reset_daily_nav(tmp_path):
    archive, state = tmp_path / "archive", tmp_path / "state"
    source(archive)
    args = dict(clock=lambda: AT, account_loader=lambda _: account(),
                quote_factory=lambda: Quotes(lambda: AT), session_resolver=is_open)
    advance_market(archive, state, "kr", now=AT, **args)
    later = AT + timedelta(days=1)
    result = advance_market(archive, state, "kr", now=later, clock=lambda: later,
        session_resolver=lambda **_: {"is_open": False, "phase": "closed"},
        account_loader=lambda _: pytest.fail("no account calls outside session"))
    assert result["status"] == "MARKET_CLOSED"
    assert result["order_counts"]["CANCELLED"] == 1
    assert result["last_observation_at"] == AT.isoformat()
    broker = PaperBroker(archive / "paper/kr.sqlite")
    try:
        assert broker._get("day") == AT.date().isoformat()
        assert broker.db.execute("select count(*) from observations").fetchone()[0] == 1
    finally:
        broker.close()


def test_runtime_disabled_until_explicit_local_paper_enable(tmp_path):
    assert tick(tmp_path / "a", tmp_path / "s", now=AT)["status"] == "DISABLED"
    (tmp_path / "s/enabled.json").write_text(json.dumps({"enabled": True, "mode": "LIVE"}))
    assert tick(tmp_path / "a", tmp_path / "s", now=AT)["status"] == "DISABLED"


def _enabled_state(state):
    atomic_write_json(state / "enabled.json", {
        "enabled": True, "mode": "LOCAL_PAPER_ONLY", "real_orders_enabled": False,
    })


def _after_existing_consumer_releases(state, monkeypatch, clock, acquired_at, callback):
    attempted = Event()
    @contextmanager
    def observed_lock(path, *, timeout):
        attempted.set()
        with interprocess_file_lock(path, timeout=timeout):
            yield
    monkeypatch.setattr(paper_runtime, "interprocess_file_lock", observed_lock)
    with ThreadPoolExecutor(max_workers=1) as pool:
        with interprocess_file_lock(state / "paper.lock", timeout=0):
            future = pool.submit(callback)
            assert attempted.wait(2)
            assert not future.done()
            clock[0] = acquired_at
        return future.result(timeout=10)


def test_handoff_waits_on_same_lock_then_samples_current_clock(tmp_path, monkeypatch):
    state, archive = tmp_path / "state", tmp_path / "archive"
    _enabled_state(state)
    now = [AT]
    clock_reads, markets = [], []
    def clock():
        clock_reads.append(now[0])
        return now[0]
    def advance(archive, state, market, *, now, **kwargs):
        markets.append((market, now))
        return {"checked_at": now.isoformat(), "status": "WAITING_SOURCE"}
    monkeypatch.setattr(paper_runtime, "advance_market", advance)
    acquired_at = AT + timedelta(seconds=12)
    result = _after_existing_consumer_releases(state, monkeypatch, now, acquired_at,
        lambda: tick(archive, state, clock=clock, lock_timeout=15))
    assert markets == [("kr", acquired_at), ("us", acquired_at)]
    assert clock_reads and set(clock_reads) == {acquired_at}
    assert result["checked_at"] == acquired_at.isoformat()
    assert result["real_orders_enabled"] is False


def test_explicit_clock_cannot_move_back_before_initial_now(tmp_path, monkeypatch):
    state, archive = tmp_path / "state", tmp_path / "archive"
    _enabled_state(state)
    monkeypatch.setattr(paper_runtime, "advance_market", lambda *a, **k: pytest.fail("no consumer entry"))
    with pytest.raises(ValueError, match="precedes explicit now"):
        tick(archive, state, now=AT, clock=lambda: AT - timedelta(seconds=1), lock_timeout=15)
    assert not archive.exists()


@pytest.mark.parametrize("timeout", [None, 0.01])
def test_default_tick_and_timed_out_wait_do_not_enter_consumer(tmp_path, monkeypatch, timeout):
    state, archive = tmp_path / "state", tmp_path / "archive"
    _enabled_state(state)
    before = (state / "enabled.json").read_bytes()
    monkeypatch.setattr(paper_runtime, "advance_market", lambda *a, **k: pytest.fail("no consumer entry"))
    expected_timeout = 0 if timeout is None else timeout
    @contextmanager
    def checked_lock(path, *, timeout):
        assert path == state / "paper.lock"
        assert timeout == expected_timeout
        with interprocess_file_lock(path, timeout=timeout):
            yield
    monkeypatch.setattr(paper_runtime, "interprocess_file_lock", checked_lock)
    kwargs = {} if timeout is None else {"lock_timeout": timeout}
    with interprocess_file_lock(state / "paper.lock", timeout=0):
        with pytest.raises(TimeoutError):
            tick(archive, state, clock=lambda: pytest.fail("no pre-lock clock"), **kwargs)
    assert (state / "enabled.json").read_bytes() == before
    assert not archive.exists()
    assert sorted(p.name for p in state.iterdir()) == ["enabled.json", "paper.lock"]


def test_session_closed_while_waiting_never_reads_account_or_queues_order(tmp_path, monkeypatch):
    state, archive = tmp_path / "state", tmp_path / "archive"
    _enabled_state(state)
    source(archive)
    now = [AT]
    session_clocks = []
    def session(*, market, now_local):
        session_clocks.append(now_local)
        return {"is_open": now_local < AT + timedelta(seconds=5), "phase": "closed"}
    acquired_at = AT + timedelta(seconds=10)
    result = _after_existing_consumer_releases(state, monkeypatch, now, acquired_at,
        lambda: tick(archive, state, clock=lambda: now[0], lock_timeout=15,
            session_resolver=session, account_loader=lambda _: pytest.fail("closed before account read"),
            quote_factory=lambda: pytest.fail("closed before quote read")))
    assert all(row["status"] == "MARKET_CLOSED" for row in result["markets"].values())
    assert session_clocks == [acquired_at, acquired_at]
    assert not (archive / "paper/kr.sqlite").exists()


@pytest.mark.parametrize("elapsed", [120, 600])
def test_wait_does_not_extend_original_signal_or_source_expiry(tmp_path, monkeypatch, elapsed):
    state, archive = tmp_path / "state", tmp_path / "archive"
    _enabled_state(state)
    original = source(archive)
    original_bundle = (original / "decision_bundle_v2.json").read_bytes()
    now = [AT + timedelta(seconds=elapsed - 5)]
    acquired_at = AT + timedelta(seconds=elapsed)
    result = _after_existing_consumer_releases(state, monkeypatch, now, acquired_at,
        lambda: tick(archive, state, clock=lambda: now[0], lock_timeout=15,
            account_loader=lambda _: account(now[0]), quote_factory=lambda: Quotes(lambda: now[0]),
            session_resolver=is_open))
    kr = result["markets"]["kr"]
    assert not kr["order_counts"].get("PENDING") and not kr["order_counts"].get("FILLED")
    broker = PaperBroker(archive / "paper/kr.sqlite")
    try:
        if elapsed == 120:
            assert broker.db.execute("SELECT reason FROM orders").fetchall()[0][0] == "signal_expired_or_future"
        else:
            assert "SOURCE_EXECUTION_EXPIRED" in kr["blockers"]
            assert broker.db.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 0
    finally:
        broker.close()
    assert (original / "decision_bundle_v2.json").read_bytes() == original_bundle


def test_waited_tick_preserves_original_signal_deduplication(tmp_path, monkeypatch):
    state, archive = tmp_path / "state", tmp_path / "archive"
    _enabled_state(state)
    source(archive)
    now = [AT]
    args = dict(clock=lambda: now[0], account_loader=lambda _: account(now[0]),
                quote_factory=lambda: Quotes(lambda: now[0]), session_resolver=is_open)
    first = tick(archive, state, **args)
    assert first["markets"]["kr"]["order_counts"]["PENDING"] == 1
    second = _after_existing_consumer_releases(state, monkeypatch, now, AT + timedelta(seconds=12),
        lambda: tick(archive, state, lock_timeout=15, **args))
    now[0] += timedelta(seconds=1)
    third = tick(archive, state, **args)
    assert second["markets"]["kr"]["order_counts"] == third["markets"]["kr"]["order_counts"]
    assert third["markets"]["kr"]["order_counts"]["FILLED"] == 1
    assert sum(third["markets"]["kr"]["order_counts"].values()) == 1


def test_future_analysis_is_not_a_source(tmp_path):
    source(tmp_path / "a", AT + timedelta(minutes=1))
    result = advance_market(tmp_path / "a", tmp_path / "s", "kr", now=AT,
        session_resolver=is_open, account_loader=lambda _: pytest.fail("future source rejected before API"))
    assert result["status"] == "WAITING_SOURCE"


def raw_quote():
    return {"rt_cd": "0", "output2": [{"stck_bsop_date": "20261019", "stck_cntg_hour": "095900",
        "stck_oprc": "20000", "stck_hgpr": "20010", "stck_lwpr": "19990", "stck_prpr": "20000", "cntg_vol": "1000"}]}


BOOK = {"rt_cd": "0", "output1": {"bidp1": "19995", "askp1": "20005", "aspr_acpt_hour": "100000"}}


def test_clock_correction_never_changes_broker_event_or_accepts_future_book():
    book = deepcopy(BOOK)
    book['output1']['aspr_acpt_hour'] = '100001'
    with pytest.raises(ValueError, match='ORDERBOOK_CLOCK_STALE_OR_FUTURE'):
        normalize_quote(ticker=TICKER, market='kr', chart=raw_quote(), orderbook=book, observed_at=AT)
    corrected = AT + timedelta(seconds=2)
    result = normalize_quote(ticker=TICKER, market='kr', chart=raw_quote(), orderbook=book, observed_at=corrected)
    assert result['orderbook_event_at'] == (AT + timedelta(seconds=1)).isoformat()
    assert result['observed_at'] == corrected.isoformat()
    assert book['output1']['aspr_acpt_hour'] == '100001'


def test_completed_dated_quote_keeps_source_time_and_rejects_bad_records():
    result = normalize_quote(ticker=TICKER, market="kr", chart=raw_quote(), orderbook=BOOK, observed_at=AT)
    assert datetime.fromisoformat(result["as_of"]) == AT
    assert result["price_krw"] == 20000


@pytest.mark.parametrize("case", ["empty", "missing_date", "bad_date", "future", "stale", "missing_book", "bad_price", "bad_response"])
def test_quote_invalid_clocks_empty_and_values_are_not_retrieval_timestamped(case):
    chart, book = raw_quote(), deepcopy(BOOK)
    row = chart["output2"][0]
    if case == "empty":
        chart["output2"] = []
    elif case == "missing_date":
        row.pop("stck_bsop_date")
    elif case == "bad_date":
        row["stck_bsop_date"] = "not-a-date"
    elif case == "future":
        row["stck_cntg_hour"] = "100100"
    elif case == "stale":
        row["stck_cntg_hour"] = "095000"
    elif case == "missing_book":
        book["output1"] = {}
    elif case == "bad_price":
        row["stck_prpr"] = "NaN"
    elif case == "bad_response":
        chart["rt_cd"] = "1"
    with pytest.raises(ValueError):
        normalize_quote(ticker=TICKER, market="kr", chart=chart, orderbook=book, observed_at=AT)


def test_us_requires_separate_observed_reference_rate():
    observed = datetime.fromisoformat("2026-10-19T10:00:00-04:00")
    chart = {"rt_cd": "0", "output2": [{"xymd": "20261019", "xhms": "095900", "open": "100", "high": "101", "low": "99", "last": "100", "evol": "100"}]}
    book = {"rt_cd": "0", "output1": {"pbid1": 99.99, "pask1": 100.01, "dymd": "20261019", "dhms": "230000"}}
    with pytest.raises(ValueError, match="FX_REFERENCE"):
        normalize_quote(ticker="AAPL", market="us", chart=chart, orderbook=book, observed_at=observed)
    fx = {"observed_at": observed.isoformat(), "base_currency": "USD", "quote_currency": "KRW", "rate": 1400,
          "source": "kis.inquire_present_balance.output2.frst_bltn_exrt", "kind": "BROKER_REFERENCE_RATE"}
    result = normalize_quote(ticker="AAPL", market="us", chart=chart, orderbook=book, observed_at=observed, fx_quote=fx)
    assert result["price_krw"] == 140000
    fx["observed_at"] = (observed + timedelta(seconds=1)).isoformat()
    with pytest.raises(ValueError):
        normalize_quote(ticker="AAPL", market="us", chart=chart, orderbook=book, observed_at=observed, fx_quote=fx)


def test_explicit_other_symbol_orderbook_is_not_relabelled():
    book = deepcopy(BOOK)
    book["output1"]["code"] = "000660"
    with pytest.raises(ValueError, match="IDENTITY_MISMATCH"):
        normalize_quote(ticker=TICKER, market="kr", chart=raw_quote(), orderbook=book, observed_at=AT)


def test_maintenance_clock_is_monotone_with_following_execution(tmp_path):
    broker = PaperBroker(tmp_path / "paper.sqlite")
    try:
        broker.seed(account())
        broker.expire_pending(now=(AT + timedelta(minutes=2)).isoformat())
        with pytest.raises(ValueError):
            broker.expire_pending(now=(AT + timedelta(minutes=1)).isoformat())
        with pytest.raises(ValueError):
            broker.step(now=(AT + timedelta(minutes=1)).isoformat(), quotes={}, signals=[])
    finally:
        broker.close()
