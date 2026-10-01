from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
from pathlib import Path

import pytest

from tradingagents.scheduled import runner


def manifest(run_id, started, finished, *, market="US", mode="full"):
    return {"run_id": run_id, "started_at": started, "finished_at": finished,
            "status": "success", "settings": {"market": market, "run_mode": mode},
            "tickers": [{"ticker": "AAPL" if market == "US" else "005930",
                         "status": "success", "artifacts": {"analysis_json": "analysis.json"}}]}


def publish(root, payload):
    run_dir = root / "runs" / "2026" / payload["run_id"]
    return runner._publish_completed_run_manifest(archive_dir=root, run_dir=run_dir, manifest=payload)


def read_latest(root):
    return json.loads((root / "latest-run.json").read_text(encoding="utf-8"))


def test_older_full_finishing_late_does_not_replace_new_overlay(tmp_path):
    overlay = manifest("20261001-140000-overlay", "2026-10-01T14:00:00Z", "2026-10-01T14:05:00Z", mode="overlay_only")
    old_full = manifest("20261001-110000-full", "2026-10-01T11:00:00Z", "2026-10-01T15:00:00Z")
    assert publish(tmp_path, overlay)
    assert not publish(tmp_path, old_full)
    assert read_latest(tmp_path) == overlay
    assert json.loads((tmp_path / "runs/2026" / old_full["run_id"] / "run.json").read_text()) == old_full
    # Full baseline remains independently discoverable; no full/overlay merge.
    assert runner._find_latest_full_run_manifest(tmp_path, market="US")["run_id"] == old_full["run_id"]


def test_timezone_order_and_cross_market_payload_are_not_merged(tmp_path):
    us = manifest("us", "2026-10-01T10:00:00-04:00", "2026-10-01T10:01:00-04:00")
    kr = manifest("kr", "2026-10-01T22:00:00+09:00", "2026-10-01T23:10:00+09:00", market="KR")
    assert publish(tmp_path, us)
    assert not publish(tmp_path, kr)
    assert read_latest(tmp_path) == us
    assert runner._find_latest_full_run_manifest(tmp_path, market="KR")["run_id"] == "kr"


def test_new_full_advances_as_whole_manifest(tmp_path):
    old = manifest("old", "2026-10-01T14:00:00Z", "2026-10-01T14:01:00Z", mode="overlay_only")
    new = manifest("new", "2026-10-01T15:00:00Z", "2026-10-01T15:01:00Z")
    old["overlay_source_run_id"] = "yesterday"
    publish(tmp_path, old)
    assert publish(tmp_path, new)
    assert read_latest(tmp_path) == new
    assert "overlay_source_run_id" not in read_latest(tmp_path)


def test_simultaneous_writers_choose_deterministic_latest_start(tmp_path):
    payloads = [manifest(f"run-{i:02d}", f"2026-10-01T14:{i:02d}:00Z", "2026-10-01T15:00:00Z") for i in range(20)]
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lambda payload: publish(tmp_path, payload), reversed(payloads)))
    assert read_latest(tmp_path) == payloads[-1]
    assert len(list((tmp_path / "runs/2026").glob("*/run.json"))) == 20


def test_equal_starts_use_run_identity_tie_break_not_finish_time(tmp_path):
    a = manifest("a", "2026-10-01T14:00:00Z", "2026-10-01T16:00:00Z")
    b = manifest("b", "2026-10-01T14:00:00Z", "2026-10-01T15:00:00Z")
    publish(tmp_path, b)
    assert not publish(tmp_path, a)
    assert read_latest(tmp_path) == b


@pytest.mark.parametrize("broken", ["{broken", "[]", '{"run_id":"legacy","started_at":"2026-10-01T14:00:00"}'])
def test_unverified_existing_pointer_is_preserved(tmp_path, broken):
    path = tmp_path / "latest-run.json"
    path.write_text(broken)
    payload = manifest("new", "2026-10-01T15:00:00Z", "2026-10-01T15:01:00Z")
    with pytest.raises(RuntimeError, match="unverified chronology"):
        publish(tmp_path, payload)
    assert path.read_text() == broken
    assert (tmp_path / "runs/2026/new/run.json").is_file()


@pytest.mark.parametrize("field,value", [
    ("started_at", "2026-10-01T14:00:00"), ("started_at", None), ("finished_at", None),
    ("finished_at", "2026-10-01T14:00:00"), ("finished_at", "2026-10-01T13:00:00Z"),
])
def test_invalid_candidate_does_not_change_pointer(tmp_path, field, value):
    old = manifest("old", "2026-10-01T14:00:00Z", "2026-10-01T14:01:00Z")
    publish(tmp_path, old)
    candidate = deepcopy(old)
    candidate.update(run_id="new")
    candidate[field] = value
    with pytest.raises(ValueError):
        publish(tmp_path, candidate)
    assert read_latest(tmp_path) == old


def test_lock_failure_has_no_unlocked_pointer_fallback(monkeypatch, tmp_path):
    old = manifest("old", "2026-10-01T14:00:00Z", "2026-10-01T14:01:00Z")
    publish(tmp_path, old)
    def unavailable(*args, **kwargs):
        raise TimeoutError("lock timeout")
    monkeypatch.setattr(runner, "interprocess_file_lock", unavailable)
    new = manifest("new", "2026-10-01T15:00:00Z", "2026-10-01T15:01:00Z")
    with pytest.raises(TimeoutError):
        publish(tmp_path, new)
    assert read_latest(tmp_path) == old


def test_duplicate_identity_cannot_replace_other_market_archive(tmp_path):
    us = manifest("same", "2026-10-01T14:00:00Z", "2026-10-01T14:01:00Z")
    kr = manifest("same", "2026-10-01T14:00:00Z", "2026-10-01T14:02:00Z", market="KR")
    publish(tmp_path, us)
    with pytest.raises(RuntimeError, match="identity collision"):
        publish(tmp_path, kr)
    assert read_latest(tmp_path) == us
    assert json.loads((tmp_path / "runs/2026/same/run.json").read_text()) == us


def test_identical_publication_is_idempotent(tmp_path):
    payload = manifest("same", "2026-10-01T14:00:00Z", "2026-10-01T14:01:00Z")
    assert publish(tmp_path, payload)
    assert publish(tmp_path, payload)
    assert read_latest(tmp_path) == payload


def test_late_full_thesis_is_not_hidden_by_newer_overlay_index(tmp_path):
    old = manifest("old-full", "2026-10-01T10:00:00Z", "2026-10-01T10:10:00Z")
    overlay = manifest("later-overlay", "2026-10-01T14:00:00Z", "2026-10-01T14:05:00Z", mode="overlay_only")
    overlay["overlay_source_run_id"] = old["run_id"]
    overlay["tickers"][0]["artifacts"]["microstructure_snapshot_json"] = "microstructure.json"
    overlay["tickers"][0]["artifacts"]["microstructure_report_md"] = "microstructure.md"
    new_full = manifest("new-full", "2026-10-01T12:00:00Z", "2026-10-01T15:00:00Z")
    publish(tmp_path, old)
    publish(tmp_path, overlay)
    assert not publish(tmp_path, new_full)
    assert read_latest(tmp_path) == overlay  # quote lineage remains independent
    selected = runner._resolve_latest_overlay_source_manifest(tmp_path, tickers=["AAPL"], market="US")
    assert selected == new_full  # next overlay copies the new whole thesis
    assert "microstructure_snapshot_json" not in selected["tickers"][0]["artifacts"]


@pytest.mark.parametrize("defect", ["failed", "partial", "coverage", "other_market", "unfinished", "target_gap", "future"])
def test_late_full_with_quality_or_coverage_gap_is_not_promoted(tmp_path, defect):
    old = manifest("old-full", "2026-10-01T10:00:00Z", "2026-10-01T10:10:00Z")
    overlay = manifest("later-overlay", "2026-10-01T14:00:00Z", "2026-10-01T14:05:00Z", mode="overlay_only")
    overlay["overlay_source_run_id"] = old["run_id"]
    overlay["tickers"][0]["artifacts"]["microstructure_snapshot_json"] = "microstructure.json"
    overlay["tickers"][0]["artifacts"]["microstructure_report_md"] = "microstructure.md"
    new_full = manifest("new-full", "2026-10-01T12:00:00Z", "2026-10-01T15:00:00Z")
    if defect == "failed":
        new_full["status"] = "failed"
    elif defect == "partial":
        new_full["summary"] = {"failed_tickers": 1}
    elif defect == "coverage":
        new_full["active_universe"] = {"mode": "adaptive_required_coverage", "coverage": {"complete": False}}
    elif defect == "other_market":
        new_full["settings"]["market"] = "KR"
    elif defect == "target_gap":
        new_full["tickers"][0]["ticker"] = "AMZN"
    elif defect == "future":
        new_full["started_at"] = "2099-10-01T12:00:00Z"
        new_full["finished_at"] = "2099-10-01T15:00:00Z"
    else:
        del new_full["finished_at"]
    publish(tmp_path, old)
    publish(tmp_path, overlay)
    runner._write_json(tmp_path / "runs/2026/new-full/run.json", new_full)
    selected = runner._resolve_latest_overlay_source_manifest(tmp_path, tickers=["AAPL"], market="US")
    assert selected == overlay


def test_overlay_chain_is_compared_to_its_full_thesis_not_quote_clock(tmp_path):
    old = manifest("old-full", "2026-10-01T10:00:00Z", "2026-10-01T10:10:00Z")
    first = manifest("first-overlay", "2026-10-01T13:00:00Z", "2026-10-01T13:05:00Z", mode="overlay_only")
    second = manifest("second-overlay", "2026-10-01T14:00:00Z", "2026-10-01T14:05:00Z", mode="overlay_only")
    first["overlay_source_run_id"] = old["run_id"]
    second["overlay_source_run_id"] = first["run_id"]
    for overlay in (first, second):
        overlay["tickers"][0]["artifacts"].update(
            microstructure_snapshot_json="microstructure.json", microstructure_report_md="microstructure.md",
        )
    for payload in (old, first, second):
        publish(tmp_path, payload)
    new_full = manifest("new-full", "2026-10-01T12:00:00Z", "2026-10-01T15:00:00Z")
    assert not publish(tmp_path, new_full)
    assert runner._resolve_latest_overlay_source_manifest(tmp_path, tickers=["AAPL"], market="US") == new_full
