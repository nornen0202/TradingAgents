"""Exercise the real watchdog with equivalent instants; never start workers or APIs."""
from datetime import datetime, timezone
import hashlib
import json
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest

from tradingagents import local_automation as local
from tradingagents.atomic_io import atomic_write_json


@pytest.fixture
def offline_scheduler(monkeypatch):
    from tradingagents import local_advisory_recovery
    from tradingagents.execution import refresh_runtime
    from tradingagents.scheduled import automation_calendar, runner

    seen = []
    def calendar(*, market, now):
        seen.append((market, now))
        return SimpleNamespace(is_session=True)
    monkeypatch.setattr(automation_calendar, "automated_market_session_status", calendar)
    monkeypatch.setattr(runner, "_iter_run_manifests_desc", lambda _, **kwargs: [])
    monkeypatch.setattr(local, "full_research_session_hold", lambda *a, **kw: None)
    monkeypatch.setattr(refresh_runtime, "refresh_due", lambda *a, **kw: [])
    monkeypatch.setattr(local_advisory_recovery, "recover_due", lambda *a, **kw: [])
    monkeypatch.setattr(local.subprocess, "run", lambda *a, **kw: pytest.fail("Real worker launched"))
    monkeypatch.setattr(local, "preflight", lambda *a: pytest.fail("Real preflight launched"))
    return seen


@pytest.mark.parametrize("moment,expected", [
    ("2026-10-22T05:00:00+09:00", {"daily-codex-kr", "daily-codex-us"}),
    ("2026-10-22T10:14:59+09:00", {"daily-codex-kr"}),
    ("2026-10-22T10:15:00+09:00", set()),
    ("2026-10-22T17:49:59+09:00", set()),
    ("2026-10-22T17:50:00+09:00", {"daily-codex-us"}),
    ("2026-10-22T23:59:59+09:00", {"daily-codex-us"}),
    ("2026-10-23T00:00:00+09:00", {"daily-codex-us"}),
    ("2026-10-23T23:59:59+09:00", {"daily-codex-us"}),
    ("2026-10-24T00:00:00+09:00", {"daily-codex-us"}),
    ("2026-10-24T08:00:00+09:00", {"daily-codex-us"}),
    ("2026-10-24T08:00:01+09:00", set()),
])
def test_actual_watchdog_uses_same_slots_for_equivalent_instants(tmp_path, offline_scheduler, moment, expected):
    kst = datetime.fromisoformat(moment)
    observations = []
    for now in (kst, kst.astimezone(timezone.utc), kst.astimezone(ZoneInfo("America/New_York"))):
        observations.append(local.run_due(tmp_path / "archive", tmp_path / "state",
            now=now, dry_run=True, research_only=True))
    assert observations[0] == observations[1] == observations[2]
    assert {row["target"] for row in observations[0]} == expected
    assert {row["target"]: row["status"] for row in observations[0]} == {
        name: ("DEFERRED_FOR_NEXT_MARKET_RESEARCH" if name == "daily-codex-us" and "daily-codex-kr" in expected else "DUE")
        for name in expected}
    assert all(now == kst and getattr(now.tzinfo, "key", None) == "Asia/Seoul"
        for _, now in offline_scheduler)
    assert not (tmp_path / "state").exists()


@pytest.mark.parametrize("value", [datetime(2026, 10, 22, 17, 50), "2026-10-22T17:50:00+09:00", "invalid", 0, False])
def test_invalid_or_naive_scheduler_clock_fails_before_target_lookup(tmp_path, monkeypatch, value):
    monkeypatch.setattr(local, "script", lambda *a: pytest.fail("Target lookup with an invalid clock"))
    with pytest.raises(ValueError, match="Aware local automation clock required"):
        local.run_due(tmp_path / "archive", tmp_path / "state", now=value, dry_run=True)
    assert not (tmp_path / "state").exists()


def test_idle_research_tick_does_not_read_unneeded_archive(tmp_path, monkeypatch, offline_scheduler):
    from tradingagents.scheduled import runner
    monkeypatch.setattr(runner, "_iter_run_manifests_desc", lambda *a, **kw: pytest.fail("No daily target needs archive evidence"))
    now = datetime.fromisoformat("2026-10-22T12:00:00+09:00")
    assert local.run_due(tmp_path / "archive", tmp_path / "state", now=now, research_only=True) == []


def test_delegated_tick_does_not_read_unneeded_archive(tmp_path, monkeypatch, offline_scheduler):
    from tradingagents.scheduled import runner
    from tradingagents.execution import research_runtime
    monkeypatch.setattr(research_runtime, "research_lane_enabled", lambda _: True)
    monkeypatch.setattr(runner, "_iter_run_manifests_desc", lambda *a, **kw: pytest.fail("Research owner will verify its own evidence"))
    now = datetime.fromisoformat("2026-10-22T18:00:00+09:00")
    rows = local.run_due(tmp_path / "archive", tmp_path / "state", now=now, dry_run=True)
    assert rows and all(row["status"] == "DELEGATED_TO_RESEARCH_LANE" for row in rows)


def test_friday_utc_worker_uses_original_key_and_budget_after_kst_midnight(tmp_path, monkeypatch, offline_scheduler):
    from tradingagents.scheduled import config

    state = tmp_path / "state"
    session_start = "2026-10-23T17:45:00+09:00"
    key = hashlib.sha256(f"daily-codex-us:{session_start}".encode()).hexdigest()
    receipt_path = state / "attempts" / f"{key}.json"
    atomic_write_json(receipt_path, {"target": "daily-codex-us", "attempts": 3,
        "started_at": "2026-10-23T18:00:00+09:00", "exit_code": 1})
    monkeypatch.setattr(local, "preflight", lambda *a: None)
    monkeypatch.setattr(local, "require_storage_headroom", lambda *a: None)
    monkeypatch.setattr(config, "load_scheduled_config", lambda *a: SimpleNamespace(llm=SimpleNamespace(codex_workspace_dir=tmp_path)))
    calls = []
    monkeypatch.setattr(local.subprocess, "run", lambda args, **kw: calls.append(args) or SimpleNamespace(returncode=0))
    utc = datetime.fromisoformat("2026-10-23T23:59:59+09:00").astimezone(timezone.utc)
    assert local.run_due(tmp_path / "archive", state, now=utc, research_only=True) == [
        {"target": "daily-codex-us", "status": "DUE"}]
    receipt = json.loads(receipt_path.read_text())
    assert receipt["attempts"] == 4 and receipt["started_at"] == "2026-10-23T23:59:59+09:00"
    before = receipt_path.read_bytes()
    for now in (utc, utc.astimezone(ZoneInfo("Asia/Seoul")), datetime.fromisoformat("2026-10-24T00:00:00+09:00")):
        assert local.run_due(tmp_path / "archive", state, now=now, research_only=True) == [
            {"target": "daily-codex-us", "status": "RETRY_BUDGET_OR_COOLDOWN"}]
    assert receipt_path.read_bytes() == before
    assert list((state / "attempts").glob("*.json")) == [receipt_path]
    assert len(calls) == 1 and "--disable-execution-refresh" in calls[0]


@pytest.mark.parametrize("moment", ["2026-10-22T05:00:00+09:00", "2026-10-22T17:50:00+09:00"])
def test_independent_research_delegation_reaches_actual_daily_watchdog(tmp_path, offline_scheduler, moment):
    from tradingagents.execution.research_runtime import research_due

    state, archive = tmp_path / "state", tmp_path / "archive"
    atomic_write_json(state / "research-lane-enabled.json", {
        "mode": "PAPER_RESEARCH_INDEPENDENT_V1", "enabled": True, "real_orders_enabled": False})
    atomic_write_json(state / "kis-strategy/enabled.json", {"mode": "KIS_DEMO_STRATEGY", "enabled": True,
        "real_orders_enabled": False, "allocation_mode": "DEMO_NATIVE_ONE_SHARE_V1"})
    atomic_write_json(state / "actions-drained.json", {})
    before = {path: path.read_bytes() for path in state.rglob("*.json")}
    utc = datetime.fromisoformat(moment).astimezone(timezone.utc)
    delegated = local.run_due(archive, state, now=utc, dry_run=True)
    assert delegated and all(row["status"] == "DELEGATED_TO_RESEARCH_LANE" for row in delegated)
    actual = research_due(archive, state, now=utc, dry_run=True,
        executor=lambda *a, **kw: pytest.fail("Research execution in a dry run"),
        session_resolver=lambda **kw: pytest.fail("Daily research was lost before the slot lane"))
    assert actual == [{"status": "DAILY_RESEARCH_DUE", "decisions": [
        {"target": row["target"], "status": ("DEFERRED_FOR_NEXT_MARKET_RESEARCH"
         if row["target"] == "daily-codex-us" and len(delegated) == 2 else "DUE")} for row in delegated]}]
    assert {path: path.read_bytes() for path in state.rglob("*.json")} == before
    assert not (state / "attempts").exists()


@pytest.mark.parametrize("market,window",[("kr","2026-10-22T04:30:00+09:00"),("us","2026-10-21T17:45:00+09:00")])
def test_explicit_missed_daily_recovery_preserves_slot_budget_and_actual_start(tmp_path,offline_scheduler,monkeypatch,market,window):
    import hashlib,json
    from types import SimpleNamespace
    from tradingagents.scheduled import config
    now=datetime.fromisoformat("2026-10-22T15:40:00+09:00")
    state=tmp_path / "state"
    key=hashlib.sha256(f"daily-codex-{market}:{window}".encode()).hexdigest()
    path=state / "attempts" / f"{key}.json"
    atomic_write_json(path,{"attempts":2,"started_at":"2026-10-22T06:00:00+09:00","exit_code":1})
    before=path.read_bytes()
    result=local.run_due(tmp_path / "archive",state,now=now,research_only=True,dry_run=True,catch_up_market=market)
    assert result==[{"target":f"daily-codex-{market}","status":"DUE"}]
    assert path.read_bytes()==before
    monkeypatch.setattr(config,"load_scheduled_config",lambda _:SimpleNamespace(llm=SimpleNamespace(codex_workspace_dir="unused")))
    monkeypatch.setattr(local,"preflight",lambda _:None)
    monkeypatch.setattr(local,"require_storage_headroom",lambda *a:None)
    calls=[]
    monkeypatch.setattr(local.subprocess,"run",lambda args,**kw:calls.append(args) or SimpleNamespace(returncode=0))
    local.run_due(tmp_path / "archive",state,now=now,research_only=True,catch_up_market=market)
    receipt=json.loads(path.read_text())
    assert receipt["attempts"]==3 and receipt["started_at"]==now.isoformat()
    assert receipt["original_window_start"]==window and receipt["recovery"]=="MISSED_WINDOW_CATCHUP"
    assert "--disable-execution-refresh" in calls[0]
    atomic_write_json(path,{**receipt,"attempts":4})
    assert local.run_due(tmp_path / "archive",state,now=now,research_only=True,catch_up_market=market)[0]["status"]=="RETRY_BUDGET_OR_COOLDOWN"
    assert len(calls)==1


@pytest.mark.parametrize("clock,market",[("2026-10-22T09:00:00+09:00","kr"),("2026-10-22T17:45:00+09:00","us"),("2026-10-25T15:00:00+09:00","kr")])
def test_catchup_never_invents_a_new_slot(tmp_path,offline_scheduler,clock,market):
    with pytest.raises(ValueError):
        local.run_due(tmp_path / "archive",tmp_path / "state",now=datetime.fromisoformat(clock),research_only=True,catch_up_market=market)
    assert not (tmp_path / "state").exists()
