import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
import subprocess

import pytest
import yaml

from tradingagents import local_automation as local
from tradingagents.atomic_io import interprocess_file_lock


@pytest.fixture(autouse=True)
def ample_test_storage(monkeypatch):
    monkeypatch.setattr(local, "require_storage_headroom", lambda *paths: None)


@pytest.mark.parametrize("free,passes", [(4 * 1024**3, True), (4 * 1024**3 - 1, False)])
def test_local_output_reserve_blocks_full_disk_before_auth(tmp_path, monkeypatch, free, passes):
    from importlib import util
    spec = util.spec_from_file_location("local_storage_test", Path(local.__file__))
    unpatched = util.module_from_spec(spec)
    spec.loader.exec_module(unpatched)
    monkeypatch.setattr(unpatched.shutil, "disk_usage", lambda path: SimpleNamespace(free=free))
    if passes:
        unpatched.require_storage_headroom(tmp_path / "not-created")
    else:
        with pytest.raises(unpatched.LocalStorageHeadroomError):
            unpatched.require_storage_headroom(tmp_path / "not-created")


def test_manual_finalization_counts_against_existing_budget_without_rewriting_history(tmp_path, monkeypatch):
    import hashlib
    from tradingagents.scheduled import runner
    from tradingagents import local_advisory_recovery
    now = datetime(2026, 10, 9, 12, 0, tzinfo=timezone.utc)
    item = target()
    watchdog = SimpleNamespace(due_targets=lambda *a, **k: [item])
    monkeypatch.setattr(local, "script", lambda _: watchdog)
    monkeypatch.setattr(runner, "_iter_run_manifests_desc", lambda _: [])
    monkeypatch.setattr(local_advisory_recovery, "recover_due", lambda *a, **k: [])
    key = hashlib.sha256(f"{item.name}:{item.window_start_kst.isoformat()}".encode()).hexdigest()
    original = tmp_path / "attempts" / f"{key}.json"
    original.parent.mkdir()
    original.write_text(json.dumps({"attempts": 1, "started_at": item.window_start_kst.isoformat(), "exit_code": 1}))
    manual = tmp_path / "finalization-recovery" / f"{key}.json"
    manual.parent.mkdir()
    manual.write_text(json.dumps({"attempts": 1, "status": "FAILED"}))
    before = original.read_bytes()
    assert local.run_due(tmp_path / "archive", tmp_path, now=now) == [
        {"target": item.name, "status": "RETRY_BUDGET_OR_COOLDOWN"}]
    assert original.read_bytes() == before


def target():
    return SimpleNamespace(name="daily-codex-us", workflow_file="daily-codex-analysis.yml", inputs={"profile": "us"},
                           window_start_kst=datetime(2026, 10, 9, 8, 45, tzinfo=timezone.utc), max_failed_attempts=2)


def full_manifest():
    return {"started_at": "2026-10-09T09:00:00+00:00", "finished_at": "2026-10-09T10:00:00+00:00",
            "label": "local-scheduler-us-full", "settings": {"market": "US", "run_mode": "full"}, "status": "success",
            "summary": {"failed_tickers": 0, "configured_ticker_count": 2},
            "active_universe": {"coverage": {"complete": True}},
            "tickers": [{"ticker": "AAPL", "status": "success", "artifacts": {"analysis_json": "AAPL.json"}},
                        {"ticker": "MSFT", "status": "success", "artifacts": {"analysis_json": "MSFT.json"}}]}


def test_coverage_is_independent_of_failed_delivery():
    manifest = full_manifest()
    manifest["publication"] = {"status": "failed"}
    assert local.completed_target(manifest, target())


@pytest.mark.parametrize("clock,expected", [
    ("10:29", None), ("10:30", "1030"), ("12:49", "1030"),
    ("12:50", "1250"), ("13:00", "1250"), ("13:09", "1250"),
    ("13:10", "1310"), ("13:29", "1310"),
    ("13:30", "1330"), ("14:29", "1330"), ("14:30", "1430"),
    ("14:50", "1430"), ("14:51", None),
])
def test_local_kr_refreshes_precede_all_three_work_briefings(tmp_path, monkeypatch, clock, expected):
    from tradingagents.scheduled import runner, automation_calendar
    from tradingagents import local_advisory_recovery
    monkeypatch.setattr(runner, "_iter_run_manifests_desc", lambda _: [])
    monkeypatch.setattr(automation_calendar, "automated_market_session_status",
                        lambda **kwargs: SimpleNamespace(is_session=True))
    monkeypatch.setattr(local_advisory_recovery, "recover_due", lambda *a, **k: [])
    now = datetime.fromisoformat(f"2026-10-15T{clock}:00+09:00")
    decisions = local.run_due(tmp_path / "archive", tmp_path, now=now, dry_run=True)
    overlays = [d for d in decisions if d["target"].startswith("intraday-overlay-kr-")]
    assert overlays == ([] if expected is None else [
        {"target": f"intraday-overlay-kr-{expected}", "status": "DUE"}])


def test_old_kr_refresh_does_not_cover_pre_work_refresh_and_calendar_still_holds():
    watchdog = local.script("scheduled_actions_watchdog")
    now = datetime.fromisoformat("2026-10-15T10:40:00+09:00")
    targets = watchdog.due_targets(now, kr_overlay_checkpoints=local.KR_WORK_OVERLAY_CHECKPOINTS)
    target = next(t for t in targets if t.name == "intraday-overlay-kr-1030")
    manifest = {"settings": {"market": "KR", "run_mode": "overlay_only"}, "status": "success",
                "started_at": "2026-10-15T10:08:55+09:00", "finished_at": "2026-10-15T10:10:59+09:00",
                "summary": {"failed_tickers": 0},
                "execution": {"overlay_phase": {"selected_checkpoints": ["09:35"]},
                              "refresh_checkpoint": "09:35", "execution_asof": "2026-10-15T10:09:00+09:00"}}
    assert not local.completed_target(manifest, target)
    manifest.update(started_at="2026-10-15T10:33:55+09:00", finished_at="2026-10-15T10:36:00+09:00")
    manifest["execution"]["execution_asof"] = "2026-10-15T10:34:00+09:00"
    assert local.completed_target(manifest, target)
    held = watchdog.due_targets(now, kr_overlay_checkpoints=local.KR_WORK_OVERLAY_CHECKPOINTS,
        market_status_resolver=lambda **kwargs: SimpleNamespace(is_session=False))
    assert not any(t.name.startswith("intraday-overlay-kr-") for t in held)


@pytest.mark.parametrize("clock,expected", [
    ("2026-10-15T23:19:00+09:00", "1015-2240"),
    ("2026-10-15T23:20:00+09:00", "1015-2320"),
    ("2026-10-15T23:30:00+09:00", "1015-2320"),
    ("2026-10-15T23:40:00+09:00", "1015-2340"),
    ("2026-10-16T00:00:00+09:00", "1016-0000"),
])
def test_us_web_report_has_preparation_and_final_recheck_slots(clock, expected):
    watchdog = local.script("scheduled_actions_watchdog")
    targets = watchdog.due_targets(datetime.fromisoformat(clock),
        us_overlay_checkpoints=local.US_WORK_OVERLAY_CHECKPOINTS,
        market_status_resolver=lambda **kwargs: SimpleNamespace(is_session=True))
    assert any(t.name == f"intraday-overlay-us-{expected}" for t in targets)


@pytest.mark.parametrize("change", [
    lambda m: m.update(status="partial_failure"),
    lambda m: m["summary"].update(failed_tickers=1),
    lambda m: m["active_universe"]["coverage"].update(complete=False),
    lambda m: m["settings"].update(run_mode="overlay_only"),
    lambda m: m["settings"].update(analysis_mode="smoke"),
    lambda m: m["settings"].update(market="KR"),
    lambda m: m.update(label="manual-us"),
    lambda m: m.update(started_at="2026-10-08T09:00:00+00:00"),
    lambda m: m.update(finished_at="2026-10-09T08:00:00+00:00"),
    lambda m: m["tickers"].pop(),
])
def test_incomplete_or_wrong_cohort_never_suppresses_new_research(change):
    manifest = full_manifest()
    change(manifest)
    assert not local.completed_target(manifest, target())


def partial_manifest():
    manifest = full_manifest()
    manifest.update(run_id="20261009T090000_local-scheduler-us-full", status="partial_failure")
    manifest["summary"].update(successful_tickers=1, failed_tickers=1)
    manifest["tickers"][1]["status"] = "failed"
    return manifest


@pytest.mark.parametrize("change", [
    lambda m: m["settings"].update(market="KR"),
    lambda m: m["settings"].update(run_mode="overlay_only"),
    lambda m: m["settings"].update(analysis_mode="smoke"),
    lambda m: m.update(label="manual-us"),
    lambda m: m.update(started_at="2026-10-08T09:00:00+00:00"),
    lambda m: m.update(finished_at=None),
    lambda m: m.update(finished_at="2026-10-09T13:00:00+00:00"),
    lambda m: m.update(started_at="2026-10-09T09:00:00"),
    lambda m: m.update(status="running"),
    lambda m: m["summary"].update(successful_tickers=0),
    lambda m: m["summary"].update(failed_tickers=0),
])
def test_partial_recovery_never_selects_another_session_or_active_worker(change):
    manifest = partial_manifest()
    change(manifest)
    assert local.partial_target_source([manifest], target(), window_start=target().window_start_kst,
                                       now=datetime(2026, 10, 9, 12, tzinfo=timezone.utc)) is None


@pytest.mark.parametrize("exit_code", [0, 1])
def test_partial_local_retry_uses_failed_only_runner_and_preserves_budget(tmp_path, monkeypatch, exit_code):
    import hashlib
    from tradingagents.scheduled import runner
    from tradingagents.notifications import local as notifications

    item = target()
    now = datetime(2026, 10, 9, 12, tzinfo=timezone.utc)
    manifest = partial_manifest()
    older = partial_manifest()
    older["run_id"] = "20261009T085000_local-scheduler-us-full"
    monkeypatch.setattr(local, "script", lambda _: SimpleNamespace(due_targets=lambda *a, **k: [item]))
    monkeypatch.setattr(runner, "_iter_run_manifests_desc", lambda _: [(manifest, None), (older, None)])
    monkeypatch.setattr(local, "preflight", lambda _: None)
    calls, failures = [], []
    monkeypatch.setattr(local.subprocess, "run", lambda args, **kw: calls.append(args) or SimpleNamespace(returncode=exit_code))
    monkeypatch.setattr(notifications, "queue_failure", lambda *a, **kw: failures.append(kw))
    key = hashlib.sha256(f"{item.name}:{item.window_start_kst.isoformat()}".encode()).hexdigest()
    receipt = tmp_path / "attempts" / f"{key}.json"
    receipt.parent.mkdir()
    receipt.write_text(json.dumps({"attempts": 1, "started_at": item.window_start_kst.isoformat(), "exit_code": 1}))
    before = json.dumps(manifest, sort_keys=True)
    assert local.run_due(tmp_path / "archive", tmp_path, now=now) == [{"target": item.name, "status": "DUE"}]
    assert len(calls) == 1  # A rejected source cannot trigger a fallback full run.
    assert calls[0][calls[0].index("--resume-from-run") + 1] == manifest["run_id"]
    assert "--strict" in calls[0]
    assert json.loads(receipt.read_text())["attempts"] == 2
    assert len(failures) == exit_code
    assert json.dumps(manifest, sort_keys=True) == before
    monkeypatch.setattr(local.subprocess, "run", lambda *a, **k: pytest.fail("exhausted budget"))
    assert local.run_due(tmp_path / "archive", tmp_path, now=now)[0]["status"] == "RETRY_BUDGET_OR_COOLDOWN"


def test_producer_lock_does_not_block_publication(tmp_path):
    with interprocess_file_lock(tmp_path / "run-due.lock", timeout=0):
        with interprocess_file_lock(tmp_path / "publish.lock", timeout=0):
            pass
        with pytest.raises(TimeoutError):
            with interprocess_file_lock(tmp_path / "run-due.lock", timeout=0):
                pass


def test_daily_research_delegation_keeps_producer_free_and_original_attempt_budget(tmp_path, monkeypatch):
    import hashlib
    from tradingagents.execution import refresh_runtime
    from tradingagents.scheduled import runner
    item = target()
    now = datetime(2026, 10, 9, 12, tzinfo=timezone.utc)
    monkeypatch.setattr(local, "script", lambda _: SimpleNamespace(due_targets=lambda *a, **k: [item]))
    monkeypatch.setattr(runner, "_iter_run_manifests_desc", lambda _: [])
    monkeypatch.setattr(local, "preflight", lambda _: None)
    monkeypatch.setattr(local, "full_research_session_hold", lambda *a, **k: None)
    monkeypatch.setattr(refresh_runtime, "refresh_due", lambda *a, **k: [{"status": "REFRESH_COOLDOWN"}])
    local.atomic_write_json(tmp_path / "research-lane-enabled.json", {
        "mode": "PAPER_RESEARCH_INDEPENDENT_V1", "enabled": True, "real_orders_enabled": False})
    local.atomic_write_json(tmp_path / "kis-strategy/enabled.json", {"mode": "KIS_DEMO_STRATEGY", "enabled": True,
        "real_orders_enabled": False, "allocation_mode": "DEMO_NATIVE_ONE_SHARE_V1"})
    local.atomic_write_json(tmp_path / "actions-drained.json", {})
    key = hashlib.sha256(f"{item.name}:{item.window_start_kst.isoformat()}".encode()).hexdigest()
    receipt = tmp_path / "attempts" / f"{key}.json"
    local.atomic_write_json(receipt, {"attempts": 1, "started_at": "2026-10-09T09:00:00+00:00", "exit_code": 1})
    before = receipt.read_bytes()
    with interprocess_file_lock(tmp_path / "run-due.lock", timeout=0):
        assert local.run_due(tmp_path / "archive", tmp_path, now=now) == [
            {"target": item.name, "status": "DELEGATED_TO_RESEARCH_LANE"}, {"status": "REFRESH_COOLDOWN"}]
    assert receipt.read_bytes() == before
    calls = []
    def full(args, **kwargs):
        with interprocess_file_lock(tmp_path / "run-due.lock", timeout=0):
            calls.append(args)
        return SimpleNamespace(returncode=0)
    monkeypatch.setattr(local.subprocess, "run", full)
    with interprocess_file_lock(tmp_path / "research-kis.lock", timeout=0):
        assert local.run_due(tmp_path / "archive", tmp_path, now=now, research_only=True) == [
            {"target": item.name, "status": "DUE"}]
    assert calls[0][calls[0].index("--run-mode") + 1] == "full"
    assert json.loads(receipt.read_text())["attempts"] == 2
    after = receipt.read_bytes()
    assert local.run_due(tmp_path / "archive", tmp_path, now=now, research_only=True)[0]["status"] == "RETRY_BUDGET_OR_COOLDOWN"
    assert receipt.read_bytes() == after and len(calls) == 1


@pytest.mark.parametrize('enabled', [False, True])
def test_scheduled_overlay_cannot_starve_enabled_paper_refresh(tmp_path, monkeypatch, enabled):
    from tradingagents.scheduled import runner
    item = target()
    item.workflow_file = 'intraday-overlay-refresh.yml'
    monkeypatch.setattr(local, 'script', lambda _: SimpleNamespace(due_targets=lambda *a, **k: [item]))
    monkeypatch.setattr(local, 'local_target_window_start', lambda *a, **k: item.window_start_kst)
    monkeypatch.setattr(runner, '_iter_run_manifests_desc', lambda _: [])
    calls = []
    monkeypatch.setattr(local.subprocess, 'run', lambda args, **kw: calls.append(args) or SimpleNamespace(returncode=0))
    if enabled:
        local.atomic_write_json(tmp_path/'paper/enabled.json', {'enabled':True,'mode':'LOCAL_PAPER_ONLY','real_orders_enabled':False})
    local.run_due(tmp_path/'archive',tmp_path,now=datetime(2026,10,9,12,tzinfo=timezone.utc))
    assert len(calls) == 1
    assert ('--lightweight-execution-refresh' in calls[0]) is enabled
    assert calls[0][calls[0].index('--run-mode')+1] == 'overlay_only'


def test_drain_waits_without_cancelling_existing_producer(tmp_path, monkeypatch):
    monkeypatch.setattr(local.subprocess, "check_output", lambda *a, **k: "local\n")
    monkeypatch.setattr(local, "github_active_writers", lambda: [37977141414])
    assert local.drain_actions(tmp_path) == [37977141414]
    assert not (tmp_path / "actions-drained.json").exists()
    monkeypatch.setattr(local, "github_active_writers", lambda: [])
    assert local.drain_actions(tmp_path) == []
    monkeypatch.setattr(local, "github_active_writers", lambda: pytest.fail("Actions read after drain"))
    assert local.drain_actions(tmp_path) == []


def test_drain_requires_explicit_local_authority(tmp_path, monkeypatch):
    monkeypatch.setattr(local.subprocess, "check_output", lambda *a, **k: "github\n")
    with pytest.raises(ValueError, match="authority"):
        local.drain_actions(tmp_path)


@pytest.mark.parametrize("status,age_hours,jobs,expected", [
    ("queued", 48, 0, []), ("queued", 48, 1, [42]), ("queued", 1, 0, [42]), ("in_progress", 48, 0, [42]),
])
def test_old_jobless_queue_cannot_block_current_work_but_started_work_is_preserved(monkeypatch, status, age_hours, jobs, expected):
    from datetime import timedelta
    run = {"id": 42, "status": status, "head_branch": "main", "head_repository": {"full_name": local.REPOSITORY},
           "path": ".github/workflows/daily-codex-analysis.yml", "created_at": (datetime.now(timezone.utc) - timedelta(hours=age_hours)).isoformat()}
    monkeypatch.setattr(local.subprocess, "run", lambda *a, **k: SimpleNamespace(stdout=json.dumps({"workflow_runs": [run]})))
    monkeypatch.setattr(local.subprocess, "check_output", lambda *a, **k: json.dumps({"total_count": jobs, "jobs": [] if not jobs else [{"status": "queued"}]}))
    assert local.github_active_writers() == expected


def test_archive_outbox_detects_report_changes_but_not_worker_scratch(tmp_path, monkeypatch):
    monkeypatch.delenv("TRADINGAGENTS_PRISM_TELEGRAM_ARCHIVE_DIR", raising=False)
    monkeypatch.delenv("TRADINGAGENTS_YOUTUBE_ARCHIVE_DIR", raising=False)
    report = tmp_path / "work-reports" / "kr" / "latest.json"
    report.parent.mkdir(parents=True)
    report.write_text('{"report_sha256":"old"}')
    before = local.archive_fingerprint(tmp_path)
    (tmp_path / "partial-ticker.json").write_text("scratch")
    assert local.archive_fingerprint(tmp_path) == before
    report.write_text('{"report_sha256":"new"}')
    assert local.archive_fingerprint(tmp_path) != before


@pytest.mark.parametrize("subdir,filename", [
    ("", "run.json"),
    ("youtube-archive", "youtube_run.json"),
    ("prism-telegram-archive", "prism_telegram_run.json"),
])
def test_archive_outbox_detects_producer_completion_without_work_report(tmp_path, monkeypatch, subdir, filename):
    monkeypatch.delenv("TRADINGAGENTS_PRISM_TELEGRAM_ARCHIVE_DIR", raising=False)
    monkeypatch.delenv("TRADINGAGENTS_YOUTUBE_ARCHIVE_DIR", raising=False)
    run_dir = tmp_path / subdir / "runs" / "2026" / "producer-run"
    run_dir.mkdir(parents=True)
    before = local.archive_fingerprint(tmp_path)
    (run_dir / "attempt.json").write_text('{"status":"RUNNING"}')
    scratch = run_dir / "tickers" / "TEST"
    scratch.mkdir(parents=True)
    (scratch / "run.json").write_text('{"status":"success"}')
    assert local.archive_fingerprint(tmp_path) == before
    (run_dir / filename).write_text('{"status":"success","finished_at":"2026-10-12T03:06:00Z"}')
    completed = local.archive_fingerprint(tmp_path)
    assert completed != before
    (run_dir / "attempt.json").write_text('{"status":"SUCCESS"}')
    assert local.archive_fingerprint(tmp_path) == completed


def test_site_branch_is_nonforcing_public_only_and_blocks_rollback(tmp_path, monkeypatch):
    upstream = tmp_path / "upstream.git"
    subprocess.run(["git", "init", "--bare", str(upstream)], check=True, capture_output=True)
    state, site = tmp_path / "state", tmp_path / "site"
    state.mkdir()
    site.mkdir()
    (site / "index.html").write_text("public")
    strategy_bytes = b'{\r\n  "schema": "test",\r\n  "rows": []\r\n}\r\n'
    (site / "strategy.json").write_bytes(strategy_bytes)
    snapshot = {"schema": "tradingagents.pages-snapshot/v1", "generated_epoch_ms": 1000, "run_id": 1, "run_attempt": 1}
    (site / "pages-snapshot.json").write_text(json.dumps(snapshot))
    original = local.git_run
    def git_run(args, **kwargs):
        if "remote" in args and "add" in args:
            args = [*args[:-1], str(upstream)]
        result = original(args, **kwargs)
        if "init" in args:
            # Reproduce a Windows host with inherited autocrlf conversion.
            original([f"--git-dir={state / 'pages.git'}", "config", "core.autocrlf", "true"])
        return result
    monkeypatch.setattr(local, "git_run", git_run)
    commit = local.push_site(site, state)
    files = original([f"--git-dir={upstream}", "ls-tree", "-r", "--name-only", "gh-pages"])
    assert files.splitlines() == [".nojekyll", "index.html", "pages-snapshot.json", "strategy.json"]
    assert subprocess.check_output(["git", f"--git-dir={upstream}", "show", f"{commit}:strategy.json"]) == strategy_bytes
    assert original([f"--git-dir={upstream}", "rev-parse", "gh-pages"]) == commit
    with pytest.raises(ValueError, match="superseded"):
        local.push_site(site, state)
    snapshot["generated_epoch_ms"] = 2000
    (site / "pages-snapshot.json").write_text(json.dumps(snapshot))
    newer = local.push_site(site, state)
    assert original([f"--git-dir={upstream}", "rev-parse", f"{newer}^"]) == commit


@pytest.mark.parametrize("name", [".env", "api_keys.json", "portfolio-private/account.json", "telegram.session"])
def test_private_files_never_enter_public_branch(tmp_path, name):
    (tmp_path / "index.html").write_text("public")
    (tmp_path / "pages-snapshot.json").write_text("{}")
    private = tmp_path / name
    private.parent.mkdir(parents=True, exist_ok=True)
    private.write_text("private")
    with pytest.raises(ValueError, match="private"):
        local.push_site(tmp_path, tmp_path / "state")


def test_handoff_is_completed_only_for_exact_public_report(tmp_path):
    runtime, site = tmp_path / "runtime", tmp_path / "site"
    receipt = runtime / "handoffs" / "kr" / "sha.json"
    receipt.parent.mkdir(parents=True)
    receipt.write_text(json.dumps({"status": "LOCAL_PUBLISH_PENDING", "surface": "kr", "event_id": "kr:event", "report_sha256": "sha"}))
    report = site / "work" / "v1" / "kr" / "report" / "latest.json"
    report.parent.mkdir(parents=True)
    publication = {"verified_at": "now", "commit": "commit"}
    report.write_text(json.dumps({"event_id": "kr:other", "report_sha256": "sha"}))
    local.complete_handoffs(site, runtime, publication)
    assert json.loads(receipt.read_text())["status"] == "LOCAL_PUBLISH_PENDING"
    report.write_text(json.dumps({"event_id": "kr:event", "report_sha256": "sha"}))
    local.complete_handoffs(site, runtime, publication)
    assert json.loads(receipt.read_text())["external_delivery_verified"] is True


def test_core_cloud_writers_yield_to_local_authority():
    for filename, job in [("daily-codex-analysis.yml", "schedule_gate"), ("intraday-overlay-refresh.yml", "overlay_gate"),
                          ("scheduled-actions-watchdog.yml", "dispatch_missing_scheduled_actions"),
                          ("work-report-pages-refresh.yml", "prepare_self_hosted_runner"),
                          ("publish-ai-context.yml", "mirror"), ("hosted-runner-recovery.yml", "recover"),
                          ("daily-youtube-reports.yml", "deploy"), ("daily-prism-telegram-reports.yml", "deploy")]:
        workflow = yaml.safe_load(Path(f".github/workflows/{filename}").read_text(encoding="utf-8"))
        assert "vars.TRADINGAGENTS_AUTOMATION_BACKEND != 'local'" in workflow["jobs"][job]["if"]
    for filename, job in [("daily-codex-analysis.yml", "deploy"), ("intraday-overlay-refresh.yml", "deploy_overlay"),
                          ("work-report-pages-refresh.yml", "deploy"), ("account-portfolio-report-verify.yml", "deploy")]:
        workflow = yaml.safe_load(Path(f".github/workflows/{filename}").read_text(encoding="utf-8"))
        assert "vars.TRADINGAGENTS_AUTOMATION_BACKEND != 'local'" in workflow["jobs"][job]["if"]


def test_local_handoff_queues_without_dispatch_and_never_claims_delivery(tmp_path, monkeypatch):
    from tradingagents.work.handoff import dispatch_pages_handoff
    report_path = tmp_path / "report.json"
    report_path.write_text("{}")
    event, report_sha = "kr:event", "a" * 64
    runtime = SimpleNamespace(root=tmp_path / "work", status=lambda _: {"state": {
        "last_acked_event_id": event, "last_acked_report_sha256": report_sha, "last_acked_report_path": str(report_path)}})
    monkeypatch.setenv("TRADINGAGENTS_AUTOMATION_BACKEND", "local")
    result = dispatch_pages_handoff(runtime, surface="kr", event_id=event, report_sha256=report_sha,
                                   repository=local.REPOSITORY, runner=lambda *a, **k: pytest.fail("workflow dispatch"))
    assert result["status"] == "LOCAL_PUBLISH_PENDING"
    assert result["external_delivery_verified"] is False
    repeated = dispatch_pages_handoff(runtime, surface="kr", event_id=event, report_sha256=report_sha,
                                     repository=local.REPOSITORY)
    assert repeated["status"] == "LOCAL_PUBLISH_PENDING" and repeated["already_queued"]


def test_only_specific_actions_disabled_error_queues_local_handoff(tmp_path, monkeypatch):
    from tradingagents.work.handoff import dispatch_pages_handoff
    from tradingagents.work.runtime import WorkRuntimeError
    monkeypatch.delenv("TRADINGAGENTS_AUTOMATION_BACKEND", raising=False)
    monkeypatch.setattr("tradingagents.work.handoff.shutil.which", lambda _: "gh")
    report_path = tmp_path / "report.json"
    report_path.write_text("{}")
    runtime = SimpleNamespace(root=tmp_path / "work", status=lambda _: {"state": {
        "last_acked_event_id": "us:event", "last_acked_report_sha256": "b" * 64, "last_acked_report_path": str(report_path)}})
    binding = dict(surface="us", event_id="us:event", report_sha256="b" * 64, repository=local.REPOSITORY)
    with pytest.raises(WorkRuntimeError, match="dispatch failed"):
        dispatch_pages_handoff(runtime, **binding, runner=lambda *a, **k: subprocess.CompletedProcess([], 1, stderr="permission denied"))
    result = dispatch_pages_handoff(runtime, **binding, runner=lambda *a, **k: subprocess.CompletedProcess([], 1, stderr="Actions has been disabled for this repository. (HTTP 422)"))
    assert result["status"] == "LOCAL_PUBLISH_PENDING" and result["external_delivery_verified"] is False


def test_local_mirror_rejects_extra_files_before_any_remote_write(monkeypatch):
    mirror = local.script("publish_ai_context")
    monkeypatch.setattr(mirror, "api", lambda *a, **k: pytest.fail("Remote mutation before validation"))
    with pytest.raises(ValueError, match="file set"):
        mirror.publish(({}, {name: b"{}" for name in mirror.FILES | {"manifest.json", "private.json"}}))


@pytest.fixture
def delayed_publication(tmp_path, monkeypatch):
    from tradingagents.notifications import local as notifications
    from tradingagents.scheduled import config, site

    calls = {name: [] for name in ("build", "push", "mirror", "handoff", "reconcile", "sleep")}
    state = tmp_path / "state"
    state.mkdir()

    def build(archive, destination, settings):
        calls["build"].append(destination)
        (destination / "ai").mkdir(parents=True, exist_ok=True)
        (destination / "ai/manifest.json").write_text("{}", encoding="utf-8")

    snapshot = SimpleNamespace(create_snapshot=lambda *a, **k: None,
                               fetch_live_snapshot=lambda *a: {},
                               should_deploy=lambda *a: (True, "new snapshot"))
    mirror = SimpleNamespace(FILES=set(), publish=lambda value: calls["mirror"].append(value))
    modules = {"pages_snapshot": snapshot, "publish_ai_context": mirror,
               "verify_work_pages_handoff": SimpleNamespace()}
    monkeypatch.setattr(local, "script", modules.__getitem__)
    monkeypatch.setattr(config, "load_scheduled_config", lambda *a: SimpleNamespace(site={}))
    monkeypatch.setattr(site, "build_site", build)
    monkeypatch.setattr(local, "git_run", lambda *a, **k: "source-revision")

    def push(*args):
        calls["push"].append(args)
        return f"commit-{len(calls['push'])}"

    monkeypatch.setattr(local, "push_site", push)
    monkeypatch.setattr(local, "ensure_branch_pages", lambda *a: None)
    monkeypatch.setenv("GH_TOKEN", "offline-fixture")
    monkeypatch.setattr(local, "complete_handoffs", lambda *a: calls["handoff"].append(a[-1].copy()))
    monkeypatch.setattr(notifications, "reconcile_safely",
                        lambda *a, **k: calls["reconcile"].append(local.read_json(state / "publication.json", {})))
    monkeypatch.setattr(local.time, "sleep", calls["sleep"].append)
    return tmp_path / "archive", state, tmp_path / "work", calls


def test_each_changed_generation_finishes_delivery_before_next_producer(monkeypatch, delayed_publication):
    archive, state, runtime, calls = delayed_publication
    generations = iter(("first-overlay", "next-overlay"))
    monkeypatch.setattr(local, "archive_fingerprint", lambda _: next(generations))
    observations = iter((False, False, False, False, False, True, False, True))
    monkeypatch.setattr(local, "verify_live", lambda _: next(observations))

    first = local.publish(archive, state, runtime, publication_locked=True)
    second = local.publish(archive, state, runtime, publication_locked=True)

    assert [first["status"], second["status"]] == ["DELIVERY_VERIFIED", "DELIVERY_VERIFIED"]
    assert [v["fingerprint"] for v in calls["handoff"]] == ["first-overlay", "next-overlay"]
    assert [v.get("status") for v in calls["reconcile"]] == [
        None, "DELIVERY_VERIFIED", "DELIVERY_VERIFIED", "DELIVERY_VERIFIED"]
    assert len(calls["build"]) == len(calls["push"]) == len(calls["mirror"]) == 2
    assert calls["sleep"] == [15] * 6


def test_unpropagated_snapshot_stays_pending_and_resumes_without_republishing(monkeypatch, delayed_publication):
    archive, state, runtime, calls = delayed_publication
    monkeypatch.setattr(local, "archive_fingerprint", lambda _: "same-overlay")
    probes = []
    monkeypatch.setattr(local, "verify_live", lambda _: probes.append(False) or False)

    pending = local.publish(archive, state, runtime, publication_locked=True)

    assert pending["status"] == "PAGES_PENDING"
    assert len(probes) == 7
    assert calls["sleep"] == [15] * 6
    assert not calls["handoff"]
    assert len(calls["reconcile"]) == 1
    monkeypatch.setattr(local, "verify_live", lambda _: True)
    delivered = local.publish(archive, state, runtime, publication_locked=True)
    assert delivered["status"] == "DELIVERY_VERIFIED"
    assert len(calls["build"]) == len(calls["push"]) == len(calls["mirror"]) == 1
    assert len(calls["handoff"]) == 1


def test_live_verification_errors_keep_existing_failure_path(monkeypatch, delayed_publication):
    archive, state, runtime, calls = delayed_publication
    monkeypatch.setattr(local, "archive_fingerprint", lambda _: "same-overlay")

    def broken(_):
        raise ValueError("snapshot integrity error")

    monkeypatch.setattr(local, "verify_live", broken)
    with pytest.raises(ValueError, match="snapshot integrity"):
        local.publish(archive, state, runtime, publication_locked=True)
    assert local.read_json(state / "publication.json")["status"] == "PAGES_PENDING"
    assert not calls["handoff"]
    assert not calls["sleep"]


@pytest.mark.parametrize("mutated,live", [(False, True), (False, False), (True, True)])
def test_pending_generation_survives_new_inputs_but_not_partial_build(
        monkeypatch, delayed_publication, mutated, live):
    archive, state, runtime, calls = delayed_publication
    monkeypatch.setattr(local, "archive_fingerprint", lambda _: "newer-overlay")
    original = {"status": "PAGES_PENDING", "commit": "already-pushed",
                "fingerprint": "older-overlay", "mirror_verified": True}
    local.atomic_write_json(state / "publication.json", original)
    for relative in ("pages-snapshot.json", "mobile/strategy.json",
                     "work/v1/kr/report/latest.json", "work/v1/us/report/latest.json"):
        local.atomic_write_json(state / "site" / relative, {"generation": "pushed"})
    if mutated:
        local.atomic_write_json(state / "site/mobile/strategy.json", {"generation": "partial-build"})
    monkeypatch.setattr(local, "git_run", lambda *a, **k: '{"generation":"pushed"}')
    monkeypatch.setattr(local, "verify_live", lambda _: live)
    result = local.publish(archive, state, runtime, publication_locked=True)
    assert result["status"] == ("DELIVERY_VERIFIED" if live else "PAGES_PENDING")
    assert result["fingerprint"] == ("newer-overlay" if mutated else "older-overlay")
    assert len(calls["build"]) == len(calls["push"]) == int(mutated)
    if live:
        assert calls["handoff"][-1]["commit"] == ("commit-1" if mutated else "already-pushed")
    else:
        assert not calls["handoff"] and calls["sleep"] == [15] * 6
