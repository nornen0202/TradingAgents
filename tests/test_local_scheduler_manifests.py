"""Original scheduler decisions survive memory-bounded manifest projection."""
import copy
import gc
import hashlib
import json
from datetime import datetime, timedelta, timezone
import tracemalloc
from types import SimpleNamespace

import pytest

from tradingagents import local_automation as local
from tradingagents.scheduled import runner


NOW = datetime(2026, 10, 22, 14, tzinfo=timezone.utc)
BOUNDARY = datetime(2026, 10, 22, 8, tzinfo=timezone.utc)


def target(profile="us", mode="full"):
    return SimpleNamespace(
        name=f"daily-codex-{profile}", inputs={"profile": profile},
        workflow_file="daily-codex-analysis.yml" if mode == "full" else "intraday-overlay-refresh.yml",
        window_start_kst=BOUNDARY, max_failed_attempts=2,
    )


def manifest(run_id="20261022T180000_z", profile="us", mode="full"):
    return {
        "run_id": run_id, "label": f"local-scheduler-{profile}-full", "status": "success",
        "started_at": "2026-10-22T09:00:00+00:00", "finished_at": "2026-10-22T10:00:00+00:00",
        "settings": {"market": profile.upper(), "market_scope": profile.upper(),
                     "run_mode": mode, "analysis_mode": "full", "large_unused_setting": "irrelevant"},
        "summary": {"successful_tickers": 2, "failed_tickers": 0, "configured_ticker_count": 2},
        "active_universe": {"coverage": {"complete": True, "holding_tickers": ["AAPL"]}},
        "tickers": [
            {"ticker": "AAPL", "status": "success", "artifacts": {"analysis_json": "tickers/AAPL/analysis.json"}},
            {"ticker": "MSFT", "status": "success", "artifacts": {"analysis_json": "tickers/MSFT/analysis.json"}},
        ],
        "execution": {"execution_asof": "2026-10-22T09:59:00+00:00", "refresh_checkpoint": "09:59",
                      "overlay_phase": {"selected_checkpoints": ["09:59"]}},
        "llm_usage": {"events": [{"unused_body": "not a scheduler input"}]},
        "research_recovery": {"parent_manifest_sha256": "original hash remains on disk"},
    }


def write(archive, data, *, directory=None, year="2026"):
    path = archive / "runs" / year / (directory or data["run_id"]) / "run.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def legacy_scan(archive):
    """Independent pre-change traversal, including eager parse errors."""
    root = archive / "runs"
    if not root.exists():
        return []
    values = []
    for year in sorted((p for p in root.iterdir() if p.is_dir()), reverse=True):
        for directory in sorted((p for p in year.iterdir() if p.is_dir()), reverse=True):
            path = directory / "run.json"
            if path.exists():
                values.append((json.loads(path.read_text(encoding="utf-8")), directory))
    return values


def outcome(callback):
    try:
        return "return", callback()
    except Exception as exc:
        return "raise", type(exc)


@pytest.mark.parametrize("profile", ["kr", "us"])
@pytest.mark.parametrize("mode", ["full", "overlay_only"])
@pytest.mark.parametrize("case", [
    "normal", "partial", "failed", "future", "invalid_date", "missing_date", "naive_date",
    "reversed_dates", "old", "wrong_market_scope", "manual", "coverage_missing_complete",
    "coverage_incomplete", "coverage_malformed", "ticker_duplicate", "ticker_missing_artifact",
    "ticker_malformed", "settings_malformed", "summary_malformed", "phase_malformed", "checkpoint_missing",
])
def test_projection_preserves_existing_selector_results(profile, mode, case):
    data = manifest(profile=profile, mode=mode)
    if case == "partial":
        data["status"] = "partial_failure"
        data["summary"].update(successful_tickers=1, failed_tickers=1)
        data["tickers"][1]["status"] = "failed"
    elif case == "failed":
        data["status"] = "failed"
    elif case in {"future", "invalid_date", "missing_date", "naive_date", "reversed_dates", "old"}:
        data["finished_at"] = {
            "future": "2026-10-22T15:00:00+00:00", "invalid_date": "not a date", "missing_date": None,
            "naive_date": "2026-10-22T10:00:00", "reversed_dates": "2026-10-22T07:00:00+00:00",
            "old": "2026-10-21T10:00:00+00:00",
        }[case]
        if case == "old":
            data["started_at"] = "2026-10-21T09:00:00+00:00"
    elif case == "wrong_market_scope":
        data["settings"]["market_scope"] = "US" if profile == "kr" else "KR"
    elif case == "manual":
        data["label"] = "manual-us"
    elif case.startswith("coverage_"):
        data["active_universe"]["coverage"] = {
            "coverage_missing_complete": {"required_holdings": ["AAPL"]},
            "coverage_incomplete": {"complete": False}, "coverage_malformed": ["invalid"],
        }[case]
    elif case == "ticker_duplicate":
        data["tickers"][0]["ticker"] = "005930.KS" if profile == "kr" else "AAPL"
        data["tickers"][1]["ticker"] = "005930" if profile == "kr" else "aapl"
    elif case == "ticker_missing_artifact":
        data["tickers"][1]["artifacts"] = {"irrelevant": "must not count as analysis"}
    elif case == "ticker_malformed":
        data["tickers"][1] = "invalid"
    elif case == "settings_malformed":
        data["settings"] = ["invalid"]
    elif case == "summary_malformed":
        data["summary"] = ["invalid"]
    elif case == "phase_malformed":
        data["execution"]["overlay_phase"] = ["invalid"]
    elif case == "checkpoint_missing":
        data["execution"]["overlay_phase"] = {"irrelevant": True}
    original = copy.deepcopy(data)
    projected = local._scheduler_manifest_view(data)
    item = target(profile, mode)
    assert outcome(lambda: local.completed_target(projected, item, now=NOW)) == outcome(
        lambda: local.completed_target(data, item, now=NOW))
    assert outcome(lambda: local.partial_target_source([projected], item, window_start=BOUNDARY, now=NOW)) == outcome(
        lambda: local.partial_target_source([data], item, window_start=BOUNDARY, now=NOW))
    assert data == original


@pytest.mark.parametrize("bad_finish", ["2026-10-22T15:00:00+00:00", None, "invalid", "2026-10-22T10:00:00"])
def test_partial_future_missing_or_malformed_clocks_still_skip_to_older(tmp_path, bad_finish):
    for name, finish in [("20261022T180000_z", bad_finish), ("20261022T180000_a", "2026-10-22T10:00:00+00:00")]:
        data = manifest(name)
        data.update(status="partial_failure", finished_at=finish)
        data["summary"].update(successful_tickers=1, failed_tickers=1)
        write(tmp_path, data)
    projected = [m for m, _ in runner._iter_run_manifests_desc(tmp_path, project=local._scheduler_manifest_view)]
    assert local.partial_target_source(projected, target(), window_start=BOUNDARY, now=NOW) == "20261022T180000_a"


def test_default_and_projected_traversal_preserve_order_and_original_bytes(tmp_path):
    for year, name in [("2025", "z"), ("2026", "a"), ("2026", "z")]:
        data = manifest(name)
        data["status"] = "partial_failure"
        data["summary"].update(successful_tickers=1, failed_tickers=1)
        write(tmp_path, data, year=year)
    (tmp_path / "runs" / "2026" / "not-completed").mkdir()
    original = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in tmp_path.rglob("*") if p.is_file()}
    legacy = legacy_scan(tmp_path)
    assert runner._iter_run_manifests_desc(tmp_path) == legacy
    projected = runner._iter_run_manifests_desc(tmp_path, project=local._scheduler_manifest_view)
    assert [p for _, p in projected] == [p for _, p in legacy]
    assert local.partial_target_source([m for m, _ in projected], target(), window_start=BOUNDARY, now=NOW) == "z"
    assert {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in tmp_path.rglob("*") if p.is_file()} == original


def test_no_negative_or_stale_cache_hides_new_completion(tmp_path):
    path = write(tmp_path, manifest())
    path.unlink()
    assert runner._iter_run_manifests_desc(tmp_path, project=local._scheduler_manifest_view) == []
    data = manifest()
    data["status"] = "partial_failure"
    write(tmp_path, data)
    first = runner._iter_run_manifests_desc(tmp_path, project=local._scheduler_manifest_view)
    assert first[0][0]["status"] == "partial_failure"
    data["status"] = "success"
    write(tmp_path, data)
    second = runner._iter_run_manifests_desc(tmp_path, project=local._scheduler_manifest_view)
    assert second[0][0]["status"] == "success"
    assert not list(tmp_path.glob(".*"))


def test_older_broken_json_fails_before_scheduler_actions(tmp_path, monkeypatch):
    write(tmp_path, manifest("z"))
    bad = write(tmp_path, manifest("a"))
    bad.write_text('{"unfinished":', encoding="utf-8")
    for scan in (legacy_scan, runner._iter_run_manifests_desc):
        with pytest.raises(json.JSONDecodeError):
            scan(tmp_path)
    monkeypatch.setattr(local, "script", lambda _: SimpleNamespace(due_targets=lambda *a, **k: [target()]))
    monkeypatch.setattr(local, "atomic_write_json", lambda *a, **k: pytest.fail("must not create an attempt"))
    monkeypatch.setattr(local.subprocess, "run", lambda *a, **k: pytest.fail("must not launch a worker"))
    with pytest.raises(json.JSONDecodeError):
        local.run_due(tmp_path, tmp_path / "state", now=NOW, research_only=True)


def test_large_unused_bodies_are_not_retained_across_manifests(tmp_path):
    payload_bytes = 1024 * 1024
    count = 20
    for index in range(count):
        data = manifest(f"{index:04d}")
        data["llm_usage"]["events"][0]["unused_body"] = "x" * payload_bytes
        write(tmp_path, data)
    del data
    gc.collect()
    tracemalloc.start()
    try:
        result = runner._iter_run_manifests_desc(tmp_path, project=local._scheduler_manifest_view)
        current, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert len(result) == count
    assert all(local.completed_target(m, target(), now=NOW) for m, _ in result)
    # A full list necessarily retains at least the 20 MiB string corpus. Allow
    # several parse/read temporaries, but never archive-sized retained bodies.
    assert peak < 6 * payload_bytes, (current, peak)
    assert current < payload_bytes, (current, peak)
    assert all("llm_usage" not in m and "research_recovery" not in m for m, _ in result)


@pytest.mark.parametrize("mode,receipt", [("full", True), ("overlay_only", True), ("overlay_only", False)])
@pytest.mark.parametrize("seconds_before_finish,expected", [(0, True), (0.000001, False), (-1, True)])
def test_completion_is_inclusive_at_aware_cutoff_and_rejects_future(mode, receipt, seconds_before_finish, expected):
    data = manifest(mode=mode)
    if not receipt:
        data.pop("execution")
    finish = datetime.fromisoformat(data["finished_at"])
    cutoff = finish - timedelta(seconds=seconds_before_finish)
    # Different offsets represent the same boundary, including legacy overlays
    # without an execution receipt. A future completion is intentionally no
    # longer considered completed, unlike the former unbounded selector.
    cutoff = cutoff.astimezone(timezone(timedelta(hours=9)))
    for candidate in (data, local._scheduler_manifest_view(data)):
        assert local.completed_target(candidate, target(mode=mode), now=cutoff) is expected


@pytest.mark.parametrize("bad_now", ["2026-10-22", "invalid", 123, datetime(2026, 10, 22, 14)])
def test_completion_rejects_invalid_or_naive_cutoff(bad_now):
    with pytest.raises(ValueError, match="Aware scheduler completion clock"):
        local.completed_target(manifest(), target(), now=bad_now)


def test_direct_completion_defaults_to_actual_aware_utc(monkeypatch):
    calls = []

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            calls.append(tz)
            return cls(2026, 10, 22, 14, tzinfo=timezone.utc).astimezone(tz)

    monkeypatch.setattr(local, "datetime", Clock)
    data = manifest()
    assert local.completed_target(data, target())
    data["finished_at"] = "2026-10-22T14:00:00.000001+00:00"
    assert not local.completed_target(data, target())
    assert calls == [timezone.utc, timezone.utc]


@pytest.mark.parametrize("profile", ["kr", "us"])
@pytest.mark.parametrize("mode,receipt", [("full", True), ("overlay_only", True), ("overlay_only", False)])
@pytest.mark.parametrize("past_complete", [False, True])
def test_future_manifest_cannot_change_past_scheduler_decision(
    tmp_path, monkeypatch, profile, mode, receipt, past_complete,
):
    from tradingagents import local_advisory_recovery
    from tradingagents.execution import refresh_runtime

    item = target(profile, mode)
    monkeypatch.setattr(local, "script", lambda _: SimpleNamespace(due_targets=lambda *a, **k: [item]))
    monkeypatch.setattr(local, "local_target_window_start", lambda *a, **k: BOUNDARY)
    monkeypatch.setattr(local, "full_research_session_hold", lambda *a, **k: None)
    monkeypatch.setattr(refresh_runtime, "refresh_due", lambda *a, **k: [])
    monkeypatch.setattr(local_advisory_recovery, "recover_due", lambda *a, **k: [])
    monkeypatch.setattr(local.subprocess, "run", lambda *a, **k: pytest.fail("read-only scheduler fixture"))
    monkeypatch.setattr(local, "atomic_write_json", lambda *a, **k: pytest.fail("no attempt or ledger writes"))
    archive, state = tmp_path / "archive", tmp_path / "state"
    if past_complete:
        write(archive, manifest("20261022T180000_past", profile, mode))
    before = local.run_due(archive, state, now=NOW, dry_run=True)
    future = manifest("20261022T235959_future", profile, mode)
    future.update(started_at=(NOW - timedelta(seconds=1)).isoformat(),
                  finished_at=(NOW + timedelta(seconds=1)).isoformat())
    if receipt:
        future["execution"]["execution_asof"] = NOW.isoformat()
    else:
        future.pop("execution")
    write(archive, future)
    after = local.run_due(archive, state, now=NOW, dry_run=True)
    assert before == after == [{"target": item.name, "status": "RESEARCH_COMPLETE" if past_complete else "DUE"}]
    assert not state.exists()
