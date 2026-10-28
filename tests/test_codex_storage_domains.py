from pathlib import Path
import sys
from unittest.mock import Mock
import pytest
sys.path.insert(0, str(Path(__file__).parents[1] / "tools"))
import maintain_codex_storage_policy as policy


def configuration():
    return {"domains": [{"id": "ta"}, {"id": "repair"}, {"id": "codex"}]}


def test_failed_domain_does_not_skip_healthy_domains(monkeypatch):
    monkeypatch.setattr(policy.storage, "validate_volumes", lambda x: None)
    calls = []
    def run(domain, **kw):
        calls.append((domain["id"], kw))
        if domain["id"] == "repair": raise OSError("device absent")
        return 0
    monkeypatch.setattr(policy, "run_policy", run)
    assert policy.domain_policy(configuration(), apply=True) == 2
    assert [x[0] for x in calls] == ["ta", "repair", "codex"]
    assert all(x[1]["apply"] for x in calls)


def test_degraded_preflight_distinct_from_shared_failure(monkeypatch):
    monkeypatch.setattr(policy.storage, "validate_volumes", lambda x: None)
    monkeypatch.setattr(policy, "run_policy", lambda d, **kw: 2 if d["id"] == "repair" else 0)
    assert policy.domain_policy(configuration(), apply=False, preflight_only=True) == 3
    def fail(x): raise OSError("backup missing")
    monkeypatch.setattr(policy.storage, "validate_volumes", fail)
    assert policy.domain_policy(configuration(), apply=False, preflight_only=True) == 2


def test_shared_failure_blocks_all_mutations(monkeypatch):
    def fail(x): raise OSError("backup missing")
    monkeypatch.setattr(policy.storage, "validate_volumes", fail)
    run = Mock(return_value=0)
    monkeypatch.setattr(policy, "run_policy", run)
    assert policy.domain_policy(configuration(), apply=True) == 2
    assert all(not call.kwargs["apply"] and call.kwargs["preflight_only"] for call in run.call_args_list)


def test_duplicate_mutation_roots_refused_before_writes(monkeypatch, tmp_path):
    monkeypatch.setattr(policy.storage, "validate_volumes", lambda x: None)
    cfg = configuration()
    for d in cfg["domains"]: d["workers"] = [{"root":str(tmp_path)}]
    run = Mock()
    monkeypatch.setattr(policy, "run_policy", run)
    with pytest.raises(ValueError, match="Duplicate"): policy.domain_policy(cfg, apply=True)
    run.assert_not_called()


def test_dry_run_never_creates_health_receipt(monkeypatch, tmp_path):
    monkeypatch.setattr(policy.storage, "validate_volumes", lambda x: None)
    monkeypatch.setattr(policy, "run_policy", lambda *a, **kw: 0)
    cfg = configuration();cfg["health_receipt"] = str(tmp_path/"absent"/"health.json")
    assert policy.domain_policy(cfg, apply=False) == 0
    assert not (tmp_path/"absent").exists()


def test_apply_health_tracks_failure_and_recovery(monkeypatch, tmp_path):
    monkeypatch.setattr(policy.storage, "validate_volumes", lambda x: None)
    monkeypatch.setattr(policy, "run_policy", lambda d, **kw: 2 if d["id"] == "repair" else 0)
    import json
    cfg = configuration();cfg["health_receipt"] = str(tmp_path/"health.json")
    policy.domain_policy(cfg, apply=True);policy.domain_policy(cfg, apply=True)
    assert json.loads(Path(cfg["health_receipt"]).read_text())["consecutive_failed_runs"] == 2
    monkeypatch.setattr(policy, "run_policy", lambda *a, **kw: 0)
    policy.domain_policy(cfg, apply=True)
    r=json.loads(Path(cfg["health_receipt"]).read_text())
    assert r["healthy"] and r["alert_state_changed"] and r["consecutive_failed_runs"] == 0


def test_worker_manifest_discovery_ignores_unrelated_archive_runs(tmp_path):
    import json
    archive = tmp_path/"runs"
    for name in ("wanted", "unrelated"):
        p=archive/"2026"/name/"run.json";p.parent.mkdir(parents=True)
        p.write_text(json.dumps({"status":"success","finished_at":"2026-10-01T00:00:00+00:00","run_id":name}))
    assert set(policy.completed_runs([str(archive)], {"wanted"})) == {"wanted"}
    assert policy.completed_runs([str(archive)], set()) == {}


def test_health_only_can_save_receipt_without_running_retention(monkeypatch, tmp_path):
    import json
    monkeypatch.setattr(policy.storage, "validate_volumes", lambda x: None)
    run = Mock(return_value=0)
    monkeypatch.setattr(policy, "run_policy", run)
    cfg=configuration();cfg["health_receipt"]=str(tmp_path/"health.json")
    assert policy.domain_policy(cfg, apply=True, health_only=True) == 0
    assert all(call.kwargs["preflight_only"] for call in run.call_args_list)
    assert json.loads(Path(cfg["health_receipt"]).read_text())["mode"] == "health-only"
