"""The localhost viewer separates read probes from observed VTS execution proof."""
import copy
from http.server import ThreadingHTTPServer
import json
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from tradingagents.charting.operations import kis_validation_health, paper_health
from tradingagents.charting.server import make_handler


ASOF = "2026-10-16T01:00:00Z"


def receipt():
    return {"schema": "tradingagents.kis-session-validation/v1", "mode": "KIS_DEMO",
        "live_orders_enabled": False, "checked_at": "2026-10-16T00:59:59Z", "markets": {
            market: {"status": "VERIFIED", "checked_at": "2026-10-16T00:59:50Z", "stages": {
                stage: {"verified": True, "observed_at": "2026-10-16T00:55:00Z",
                    "source": "KIS_DEMO_BROKER_ACK" if stage == "submitted" else "KIS_DEMO_BROKER_REPORT",
                    "order_id": "PRIVATE_ORDER", "price": 12345}
                for stage in ("submitted", "filled", "cancelled")},
                "campaign_id": "PRIVATE_CAMPAIGN", "account": "PRIVATE_ACCOUNT", "app_key": "PRIVATE_SECRET"}
            for market in ("KR", "US")}, "local_paper": {"path": "C:/PRIVATE_FILE", "cash": 12345}}


def write(root, value):
    path = root / "paper/kis-session-validation.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def test_projection_displays_only_timestamped_broker_proofs(tmp_path):
    write(tmp_path, receipt())
    projected = kis_validation_health(tmp_path, analysis_as_of=ASOF)
    assert projected["read_only"] and projected["live_orders_enabled"] is False
    for row in projected["markets"].values():
        assert row["status"] == "VERIFIED"
        assert all(stage["verified"] for stage in row["stages"].values())
        assert set(row) == {"market", "mode", "status", "checked_at", "stages", "blocker"}
        for stage in row["stages"].values():
            assert set(stage) == {"verified", "observed_at"}
    assert "PRIVATE" not in json.dumps(projected) and "12345" not in json.dumps(projected)


@pytest.mark.parametrize("changes", [{"checked_at": None}, {"checked_at": "bad"}, {"checked_at": "2026-10-16"},
    {"checked_at": "2026-10-16T02:00:00Z"}, {"schema": "unknown"}, {"mode": "REAL"},
    {"live_orders_enabled": True}, {"live_orders_enabled": 0}, {"markets": []}])
def test_invalid_root_receipt_reveals_no_validation_state(tmp_path, changes):
    before = kis_validation_health(tmp_path, analysis_as_of=ASOF)
    write(tmp_path, {**receipt(), **changes})
    assert kis_validation_health(tmp_path, analysis_as_of=ASOF) == before


@pytest.mark.parametrize("stamp", [None, "bad", "2026-10-16", "2026-10-16T01:00:01Z", "2026-10-16T00:59:59.5Z"])
def test_market_receipt_must_be_known_by_root_clock(tmp_path, stamp):
    value = receipt()
    value["markets"]["US"]["checked_at"] = stamp
    write(tmp_path, value)
    result = kis_validation_health(tmp_path, analysis_as_of=ASOF)
    assert result["markets"]["US"]["status"] == "UNAVAILABLE"
    assert result["markets"]["KR"]["status"] == "VERIFIED"


@pytest.mark.parametrize("changes", [{"observed_at": None}, {"observed_at": "bad"}, {"observed_at": "2026-10-16"},
    {"observed_at": "2026-10-16T02:00:00Z"}, {"observed_at": "2026-10-16T00:59:51Z"},
    {"verified": 1}, {"verified": False}, {"source": "FIXTURE"}, {"source": "KIS_DEMO_BROKER_ACK"}])
def test_ack_fake_or_unknown_clock_cannot_prove_a_fill(tmp_path, changes):
    value = receipt()
    value["markets"]["KR"]["stages"]["filled"].update(changes)
    write(tmp_path, value)
    row = kis_validation_health(tmp_path, analysis_as_of=ASOF)["markets"]["KR"]
    assert row["status"] == "ATTENTION"
    assert row["stages"]["filled"] == {"verified": False, "observed_at": None}
    assert row["stages"]["submitted"]["verified"]


def test_empty_and_pending_results_never_manufacture_execution_proofs(tmp_path):
    write(tmp_path, {})
    assert kis_validation_health(tmp_path, analysis_as_of=ASOF)["markets"]["US"]["status"] == "UNAVAILABLE"
    value = receipt()
    value["markets"]["US"].update(status="WAITING_SESSION", stages={}, blocker="PRIVATE_SECRET")
    write(tmp_path, value)
    row = kis_validation_health(tmp_path, analysis_as_of=ASOF)["markets"]["US"]
    assert row["status"] == "WAITING_SESSION" and row["blocker"] == "OPERATOR_REVIEW_REQUIRED"
    assert not any(stage["verified"] for stage in row["stages"].values())
    with pytest.raises(ValueError, match="timezone"):
        kis_validation_health(tmp_path, analysis_as_of="2026-10-16")


def test_validation_api_is_fixed_path_read_only_and_works_without_tickers(tmp_path):
    write(tmp_path, receipt())
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(archive_dir=tmp_path))
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        assert json.load(urlopen(base + "/api/tickers?as_of=" + ASOF)) == []
        payload = json.load(urlopen(base + "/api/kis-validation-health?as_of=" + ASOF + "&path=C:/PRIVATE_FILE"))
        assert payload["markets"]["US"]["status"] == "VERIFIED"
        assert "PRIVATE" not in json.dumps(payload)
        for route in ("/api/kis-validation-health", "/api/kis-demo-health"):
            with pytest.raises(HTTPError) as error:
                urlopen(Request(base + route, method="POST", data=b"{}"))
            assert error.value.code == 501
        with pytest.raises(HTTPError) as error:
            urlopen(base + "/api/kis-validation-health?as_of=2099-01-01T00:00:00Z")
        assert error.value.code == 400
    finally:
        server.shutdown()
        worker.join(timeout=5)
        server.server_close()


def test_paper_receipt_clocks_do_not_hide_a_stale_market_or_backdate_counts(tmp_path):
    path = tmp_path / "status.json"
    value = {"schema": "tradingagents.paper-runtime/v1", "mode": "LOCAL_PAPER_ONLY", "enabled": True,
        "broker_orders_sent": 0, "real_orders_enabled": False, "checked_at": "2026-10-16T00:59:59Z",
        "markets": {"kr": {"status": "ACTIVE", "checked_at": "2026-10-16T00:30:00Z",
                    "last_quote_at": "2026-10-16T00:30:01Z", "order_counts": {"FILLED": 1}},
                    "us": {"status": "ACTIVE", "checked_at": "2026-10-16T01:00:00Z", "order_counts": {"FILLED": 9}}}}
    path.write_text(json.dumps(value))
    view = paper_health(path, analysis_as_of=ASOF)
    assert not view["stale"] and view["markets"]["kr"]["stale"]
    assert view["markets"]["kr"]["last_quote_at"] is None
    assert "us" not in view["markets"]
    unsafe = copy.deepcopy(value)
    unsafe["broker_orders_sent"] = False
    path.write_text(json.dumps(unsafe))
    assert paper_health(path, analysis_as_of=ASOF)["status"] == "UNAVAILABLE"
