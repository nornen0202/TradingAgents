from __future__ import annotations

import importlib.util
import sys
from datetime import datetime
from pathlib import Path


MODULE_PATH = Path(".github/scripts/scheduled_workflow_gate.py")
SPEC = importlib.util.spec_from_file_location("scheduled_workflow_gate", MODULE_PATH)
gate = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = gate
SPEC.loader.exec_module(gate)


class FakeClient:
    def __init__(self, *, runs=None, jobs=None):
        self.runs = runs or []
        self.jobs = jobs or {}

    def list_runs(self, workflow_file, *, created_since_utc):
        self.last_workflow_file = workflow_file
        self.last_created_since_utc = created_since_utc
        return self.runs

    def list_jobs(self, run_id):
        return self.jobs.get(run_id, [])


def _kst(value: str):
    return datetime.fromisoformat(value).replace(tzinfo=gate.KST)


def _codex_targets():
    return gate.load_schedule_targets(
        """
        {
          "10 7 * * 1-5": {"profile": "us", "window_start": "16:00", "target_jobs": ["analyze_us"]},
          "10 21 * * 0-4": {"profile": "kr", "window_start": "06:00", "target_jobs": ["analyze_kr"]}
        }
        """
    )


def _youtube_targets():
    return gate.load_schedule_targets(
        """
        {
          "17 11 * * *": {"profile": "youtube", "window_start": "19:00", "target_jobs": ["build_youtube_pages"]}
        }
        """
    )


def test_scheduled_codex_skips_when_watchdog_dispatch_target_job_is_running():
    client = FakeClient(
        runs=[{"id": 111, "event": "workflow_dispatch", "status": "in_progress", "conclusion": ""}],
        jobs={111: [{"name": "analyze_us", "status": "in_progress", "conclusion": ""}]},
    )

    profile, should_run, reason = gate.decide_schedule_gate(
        event_name="schedule",
        schedule="10 7 * * 1-5",
        requested_profile="",
        manual_default_profile="all",
        workflow_file="daily-codex-analysis.yml",
        current_run_id=222,
        client=client,
        targets=_codex_targets(),
        now_kst=_kst("2026-06-03T16:40:00"),
    )

    assert profile == "us"
    assert should_run is False
    assert "workflow_dispatch run 111 covers analyze_us" in reason


def test_scheduled_codex_does_not_skip_for_other_profile_target_job():
    client = FakeClient(
        runs=[{"id": 111, "event": "workflow_dispatch", "status": "in_progress", "conclusion": ""}],
        jobs={111: [{"name": "analyze_kr", "status": "in_progress", "conclusion": ""}]},
    )

    profile, should_run, reason = gate.decide_schedule_gate(
        event_name="schedule",
        schedule="10 7 * * 1-5",
        requested_profile="",
        manual_default_profile="all",
        workflow_file="daily-codex-analysis.yml",
        current_run_id=222,
        client=client,
        targets=_codex_targets(),
        now_kst=_kst("2026-06-03T16:40:00"),
    )

    assert profile == "us"
    assert should_run is True
    assert "running now" in reason


def test_scheduled_youtube_skips_when_prior_manual_pages_job_succeeded():
    client = FakeClient(
        runs=[{"id": 333, "event": "workflow_dispatch", "status": "completed", "conclusion": "success"}],
        jobs={333: [{"name": "build_youtube_pages", "status": "completed", "conclusion": "success"}]},
    )

    profile, should_run, reason = gate.decide_schedule_gate(
        event_name="schedule",
        schedule="17 11 * * *",
        requested_profile="",
        manual_default_profile="",
        workflow_file="daily-youtube-reports.yml",
        current_run_id=444,
        client=client,
        targets=_youtube_targets(),
        now_kst=_kst("2026-06-03T20:17:00"),
    )

    assert profile == "youtube"
    assert should_run is False
    assert "covers build_youtube_pages" in reason


def test_scheduled_youtube_skips_when_us_intraday_overlay_window_is_active():
    profile, should_run, reason = gate.decide_schedule_gate(
        event_name="schedule",
        schedule="17 11 * * *",
        requested_profile="",
        manual_default_profile="",
        workflow_file="daily-youtube-reports.yml",
        current_run_id=445,
        client=FakeClient(),
        targets=_youtube_targets(),
        now_kst=_kst("2026-06-02T00:19:00"),
        block_us_intraday_overlay=True,
    )

    assert profile == "youtube"
    assert should_run is False
    assert "US intraday overlay window is active" in reason


def test_failed_prior_run_does_not_block_recovery():
    client = FakeClient(
        runs=[{"id": 555, "event": "schedule", "status": "completed", "conclusion": "failure"}],
        jobs={555: [{"name": "analyze_us", "status": "completed", "conclusion": "failure"}]},
    )

    _profile, should_run, reason = gate.decide_schedule_gate(
        event_name="schedule",
        schedule="10 7 * * 1-5",
        requested_profile="",
        manual_default_profile="all",
        workflow_file="daily-codex-analysis.yml",
        current_run_id=666,
        client=client,
        targets=_codex_targets(),
        now_kst=_kst("2026-06-03T16:40:00"),
    )

    assert should_run is True
    assert "running now" in reason


def test_manual_dispatch_always_runs_requested_profile():
    profile, should_run, reason = gate.decide_schedule_gate(
        event_name="workflow_dispatch",
        schedule="",
        requested_profile="kr",
        manual_default_profile="all",
        workflow_file="daily-codex-analysis.yml",
        current_run_id=777,
        client=FakeClient(),
        targets=_codex_targets(),
        now_kst=_kst("2026-06-03T16:40:00"),
    )

    assert profile == "kr"
    assert should_run is True
    assert "Manual dispatch runs profile=kr" in reason


def test_unrecognized_schedule_is_skipped_before_heavy_jobs():
    profile, should_run, reason = gate.decide_schedule_gate(
        event_name="schedule",
        schedule="0 0 * * *",
        requested_profile="",
        manual_default_profile="all",
        workflow_file="daily-codex-analysis.yml",
        current_run_id=888,
        client=FakeClient(),
        targets=_codex_targets(),
        now_kst=_kst("2026-06-03T16:40:00"),
    )

    assert profile == ""
    assert should_run is False
    assert "Unrecognized scheduled cron" in reason
