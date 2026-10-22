from datetime import datetime, timedelta, timezone
import json

import pytest

from tradingagents.atomic_io import atomic_write_json, interprocess_file_lock
from tradingagents.execution import research_runtime as research
from tradingagents.scheduled import runner
from tests.scheduled.test_research_refresh import cohort, encoded_decision

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


def original_approval(h, *, conditional=False):
    path = h.source / "tickers/AAPL/analysis.json"
    analysis = json.loads(path.read_text())
    analysis.update(decision=encoded_decision(portfolio_stance="BULLISH",
        entry_action="WAIT" if conditional else "STARTER",
        conditional_entry_action="STARTER" if conditional else "NONE",
        conditional_entry_valid_until=(NOW + timedelta(hours=1)).isoformat() if conditional else None,
        data_coverage={"company_news_count": 2},
        execution_levels={"levels": [{"level_type": "BREAKOUT", "price": 100, "confirmation": "intraday"}]}),
        tool_telemetry={"fallback_count": 0})
    h.observations["strategy_table"] = [h.observations["strategy_table"][0]]
    atomic_write_json(h.source / "decision_bundle_v2.json", h.observations)
    return path, analysis


@pytest.mark.parametrize("case", ["live_base", "live_conditional", "expired_base", "expired_conditional",
    "future_finished", "missing_finished", "missing_started", "backwards", "naive", "bad_date",
    "failed", "wrong_ticker", "missing_ticker", "legacy_label", "invalid_json", "incomplete", "non_object",
    "wait", "invalidated", "fallback", "missing_requests", "bad_telemetry", "no_news", "no_tools"])
def test_production_json_authorizations_only_skip_executable_original_research(tmp_path, monkeypatch, case):
    h = Harness(tmp_path, monkeypatch)
    path, analysis = original_approval(h, conditional=case in {"live_conditional", "expired_conditional"})
    if case == "expired_base":
        analysis.update(started_at=(NOW-timedelta(hours=24, minutes=1)).isoformat(),
            finished_at=(NOW-timedelta(hours=24)).isoformat())
    if case == "expired_conditional":
        decision = json.loads(analysis["decision"])
        decision["conditional_entry_valid_until"] = NOW.isoformat()
        analysis["decision"] = json.dumps(decision)
    if case == "future_finished":
        analysis["finished_at"] = (NOW+timedelta(seconds=1)).isoformat()
    if case == "missing_finished":
        analysis.pop("finished_at")
    if case == "missing_started":
        analysis.pop("started_at")
    if case == "backwards":
        analysis["started_at"] = NOW.isoformat()
    if case == "naive":
        analysis["finished_at"] = "2026-10-21T13:00:00"
    if case == "bad_date":
        analysis["finished_at"] = "2026-02-30T13:00:00Z"
    if case == "failed":
        analysis["status"] = "failed"
    if case == "wrong_ticker":
        analysis["ticker"] = "MSFT"
    if case == "missing_ticker":
        analysis.pop("ticker")
    if case == "legacy_label":
        analysis["decision"] = "BUY"
    if case == "invalid_json":
        analysis["decision"] = '{"entry_action":'
    if case == "incomplete":
        analysis["decision"] = json.dumps({"entry_action": "STARTER"})
    if case == "non_object":
        analysis = [analysis]
    if case in {"wait", "no_news"}:
        decision = json.loads(analysis["decision"])
        if case == "wait":
            decision["entry_action"] = "WAIT"
        else:
            decision["data_coverage"]["company_news_count"] = 0
        analysis["decision"] = json.dumps(decision)
    if case == "invalidated":
        h.observations["strategy_table"][0]["raw_codes"] = {"decision_state": "INVALIDATED"}
    if case == "fallback":
        analysis["tool_telemetry"]["fallback_count"] = 3
    if case == "missing_requests":
        analysis["tool_telemetry"]["request_outcomes"] = []
    if case == "bad_telemetry":
        analysis["tool_telemetry"] = ["unverified"]
    if case == "no_tools":
        analysis["quality_flags"] = ["no_tool_calls_detected"]
    atomic_write_json(path, analysis)
    atomic_write_json(h.source / "decision_bundle_v2.json", h.observations)
    before = path.read_bytes()
    targets = research.select_targets(h.source, h.manifest, h.source, market="US", now=NOW,
        allowed=("AAPL",), cap=500)
    assert targets == ([] if case in {"live_base", "live_conditional"} else ["AAPL"])
    assert path.read_bytes() == before
    assert h.calls == []


@pytest.mark.parametrize("conditional", [False, True])
@pytest.mark.parametrize("offset_seconds", [-1, 0, 1])
def test_research_and_order_planner_use_identical_expiry_boundaries(tmp_path, conditional, offset_seconds):
    from tests.execution.test_demo_runtime import Harness as OrderHarness
    from tests.execution.test_demo_strategy_plan import native_source
    from tradingagents.execution.demo_strategy_plan import plan

    h = OrderHarness(tmp_path, "US")
    run, contract = native_source(h)
    analysis_path = run / "tickers" / h.ticker / "analysis.json"
    analysis = json.loads(analysis_path.read_text())
    decision = json.loads(analysis["decision"])
    if conditional:
        decision["conditional_entry_valid_until"] = (h.now+timedelta(seconds=offset_seconds)).isoformat()
        contract["entry_valid_until"] = decision["conditional_entry_valid_until"]
    else:
        decision.update(entry_action="STARTER", conditional_entry_action="NONE", conditional_entry_valid_until=None)
        finished = h.now-timedelta(hours=24)+timedelta(seconds=offset_seconds)
        analysis.update(started_at=(finished-timedelta(minutes=5)).isoformat(), finished_at=finished.isoformat())
        contract.update(analysis_asof=finished.isoformat(), entry_action_base="STARTER", entry_valid_until=None)
    analysis["decision"] = json.dumps(decision)
    atomic_write_json(analysis_path, analysis)
    atomic_write_json(run / "tickers" / h.ticker / "execution_contract.json", contract)
    update_path = run / "tickers" / h.ticker / "execution_update.json"
    update = json.loads(update_path.read_text())
    update["analysis_asof"] = contract["analysis_asof"]
    atomic_write_json(update_path, update)
    candidate_path = run / "portfolio-private/portfolio_candidates.json"
    candidates = json.loads(candidate_path.read_text())
    candidates["candidates"][0]["structured_decision"] = decision
    atomic_write_json(candidate_path, candidates)
    orders, _ = plan(run, "US", h.now, (h.ticker,), {})
    assert research.current_entry_authorization(analysis, h.now, ticker=h.ticker) is (offset_seconds > 0)
    assert bool(orders) is (offset_seconds > 0)
    assert h.calls == []


def test_bounded_refresh_preserves_all_original_theses_and_does_not_create_approval(tmp_path, monkeypatch):
    h = Harness(tmp_path, monkeypatch)
    originals = {path: path.read_bytes() for path in h.source.rglob("*") if path.is_file()}
    result = h.tick()
    assert result[0]["status"] == "COMPLETED"
    assert result[0]["broker_orders_sent"] == 0 and result[0]["real_orders_enabled"] is False
    assert h.calls[0]["targets"] == ["AAPL", "AMD"]
    assert {path: path.read_bytes() for path in originals} == originals
    for ticker in ("AAPL", "AMD", "MSFT"):
        analysis = json.loads((h.source / "tickers" / ticker / "analysis.json").read_text())
        assert json.loads(analysis["decision"])["entry_action"] == "WAIT"
        assert not research.current_entry_authorization(analysis, NOW, ticker=ticker)
    assert not list(h.state.glob("kis-strategy/*.sqlite"))


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
