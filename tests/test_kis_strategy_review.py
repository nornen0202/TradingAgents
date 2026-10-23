from http.server import ThreadingHTTPServer
from datetime import datetime, timezone
import json
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from tradingagents.atomic_io import atomic_write_json
from tradingagents.charting.operations import kis_strategy_health
from tradingagents.charting.server import make_handler

NOW = "2026-10-19T01:00:00Z"


def receipt():
    return {"schema": "tradingagents.kis-strategy-runtime/v1", "mode": "KIS_DEMO_STRATEGY", "enabled": True,
        "real_orders_enabled": False, "checked_at": NOW, "private": "PRIVATE_SECRET", "markets": {
            "KR": {"status": "ACTIVE", "checked_at": NOW, "gate_passed": True, "blockers": [], "account": "PRIVATE_ACCOUNT",
                "order_counts": {"FILLED": 1}, "orders": [{"id": "PRIVATE_ID", "ticker": "005930.KS", "run_id": "strategy-run-1", "side": "BUY",
                    "quantity": 1, "filled_quantity": 1, "limit_price": 70000, "average_fill_price": 69900, "status": "FILLED", "cancel_status": None,
                    "prepared_at": "2026-10-19T00:59:00Z", "observed_at": "2026-10-19T00:59:10Z"}],
                "performance": {"basis": "STRATEGY_GROSS_CASHFLOWS_PLUS_MARKED_HOLDINGS", "currency": "KRW", "status": "AVAILABLE", "gross_pnl": 100,
                    "observed_at": NOW, "mark_times": ["2026-10-19T00:59:50Z"], "net_pnl": 999, "fees_known": True, "settlement_known": True}},
            "US": {"status": "WAITING_VALIDATION", "checked_at": NOW, "gate_passed": False, "blockers": ["VALIDATION_REQUIRED"]}}}


def write(root, payload):
    atomic_write_json(root / "paper/kis-strategy-runtime.json", payload)


def test_native_currency_gross_performance_order_history_and_private_projection(tmp_path):
    write(tmp_path, receipt())
    value = kis_strategy_health(tmp_path, analysis_as_of=NOW)
    assert "PRIVATE" not in json.dumps(value)
    kr, us = value["markets"]["KR"], value["markets"]["US"]
    assert kr["orders"][0]["average_fill_price"] == 69900
    assert kr["performance"]["gross_pnl"] == 100
    assert kr["performance"]["net_pnl"] is None
    assert kr["performance"]["fees_known"] is False and kr["performance"]["settlement_known"] is False
    assert us["status"] == "WAITING_VALIDATION"


def test_planning_rejections_and_producer_limits_are_visible_without_secrets(tmp_path):
    from tests.execution.test_strategy_diagnostics import allocation
    raw = receipt()
    row = raw["markets"]["KR"]
    row["allocation_diagnostics"] = allocation()
    row["source_diagnostics"] = {"status": "EXECUTION_OBSERVATIONS_AVAILABLE", "strategy_rows": 30,
                                  "execution_ready_rows": 30, "allocated_orders": None}
    row["refresh_attempt"] = {"market": "kr", "session_date": "2026-10-19", "started_at": "2026-10-19T00:50:00Z",
        "finished_at": "2026-10-19T00:51:00Z", "status": "FAILED", "consecutive_failures": 3,
        "real_orders_enabled": False, "error_type": "LocalStorageHeadroomError", "private": "PRIVATE_SECRET"}
    write(tmp_path, raw)
    view = kis_strategy_health(tmp_path, analysis_as_of=NOW)["markets"]["KR"]
    assert view["allocation_diagnostics"]["reason_counts"] == {"NO_AUTHORIZED_EXECUTION_ACTION": 30}
    assert view["source_diagnostics"]["status"] == "EXECUTION_OBSERVATIONS_AVAILABLE"
    assert view["refresh_health"]["status"] == "RETRY_LIMIT_REACHED"
    assert "PRIVATE" not in json.dumps(view)
    row["refresh_attempt"]["finished_at"] = "2026-10-20T00:51:00Z"
    write(tmp_path, raw)
    assert kis_strategy_health(tmp_path, analysis_as_of=NOW)["markets"]["KR"]["refresh_health"] == {"status": "UNVERIFIED"}


@pytest.mark.parametrize("changes", [{"checked_at": None}, {"checked_at": "bad"}, {"checked_at": "2026-10-20T01:00:00Z"},
    {"mode": "real"}, {"real_orders_enabled": True}, {"markets": []}])
def test_invalid_root_cannot_show_trading(tmp_path, changes):
    write(tmp_path, {**receipt(), **changes})
    assert kis_strategy_health(tmp_path, analysis_as_of=NOW)["status"] == "UNAVAILABLE"


@pytest.mark.parametrize("stamp", [None, "bad", "2026-10-19", "2026-10-20T01:00:00Z"])
def test_unknown_or_future_fill_and_performance_not_past_evidence(tmp_path, stamp):
    raw = receipt()
    raw["markets"]["KR"]["orders"][0]["observed_at"] = stamp
    raw["markets"]["KR"]["performance"]["observed_at"] = stamp
    write(tmp_path, raw)
    kr = kis_strategy_health(tmp_path, analysis_as_of=NOW)["markets"]["KR"]
    assert not kr["orders"] and kr["performance"] is None


def test_currency_missing_basis_and_unobserved_pnl_cannot_claim_performance(tmp_path):
    raw = receipt()
    raw["markets"]["KR"]["performance"]["currency"] = "USD"
    write(tmp_path, raw)
    assert kis_strategy_health(tmp_path, analysis_as_of=NOW)["markets"]["KR"]["performance"] is None
    raw["markets"]["KR"]["orders"] = "bad"
    raw["markets"]["KR"]["order_counts"] = []
    raw["markets"]["KR"]["blockers"] = 1
    write(tmp_path, raw)
    assert not kis_strategy_health(tmp_path, analysis_as_of=NOW)["markets"]["KR"]["orders"]


def evaluation_fixture():
    from tradingagents.execution.strategy_evaluation import evaluate_strategy_orders
    orders = [{"id": f"private-{side}", "ticker": "005930.KS", "side": side, "quantity": 1,
               "filled_quantity": 1, "fill_notional": amount, "status": "FILLED", "mode": "demo",
               "source": "KIS_DEMO_BROKER_REPORT", "strategy_performance": True,
               "prepared_at": stamp, "observed_at": stamp, "ingested_at": stamp}
              for side, amount, stamp in (("BUY", 69900, "2026-10-19T00:58:00Z"),
                                          ("SELL", 70000, "2026-10-19T00:59:00Z"))]
    return evaluate_strategy_orders(orders, market="KR", as_of=NOW, gross_pnl=100, valuation_complete=True)


def test_cost_assumptions_are_separate_from_actual_net_and_private_fields(tmp_path):
    raw = receipt()
    evaluation = evaluation_fixture()
    evaluation.update(private="PRIVATE_SECRET", net_pnl=999, actual_cost=0, fees_known=True)
    raw["markets"]["KR"]["evaluation"] = evaluation
    write(tmp_path, raw)
    result = kis_strategy_health(tmp_path, analysis_as_of=NOW)["markets"]["KR"]["evaluation"]
    assert "PRIVATE" not in json.dumps(result)
    assert result["sample"]["closed_inventory_episodes"] == 1
    assert result["cost_sensitivity"]["scenarios"][0]["estimated_pnl_after_assumed_cost"] == -40
    assert result["net_pnl"] is None and result["actual_cost"] is None and result["fees_known"] is False
    assert result["readiness"] == "NOT_READY_FOR_REAL_INVESTMENT"
    assert result["automatic_live_transition"] is False


@pytest.mark.parametrize("damage", ["future", "missing_date", "bad_date", "future_fill", "actual_basis",
                                   "wrong_currency", "wrong_market", "bad_cost", "bad_pnl", "bad_sample", "live",
                                   "zero_fill_quantity", "empty_unmet", "no_fills_realized"])
def test_invalid_cost_evaluation_never_appears_as_evidence(tmp_path, damage):
    raw = receipt()
    evaluation = evaluation_fixture()
    if damage in {"future", "missing_date", "bad_date"}:
        evaluation["analysis_as_of"] = {"future": "2026-10-20T00:00:00Z", "missing_date": None, "bad_date": "bad"}[damage]
    elif damage == "future_fill":
        evaluation["sample"]["last_observed_at"] = "2026-10-20T00:00:00Z"
    elif damage == "actual_basis":
        evaluation["cost_sensitivity"]["basis"] = "ACTUAL_COST"
    elif damage == "wrong_currency":
        evaluation["currency"] = "USD"
    elif damage == "wrong_market":
        evaluation["market"] = "US"
    elif damage == "bad_cost":
        evaluation["cost_sensitivity"]["scenarios"][0]["estimated_cost"] = 0
    elif damage == "bad_pnl":
        evaluation["cost_sensitivity"]["scenarios"][0]["estimated_pnl_after_assumed_cost"] = float("nan")
    elif damage == "bad_sample":
        evaluation["sample"]["buy_filled_orders"] = True
    elif damage == "zero_fill_quantity":
        evaluation["sample"]["buy_filled_quantity"] = evaluation["sample"]["sell_filled_quantity"] = 0
    elif damage == "empty_unmet":
        evaluation["unmet_criteria"] = []
    elif damage == "no_fills_realized":
        from tradingagents.execution.strategy_evaluation import evaluate_strategy_orders
        evaluation = evaluate_strategy_orders([], market="KR", as_of=NOW, gross_pnl=None, valuation_complete=True)
        evaluation.update(realized_basis="FULLY_CLOSED_STRATEGY_CASHFLOWS", realized_gross_pnl=999)
    else:
        evaluation["real_orders_enabled"] = True
    raw["markets"]["KR"]["evaluation"] = evaluation
    write(tmp_path, raw)
    assert kis_strategy_health(tmp_path, analysis_as_of=NOW)["markets"]["KR"]["evaluation"] is None


def test_localhost_endpoint_read_only_and_past_cutoff(tmp_path, monkeypatch):
    from tradingagents.charting import server as module
    monkeypatch.setattr(module, "now_utc", lambda: datetime(2026, 10, 20, tzinfo=timezone.utc))
    write(tmp_path, receipt())
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(archive_dir=tmp_path))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}/api/kis-strategy-health"
    try:
        with urlopen(base + "?as_of=2026-10-19T01%3A00%3A00Z") as response:
            value = json.load(response)
            assert value["read_only"] is True
            assert value["markets"]["KR"]["performance"]["gross_pnl"] == 100
        with urlopen(base + "?as_of=2026-10-18T00%3A00%3A00Z") as response:
            assert json.load(response)["status"] == "UNAVAILABLE"
    finally:
        with pytest.raises(HTTPError) as post:
            urlopen(Request(base, method="POST"))
        assert post.value.code == 501
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
