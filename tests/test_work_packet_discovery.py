import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Barrier

import pytest

from tradingagents.work import packet


AT = datetime(2026, 10, 29, 17, tzinfo=timezone.utc)
RUN = "20261029T165900_fixture"


@pytest.fixture
def current(tmp_path):
    root = tmp_path / "archive"
    directory = root / "runs/2026" / RUN
    directory.mkdir(parents=True)
    manifest = {"run_id": RUN, "status": "success", "started_at": (AT-timedelta(minutes=1)).isoformat(),
        "finished_at": (AT-timedelta(seconds=1)).isoformat(), "settings": {"market": "US", "run_mode": "overlay_only"}}
    attempt = {"run_id": RUN, "status": "SUCCESS", "market": "US", "run_mode": "overlay_only", "started_at": manifest["started_at"],
        "finished_at": (AT-timedelta(microseconds=1)).isoformat()}
    bundle = {"run_id": RUN, "market": "US", "quality": {"decision_ready": True}}
    def save(m=manifest, a=attempt, b=bundle, pointer=None):
        for path, value in ((root/"latest-run.json", m if pointer is None else pointer),
                            (directory/"run.json", m), (directory/"attempt.json", a),
                            (directory/"decision_bundle_v2.json", b)):
            path.write_text(json.dumps(value), encoding="utf-8")
    save()
    return root, directory, manifest, attempt, bundle, save


def test_guarded_ready_producer_avoids_archive_scan(current, monkeypatch):
    root, directory, manifest, attempt, bundle, save = current
    original = Path.glob
    def glob(path, pattern):
        if path == root/"runs":
            pytest.fail("exact verified producer must not scan historical manifests")
        return original(path, pattern)
    monkeypatch.setattr(Path, "glob", glob)
    selected = packet._market_sources(root, "us", expected_producer_run_id=RUN, now=AT)
    assert selected == [{"manifest": manifest, "bundle": bundle, "run_dir": directory.resolve()}]


@pytest.mark.parametrize("case", ["pointer_missing", "pointer_stale", "canonical_changed", "failed", "running",
    "missing_clock", "bad_clock", "future_clock", "naive_clock", "wrong_attempt", "wrong_attempt_clock",
    "future_attempt", "wrong_attempt_market", "wrong_attempt_mode", "wrong_bundle", "wrong_market", "unready", "escape"])
def test_guarded_discovery_never_shortcuts_unverified_source(current, case):
    root, directory, manifest, attempt, bundle, save = current
    expected = RUN
    pointer = None
    if case == "pointer_stale": pointer = {**manifest, "run_id": "previous"}
    elif case == "canonical_changed": pointer = {**manifest, "status": "failed"}
    elif case == "failed": manifest["status"] = "failed"
    elif case == "running": attempt["status"] = "RUNNING"
    elif case == "missing_clock": manifest["finished_at"] = None
    elif case == "bad_clock": manifest["finished_at"] = "bad"
    elif case == "future_clock": manifest["finished_at"] = (AT+timedelta(seconds=1)).isoformat()
    elif case == "naive_clock": manifest["finished_at"] = AT.replace(tzinfo=None).isoformat()
    elif case == "wrong_attempt": attempt["run_id"] = "other"
    elif case == "wrong_attempt_clock": attempt["started_at"] = AT.isoformat()
    elif case == "future_attempt": attempt["finished_at"] = (AT+timedelta(seconds=1)).isoformat()
    elif case == "wrong_attempt_market": attempt["market"] = "KR"
    elif case == "wrong_attempt_mode": attempt["run_mode"] = "full"
    elif case == "wrong_bundle": bundle["run_id"] = "other"
    elif case == "wrong_market": bundle["market"] = "KR"
    elif case == "unready": bundle["quality"]["decision_ready"] = False
    elif case == "escape": expected = "../other"
    save(pointer=pointer)
    if case == "pointer_missing": (root/"latest-run.json").unlink()
    assert packet._guarded_current_source(root, "us", expected, AT) is None


def test_changed_pointer_uses_full_discovery_instead_of_pinning_old_source(current):
    root, directory, manifest, attempt, bundle, save = current
    newer = "20261029T170000_newer"
    new_dir = root/"runs/2026"/newer
    new_dir.mkdir()
    new_manifest = {**manifest, "run_id": newer, "started_at": AT.isoformat()}
    new_bundle = {**bundle, "run_id": newer}
    for path, value in ((new_dir/"run.json", new_manifest), (new_dir/"decision_bundle_v2.json", new_bundle),
                        (root/"latest-run.json", new_manifest)):
        path.write_text(json.dumps(value), encoding="utf-8")
    selected = packet._market_sources(root, "us", expected_producer_run_id=RUN, now=AT)
    assert selected[0]["manifest"]["run_id"] == newer


def test_exact_non_executable_current_avoids_historical_scan_without_promotion(current, monkeypatch):
    root, directory, manifest, attempt, bundle, save = current
    bundle["quality"]["decision_ready"] = False
    bundle["strategy_table"] = [{"ticker": "SPG", "action_ready": False,
        "execution": {"readiness": "NEEDS_LIVE_RECHECK", "action_now": None}}]
    save()
    monkeypatch.setattr(Path, "glob", lambda *args: pytest.fail("historical references must not age fresh inputs"))
    selected = packet._market_sources(root, "us", expected_producer_run_id=RUN, now=AT)
    assert selected == [{"manifest": manifest, "bundle": bundle, "run_dir": directory.resolve()}]
    assert selected[0]["bundle"]["quality"]["decision_ready"] is False
    assert selected[0]["bundle"]["strategy_table"][0]["execution"]["action_now"] is None


@pytest.mark.parametrize("readiness", [None, "false", 0])
def test_non_boolean_readiness_never_qualifies_for_exact_non_executable_read(current, readiness):
    root, directory, manifest, attempt, bundle, save = current
    bundle["quality"]["decision_ready"] = readiness
    save()
    assert packet._guarded_current_source(root, "us", RUN, AT, allow_non_executable=True) is None


@pytest.mark.parametrize("case", ["failed", "running", "future", "changed_pointer"])
def test_non_executable_read_still_requires_exact_terminal_source(current, case):
    root, directory, manifest, attempt, bundle, save = current
    bundle["quality"]["decision_ready"] = False
    pointer = None
    if case == "failed":
        manifest["status"] = "failed"
    elif case == "running":
        attempt["status"] = "RUNNING"
    elif case == "future":
        attempt["finished_at"] = (AT + timedelta(seconds=1)).isoformat()
    elif case == "changed_pointer":
        pointer = {**manifest, "run_id": "newer"}
    save(pointer=pointer)
    assert packet._guarded_current_source(root, "us", RUN, AT, allow_non_executable=True) is None


@pytest.mark.parametrize("elapsed", [119, 120])
def test_exact_non_executable_packet_preserves_expiry_and_does_not_select_past_ready(tmp_path, elapsed):
    from tests.test_chatgpt_work import _write_market_run
    run_id = "20261029T170000_current"
    directory = _write_market_run(tmp_path, run_id=run_id, market="us",
        started_at=AT.isoformat(), row_mode="CONDITIONAL")
    manifest_path = directory / "run.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.update(status="success", finished_at=(AT + timedelta(seconds=1)).isoformat())
    manifest["settings"]["execution_max_data_age_seconds"] = 120
    for path in (manifest_path, tmp_path / "latest-run.json"):
        path.write_text(json.dumps(manifest), encoding="utf-8")
    (directory / "attempt.json").write_text(json.dumps({"run_id": run_id, "status": "SUCCESS",
        "market": "US", "run_mode": "overlay_only", "started_at": manifest["started_at"],
        "finished_at": manifest["finished_at"]}), encoding="utf-8")
    _write_market_run(tmp_path, run_id="20261029T165900_previous", market="us",
        started_at=(AT - timedelta(minutes=1)).isoformat(), row_mode="IMMEDIATE")
    before = (directory / "decision_bundle_v2.json").read_bytes()
    body = packet.build_surface_packet("us", archive_dir=tmp_path,
        youtube_archive_dir=tmp_path / "youtube", prism_archive_dir=tmp_path / "prism",
        expected_producer_run_id=run_id, now=AT + timedelta(seconds=elapsed))["body"]
    assert body["current"]["run_id"] == run_id and body["last_ready"] == {}
    row = body["current"]["bundle"]["strategy_table"][0]
    assert row["execution"]["valid_until"] == (AT + timedelta(seconds=120)).isoformat()
    assert row["quality"]["execution_ready"] is False
    assert row["execution"]["action_now"] is None
    assert body["guardrails"]["expired_at_build"] is (elapsed == 120)
    assert (directory / "decision_bundle_v2.json").read_bytes() == before


def test_supporting_sources_read_independently_at_exact_same_cutoff(monkeypatch):
    barrier = Barrier(2)
    def read(path, *, now):
        assert now is AT
        barrier.wait(timeout=3)
        return {"source_health": "OK", "events": [], "coverage": {}}
    monkeypatch.setattr(packet, "_youtube_body", read)
    monkeypatch.setattr(packet, "_prism_body", read)
    result = packet._supporting_context({"youtube": Path("youtube"), "prism": Path("prism")}, now=AT)
    assert result["youtube"]["source_health"] == result["prism"]["source_health"] == "OK"
