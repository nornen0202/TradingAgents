from datetime import datetime, timezone
import hashlib
from http.server import ThreadingHTTPServer
import json
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pandas as pd
import pytest

from tradingagents.charting.bars import validate_bars
from tradingagents.charting.capture import ChartCapture, capture_daily_frame, normalize_kis_bars
from tradingagents.charting.indicators import anchored_vwap, volume_profile
from tradingagents.charting.report import build_review, render_review
from tradingagents.charting.server import make_handler, STATIC
from tradingagents.charting.snapshot import get_replay_snapshot
from tradingagents.scheduled.config import _load_scanner_settings

ASOF = "2026-10-16T12:00:00+00:00"


def bar(**changes):
    return {"timestamp": "2026-10-16T09:00:00+00:00", "available_at": "2026-10-16T09:01:00+00:00",
            "observed_at": "2026-10-16T09:02:00+00:00", "open": 100, "high": 110, "low": 90,
            "close": 105, "volume": 1000, "session_id": "2026-10-16", "interval": "1m", **changes}


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def ticker_archive(tmp_path):
    directory = tmp_path / "tickers" / "TEST"
    directory.mkdir(parents=True)
    write(directory / "chart_evidence.json", {"ticker": "TEST", "bars": [bar()], "public_display_allowed": False})
    write(directory / "execution_update.json", {"execution_asof": "2026-10-16T10:00:00+00:00",
          "market_data_asof": "2026-10-16T09:59:00+00:00", "ingested_at": "2026-10-16T10:00:01+00:00",
          "decision_state": "WAIT", "reason_codes": ["volume_rule_not_met"]})
    write(directory / "analysis.json", {"finished_at": "2026-10-16T09:30:00+00:00"})
    write(directory / "execution_contract.json", {"ingested_at": "2026-10-16T09:30:00+00:00",
         "structured_levels": [{"price": 111, "label": "진입 기준"}]})
    return directory


@pytest.mark.parametrize("field,value", [("timestamp", None), ("observed_at", "bad"),
    ("available_at", "2026-10-16"), ("timestamp", "2026-10-17T00:00:00Z"),
    ("observed_at", "2026-10-17T00:00:00Z"), ("volume", -1), ("close", float("nan")),
    ("high", 99), ("low", 101), ("open", True), ("interval", "unknown"), ("session_id", None)])
def test_invalid_bars_never_enter_indicators(field, value):
    result = validate_bars([bar(**{field: value})], analysis_as_of=ASOF)
    assert result["bars"] == []
    assert result["rejected"]


def test_duplicate_and_future_invariance():
    normal = validate_bars([bar()], analysis_as_of=ASOF)
    assert validate_bars([bar(), bar()], analysis_as_of=ASOF)["bars"] == normal["bars"]
    assert validate_bars([bar(), bar(close=104)], analysis_as_of=ASOF)["bars"] == []
    future = bar(timestamp="2026-10-17T09:00:00Z", available_at="2026-10-17T09:01:00Z", observed_at="2026-10-17T09:02:00Z")
    assert anchored_vwap([bar(), future], anchor=bar()["timestamp"], analysis_as_of=ASOF) == anchored_vwap([bar()], anchor=bar()["timestamp"], analysis_as_of=ASOF)
    normalized = normal["bars"][0]
    assert normalized["event_time"] == normalized["timestamp"]
    assert normalized["ingested_at"] == normalized["observed_at"]
    assert normalized["evaluated_at"] == ASOF


def test_anchored_vwap_known_values_zero_volume_and_sessions():
    first = bar(high=100, low=100, open=100, close=100, volume=10)
    second = bar(timestamp="2026-10-16T09:02:00Z", available_at="2026-10-16T09:03:00Z", observed_at="2026-10-16T09:04:00Z", high=200, low=200, open=200, close=200, volume=30)
    result = anchored_vwap([first, second], anchor=first["timestamp"], analysis_as_of=ASOF)
    assert [point["value"] for point in result["series"]] == [100, 175]
    assert anchored_vwap([bar(volume=0)], anchor=first["timestamp"], analysis_as_of=ASOF)["series"][0]["value"] is None
    assert anchored_vwap([first], anchor=first["timestamp"], analysis_as_of=ASOF, session_id="other")["series"] == []
    with pytest.raises(ValueError):
        anchored_vwap([first, {**second, "interval": "1d"}], anchor=first["timestamp"], analysis_as_of=ASOF)


def test_profile_volume_conservation_and_value_area():
    result = volume_profile([bar()], analysis_as_of=ASOF, bins=10)
    assert result["total_volume"] == pytest.approx(1000)
    assert sum(row["volume"] for row in result["bins"]) == pytest.approx(1000)
    assert result["value_area_low"] <= result["poc"] <= result["value_area_high"]
    assert result["approximate"] is True
    assert volume_profile([], analysis_as_of=ASOF)["poc"] is None
    assert volume_profile([bar(volume=0)], analysis_as_of=ASOF)["poc"] is None
    flat = volume_profile([bar(open=100, high=100, low=100, close=100)], analysis_as_of=ASOF)
    assert flat["total_volume"] == pytest.approx(1000)
    for bins in (0, True, 500, 2.5):
        with pytest.raises(ValueError):
            volume_profile([bar()], analysis_as_of=ASOF, bins=bins)


def test_kis_requires_date_and_completed_minute_not_requested_interval():
    row = {"stck_bsop_date": "20261016", "stck_cntg_hour": "100000", "stck_oprc": "100",
           "stck_hgpr": "110", "stck_lwpr": "90", "stck_prpr": "105", "cntg_vol": "10"}
    result = normalize_kis_bars([row], observed_at="2026-10-16T10:02:00+09:00", timezone_name="Asia/Seoul")
    assert result[0]["interval"] == "1m"
    assert normalize_kis_bars([row], observed_at="2026-10-16T10:00:59+09:00", timezone_name="Asia/Seoul") == []
    assert normalize_kis_bars([{**row, "stck_bsop_date": ""}], observed_at=ASOF, timezone_name="Asia/Seoul") == []


def test_capture_is_local_scoped_and_uses_actual_session_close():
    frame = pd.DataFrame([{"Date": "2026-10-15", "Open": 100, "High": 110, "Low": 90, "Close": 105, "Volume": 10}])
    recorder = ChartCapture("TEST")
    token = recorder.activate()
    try:
        capture_daily_frame("TEST", frame, curr_date="2026-10-15")
        capture_daily_frame("OTHER", frame, curr_date="2026-10-15")
    finally:
        recorder.reset(token)
    result = recorder.artifact(analysis_as_of=datetime.now(timezone.utc))
    assert len(result["bars"]) == 1
    assert result["bars"][0]["timestamp"] == "2026-10-15T20:00:00+00:00"
    assert result["public_display_allowed"] is False
    assert recorder.artifact(analysis_as_of="2026-10-15T20:01:00Z")["bars"] == []


def test_review_excludes_late_decision_plan_evidence_and_escapes(tmp_path):
    directory = ticker_archive(tmp_path)
    write(directory / "evidence_ledger.json", {"items": [{"claim": "<script>alert(1)</script>", "kind": "fact",
         "known_at": "2026-10-16T10:00:00Z", "published_at": "2026-10-16T09:00:00Z", "observed_at": "2026-10-16T10:00:00Z"},
         {"claim": "UNVERIFIED_SECRET"}]})
    early = get_replay_snapshot("TEST", "2026-10-16T09:15:00Z", ticker_dir=directory)
    assert early["execution"] == {} and early["plan"] == {} and early["evidence"] == []
    late = get_replay_snapshot("TEST", ASOF, ticker_dir=directory)
    assert late["execution_verdict"] == "WAIT"
    assert late["block_reasons"] == ["volume_rule_not_met"]
    assert late["price_levels"][0]["price"] == 111
    assert late["freshness_status"] == "STALE"
    rendered = render_review(late)
    assert "<script>alert(1)</script>" not in rendered
    assert "&lt;script&gt;" in rendered and "UNVERIFIED_SECRET" not in rendered
    public = render_review(late, public=True)
    assert "<svg" not in public and "volume_rule_not_met" not in public
    assert late["read_only"] is True and late["broker_orders_sent"] == 0


def test_event_replay_reconstructs_prior_correction_version(tmp_path):
    from tradingagents.dataflows.event_timeline import build_event_timeline
    directory = ticker_archive(tmp_path)
    first = {"ticker": "TEST", "event_id": "e", "version_id": "v1", "title": "original",
             "published_at": "2026-10-16T09:00:00Z", "known_at": "2026-10-16T09:00:00Z", "observed_at": "2026-10-16T09:01:00Z"}
    corrected = {**first, "version_id": "v2", "title": "CORRECTED_FUTURE", "status": "corrected", "supersedes_version_id": "v1",
                 "published_at": "2026-10-16T11:00:00Z", "known_at": "2026-10-16T11:00:00Z", "observed_at": "2026-10-16T11:01:00Z"}
    write(directory / "event_timeline.json", build_event_timeline([first, corrected], analysis_as_of=ASOF))
    review = build_review(directory, analysis_as_of="2026-10-16T10:00:00Z")
    assert review["events"]["events"][0]["title"] == "original"
    assert "CORRECTED_FUTURE" not in json.dumps(review)


def test_vendor_integrity_and_license_present():
    manifest = json.loads((STATIC / "vendor-manifest.json").read_text())
    for name, digest in manifest["files"].items():
        assert hashlib.sha256((STATIC / name).read_bytes()).hexdigest() == digest
    assert "Apache License" in (STATIC / "LICENSE.lightweight-charts").read_text()
    assert "TradingView" in (STATIC / "NOTICE.lightweight-charts").read_text(encoding="utf-8")


def test_config_validates_scanner_conditions(tmp_path):
    condition = {"field": "volume_ratio", "op": "gte", "value": 1.5}
    assert _load_scanner_settings({"condition": condition}, base_dir=tmp_path, default_market="KR").condition == condition
    with pytest.raises(ValueError):
        _load_scanner_settings({"condition": {"eval": "side_effect()"}}, base_dir=tmp_path, default_market="KR")


def test_local_snapshot_api_blocks_traversal_rebinding_and_writes(tmp_path):
    ticker_archive(tmp_path)
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(tmp_path))
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    url = f"http://127.0.0.1:{server.server_port}"
    try:
        assert json.load(urlopen(url + "/api/tickers")) == ["TEST"]
        import time
        from urllib.parse import urlencode
        query = {"ticker": "TEST", "as_of": "2026-10-16T12:00:00Z"}
        for _ in range(100):
            with urlopen(url + "/api/snapshot?" + urlencode(query)) as response:
                snapshot = json.load(response)
                if response.status != 202:
                    break
            query.update(catalog_generation=snapshot["generation"], snapshot_job=snapshot["job_token"])
            time.sleep(.01)
        else:
            pytest.fail("Fixture snapshot did not finish")
        assert snapshot["ticker"] == "TEST"
        for path, code in (("/api/snapshot?ticker=..", 400), ("/../../AGENTS.md", 404)):
            with pytest.raises(HTTPError) as error:
                urlopen(url + path)
            assert error.value.code == code
        with pytest.raises(HTTPError) as error:
            urlopen(Request(url + "/api/tickers", headers={"Host": "attacker.example"}))
        assert error.value.code == 403
        with pytest.raises(HTTPError) as error:
            urlopen(Request(url + "/api/snapshot", method="POST", data=b"{}"))
        assert error.value.code == 501
    finally:
        server.shutdown()
        worker.join(timeout=5)
        server.server_close()
