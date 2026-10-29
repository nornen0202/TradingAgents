"""An active execution session must not lose its producer to another market's research."""
import hashlib
import json
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

from tradingagents import local_advisory_recovery, local_automation as local
from tradingagents.execution import paper_runtime, refresh_runtime
from tradingagents.scheduled import config, runner


NOW = datetime.fromisoformat("2026-10-21T04:45:00+09:00")


def enable(state, lane="kis-strategy", **changes):
    mode = "KIS_DEMO_STRATEGY" if lane == "kis-strategy" else "LOCAL_PAPER_ONLY"
    path = state / lane / "enabled.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"enabled": True, "mode": mode,
                                "real_orders_enabled": False, **changes}), encoding="utf-8")


def target(profile="kr", mode="full"):
    return SimpleNamespace(
        name=f"daily-codex-{profile}" if mode == "full" else f"intraday-overlay-{profile}",
        workflow_file="daily-codex-analysis.yml" if mode == "full" else "intraday-overlay-refresh.yml",
        inputs={"profile": profile}, window_start_kst=NOW.replace(hour=4, minute=30),
        max_failed_attempts=4,
    )


def receipt_path(state, item):
    key = hashlib.sha256(f"{item.name}:{item.window_start_kst.isoformat()}".encode()).hexdigest()
    return state / "attempts" / f"{key}.json"


def wire(monkeypatch, item, *, refreshes=()):
    calls = {"workers": [], "preflights": [], "refreshes": []}
    monkeypatch.setattr(local, "script", lambda _: SimpleNamespace(due_targets=lambda *a, **k: [item]))
    monkeypatch.setattr(runner, "_iter_run_manifests_desc", lambda _, **kwargs: [])
    monkeypatch.setattr(local, "require_storage_headroom", lambda *a: None)
    monkeypatch.setattr(local, "preflight", lambda path: calls["preflights"].append(path))
    monkeypatch.setattr(config, "load_scheduled_config", lambda _: SimpleNamespace(
        llm=SimpleNamespace(codex_workspace_dir="unused")))
    monkeypatch.setattr(local.subprocess, "run", lambda args, **kw:
                        calls["workers"].append(args) or SimpleNamespace(returncode=0))
    monkeypatch.setattr(refresh_runtime, "refresh_due", lambda *a, **kw:
                        calls["refreshes"].append(kw) or list(refreshes))
    monkeypatch.setattr(local_advisory_recovery, "recover_due", lambda *a, **kw:
                        pytest.fail("advisory work must not occupy a deferred execution session"))
    return calls


@pytest.mark.parametrize("lane", ["paper", "kis-strategy"])
def test_refresh_enabled_requires_explicit_safe_configuration(tmp_path, lane):
    assert refresh_runtime.execution_refresh_enabled(tmp_path) is False
    enable(tmp_path, lane)
    assert refresh_runtime.execution_refresh_enabled(tmp_path) is True
    for changes in ({"real_orders_enabled": True}, {"real_orders_enabled": None},
                    {"enabled": False}, {"mode": "LIVE"}):
        enable(tmp_path, lane, **changes)
        assert refresh_runtime.execution_refresh_enabled(tmp_path) is False


@pytest.mark.parametrize("profile,other", [("kr", "us"), ("us", "kr")])
def test_hold_checks_only_other_market_when_demo_enabled(tmp_path, monkeypatch, profile, other):
    calls = []
    monkeypatch.setattr(paper_runtime, "_runtime_session", lambda **kw:
                        calls.append(kw) or {"is_open": True, "phase": "regular"})
    assert local.full_research_session_hold(profile, tmp_path, now=NOW) is None
    assert calls == []
    enable(tmp_path)
    assert local.full_research_session_hold(profile, tmp_path, now=NOW) == "DEFERRED_FOR_OTHER_MARKET_SESSION"
    assert calls == [{"market": other, "now_local": NOW}]


@pytest.mark.parametrize("session", [None, {}, "unavailable", {"is_open": False, "phase": "unknown"},
                                    {"is_open": None, "phase": "closed"},
                                    {"is_open": False, "phase": "regular"}])
def test_unconfirmed_calendar_never_grants_full_research_admission(tmp_path, monkeypatch, session):
    enable(tmp_path)
    monkeypatch.setattr(paper_runtime, "_runtime_session", lambda **kw: session)
    assert local.full_research_session_hold("kr", tmp_path, now=NOW) == "AWAITING_OTHER_MARKET_CALENDAR"


def test_calendar_exception_holds_without_writing_state(tmp_path, monkeypatch):
    enable(tmp_path)
    before = {p.relative_to(tmp_path): p.read_bytes() for p in tmp_path.rglob("*.json")}
    def unavailable(**kwargs):
        raise RuntimeError("calendar unavailable")
    monkeypatch.setattr(paper_runtime, "_runtime_session", unavailable)
    assert local.full_research_session_hold("kr", tmp_path, now=NOW) == "AWAITING_OTHER_MARKET_CALENDAR"
    assert {p.relative_to(tmp_path): p.read_bytes() for p in tmp_path.rglob("*.json")} == before


@pytest.mark.parametrize("stamp,expected", [
    ("2026-10-21T04:45:00+09:00", "DEFERRED_FOR_OTHER_MARKET_SESSION"),
    ("2026-10-21T05:00:00+09:00", None),
    ("2026-11-04T04:45:00+09:00", "DEFERRED_FOR_OTHER_MARKET_SESSION"),
    ("2026-11-04T06:00:00+09:00", None),
    ("2026-11-27T04:45:00+09:00", None),  # Thanksgiving in New York.
    ("2026-11-28T04:45:00+09:00", None),  # After the 13:00 New York early close.
])
def test_admission_uses_actual_dst_holiday_and_early_close_calendar(tmp_path, monkeypatch, stamp, expected):
    pytest.importorskip("exchange_calendars")
    from tradingagents.scheduled.market_calendar import market_session_state
    enable(tmp_path)
    monkeypatch.setattr(paper_runtime, "_runtime_session", market_session_state)
    assert local.full_research_session_hold("kr", tmp_path, now=datetime.fromisoformat(stamp)) == expected


def test_deferred_full_preserves_original_receipt_and_runs_freshness(tmp_path, monkeypatch):
    item = target()
    enable(tmp_path)
    path = receipt_path(tmp_path, item)
    path.parent.mkdir()
    path.write_text(json.dumps({"target": item.name, "attempts": 1,
                               "started_at": (NOW - timedelta(hours=2)).isoformat(), "exit_code": 1}))
    before = path.read_bytes()
    refresh = {"target": "execution-freshness-us", "status": "COMPLETED"}
    calls = wire(monkeypatch, item, refreshes=[refresh])
    monkeypatch.setattr(paper_runtime, "_runtime_session", lambda **kw: {"is_open": True, "phase": "regular"})
    assert local.run_due(tmp_path / "archive", tmp_path, now=NOW) == [
        {"target": item.name, "status": "DEFERRED_FOR_OTHER_MARKET_SESSION"}, refresh]
    assert calls["workers"] == calls["preflights"] == []
    assert len(calls["refreshes"]) == 1
    assert path.read_bytes() == before
    assert list(path.parent.iterdir()) == [path]


@pytest.mark.parametrize("session,status", [
    ({"is_open": True, "phase": "regular"}, "DEFERRED_FOR_OTHER_MARKET_SESSION"),
    ({"is_open": False, "phase": "unknown"}, "AWAITING_OTHER_MARKET_CALENDAR"),
])
def test_hold_without_refresh_does_not_start_advisory_or_spend_attempt(tmp_path, monkeypatch, session, status):
    item = target()
    enable(tmp_path)
    calls = wire(monkeypatch, item)
    monkeypatch.setattr(paper_runtime, "_runtime_session", lambda **kw: session)
    assert local.run_due(tmp_path / "archive", tmp_path, now=NOW) == [{"target": item.name, "status": status}]
    assert not (tmp_path / "attempts").exists()
    assert calls["workers"] == calls["preflights"] == []
    assert len(calls["refreshes"]) == 1


def test_market_close_admits_exactly_once_under_original_window_key(tmp_path, monkeypatch):
    item = target()
    enable(tmp_path)
    calls = wire(monkeypatch, item)
    monkeypatch.setattr(paper_runtime, "_runtime_session", lambda **kw: {
        "is_open": kw["now_local"] < NOW.replace(hour=5, minute=0),
        "phase": "regular" if kw["now_local"] < NOW.replace(hour=5, minute=0) else "closed"})
    assert local.run_due(tmp_path / "archive", tmp_path, now=NOW)[0]["status"] == "DEFERRED_FOR_OTHER_MARKET_SESSION"
    close = NOW.replace(hour=5, minute=0)
    assert local.run_due(tmp_path / "archive", tmp_path, now=close) == [{"target": item.name, "status": "DUE"}]
    path = receipt_path(tmp_path, item)
    receipt = json.loads(path.read_text())
    assert receipt["attempts"] == 1 and receipt["started_at"] == close.isoformat()
    assert list(path.parent.iterdir()) == [path]
    monkeypatch.setattr(local_advisory_recovery, "recover_due", lambda *a, **kw: [])
    assert local.run_due(tmp_path / "archive", tmp_path, now=close + timedelta(minutes=5))[0]["status"] == "RETRY_BUDGET_OR_COOLDOWN"
    assert len(calls["workers"]) == len(calls["preflights"]) == 1
    assert json.loads(path.read_text()) == receipt


def test_dry_run_hold_is_read_only(tmp_path, monkeypatch):
    enable(tmp_path)
    item = target()
    calls = wire(monkeypatch, item)
    monkeypatch.setattr(paper_runtime, "_runtime_session", lambda **kw: {"is_open": True, "phase": "regular"})
    before = {p.relative_to(tmp_path): p.read_bytes() for p in tmp_path.rglob("*.json")}
    assert local.run_due(tmp_path / "archive", tmp_path, now=NOW, dry_run=True)[0]["status"] == "DEFERRED_FOR_OTHER_MARKET_SESSION"
    assert calls["workers"] == calls["preflights"] == []
    assert calls["refreshes"][0]["dry_run"] is True
    assert {p.relative_to(tmp_path): p.read_bytes() for p in tmp_path.rglob("*.json")} == before


def test_overlay_admission_is_not_subject_to_full_research_hold(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "_resolve_latest_full_overlay_baseline_manifest", lambda *a, **kw: {"run_id": "ready"})
    enable(tmp_path)
    item = target(mode="overlay_only")
    calls = wire(monkeypatch, item)
    monkeypatch.setattr(local, "full_research_session_hold", lambda *a, **kw: pytest.fail("overlay admission changed"))
    assert local.run_due(tmp_path / "archive", tmp_path, now=NOW) == [{"target": item.name, "status": "DUE"}]
    assert len(calls["workers"]) == 1 and calls["preflights"] == []
    assert "--disable-execution-refresh" not in calls["workers"][0]


@pytest.mark.parametrize("attempts,started", [(4, NOW - timedelta(hours=2)), (1, NOW - timedelta(minutes=5))])
def test_existing_budget_and_cooldown_are_decided_before_session_hold(tmp_path, monkeypatch, attempts, started):
    item = target()
    enable(tmp_path)
    calls = wire(monkeypatch, item)
    path = receipt_path(tmp_path, item)
    path.parent.mkdir()
    path.write_text(json.dumps({"attempts": attempts, "started_at": started.isoformat(), "exit_code": 1}))
    before = path.read_bytes()
    monkeypatch.setattr(local, "full_research_session_hold", lambda *a, **kw: pytest.fail("budget bypass"))
    monkeypatch.setattr(local_advisory_recovery, "recover_due", lambda *a, **kw: [])
    assert local.run_due(tmp_path / "archive", tmp_path, now=NOW)[0]["status"] == "RETRY_BUDGET_OR_COOLDOWN"
    assert calls["workers"] == calls["preflights"] == []
    assert path.read_bytes() == before


@pytest.mark.parametrize("us_open", [False, True])
def test_current_kr_window_precedes_overnight_us_retry(tmp_path, monkeypatch, us_open):
    kr, us = target(), target("us")
    us.window_start_kst = NOW - timedelta(hours=11)
    enable(tmp_path)
    calls = wire(monkeypatch, kr)
    monkeypatch.setattr(local, "script", lambda _: SimpleNamespace(due_targets=lambda *a, **k: [us, kr]))
    monkeypatch.setattr(paper_runtime, "_runtime_session", lambda **kw: {
        "is_open": us_open and kw["market"] == "us",
        "phase": "regular" if us_open and kw["market"] == "us" else "closed"})
    result = local.run_due(tmp_path / "archive", tmp_path, now=NOW, research_only=True)
    if us_open:
        assert result == [{"target":kr.name,"status":"DEFERRED_FOR_OTHER_MARKET_SESSION"},
                          {"target":us.name,"status":"DEFERRED_FOR_NEXT_MARKET_RESEARCH"}]
        assert not calls["workers"]
    else:
        assert result == [{"target":kr.name,"status":"DUE"}]
        assert "local-scheduler-kr-full" in calls["workers"][0]
    assert not receipt_path(tmp_path, us).exists()
