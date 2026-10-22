from datetime import datetime, timedelta, timezone
import json

import pytest

from tradingagents.atomic_io import atomic_write_json, interprocess_file_lock
from tradingagents.execution import research_runtime as research
from tradingagents.scheduled import runner
from tests.scheduled.test_research_refresh import cohort

NOW = datetime(2026, 10, 21, 14, 11, tzinfo=timezone.utc)


class Harness:
    def __init__(self, root, monkeypatch):
        self.archive, self.state = root / "archive", root / "state"
        self.source, self.manifest = cohort(self.archive, start=NOW - timedelta(hours=2))
        self.calls = []
        atomic_write_json(self.state / "actions-drained.json", {"drained_at": NOW.isoformat()})
        self.enable()
        self.quote(NOW)
        monkeypatch.setattr(runner, "_resolve_latest_full_overlay_baseline_manifest", lambda *a, **k: self.manifest)
        monkeypatch.setattr(runner, "_resolve_latest_overlay_source_manifest", lambda *a, **k: self.manifest)

    def enable(self, **changes):
        data = {"enabled": True, "mode": "KIS_DEMO_STRATEGY", "allocation_mode": "DEMO_NATIVE_ONE_SHARE_V1", "real_orders_enabled": False}
        data.update(changes)
        atomic_write_json(self.state / "kis-strategy/enabled.json", data)

    def quote(self, now):
        self.observations = {"generated_at": now.isoformat(), "strategy_table": [
            {"ticker": t, "market_session": "regular", "last_price": 100,
             "market_data_asof": (now - timedelta(seconds=15)).isoformat(), "confidence": .6}
            for t in ("AAPL", "AMD", "MSFT")]}
        atomic_write_json(self.source / "decision_bundle_v2.json", self.observations)

    def execute(self, config, **kwargs):
        # A long model call must leave quote production and reconciliation free.
        with interprocess_file_lock(self.state / "run-due.lock", timeout=0), interprocess_file_lock(self.state / "kis-strategy/strategy.lock", timeout=0):
            self.calls.append(kwargs["research_refresh_plan"])
        assert config.run.run_mode == "selective_rerun_only"
        assert not config.execution.execution_refresh_enabled
        assert not config.portfolio.enabled
        assert kwargs["defer_execution_handoff"] and kwargs["skip_site_build"]
        return {"run_id": "new-normal-research", "status": "success", "research_refresh": {"completed": True}}

    def tick(self, now=NOW, **kwargs):
        return research.research_due(self.archive, self.state, now=now, executor=self.execute,
            prepare=lambda _: None, universe_loader=lambda: {"KR": (), "US": ("AAPL", "AMD", "MSFT")},
            session_resolver=lambda **k: {"is_open": k["market"] == "us", "phase": "regular"}, **kwargs)


def test_fixed_slots_bound_distinct_targets_without_changing_order_limits(tmp_path, monkeypatch):
    h = Harness(tmp_path, monkeypatch)
    assert h.tick()[0]["status"] == "COMPLETED"
    assert h.calls[0]["targets"] == ["AAPL", "AMD"]
    assert h.tick() == []
    later = NOW + timedelta(hours=3)
    h.quote(later)
    assert h.tick(later)[0]["status"] == "COMPLETED"
    assert h.calls[1]["targets"] == ["MSFT"]
    assert h.tick(later) == []
    assert len(h.calls) == 2
    assert not list(h.state.glob("kis-strategy/*.sqlite"))


@pytest.mark.parametrize("status", ["STARTED", "FAILED", "COMPLETED"])
def test_interrupted_or_failed_slot_is_never_reset_and_replayed(tmp_path, monkeypatch, status):
    h = Harness(tmp_path, monkeypatch)
    path = h.state / "research-refresh/us/2026-10-21-0.json"
    atomic_write_json(path, {"status": status, "targets": ["AAPL", "AMD"]})
    before = path.read_bytes()
    assert h.tick() == []
    assert h.calls == []
    assert path.read_bytes() == before


def test_research_failure_is_recorded_without_stalling_other_lanes(tmp_path, monkeypatch):
    h = Harness(tmp_path, monkeypatch)
    def raise_error(*a, **k):
        raise RuntimeError("fixture failure")
    h.execute = raise_error
    assert h.tick()[0]["status"] == "FAILED"
    assert h.tick() == []
    assert json.loads((h.state / "research-refresh/us/2026-10-21-0.json").read_text())["error_type"] == "RuntimeError"


@pytest.mark.parametrize("change", ["empty", "future", "undated", "stale", "cap", "bad_price", "closed", "allowlist"])
def test_missing_unusable_observations_cannot_select_a_research_target(tmp_path, monkeypatch, change):
    h = Harness(tmp_path, monkeypatch)
    for row in h.observations["strategy_table"]:
        if change == "future":
            row["market_data_asof"] = (NOW + timedelta(seconds=1)).isoformat()
        if change == "undated":
            row["market_data_asof"] = None
        if change == "stale":
            row["market_data_asof"] = (NOW - timedelta(seconds=120)).isoformat()
        if change == "cap":
            row["last_price"] = 501
        if change == "bad_price":
            row["last_price"] = True
        if change == "closed":
            row["market_session"] = "closed"
    if change == "empty":
        h.observations["strategy_table"] = []
    atomic_write_json(h.source / "decision_bundle_v2.json", h.observations)
    targets = research.select_targets(h.source, h.manifest, h.source, market="US", now=NOW,
        allowed=() if change == "allowlist" else ("AAPL", "AMD", "MSFT"), cap=500)
    assert targets == []
    assert h.calls == []


@pytest.mark.parametrize("change", [{"enabled": False}, {"real_orders_enabled": True}, {"allocation_mode": "other"}])
def test_existing_opt_in_is_required(tmp_path, monkeypatch, change):
    h = Harness(tmp_path, monkeypatch)
    h.enable(**change)
    assert h.tick() == []
    assert h.calls == []


def test_dry_run_never_starts_models_or_consumes_research_slot(tmp_path, monkeypatch):
    h = Harness(tmp_path, monkeypatch)
    assert h.tick(dry_run=True)[0]["status"] == "DUE"
    assert not list(h.state.glob("research-refresh/**/*.json"))
    assert h.calls == []


def test_missed_slot_is_not_launched_near_the_close(tmp_path, monkeypatch):
    h = Harness(tmp_path, monkeypatch)
    later = NOW + timedelta(hours=5)
    h.quote(later)
    assert h.tick(later) == []
    assert h.calls == []


def test_installed_research_lane_admits_daily_full_with_unchanged_dispatcher(tmp_path, monkeypatch):
    from tradingagents import local_automation as local
    h = Harness(tmp_path, monkeypatch)
    atomic_write_json(h.state / "research-lane-enabled.json", {
        "mode": "PAPER_RESEARCH_INDEPENDENT_V1", "enabled": True, "real_orders_enabled": False})
    seen = []
    def due(archive, state, **kwargs):
        seen.append(kwargs)
        with interprocess_file_lock(state / "run-due.lock", timeout=0):
            return [{"target": "daily-codex-us", "status": "DUE"}]
    monkeypatch.setattr(local, "run_due", due)
    assert h.tick()[0]["status"] == "DAILY_RESEARCH_ATTEMPTED"
    assert seen == [{"now": NOW, "dry_run": False, "research_only": True}]
    assert h.calls == []


def test_new_research_waits_for_existing_producer_ownership_transfer(tmp_path, monkeypatch):
    h = Harness(tmp_path, monkeypatch)
    (h.state / "actions-drained.json").unlink()
    assert h.tick() == [{"status": "WAITING_LOCAL_AUTOMATION_AUTHORITY"}]
    assert h.calls == []


@pytest.mark.parametrize("kst_clock,expected", [
    ("2026-10-22T17:49:00+09:00", []),
    ("2026-10-22T17:50:00+09:00", ["daily-codex-us"]),
    ("2026-10-23T00:10:00+09:00", ["daily-codex-us"]),
    ("2026-10-24T00:10:00+09:00", ["daily-codex-us"]),
    ("2026-10-22T05:01:00+09:00", ["daily-codex-us", "daily-codex-kr"]),
])
def test_independent_daily_research_uses_korean_schedule_for_utc_clock(
        tmp_path, monkeypatch, kst_clock, expected):
    from types import SimpleNamespace
    from tradingagents import local_automation as local
    from tradingagents.scheduled import automation_calendar

    h = Harness(tmp_path, monkeypatch)
    atomic_write_json(h.state / "research-lane-enabled.json", {
        "mode": "PAPER_RESEARCH_INDEPENDENT_V1", "enabled": True, "real_orders_enabled": False})
    monkeypatch.setattr(runner, "_iter_run_manifests_desc", lambda _: [])
    monkeypatch.setattr(automation_calendar, "automated_market_session_status",
                        lambda **kwargs: SimpleNamespace(is_session=True))
    monkeypatch.setattr(local, "full_research_session_hold", lambda *a, **k: None)
    now = datetime.fromisoformat(kst_clock)
    # The installed research entry point normalizes its clock to UTC. Exercise
    # the real daily dispatcher, rather than mocking away its KST calendar.
    decisions = local.run_due(h.archive, h.state, now=now.astimezone(timezone.utc),
                              dry_run=True, research_only=True)
    assert [row["target"] for row in decisions if row["status"] == "DUE"] == expected
    assert decisions == local.run_due(h.archive, h.state, now=now,
                                     dry_run=True, research_only=True)
    result = h.tick(now, dry_run=True)
    if expected:
        assert result == [{"status": "DAILY_RESEARCH_DUE", "decisions": decisions}]
    else:
        assert result == []
    assert not list((h.state / "attempts").glob("*.json"))
    assert not list((h.state / "research-refresh").glob("**/*.json"))
    assert h.calls == []
