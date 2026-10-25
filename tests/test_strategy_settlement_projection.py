"""The review API derives costs from configured readonly ledgers, never JSON claims."""
from copy import deepcopy
from datetime import timedelta
import hashlib
import json
from pathlib import Path
import sqlite3

import pytest

from tradingagents.charting.operations import kis_strategy_health, _readonly_strategy_costs
from tests.execution.test_strategy_settlement import imported_roundtrip


def runtime(archive, h, result):
    path = archive / "paper/kis-strategy-runtime.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"schema": "tradingagents.kis-strategy-runtime/v1", "mode": "KIS_DEMO_STRATEGY",
        "real_orders_enabled": False, "enabled": True, "checked_at": h.now.isoformat(),
        "markets": {h.market: {"status": "ACTIVE", "gate_passed": True,
                              "checked_at": h.now.isoformat(), **result}}}), encoding="utf-8")
    return path


def read(archive, h, *, ledger=True):
    return kis_strategy_health(archive, analysis_as_of=h.now,
                               strategy_ledger_dir=h.root if ledger else None)["markets"][h.market]["evaluation"]


@pytest.mark.parametrize("market", ["KR", "US"])
@pytest.mark.parametrize("partial", [False, True])
def test_actual_cost_projection_requires_independent_same_ledger_read(tmp_path, market, partial):
    h, _, _, result = imported_roundtrip(tmp_path, market, partial=partial)
    archive = tmp_path / "ui"
    runtime(archive, h, result)
    path = h.root / f"{market.lower()}-strategy.sqlite"
    before = (hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mtime_ns, set(h.root.iterdir()))
    calls = list(h.calls)
    view = read(archive, h)
    cost = 3 if partial else 2
    assert view["actual_cost"] == cost and view["net_pnl"] == 3-cost
    assert view["realized_net_pnl"] == 3-cost and view["exact_fifo_available"] is True
    assert view["cost_evidence_status"] == "COMPLETE_REVIEWED_IMPORT"
    assert view["actual_cost_basis"] == "OPERATOR_REVIEWED_EXECUTION_SETTLEMENT_IMPORT"
    assert view["readiness"] == "NOT_READY_FOR_REAL_INVESTMENT"
    assert view["automatic_live_transition"] is view["real_orders_enabled"] is False
    assert calls == h.calls
    assert before == (hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mtime_ns, set(h.root.iterdir()))
    encoded = json.dumps(view)
    for private in (h.credentials.scope(), "broker_order_id", "reviewer_id", "source_bytes", "account_scope"):
        assert private not in encoded


def test_cached_complete_cost_claim_without_configured_ledger_remains_unknown(tmp_path):
    h, _, _, result = imported_roundtrip(tmp_path)
    archive = tmp_path / "ui"
    runtime(archive, h, result)
    view = read(archive, h, ledger=False)
    assert view["actual_cost"] is view["net_pnl"] is None
    assert view["fees_known"] is view["settlement_known"] is False
    assert view["cost_evidence_status"] == "UNVERIFIED"
    assert "ACTUAL_FEES_TAXES_FX_UNVERIFIED" in view["unmet_criteria"]


def test_cached_amounts_cannot_override_validated_ledger(tmp_path):
    h, _, _, result = imported_roundtrip(tmp_path)
    archive = tmp_path / "ui"
    result = deepcopy(result)
    result["evaluation"].update(actual_cost=999, net_pnl=999, realized_net_pnl=999)
    runtime(archive, h, result)
    view = read(archive, h)
    assert (view["actual_cost"], view["net_pnl"], view["realized_net_pnl"]) == (2, 1, 1)


def test_future_import_cannot_fill_in_historical_unknown_costs(tmp_path):
    h, before, _, _ = imported_roundtrip(tmp_path)
    h.now -= timedelta(seconds=1)
    archive = tmp_path / "ui"
    runtime(archive, h, before)
    view = read(archive, h)
    assert view["actual_cost"] is view["net_pnl"] is None
    assert view["settlement_known"] is False


def test_missing_ledger_is_not_created_and_raw_claim_is_not_authority(tmp_path):
    h, _, _, result = imported_roundtrip(tmp_path)
    archive = tmp_path / "ui"
    runtime(archive, h, result)
    missing = tmp_path / "absent"
    view = kis_strategy_health(archive, analysis_as_of=h.now, strategy_ledger_dir=missing)["markets"][h.market]["evaluation"]
    assert view["actual_cost"] is None and not missing.exists()


def test_active_journal_and_wal_are_deferred_without_sqlite_side_effects(tmp_path):
    h, _, _, _ = imported_roundtrip(tmp_path)
    path = h.root / "us-strategy.sqlite"
    journal = Path(str(path)+"-journal")
    journal.write_bytes(b"active or hot journal; never repair here")
    assert _readonly_strategy_costs(h.root, "US", h.now) is None
    journal.unlink()
    with sqlite3.connect(path) as db:
        db.execute("PRAGMA journal_mode=WAL")
    before = {p.name: p.read_bytes() for p in h.root.iterdir() if p.is_file()}
    assert _readonly_strategy_costs(h.root, "US", h.now) is None
    assert before == {p.name: p.read_bytes() for p in h.root.iterdir() if p.is_file()}


def test_mismatched_cached_cashflows_cannot_produce_a_net_result(tmp_path):
    h, _, _, result = imported_roundtrip(tmp_path)
    archive = tmp_path / "ui"
    result["evaluation"]["sample"]["buy_filled_quantity"] += 1
    runtime(archive, h, result)
    view = read(archive, h)
    assert view is None or view["net_pnl"] is None


@pytest.mark.parametrize("bad_sample", [[1], "wrong", 1, True])
def test_malformed_cached_sample_cannot_invoke_ledger_reader(tmp_path, monkeypatch, bad_sample):
    from tradingagents.charting import operations
    monkeypatch.setattr(operations, "_readonly_strategy_costs", lambda *a: pytest.fail("Malformed sample triggered ledger read"))
    h, _, _, result = imported_roundtrip(tmp_path)
    result["evaluation"]["sample"] = bad_sample
    archive = tmp_path / "ui"
    runtime(archive, h, result)
    assert read(archive, h) is None


@pytest.mark.parametrize("fails", [False, True])
def test_readonly_connection_handle_is_closed_on_success_and_error(tmp_path, monkeypatch, fails):
    from datetime import datetime, timezone
    from tradingagents.execution import demo_runtime
    path = tmp_path / "us-strategy.sqlite"
    db = sqlite3.connect(path)
    db.execute("CREATE TABLE fixture (n INTEGER)")
    db.commit()
    db.close()
    def summary(db, cutoff, market):
        assert db.execute("PRAGMA query_only").fetchone()[0] == 1
        if fails:
            raise ValueError("Bad schema/evidence")
        return {"evaluation": {"cost_evidence_status": "UNVERIFIED"}, "orders": []}
    monkeypatch.setattr(demo_runtime, "summary", summary)
    result = _readonly_strategy_costs(tmp_path, "US", datetime.now(timezone.utc))
    assert (result is None) is fails
    # Windows refuses rename while an SQLite reader handle remains open. Do not
    # use gc.collect() as a substitute for deterministic resource release.
    path.rename(tmp_path / "released.sqlite")


@pytest.mark.parametrize("field,wrong", [("ticker", "WRONG"), ("id", "different-intent"), ("run_id", "other-run"), ("fill_notional", 999)])
def test_cost_cannot_be_displayed_against_a_different_cached_order(tmp_path, field, wrong):
    h, _, _, result = imported_roundtrip(tmp_path)
    result["orders"][0][field] = wrong
    archive = tmp_path / "ui"
    runtime(archive, h, result)
    view = read(archive, h)
    assert view["actual_cost"] is view["net_pnl"] is None


def test_partial_sell_projects_settled_fifo_without_borrowing_cached_open_inventory_mark(tmp_path):
    from tradingagents.execution import demo_runtime
    from tradingagents.execution.strategy_settlement import import_strategy_settlement
    from tests.execution.test_demo_runtime import Harness
    from tests.execution.test_strategy_settlement import document

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
    orders = h.tick()["orders"]
    h.now += timedelta(seconds=5)
    calls = list(h.calls)
    with h.factory("US", h.root / "us-strategy.sqlite", lambda: h.now, (h.ticker,), h.credentials.scope()) as broker:
        for order in orders:
            receipt, source = document(h, order, partial=True)
            assert import_strategy_settlement(broker, receipt, source_bytes=source)
        # The producer has a fresh mark, but the viewer cannot independently
        # reproduce its price from the cached timestamp and aggregate alone.
        mark = {**h.quote("US", h.ticker, lambda: h.now), "last_price": 210}
        result = demo_runtime.summary(broker.db, h.now, "US", {h.ticker: mark})
    assert result["evaluation"]["gross_pnl"] == 12
    assert result["evaluation"]["net_pnl"] == 9
    archive = tmp_path / "ui"
    runtime(archive, h, result)

    view = read(archive, h)
    assert view["actual_cost"] == 3
    assert view["realized_actual_cost"] == 2
    assert view["realized_net_pnl"] == -1
    assert view["exact_fifo_available"] is True
    assert view["net_pnl"] is None
    assert view["status"] == "AVAILABLE_GROSS_ONLY"
    assert view["cost_evidence_status"] == "COMPLETE_REVIEWED_IMPORT"
    assert view["sample"]["buy_filled_quantity"] == 2
    assert view["sample"]["sell_filled_quantity"] == 1
    assert "OPEN_STRATEGY_INVENTORY" in view["unmet_criteria"]
    assert "ORDER_PENDING_OR_UNRESOLVED" in view["unmet_criteria"]
    assert view["cost_sensitivity"]["includes_future_exit_cost"] is False
    assert view["readiness"] == "NOT_READY_FOR_REAL_INVESTMENT"
    assert view["automatic_live_transition"] is view["real_orders_enabled"] is False
    assert h.calls == calls
