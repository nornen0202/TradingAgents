"""Offline append-only allocation and point-in-time feedback regressions."""
from copy import deepcopy
from datetime import datetime, timezone
import json
import sqlite3

import pytest

from tradingagents.performance import journal
from tradingagents.performance.action_outcomes import summarize_action_performance
from tradingagents.performance.lifecycle import append_lifecycle_event, initialize_lifecycle
from tradingagents.performance.outcome_revisions import (
    CLOCKS, REVISION_KIND, read_events, select_retrospectives,
)
from tradingagents.performance.replay import replay_action_history


T = [f"2026-09-21T00:0{i}:00+00:00" for i in range(9)]


@pytest.fixture
def ledger(tmp_path):
    path = tmp_path / "fixture.sqlite"
    conn = sqlite3.connect(path, isolation_level=None)
    conn.row_factory = sqlite3.Row
    initialize_lifecycle(conn)
    yield conn, path
    conn.close()


def fill(conn, identity, *, side="BUY", quantity=1, price=100, cost=1,
         occurred=2, known=None, mode="demo", currency="USD", ticker="A"):
    known = occurred if known is None else known
    append_lifecycle_event(conn, event_id="intent:" + identity, signal_id="signal:" + identity,
        intent_id=identity, kind="INTENT", mode=mode, occurred_at=T[0], available_at=T[0],
        ingested_at=T[known], payload={"ticker": ticker, "side": side, "quantity": quantity})
    append_lifecycle_event(conn, event_id=identity, signal_id="signal:" + identity,
        intent_id=identity, kind="FILL", mode=mode, occurred_at=T[occurred], available_at=T[occurred],
        confirmed_at=T[occurred], settled_at=T[occurred], ingested_at=T[known],
        payload={"ticker": ticker, "side": side, "quantity": quantity, "price": price,
                 "cost": cost, "currency": currency})


def active(conn, at):
    return [event["payload"] for event in select_retrospectives(read_events(conn), analysis_as_of=T[at])]


def count(conn, table):
    return conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]


def late_buy(conn, *, mode="demo"):
    fill(conn, "B", mode=mode)
    fill(conn, "S", side="SELL", price=120, occurred=3, mode=mode)
    journal.record_fill_retrospectives(conn, exit_event_id="S", evaluated_at=T[3], clock=lambda: T[3])
    fill(conn, "A", price=90, occurred=1, known=4, mode=mode)
    journal.record_fill_retrospectives(conn, exit_event_id="S", evaluated_at=T[4], clock=lambda: T[4])


@pytest.mark.parametrize("mode", ["paper", "demo", "actual"])
def test_late_buy_replaces_whole_exit_without_changing_past_or_source_rows(ledger, mode):
    conn, path = ledger
    fill(conn, "B", mode=mode)
    fill(conn, "S", side="SELL", price=120, occurred=3, mode=mode)
    first_ids = journal.record_fill_retrospectives(conn, exit_event_id="S", evaluated_at=T[3], clock=lambda: T[3])
    before = replay_action_history(path, analysis_as_of=T[3])
    stored = tuple(conn.execute("SELECT * FROM trade_journal WHERE id=?", (first_ids[0],)).fetchone())
    original_events = {row[0]: tuple(row) for row in conn.execute("SELECT * FROM lifecycle_events")}
    assert before["retrospectives"][0]["net_profit"] == 18
    fill(conn, "A", price=90, occurred=1, known=4, mode=mode)
    new_ids = journal.record_fill_retrospectives(conn, exit_event_id="S", evaluated_at=T[4], clock=lambda: T[4])
    after = replay_action_history(path, analysis_as_of=T[4])
    assert len(after["retrospectives"]) == 1
    assert after["retrospectives"][0]["net_profit"] == 28
    assert after["retrospectives"][0]["closed_quantity"] == 1
    assert replay_action_history(path, analysis_as_of=T[3]) == before
    assert tuple(conn.execute("SELECT * FROM trade_journal WHERE id=?", (first_ids[0],)).fetchone()) == stored
    for row in conn.execute("SELECT * FROM lifecycle_events"):
        if row[0] in original_events:
            assert tuple(row) == original_events[row[0]]
    counts = [count(conn, name) for name in ("trade_journal", "learned_intuitions", "lifecycle_events")]
    assert journal.record_fill_retrospectives(conn, exit_event_id="S", evaluated_at=T[5], clock=lambda: T[5]) == new_ids
    assert [count(conn, name) for name in ("trade_journal", "learned_intuitions", "lifecycle_events")] == counts
    for at in (3, 4, 5):
        summary = summarize_action_performance(path, analysis_as_of=T[at])
        assert summary.closed_trades == summary.learned_intuitions == 1
        assert summary.data_quality["actual_closed_trade_reviews"] == (1 if mode == "actual" else 0)
    assert count(conn, "trade_journal") == count(conn, "learned_intuitions") == 2


def test_same_entry_exit_pair_can_change_quantity_in_a_new_revision(ledger):
    conn, path = ledger
    fill(conn, "B", quantity=2, cost=2)
    fill(conn, "S", side="SELL", quantity=2, cost=2, price=120, occurred=3)
    journal.record_fill_retrospectives(conn, exit_event_id="S", evaluated_at=T[3], clock=lambda: T[3])
    fill(conn, "A", price=90, occurred=1, known=4)
    journal.record_fill_retrospectives(conn, exit_event_id="S", evaluated_at=T[4], clock=lambda: T[4])
    previous, current = active(conn, 3), active(conn, 4)
    assert [(r["entry_fill_id"], r["closed_quantity"]) for r in previous] == [("B", 2)]
    assert {r["entry_fill_id"]: r["closed_quantity"] for r in current} == {"A": 1, "B": 1}
    assert sum(r["net_profit"] for r in current) == 46
    assert count(conn, "trade_journal") == 3
    summary = summarize_action_performance(path, analysis_as_of=T[4])
    assert summary.closed_trades == summary.learned_intuitions == 2


def test_partial_multiple_sells_reallocate_without_consuming_lots_twice(ledger):
    conn, _ = ledger
    fill(conn, "B", quantity=3, cost=3)
    fill(conn, "S1", side="SELL", price=120, occurred=3)
    fill(conn, "S2", side="SELL", quantity=2, cost=2, price=130, occurred=4)
    for exit_id in ("S1", "S2"):
        journal.record_fill_retrospectives(conn, exit_event_id=exit_id, evaluated_at=T[4], clock=lambda: T[4])
    assert sum(r["net_profit"] for r in active(conn, 4)) == 74
    fill(conn, "A", price=90, occurred=1, known=5)
    for exit_id in ("S1", "S2"):
        journal.record_fill_retrospectives(conn, exit_event_id=exit_id, evaluated_at=T[5], clock=lambda: T[5])
    rows = active(conn, 5)
    assert sum(r["net_profit"] for r in rows) == 84
    assert {r["exit_fill_id"]: (r["entry_fill_id"], r["closed_quantity"]) for r in rows} == {
        "S1": ("A", 1), "S2": ("B", 2)}
    assert sum(r["closed_quantity"] for r in rows) == 3


def test_empty_revision_withdraws_unknown_seed_basis_without_deleting_lessons(ledger):
    conn, path = ledger
    fill(conn, "B")
    fill(conn, "S", side="SELL", price=120, occurred=3)
    journal.record_fill_retrospectives(conn, exit_event_id="S", evaluated_at=T[3], clock=lambda: T[3])
    append_lifecycle_event(conn, event_id="late-seed", signal_id="seed", kind="ACCOUNT_SEED", mode="demo",
        occurred_at=T[1], available_at=T[1], ingested_at=T[4],
        payload={"cash": 0, "currency": "USD", "positions": {"A": 1}})
    assert journal.record_fill_retrospectives(conn, exit_event_id="S", evaluated_at=T[4], clock=lambda: T[4]) == []
    assert active(conn, 4) == []
    projection = replay_action_history(path, analysis_as_of=T[4], ticker="A")
    assert projection["retrospectives"] == []
    assert not any(e["kind"] == "ACCOUNT_SEED" for e in projection["events"])
    replay = replay_action_history(path, analysis_as_of=T[4])
    assert replay["retrospectives"] == []
    assert replay["accounts"]["demo:USD"]["positions"] == {"A": 1}
    assert replay["accounts"]["demo:USD"]["cash"] == 18
    assert active(conn, 3)[0]["net_profit"] == 18
    assert count(conn, "trade_journal") == count(conn, "learned_intuitions") == 1
    summary = summarize_action_performance(path, analysis_as_of=T[4])
    assert summary.closed_trades == summary.learned_intuitions == 0
    assert journal.record_fill_retrospectives(conn, exit_event_id="S", evaluated_at=T[5], clock=lambda: T[5]) == []


def test_mode_and_currency_allocations_are_independent(ledger):
    conn, _ = ledger
    for index, (mode, currency) in enumerate((("demo", "USD"), ("demo", "KRW"), ("actual", "USD"), ("paper", "KRW"))):
        fill(conn, f"B{index}", mode=mode, currency=currency)
        fill(conn, f"S{index}", side="SELL", price=120, occurred=3, mode=mode, currency=currency)
        journal.record_fill_retrospectives(conn, exit_event_id=f"S{index}", evaluated_at=T[3], clock=lambda: T[3])
    before = {r["exit_fill_id"]: r for r in active(conn, 3)}
    fill(conn, "late", price=90, occurred=1, known=4)
    for index in range(4):
        journal.record_fill_retrospectives(conn, exit_event_id=f"S{index}", evaluated_at=T[4], clock=lambda: T[4])
    after = {r["exit_fill_id"]: r for r in active(conn, 4)}
    assert after["S0"]["net_profit"] == 28
    for identity in ("S1", "S2", "S3"):
        assert after[identity] == before[identity]


@pytest.mark.parametrize("clock", CLOCKS)
@pytest.mark.parametrize("value", [None, "bad-date", T[5]])
def test_missing_invalid_future_revision_clocks_cannot_hide_the_previous_version(ledger, clock, value):
    conn, _ = ledger
    late_buy(conn)
    events = deepcopy(read_events(conn))
    latest = next(e for e in events if e["kind"] == REVISION_KIND and e["payload"]["previous_revision_id"])
    latest[clock] = value
    assert [e["payload"]["net_profit"] for e in select_retrospectives(events, analysis_as_of=T[4])] == [18]


@pytest.mark.parametrize("clock", CLOCKS)
@pytest.mark.parametrize("value", [None, "bad-date", T[5]])
def test_invalid_or_future_fill_does_not_change_published_allocation(ledger, clock, value):
    conn, _ = ledger
    fill(conn, "B")
    fill(conn, "S", side="SELL", price=120, occurred=3)
    journal.record_fill_retrospectives(conn, exit_event_id="S", evaluated_at=T[3], clock=lambda: T[3])
    fill(conn, "A", price=90, occurred=1, known=4)
    events = deepcopy(read_events(conn))
    next(e for e in events if e["event_id"] == "A")[clock] = value
    assert [e["payload"]["net_profit"] for e in select_retrospectives(events, analysis_as_of=T[4])] == [18]


def test_revision_and_all_new_reviews_and_lessons_roll_back_atomically(ledger, monkeypatch):
    conn, _ = ledger
    fill(conn, "B", quantity=2, cost=2)
    fill(conn, "S", side="SELL", quantity=2, cost=2, price=120, occurred=3)
    journal.record_fill_retrospectives(conn, exit_event_id="S", evaluated_at=T[3], clock=lambda: T[3])
    fill(conn, "A", price=90, occurred=1, known=4)
    tables = ("trade_journal", "learned_intuitions", "lifecycle_events")
    before = {table: [tuple(row) for row in conn.execute(f"SELECT * FROM {table}")] for table in tables}
    original = journal.append_lifecycle_event
    def fail_revision(*args, **kwargs):
        if kwargs.get("kind") == REVISION_KIND:
            raise RuntimeError("fixture allocation publication failure")
        return original(*args, **kwargs)
    monkeypatch.setattr(journal, "append_lifecycle_event", fail_revision)
    with pytest.raises(RuntimeError, match="publication failure"):
        journal.record_fill_retrospectives(conn, exit_event_id="S", evaluated_at=T[4], clock=lambda: T[4])
    assert {table: [tuple(row) for row in conn.execute(f"SELECT * FROM {table}")] for table in tables} == before
    assert active(conn, 4)[0]["net_profit"] == 36


def test_backdated_publication_and_fork_are_rejected(ledger):
    conn, _ = ledger
    late_buy(conn)
    counts = count(conn, "lifecycle_events")
    with pytest.raises(ValueError, match="backdated"):
        journal.record_fill_retrospectives(conn, exit_event_id="S", evaluated_at=T[3], clock=lambda: T[3])
    assert count(conn, "lifecycle_events") == counts
    events = deepcopy(read_events(conn))
    fork = deepcopy(next(e for e in events if e["kind"] == REVISION_KIND and e["payload"]["previous_revision_id"]))
    fork["event_id"] += ":fork"
    with pytest.raises(ValueError, match="fork"):
        select_retrospectives(events + [fork], analysis_as_of=T[4])


def test_missing_member_or_wrong_currency_reference_fails_closed(ledger):
    conn, _ = ledger
    late_buy(conn)
    events = deepcopy(read_events(conn))
    latest = next(e for e in events if e["kind"] == REVISION_KIND and e["payload"]["previous_revision_id"])
    latest["payload"]["review_ids"] = ["missing-review"]
    with pytest.raises(ValueError, match="membership"):
        select_retrospectives(events, analysis_as_of=T[4])
    events = deepcopy(read_events(conn))
    next(e for e in events if e["event_id"] == "A")["payload"]["currency"] = "KRW"
    with pytest.raises(ValueError, match="input evidence"):
        select_retrospectives(events, analysis_as_of=T[4])


def test_first_revision_supersedes_legacy_review_only_after_publication(ledger):
    conn, _ = ledger
    fill(conn, "B")
    fill(conn, "S", side="SELL", price=120, occurred=3)
    legacy = journal.generate_closed_trade_review(entry_context={"ticker": "A", "action": "BUY"},
        exit_context={"ticker": "A", "action": "SELL"}, realized_return_pct=18, holding_days=0)
    legacy.update(review_id="legacy-review", entry_fill_id="B", exit_fill_id="S", signal_id="signal:S",
        closed_quantity=1, net_profit=18, total_cost=2, currency="USD", mode="demo",
        created_at=T[3], ingested_at=T[3], confirmed_at=T[3], settled_at=T[3], closed_at=T[3])
    journal.store_closed_trade_review(conn, legacy)
    fill(conn, "A", price=90, occurred=1, known=4)
    journal.record_fill_retrospectives(conn, exit_event_id="S", evaluated_at=T[4], clock=lambda: T[4])
    assert active(conn, 3)[0]["review_id"] == "legacy-review"
    assert [r["net_profit"] for r in active(conn, 4)] == [28]
    assert count(conn, "trade_journal") == 2


def test_default_publication_clock_does_not_backdate_a_historical_calculation(ledger):
    conn, path = ledger
    fill(conn, "B")
    fill(conn, "S", side="SELL", price=120, occurred=3)
    started = datetime.now(timezone.utc)
    journal.record_fill_retrospectives(conn, exit_event_id="S", evaluated_at=T[3])
    finished = datetime.now(timezone.utc)
    events = read_events(conn)
    published = [e for e in events if e["kind"] in {REVISION_KIND, "RETROSPECTIVE"}]
    assert len(published) == 2
    for event in published:
        assert started <= datetime.fromisoformat(event["ingested_at"]) <= finished
        assert event["ingested_at"] == event["available_at"]
    assert active(conn, 3) == []
    assert replay_action_history(path, analysis_as_of=T[3])["retrospectives"] == []
    assert summarize_action_performance(path, analysis_as_of=T[3]).closed_trades == 0
    assert select_retrospectives(events, analysis_as_of=finished.isoformat())[0]["payload"]["net_profit"] == 18


def test_input_cutoff_and_publication_clock_are_distinct(ledger):
    conn, _ = ledger
    fill(conn, "B")
    fill(conn, "S", side="SELL", price=120, occurred=3)
    fill(conn, "A", price=90, occurred=1, known=4)
    ids = journal.record_fill_retrospectives(conn, exit_event_id="S", evaluated_at=T[3], clock=lambda: T[5])
    assert active(conn, 4) == []
    assert active(conn, 5)[0]["net_profit"] == 18
    head = next(e for e in read_events(conn) if e["kind"] == REVISION_KIND)
    assert head["payload"]["input_as_of"] == T[3]
    assert head["available_at"] == T[5]
    # Repeating the same historical computation is a no-op; its publication
    # remains the first actual time, even when the input cutoff is much older.
    before = count(conn, "lifecycle_events")
    assert journal.record_fill_retrospectives(conn, exit_event_id="S", evaluated_at=T[3], clock=lambda: T[6]) == ids
    assert count(conn, "lifecycle_events") == before


@pytest.mark.parametrize("clock", [lambda: None, lambda: "invalid", lambda: "2026-09-21", lambda: T[2]])
def test_invalid_or_pre_cutoff_publication_clock_cannot_append(ledger, clock):
    conn, _ = ledger
    fill(conn, "B")
    fill(conn, "S", side="SELL", price=120, occurred=3)
    before = count(conn, "lifecycle_events")
    with pytest.raises(ValueError):
        journal.record_fill_retrospectives(conn, exit_event_id="S", evaluated_at=T[3], clock=clock)
    assert count(conn, "lifecycle_events") == before


def test_mixed_exit_revisions_cannot_allocate_the_same_buy_twice(ledger):
    conn, path = ledger
    fill(conn, "B", occurred=2)
    fill(conn, "C", occurred=3, price=110)
    fill(conn, "S1", side="SELL", occurred=4, price=120)
    fill(conn, "S2", side="SELL", occurred=5, price=130)
    for identity in ("S1", "S2"):
        journal.record_fill_retrospectives(conn, exit_event_id=identity, evaluated_at=T[5], clock=lambda: T[5])
    assert sum(r["closed_quantity"] for r in active(conn, 5)) == 2
    fill(conn, "A", occurred=1, known=6, price=90)
    # Refreshing only the second SELL moves it from C to B, while stale S1
    # still claims B. Readers must fail closed until the complete refresh.
    journal.record_fill_retrospectives(conn, exit_event_id="S2", evaluated_at=T[6], clock=lambda: T[6])
    with pytest.raises(ValueError, match="entry quantity"):
        active(conn, 6)
    with pytest.raises(ValueError, match="entry quantity"):
        replay_action_history(path, analysis_as_of=T[6])
    with pytest.raises(ValueError, match="entry quantity"):
        summarize_action_performance(path, analysis_as_of=T[6])
    assert sum(r["net_profit"] for r in active(conn, 5)) == 36
    journal.record_fill_retrospectives(conn, exit_event_id="S1", evaluated_at=T[6], clock=lambda: T[6])
    assert {r["entry_fill_id"] for r in active(conn, 6)} == {"A", "B"}
    assert sum(r["closed_quantity"] for r in active(conn, 6)) == 2


def test_partial_refresh_without_duplicate_buy_still_rejects_mixed_input_basis(ledger):
    conn, path = ledger
    fill(conn, "B", occurred=2)
    fill(conn, "C", occurred=3, price=110)
    fill(conn, "S1", side="SELL", occurred=4, price=120)
    journal.record_fill_retrospectives(conn, exit_event_id="S1", evaluated_at=T[4], clock=lambda: T[4])
    fill(conn, "S2", side="SELL", occurred=5, price=130)
    journal.record_fill_retrospectives(conn, exit_event_id="S2", evaluated_at=T[5], clock=lambda: T[5])
    assert sum(r["net_profit"] for r in active(conn, 5)) == 36
    fill(conn, "A", occurred=1, known=6, price=90)
    journal.record_fill_retrospectives(conn, exit_event_id="S1", evaluated_at=T[6], clock=lambda: T[6])
    with pytest.raises(ValueError, match="input snapshots"):
        active(conn, 6)
    with pytest.raises(ValueError, match="input snapshots"):
        summarize_action_performance(path, analysis_as_of=T[6])
    # A later publication cannot make the intermediate as-of valid retroactively.
    journal.record_fill_retrospectives(conn, exit_event_id="S2", evaluated_at=T[6], clock=lambda: T[7])
    assert sum(r["net_profit"] for r in active(conn, 7)) == 56
    with pytest.raises(ValueError, match="input snapshots"):
        replay_action_history(path, analysis_as_of=T[6])
    assert sum(r["net_profit"] for r in active(conn, 5)) == 36


@pytest.mark.parametrize("invalid_seed", ["duplicate", "after_fill"])
def test_opening_seed_contract_is_shared_by_writer_selector_summary_and_ticker_replay(ledger, invalid_seed):
    conn, path = ledger
    fill(conn, "B", occurred=2)
    fill(conn, "S", side="SELL", price=120, occurred=4)
    journal.record_fill_retrospectives(conn, exit_event_id="S", evaluated_at=T[4], clock=lambda: T[4])
    seed_times = (0, 1) if invalid_seed == "duplicate" else (3,)
    for index, occurred in enumerate(seed_times):
        append_lifecycle_event(conn, event_id=f"seed:{index}", signal_id=f"seed:{index}", kind="ACCOUNT_SEED", mode="demo",
            occurred_at=T[occurred], available_at=T[occurred], ingested_at=T[5],
            payload={"cash": 1000, "currency": "USD", "positions": {"A": 1}})
    expected = "duplicate account seed" if invalid_seed == "duplicate" else "seed cannot follow"
    before = count(conn, "lifecycle_events")
    with pytest.raises(ValueError, match=expected):
        journal.record_fill_retrospectives(conn, exit_event_id="S", evaluated_at=T[5], clock=lambda: T[5])
    assert count(conn, "lifecycle_events") == before
    for query in (lambda: active(conn, 5), lambda: summarize_action_performance(path, analysis_as_of=T[5]),
                  lambda: replay_action_history(path, analysis_as_of=T[5]),
                  lambda: replay_action_history(path, analysis_as_of=T[5], ticker="A")):
        with pytest.raises(ValueError, match=expected):
            query()
    assert active(conn, 4)[0]["net_profit"] == 18


def test_opening_seed_at_same_instant_precedes_buy_for_unknown_cost_basis(ledger):
    conn, _ = ledger
    fill(conn, "B", occurred=2)
    append_lifecycle_event(conn, event_id="z-late-sorting-seed", signal_id="seed", kind="ACCOUNT_SEED", mode="demo",
        occurred_at=T[2], available_at=T[2], ingested_at=T[2],
        payload={"cash": 1000, "currency": "USD", "positions": {"A": 1}})
    fill(conn, "S", side="SELL", occurred=4, price=120)
    assert journal.record_fill_retrospectives(conn, exit_event_id="S", evaluated_at=T[4], clock=lambda: T[4]) == []
    assert active(conn, 4) == []


def test_partial_legacy_transition_requires_complete_revision_coverage(ledger):
    conn, path = ledger
    fill(conn, "B", occurred=2)
    fill(conn, "C", occurred=3, price=110)
    fill(conn, "S1", side="SELL", occurred=4, price=120)
    fill(conn, "S2", side="SELL", occurred=5, price=130)
    for entry, exit_id in (("B", "S1"), ("C", "S2")):
        review = journal.generate_closed_trade_review(entry_context={"ticker": "A", "action": "BUY"},
            exit_context={"ticker": "A", "action": "SELL"}, realized_return_pct=18, holding_days=0)
        review.update(review_id="legacy:" + exit_id, entry_fill_id=entry, exit_fill_id=exit_id,
            signal_id="signal:" + exit_id, closed_quantity=1, net_profit=18, total_cost=2,
            currency="USD", mode="demo", created_at=T[5], ingested_at=T[5],
            confirmed_at=T[5], settled_at=T[5], closed_at=T[5])
        journal.store_closed_trade_review(conn, review)
    assert sum(r["net_profit"] for r in active(conn, 5)) == 36
    fill(conn, "A", price=90, occurred=1, known=6)
    journal.record_fill_retrospectives(conn, exit_event_id="S1", evaluated_at=T[6], clock=lambda: T[6])
    with pytest.raises(ValueError, match="complete revision coverage"):
        active(conn, 6)
    with pytest.raises(ValueError, match="complete revision coverage"):
        summarize_action_performance(path, analysis_as_of=T[6])
    journal.record_fill_retrospectives(conn, exit_event_id="S2", evaluated_at=T[6], clock=lambda: T[6])
    assert sum(r["net_profit"] for r in active(conn, 6)) == 56
    assert sum(r["net_profit"] for r in active(conn, 5)) == 36
    assert count(conn, "trade_journal") == 4


def test_ticker_seed_guard_reads_earlier_other_symbol_fills_without_exposing_them(ledger):
    conn, path = ledger
    fill(conn, "B", occurred=3)
    fill(conn, "S", side="SELL", price=120, occurred=4)
    journal.record_fill_retrospectives(conn, exit_event_id="S", evaluated_at=T[4], clock=lambda: T[4])
    fill(conn, "other", occurred=1, known=5, ticker="OTHER")
    append_lifecycle_event(conn, event_id="seed", signal_id="seed", kind="ACCOUNT_SEED", mode="demo",
        occurred_at=T[2], available_at=T[2], ingested_at=T[4],
        payload={"cash": 1000, "currency": "USD", "positions": {"OTHER": 7}})
    projection = replay_action_history(path, analysis_as_of=T[4], ticker="A")
    assert projection["retrospectives"][0]["net_profit"] == 18
    assert all(e["payload"].get("ticker") == "A" for e in projection["events"])
    for query in (lambda: summarize_action_performance(path, analysis_as_of=T[5]),
                  lambda: replay_action_history(path, analysis_as_of=T[5]),
                  lambda: replay_action_history(path, analysis_as_of=T[5], ticker="A")):
        with pytest.raises(ValueError, match="seed cannot follow"):
            query()


@pytest.mark.parametrize("clock", CLOCKS)
@pytest.mark.parametrize("value", [None, "bad-date", T[5]])
def test_ticker_seed_dependency_clocks_are_verified_before_the_guard(ledger, clock, value):
    conn, path = ledger
    fill(conn, "B", occurred=3)
    fill(conn, "S", side="SELL", price=120, occurred=4)
    journal.record_fill_retrospectives(conn, exit_event_id="S", evaluated_at=T[4], clock=lambda: T[4])
    append_lifecycle_event(conn, event_id="intent:other", signal_id="signal:other", intent_id="other", kind="INTENT",
        mode="demo", occurred_at=T[0], available_at=T[0], ingested_at=T[0],
        payload={"ticker": "OTHER", "side": "BUY", "quantity": 1})
    # Model malformed legacy storage without relaxing the append API contract.
    event = dict(event_id="other", signal_id="signal:other", intent_id="other", kind="FILL", mode="demo",
        occurred_at=T[1], available_at=T[1], confirmed_at=T[1], settled_at=T[1], ingested_at=T[1],
        payload_json=json.dumps({"ticker": "OTHER", "side": "BUY", "quantity": 1, "price": 100, "cost": 1, "currency": "USD"}))
    # Required SQL columns cannot be null; an empty value is equally unknown.
    event[clock] = "" if value is None and clock in {"occurred_at", "available_at"} else value
    conn.execute("INSERT INTO lifecycle_events (" + ",".join(event) + ") VALUES (" + ",".join("?" for _ in event) + ")", tuple(event.values()))
    append_lifecycle_event(conn, event_id="seed", signal_id="seed", kind="ACCOUNT_SEED", mode="demo",
        occurred_at=T[2], available_at=T[2], ingested_at=T[4],
        payload={"cash": 1000, "currency": "USD", "positions": {"OTHER": 7}})
    projection = replay_action_history(path, analysis_as_of=T[4], ticker="A")
    assert projection["retrospectives"][0]["net_profit"] == 18
    assert all(e["payload"].get("ticker") == "A" for e in projection["events"])


def test_paper_new_sell_migrates_existing_legacy_exits_at_one_publication_clock(tmp_path, monkeypatch):
    from tradingagents.execution.paper import PaperBroker, PaperLimits
    path = tmp_path / "paper.sqlite"
    broker = PaperBroker(path, PaperLimits(cash_floor=0, max_order_nav=.5, max_single_name=1,
        max_daily_turnover=1, slippage_bps=0, fee_bps=100, sell_tax_bps=0))
    def quote(at, price):
        return {"A": dict(as_of=T[at], price_krw=price, spread_bps=0, session="regular", executable=True)}
    def signal(identity, at, side, quantity):
        return dict(signal_id=identity, run_id=identity, ticker="A", action=side, quantity=quantity,
                    execution_ready=True, available_at=T[at], valid_until=T[8])
    def legacy_writer(conn, *, exit_event_id, **kwargs):
        entry = next(e for e in read_events(conn) if e["kind"] == "FILL" and e["payload"]["side"] == "BUY")
        exit_event = next(e for e in read_events(conn) if e["event_id"] == exit_event_id)
        buy, sell = entry["payload"], exit_event["payload"]
        cost = buy["cost"] / buy["quantity"] + sell["cost"]
        profit = sell["price"] - buy["price"] - cost
        review = journal.generate_closed_trade_review(entry_context={"ticker": "A", "action": "BUY"},
            exit_context={"ticker": "A", "action": "SELL"}, realized_return_pct=profit, holding_days=0)
        review.update(review_id="legacy:paper", entry_fill_id=entry["event_id"], exit_fill_id=exit_event_id,
            signal_id=exit_event["signal_id"], closed_quantity=1, net_profit=profit, total_cost=cost,
            currency="KRW", mode="paper", created_at=T[3], ingested_at=T[3],
            confirmed_at=T[3], settled_at=T[3], closed_at=T[3])
        return [journal.store_closed_trade_review(conn, review)]
    try:
        broker.seed(dict(as_of=T[0], available_cash_krw=1000, positions=[]))
        broker.step(now=T[0], quotes=quote(0, 100), signals=[signal("buy", 0, "BUY", 2)])
        broker.step(now=T[1], quotes=quote(1, 100), signals=[])
        broker.step(now=T[2], quotes=quote(2, 110), signals=[signal("sell1", 2, "REDUCE", 1)])
        with monkeypatch.context() as patch:
            patch.setattr(journal, "record_fill_retrospectives", legacy_writer)
            broker.step(now=T[3], quotes=quote(3, 110), signals=[])
        old = tuple(broker.db.execute("SELECT * FROM trade_journal WHERE review_id='legacy:paper'").fetchone())
        before = replay_action_history(path, analysis_as_of=T[3])
        broker.step(now=T[4], quotes=quote(4, 120), signals=[signal("sell2", 4, "REDUCE", 1)])
        broker.step(now=T[5], quotes=quote(5, 120), signals=[])
        assert replay_action_history(path, analysis_as_of=T[3]) == before
        current = replay_action_history(path, analysis_as_of=T[5])
        assert len(current["retrospectives"]) == 2
        assert sum(row["net_profit"] for row in current["retrospectives"]) == pytest.approx(25.7)
        revisions = [e for e in read_events(broker.db) if e["kind"] == REVISION_KIND]
        assert len(revisions) == 2 and {e["available_at"] for e in revisions} == {T[5]}
        assert tuple(broker.db.execute("SELECT * FROM trade_journal WHERE review_id='legacy:paper'").fetchone()) == old
        assert summarize_action_performance(path, analysis_as_of=T[5]).closed_trades == 2
    finally:
        broker.close()
