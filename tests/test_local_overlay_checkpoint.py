import hashlib
import json
from datetime import datetime
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest

from tradingagents import local_automation as local
from tradingagents.scheduled import automation_calendar, config as config_module, runner


def kst(value):
    return datetime.fromisoformat(value).replace(tzinfo=ZoneInfo("Asia/Seoul"))


def us_target(now):
    return next(t for t in local.script("scheduled_actions_watchdog").due_targets(now)
                if t.name.startswith("intraday-overlay-us-"))


@pytest.mark.parametrize("now,expected", [
    ("2026-10-13T22:35:00", "2026-10-13T23:00:00"),
    ("2026-10-13T22:54:00", "2026-10-13T23:00:00"),
    ("2026-10-13T23:03:00", "2026-10-13T23:00:00"),
    ("2026-10-14T00:20:00", "2026-10-13T23:00:00"),
    ("2026-10-14T00:43:00", "2026-10-14T00:40:00"),
    ("2026-10-14T02:13:00", "2026-10-14T02:10:00"),
    ("2026-11-06T22:35:00", "2026-11-07T00:00:00"),
    ("2026-11-06T23:54:00", "2026-11-07T00:00:00"),
    ("2026-11-07T00:03:00", "2026-11-07T00:00:00"),
    ("2026-11-07T00:43:00", "2026-11-07T00:40:00"),
])
def test_first_us_checkpoint_uses_market_session_date_across_dst_and_midnight(now, expected):
    now = kst(now)
    target = us_target(now)
    original_window = target.window_start_kst
    original_name = target.name
    assert local.local_target_window_start(target, now=now) == kst(expected)
    assert (target.window_start_kst, target.name) == (original_window, original_name)


def test_alignment_reads_effective_config_and_leaves_other_targets_unchanged(monkeypatch):
    execution = SimpleNamespace(execution_refresh_enabled=True,
                               execution_refresh_checkpoints_local=["11:00", "10:15"],
                               execution_refresh_checkpoints_kst=[],
                               execution_checkpoint_timezone="America/New_York")
    monkeypatch.setattr(config_module, "load_scheduled_config", lambda _: SimpleNamespace(execution=execution))
    now = kst("2026-10-13T23:20:00")
    assert local.local_target_window_start(us_target(now), now=now) == kst("2026-10-13T23:15:00")
    execution.execution_refresh_enabled = False
    target = us_target(now)
    assert local.local_target_window_start(target, now=now) == target.window_start_kst
    monkeypatch.setattr(config_module, "load_scheduled_config", lambda _: pytest.fail("unrelated config read"))
    for target in local.script("scheduled_actions_watchdog").due_targets(kst("2026-10-13T10:07:00")):
        assert local.local_target_window_start(target, now=now) == target.window_start_kst


def overlay_manifest(started="2026-10-13T22:54:00+09:00", finished="2026-10-13T22:55:00+09:00"):
    return {"settings": {"market": "US", "run_mode": "overlay_only"}, "status": "success",
            "summary": {"total_tickers": 30, "failed_tickers": 0},
            "started_at": started, "finished_at": finished}


def wire_overlay_only(monkeypatch, manifests=()):
    watchdog = local.script("scheduled_actions_watchdog")
    monkeypatch.setattr(local, "script", lambda _: SimpleNamespace(
        due_targets=lambda now, **kwargs: [t for t in watchdog.due_targets(now, **kwargs)
                                           if t.workflow_file == "intraday-overlay-refresh.yml"]))
    monkeypatch.setattr(automation_calendar, "automated_market_session_status",
                        lambda market, now: SimpleNamespace(is_session=True))
    monkeypatch.setattr(runner, "_iter_run_manifests_desc", lambda _: [(m, None) for m in manifests])


def write_receipt(state, target, **updates):
    key = hashlib.sha256(f"{target.name}:{target.window_start_kst.isoformat()}".encode()).hexdigest()
    path = state / "attempts" / f"{key}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"target": target.name, "attempts": 1, "exit_code": 0,
                               "started_at": "2026-10-13T22:53:55+09:00", **updates}))
    return path


@pytest.mark.parametrize("now", ["2026-10-13T22:35:00", "2026-10-13T22:54:00"])
def test_early_tick_waits_without_spending_attempt_or_running_worker(tmp_path, monkeypatch, now):
    wire_overlay_only(monkeypatch)
    monkeypatch.setattr(local.subprocess, "run", lambda *a, **k: pytest.fail("early worker launch"))
    decisions = local.run_due(tmp_path / "archive", tmp_path / "state", now=kst(now))
    assert [d["status"] for d in decisions] == ["AWAITING_EXECUTION_CHECKPOINT"]
    assert not (tmp_path / "state").exists()


def test_legacy_early_success_does_not_suppress_real_refresh_or_reset_its_budget(tmp_path, monkeypatch):
    now = kst("2026-10-13T23:08:00")
    target = us_target(now)
    state = tmp_path / "state"
    path = write_receipt(state, target)
    wire_overlay_only(monkeypatch, [overlay_manifest()])
    calls = []
    monkeypatch.setattr(local.subprocess, "run", lambda args, **kwargs: calls.append(args) or SimpleNamespace(returncode=0))
    monkeypatch.setattr(local, "preflight", lambda _: pytest.fail("full analysis preflight"))
    assert local.run_due(tmp_path / "archive", state, now=now) == [{"target": target.name, "status": "DUE"}]
    assert len(calls) == 1
    assert calls[0][calls[0].index("--run-mode") + 1] == "overlay_only"
    assert "--disable-execution-refresh" not in calls[0]
    assert json.loads(path.read_text())["attempts"] == 2
    assert list((state / "attempts").iterdir()) == [path]


@pytest.mark.parametrize("attempts,exit_code", [(1, 1), (2, 1), (2, 0)])
def test_failed_cooldown_and_exhausted_budget_are_never_exempted(tmp_path, monkeypatch, attempts, exit_code):
    now = kst("2026-10-13T23:08:00")
    target = us_target(now)
    state = tmp_path / "state"
    path = write_receipt(state, target, attempts=attempts, exit_code=exit_code)
    before = path.read_bytes()
    wire_overlay_only(monkeypatch, [overlay_manifest()])
    monkeypatch.setattr(local.subprocess, "run", lambda *a, **k: pytest.fail("budget bypass"))
    assert local.run_due(tmp_path / "archive", state, now=now)[0]["status"] == "RETRY_BUDGET_OR_COOLDOWN"
    assert path.read_bytes() == before


def test_completed_real_refresh_suppresses_duplicate_even_when_publication_is_pending(tmp_path, monkeypatch):
    manifest = overlay_manifest("2026-10-13T23:03:00+09:00", "2026-10-13T23:04:00+09:00")
    manifest["publication"] = {"status": "PAGES_PENDING"}
    wire_overlay_only(monkeypatch, [overlay_manifest(), manifest])
    monkeypatch.setattr(local.subprocess, "run", lambda *a, **k: pytest.fail("duplicate overlay"))
    assert local.run_due(tmp_path / "archive", tmp_path / "state", now=kst("2026-10-13T23:08:00"))[0]["status"] == "RESEARCH_COMPLETE"


@pytest.mark.parametrize("is_session", [False, None])
def test_closed_or_unknown_market_never_creates_a_local_overlay(tmp_path, monkeypatch, is_session):
    wire_overlay_only(monkeypatch)
    monkeypatch.setattr(automation_calendar, "automated_market_session_status",
                        lambda market, now: SimpleNamespace(is_session=is_session))
    monkeypatch.setattr(local.subprocess, "run", lambda *a, **k: pytest.fail("closed-market worker"))
    assert local.run_due(tmp_path / "archive", tmp_path / "state", now=kst("2026-10-13T23:08:00")) == []
    assert not (tmp_path / "state").exists()
