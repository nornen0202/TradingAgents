from __future__ import annotations

import importlib.util
import sys
from datetime import datetime
from pathlib import Path


MODULE_PATH = Path(".github/scripts/scheduled_actions_watchdog.py")
SPEC = importlib.util.spec_from_file_location("scheduled_actions_watchdog", MODULE_PATH)
watchdog = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = watchdog
SPEC.loader.exec_module(watchdog)


class FakeClient:
    def __init__(self, *, runs=None, jobs=None):
        self.runs = runs or []
        self.jobs = jobs or {}
        self.dispatches = []

    def list_runs(self, workflow_file, *, created_since_utc):
        self.last_workflow_file = workflow_file
        self.last_created_since_utc = created_since_utc
        return self.runs

    def list_jobs(self, run_id):
        return self.jobs.get(run_id, [])

    def dispatch(self, workflow_file, inputs):
        self.dispatches.append((workflow_file, inputs))


def _kst(value: str):
    return datetime.fromisoformat(value).replace(tzinfo=watchdog.KST)


def test_youtube_watchdog_is_due_after_backup_window():
    targets = watchdog.due_targets(_kst("2026-06-01T21:57:00"))

    youtube = [target for target in targets if target.name == "youtube-daily"]
    assert len(youtube) == 1
    assert youtube[0].workflow_file == "daily-youtube-reports.yml"
    assert youtube[0].job_names == ("build_youtube_pages",)
    assert youtube[0].window_start_kst == _kst("2026-06-01T19:00:00")


def test_daily_codex_us_watchdog_is_due_on_weekday_afternoon():
    targets = watchdog.due_targets(_kst("2026-06-01T18:07:00"))

    codex_us = [target for target in targets if target.name == "daily-codex-us"]
    assert len(codex_us) == 1
    assert codex_us[0].inputs == {"profile": "us"}
    assert codex_us[0].job_names == ("analyze_us",)
    assert codex_us[0].window_start_kst == _kst("2026-06-01T16:00:00")


def test_daily_codex_us_watchdog_yields_before_youtube_window():
    targets = watchdog.due_targets(_kst("2026-06-01T20:07:00"))

    assert not [target for target in targets if target.name == "daily-codex-us"]


def test_daily_codex_kr_watchdog_yields_before_intraday_overlay_window():
    targets = watchdog.due_targets(_kst("2026-06-01T09:25:00"))

    assert not [target for target in targets if target.name == "daily-codex-kr"]


def test_youtube_watchdog_stays_due_during_late_recovery_window():
    targets = watchdog.due_targets(_kst("2026-06-01T23:07:00"))

    assert [target for target in targets if target.name == "youtube-daily"]


def test_youtube_watchdog_covers_delayed_after_midnight_run():
    targets = watchdog.due_targets(_kst("2026-06-02T00:19:00"))

    youtube = [target for target in targets if target.name == "youtube-daily"]
    assert len(youtube) == 1
    assert youtube[0].window_start_kst == _kst("2026-06-01T19:00:00")


def test_youtube_watchdog_yields_after_late_recovery_window():
    targets = watchdog.due_targets(_kst("2026-06-02T04:07:00"))

    assert not [target for target in targets if target.name == "youtube-daily"]


def test_watchdog_ignores_gate_only_success_when_target_job_skipped():
    target = watchdog.WatchdogTarget(
        name="youtube-daily",
        workflow_file="daily-youtube-reports.yml",
        job_names=("build_youtube_pages",),
        window_start_kst=_kst("2026-06-01T19:00:00"),
        inputs={"lookback_hours": "24", "publish": "true"},
    )
    client = FakeClient(
        runs=[{"id": 123, "status": "completed", "conclusion": "success"}],
        jobs={123: [{"name": "build_youtube_pages", "status": "completed", "conclusion": "skipped"}]},
    )

    covered, reason = watchdog.target_is_covered(client=client, target=target)

    assert not covered
    assert "No successful target jobs" in reason


def test_watchdog_ignores_active_run_without_target_job():
    target = watchdog.WatchdogTarget(
        name="daily-codex-us",
        workflow_file="daily-codex-analysis.yml",
        job_names=("analyze_us",),
        window_start_kst=_kst("2026-06-01T16:00:00"),
        inputs={"profile": "us"},
    )
    client = FakeClient(
        runs=[{"id": 321, "status": "in_progress", "conclusion": ""}],
        jobs={321: [{"name": "analyze_kr", "status": "in_progress", "conclusion": ""}]},
    )

    covered, reason = watchdog.target_is_covered(client=client, target=target)

    assert not covered
    assert "No successful target jobs" in reason


def test_watchdog_treats_active_target_job_as_covered():
    target = watchdog.WatchdogTarget(
        name="daily-codex-us",
        workflow_file="daily-codex-analysis.yml",
        job_names=("analyze_us",),
        window_start_kst=_kst("2026-06-01T16:00:00"),
        inputs={"profile": "us"},
    )
    client = FakeClient(
        runs=[{"id": 654, "status": "in_progress", "conclusion": ""}],
        jobs={654: [{"name": "analyze_us", "status": "in_progress", "conclusion": ""}]},
    )

    covered, reason = watchdog.target_is_covered(client=client, target=target)

    assert covered
    assert "covers analyze_us" in reason


def test_watchdog_dispatches_when_due_target_is_uncovered():
    target_time = _kst("2026-06-01T21:57:00")
    client = FakeClient(runs=[])

    messages = watchdog.run_watchdog(client=client, now_kst=target_time)

    assert ("daily-youtube-reports.yml", {"lookback_hours": "24", "publish": "true"}) in client.dispatches
    assert any("youtube-daily: dispatched" in message for message in messages)


def test_watchdog_does_not_dispatch_when_target_job_succeeded():
    target = watchdog.WatchdogTarget(
        name="daily-codex-us",
        workflow_file="daily-codex-analysis.yml",
        job_names=("analyze_us",),
        window_start_kst=_kst("2026-06-01T16:00:00"),
        inputs={"profile": "us"},
    )
    client = FakeClient(
        runs=[{"id": 456, "status": "completed", "conclusion": "success"}],
        jobs={456: [{"name": "analyze_us", "status": "completed", "conclusion": "success"}]},
    )

    covered, reason = watchdog.target_is_covered(client=client, target=target)

    assert covered
    assert "covers analyze_us" in reason
