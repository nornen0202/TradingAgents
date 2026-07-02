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
        if isinstance(self.runs, dict):
            return self.runs.get(workflow_file, [])
        return self.runs

    def list_jobs(self, run_id):
        return self.jobs.get(run_id, [])

    def dispatch(self, workflow_file, inputs):
        self.dispatches.append((workflow_file, inputs))


def _kst(value: str):
    return datetime.fromisoformat(value).replace(tzinfo=watchdog.KST)


def test_youtube_watchdog_is_due_after_backup_window():
    targets = watchdog.due_targets(_kst("2026-06-02T06:57:00"))

    youtube = [target for target in targets if target.name == "youtube-daily"]
    assert len(youtube) == 1
    assert youtube[0].workflow_file == "daily-youtube-reports.yml"
    assert youtube[0].job_names == ("build_youtube_pages",)
    assert youtube[0].window_start_kst == _kst("2026-06-02T05:00:00")
    assert youtube[0].blockers[0].name == "daily-codex-us-pages"
    assert youtube[0].blockers[0].job_names == ("analyze_us", "build_pages")
    assert youtube[0].blockers[0].window_start_kst == _kst("2026-06-01T17:45:00")
    assert youtube[0].blockers[1].name == "intraday-overlay-us-publish"
    assert youtube[0].blockers[1].window_start_kst == _kst("2026-06-01T22:30:00")


def test_daily_codex_us_watchdog_is_due_on_weekday_afternoon():
    targets = watchdog.due_targets(_kst("2026-06-01T18:07:00"))

    codex_us = [target for target in targets if target.name == "daily-codex-us"]
    assert len(codex_us) == 1
    assert codex_us[0].inputs == {"profile": "us"}
    assert codex_us[0].job_names == ("analyze_us", "build_pages")
    assert codex_us[0].window_start_kst == _kst("2026-06-01T17:45:00")
    assert codex_us[0].blockers[0].name == "intraday-overlay-kr-publish"


def test_daily_codex_us_watchdog_stays_due_during_late_recovery_window():
    targets = watchdog.due_targets(_kst("2026-06-01T21:44:00"))

    assert [target for target in targets if target.name == "daily-codex-us"]


def test_daily_codex_us_watchdog_yields_after_late_recovery_window():
    targets = watchdog.due_targets(_kst("2026-06-01T23:17:00"))

    assert not [target for target in targets if target.name == "daily-codex-us"]


def test_daily_codex_kr_watchdog_stays_due_before_ten_kst_target():
    targets = watchdog.due_targets(_kst("2026-06-01T09:37:00"))

    assert [target for target in targets if target.name == "daily-codex-kr"]


def test_daily_codex_kr_watchdog_yields_after_recovery_window():
    targets = watchdog.due_targets(_kst("2026-06-01T10:17:00"))

    assert not [target for target in targets if target.name == "daily-codex-kr"]


def test_daily_codex_kr_watchdog_does_not_wait_for_youtube_publish():
    client = FakeClient(
        runs={
            "daily-youtube-reports.yml": [{"id": 301, "status": "in_progress", "conclusion": ""}],
            "intraday-overlay-refresh.yml": [],
            "daily-codex-analysis.yml": [],
        },
        jobs={301: [{"name": "build_youtube_pages", "status": "in_progress", "conclusion": ""}]},
    )

    messages = watchdog.run_watchdog(client=client, now_kst=_kst("2026-06-01T07:58:00"))

    assert ("daily-codex-analysis.yml", {"profile": "kr"}) in client.dispatches
    assert any("daily-codex-kr: dispatched" in message for message in messages)
    assert not any("daily-codex-kr: waiting" in message for message in messages)


def test_daily_codex_us_watchdog_waits_for_kr_overlay_publish():
    client = FakeClient(
        runs={
            "intraday-overlay-refresh.yml": [{"id": 302, "status": "in_progress", "conclusion": ""}],
            "daily-codex-analysis.yml": [],
        },
        jobs={302: [{"name": "publish_overlay_site", "status": "in_progress", "conclusion": ""}]},
    )

    messages = watchdog.run_watchdog(client=client, now_kst=_kst("2026-06-01T18:07:00"))

    assert not client.dispatches
    assert any("daily-codex-us: waiting" in message for message in messages)
    assert any("intraday-overlay-kr-publish" in message for message in messages)


def test_kr_intraday_overlay_watchdog_depends_on_daily_codex_completion():
    targets = watchdog.due_targets(_kst("2026-06-01T10:07:00"))

    overlay_kr = [target for target in targets if target.name == "intraday-overlay-kr"]
    assert len(overlay_kr) == 1
    assert overlay_kr[0].inputs == {"profile": "kr", "run_mode": "overlay_only"}
    assert overlay_kr[0].dependencies[0].name == "daily-codex-kr"
    assert overlay_kr[0].dependencies[0].job_names == ("analyze_kr", "build_pages")
    assert overlay_kr[0].dependencies[0].window_start_kst == _kst("2026-06-01T04:30:00")


def test_us_intraday_overlay_watchdog_uses_previous_daily_window_after_midnight():
    targets = watchdog.due_targets(_kst("2026-06-02T00:19:00"))

    overlay_us = [target for target in targets if target.name == "intraday-overlay-us"]
    assert len(overlay_us) == 1
    assert overlay_us[0].inputs == {"profile": "us", "run_mode": "overlay_only"}
    assert overlay_us[0].dependencies[0].name == "daily-codex-us"
    assert overlay_us[0].dependencies[0].job_names == ("analyze_us", "build_pages")
    assert overlay_us[0].dependencies[0].window_start_kst == _kst("2026-06-01T17:45:00")


def test_youtube_watchdog_stays_due_during_late_recovery_window():
    targets = watchdog.due_targets(_kst("2026-06-02T07:07:00"))

    assert [target for target in targets if target.name == "youtube-daily"]


def test_youtube_watchdog_yields_during_us_intraday_overlay_window():
    targets = watchdog.due_targets(_kst("2026-06-02T00:19:00"))

    assert not [target for target in targets if target.name == "youtube-daily"]
    assert [target for target in targets if target.name == "intraday-overlay-us"]


def test_youtube_watchdog_recovers_after_us_intraday_overlay_window():
    targets = watchdog.due_targets(_kst("2026-06-02T07:08:00"))

    youtube = [target for target in targets if target.name == "youtube-daily"]
    assert len(youtube) == 1
    assert youtube[0].window_start_kst == _kst("2026-06-02T05:00:00")


def test_youtube_watchdog_yields_after_late_recovery_window():
    targets = watchdog.due_targets(_kst("2026-06-02T15:07:00"))

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
    assert "active target job(s): analyze_us" in reason


def test_watchdog_dispatches_when_due_target_is_uncovered():
    target_time = _kst("2026-06-02T06:57:00")
    client = FakeClient(runs=[])

    messages = watchdog.run_watchdog(client=client, now_kst=target_time)

    assert ("daily-youtube-reports.yml", {"lookback_hours": "24", "publish": "true"}) in client.dispatches
    assert any("youtube-daily: dispatched" in message for message in messages)


def test_watchdog_waits_to_dispatch_youtube_until_daily_pages_build_finishes():
    client = FakeClient(
        runs={
            "daily-codex-analysis.yml": [{"id": 901, "status": "in_progress", "conclusion": ""}],
            "daily-youtube-reports.yml": [],
        },
        jobs={901: [{"name": "build_pages", "status": "queued", "conclusion": ""}]},
    )

    messages = watchdog.run_watchdog(client=client, now_kst=_kst("2026-06-02T07:07:00"))

    assert not client.dispatches
    assert any("youtube-daily: waiting" in message for message in messages)
    assert any("daily-codex-us-pages run 901 has build_pages: queued" in message for message in messages)


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
    assert "covers target job set: analyze_us" in reason


def test_watchdog_retries_when_analysis_succeeded_but_pages_failed():
    target = watchdog.WatchdogTarget(
        name="daily-codex-us",
        workflow_file="daily-codex-analysis.yml",
        job_names=("analyze_us", "build_pages"),
        window_start_kst=_kst("2026-06-01T16:00:00"),
        inputs={"profile": "us"},
    )
    client = FakeClient(
        runs=[{"id": 457, "status": "completed", "conclusion": "success"}],
        jobs={
            457: [
                {"name": "analyze_us", "status": "completed", "conclusion": "success"},
                {"name": "build_pages", "status": "completed", "conclusion": "failure"},
            ]
        },
    )

    covered, reason = watchdog.target_is_covered(client=client, target=target)

    assert not covered
    assert "No successful target jobs" in reason


def test_watchdog_waits_to_dispatch_overlay_until_daily_dependency_completes():
    client = FakeClient(
        runs={
            "daily-codex-analysis.yml": [{"id": 701, "status": "in_progress", "conclusion": ""}],
            "intraday-overlay-refresh.yml": [],
            "daily-youtube-reports.yml": [{"id": 801, "status": "completed", "conclusion": "success"}],
        },
        jobs={801: [{"name": "build_youtube_pages", "status": "completed", "conclusion": "success"}]},
    )

    messages = watchdog.run_watchdog(client=client, now_kst=_kst("2026-06-01T10:07:00"))

    assert ("daily-codex-analysis.yml", {"profile": "kr"}) in client.dispatches
    assert ("intraday-overlay-refresh.yml", {"profile": "kr", "run_mode": "overlay_only"}) not in client.dispatches
    assert any("intraday-overlay-kr: waiting" in message for message in messages)
    assert any("daily-codex-kr still active" in message for message in messages)


def test_watchdog_dispatches_overlay_after_daily_dependency_completed():
    client = FakeClient(
        runs={
            "daily-codex-analysis.yml": [{"id": 702, "status": "completed", "conclusion": "success"}],
            "intraday-overlay-refresh.yml": [],
            "daily-youtube-reports.yml": [{"id": 802, "status": "completed", "conclusion": "success"}],
        },
        jobs={
            702: [
                {"name": "analyze_kr", "status": "completed", "conclusion": "success"},
                {"name": "build_pages", "status": "completed", "conclusion": "success"},
            ],
            802: [{"name": "build_youtube_pages", "status": "completed", "conclusion": "success"}],
        },
    )

    messages = watchdog.run_watchdog(client=client, now_kst=_kst("2026-06-01T10:07:00"))

    assert ("intraday-overlay-refresh.yml", {"profile": "kr", "run_mode": "overlay_only"}) in client.dispatches
    assert any("intraday-overlay-kr: dispatched" in message for message in messages)
