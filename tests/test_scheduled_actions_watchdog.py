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
    def __init__(self, *, runs=None, jobs=None, diagnostics=None):
        self.runs = runs or []
        self.jobs = jobs or {}
        self.diagnostics = diagnostics
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

    def failure_diagnostic_signature(self, run_id):
        if self.diagnostics is None:
            return "a" * 64
        return self.diagnostics.get(run_id, "")


def _kst(value: str):
    return datetime.fromisoformat(value).replace(tzinfo=watchdog.KST)


def test_youtube_watchdog_is_due_after_backup_window():
    targets = watchdog.due_targets(_kst("2026-06-02T06:57:00"))

    youtube = [target for target in targets if target.name == "youtube-daily"]
    assert len(youtube) == 1
    assert youtube[0].workflow_file == "daily-youtube-reports.yml"
    assert youtube[0].job_names == ("build_youtube_pages", "deploy", "youtube_coverage")
    assert youtube[0].work_job_names == ("build_youtube_pages",)
    assert youtube[0].inputs["recovery_source"] == "cloud_watchdog"
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
    assert codex_us[0].inputs == {"profile": "us", "recovery_source": "cloud_watchdog"}
    assert codex_us[0].job_names == ("analyze_us", "build_pages", "deploy")
    assert codex_us[0].work_job_names == ("analyze_us",)
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

    assert (
        "daily-codex-analysis.yml",
        {"profile": "kr", "recovery_source": "cloud_watchdog"},
    ) in client.dispatches
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

    overlay_kr = [target for target in targets if target.name.startswith("intraday-overlay-kr-")]
    assert len(overlay_kr) == 1
    assert overlay_kr[0].inputs == {
        "profile": "kr",
        "run_mode": "overlay_only",
        "recovery_source": "cloud_watchdog",
    }
    assert overlay_kr[0].job_names == (
        "overlay_gate",
        "overlay_refresh_kr",
        "publish_overlay_site",
        "deploy_overlay",
    )
    assert overlay_kr[0].work_job_names == ("overlay_refresh_kr",)
    assert overlay_kr[0].dependencies[0].name == "daily-codex-kr"
    assert overlay_kr[0].dependencies[0].job_names == ("analyze_kr", "build_pages")
    assert overlay_kr[0].window_start_kst == _kst("2026-06-01T10:05:00")
    assert overlay_kr[0].dependencies[0].window_start_kst == _kst("2026-05-31T10:07:00")


def test_us_intraday_overlay_watchdog_uses_previous_daily_window_after_midnight():
    targets = watchdog.due_targets(_kst("2026-06-02T00:19:00"))

    overlay_us = [target for target in targets if target.name.startswith("intraday-overlay-us-")]
    assert len(overlay_us) == 1
    assert overlay_us[0].inputs == {
        "profile": "us",
        "run_mode": "overlay_only",
        "recovery_source": "cloud_watchdog",
    }
    assert overlay_us[0].job_names == (
        "overlay_gate",
        "overlay_refresh_us",
        "publish_overlay_site",
        "deploy_overlay",
    )
    assert overlay_us[0].dependencies[0].name == "daily-codex-us"
    assert overlay_us[0].dependencies[0].job_names == ("analyze_us", "build_pages")
    assert overlay_us[0].window_start_kst == _kst("2026-06-01T22:40:00")
    assert overlay_us[0].dependencies[0].window_start_kst == _kst("2026-06-01T00:19:00")


def test_youtube_watchdog_stays_due_during_late_recovery_window():
    targets = watchdog.due_targets(_kst("2026-06-02T07:07:00"))

    assert [target for target in targets if target.name == "youtube-daily"]


def test_youtube_watchdog_yields_during_us_intraday_overlay_window():
    targets = watchdog.due_targets(_kst("2026-06-02T00:19:00"))

    assert not [target for target in targets if target.name == "youtube-daily"]
    assert [target for target in targets if target.name.startswith("intraday-overlay-us-")]


def test_youtube_watchdog_recovers_after_us_intraday_overlay_window():
    targets = watchdog.due_targets(_kst("2026-06-02T07:08:00"))

    youtube = [target for target in targets if target.name == "youtube-daily"]
    assert len(youtube) == 1
    assert youtube[0].window_start_kst == _kst("2026-06-02T05:00:00")


def test_youtube_watchdog_yields_after_late_recovery_window():
    targets = watchdog.due_targets(_kst("2026-06-02T15:07:00"))

    assert not [target for target in targets if target.name == "youtube-daily"]


def test_watchdog_accepts_completed_success_with_explicit_no_work_target():
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

    assert covered
    assert "explicit no-work" in reason


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


def test_watchdog_requires_publish_and_deploy_after_overlay_success():
    target = watchdog.WatchdogTarget(
        name="intraday-overlay-kr-1005",
        workflow_file="intraday-overlay-refresh.yml",
        job_names=(
            "overlay_gate",
            "overlay_refresh_kr",
            "publish_overlay_site",
            "deploy_overlay",
        ),
        work_job_names=("overlay_refresh_kr",),
        window_start_kst=_kst("2026-06-01T10:05:00"),
        inputs={"profile": "kr", "run_mode": "overlay_only"},
    )
    client = FakeClient(
        runs=[{"id": 655, "status": "completed", "conclusion": "failure"}],
        jobs={
            655: [
                {"name": "overlay_gate", "status": "completed", "conclusion": "success"},
                {"name": "overlay_refresh_kr", "status": "completed", "conclusion": "success"},
                {"name": "publish_overlay_site", "status": "completed", "conclusion": "failure"},
                {"name": "deploy_overlay", "status": "completed", "conclusion": "skipped"},
            ]
        },
    )

    covered, reason = watchdog.target_is_covered(client=client, target=target)

    assert not covered
    assert "No successful target jobs" in reason


def test_watchdog_suppresses_repeated_failures_after_retry_budget():
    target = watchdog.WatchdogTarget(
        name="youtube-daily",
        workflow_file="daily-youtube-reports.yml",
        job_names=("build_youtube_pages",),
        window_start_kst=_kst("2026-06-01T05:00:00"),
        inputs={"lookback_hours": "24", "publish": "true"},
        max_failed_attempts=2,
    )
    client = FakeClient(
        runs=[
            {"id": 702, "status": "completed", "conclusion": "failure"},
            {"id": 701, "status": "completed", "conclusion": "failure"},
        ],
        jobs={
            702: [{"name": "build_youtube_pages", "status": "completed", "conclusion": "failure"}],
            701: [{"name": "build_youtube_pages", "status": "completed", "conclusion": "failure"}],
        },
    )

    covered, reason = watchdog.target_is_covered(client=client, target=target)

    assert covered
    assert "Retry budget exhausted" in reason


def test_watchdog_retry_budget_only_counts_identical_target_job_failures():
    target = watchdog.WatchdogTarget(
        name="intraday-overlay-us",
        workflow_file="intraday-overlay-refresh.yml",
        job_names=("overlay_refresh_us",),
        window_start_kst=_kst("2026-06-01T22:40:00"),
        inputs={"profile": "us"},
        max_failed_attempts=2,
    )
    client = FakeClient(
        runs=[
            {"id": 712, "status": "completed", "head_sha": "b" * 40},
            {"id": 711, "status": "completed", "head_sha": "a" * 40},
        ],
        jobs={
            712: [{"name": "overlay_refresh_us", "status": "completed", "conclusion": "failure"}],
            711: [{"name": "overlay_refresh_us", "status": "completed", "conclusion": "failure"}],
        },
    )

    covered, reason = watchdog.target_is_covered(client=client, target=target)

    assert not covered
    assert "No successful target jobs" in reason


def test_watchdog_uses_failure_cooldown_window_across_overlay_checkpoints():
    target = watchdog.WatchdogTarget(
        name="intraday-overlay-kr-1200",
        workflow_file="intraday-overlay-refresh.yml",
        job_names=("overlay_gate", "overlay_refresh_kr", "publish_overlay_site", "deploy_overlay"),
        work_job_names=("overlay_refresh_kr",),
        window_start_kst=_kst("2026-06-01T12:00:00"),
        inputs={"profile": "kr"},
        max_failed_attempts=2,
        failure_window_start_kst=_kst("2026-06-01T09:30:00"),
    )
    client = FakeClient(
        runs=[
            {
                "id": 722,
                "status": "completed",
                "head_sha": "a" * 40,
                "created_at": "2026-06-01T02:00:00Z",
            },
            {
                "id": 721,
                "status": "completed",
                "head_sha": "a" * 40,
                "created_at": "2026-06-01T01:00:00Z",
            },
        ],
        jobs={
            722: [{"name": "overlay_refresh_kr", "status": "completed", "conclusion": "failure"}],
            721: [{"name": "overlay_refresh_kr", "status": "completed", "conclusion": "failure"}],
        },
    )

    covered, reason = watchdog.target_is_covered(client=client, target=target)

    assert covered
    assert "identical target-job failure" in reason


def test_watchdog_success_resets_older_identical_failure_budget():
    target = watchdog.WatchdogTarget(
        name="intraday-overlay-kr-1200",
        workflow_file="intraday-overlay-refresh.yml",
        job_names=("overlay_refresh_kr",),
        window_start_kst=_kst("2026-06-01T12:00:00"),
        inputs={"profile": "kr"},
        max_failed_attempts=2,
        failure_window_start_kst=_kst("2026-06-01T09:30:00"),
    )
    client = FakeClient(
        runs=[
            {"id": 744, "status": "completed", "head_sha": "a" * 40, "created_at": "2026-06-01T03:01:00Z"},
            {"id": 743, "status": "completed", "head_sha": "a" * 40, "created_at": "2026-06-01T02:00:00Z"},
            {"id": 742, "status": "completed", "head_sha": "a" * 40, "created_at": "2026-06-01T01:00:00Z"},
            {"id": 741, "status": "completed", "head_sha": "a" * 40, "created_at": "2026-06-01T00:45:00Z"},
        ],
        jobs={
            744: [{"name": "overlay_refresh_kr", "status": "completed", "conclusion": "failure"}],
            743: [{"name": "overlay_refresh_kr", "status": "completed", "conclusion": "success"}],
            742: [{"name": "overlay_refresh_kr", "status": "completed", "conclusion": "failure"}],
            741: [{"name": "overlay_refresh_kr", "status": "completed", "conclusion": "failure"}],
        },
    )

    covered, reason = watchdog.target_is_covered(client=client, target=target)

    assert not covered
    assert "No successful target jobs" in reason


def test_watchdog_skipped_target_jobs_do_not_consume_retry_budget():
    target = watchdog.WatchdogTarget(
        name="intraday-overlay-us",
        workflow_file="intraday-overlay-refresh.yml",
        job_names=("overlay_refresh_us",),
        window_start_kst=_kst("2026-06-01T22:40:00"),
        inputs={"profile": "us"},
        max_failed_attempts=2,
    )
    client = FakeClient(
        runs=[
            {"id": 732, "status": "completed", "conclusion": "success"},
            {"id": 731, "status": "completed", "conclusion": "success"},
        ],
        jobs={
            732: [{"name": "overlay_refresh_us", "status": "completed", "conclusion": "skipped"}],
            731: [{"name": "overlay_refresh_us", "status": "completed", "conclusion": "skipped"}],
        },
    )

    covered, reason = watchdog.target_is_covered(client=client, target=target)

    assert covered
    assert "explicit no-work" in reason


def test_watchdog_repeated_log_unavailable_failure_has_bounded_budget():
    target = watchdog.WatchdogTarget(
        name="intraday-overlay-us",
        workflow_file="intraday-overlay-refresh.yml",
        job_names=("overlay_refresh_us",),
        window_start_kst=_kst("2026-06-01T22:40:00"),
        inputs={"profile": "us"},
        max_failed_attempts=2,
    )
    client = FakeClient(
        runs=[
            {"id": 752, "status": "completed", "conclusion": "failure", "head_sha": "a" * 40},
            {"id": 751, "status": "completed", "conclusion": "failure", "head_sha": "a" * 40},
        ],
        jobs={
            752: [{"name": "overlay_refresh_us", "status": "completed", "conclusion": "failure"}],
            751: [{"name": "overlay_refresh_us", "status": "completed", "conclusion": "failure"}],
        },
        diagnostics={},
    )

    covered, reason = watchdog.target_is_covered(client=client, target=target)

    assert covered
    assert "Retry budget exhausted" in reason


def test_watchdog_repeated_missing_publish_and_deploy_consumes_budget():
    required = ("overlay_gate", "overlay_refresh_kr", "publish_overlay_site", "deploy_overlay")
    target = watchdog.WatchdogTarget(
        name="intraday-overlay-kr",
        workflow_file="intraday-overlay-refresh.yml",
        job_names=required,
        work_job_names=("overlay_refresh_kr",),
        window_start_kst=_kst("2026-06-01T10:05:00"),
        inputs={"profile": "kr", "run_mode": "overlay_only"},
        max_failed_attempts=2,
    )
    incomplete_jobs = [
        {"name": "overlay_gate", "status": "completed", "conclusion": "success"},
        {"name": "overlay_refresh_kr", "status": "completed", "conclusion": "success"},
        {"name": "publish_overlay_site", "status": "completed", "conclusion": "skipped"},
        {"name": "deploy_overlay", "status": "completed", "conclusion": "skipped"},
    ]
    client = FakeClient(
        runs=[
            {"id": 772, "status": "completed", "conclusion": "success", "head_sha": "a" * 40},
            {"id": 771, "status": "completed", "conclusion": "success", "head_sha": "a" * 40},
        ],
        jobs={772: incomplete_jobs, 771: incomplete_jobs},
    )

    covered, reason = watchdog.target_is_covered(client=client, target=target)

    assert covered
    assert "Retry budget exhausted" in reason


def test_watchdog_dispatches_when_due_target_is_uncovered():
    target_time = _kst("2026-06-02T06:57:00")
    client = FakeClient(runs=[])

    messages = watchdog.run_watchdog(client=client, now_kst=target_time)

    assert (
        "daily-youtube-reports.yml",
        {
            "lookback_hours": "24",
            "publish": "true",
            "recovery_source": "cloud_watchdog",
        },
    ) in client.dispatches
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
        jobs={
            701: [{"name": "analyze_kr", "status": "in_progress", "conclusion": ""}],
            801: [
                {"name": "build_youtube_pages", "status": "completed", "conclusion": "success"},
                {"name": "deploy", "status": "completed", "conclusion": "success"},
            ],
        },
    )

    messages = watchdog.run_watchdog(client=client, now_kst=_kst("2026-06-01T10:07:00"))

    assert (
        "daily-codex-analysis.yml",
        {"profile": "kr", "recovery_source": "cloud_watchdog"},
    ) not in client.dispatches
    assert (
        "intraday-overlay-refresh.yml",
        {
            "profile": "kr",
            "run_mode": "overlay_only",
            "recovery_source": "cloud_watchdog",
        },
    ) not in client.dispatches
    assert any("intraday-overlay-kr-1005: waiting" in message for message in messages)
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

    assert (
        "intraday-overlay-refresh.yml",
        {
            "profile": "kr",
            "run_mode": "overlay_only",
            "recovery_source": "cloud_watchdog",
        },
    ) in client.dispatches
    assert any("intraday-overlay-kr-1005: dispatched" in message for message in messages)


def test_watchdog_reuses_fixed_checkpoint_window_between_poll_cycles():
    first = [
        target
        for target in watchdog.due_targets(_kst("2026-06-01T10:07:00"))
        if target.name.startswith("intraday-overlay-kr-")
    ][0]
    later = [
        target
        for target in watchdog.due_targets(_kst("2026-06-01T11:37:00"))
        if target.name.startswith("intraday-overlay-kr-")
    ][0]

    assert first.name == later.name == "intraday-overlay-kr-1005"
    assert first.window_start_kst == later.window_start_kst == _kst("2026-06-01T10:05:00")
