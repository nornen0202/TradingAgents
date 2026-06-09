from __future__ import annotations

import importlib.util
import sys
from datetime import datetime
from pathlib import Path


MODULE_PATH = Path(".github/scripts/intraday_overlay_gate.py")
SPEC = importlib.util.spec_from_file_location("intraday_overlay_gate", MODULE_PATH)
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


def test_kr_overlay_waits_when_daily_codex_workflow_is_still_active():
    client = FakeClient(runs=[{"id": 101, "status": "in_progress", "conclusion": ""}])

    decisions, messages = gate.decide_intraday_gate(
        event_name="schedule",
        schedule="35 0-5 * * 1-5",
        requested_profile="",
        client=client,
        now_kst=_kst("2026-06-04T10:35:00"),
    )

    assert decisions == {"us": False, "kr": False}
    assert any("still active" in message for message in messages)
    assert client.last_workflow_file == "daily-codex-analysis.yml"
    assert client.last_created_since_utc == _kst("2026-06-04T06:00:00").astimezone(gate.UTC)


def test_kr_overlay_waits_when_only_daily_gate_job_succeeded():
    client = FakeClient(
        runs=[{"id": 102, "status": "completed", "conclusion": "success"}],
        jobs={102: [{"name": "schedule_gate", "status": "completed", "conclusion": "success"}]},
    )

    decisions, messages = gate.decide_intraday_gate(
        event_name="schedule",
        schedule="20 6 * * 1-5",
        requested_profile="",
        client=client,
        now_kst=_kst("2026-06-04T15:20:00"),
    )

    assert decisions["kr"] is False
    assert any("No completed successful Daily Codex KR target job" in message for message in messages)


def test_kr_overlay_waits_until_daily_pages_build_succeeds():
    client = FakeClient(
        runs=[{"id": 103, "status": "completed", "conclusion": "success"}],
        jobs={
            103: [
                {"name": "analyze_kr", "status": "completed", "conclusion": "success"},
                {"name": "build_pages", "status": "queued", "conclusion": ""},
            ]
        },
    )

    decisions, messages = gate.decide_intraday_gate(
        event_name="schedule",
        schedule="50 0-5 * * 1-5",
        requested_profile="",
        client=client,
        now_kst=_kst("2026-06-04T11:50:00"),
    )

    assert decisions["kr"] is False
    assert any("No completed successful Daily Codex KR target job" in message for message in messages)


def test_kr_overlay_waits_when_newer_daily_run_is_active_after_prior_success():
    client = FakeClient(
        runs=[
            {"id": 204, "status": "completed", "conclusion": "success", "created_at": "2026-06-04T01:00:00Z"},
            {"id": 205, "status": "in_progress", "conclusion": "", "created_at": "2026-06-04T01:30:00Z"},
        ],
        jobs={
            204: [
                {"name": "analyze_kr", "status": "completed", "conclusion": "success"},
                {"name": "build_pages", "status": "completed", "conclusion": "success"},
            ]
        },
    )

    decisions, messages = gate.decide_intraday_gate(
        event_name="schedule",
        schedule="50 0-5 * * 1-5",
        requested_profile="",
        client=client,
        now_kst=_kst("2026-06-04T11:50:00"),
    )

    assert decisions["kr"] is False
    assert any("Newer Daily Codex KR run(s) still active" in message for message in messages)


def test_kr_overlay_runs_after_completed_daily_codex_target_jobs():
    client = FakeClient(
        runs=[{"id": 104, "status": "completed", "conclusion": "success"}],
        jobs={
            104: [
                {"name": "analyze_kr", "status": "completed", "conclusion": "success"},
                {"name": "build_pages", "status": "completed", "conclusion": "success"},
            ]
        },
    )

    decisions, messages = gate.decide_intraday_gate(
        event_name="schedule",
        schedule="50 0-5 * * 1-5",
        requested_profile="",
        client=client,
        now_kst=_kst("2026-06-04T11:50:00"),
    )

    assert decisions["kr"] is True
    assert any("allowed" in message for message in messages)


def test_us_overlay_after_midnight_uses_previous_kst_daily_window():
    client = FakeClient(
        runs=[{"id": 105, "status": "completed", "conclusion": "success"}],
        jobs={
            105: [
                {"name": "analyze_us", "status": "completed", "conclusion": "success"},
                {"name": "build_pages", "status": "completed", "conclusion": "success"},
            ]
        },
    )

    decisions, _messages = gate.decide_intraday_gate(
        event_name="schedule",
        schedule="50 19,20 * * 1-5",
        requested_profile="",
        client=client,
        now_kst=_kst("2026-06-05T05:50:00"),
    )

    assert decisions["us"] is True
    assert client.last_created_since_utc == _kst("2026-06-04T16:00:00").astimezone(gate.UTC)


def test_manual_all_profile_can_run_each_side_independently():
    client = FakeClient(
        runs=[
            {"id": 201, "status": "completed", "conclusion": "success"},
            {"id": 202, "status": "completed", "conclusion": "failure"},
        ],
        jobs={
            201: [
                {"name": "analyze_us", "status": "completed", "conclusion": "success"},
                {"name": "build_pages", "status": "completed", "conclusion": "success"},
            ]
        },
    )

    decisions, _messages = gate.decide_intraday_gate(
        event_name="workflow_dispatch",
        schedule="",
        requested_profile="all",
        client=client,
        now_kst=_kst("2026-06-04T23:00:00"),
    )

    assert decisions == {"us": True, "kr": False}
