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
