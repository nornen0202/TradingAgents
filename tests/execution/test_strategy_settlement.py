"""Reviewed settlement imports; real guarded brokers with offline responses only."""
from copy import deepcopy
from datetime import timedelta
import hashlib
import json
import sqlite3

import pytest

from tradingagents.execution import demo_runtime
from tradingagents.execution.kis_demo import DemoError
from tradingagents.execution.strategy_evaluation import evaluate_strategy_orders
from tradingagents.execution.strategy_settlement import (
    SCHEMA, import_strategy_settlement, strategy_settlement_evidence, settled_cost_totals,
)
from tests.execution.test_strategy_evaluation import completed_harness
from tests.execution.test_demo_runtime import Harness
from tests.execution.test_kis_paper import _observed_import_broker
from types import SimpleNamespace


def document(h, order, *, revision="first", previous=None, commission=1, partial=False):
    source = b"Offline fixture: independently reviewed, execution-attributed KIS demo statement"
    prepared = demo_runtime.at(order["prepared_at"])
    executions = []
    if partial and order["side"] == "BUY":
        first_price = h.price
        second_price = order["fill_notional"] - first_price
        splits = [(1, first_price, 1), (1, second_price, 11)]
    else:
        splits = [(order["filled_quantity"], order["fill_notional"] / order["filled_quantity"], 1)]
    for i, (quantity, price, offset) in enumerate(splits):
        executions.append({"fill_id": f"{order['id']}:execution:{i}", "quantity": quantity, "price": price,
            "commission": commission, "tax": 0, "fx_cost": 0, "other_cost": 0,
            "currency": "KRW" if h.market == "KR" else "USD",
            "executed_at": (prepared + timedelta(seconds=offset)).isoformat(),
            "confirmed_at": (prepared + timedelta(seconds=offset + 1)).isoformat(),
            "settled_at": (prepared + timedelta(seconds=offset + 2)).isoformat()})
    value = {"schema": SCHEMA, "environment": "demo", "market": h.market,
        "currency": "KRW" if h.market == "KR" else "USD", "account_scope": h.credentials.scope(),
        "intent_id": order["id"], "broker_order_id": "1" if order["side"] == "BUY" else "2",
        "revision_id": order["id"] + ":" + revision,
        "previous_revision_id": order["id"] + ":" + previous if previous else None,
        "attribution": "ORDER_EXECUTION", "cost_coverage": "ALL_COMPONENTS_IN_TRADING_CURRENCY",
        "source": {"kind": "KIS_DEMO_SETTLEMENT_DOCUMENT", "sha256": hashlib.sha256(source).hexdigest(),
                   "observed_at": h.now.isoformat(), "available_at": h.now.isoformat()},
        "review": {"approved": True, "reviewer_id": "offline-fixture-reviewer", "reviewed_at": h.now.isoformat()},
        "corrections_checked_through": h.now.isoformat(), "fills": executions}
    return value, source


def imported_roundtrip(tmp_path, market="US", *, partial=False):
    h, result = completed_harness(tmp_path, market, partial=partial)
    h.now += timedelta(seconds=5)
    docs = [document(h, order, partial=partial) for order in result["orders"]]
    path = h.root / f"{market.lower()}-strategy.sqlite"
    with h.factory(market, path, lambda: h.now, (h.ticker,), h.credentials.scope()) as broker:
        before = list(h.calls)
        for value, source in docs:
            assert import_strategy_settlement(broker, value, source_bytes=source)
        assert h.calls == before  # The import never makes any HTTP request.
        summary = demo_runtime.summary(broker.db, h.now, market)
    return h, result, docs, summary


@pytest.mark.parametrize("market", ["KR", "US"])
@pytest.mark.parametrize("partial", [False, True])
def test_real_broker_owned_cumulative_checkpoints_connect_reviewed_costs_to_evaluation(tmp_path, market, partial):
    h, before, docs, after = imported_roundtrip(tmp_path, market, partial=partial)
    evaluation = after["evaluation"]
    expected = 3 if partial else 2
    assert before["evaluation"]["actual_cost"] is before["performance"]["net_pnl"] is None
    assert evaluation["actual_cost"] == expected
    assert evaluation["net_pnl"] == 3 - expected
    assert evaluation["realized_net_pnl"] == 3 - expected
    assert evaluation["realized_actual_cost"] == expected
    assert evaluation["exact_fifo_available"] is evaluation["settlement_known"] is evaluation["fees_known"] is True
    assert evaluation["status"] == "AVAILABLE_NET_OF_REVIEWED_COSTS"
    assert after["performance"]["net_pnl"] == 3 - expected
    assert after["orders"] == before["orders"]
    assert evaluation["readiness"] == "NOT_READY_FOR_REAL_INVESTMENT"
    assert evaluation["automatic_live_transition"] is evaluation["real_orders_enabled"] is False
    assert "STATISTICAL_AND_OUT_OF_SAMPLE_VALIDATION_REQUIRED" in evaluation["unmet_criteria"]


def test_duplicate_import_is_noop_conflicting_duplicate_and_fork_fail_closed(tmp_path):
    h, before, docs, _ = imported_roundtrip(tmp_path)
    with h.factory(h.market, h.root / "us-strategy.sqlite", lambda: h.now, (h.ticker,), h.credentials.scope()) as broker:
        value, source = docs[0]
        count = broker.db.execute("SELECT count(*) FROM strategy_settlements").fetchone()[0]
        assert not import_strategy_settlement(broker, value, source_bytes=source)
        changed = deepcopy(value)
        changed["fills"][0]["commission"] += 1
        with pytest.raises(DemoError, match="different evidence"):
            import_strategy_settlement(broker, changed, source_bytes=source)
        changed["revision_id"] = "fork"
        with pytest.raises(DemoError, match="predecessor"):
            import_strategy_settlement(broker, changed, source_bytes=source)
        assert broker.db.execute("SELECT count(*) FROM strategy_settlements").fetchone()[0] == count
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            broker.db.execute("UPDATE strategy_settlements SET ingested_at='changed'")


def test_cost_correction_is_append_only_and_cannot_change_prior_cutoff(tmp_path):
    h, before, docs, original = imported_roundtrip(tmp_path)
    cutoff = h.now.isoformat()
    h.now += timedelta(minutes=1)
    corrected, source = document(h, before["orders"][0], revision="correction", previous="first", commission=1.5)
    with h.factory(h.market, h.root / "us-strategy.sqlite", lambda: h.now, (h.ticker,), h.credentials.scope()) as broker:
        old_rows = [tuple(row) for row in broker.db.execute("SELECT * FROM strategy_settlements")]
        assert import_strategy_settlement(broker, corrected, source_bytes=source)
        new_rows = [tuple(row) for row in broker.db.execute("SELECT * FROM strategy_settlements")]
        assert all(row in new_rows for row in old_rows) and len(new_rows) == len(old_rows) + 1
        old_proof = strategy_settlement_evidence(broker.db, before["orders"], market="US", as_of=cutoff)
        old = evaluate_strategy_orders(before["orders"], market="US", as_of=cutoff, gross_pnl=3,
            valuation_complete=True, settlement_evidence=old_proof)
        assert old == original["evaluation"]
        current = demo_runtime.summary(broker.db, h.now, "US")["evaluation"]
        assert current["actual_cost"] == 2.5 and current["net_pnl"] == .5


@pytest.mark.parametrize("mutate", [
    lambda d: d.update(environment="real"), lambda d: d.update(market="KR"),
    lambda d: d.update(account_scope="another-account"), lambda d: d.update(broker_order_id="another-order"),
    lambda d: d.update(attribution="ACCOUNT_DAY_TOTAL"), lambda d: d.update(cost_coverage="RATE_SCHEDULE"),
    lambda d: d["source"].update(sha256="0" * 64), lambda d: d["review"].update(approved=False),
    lambda d: d["review"].update(reviewer_id=""), lambda d: d["fills"][0].pop("fx_cost"),
    lambda d: d["fills"][0].update(currency="KRW"), lambda d: d["fills"][0].update(commission=None),
    lambda d: d["fills"][0].update(tax=-1), lambda d: d["fills"][0].update(other_cost=True),
    lambda d: d["fills"].append(deepcopy(d["fills"][0])),
    lambda d: d["fills"][0].update(quantity=2), lambda d: d["fills"][0].update(price=190),
])
def test_unverified_cost_scope_source_identity_coverage_or_money_never_imports(tmp_path, mutate):
    h, before = completed_harness(tmp_path, "US")
    h.now += timedelta(seconds=5)
    value, source = document(h, before["orders"][0])
    mutate(value)
    with h.factory(h.market, h.root / "us-strategy.sqlite", lambda: h.now, (h.ticker,), h.credentials.scope()) as broker:
        with pytest.raises((DemoError, ValueError)):
            import_strategy_settlement(broker, value, source_bytes=source)
        result = demo_runtime.summary(broker.db, h.now, "US")
        assert result["evaluation"]["actual_cost"] is result["evaluation"]["net_pnl"] is None


@pytest.mark.parametrize("field", ["executed_at", "confirmed_at", "settled_at"])
@pytest.mark.parametrize("value", [None, "bad", "2026-10-19T14:00:00", "2026-02-30T14:00:00Z", "2027-10-19T14:00:00Z"])
def test_future_missing_naive_bad_execution_and_settlement_clocks_are_rejected(tmp_path, field, value):
    h, before = completed_harness(tmp_path, "US")
    h.now += timedelta(seconds=5)
    doc, source = document(h, before["orders"][0])
    doc["fills"][0][field] = value
    with h.factory(h.market, h.root / "us-strategy.sqlite", lambda: h.now, (h.ticker,), h.credentials.scope()) as broker:
        with pytest.raises((DemoError, ValueError)):
            import_strategy_settlement(broker, doc, source_bytes=source)


def test_missing_one_side_costs_never_becomes_zero_and_legacy_lifecycle_is_not_promoted(tmp_path):
    h, result = completed_harness(tmp_path, "US")
    h.now += timedelta(seconds=5)
    value, source = document(h, result["orders"][0])
    with h.factory(h.market, h.root / "us-strategy.sqlite", lambda: h.now, (h.ticker,), h.credentials.scope()) as broker:
        assert import_strategy_settlement(broker, value, source_bytes=source)
        evaluation = demo_runtime.summary(broker.db, h.now, "US")["evaluation"]
        assert evaluation["actual_cost"] is evaluation["net_pnl"] is None
        assert evaluation["cost_evidence_status"] == "PARTIAL_REVIEWED_IMPORT"


def test_validation_or_manual_order_cannot_be_adopted_by_cost_import(tmp_path):
    broker, _, moment = _observed_import_broker(tmp_path)
    h = SimpleNamespace(market="KR", price=70000, now=moment[0], credentials=broker.client.credentials)
    value, source = document(h, {"id": "vts-intent-1", "side": "BUY", "filled_quantity": 1,
                                "fill_notional": 70000, "prepared_at": (moment[0] - timedelta(seconds=10)).isoformat()})
    value["broker_order_id"] = "123"
    try:
        with pytest.raises(DemoError, match="normal-strategy"):
            import_strategy_settlement(broker, value, source_bytes=source)
    finally:
        broker.close()


def test_empty_or_incomplete_broker_execution_evidence_never_implies_cost_or_settlement(tmp_path):
    h, result = completed_harness(tmp_path, "US")
    h.now += timedelta(seconds=5)
    doc, source = document(h, result["orders"][0])
    doc["fills"] = []
    with h.factory(h.market, h.root / "us-strategy.sqlite", lambda: h.now, (h.ticker,), h.credentials.scope()) as broker:
        with pytest.raises(DemoError, match="executions"):
            import_strategy_settlement(broker, doc, source_bytes=source)


def test_partial_sell_fifo_keeps_open_entry_cost_and_future_exit_cost_separate(tmp_path):
    h = Harness(tmp_path, "US")
    h.source(qty=2)
    h.tick()
    h.now += timedelta(seconds=10)
    h.fill(qty=1, amount=200)
    h.tick()
    h.now += timedelta(seconds=20)
    h.fill(qty=2, amount=399)
    h.tick()
    h.now += timedelta(seconds=20)
    h.source("fixture-2", action="EXIT_NOW", qty=5)
    h.tick()
    h.now += timedelta(seconds=20)
    h.fill("2", qty=1, amount=201)
    result = h.tick()
    h.now += timedelta(seconds=5)
    with h.factory(h.market, h.root / "us-strategy.sqlite", lambda: h.now, (h.ticker,), h.credentials.scope()) as broker:
        for order in result["orders"]:
            receipt, source = document(h, order, partial=True)
            assert import_strategy_settlement(broker, receipt, source_bytes=source)
        result = demo_runtime.summary(broker.db, h.now, "US", {h.ticker: h.quote("US", h.ticker, lambda: h.now)})["evaluation"]
    assert result["actual_cost"] == 3 and result["net_pnl"] == -1
    assert result["realized_actual_cost"] == 2 and result["realized_net_pnl"] == -1
    assert "OPEN_STRATEGY_INVENTORY" in result["unmet_criteria"]
    assert result["cost_sensitivity"]["includes_future_exit_cost"] is False


@pytest.mark.parametrize("location,field", [("source", "observed_at"), ("source", "available_at"),
                                            ("review", "reviewed_at"), (None, "corrections_checked_through")])
@pytest.mark.parametrize("value", [None, "bad", "2026-10-19T14:00:00", "2027-10-19T14:00:00Z"])
def test_source_review_correction_clocks_are_explicit_and_not_future(tmp_path, location, field, value):
    h, before = completed_harness(tmp_path, "US")
    h.now += timedelta(seconds=5)
    doc, source = document(h, before["orders"][0])
    (doc[location] if location else doc)[field] = value
    with h.factory(h.market, h.root / "us-strategy.sqlite", lambda: h.now, (h.ticker,), h.credentials.scope()) as broker:
        with pytest.raises((DemoError, ValueError)):
            import_strategy_settlement(broker, doc, source_bytes=source)


def test_future_revision_bytes_are_not_read_or_scored_at_earlier_cutoff(tmp_path):
    h, before, _, original = imported_roundtrip(tmp_path)
    cutoff = h.now.isoformat()
    with h.factory(h.market, h.root / "us-strategy.sqlite", lambda: h.now, (h.ticker,), h.credentials.scope()) as broker:
        broker.db.execute("INSERT INTO strategy_settlements VALUES (?,?,?,?,?)",
            ("future", before["orders"][0]["id"], "missing-future-parent", (h.now + timedelta(days=1)).isoformat(), "malformed future JSON"))
        proof = strategy_settlement_evidence(broker.db, before["orders"], market="US", as_of=cutoff)
        result = evaluate_strategy_orders(before["orders"], market="US", as_of=cutoff, gross_pnl=3,
            valuation_complete=True, settlement_evidence=proof)
        assert result == original["evaluation"]


def test_single_average_execution_cannot_hide_an_observed_partial_fill(tmp_path):
    h, before = completed_harness(tmp_path, "US", partial=True)
    h.now += timedelta(seconds=5)
    doc, source = document(h, before["orders"][0], partial=False)
    with h.factory(h.market, h.root / "us-strategy.sqlite", lambda: h.now, (h.ticker,), h.credentials.scope()) as broker:
        with pytest.raises(DemoError, match="partial fill"):
            import_strategy_settlement(broker, doc, source_bytes=source)


def test_later_partial_quantity_requires_new_snapshot_and_preserves_original_execution(tmp_path):
    h = Harness(tmp_path, "US")
    h.source(qty=2)
    h.tick()
    h.now += timedelta(seconds=10)
    h.fill(qty=1, amount=200)
    partial = h.tick()
    h.now += timedelta(seconds=5)
    first, source = document(h, partial["orders"][0])
    with h.factory(h.market, h.root / "us-strategy.sqlite", lambda: h.now, (h.ticker,), h.credentials.scope()) as broker:
        assert import_strategy_settlement(broker, first, source_bytes=source)
        early_summary = demo_runtime.summary(broker.db, h.now, "US", {h.ticker: h.quote("US", h.ticker, lambda: h.now)})
        early = early_summary["evaluation"]
        early_cutoff = h.now.isoformat()
        assert early["actual_cost"] == 1 and early["realized_net_pnl"] is None
    h.now += timedelta(seconds=10)
    h.fill(qty=2, amount=399)
    later = h.tick()
    assert later["evaluation"]["actual_cost"] is None
    h.now += timedelta(seconds=5)
    expanded, source = document(h, later["orders"][0], revision="expanded", previous="first", partial=True)
    with h.factory(h.market, h.root / "us-strategy.sqlite", lambda: h.now, (h.ticker,), h.credentials.scope()) as broker:
        assert import_strategy_settlement(broker, expanded, source_bytes=source)
        full = demo_runtime.summary(broker.db, h.now, "US", {h.ticker: h.quote("US", h.ticker, lambda: h.now)})["evaluation"]
        assert full["actual_cost"] == 2 and full["net_pnl"] == -1
        assert full["realized_net_pnl"] is None
        historical = strategy_settlement_evidence(broker.db, early_summary["orders"], market="US", as_of=early_cutoff)
        replay = evaluate_strategy_orders(early_summary["orders"], market="US", as_of=early_cutoff, gross_pnl=0,
            valuation_complete=True, settlement_evidence=historical)
        assert replay == early


def test_exported_proof_is_detached_and_serialized_claims_cannot_be_promoted(tmp_path):
    h, before, _, _ = imported_roundtrip(tmp_path, partial=True)
    with h.factory(h.market, h.root / "us-strategy.sqlite", lambda: h.now, (h.ticker,), h.credentials.scope()) as broker:
        proof = strategy_settlement_evidence(broker.db, before["orders"], market="US", as_of=h.now.isoformat())
    exported = dict(proof)
    exported["orders"][0]["fills"][0]["commission"] = 999
    result = settled_cost_totals(proof, before["orders"], currency="USD", as_of=h.now.isoformat())
    assert result["actual_cost"] == 3 and result["exact_fifo_available"] is True
    rejected = settled_cost_totals(exported, before["orders"], currency="USD", as_of=h.now.isoformat())
    assert rejected["status"] == "INVALID" and rejected["actual_cost"] is None
    untrusted = evaluate_strategy_orders(before["orders"], market="US", as_of=h.now.isoformat(), gross_pnl=3,
        valuation_complete=True, settlement_evidence=exported)
    assert untrusted["cost_evidence_status"] == "INVALID"
    assert untrusted["actual_cost"] is untrusted["net_pnl"] is None
    assert untrusted["fees_known"] is untrusted["settlement_known"] is False
    with pytest.raises(AttributeError, match="immutable"):
        proof._encoded = json.dumps(exported)


@pytest.mark.parametrize("tamper", ["body", "tr_id", "endpoint", "ack", "fingerprint", "request_clock", "owner",
                                   "strategy_terms", "paper_terms", "source", "observation", "reconciliation"])
def test_imported_cost_reread_rejects_changed_original_order_or_cumulative_proof(tmp_path, tamper):
    h, before, _, _ = imported_roundtrip(tmp_path)
    identity = before["orders"][0]["id"]
    with h.factory(h.market, h.root / "us-strategy.sqlite", lambda: h.now, (h.ticker,), h.credentials.scope()) as broker:
        db = broker.db
        if tamper == "body":
            body = json.loads(db.execute("SELECT body FROM intents WHERE id=?", (identity,)).fetchone()[0])
            body["OVRS_ORD_UNPR"] = "999"
            db.execute("UPDATE intents SET body=? WHERE id=?", (json.dumps(body), identity))
        elif tamper == "tr_id":
            db.execute("UPDATE intents SET tr_id='TTTT1002U' WHERE id=?", (identity,))
        elif tamper == "endpoint":
            db.execute("UPDATE intents SET endpoint='order-cash' WHERE id=?", (identity,))
        elif tamper == "ack":
            db.execute("UPDATE requests SET response=? WHERE id=?", (json.dumps({"broker_order_id": "999"}), identity))
        elif tamper == "fingerprint":
            db.execute("UPDATE requests SET fingerprint='changed' WHERE id=?", (identity,))
        elif tamper == "request_clock":
            db.execute("UPDATE requests SET created_at=? WHERE id=?", ((h.now + timedelta(days=1)).isoformat(), identity))
        elif tamper == "owner":
            db.execute("UPDATE owner SET scope='another-account'")
        elif tamper == "strategy_terms":
            db.execute("DROP TRIGGER strategy_terms_no_update")  # Deliberate fixture corruption only.
            db.execute("UPDATE strategy_attempts SET terms='{}' WHERE id=?", (identity,))
        elif tamper == "paper_terms":
            db.execute("DROP TRIGGER paper_intents_no_update")
            db.execute("UPDATE paper_intents SET terms='{}' WHERE id=?", (identity,))
        elif tamper == "source":
            db.execute("DROP TRIGGER strategy_source_no_update")
            db.execute("INSERT OR IGNORE INTO strategy_source_evidence VALUES (?,?)", (identity, "changed"))
            db.execute("UPDATE strategy_source_evidence SET evidence='changed' WHERE id=?", (identity,))
        elif tamper == "observation":
            raw = json.loads(db.execute("SELECT evidence FROM paper_observations WHERE id=? LIMIT 1", (identity,)).fetchone()[0])
            raw["fill_notional"] = 999
            db.execute("UPDATE paper_observations SET evidence=? WHERE id=?", (json.dumps(raw), identity))
        else:
            db.execute("UPDATE reconciliations SET evidence='{}' WHERE id=?", (identity,))
        proof = strategy_settlement_evidence(db, before["orders"], market="US", as_of=h.now.isoformat())
        assert proof["status"] == "INVALID"
        result = evaluate_strategy_orders(before["orders"], market="US", as_of=h.now.isoformat(), gross_pnl=3,
            valuation_complete=True, settlement_evidence=proof)
        assert result["actual_cost"] is result["net_pnl"] is None
        assert result["cost_evidence_status"] == "INVALID"


def test_validated_proof_cannot_be_reused_for_different_orders_cutoff_or_currency(tmp_path):
    h, before, _, _ = imported_roundtrip(tmp_path)
    with h.factory(h.market, h.root / "us-strategy.sqlite", lambda: h.now, (h.ticker,), h.credentials.scope()) as broker:
        proof = strategy_settlement_evidence(broker.db, before["orders"], market="US", as_of=h.now.isoformat())
    changed = deepcopy(before["orders"])
    changed[0]["prepared_at"] = (demo_runtime.at(changed[0]["prepared_at"]) + timedelta(seconds=1)).isoformat()
    for orders, currency, cutoff in ((changed, "USD", h.now.isoformat()),
            (before["orders"], "KRW", h.now.isoformat()),
            (before["orders"], "USD", (h.now + timedelta(seconds=1)).isoformat())):
        result = settled_cost_totals(proof, orders, currency=currency, as_of=cutoff)
        assert result["status"] == "INVALID" and result["actual_cost"] is None


def test_broker_document_availability_precedes_local_collection_and_operator_review(tmp_path):
    h, before = completed_harness(tmp_path, "US")
    h.now += timedelta(seconds=5)
    doc, source = document(h, before["orders"][0])
    doc["source"]["available_at"] = (h.now - timedelta(seconds=2)).isoformat()
    doc["source"]["observed_at"] = (h.now - timedelta(seconds=1)).isoformat()
    with h.factory(h.market, h.root / "us-strategy.sqlite", lambda: h.now, (h.ticker,), h.credentials.scope()) as broker:
        assert import_strategy_settlement(broker, doc, source_bytes=source)
    doc["source"]["available_at"] = h.now.isoformat()
    doc["source"]["observed_at"] = (h.now - timedelta(seconds=1)).isoformat()
    with h.factory(h.market, h.root / "us-strategy.sqlite", lambda: h.now, (h.ticker,), h.credentials.scope()) as broker:
        with pytest.raises(DemoError, match="source/review"):
            import_strategy_settlement(broker, doc, source_bytes=source)


def test_cost_revalidation_works_on_readonly_ledger_without_schema_or_state_writes(tmp_path):
    h, before, _, original = imported_roundtrip(tmp_path)
    path = h.root / "us-strategy.sqlite"
    with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True) as db:
        db.execute("PRAGMA query_only=ON")
        proof = strategy_settlement_evidence(db, before["orders"], market="US", as_of=h.now.isoformat())
        result = evaluate_strategy_orders(before["orders"], market="US", as_of=h.now.isoformat(), gross_pnl=3,
            valuation_complete=True, settlement_evidence=proof)
        assert result == original["evaluation"]
        assert db.total_changes == 0
