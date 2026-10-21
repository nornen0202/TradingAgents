from datetime import datetime, timedelta
import json
from pathlib import Path

import pytest

from tradingagents.execution import refresh_runtime as refresh
from tests.execution.test_paper_runtime import source


AT = datetime.fromisoformat("2026-10-19T10:00:00+09:00")


def enable(state):
    path = state / "paper/enabled.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"enabled": True, "mode": "LOCAL_PAPER_ONLY", "real_orders_enabled": False}))


def open_kr(**kwargs):
    return {"is_open": kwargs["market"] == "kr"}


def test_expired_source_causes_new_observation_not_renewal_and_uses_existing_consumer(tmp_path, monkeypatch):
    from tradingagents import local_automation
    monkeypatch.setattr(local_automation, "require_storage_headroom", lambda *a: None)
    archive, state = tmp_path / "archive", tmp_path / "state"
    enable(state)
    run = source(archive, AT - timedelta(minutes=20))
    originals = {str(p): p.read_bytes() for p in run.rglob("*.json")}
    calls = []
    def execute(config, **kwargs):
        calls.append((config, kwargs))
        return {"status": "success", "run_id": "new-observations"}
    result = refresh.refresh_due(archive, state, now=AT, clock=lambda: AT + timedelta(seconds=80),
        session_resolver=open_kr, executor=execute)
    assert result == [{"target": "execution-freshness-kr", "status": "COMPLETED"}]
    config, args = calls[0]
    assert config.run.run_mode == "overlay_only"
    assert config.execution.execution_selective_rerun_enabled is False
    assert config.execution.execution_session_gate_enabled is True
    assert config.execution.execution_refresh_checkpoints_local == ("10:00",)
    assert args["paper_state_dir"] == state
    assert config.storage.archive_dir == archive
    assert all(Path(p).read_bytes() == contents for p, contents in originals.items())
    assert refresh.refresh_due(archive, state, now=AT + timedelta(minutes=1),
        session_resolver=open_kr, executor=lambda *a, **k: pytest.fail("no duplicate producer"))[0]["status"] == "REFRESH_COOLDOWN"


@pytest.mark.parametrize("age,expected", [(119, False), (120, True), (600, True)])
def test_refresh_boundary_is_shorter_than_unchanged_consumer_expiry(tmp_path, age, expected):
    archive, state = tmp_path / "archive", tmp_path / "state"
    enable(state)
    source(archive, AT - timedelta(seconds=age))
    result = refresh.refresh_due(archive, state, now=AT, dry_run=True, session_resolver=open_kr)
    assert bool(result) is expected
    assert not (state / "execution-refresh").exists()


@pytest.mark.parametrize("bad", [None, "bad", "2026-10-19T10:00:00", "2026-10-19T10:01:00+09:00"])
def test_unverifiable_or_future_bundle_is_never_reused(tmp_path, bad):
    archive, state = tmp_path / "archive", tmp_path / "state"
    enable(state)
    run = source(archive, AT - timedelta(minutes=1))
    p = run / "decision_bundle_v2.json"
    d = json.loads(p.read_text())
    d['generated_at'] = bad
    p.write_text(json.dumps(d))
    assert refresh.refresh_due(archive, state, now=AT, dry_run=True, session_resolver=open_kr)[0]['status'] == 'DUE'


def test_no_implicit_enable_and_no_closed_market_fetch(tmp_path):
    assert refresh.refresh_due(tmp_path, tmp_path, now=AT,
        session_resolver=lambda **k: pytest.fail("disabled")) == []
    enable(tmp_path)
    assert refresh.refresh_due(tmp_path, tmp_path, now=AT,
        session_resolver=lambda **k: {"is_open": False},
        executor=lambda *a, **k: pytest.fail("closed")) == []


def test_failure_budget_and_us_session_day_across_kst_midnight(tmp_path, monkeypatch):
    from tradingagents import local_automation
    monkeypatch.setattr(local_automation, "require_storage_headroom", lambda *a: None)
    enable(tmp_path)
    at = datetime.fromisoformat("2026-10-20T00:00:00+09:00")
    def fail(*a, **k):
        raise RuntimeError("private broker context must not escape")
    for minute in (0, 5, 10):
        now = at + timedelta(minutes=minute)
        result = refresh.refresh_due(tmp_path, tmp_path, now=now, clock=lambda: now,
            session_resolver=lambda **k: {"is_open": k['market'] == 'us'}, executor=fail)
        assert result[0]['status'] == 'FAILED'
    p = tmp_path / 'execution-refresh/us.json'
    assert 'private broker' not in p.read_text()
    assert json.loads(p.read_text())['session_date'] == '2026-10-19'
    assert refresh.refresh_due(tmp_path, tmp_path, now=at + timedelta(minutes=15),
        session_resolver=lambda **k: {"is_open": k['market'] == 'us'}, executor=fail)[0]['status'] == 'REFRESH_RETRY_LIMIT'


def test_existing_producer_calls_refresh_before_advisory_recovery(tmp_path, monkeypatch):
    from types import SimpleNamespace
    from tradingagents import local_automation as local, local_advisory_recovery
    from tradingagents.scheduled import runner
    monkeypatch.setattr(local, 'script', lambda _: SimpleNamespace(due_targets=lambda *a, **k: []))
    monkeypatch.setattr(runner, '_iter_run_manifests_desc', lambda _: [])
    monkeypatch.setattr(refresh, 'refresh_due', lambda *a, **k: [{'target': 'execution-freshness-kr', 'status': 'COMPLETED'}])
    monkeypatch.setattr(local_advisory_recovery, 'recover_due', lambda *a, **k: pytest.fail('freshness gets priority'))
    assert local.run_due(tmp_path, tmp_path, now=AT)[0]['status'] == 'COMPLETED'


@pytest.mark.parametrize("status,seconds,expected", [
    ("COMPLETED", 299.7, "DUE"),
    ("COMPLETED", 240, "REFRESH_COOLDOWN"),
    ("FAILED", 299.7, "REFRESH_COOLDOWN"),
    ("STARTED", 299.7, "REFRESH_COOLDOWN"),
    ("FAILED", 300, "DUE"),
    ("COMPLETED", -1, "REFRESH_COOLDOWN"),
])
def test_scheduled_launch_jitter_does_not_skip_successful_next_slot(tmp_path, status, seconds, expected):
    archive, state = tmp_path / "archive", tmp_path / "state"
    enable(state)
    started = AT + timedelta(minutes=5, seconds=4.858298)
    source(archive, started + timedelta(seconds=103))
    p = state / "execution-refresh/kr.json"
    p.parent.mkdir()
    p.write_text(json.dumps({"started_at": started.isoformat(), "session_date": started.date().isoformat(),
                            "status": status, "consecutive_failures": 0 if status == "COMPLETED" else 1}))
    result = refresh.refresh_due(archive, state, now=started + timedelta(seconds=seconds),
                                 dry_run=True, session_resolver=open_kr)
    assert result[0]["status"] == expected


def test_next_slot_still_waits_for_actual_source_age(tmp_path):
    archive, state = tmp_path / "archive", tmp_path / "state"
    enable(state)
    started = AT + timedelta(minutes=4, seconds=50)
    source(archive, started + timedelta(seconds=30))
    p = state / "execution-refresh/kr.json"
    p.parent.mkdir()
    p.write_text(json.dumps({"started_at": started.isoformat(), "session_date": started.date().isoformat(),
                            "status": "COMPLETED", "consecutive_failures": 0}))
    assert refresh.refresh_due(archive, state, now=started + timedelta(seconds=60),
                               dry_run=True, session_resolver=open_kr) == []


@pytest.mark.parametrize("observed,expected", [
    ((AT - timedelta(seconds=119)).isoformat(), False),
    ((AT - timedelta(seconds=120)).isoformat(), True),
    ((AT - timedelta(seconds=300)).isoformat(), True),
    ((AT + timedelta(seconds=1)).isoformat(), True),
    (None, True), ("bad", True), ("2026-10-19T09:59:00", True),
])
def test_recent_publication_does_not_renew_original_quote(tmp_path, observed, expected):
    archive, state = tmp_path / "archive", tmp_path / "state"
    enable(state)
    run = source(archive, AT - timedelta(seconds=30))
    path = run / "decision_bundle_v2.json"
    bundle = json.loads(path.read_text())
    bundle["strategy_table"][0]["market_data_asof"] = observed
    path.write_text(json.dumps(bundle))
    originals = {p: p.read_bytes() for p in run.rglob("*.json")}
    result = refresh.refresh_due(archive, state, now=AT, dry_run=True, session_resolver=open_kr)
    assert bool(result) is expected
    assert all(p.read_bytes() == value for p, value in originals.items())
    assert not (state / "execution-refresh").exists()


@pytest.mark.parametrize("rows", [None, [], {}, [None], [{}], [{"market_data_asof": None}]])
def test_missing_observations_do_not_suppress_refresh(tmp_path, rows):
    archive, state = tmp_path / "archive", tmp_path / "state"
    enable(state)
    run = source(archive, AT - timedelta(seconds=30))
    path = run / "decision_bundle_v2.json"
    bundle = json.loads(path.read_text())
    bundle["strategy_table"] = rows
    path.write_text(json.dumps(bundle))
    assert refresh.refresh_due(archive, state, now=AT, dry_run=True, session_resolver=open_kr)[0]["status"] == "DUE"


@pytest.mark.parametrize("prior_status,seconds,expected", [
    ("COMPLETED", 299.7, "DUE"),
    ("COMPLETED", 240, "REFRESH_COOLDOWN"),
    ("STARTED", 299.7, "REFRESH_COOLDOWN"),
    ("FAILED", 299.7, "REFRESH_COOLDOWN"),
    ("FAILED", 300, "DUE"),
])
def test_late_publication_mixed_clocks_keep_original_attempt_limits(tmp_path, prior_status, seconds, expected):
    archive, state = tmp_path / "archive", tmp_path / "state"
    enable(state)
    started = AT + timedelta(seconds=5)
    now = started + timedelta(seconds=seconds)
    run = source(archive, now - timedelta(seconds=55))
    path = run / "decision_bundle_v2.json"
    bundle = json.loads(path.read_text())
    # One fresh row cannot hide another expired row, even with no executable signal.
    bundle["strategy_table"].append({"ticker": "000660.KS", "quality": {"execution_ready": False},
        "market_data_asof": (now - timedelta(seconds=180)).isoformat()})
    path.write_text(json.dumps(bundle))
    receipt = state / "execution-refresh/kr.json"
    receipt.parent.mkdir()
    receipt.write_text(json.dumps({"started_at": started.isoformat(), "session_date": started.date().isoformat(),
        "status": prior_status, "consecutive_failures": 0 if prior_status == "COMPLETED" else 1}))
    before = receipt.read_bytes()
    result = refresh.refresh_due(archive, state, now=now, dry_run=True, session_resolver=open_kr)
    assert result[0]["status"] == expected
    assert receipt.read_bytes() == before


def test_expired_observation_still_respects_failure_budget(tmp_path):
    archive, state = tmp_path / "archive", tmp_path / "state"
    enable(state)
    run = source(archive, AT - timedelta(seconds=30))
    path = run / "decision_bundle_v2.json"
    bundle = json.loads(path.read_text())
    bundle["strategy_table"][0]["market_data_asof"] = (AT - timedelta(seconds=180)).isoformat()
    path.write_text(json.dumps(bundle))
    receipt = state / "execution-refresh/kr.json"
    receipt.parent.mkdir()
    receipt.write_text(json.dumps({"started_at": (AT - timedelta(minutes=5)).isoformat(),
        "session_date": AT.date().isoformat(), "status": "FAILED", "consecutive_failures": 3}))
    assert refresh.refresh_due(archive, state, now=AT, dry_run=True, session_resolver=open_kr)[0]["status"] == "REFRESH_RETRY_LIMIT"
