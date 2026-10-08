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


def test_watchdog_keeps_pre_boundary_manual_full_active_without_counting_old_success():
    target = next(t for t in watchdog.due_targets(_kst('2026-09-30T18:00:00')) if t.name=='daily-codex-us')
    for status, expected in [('in_progress',True),('completed',False)]:
        client=FakeClient(runs=[{'id':111,'created_at':'2026-09-30T07:35:00Z','status':status,
            'conclusion':'success' if status=='completed' else '', 'display_title':'Daily [profile=us] [run_mode=full]'}],
            jobs={111:[{'name':name,'status':status,'conclusion':'success' if status=='completed' else ''} for name in target.job_names]})
        covered,_=watchdog.target_is_covered(client=client,target=target)
        assert covered is expected
        assert client.last_created_since_utc <= datetime.fromisoformat('2026-09-30T07:35:00+00:00')


def test_smoke_or_site_rebuild_does_not_satisfy_daily_full_analysis():
    target=next(t for t in watchdog.due_targets(_kst('2026-09-30T18:00:00')) if t.name=='daily-codex-us')
    for mode in ['smoke','site_only']:
        client=FakeClient(runs=[{'id':111,'created_at':'2026-09-30T08:50:00Z','status':'completed','conclusion':'success',
            'display_title':f'Daily [profile=us] [run_mode={mode}] [request_scope=default_universe]'}],
            jobs={111:[{'name':name,'status':'completed','conclusion':'success'} for name in target.job_names]})
        assert not watchdog.target_is_covered(client=client,target=target)[0]


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


def test_prism_recovery_grace_daily_window_and_original_collection_interval():
    for moment in ("2026-10-08T07:49:59", "2026-10-08T17:00:00", "2026-10-09T01:00:00"):
        assert not any(t.name == "prism-daily" for t in watchdog.due_targets(_kst(moment)))
    for moment, lookback in (("2026-10-08T07:50:00", "375"),
                             ("2026-10-08T08:35:00.1", "421"),
                             ("2026-10-10T10:00:00", "505")):
        target = next(t for t in watchdog.due_targets(_kst(moment)) if t.name == "prism-daily")
        assert target.window_start_kst == _kst(moment[:10] + "T07:35:00")
        assert target.inputs == {"lookback_minutes": lookback, "max_messages": "80", "recovery_source": "cloud_watchdog"}
        assert target.work_job_names == ("build_prism_telegram_pages",)
        assert "mode" not in target.inputs
    targets = watchdog.due_targets(_kst("2026-10-09T10:00:00"),
        market_status_resolver=lambda **kwargs: type("Closed", (), {"is_session": False})())
    assert any(t.name == "prism-daily" for t in targets)


def test_prism_old_success_is_not_today_completion_but_active_owner_is_protected():
    target = next(t for t in watchdog.due_targets(_kst("2026-10-08T10:00:00")) if t.name == "prism-daily")
    for created, status, jobs, expected in (
        ("2026-10-07T01:44:00Z", "completed", [{"name": n, "status": "completed", "conclusion": "success"} for n in target.job_names], False),
        ("2026-10-07T22:35:00Z", "completed", [{"name": n, "status": "completed", "conclusion": "success"} for n in target.job_names], True),
        ("2026-10-07T22:35:00Z", "completed", [{"name": "build_prism_telegram_pages", "status": "completed", "conclusion": "success"}, {"name": "deploy", "status": "completed", "conclusion": "cancelled"}], True),
        ("2026-10-07T22:35:00Z", "queued", [], True),
        ("2026-10-07T01:44:00Z", "in_progress", [{"name": "build_prism_telegram_pages", "status": "in_progress"}], True),
    ):
        client = FakeClient(runs=[dict(id=100, created_at=created, status=status, conclusion="success" if status == "completed" else "")], jobs={100: jobs})
        assert watchdog.target_is_covered(client=client, target=target)[0] is expected


def test_prism_yields_to_active_market_or_youtube_jobs_and_keeps_retry_budget():
    target = next(t for t in watchdog.due_targets(_kst("2026-10-08T10:00:00")) if t.name == "prism-daily")
    for blocker in target.blockers:
        client = FakeClient(runs={blocker.workflow_file: [dict(id=100, created_at="2026-10-08T00:55:00Z", status="in_progress")]},
            jobs={100: [dict(name=blocker.job_names[0], status="in_progress")]})
        assert watchdog.blockers_are_clear(client=client, target=target)[0] is False
    client = FakeClient(runs=[dict(id=i, created_at="2026-10-08T00:00:00Z", status="completed", conclusion="failure") for i in (100, 101)],
        jobs={i: [dict(name="build_prism_telegram_pages", status="completed", conclusion="failure")] for i in (100, 101)})
    covered, reason = watchdog.target_is_covered(client=client, target=target)
    assert covered and reason.startswith("Retry budget exhausted")


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


def test_daily_codex_us_watchdog_yields_after_overnight_recovery_window():
    targets = watchdog.due_targets(_kst("2026-06-02T08:17:00"))

    assert not [target for target in targets if target.name == "daily-codex-us"]


def test_daily_codex_kr_watchdog_stays_due_before_ten_kst_target():
    targets = watchdog.due_targets(_kst("2026-06-01T09:37:00"))

    codex_kr = [target for target in targets if target.name == "daily-codex-kr"]
    assert codex_kr
    assert codex_kr[0].max_failed_attempts == 4


def test_us_recovery_after_midnight_preserves_session_and_retry_budget():
    for when, expected in (("2026-09-30T02:15:00", "2026-09-29T17:45:00"),
                           ("2026-10-03T07:15:00", "2026-10-02T17:45:00")):
        target = next(item for item in watchdog.due_targets(_kst(when)) if item.name == "daily-codex-us")
        assert target.window_start_kst == _kst(expected)
        assert target.max_failed_attempts == 4


def test_daily_codex_kr_watchdog_yields_after_recovery_window():
    targets = watchdog.due_targets(_kst("2026-06-01T10:17:00"))

    assert not [target for target in targets if target.name == "daily-codex-kr"]


def test_watchdog_filters_market_targets_on_exchange_holiday():
    class Status:
        def __init__(self, is_session):
            self.is_session = is_session

    targets = watchdog.due_targets(
        _kst("2026-08-17T10:07:00"),
        market_status_resolver=lambda *, market, now: Status(market != "kr"),
    )

    assert not [target for target in targets if target.name.startswith("intraday-overlay-kr-")]


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


def test_previous_session_jobless_schedule_does_not_block_new_kr_production():
    # A native US-era run was still queued with no jobs when the KR window
    # opened. It must retain US ownership without suppressing the new KR day.
    client = FakeClient(runs={"daily-codex-analysis.yml": [{
        "id": 37655538332, "event": "schedule", "status": "queued",
        "created_at": "2026-10-07T16:57:30Z", "display_title": "Daily Codex Analysis",
    }]})

    messages = watchdog.run_watchdog(client=client, now_kst=_kst("2026-10-08T04:55:00"))

    assert client.dispatches == [
        ("daily-codex-analysis.yml", {"profile": "kr", "recovery_source": "cloud_watchdog"})
    ]
    assert any("daily-codex-us: covered" in message for message in messages)
    assert any("daily-codex-kr: dispatched" in message for message in messages)


def test_jobless_schedule_exception_preserves_current_or_identifiable_ownership():
    target = next(t for t in watchdog.due_targets(_kst("2026-10-08T04:55:00"))
                  if t.name == "daily-codex-kr")
    old_run = {"id": 321, "event": "schedule", "status": "queued",
               "created_at": "2026-10-07T16:57:30Z", "display_title": "Daily Codex Analysis"}
    cases = [
        ({"created_at": "2026-10-07T19:30:00Z"}, []),
        ({"created_at": None}, []),
        ({"created_at": "invalid"}, []),
        ({"event": "workflow_dispatch"}, []),
        ({"display_title": "Daily [profile=kr] [run_mode=full]"}, []),
        ({"display_title": "Daily [profile=all]"}, []),
        ({"status": "in_progress"}, []),
        ({}, [{"name": "analysis_gate", "status": "queued", "conclusion": ""}]),
        ({}, [{"name": "analyze_kr", "status": "in_progress", "conclusion": ""}]),
        ({}, [{"name": "deploy", "status": "waiting", "conclusion": ""}]),
    ]
    for changes, jobs in cases:
        client = FakeClient(runs=[old_run | changes], jobs={321: jobs})
        assert watchdog.target_is_covered(client=client, target=target)[0], (changes, jobs)


def test_previous_jobless_advisory_schedule_keeps_ownership():
    target = watchdog.WatchdogTarget(
        name="youtube-daily", workflow_file="daily-youtube-reports.yml",
        job_names=("build_youtube_pages",), window_start_kst=_kst("2026-10-08T05:00:00"), inputs={},
    )
    client = FakeClient(runs=[{"id": 123, "event": "schedule", "status": "queued",
                              "created_at": "2026-10-07T16:57:30Z"}])
    assert watchdog.target_is_covered(client=client, target=target)[0]


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


def test_watchdog_log_signature_ignores_volatile_github_correlation_ids():
    first = watchdog._log_text_diagnostic_signature(
        "2026-08-17T13:56:43Z ##[error]Response status code does not indicate success: "
        "429 (Too Many Requests). 06CA:C276A:1261:191C8:6A8312F6"
    )
    second = watchdog._log_text_diagnostic_signature(
        "2026-08-17T14:04:47Z ##[error]Response status code does not indicate success: "
        "429 (Too Many Requests). 3125:1C2169:29B4:1DD30:6A8314DF"
    )

    assert first == second


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


def test_watchdog_defers_transient_dispatch_failure_without_failing_run():
    class DispatchUnavailableClient(FakeClient):
        def dispatch(self, workflow_file, inputs):
            import urllib.error

            raise urllib.error.HTTPError(
                "https://api.github.test/dispatches",
                503,
                "Service Unavailable",
                {},
                None,
            )

    client = DispatchUnavailableClient(runs=[])

    messages = watchdog.run_watchdog(
        client=client,
        now_kst=_kst("2026-06-02T06:57:00"),
    )

    assert any(
        "youtube-daily: dispatch deferred; GitHub Actions API unavailable HTTP 503"
        in message
        for message in messages
    )


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

def test_watchdog_does_not_hide_permanent_dispatch_errors():
    import urllib.error
    import pytest

    class UnauthorizedClient(FakeClient):
        def dispatch(self, *_args):
            raise urllib.error.HTTPError("https://api.github.test", 401, "Unauthorized", {}, None)

    with pytest.raises(urllib.error.HTTPError):
        watchdog.run_watchdog(client=UnauthorizedClient(), now_kst=_kst("2026-06-02T06:57:00"))


def test_watchdog_reports_calendar_hold_without_querying_market_workflows():
    from datetime import date
    from tradingagents.scheduled.automation_calendar import MarketSessionStatus

    messages = watchdog.run_watchdog(
        client=FakeClient(), now_kst=_kst("2026-06-02T18:07:00"),
        market_status_resolver=lambda **_kw: MarketSessionStatus("us", date(2026, 6, 2), None, "test"),
        dry_run=True,
    )
    assert any("held;" in message and "unavailable" in message for message in messages)
