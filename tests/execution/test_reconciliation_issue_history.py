"""Actual issue writers retain dated SET/CLEAR evidence; no broker network."""
from datetime import timedelta, timezone
import json
import sqlite3

import pytest

from tradingagents.execution.kis_demo import DemoError, reconciliation_issue_state
from tradingagents.execution.strategy_settlement import strategy_settlement_evidence, settled_cost_totals
from tests.execution.test_strategy_settlement import imported_roundtrip


def state(broker, identity, at):
    return reconciliation_issue_state(broker.db, identity, as_of=at)


def evidence(broker, orders, h, cutoff, *, historical):
    proof = strategy_settlement_evidence(broker.db, orders, market=h.market, as_of=cutoff, historical=historical)
    return proof, settled_cost_totals(proof, orders, currency="KRW" if h.market == "KR" else "USD", as_of=cutoff)


@pytest.mark.parametrize("market", ["KR", "US"])
def test_original_set_and_verified_reconcile_clear_do_not_rewrite_past_costs(tmp_path, market):
    h, before, _, original = imported_roundtrip(tmp_path, market)
    clear_cutoff = h.now.isoformat()
    identity = before["orders"][0]["id"]
    h.now += timedelta(seconds=10)
    with h.factory(market, h.root / f"{market.lower()}-strategy.sqlite", lambda: h.now, (h.ticker,), h.credentials.scope()) as broker:
        broker.journal._block(identity, "fixture_query_unavailable")
        blocked_cutoff = h.now.isoformat()
        assert state(broker, identity, clear_cutoff)["status"] == "CLEAR"
        assert state(broker, identity, blocked_cutoff)["status"] == "ACTIVE"
        past, costs = evidence(broker, before["orders"], h, clear_cutoff, historical=True)
        assert past["status"] == "COMPLETE_REVIEWED_IMPORT"
        assert costs["actual_cost"] == original["evaluation"]["actual_cost"] == 2
        current, costs = evidence(broker, before["orders"], h, blocked_cutoff, historical=False)
        assert current["status"] == "INVALID" and costs["actual_cost"] is None
        # Default/live current evaluation cannot use an earlier cutoff to
        # ignore the still-active mutable order gate.
        strict_past, _ = evidence(broker, before["orders"], h, clear_cutoff, historical=False)
        assert strict_past["status"] == "INVALID"
        calls = list(h.calls)
        body = json.loads(broker.db.execute("SELECT body FROM intents WHERE id=?", (identity,)).fetchone()[0])
        with pytest.raises(DemoError, match="ambiguous"):
            broker.journal._write_once("new-blocked-order", "order-cash" if market == "KR" else "order",
                "VTTC0012U" if market == "KR" else "VTTT1002U", body, h.now.isoformat())
        assert h.calls == calls
        count = broker.db.execute("SELECT count(*) FROM reconciliation_issue_history").fetchone()[0]
        h.now += timedelta(seconds=1)
        broker.journal._block(identity, "fixture_query_unavailable")
        assert broker.db.execute("SELECT count(*) FROM reconciliation_issue_history").fetchone()[0] == count
        h.now += timedelta(seconds=10)
        broker.reconcile(intent_id=identity)  # Original validated KR/US CLEAR writer.
        assert not broker.db.execute("SELECT 1 FROM reconciliation_issues WHERE id=?", (identity,)).fetchone()
        assert state(broker, identity, h.now)["status"] == "CLEAR"
        during, costs = evidence(broker, before["orders"], h, blocked_cutoff, historical=True)
        assert during["status"] == "INVALID" and costs["actual_cost"] is None
        past, costs = evidence(broker, before["orders"], h, clear_cutoff, historical=True)
        assert past["status"] == "COMPLETE_REVIEWED_IMPORT" and costs["actual_cost"] == 2
        current, costs = evidence(broker, before["orders"], h, h.now.isoformat(), historical=False)
        assert current["status"] == "COMPLETE_REVIEWED_IMPORT" and costs["actual_cost"] == 2
        history = broker.db.execute("SELECT transition,observed_at,ingested_at FROM reconciliation_issue_history WHERE intent_id=? ORDER BY sequence", (identity,)).fetchall()
        assert [r[0] for r in history][-2:] == ["SET", "CLEAR"]
        assert all(r[1] == r[2] for r in history)  # Frozen deterministic broker clock seam.


@pytest.mark.parametrize("market", ["KR", "US"])
def test_legacy_undated_issue_is_unknown_before_first_seen_and_future_clear(tmp_path, market):
    h, before, _, _ = imported_roundtrip(tmp_path, market)
    identity = before["orders"][0]["id"]
    early = h.now.isoformat()
    path = h.root / f"{market.lower()}-strategy.sqlite"
    h.now += timedelta(seconds=10)
    with h.factory(market, path, lambda: h.now, (h.ticker,), h.credentials.scope()) as broker:
        broker.journal._block(identity, "fixture_legacy_issue")
        # Temporary legacy-schema fixture: retain the actual original issue
        # writer's mutable row but remove the not-yet-deployed dated table.
        broker.db.execute("DROP TABLE reconciliation_issue_history")
        assert state(broker, identity, early)["status"] == "UNVERIFIED"
        tables = broker.db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        assert state(broker, identity, h.now)["status"] == "UNVERIFIED"
        assert broker.db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall() == tables
    h.now += timedelta(seconds=10)
    first_seen = h.now.isoformat()
    with h.factory(market, path, lambda: h.now, (h.ticker,), h.credentials.scope()) as broker:
        history = broker.db.execute("SELECT transition,observed_at FROM reconciliation_issue_history WHERE intent_id=?", (identity,)).fetchall()
        assert len(history) == 1 and history[0][0] == "LEGACY_UNKNOWN"
        assert history[0][1] == h.now.astimezone(timezone.utc).isoformat()
        assert state(broker, identity, early)["status"] == "UNVERIFIED"
        assert state(broker, identity, first_seen)["status"] == "UNVERIFIED"
        h.now += timedelta(seconds=10)
        broker.reconcile(intent_id=identity)
        assert state(broker, identity, h.now)["status"] == "CLEAR"
        assert state(broker, identity, first_seen)["status"] == "UNVERIFIED"
        assert state(broker, identity, early)["status"] == "UNVERIFIED"


@pytest.mark.parametrize("tamper", ["unlogged_clear", "unlogged_issue", "history_content"])
def test_undated_current_edits_and_history_tamper_are_not_cost_authority(tmp_path, tamper):
    h, before, _, _ = imported_roundtrip(tmp_path)
    identity = before["orders"][0]["id"]
    cutoff = h.now.isoformat()
    h.now += timedelta(seconds=10)
    with h.factory(h.market, h.root / "us-strategy.sqlite", lambda: h.now, (h.ticker,), h.credentials.scope()) as broker:
        if tamper == "unlogged_clear":
            broker.journal._block(identity, "fixture_known_issue")
            broker.db.execute("DELETE FROM reconciliation_issues WHERE id=?", (identity,))
        elif tamper == "unlogged_issue":
            broker.db.execute("INSERT INTO reconciliation_issues VALUES (?,?)", (identity, "fixture_undated_issue"))
            broker.journal._observe_unlogged_issue(identity)
        else:
            with pytest.raises(sqlite3.IntegrityError, match="immutable"):
                broker.db.execute("UPDATE reconciliation_issue_history SET reason='changed' WHERE intent_id=?", (identity,))
            broker.db.execute("DROP TRIGGER reconciliation_issue_history_no_update")
            broker.db.execute("UPDATE reconciliation_issue_history SET reason='changed' WHERE intent_id=?", (identity,))
        assert state(broker, identity, cutoff)["status"] == "UNVERIFIED"
        proof, costs = evidence(broker, before["orders"], h, cutoff, historical=True)
        assert proof["status"] == "INVALID" and costs["actual_cost"] is None


def test_issue_clock_regression_keeps_current_live_block_and_is_not_backdated(tmp_path):
    h, before, _, _ = imported_roundtrip(tmp_path)
    identity = before["orders"][0]["id"]
    with h.factory(h.market, h.root / "us-strategy.sqlite", lambda: h.now, (h.ticker,), h.credentials.scope()) as broker:
        h.now += timedelta(seconds=10)
        broker.journal._block(identity, "first_issue")
        count = broker.db.execute("SELECT count(*) FROM reconciliation_issue_history").fetchone()[0]
        h.now -= timedelta(seconds=5)
        with pytest.raises(DemoError, match="clock regressed"):
            broker.journal._block(identity, "second_issue")
        assert broker.db.execute("SELECT reason FROM reconciliation_issues WHERE id=?", (identity,)).fetchone()[0] == "second_issue"
        assert broker.db.execute("SELECT count(*) FROM reconciliation_issue_history").fetchone()[0] == count
        assert state(broker, identity, h.now)["status"] == "UNVERIFIED"
