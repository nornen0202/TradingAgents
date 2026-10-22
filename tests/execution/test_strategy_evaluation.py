"""Deterministic strategy evidence and cost-sensitivity checks; no external API."""
from contextlib import closing
from datetime import timedelta, timezone
import json
import sqlite3

import pytest

from tradingagents.execution import demo_runtime
from tradingagents.execution.kis_demo import DemoError
from tradingagents.execution.strategy_evaluation import evaluate_strategy_orders
from tests.execution.test_demo_runtime import Harness


NOW = "2026-10-19T15:00:00+00:00"


def order(identity="buy", side="BUY", *, quantity=1, filled=1, amount=100, **changes):
    value = {"id": identity, "ticker": "AAPL", "side": side, "quantity": quantity,
             "filled_quantity": filled, "fill_notional": amount, "status": "FILLED",
             "prepared_at": "2026-10-19T14:00:00+00:00" if side == "BUY" else "2026-10-19T14:30:00+00:00",
             "observed_at": "2026-10-19T14:01:00+00:00" if side == "BUY" else "2026-10-19T14:31:00+00:00",
             "ingested_at": "2026-10-19T14:01:01+00:00" if side == "BUY" else "2026-10-19T14:31:01+00:00",
             "mode": "demo", "source": "KIS_DEMO_BROKER_REPORT", "strategy_performance": True}
    value.update(changes)
    return value


def evaluate(orders, *, gross=10, complete=True, market="US"):
    return evaluate_strategy_orders(orders, market=market, as_of=NOW, gross_pnl=gross, valuation_complete=complete)


def roundtrip():
    return [order(), order("sell", "SELL", amount=110)]


def test_empty_and_acknowledgements_never_become_fills_or_zero_cost_performance():
    for orders in ([], [order(filled=0, amount=0, status="ACKNOWLEDGED", observed_at=None, ingested_at=None)]):
        result = evaluate(orders, gross=None)
        assert result["status"] == "NO_FILLS"
        assert result["sample"]["filled_order_count"] == 0
        assert result["sample"]["closed_inventory_episodes"] == 0
        assert result["turnover"] == 0
        assert result["gross_pnl"] is result["realized_gross_pnl"] is result["actual_cost"] is result["net_pnl"] is None
        assert all(s["estimated_cost"] is s["estimated_pnl_after_assumed_cost"] is None for s in result["cost_sensitivity"]["scenarios"])
        assert "NO_STRATEGY_FILLS" in result["unmet_criteria"]


def test_completed_roundtrip_has_explicit_assumptions_and_no_actual_net_claim():
    result = evaluate(roundtrip())
    assert result["sample"]["buy_filled_orders"] == result["sample"]["sell_filled_orders"] == 1
    assert result["sample"]["closed_inventory_episodes"] == 1
    assert result["sample"]["order_session_count"] == 1
    assert result["turnover"] == 210 and result["realized_gross_pnl"] == 10
    scenarios = result["cost_sensitivity"]["scenarios"]
    assert [s["estimated_cost"] for s in scenarios] == [.21, .63, 1.05]
    assert [s["estimated_pnl_after_assumed_cost"] for s in scenarios] == [9.79, 9.37, 8.95]
    assert result["cost_sensitivity"]["basis"] == "ASSUMPTION_ONLY_NOT_BROKER_COSTS"
    assert result["actual_cost"] is result["net_pnl"] is None
    assert result["fees_known"] is result["settlement_known"] is result["exact_fifo_available"] is False
    assert result["readiness"] == "NOT_READY_FOR_REAL_INVESTMENT"
    assert result["automatic_live_transition"] is result["real_orders_enabled"] is False
    assert "BROKER_CORRECTIONS_UNVERIFIED" in result["unmet_criteria"]
    assert "STATISTICAL_AND_OUT_OF_SAMPLE_VALIDATION_REQUIRED" in result["unmet_criteria"]


@pytest.mark.parametrize("market,expected", [("KR", 1), ("US", .01)])
def test_small_assumed_cost_rounds_up_instead_of_disappearing(market, expected):
    result = evaluate([order(amount=1)], gross=0, market=market)
    assert result["cost_sensitivity"]["scenarios"][0]["estimated_cost"] == expected
    assert result["cost_sensitivity"]["scenarios"][0]["estimated_pnl_after_assumed_cost"] == -expected


def test_open_position_or_unknown_mark_never_fabricates_realized_profit():
    result = evaluate([order()], gross=7)
    assert result["gross_pnl"] == 7 and result["realized_gross_pnl"] is None
    assert result["open_positions"] == {"AAPL": 1}
    assert result["sample"]["closed_inventory_episodes"] == 0
    assert result["cost_sensitivity"]["includes_future_exit_cost"] is False
    missing_mark = evaluate([order()], gross=None, complete=False)
    assert missing_mark["status"] == "INCOMPLETE"
    assert all(s["estimated_pnl_after_assumed_cost"] is None for s in missing_mark["cost_sensitivity"]["scenarios"])


def test_missing_execution_money_stays_unknown_and_unsettled():
    result = evaluate([order(fill_notional=None)], gross=None, complete=False)
    assert result["turnover"] is result["actual_cost"] is result["gross_pnl"] is None
    assert "FILL_NOTIONAL_UNVERIFIED" in result["unmet_criteria"]
    assert all(s["estimated_cost"] is None for s in result["cost_sensitivity"]["scenarios"])


@pytest.mark.parametrize("field", ["prepared_at", "observed_at", "ingested_at"])
@pytest.mark.parametrize("value", [None, "bad", "2026-10-19T14:00:00", "2026-10-20T14:00:00+00:00"])
def test_missing_invalid_naive_future_clocks_are_not_performance_evidence(field, value):
    with pytest.raises(ValueError):
        evaluate([order(**{field: value})], gross=None)


@pytest.mark.parametrize("value", [None, "bad", "2026-10-19T15:00:00"])
def test_evaluation_requires_aware_analysis_cutoff(value):
    with pytest.raises(ValueError):
        evaluate_strategy_orders([], market="US", as_of=value, gross_pnl=None, valuation_complete=True)


@pytest.mark.parametrize("change", [{"mode": "paper"}, {"mode": "actual"}, {"source": "VALIDATION"}, {"strategy_performance": False}])
def test_local_simulation_and_validation_fills_cannot_enter_strategy_result(change):
    with pytest.raises(ValueError, match="STRATEGY_PROOF"):
        evaluate([order(**change)])


@pytest.mark.parametrize("amount", [-1, 0, float("nan"), float("inf"), True, "100"])
def test_bad_fill_amount_never_becomes_cost_or_profit(amount):
    with pytest.raises(ValueError):
        evaluate([order(amount=amount)])


def test_duplicate_cumulative_snapshots_are_rejected_not_added():
    with pytest.raises(ValueError, match="DUPLICATE"):
        evaluate([order(), order()])


def test_unsourced_short_and_gross_conflict_fail_closed():
    with pytest.raises(ValueError, match="UNOWNED_SELL"):
        evaluate([order("sell", "SELL")])
    with pytest.raises(ValueError, match="GROSS_CASHFLOW_MISMATCH"):
        evaluate(roundtrip(), gross=99)


@pytest.mark.parametrize("observed,ingested", [
    ("2026-10-19T14:45:00+00:00", "2026-10-19T14:45:01+00:00"),
    ("2026-10-19T14:01:00+00:00", "2026-10-19T14:45:00+00:00"),
])
def test_unknown_execution_sequence_cannot_claim_roundtrip_or_fifo(observed, ingested):
    orders = roundtrip()
    orders[0].update(observed_at=observed, ingested_at=ingested)
    result = evaluate(orders)
    assert result["sample"]["closed_inventory_episodes"] is None
    assert result["realized_gross_pnl"] is None and result["exact_fifo_available"] is False
    assert "CLOSED_STRATEGY_ROUND_TRIP_UNVERIFIED" in result["unmet_criteria"]


@pytest.mark.parametrize("market", ["KR", "US"])
def test_runtime_evaluates_only_latest_cumulative_quantity_once(tmp_path, market):
    h = Harness(tmp_path, market)
    if market == "KR":
        h.price = 40000  # Two shares remain inside the unchanged KR order cap.
    h.source(qty=2)
    h.tick()
    h.now += timedelta(seconds=10)
    h.fill(qty=1, amount=h.price - 1)
    first = h.tick()["evaluation"]
    assert first["sample"]["buy_filled_quantity"] == 1
    h.now += timedelta(seconds=10)
    h.fill(qty=2, amount=h.price * 2 - 2)
    second = h.tick()["evaluation"]
    assert second["sample"]["buy_filled_orders"] == 1
    assert second["sample"]["buy_filled_quantity"] == 2
    assert second["turnover"] == h.price * 2 - 2
    assert h.tick()["evaluation"]["turnover"] == second["turnover"]
    assert len(h.orders) == 1


@pytest.mark.parametrize("change", [
    {"broker_order_id": "foreign-order"}, {"mode": "paper"}, {"live_orders_enabled": True},
    {"observed_at": None}, {"observed_at": "bad"}, {"ingested_at": None}, {"ingested_at": "bad"},
    {"ingested_at": "2099-01-01T00:00:00Z"}, {"filled_qty": 0}, {"remaining_qty": 1},
])
def test_summary_rejects_mismatched_or_undated_broker_proof(tmp_path, change):
    h = Harness(tmp_path, "US")
    h.tick()
    h.now += timedelta(seconds=10)
    h.fill()
    h.tick()
    with sqlite3.connect(h.root / "us-strategy.sqlite") as db:
        identity, _, raw = db.execute("SELECT * FROM paper_observations ORDER BY observed_at DESC LIMIT 1").fetchone()
        row = json.loads(raw)
        moment = (h.now + timedelta(seconds=1)).isoformat()
        row.update(observed_at=moment, ingested_at=moment)
        row.update(change)
        db.execute("INSERT INTO paper_observations VALUES (?,?,?)", (identity, moment, json.dumps(row)))
        db.row_factory = sqlite3.Row
        with pytest.raises((ValueError, TypeError)):
            demo_runtime.summary(db, h.now + timedelta(seconds=2), "US")


def availability(value, **changes):
    proof = {key: value[key] for key in ("source", "filled_quantity", "fill_notional", "observed_at", "ingested_at")}
    proof.update(changes)
    return proof


def completed_harness(path, market, *, partial=False):
    h = Harness(path, market)
    quantity = 2 if partial else 1
    if partial and market == "KR":
        h.price = 40000
    h.source(qty=quantity)
    h.tick()
    if partial:
        h.now += timedelta(seconds=10)
        h.fill(qty=1)
        h.tick()
    h.now += timedelta(seconds=20)
    h.fill(qty=quantity, amount=h.price * quantity - 1)
    h.tick()
    h.now += timedelta(seconds=20)
    h.source("fixture-2", action="EXIT_NOW", qty=5)
    h.tick()
    h.now += timedelta(seconds=20)
    h.fill("2", qty=quantity, amount=h.price * quantity + 2)
    result = h.tick()
    return h, result


def append_observation(db, identity, moment, **changes):
    raw = db.execute("SELECT evidence FROM paper_observations WHERE id=? ORDER BY observed_at DESC LIMIT 1", (identity,)).fetchone()[0]
    proof = json.loads(raw)
    proof.update(observed_at=moment.isoformat(), ingested_at=moment.isoformat())
    proof.update(changes)
    db.execute("INSERT INTO paper_observations VALUES (?,?,?)", (identity, moment.isoformat(), json.dumps(proof, sort_keys=True)))


@pytest.mark.parametrize("market", ["KR", "US"])
@pytest.mark.parametrize("partial", [False, True])
def test_actual_broker_repeat_report_preserves_roundtrip_and_first_fill_but_refreshes_latest_clocks(tmp_path, market, partial):
    h, before = completed_harness(tmp_path, market, partial=partial)
    buy = next(o for o in before["orders"] if o["side"] == "BUY")
    assert before["evaluation"]["sample"]["closed_inventory_episodes"] == 1
    assert before["evaluation"]["realized_gross_pnl"] == 3
    assert buy["fill_availability"]["observed_at"] == buy["observed_at"]
    if partial:
        assert demo_runtime.at(buy["first_fill_observed_at"]) < demo_runtime.at(buy["fill_availability"]["observed_at"])
    h.now += timedelta(seconds=20)
    with h.factory(market, h.root / f"{market.lower()}-strategy.sqlite", lambda: h.now, (h.ticker,), h.credentials.scope()) as broker:
        old_rows = set(tuple(row) for row in broker.db.execute("SELECT * FROM paper_observations"))
        broker.reconcile(intent_id=buy["id"])
        after = demo_runtime.summary(broker.db, h.now, market)
        new_rows = set(tuple(row) for row in broker.db.execute("SELECT * FROM paper_observations"))
        assert old_rows < new_rows and len(new_rows) == len(old_rows) + 1
        broker.reconcile(intent_id=buy["id"])  # Identical full PK is still ignored.
        assert set(tuple(row) for row in broker.db.execute("SELECT * FROM paper_observations")) == new_rows
    repeated = next(o for o in after["orders"] if o["side"] == "BUY")
    assert repeated["fill_availability"] == buy["fill_availability"]
    assert repeated["first_fill_observed_at"] == buy["first_fill_observed_at"]
    assert demo_runtime.at(repeated["observed_at"]) == demo_runtime.at(repeated["ingested_at"]) == h.now
    assert repeated["observed_at"] != buy["observed_at"]
    assert after["order_counts"] == before["order_counts"] and after["owned"] == before["owned"]
    expected = dict(before["evaluation"])
    expected["analysis_as_of"] = after["evaluation"]["analysis_as_of"]
    expected["sample"] = {**expected["sample"], "last_observed_at": repeated["observed_at"]}
    assert after["evaluation"] == expected


def test_supplied_availability_restores_sequence_without_changing_latest_report():
    orders = roundtrip()
    proof = availability(orders[0])
    orders[0].update(fill_availability=proof, first_fill_observed_at=proof["observed_at"],
                     observed_at="2026-10-19T14:45:00+00:00", ingested_at="2026-10-19T14:45:01+00:00")
    result = evaluate(orders)
    assert result["realized_gross_pnl"] == 10 and result["sample"]["closed_inventory_episodes"] == 1
    assert result["sample"]["first_observed_at"] == proof["observed_at"]
    assert result["sample"]["last_observed_at"] == orders[0]["observed_at"]


@pytest.mark.parametrize("change", [
    {"source": "VALIDATION"}, {"source": None}, {"filled_quantity": 2}, {"filled_quantity": True},
    {"fill_notional": 99}, {"fill_notional": None}, {"fill_notional": float("nan")},
    {"observed_at": None}, {"observed_at": "bad"}, {"observed_at": "2026-10-19T14:00:00"},
    {"observed_at": "2026-02-30T14:00:00Z"}, {"observed_at": "2026-10-20T14:00:00Z"},
    {"observed_at": "2026-10-19T13:59:59Z"},
    {"ingested_at": None}, {"ingested_at": "bad"}, {"ingested_at": "2026-10-19T14:01:00"},
    {"ingested_at": "2026-10-19T14:00:59Z"}, {"ingested_at": "2026-10-19T14:01:02Z"},
    {"ingested_at": "2026-10-20T14:01:00Z"},
])
def test_invalid_availability_never_falls_back_to_latest_or_creates_roundtrip(change):
    buy = order()
    buy["fill_availability"] = availability(buy, **change)
    with pytest.raises(ValueError):
        evaluate([buy, roundtrip()[1]])


@pytest.mark.parametrize("proof", [None, {}, [], {"source": "KIS_DEMO_BROKER_REPORT"}])
def test_present_but_incomplete_availability_is_not_legacy_fallback(proof):
    with pytest.raises(ValueError):
        evaluate([order(fill_availability=proof)])


@pytest.mark.parametrize("value", [None, "bad", "2026-10-19T14:00:00", "2026-10-19T13:59:59Z", "2026-10-19T14:01:02Z", "2026-10-20T14:00:00Z"])
def test_first_positive_observation_requires_original_valid_clock(value):
    with pytest.raises(ValueError):
        evaluate([order(first_fill_observed_at=value)])


@pytest.mark.parametrize("market", ["KR", "US"])
@pytest.mark.parametrize("initial_missing", [False, True])
def test_money_disappearance_or_first_confirmation_never_borrows_an_earlier_availability(tmp_path, market, initial_missing):
    h, before = completed_harness(tmp_path, market)
    buy = next(o for o in before["orders"] if o["side"] == "BUY")
    with closing(sqlite3.connect(h.root / f"{market.lower()}-strategy.sqlite")) as db:
        db.row_factory = sqlite3.Row
        if initial_missing:
            old = db.execute("SELECT observed_at,evidence FROM paper_observations WHERE id=?", (buy["id"],)).fetchone()
            raw = json.loads(old[1])
            raw["fill_notional"] = None
            db.execute("UPDATE paper_observations SET evidence=? WHERE id=?", (json.dumps(raw), buy["id"]))
        else:
            h.now += timedelta(seconds=10)
            append_observation(db, buy["id"], h.now, fill_notional=None)
        h.now += timedelta(seconds=10)
        append_observation(db, buy["id"], h.now, fill_notional=buy["fill_notional"])
        result = demo_runtime.summary(db, h.now, market)
    repeated = next(o for o in result["orders"] if o["side"] == "BUY")
    assert demo_runtime.at(repeated["fill_availability"]["ingested_at"]) == h.now
    assert repeated["first_fill_observed_at"] == buy["first_fill_observed_at"]
    assert result["evaluation"]["sample"]["closed_inventory_episodes"] is None
    assert result["evaluation"]["realized_gross_pnl"] is None


@pytest.mark.parametrize("market", ["KR", "US"])
def test_partial_quantity_cannot_supply_current_complete_quantity_availability(tmp_path, market):
    h, result = completed_harness(tmp_path, market, partial=True)
    buy, sell = result["orders"]
    sell["prepared_at"] = (demo_runtime.at(buy["first_fill_observed_at"]) + timedelta(seconds=1)).isoformat()
    checked = evaluate_strategy_orders([buy, sell], market=market, as_of=h.now.isoformat(), gross_pnl=3, valuation_complete=True)
    assert checked["sample"]["closed_inventory_episodes"] is None
    assert checked["realized_gross_pnl"] is None


@pytest.mark.parametrize("change", [
    {"fill_notional": 198}, {"fill_notional": 201}, {"filled_qty": 0}, {"filled_qty": 2},
    {"source": "VALIDATION"}, {"mode": "actual"}, {"broker_order_id": "different"},
    {"observed_at": None}, {"ingested_at": None}, {"ingested_at": "2026-10-19T14:00:00"},
    {"ingested_at": "2026-02-30T14:00:00Z"}, {"ingested_at": "2099-01-01T00:00:00Z"},
    {"ingested_at": "2026-10-19T14:00:00Z"},
])
def test_prior_valid_availability_cannot_hide_invalid_later_proof(tmp_path, change):
    h, before = completed_harness(tmp_path, "US")
    buy = before["orders"][0]
    h.now += timedelta(seconds=10)
    with closing(sqlite3.connect(h.root / "us-strategy.sqlite")) as db:
        db.row_factory = sqlite3.Row
        append_observation(db, buy["id"], h.now, **change)
        with pytest.raises(ValueError):
            demo_runtime.summary(db, h.now, "US")


def test_valid_earlier_availability_does_not_bypass_future_report_fail_closed_contract(tmp_path):
    h, before = completed_harness(tmp_path, "US")
    with closing(sqlite3.connect(h.root / "us-strategy.sqlite")) as db:
        db.row_factory = sqlite3.Row
        append_observation(db, before["orders"][0]["id"], h.now + timedelta(seconds=10))
        with pytest.raises(ValueError, match="OBSERVATION_CLOCK"):
            demo_runtime.summary(db, h.now, "US")


def test_original_ack_is_required_even_when_earlier_availability_exists(tmp_path):
    h, before = completed_harness(tmp_path, "US")
    with closing(sqlite3.connect(h.root / "us-strategy.sqlite")) as db:
        db.row_factory = sqlite3.Row
        db.execute("UPDATE requests SET status='UNKNOWN' WHERE id=?", (before["orders"][0]["id"],))
        with pytest.raises(ValueError, match="OBSERVATION_PROOF"):
            demo_runtime.summary(db, h.now, "US")


@pytest.mark.parametrize("market", ["KR", "US"])
def test_repeated_reconciliation_retains_original_journal_owner_gate(tmp_path, market):
    h, before = completed_harness(tmp_path, market)
    calls = len(h.calls)
    h.credentials = type(h.credentials)("fixture-key", "fixture-secret", "87654321", "01")
    with pytest.raises(DemoError):
        with h.factory(market, h.root / f"{market.lower()}-strategy.sqlite", lambda: h.now, (h.ticker,), h.credentials.scope()) as broker:
            broker.reconcile(intent_id=before["orders"][0]["id"])
    assert len(h.calls) == calls


def test_equal_observation_clock_with_changed_economic_state_is_ambiguous(tmp_path):
    h, before = completed_harness(tmp_path, "US")
    buy = before["orders"][0]
    with closing(sqlite3.connect(h.root / "us-strategy.sqlite")) as db:
        db.row_factory = sqlite3.Row
        append_observation(db, buy["id"], demo_runtime.at(buy["observed_at"]), fill_notional=None)
        with pytest.raises(ValueError, match="AMBIGUOUS"):
            demo_runtime.summary(db, h.now, "US")


def test_availability_sorts_actual_instants_and_keeps_observed_ingested_from_one_report(tmp_path):
    h, before = completed_harness(tmp_path, "US")
    buy = before["orders"][0]
    h.now += timedelta(seconds=10)
    with closing(sqlite3.connect(h.root / "us-strategy.sqlite")) as db:
        db.row_factory = sqlite3.Row
        # The later -05:00 text sorts before the earlier UTC report.
        append_observation(db, buy["id"], h.now.astimezone(timezone(timedelta(hours=-5))))
        result = demo_runtime.summary(db, h.now, "US")
    repeated = result["orders"][0]
    assert repeated["fill_availability"] == buy["fill_availability"]
    assert demo_runtime.at(repeated["observed_at"]) == h.now
