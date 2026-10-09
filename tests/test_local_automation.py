import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
import subprocess

import pytest
import yaml

from tradingagents import local_automation as local
from tradingagents.atomic_io import interprocess_file_lock


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


def test_producer_lock_does_not_block_publication(tmp_path):
    with interprocess_file_lock(tmp_path / "run-due.lock", timeout=0):
        with interprocess_file_lock(tmp_path / "publish.lock", timeout=0):
            pass
        with pytest.raises(TimeoutError):
            with interprocess_file_lock(tmp_path / "run-due.lock", timeout=0):
                pass


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
