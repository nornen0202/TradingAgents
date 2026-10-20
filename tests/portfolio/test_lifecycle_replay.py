"""No API, credentials, LLM or clock dependencies: evidence is fixture-only."""
import json
import sqlite3

import pytest

from tradingagents.execution.paper import PaperBroker, PaperLimits
from tradingagents.performance.action_outcomes import record_run_recommendations, record_execution_receipt, update_action_outcomes
from tradingagents.performance.journal import record_fill_retrospectives
from tradingagents.performance.lifecycle import append_lifecycle_event, stable_signal_id
from tradingagents.performance.replay import replay_action_history


T0 = "2026-09-21T10:00:00+09:00"
T1 = "2026-09-21T10:01:00+09:00"
T2 = "2026-09-21T10:02:00+09:00"
T3 = "2026-09-21T10:03:00+09:00"


def put(path, **changes):
    event = dict(event_id="signal-one", signal_id="one", kind="SIGNAL", occurred_at=T0,
                 available_at=T0, ingested_at=T0, payload={"ticker": "A", "action": "BUY"})
    event.update(changes)
    event["ingested_at"] = changes.get("ingested_at", event["available_at"])
    return append_lifecycle_event(path, **event)


def fill(path, event_id, *, quantity=1, price=100, cost=1, side="BUY", **changes):
    event = dict(event_id=event_id, signal_id="one", intent_id="order-one", kind="FILL", mode="actual",
                 occurred_at=T1, available_at=T1, confirmed_at=T1, settled_at=T2,
                 ingested_at=T1,
                 payload={"ticker": "A", "side": side, "quantity": quantity, "price": price, "cost": cost, "currency": "KRW"})
    event.update(changes)
    event["ingested_at"] = changes.get("ingested_at", event["available_at"])
    return append_lifecycle_event(path, **event)


def test_empty_and_missing_are_read_only_and_require_explicit_asof(tmp_path):
    missing = tmp_path / "missing.sqlite"
    result = replay_action_history(missing, analysis_as_of=T0)
    assert result["read_only"] and result["broker_orders_sent"] == 0
    assert result["events"] == [] and not missing.exists()
    with pytest.raises(ValueError):
        replay_action_history(missing, analysis_as_of="2026-09-21")


def test_ticker_projection_preserves_cutoff_and_skips_unrelated_validation(tmp_path, monkeypatch):
    from tradingagents.performance import replay
    path = tmp_path / "events.sqlite"
    put(path)
    put(path, event_id="future-a", available_at=T3)
    for index in range(20):
        put(path, event_id=f"other-{index}", payload={"ticker": "B", "action": "BUY"})
    expected = [event for event in replay_action_history(path, analysis_as_of=T2)["events"]
                if event["payload"]["ticker"] == "A"]
    original = replay.validate_event
    validated = []
    def validate(event):
        validated.append(event["payload"]["ticker"])
        return original(event)
    monkeypatch.setattr(replay, "validate_event", validate)
    projected = replay_action_history(path, analysis_as_of=T2, ticker="a")
    assert projected["events"] == expected
    assert projected["accounts"] == {}
    assert validated == ["A", "A"]


def test_ticker_projection_filters_in_sql_before_json_decoding(tmp_path, monkeypatch):
    from tradingagents.performance import replay
    path = tmp_path / "events.sqlite"
    put(path)
    for i in range(20):
        put(path, event_id=f"other-{i}", payload={"ticker": "B", "action": "BUY"})
    with sqlite3.connect(path) as conn:
        conn.execute("INSERT INTO lifecycle_events SELECT 'bad-legacy', signal_id, intent_id, kind, mode, occurred_at, available_at, confirmed_at, settled_at, 'broken', ingested_at FROM lifecycle_events WHERE event_id='other-0'")
    original = replay.json.loads
    decoded = []
    def loads(value):
        decoded.append(value)
        return original(value)
    monkeypatch.setattr(replay.json, "loads", loads)
    result = replay_action_history(path, analysis_as_of=T2, ticker="a")
    assert len(result["events"]) == 1
    assert len(decoded) == 1


@pytest.mark.parametrize("clock,value", [
    ("occurred_at", None), ("available_at", None), ("available_at", "bad"),
    ("available_at", "2026-09-21T10:00:00"), ("confirmed_at", None), ("settled_at", None),
    ("confirmed_at", "2026-09-20T10:00:00+09:00"),
])
def test_invalid_missing_or_naive_clocks_fail_before_append(tmp_path, clock, value):
    path = tmp_path / "events.sqlite"
    with pytest.raises(ValueError):
        fill(path, "fill", **{clock: value})
    assert not path.exists()


@pytest.mark.parametrize("clock", ["available_at", "confirmed_at", "settled_at", "ingested_at"])
def test_future_evidence_does_not_affect_any_replay_field(tmp_path, clock):
    path = tmp_path / "events.sqlite"
    put(path)
    put(path, event_id="intent", intent_id="order-one", kind="INTENT", mode="actual",
        payload={"ticker": "A", "quantity": 3, "side": "BUY", "status": "PENDING"})
    before = replay_action_history(path, analysis_as_of=T2)
    fill(path, "future", **{clock: T3})
    after = replay_action_history(path, analysis_as_of=T2)
    assert after == before


def test_append_dedup_conflict_and_sql_immutability(tmp_path):
    path = tmp_path / "events.sqlite"
    assert put(path) and not put(path)
    with pytest.raises(ValueError, match="different evidence"):
        put(path, payload={"ticker": "A", "action": "SELL"})
    with sqlite3.connect(path) as conn:
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            conn.execute("UPDATE lifecycle_events SET signal_id='changed'")
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            conn.execute("DELETE FROM lifecycle_events")
    assert len(replay_action_history([path, path], analysis_as_of=T2)["events"]) == 1


def test_partial_incremental_fills_costs_and_cash_are_separate_from_outcome(tmp_path):
    path = tmp_path / "events.sqlite"
    put(path)
    put(path, event_id="intent", intent_id="order-one", kind="INTENT", mode="actual",
        payload={"ticker": "A", "quantity": 3, "side": "BUY", "status": "PENDING"})
    put(path, event_id="outcome", kind="OUTCOME", confirmed_at=T0,
        payload={"ticker": "A", "return_5d": .20, "measurement_scope": "counterfactual_recommendation_price_path"})
    fill(path, "first", quantity=1, price=100, cost=1)
    partial = replay_action_history(path, analysis_as_of=T2, initial_cash=1000)
    assert partial["intents"][0]["status"] == "PARTIAL"
    assert partial["accounts"]["actual:KRW"]["cash"] == 899
    assert partial["signals"][0]["recommendation_outcome"]["return_5d"] == .20
    fill(path, "second", quantity=2, price=110, cost=2, occurred_at=T2, available_at=T2, confirmed_at=T2)
    complete = replay_action_history(path, analysis_as_of=T2, initial_cash=1000)
    assert complete["intents"][0]["status"] == "FILLED"
    assert complete["accounts"]["actual:KRW"] == {"cash": 677, "positions": None, "costs": 3, "cash_known": True,
        "positions_known": False, "position_changes": {"A": 3}}
    assert replay_action_history(path, analysis_as_of=T2, ticker="A")["accounts"] == {}
    assert replay_action_history(path, analysis_as_of=T2)["accounts"]["actual:KRW"]["cash"] is None


def quote(at, price=100):
    return {"A": dict(as_of=at, price_krw=price, spread_bps=0, session="regular", executable=True)}


def signal(at=T0, **changes):
    return dict(signal_id="source-one", run_id="run-one", signal_action="STARTER_NOW", source="TradingAgents",
                ticker="A", action="BUY", quantity=2, execution_ready=True, available_at=at,
                valid_until="2026-09-21T11:00:00+09:00", **changes)


def test_paper_producer_atomic_link_fifo_partial_review_and_restart(tmp_path):
    path = tmp_path / "paper.sqlite"
    limits = PaperLimits(cash_floor=0, max_order_nav=.5, max_single_name=1, max_daily_turnover=1,
                         slippage_bps=0, fee_bps=100, sell_tax_bps=0)
    broker = PaperBroker(path, limits)
    broker.seed(dict(as_of=T0, available_cash_krw=1000, positions=[]))
    broker.step(now=T0, quotes=quote(T0), signals=[signal()])
    broker.step(now=T1, quotes=quote(T1), signals=[])
    sell = signal(T2)
    sell.update(signal_id="source-exit", run_id="run-exit", signal_action="REDUCE_NOW", action="REDUCE", quantity=1)
    broker.step(now=T2, quotes=quote(T2, 110), signals=[sell])
    final = broker.step(now=T3, quotes=quote(T3, 110), signals=[])
    rows = broker.db.execute("SELECT id FROM trade_journal").fetchall()
    assert len(rows) == 1
    exit_id = "fill:paper:" + next(row["id"] for row in final["orders"] if row["side"] == "SELL")
    assert record_fill_retrospectives(broker.db, exit_event_id=exit_id) == [rows[0][0]]
    assert broker.db.execute("SELECT COUNT(*) FROM learned_intuitions").fetchone()[0] == 1
    broker.close()
    before = replay_action_history(path, analysis_as_of=T2)
    assert before["retrospectives"] == []
    replay = replay_action_history(path, analysis_as_of=T3)
    assert replay["accounts"]["paper:KRW"]["cash"] == pytest.approx(final["cash_krw"])
    assert replay["accounts"]["paper:KRW"]["positions"] == {"A": 1}
    review = replay["retrospectives"][0]
    assert review["net_profit"] == pytest.approx(7.9)  # 10 gross - 1 entry fee - 1.1 exit fee
    assert review["closed_quantity"] == 1 and review["total_cost"] == pytest.approx(2.1)
    assert review["entry_signal_id"] == stable_signal_id("run-one", "A", "STARTER_NOW")
    assert review["measurement_scope"] == "realized_fill_return_after_costs"
    reopened = PaperBroker(path, limits)
    reopened.close()
    assert replay_action_history(path, analysis_as_of=T3) == replay


def test_bad_step_rolls_back_lifecycle_and_conflicting_signal_is_rejected(tmp_path):
    path = tmp_path / "paper.sqlite"
    broker = PaperBroker(path, PaperLimits(cash_floor=0, max_order_nav=.5, max_single_name=1))
    broker.seed(dict(as_of=T0, available_cash_krw=1000, positions=[]))
    broker.step(now=T0, quotes=quote(T0), signals=[signal()])
    snapshot = replay_action_history(path, analysis_as_of=T3)
    changed = signal()
    changed["quantity"] = 3
    with pytest.raises(ValueError, match="different evidence"):
        broker.step(now=T1, quotes=quote(T1), signals=[changed])
    assert replay_action_history(path, analysis_as_of=T3) == snapshot
    assert broker.db.execute("SELECT status FROM orders").fetchone()[0] == "PENDING"
    broker.close()


def make_run(tmp_path):
    run = tmp_path / "run"
    (run / "portfolio-private").mkdir(parents=True)
    (run / "run.json").write_text(json.dumps({"run_id": "run-one", "finished_at": T0}), encoding="utf-8")
    (run / "portfolio-private" / "portfolio_report.json").write_text(json.dumps({"actions": [
        {"canonical_ticker": "A", "action_now": "STARTER_NOW", "position_metrics": {"current_price": 100}}
    ]}), encoding="utf-8")
    return run


def test_tracker_producer_outcome_future_missing_bad_dates_and_revision_visibility(tmp_path):
    path = tmp_path / "performance.sqlite"
    run = make_run(tmp_path)
    assert record_run_recommendations(run, path, recorded_at=T0) == 1
    assert record_run_recommendations(run, path, recorded_at=T0) == 0
    prices = {"A": [{"date": "2026-09-21", "close": 100}, {"date": "2026-09-22", "close": 110},
        {"date": "2026-09-23", "close": 120}, {"date": "2026-09-24", "close": 130},
        {"date": "bad", "close": 999}, {"close": 999}, {"date": "2026-09-31", "close": 999},
        {"date": "2026-09-21garbage", "close": 999}, {"date": "2026-09-21", "close": float("nan")} ]}
    update_action_outcomes(path, "2026-09-22", price_history=prices, recorded_at="2026-09-22T23:59:59.999999+00:00")
    earlier = replay_action_history(path, analysis_as_of="2026-09-22T23:59:59.999999+00:00")
    outcome = earlier["signals"][0]["recommendation_outcome"]
    assert outcome["return_1d"] == .1 and outcome["return_3d"] is None
    update_action_outcomes(path, "2026-09-24", price_history=prices, recorded_at="2026-09-24T23:59:59.999999+00:00")
    assert replay_action_history(path, analysis_as_of="2026-09-22T23:59:59.999999+00:00") == earlier
    later = replay_action_history(path, analysis_as_of="2026-09-24T23:59:59.999999+00:00")
    assert later["signals"][0]["recommendation_outcome"]["return_3d"] == .3
    assert later["fills"] == []


def test_actual_receipt_requires_costs_clocks_and_incremental_fill_identity(tmp_path):
    path = tmp_path / "actual.sqlite"
    row = {"run_id": "run-one", "ticker": "A", "action": "STARTER_NOW", "created_at": T0, "recommended_price": 99}
    receipt = dict(status="PARTIALLY_FILLED", source="kis", filled_quantity=1, requested_quantity=2,
        intent_id="broker-intent", fill_id="execution-1", side="BUY", fill_price=100, cost=1, currency="KRW",
        executed_at=T1, intent_at=T0, confirmed_at=T1, settled_at=T2)
    for key in ("fill_id", "cost", "settled_at", "confirmed_at", "intent_at"):
        bad = {k: v for k, v in receipt.items() if k != key}
        assert record_execution_receipt(path, row=row, receipt=bad) is False
    assert not path.exists()
    assert record_execution_receipt(path, row=row, receipt=receipt, recorded_at=T1)
    assert not record_execution_receipt(path, row=row, receipt=receipt, recorded_at=T2)
    assert replay_action_history(path, analysis_as_of=T1)["fills"] == []
    assert len(replay_action_history(path, analysis_as_of=T2)["fills"]) == 1


def test_reimport_does_not_backdate_first_ingestion(tmp_path):
    path = tmp_path / "late.sqlite"
    put(path, ingested_at=T3)
    assert not put(path, ingested_at=T0)
    assert replay_action_history(path, analysis_as_of=T2)["events"] == []
    result = replay_action_history(path, analysis_as_of=T3)
    assert result["events"][0]["ingested_at"] == T3
    assert result["events"][0]["event_time"] == T0
    assert result["events"][0]["evaluated_at"]
    assert result["events"][0]["is_amended"] is False


def test_default_ingestion_records_actual_import_time(tmp_path):
    path = tmp_path / "now.sqlite"
    append_lifecycle_event(path, event_id="historical-source", signal_id="signal", kind="SIGNAL",
        occurred_at=T0, available_at=T0, payload={"ticker": "A"})
    assert replay_action_history(path, analysis_as_of=T3)["events"] == []
    with sqlite3.connect(path) as conn:
        ingested = conn.execute("SELECT ingested_at FROM lifecycle_events").fetchone()[0]
    assert ingested != T0
    assert len(replay_action_history(path, analysis_as_of=ingested)["events"]) == 1


def test_incremental_overfill_and_mismatched_order_terms_rejected(tmp_path):
    path = tmp_path / "partial.sqlite"
    put(path, event_id="intent", intent_id="order-one", kind="INTENT", mode="actual",
        payload={"ticker": "A", "quantity": 2, "side": "BUY", "status": "PENDING"})
    fill(path, "first", quantity=1)
    with pytest.raises(ValueError, match="exceed"):
        fill(path, "too-many", quantity=2)
    with pytest.raises(ValueError, match="order terms"):
        fill(path, "wrong-side", side="SELL")
    assert len(replay_action_history(path, analysis_as_of=T2)["fills"]) == 1


def test_actual_receipt_arriving_after_signal_is_imported_on_same_run_retry(tmp_path):
    path = tmp_path / "performance.sqlite"
    run = make_run(tmp_path)
    record_run_recommendations(run, path, recorded_at=T0)
    report_path = run / "portfolio-private" / "portfolio_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["actions"][0]["execution_receipt"] = dict(status="FILLED", source="kis", filled_quantity=1,
        requested_quantity=1, intent_id="later-intent", fill_id="later-fill", side="BUY", fill_price=100,
        cost=1, currency="KRW", executed_at=T1, intent_at=T0, confirmed_at=T1, settled_at=T2)
    report_path.write_text(json.dumps(report), encoding="utf-8")
    assert record_run_recommendations(run, path, recorded_at=T3) == 0
    assert replay_action_history(path, analysis_as_of=T2)["fills"] == []
    result = replay_action_history(path, analysis_as_of=T3)
    assert len(result["signals"]) == 1 and len(result["fills"]) == 1


def test_actual_review_waits_for_settlement_and_handles_out_of_order_import(tmp_path):
    path = tmp_path / "actual.sqlite"
    buy_row = {"run_id": "buy", "ticker": "A", "action": "STARTER_NOW", "created_at": T0}
    sell_row = {"run_id": "sell", "ticker": "A", "action": "EXIT_NOW", "created_at": T1}
    buy = dict(status="FILLED", source="kis", filled_quantity=2, requested_quantity=2,
        intent_id="buy-intent", fill_id="buy-exec", side="BUY", fill_price=100, cost=2, currency="KRW",
        executed_at=T1, intent_at=T0, confirmed_at=T1, settled_at=T1)
    sell = dict(status="FILLED", source="kis", filled_quantity=2, requested_quantity=2,
        intent_id="sell-intent", fill_id="sell-exec", side="SELL", fill_price=110, cost=2.2, currency="KRW",
        executed_at=T2, intent_at=T1, confirmed_at=T2, settled_at=T3)
    # Importing the exit first never invents its missing cost basis.
    assert record_execution_receipt(path, row=sell_row, receipt=sell, recorded_at=T2)
    assert record_execution_receipt(path, row=buy_row, receipt=buy, recorded_at=T2)
    assert replay_action_history(path, analysis_as_of=T2)["retrospectives"] == []
    # The later reconciliation creates a review only after settlement is known.
    assert not record_execution_receipt(path, row=sell_row, receipt=sell, recorded_at=T3)
    result = replay_action_history(path, analysis_as_of=T3)
    assert len(result["retrospectives"]) == 1
    assert result["retrospectives"][0]["net_profit"] == pytest.approx(15.8)
    assert not record_execution_receipt(path, row=sell_row, receipt=sell, recorded_at="2026-09-21T10:04:00+09:00")
    assert len(replay_action_history(path, analysis_as_of="2026-09-21T10:04:00+09:00")["retrospectives"]) == 1
    assert replay_action_history(path, analysis_as_of=T2)["retrospectives"] == []


def test_seed_holdings_with_unknown_acquisition_cost_do_not_fabricate_realized_return(tmp_path):
    path = tmp_path / "paper.sqlite"
    limits = PaperLimits(cash_floor=0, max_sell_order_nav=1, max_daily_turnover=1)
    broker = PaperBroker(path, limits)
    broker.seed(dict(as_of=T0, available_cash_krw=1000, positions=[
        {"canonical_ticker": "A", "quantity": 2, "market_price_krw": 100}]))
    sell = signal()
    sell.update(action="SELL", quantity=1, signal_action="EXIT_NOW")
    broker.step(now=T0, quotes=quote(T0), signals=[sell])
    broker.step(now=T1, quotes=quote(T1), signals=[])
    broker.close()
    result = replay_action_history(path, analysis_as_of=T2)
    assert len(result["fills"]) == 1
    assert result["retrospectives"] == []
    assert result["accounts"]["paper:KRW"]["positions"] == {"A": 1}


def test_date_only_close_is_unavailable_intraday_and_unknown_availability_excluded(tmp_path):
    path = tmp_path / "performance.sqlite"
    run = make_run(tmp_path)
    record_run_recommendations(run, path, recorded_at=T0)
    prices = {"A": [{"date": "2026-09-21", "close": 100},
        {"date": "2026-09-22", "close": 110},
        {"date": "2026-09-23", "close": 999, "available_at": "bad"},
        {"date": "2026-09-24", "close": 999, "available_at": "2026-09-25T00:00:00+00:00"}]}
    update_action_outcomes(path, "2026-09-22T12:00:00+00:00", price_history=prices,
                           recorded_at="2026-09-22T12:00:00+00:00")
    result = replay_action_history(path, analysis_as_of="2026-09-22T12:00:00+00:00")
    assert result["signals"][0]["recommendation_outcome"]["return_1d"] is None
    update_action_outcomes(path, "2026-09-24", price_history=prices,
                           recorded_at="2026-09-24T23:59:59.999999+00:00")
    result = replay_action_history(path, analysis_as_of="2026-09-24T23:59:59.999999+00:00")
    assert result["signals"][0]["recommendation_outcome"]["return_1d"] == .1
    assert result["signals"][0]["recommendation_outcome"]["return_3d"] is None
