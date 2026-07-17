from __future__ import annotations

import importlib.util
import io
import sys
import urllib.error
from datetime import datetime
from email.message import Message
from pathlib import Path

import pytest


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
        if isinstance(self.runs, dict):
            return self.runs.get(workflow_file, [])
        return self.runs

    def list_jobs(self, run_id):
        return self.jobs.get(run_id, [])


def _kst(value: str):
    return datetime.fromisoformat(value).replace(tzinfo=gate.KST)


def _codex_targets():
    return gate.load_schedule_targets(
        """
        {
          "50 8 * * 1-5": {"profile": "us", "window_start": "17:45", "target_jobs": ["analyze_us"]},
          "35 19 * * 0-4": {"profile": "kr", "window_start": "04:30", "target_jobs": ["analyze_kr"]}
        }
        """
    )


def _youtube_targets():
    return gate.load_schedule_targets(
        """
        {
          "20 20 * * *": {
            "profile": "youtube",
            "window_start": "05:00",
            "target_jobs": ["build_youtube_pages", "youtube_coverage"],
            "blockers": [
              {
                "name": "daily-codex-us-pages",
                "workflow_file": "daily-codex-analysis.yml",
                "window_start": "17:45",
                "target_jobs": ["analyze_us", "build_pages"]
              },
              {
                "name": "intraday-overlay-us-publish",
                "workflow_file": "intraday-overlay-refresh.yml",
                "window_start": "22:30",
                "target_jobs": ["overlay_refresh_us", "publish_overlay_site", "deploy_overlay"]
              }
            ]
          }
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
        schedule="50 8 * * 1-5",
        requested_profile="",
        manual_default_profile="all",
        workflow_file="daily-codex-analysis.yml",
        current_run_id=222,
        client=client,
        targets=_codex_targets(),
        now_kst=_kst("2026-06-03T18:40:00"),
    )

    assert profile == "us"
    assert should_run is False
    assert "workflow_dispatch run 111 has active target job(s): analyze_us" in reason


def test_scheduled_codex_does_not_skip_for_other_profile_target_job():
    client = FakeClient(
        runs=[{"id": 111, "event": "workflow_dispatch", "status": "in_progress", "conclusion": ""}],
        jobs={111: [{"name": "analyze_kr", "status": "in_progress", "conclusion": ""}]},
    )

    profile, should_run, reason = gate.decide_schedule_gate(
        event_name="schedule",
        schedule="50 8 * * 1-5",
        requested_profile="",
        manual_default_profile="all",
        workflow_file="daily-codex-analysis.yml",
        current_run_id=222,
        client=client,
        targets=_codex_targets(),
        now_kst=_kst("2026-06-03T18:40:00"),
    )

    assert profile == "us"
    assert should_run is True
    assert "running now" in reason


def test_scheduled_youtube_skips_when_prior_manual_pages_job_succeeded():
    client = FakeClient(
        runs=[{"id": 333, "event": "workflow_dispatch", "status": "completed", "conclusion": "success"}],
        jobs={
            333: [
                {"name": "build_youtube_pages", "status": "completed", "conclusion": "success"},
                {"name": "youtube_coverage", "status": "completed", "conclusion": "success"},
            ]
        },
    )

    profile, should_run, reason = gate.decide_schedule_gate(
        event_name="schedule",
        schedule="20 20 * * *",
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
    assert "covers target job set: build_youtube_pages, youtube_coverage" in reason


def test_scheduled_youtube_does_not_count_runtime_gate_noop_as_coverage():
    client = FakeClient(
        runs=[{"id": 334, "event": "schedule", "status": "completed", "conclusion": "success"}],
        jobs={334: [{"name": "build_youtube_pages", "status": "completed", "conclusion": "success"}]},
    )

    _profile, should_run, reason = gate.decide_schedule_gate(
        event_name="schedule",
        schedule="20 20 * * *",
        requested_profile="",
        manual_default_profile="",
        workflow_file="daily-youtube-reports.yml",
        current_run_id=444,
        client=client,
        targets=_youtube_targets(),
        now_kst=_kst("2026-06-03T20:17:00"),
    )

    assert should_run is True
    assert "running now" in reason


def test_scheduled_youtube_waits_for_active_build_before_coverage_marker():
    client = FakeClient(
        runs=[{"id": 335, "event": "schedule", "status": "in_progress", "conclusion": ""}],
        jobs={335: [{"name": "build_youtube_pages", "status": "in_progress", "conclusion": ""}]},
    )

    _profile, should_run, reason = gate.decide_schedule_gate(
        event_name="schedule",
        schedule="20 20 * * *",
        requested_profile="",
        manual_default_profile="",
        workflow_file="daily-youtube-reports.yml",
        current_run_id=444,
        client=client,
        targets=_youtube_targets(),
        now_kst=_kst("2026-06-03T20:17:00"),
    )

    assert should_run is False
    assert "active target job(s): build_youtube_pages" in reason


def test_scheduled_codex_retries_when_analysis_succeeded_but_pages_did_not():
    targets = gate.load_schedule_targets(
        """
        {
          "50 8 * * 1-5": {
            "profile": "us",
            "window_start": "17:45",
            "target_jobs": ["analyze_us", "build_pages"]
          }
        }
        """
    )
    client = FakeClient(
        runs=[{"id": 112, "event": "schedule", "status": "completed", "conclusion": "success"}],
        jobs={
            112: [
                {"name": "analyze_us", "status": "completed", "conclusion": "success"},
                {"name": "build_pages", "status": "completed", "conclusion": "failure"},
            ]
        },
    )

    profile, should_run, reason = gate.decide_schedule_gate(
        event_name="schedule",
        schedule="50 8 * * 1-5",
        requested_profile="",
        manual_default_profile="all",
        workflow_file="daily-codex-analysis.yml",
        current_run_id=222,
        client=client,
        targets=targets,
        now_kst=_kst("2026-06-03T18:10:00"),
    )

    assert profile == "us"
    assert should_run is True
    assert "running now" in reason


def test_scheduled_codex_skips_only_when_analysis_and_pages_both_succeeded():
    targets = gate.load_schedule_targets(
        """
        {
          "50 8 * * 1-5": {
            "profile": "us",
            "window_start": "17:45",
            "target_jobs": ["analyze_us", "build_pages"]
          }
        }
        """
    )
    client = FakeClient(
        runs=[{"id": 113, "event": "schedule", "status": "completed", "conclusion": "success"}],
        jobs={
            113: [
                {"name": "analyze_us", "status": "completed", "conclusion": "success"},
                {"name": "build_pages", "status": "completed", "conclusion": "success"},
            ]
        },
    )

    _profile, should_run, reason = gate.decide_schedule_gate(
        event_name="schedule",
        schedule="50 8 * * 1-5",
        requested_profile="",
        manual_default_profile="all",
        workflow_file="daily-codex-analysis.yml",
        current_run_id=222,
        client=client,
        targets=targets,
        now_kst=_kst("2026-06-03T18:10:00"),
    )

    assert should_run is False
    assert "covers target job set: analyze_us, build_pages" in reason


def test_scheduled_codex_waits_when_prior_run_is_between_analysis_and_pages():
    targets = gate.load_schedule_targets(
        """
        {
          "50 8 * * 1-5": {
            "profile": "us",
            "window_start": "17:45",
            "target_jobs": ["analyze_us", "build_pages"]
          }
        }
        """
    )
    client = FakeClient(
        runs=[{"id": 114, "event": "schedule", "status": "in_progress", "conclusion": ""}],
        jobs={114: [{"name": "analyze_us", "status": "completed", "conclusion": "success"}]},
    )

    _profile, should_run, reason = gate.decide_schedule_gate(
        event_name="schedule",
        schedule="50 8 * * 1-5",
        requested_profile="",
        manual_default_profile="all",
        workflow_file="daily-codex-analysis.yml",
        current_run_id=222,
        client=client,
        targets=targets,
        now_kst=_kst("2026-06-03T18:10:00"),
    )

    assert should_run is False
    assert "waiting for build_pages" in reason


def test_scheduled_youtube_waits_when_daily_codex_pages_build_is_queued():
    client = FakeClient(
        runs={
            "daily-youtube-reports.yml": [],
            "daily-codex-analysis.yml": [{"id": 901, "event": "schedule", "status": "in_progress", "conclusion": ""}],
        },
        jobs={901: [{"name": "build_pages", "status": "queued", "conclusion": ""}]},
    )

    profile, should_run, reason = gate.decide_schedule_gate(
        event_name="schedule",
        schedule="20 20 * * *",
        requested_profile="",
        manual_default_profile="",
        workflow_file="daily-youtube-reports.yml",
        current_run_id=902,
        client=client,
        targets=_youtube_targets(),
        now_kst=_kst("2026-06-09T05:53:00"),
    )

    assert profile == "youtube"
    assert should_run is False
    assert "Active blocker daily-codex-us-pages run 901 has build_pages: queued" in reason


def test_scheduled_youtube_waits_when_daily_codex_analysis_is_running():
    client = FakeClient(
        runs={
            "daily-youtube-reports.yml": [],
            "daily-codex-analysis.yml": [{"id": 903, "event": "schedule", "status": "in_progress", "conclusion": ""}],
        },
        jobs={903: [{"name": "analyze_us", "status": "in_progress", "conclusion": ""}]},
    )

    _profile, should_run, reason = gate.decide_schedule_gate(
        event_name="schedule",
        schedule="20 20 * * *",
        requested_profile="",
        manual_default_profile="",
        workflow_file="daily-youtube-reports.yml",
        current_run_id=904,
        client=client,
        targets=_youtube_targets(),
        now_kst=_kst("2026-06-09T05:53:00"),
    )

    assert should_run is False
    assert "has analyze_us: in_progress" in reason


def test_scheduled_youtube_waits_when_us_overlay_publish_is_running():
    client = FakeClient(
        runs={
            "daily-youtube-reports.yml": [],
            "daily-codex-analysis.yml": [],
            "intraday-overlay-refresh.yml": [{"id": 905, "event": "schedule", "status": "in_progress", "conclusion": ""}],
        },
        jobs={905: [{"name": "publish_overlay_site", "status": "in_progress", "conclusion": ""}]},
    )

    _profile, should_run, reason = gate.decide_schedule_gate(
        event_name="schedule",
        schedule="20 20 * * *",
        requested_profile="",
        manual_default_profile="",
        workflow_file="daily-youtube-reports.yml",
        current_run_id=906,
        client=client,
        targets=_youtube_targets(),
        now_kst=_kst("2026-06-09T05:53:00"),
    )

    assert should_run is False
    assert "intraday-overlay-us-publish" in reason
    assert "publish_overlay_site: in_progress" in reason


def test_failed_prior_run_does_not_block_recovery():
    client = FakeClient(
        runs=[{"id": 555, "event": "schedule", "status": "completed", "conclusion": "failure"}],
        jobs={555: [{"name": "analyze_us", "status": "completed", "conclusion": "failure"}]},
    )

    _profile, should_run, reason = gate.decide_schedule_gate(
        event_name="schedule",
        schedule="50 8 * * 1-5",
        requested_profile="",
        manual_default_profile="all",
        workflow_file="daily-codex-analysis.yml",
        current_run_id=666,
        client=client,
        targets=_codex_targets(),
        now_kst=_kst("2026-06-03T18:40:00"),
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


class _JsonResponse:
    def __init__(self, payload: str = '{"workflow_runs": []}') -> None:
        self.payload = payload.encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self.payload


def _http_error(code: int, *, headers: dict[str, str] | None = None, body: str = ""):
    message = Message()
    for key, value in (headers or {}).items():
        message[key] = value
    return urllib.error.HTTPError(
        "https://api.github.com/test",
        code,
        "test",
        message,
        io.BytesIO(body.encode("utf-8")),
    )


def _retry_client(delays: list[float], *, clock: float = 100.0, max_attempts: int = 4):
    return gate.GitHubActionsGateClient(
        repository="owner/repo",
        token="token",
        max_attempts=max_attempts,
        sleep=delays.append,
        clock=lambda: clock,
    )


def _sequence_opener(calls):
    def open_next(*_args, **_kwargs):
        result = calls.pop(0)
        if isinstance(result, BaseException):
            raise result
        return result

    return open_next


def test_github_api_retries_transient_503(monkeypatch):
    calls = [_http_error(503), _JsonResponse()]
    delays: list[float] = []
    monkeypatch.setattr(gate.urllib.request, "urlopen", _sequence_opener(calls))

    payload = _retry_client(delays)._request("GET", "/actions/runs")

    assert payload == {"workflow_runs": []}
    assert delays == [1.0]


def test_github_api_honors_full_retry_after(monkeypatch):
    calls = [_http_error(429, headers={"Retry-After": "60"}), _JsonResponse()]
    delays: list[float] = []
    monkeypatch.setattr(gate.urllib.request, "urlopen", _sequence_opener(calls))

    _retry_client(delays)._request("GET", "/actions/runs")

    assert delays == [60.0]


def test_github_api_uses_primary_rate_limit_reset(monkeypatch):
    calls = [
        _http_error(403, headers={"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "120"}),
        _JsonResponse(),
    ]
    delays: list[float] = []
    monkeypatch.setattr(gate.urllib.request, "urlopen", _sequence_opener(calls))

    _retry_client(delays)._request("GET", "/actions/runs")

    assert delays == [21.0]


def test_github_api_does_not_retry_permission_403(monkeypatch):
    calls = [_http_error(403, headers={"X-RateLimit-Remaining": "42"}, body="forbidden")]
    delays: list[float] = []
    monkeypatch.setattr(gate.urllib.request, "urlopen", _sequence_opener(calls))

    with pytest.raises(urllib.error.HTTPError):
        _retry_client(delays)._request("GET", "/actions/runs")

    assert delays == []


def test_github_api_retries_confirmed_secondary_rate_limit(monkeypatch):
    calls = [_http_error(403, body='{"message":"You have exceeded a secondary rate limit."}'), _JsonResponse()]
    delays: list[float] = []
    monkeypatch.setattr(gate.urllib.request, "urlopen", _sequence_opener(calls))

    _retry_client(delays)._request("GET", "/actions/runs")

    assert delays == [60.0]


def test_github_api_raises_after_retry_exhaustion(monkeypatch):
    calls = [_http_error(503) for _ in range(4)]
    delays: list[float] = []
    monkeypatch.setattr(gate.urllib.request, "urlopen", _sequence_opener(calls))

    with pytest.raises(urllib.error.HTTPError):
        _retry_client(delays)._request("GET", "/actions/runs")

    assert delays == [1.0, 3.0, 7.0]


def test_runtime_gate_can_skip_external_blocker_checks():
    client = FakeClient(
        runs={
            "daily-youtube-reports.yml": [],
            "daily-codex-analysis.yml": [
                {"id": 901, "event": "schedule", "status": "in_progress", "conclusion": ""}
            ],
        },
        jobs={901: [{"name": "build_pages", "status": "queued", "conclusion": ""}]},
    )

    _profile, should_run, reason = gate.decide_schedule_gate(
        event_name="schedule",
        schedule="20 20 * * *",
        requested_profile="",
        manual_default_profile="",
        workflow_file="daily-youtube-reports.yml",
        current_run_id=902,
        client=client,
        targets=_youtube_targets(),
        now_kst=_kst("2026-06-09T05:53:00"),
        check_blockers=False,
    )

    assert should_run is True
    assert "running now" in reason
