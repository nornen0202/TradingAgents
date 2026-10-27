from datetime import datetime, timedelta
import json
from types import SimpleNamespace

import pytest
import yaml

from tradingagents import local_automation as local
from tradingagents import local_advisory_recovery as recovery


NOW = datetime.fromisoformat("2026-10-14T09:00:00+09:00")
YT, PRISM = recovery.SPECS["youtube"][0], recovery.SPECS["prism"][0]


@pytest.fixture
def watchdog():
    return local.script("scheduled_actions_watchdog")


class Client:
    def __init__(self, runs=None, jobs=None):
        self.runs, self.jobs = runs or {}, jobs or {}
        self.dispatched = []
        self.error = None

    def list_runs(self, workflow, **kwargs):
        return self.runs.get(workflow, [])

    def list_jobs(self, run_id):
        return self.jobs.get(run_id, [])

    def list_active_runs(self):
        return [run for runs in self.runs.values() for run in runs if run.get("status") != "completed"]

    def failure_diagnostic_signature(self, run_id):
        return "same-cause"

    def dispatch(self, workflow, inputs):
        self.dispatched.append((workflow, inputs))
        if self.error:
            raise self.error


def run_record(surface="youtube", *, run_id=10, status="completed", conclusion="success", created=None):
    return {"id": run_id, "run_attempt": 1, "status": status, "conclusion": conclusion,
            "created_at": (created or NOW - timedelta(minutes=60)).isoformat(), "head_sha": "same-sha",
            "head_branch": "main", "head_repository": {"full_name": recovery.REPOSITORY},
            "path": ".github/workflows/" + recovery.SPECS[surface][0], "event": "workflow_dispatch",
            "display_title": "[recovery_source=local_watchdog]"}


def build(surface="youtube", *, collection="success", stamp="success", conclusion="success"):
    spec = recovery.SPECS[surface]
    return {"name": spec[1], "status": "completed", "conclusion": conclusion,
            "steps": [{"name": spec[2], "conclusion": collection,
                       "started_at": "2026-10-14T08:00:00+09:00", "completed_at": "2026-10-14T08:10:00+09:00"},
                      {"name": "Stamp rollback-resistant Pages snapshot", "conclusion": stamp}]}


def write_manifest(archive, surface="youtube", *, run_id=None, status="success"):
    from tradingagents.youtube.config import load_youtube_config
    from tradingagents.prism_telegram.config import load_prism_telegram_config
    spec = recovery.SPECS[surface]
    run_id = run_id or ("youtube" if surface == "youtube" else "prism_telegram") + "_20261014_080100"
    path = archive / spec[5] / "runs" / "2026" / run_id / spec[3]
    path.parent.mkdir(parents=True)
    value = {"run_id": run_id, "status": status, "started_at": "2026-10-14T08:01:00+09:00",
             "finished_at": "2026-10-14T08:09:00+09:00",
             "channel_urls": list(load_youtube_config(local.ROOT / "config/youtube_daily.toml").channel.urls),
             "source": {"channel": load_prism_telegram_config(local.ROOT / "config/prism_telegram_daily.toml").source.channel},
             "summary": {"total_videos": 1, "successful_videos": 1, "failed_videos": 0,
                         "messages": 1, "warnings": 0}}
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def recover(tmp_path, watchdog, client, *, now=NOW, targets=None, dry_run=False):
    return recovery.recover_due(tmp_path / "archive", tmp_path / "state", watchdog=watchdog,
                                targets=targets or watchdog.due_targets(now), now=now, dry_run=dry_run,
                                client_factory=lambda _: client)


def test_idle_recovers_only_one_existing_advisory_target_and_persists_before_post(tmp_path, watchdog):
    client = Client()
    original = client.dispatch
    def dispatch(workflow, inputs):
        root = tmp_path / "state" / "advisory-recovery"
        assert json.loads((root / "admission.json").read_text())["status"] == "DISPATCH_REQUESTED"
        assert len(list((root / "attempts").glob("*.json"))) == 1
        original(workflow, inputs)
    client.dispatch = dispatch
    assert recover(tmp_path, watchdog, client)[-1]["status"] == "ADVISORY_DISPATCH_ACCEPTED"
    assert client.dispatched == [(YT, {"lookback_hours": "24", "publish": "true", "recovery_source": "local_watchdog"})]


def test_prism_reuses_original_lookback_and_message_cap(tmp_path, watchdog):
    targets = [target for target in watchdog.due_targets(NOW) if target.workflow_file == PRISM]
    client = Client()
    recover(tmp_path, watchdog, client, targets=targets)
    assert client.dispatched == [(PRISM, {"lookback_minutes": "445", "max_messages": "80", "recovery_source": "local_watchdog"})]


@pytest.mark.parametrize("clock", ["13:00", "14:30", "14:59"])
def test_late_overlap_reserves_time_for_prism_before_youtube(tmp_path, watchdog, clock):
    now = datetime.fromisoformat(f"2026-10-14T{clock}:00+09:00")
    client = Client()
    assert recover(tmp_path, watchdog, client, now=now)[-1]["status"] == "ADVISORY_DISPATCH_ACCEPTED"
    assert len(client.dispatched) == 1 and client.dispatched[0][0] == PRISM


def test_late_prism_hold_does_not_starve_ready_youtube(tmp_path, watchdog):
    now = datetime.fromisoformat("2026-10-14T14:30:00+09:00")
    a = run_record("prism", run_id=10, conclusion="failure")
    b = run_record("prism", run_id=11, conclusion="failure")
    client = Client({PRISM: [a, b]}, {i: [build("prism", collection="failure", stamp="skipped", conclusion="failure")]
                                   for i in (10, 11)})
    recover(tmp_path, watchdog, client, now=now)
    assert len(client.dispatched) == 1 and client.dispatched[0][0] == YT


@pytest.mark.parametrize("error", [None, TimeoutError("secret-token in transport error")])
def test_unknown_or_accepted_dispatch_never_repeats_without_visible_run(tmp_path, watchdog, error):
    client = Client()
    client.error = error
    first = recover(tmp_path, watchdog, client)
    later = recover(tmp_path, watchdog, client, now=NOW + timedelta(hours=3))
    assert len(client.dispatched) == 1
    assert later[0]["status"] == "ADVISORY_DISPATCH_UNRESOLVED"
    assert "secret-token" not in json.dumps(first) + json.dumps(later)
    assert "secret-token" not in (tmp_path / "state" / "advisory-recovery" / "admission.json").read_text()


def test_visible_run_admission_retains_active_ownership(tmp_path, watchdog):
    client = Client()
    recover(tmp_path, watchdog, client)
    client.runs[YT] = [run_record(status="queued", conclusion=None, created=NOW)]
    result = recover(tmp_path, watchdog, client, now=NOW + timedelta(hours=2))
    assert result == [{"target": "youtube-daily", "status": "ADVISORY_ACTIVE", "run_id": 10}]
    assert len(client.dispatched) == 1


@pytest.mark.parametrize("surface", ["youtube", "prism"])
def test_jobless_native_advisory_blocks_other_surface(tmp_path, watchdog, surface):
    run = run_record(surface, status="queued", conclusion=None)
    run["event"], run["display_title"] = "schedule", "native"
    client = Client({recovery.SPECS[surface][0]: [run]})
    assert recover(tmp_path, watchdog, client)[0]["status"] == "ADVISORY_ACTIVE"
    assert not client.dispatched


def test_green_gate_is_not_collection_or_failure_budget_reset(tmp_path, watchdog):
    client = Client({YT: [run_record()]}, {10: [build(collection="skipped", stamp="skipped")]})
    assert recover(tmp_path, watchdog, client)[-1]["status"] == "ADVISORY_DISPATCH_ACCEPTED"


@pytest.mark.parametrize("surface", ["youtube", "prism"])
def test_successful_canonical_collection_covers_local_skipped_deploy(tmp_path, monkeypatch, watchdog, surface):
    monkeypatch.delenv(recovery.SPECS[surface][4], raising=False)
    write_manifest(tmp_path / "archive", surface)
    workflow = recovery.SPECS[surface][0]
    client = Client({workflow: [run_record(surface)]}, {10: [build(surface), {"name": "deploy", "conclusion": "skipped"}]})
    targets = [target for target in watchdog.due_targets(NOW) if target.workflow_file == workflow]
    assert recover(tmp_path, watchdog, client, targets=targets)[0]["status"] == "ADVISORY_COVERED_OR_HELD"
    assert not client.dispatched


def test_no_signal_prism_success_covers_recovery_without_duplicate_dispatch(tmp_path, monkeypatch, watchdog):
    monkeypatch.delenv(recovery.SPECS["prism"][4], raising=False)
    path = write_manifest(tmp_path / "archive", "prism")
    value = json.loads(path.read_text())
    value.update(summary={"messages": 5, "signals": 0, "warnings": 1},
                 warnings=["telegram_no_ticker_level_signals_found"])
    path.write_text(json.dumps(value), encoding="utf-8")
    before = path.read_bytes()
    client = Client({PRISM: [run_record("prism")]},
                    {10: [build("prism"), {"name": "deploy", "conclusion": "skipped"}]})
    targets = [target for target in watchdog.due_targets(NOW) if target.workflow_file == PRISM]
    assert recovery.has_unbound_completion(tmp_path / "archive", targets[0], NOW)
    assert recover(tmp_path, watchdog, client, targets=targets)[0]["status"] == "ADVISORY_COVERED_OR_HELD"
    assert not client.dispatched and path.read_bytes() == before


@pytest.mark.parametrize("surface", ["youtube", "prism"])
@pytest.mark.parametrize("end_offset,expected", [(".117583", "ADVISORY_COVERED_OR_HELD"),
                                                 (".999999", "ADVISORY_COVERED_OR_HELD"),
                                                 ("+1", "ADVISORY_DIAGNOSTIC_REQUIRED")])
def test_canonical_completion_matches_only_the_github_end_second(
        tmp_path, monkeypatch, watchdog, surface, end_offset, expected):
    monkeypatch.delenv(recovery.SPECS[surface][4], raising=False)
    path = write_manifest(tmp_path / "archive", surface)
    value = json.loads(path.read_text())
    end = "2026-10-14T08:10:01+09:00" if end_offset == "+1" else f"2026-10-14T08:10:00{end_offset}+09:00"
    value["finished_at"] = end
    path.write_text(json.dumps(value), encoding="utf-8")
    workflow = recovery.SPECS[surface][0]
    client = Client({workflow: [run_record(surface)]}, {10: [build(surface), {"name": "deploy", "conclusion": "skipped"}]})
    targets = [target for target in watchdog.due_targets(NOW) if target.workflow_file == workflow]
    assert recover(tmp_path, watchdog, client, targets=targets)[0]["status"] == expected
    assert not client.dispatched


@pytest.mark.parametrize("canonical_exists,stamp,conclusion", [(False, "success", "success"), (True, "failure", "failure"),
                                                               (True, "skipped", "success")])
def test_collection_success_with_missing_canonical_or_publication_requires_diagnosis_not_reanalysis(
        tmp_path, monkeypatch, watchdog, canonical_exists, stamp, conclusion):
    monkeypatch.delenv(recovery.SPECS["youtube"][4], raising=False)
    if canonical_exists:
        write_manifest(tmp_path / "archive")
    client = Client({YT: [run_record(conclusion=conclusion)]}, {10: [build(stamp=stamp, conclusion=conclusion)]})
    result = recover(tmp_path, watchdog, client)
    assert result[0]["status"] == "ADVISORY_DIAGNOSTIC_REQUIRED"
    assert result[-1]["status"] == "ADVISORY_DISPATCH_ACCEPTED"
    assert len(client.dispatched) == 1 and client.dispatched[0][0] == PRISM


def test_native_and_local_same_cause_failures_share_watchdog_budget(tmp_path, watchdog):
    a = run_record(run_id=10, conclusion="failure")
    a["event"], a["display_title"] = "schedule", "[recovery_source=native]"
    b = run_record(run_id=11, conclusion="failure")
    client = Client({YT: [a, b]}, {10: [build(collection="failure", stamp="skipped", conclusion="failure")],
                                  11: [build(collection="failure", stamp="skipped", conclusion="failure")]})
    targets = [target for target in watchdog.due_targets(NOW) if target.workflow_file == YT]
    result = recover(tmp_path, watchdog, client, targets=targets)
    assert "Retry budget exhausted" in result[0]["reason"]
    assert not client.dispatched


def test_receipt_cooldown_and_session_cap_survive_terminal_gate_runs(tmp_path, watchdog):
    client = Client()
    targets = [target for target in watchdog.due_targets(NOW) if target.workflow_file == YT]
    recover(tmp_path, watchdog, client, targets=targets)
    client.runs[YT] = [run_record(created=NOW)]
    client.jobs[10] = [build(collection="skipped", stamp="skipped")]
    assert recover(tmp_path, watchdog, client, now=NOW + timedelta(minutes=59), targets=targets)[0]["status"] == "ADVISORY_RETRY_BUDGET_OR_COOLDOWN"
    recover(tmp_path, watchdog, client, now=NOW + timedelta(hours=1), targets=targets)
    client.runs[YT].append(run_record(run_id=11, created=NOW + timedelta(hours=1)))
    client.jobs[11] = [build(collection="skipped", stamp="skipped")]
    assert recover(tmp_path, watchdog, client, now=NOW + timedelta(hours=2), targets=targets)[0]["status"] == "ADVISORY_RETRY_BUDGET_OR_COOLDOWN"
    assert len(client.dispatched) == 2


def test_corrupt_admission_is_preserved_and_prevents_dispatch(tmp_path, watchdog):
    path = tmp_path / "state" / "advisory-recovery" / "admission.json"
    path.parent.mkdir(parents=True)
    path.write_text("corrupt evidence")
    client = Client()
    assert recover(tmp_path, watchdog, client)[-1]["reason_code"] == "RECEIPT_INVALID"
    assert path.read_text() == "corrupt evidence" and not client.dispatched


def test_dry_run_does_not_create_receipts_or_dispatch(tmp_path, watchdog):
    client = Client()
    assert recover(tmp_path, watchdog, client, dry_run=True)[0]["status"] == "ADVISORY_DUE"
    assert not (tmp_path / "state").exists() and not client.dispatched


def test_truncated_history_fails_closed(tmp_path, watchdog):
    client = Client({YT: [run_record(run_id=n) for n in range(50)]})
    assert recover(tmp_path, watchdog, client)[-1]["status"] == "ADVISORY_DIAGNOSTIC_REQUIRED"
    assert not client.dispatched


@pytest.mark.parametrize("dry_run", [False, True])
def test_core_due_never_calls_advisory_api_or_dispatches_on_same_tick(tmp_path, monkeypatch, watchdog, dry_run):
    monkeypatch.setattr(local, "require_storage_headroom", lambda *paths: None)
    from tradingagents.scheduled import runner
    targets = watchdog.due_targets(NOW)
    monkeypatch.setattr(local, "script", lambda _: SimpleNamespace(due_targets=lambda *a, **kw: targets))
    monkeypatch.setattr(runner, "_iter_run_manifests_desc", lambda _, **kwargs: [])
    monkeypatch.setattr(local, "preflight", lambda _: None)
    monkeypatch.setattr(local.subprocess, "run", lambda *a, **kw: SimpleNamespace(returncode=0))
    monkeypatch.setattr(recovery, "recover_due", lambda *a, **kw: pytest.fail("Advisory API on core tick"))
    result = local.run_due(tmp_path / "archive", tmp_path / "state", now=NOW, dry_run=dry_run)
    assert any(item["target"] == "daily-codex-kr" and item["status"] == "DUE" for item in result)


def test_idle_api_exception_does_not_queue_core_failure(tmp_path, monkeypatch, watchdog):
    from tradingagents.scheduled import runner
    from tradingagents.notifications import local as notification
    targets = [target for target in watchdog.due_targets(NOW) if target.workflow_file in recovery.WORKFLOWS]
    monkeypatch.setattr(local, "script", lambda _: SimpleNamespace(due_targets=lambda *a, **kw: targets))
    monkeypatch.setattr(runner, "_iter_run_manifests_desc", lambda _, **kwargs: [])
    monkeypatch.setattr(recovery, "create_client", lambda _: (_ for _ in ()).throw(OSError("secret auth")))
    monkeypatch.setattr(notification, "queue_failure", lambda *a, **kw: pytest.fail("Core failure from advisory API"))
    result = local.run_due(tmp_path / "archive", tmp_path / "state", now=NOW)
    assert result == [{"status": "ADVISORY_DIAGNOSTIC_REQUIRED", "error_type": "OSError", "reason_code": "API_OR_EVIDENCE_ERROR"}]


def test_provenance_is_accepted_by_workflows_and_watchdog(watchdog):
    from tradingagents.notifications.telegram import _workflow_recovery_source
    assert watchdog._run_recovery_source(run_record()) == "local_watchdog"
    assert _workflow_recovery_source(event="workflow_dispatch", display_title=run_record()["display_title"]) == "local_watchdog"
    for workflow in recovery.WORKFLOWS:
        body = yaml.safe_load((local.ROOT / ".github" / "workflows" / workflow).read_text(encoding="utf-8"))
        on = body.get("on", body.get(True))
        assert "local_watchdog" in on["workflow_dispatch"]["inputs"]["recovery_source"]["options"]
        assert "vars.TRADINGAGENTS_AUTOMATION_BACKEND != 'local'" in body["jobs"]["deploy"]["if"]


def test_unrelated_old_corrupt_manifest_does_not_block_current_coverage(tmp_path, monkeypatch, watchdog):
    monkeypatch.delenv(recovery.SPECS["youtube"][4], raising=False)
    archive = tmp_path / "archive"
    current = write_manifest(archive)
    old = current.parent.parent / "youtube_20261001_080000" / "youtube_run.json"
    old.parent.mkdir()
    old.write_text("old damaged evidence")
    client = Client({YT: [run_record()]}, {10: [build()]})
    targets = [target for target in watchdog.due_targets(NOW) if target.workflow_file == YT]
    assert recover(tmp_path, watchdog, client, targets=targets)[0]["status"] == "ADVISORY_COVERED_OR_HELD"
    assert old.read_text() == "old damaged evidence" and not client.dispatched


def test_same_day_unrelated_corrupt_manifest_is_not_opened(tmp_path, monkeypatch, watchdog):
    monkeypatch.delenv(recovery.SPECS["youtube"][4], raising=False)
    archive = tmp_path / "archive"
    current = write_manifest(archive)
    old = current.parent.parent / "youtube_20261014_060000" / "youtube_run.json"
    old.parent.mkdir()
    old.write_text("same day damaged evidence")
    client = Client({YT: [run_record()]}, {10: [build()]})
    targets = [target for target in watchdog.due_targets(NOW) if target.workflow_file == YT]
    assert recover(tmp_path, watchdog, client, targets=targets)[0]["status"] == "ADVISORY_COVERED_OR_HELD"
    assert old.read_text() == "same day damaged evidence" and not client.dispatched


def test_old_run_active_rerun_cannot_be_excluded_by_creation_window(tmp_path, watchdog):
    run = run_record(created=NOW - timedelta(days=2), status="in_progress", conclusion=None)
    run["run_attempt"] = 2
    client = Client({YT: [run]})
    assert recover(tmp_path, watchdog, client) == [{"status": "ADVISORY_ACTIVE", "run_ids": [10]}]
    assert not client.dispatched


def test_target_receipt_corruption_is_preserved_while_other_surface_recovers(tmp_path, watchdog):
    import hashlib
    target = next(target for target in watchdog.due_targets(NOW) if target.workflow_file == YT)
    key = hashlib.sha256(f"{target.name}:{target.window_start_kst.isoformat()}".encode()).hexdigest()
    path = tmp_path / "state" / "advisory-recovery" / "attempts" / f"{key}.json"
    path.parent.mkdir(parents=True)
    path.write_text('{"attempts":{}}')
    client = Client()
    result = recover(tmp_path, watchdog, client)
    assert result[0]["reason_code"] == "RECEIPT_INVALID"
    assert result[1]["status"] == "ADVISORY_DISPATCH_ACCEPTED"
    assert client.dispatched[0][0] == PRISM
    assert path.read_text() == '{"attempts":{}}'


@pytest.mark.parametrize("bad", [None, {}, [], {"status": "TERMINAL"}, {"attempts": {}}])
def test_structurally_invalid_receipts_are_not_replaced(tmp_path, watchdog, bad):
    root = tmp_path / "state" / "advisory-recovery"
    root.mkdir(parents=True)
    path = root / "admission.json"
    original = json.dumps(bad)
    path.write_text(original)
    client = Client()
    assert recover(tmp_path, watchdog, client)[0]["status"] == "ADVISORY_DIAGNOSTIC_REQUIRED"
    assert not client.dispatched and path.read_text() == original


def test_future_running_manifest_cannot_break_completed_collection(tmp_path, monkeypatch, watchdog):
    monkeypatch.delenv(recovery.SPECS["youtube"][4], raising=False)
    archive = tmp_path / "archive"
    current = write_manifest(archive)
    future = current.parent.parent / "youtube_20261014_100000" / "youtube_run.json"
    future.parent.mkdir()
    future.write_text(json.dumps({"started_at": "2026-10-14T10:00:00+09:00", "finished_at": None}))
    client = Client({YT: [run_record()]}, {10: [build()]})
    targets = [target for target in watchdog.due_targets(NOW) if target.workflow_file == YT]
    assert recover(tmp_path, watchdog, client, targets=targets)[0]["status"] == "ADVISORY_COVERED_OR_HELD"
    assert not client.dispatched


def test_failure_budget_is_not_reset_by_later_green_gate(tmp_path, watchdog):
    runs = [run_record(run_id=10, conclusion="failure"), run_record(run_id=11, conclusion="failure"),
            run_record(run_id=12, created=NOW - timedelta(minutes=10))]
    jobs = {run_id: [build(collection="failure", stamp="skipped", conclusion="failure")] for run_id in (10, 11)}
    jobs[12] = [build(collection="skipped", stamp="skipped")]
    client = Client({YT: runs}, jobs)
    targets = [target for target in watchdog.due_targets(NOW) if target.workflow_file == YT]
    assert "Retry budget exhausted" in recover(tmp_path, watchdog, client, targets=targets)[0]["reason"]
    assert not client.dispatched


def test_active_queries_have_no_created_filter_and_preserve_old_rerun(monkeypatch, watchdog):
    monkeypatch.setattr(recovery.subprocess, "run", lambda *a, **kw: SimpleNamespace(stdout="captured-token"))
    paths = []
    old = run_record(created=NOW - timedelta(days=2), status="in_progress", conclusion=None)
    def request(self, method, path, **kw):
        paths.append(path)
        return {"total_count": 1, "workflow_runs": [old]} if "status=in_progress" in path else {"total_count": 0, "workflow_runs": []}
    monkeypatch.setattr(watchdog.GitHubActionsClient, "_request", request)
    client = recovery.create_client(watchdog)
    assert client.list_active_runs() == [old]
    assert len(paths) == 5 and all("created" not in path for path in paths)


def test_truncated_active_history_never_implies_idle(monkeypatch, watchdog):
    monkeypatch.setattr(recovery.subprocess, "run", lambda *a, **kw: SimpleNamespace(stdout="captured-token"))
    monkeypatch.setattr(watchdog.GitHubActionsClient, "_request", lambda *a, **kw: {"total_count": 101, "workflow_runs": []})
    with pytest.raises(recovery.RecoveryDiagnostic, match="ACTIVE_HISTORY_TRUNCATED"):
        recovery.create_client(watchdog).list_active_runs()


def test_failed_durable_admission_write_prevents_network_mutation(tmp_path, monkeypatch, watchdog):
    monkeypatch.setattr(recovery, "atomic_write_json", lambda *a, **kw: (_ for _ in ()).throw(OSError("disk write denied")))
    client = Client()
    assert recover(tmp_path, watchdog, client)[-1]["status"] == "ADVISORY_DIAGNOSTIC_REQUIRED"
    assert not client.dispatched


def test_custom_source_success_cannot_cover_or_block_default_recovery(tmp_path, watchdog):
    run = run_record()
    run["display_title"] += " [request_scope=custom_sources]"
    client = Client({YT: [run]}, {10: [build()]})
    targets = [target for target in watchdog.due_targets(NOW) if target.workflow_file == YT]
    assert recover(tmp_path, watchdog, client, targets=targets)[0]["status"] == "ADVISORY_DISPATCH_ACCEPTED"


def test_new_complete_producer_is_not_blocked_by_superseded_missing_manifest(tmp_path, monkeypatch, watchdog):
    monkeypatch.delenv(recovery.SPECS["youtube"][4], raising=False)
    write_manifest(tmp_path / "archive")
    older = build()
    older["steps"][0].update(started_at="2026-10-14T06:00:00+09:00", completed_at="2026-10-14T06:10:00+09:00")
    client = Client({YT: [run_record(run_id=9, created=NOW - timedelta(hours=3)), run_record()]},
                    {9: [older], 10: [build()]})
    targets = [target for target in watchdog.due_targets(NOW) if target.workflow_file == YT]
    assert recover(tmp_path, watchdog, client, targets=targets)[0]["status"] == "ADVISORY_COVERED_OR_HELD"
    assert not client.dispatched


@pytest.mark.parametrize("surface", ["youtube", "prism"])
def test_old_created_run_completed_today_prevents_recollection_when_api_history_excludes_it(tmp_path, monkeypatch, watchdog, surface):
    monkeypatch.delenv(recovery.SPECS[surface][4], raising=False)
    write_manifest(tmp_path / "archive", surface)
    workflow = recovery.SPECS[surface][0]
    old = run_record(surface, created=NOW - timedelta(days=2))
    old["run_attempt"] = 2
    class FilteredClient(Client):
        def list_runs(self, workflow, *, created_since_utc):
            return [run for run in self.runs.get(workflow, []) if recovery.timestamp(run["created_at"]) >= created_since_utc]
    client = FilteredClient({workflow: [old]}, {10: [build(surface)]})
    targets = [target for target in watchdog.due_targets(NOW) if target.workflow_file == workflow]
    result = recover(tmp_path, watchdog, client, targets=targets)
    assert result[0]["reason_code"] == "CANONICAL_COMPLETE_PRODUCER_UNRESOLVED"
    assert not client.dispatched


def test_unbound_custom_canonical_does_not_cover_default_sources(tmp_path, monkeypatch, watchdog):
    monkeypatch.delenv(recovery.SPECS["youtube"][4], raising=False)
    path = write_manifest(tmp_path / "archive")
    value = json.loads(path.read_text())
    value["channel_urls"] = ["https://www.youtube.com/@custom/videos"]
    path.write_text(json.dumps(value))
    targets = [target for target in watchdog.due_targets(NOW) if target.workflow_file == YT]
    client = Client()
    assert recover(tmp_path, watchdog, client, targets=targets)[0]["status"] == "ADVISORY_DISPATCH_ACCEPTED"
