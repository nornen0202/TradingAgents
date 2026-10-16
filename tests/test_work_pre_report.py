from copy import deepcopy
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from tradingagents.atomic_io import interprocess_file_lock
from tradingagents.work import pre_report as pre


NOW = datetime.now(timezone.utc)


def packet():
    return {"body": {"source_health": "OK", "current": {
        "universe_coverage": {"status": "COMPLETE"},
        "freshness_receipt": {"producer_run_id": "refreshed", "market_data_status": "FRESH",
            "market_data_oldest_at": NOW.isoformat(), "market_data_latest_at": NOW.isoformat(),
            "account_as_of": NOW.isoformat(), "account_snapshot_health": "VALID",
            "analysis_lineage_status": "RESOLVED", "analysis_completed_at": NOW.isoformat()}}}}


def test_real_observations_and_full_coverage_required():
    original = packet()
    assert pre.freshness_blockers(original, now=NOW, started_at=NOW, run_id="refreshed") == []
    assert original == packet()


@pytest.mark.parametrize("field,value", [
    ("market_data_oldest_at", None),
    ("market_data_oldest_at", (NOW - timedelta(minutes=1)).isoformat()),
    ("market_data_latest_at", (NOW + timedelta(seconds=1)).isoformat()),
    ("account_as_of", "bad"),
    ("account_as_of", (NOW - timedelta(minutes=30)).isoformat()),
    ("account_snapshot_health", "WATCHLIST_ONLY"),
    ("market_data_status", "STALE"),
    ("producer_run_id", "cached-previous-run"),
    ("analysis_lineage_status", "UNVERIFIED"),
    ("analysis_completed_at", (NOW - timedelta(hours=36)).isoformat()),
])
def test_copied_or_invalid_input_is_never_made_current(field, value):
    item = packet()
    item["body"]["current"]["freshness_receipt"][field] = value
    assert pre.freshness_blockers(item, now=NOW, started_at=NOW, run_id="refreshed")


def test_long_refresh_and_incomplete_coverage_block():
    item = packet()
    item["body"]["current"]["universe_coverage"]["status"] = "INCOMPLETE"
    assert "UNIVERSE_NOT_COMPLETE" in pre.freshness_blockers(item, now=NOW, started_at=NOW, run_id="refreshed")
    assert pre.freshness_blockers(packet(), now=NOW + timedelta(minutes=10), started_at=NOW, run_id="refreshed")


def test_final_publish_clock_cannot_be_renewed_by_report_timestamp():
    item = packet()
    item["body"]["current"]["bundle"] = {"strategy_table": [
        {"execution": {"valid_until": (NOW + timedelta(minutes=30)).isoformat()}}]}
    assert pre.publish_freshness_blockers(item, now=NOW + timedelta(minutes=29)) == []
    assert pre.publish_freshness_blockers(item, now=NOW + timedelta(minutes=30))
    item["body"]["current"]["bundle"]["strategy_table"][0]["execution"]["valid_until"] = NOW.isoformat()
    assert "ROW_VALIDITY_EXPIRED_OR_MISSING" in pre.publish_freshness_blockers(item, now=NOW)


@pytest.fixture
def wired(tmp_path, monkeypatch):
    from tradingagents import local_automation
    monkeypatch.setattr(local_automation, "prepare_environment", lambda: None)
    monkeypatch.setattr(local_automation, "require_storage_headroom", lambda *a: None)
    monkeypatch.setattr(pre, "market_session_state", lambda **kw: {"is_open": True, "phase": "regular"})
    monkeypatch.setattr(pre, "automated_market_session_status", lambda **kw: SimpleNamespace(is_session=True))
    monkeypatch.setattr(pre, "resolve_archive_roots", lambda **kw: {"market": tmp_path / "archive"})
    prepared, configs = [], []
    runtime = SimpleNamespace(prepare=lambda *a, **kw: prepared.append(kw) or {"result": "NEW", "event_id": "new"})

    def execute(config, **kw):
        configs.append(config)
        return {"run_id": "refreshed", "status": "success"}

    def current_packet(*a, **kw):
        item = packet()
        observed = kw["now"].isoformat()
        for field in ("market_data_oldest_at", "market_data_latest_at", "account_as_of"):
            item["body"]["current"]["freshness_receipt"][field] = observed
        return item

    monkeypatch.setattr(pre, "execute_scheduled_run", execute)
    monkeypatch.setattr(pre, "build_surface_packet", current_packet)
    return runtime, prepared, configs


@pytest.mark.parametrize("surface", ["kr", "us"])
def test_refresh_before_prepare_preserves_models_and_does_not_rerun_research(wired, tmp_path, surface):
    runtime, prepared, configs = wired
    result = pre.prepare_market_report(runtime, surface, producer_state_dir=tmp_path)
    assert result["result"] == "NEW"
    assert result["pre_report_refresh"]["status"] == "REFRESHED"
    assert result["pre_report_refresh"]["event_created"] is True
    assert len(prepared) == len(configs) == 1
    config = configs[0]
    assert config.run.run_mode == "overlay_only"
    assert config.llm.deep_model == config.llm.judge_model == "gpt-6.1-sol"
    assert config.llm.codex_deep_reasoning_effort == config.llm.codex_judge_reasoning_effort == "xhigh"
    assert config.execution.execution_session_gate_enabled
    assert not config.execution.execution_selective_rerun_enabled
    assert len(config.execution.execution_refresh_checkpoints_local) == 1


def test_busy_producer_does_not_start_or_allocate_event(wired, tmp_path):
    runtime, prepared, configs = wired
    with interprocess_file_lock(tmp_path / "run-due.lock", timeout=0):
        result = pre.prepare_market_report(runtime, "us", producer_state_dir=tmp_path)
    assert result["status"] == "BUSY_NO_STATE_ADVANCE"
    assert not prepared and not configs


def test_closed_market_has_no_report_or_broker_calls(wired, tmp_path, monkeypatch):
    runtime, prepared, configs = wired
    monkeypatch.setattr(pre, "market_session_state", lambda **kw: {"is_open": False, "phase": "closed"})
    result = pre.prepare_market_report(runtime, "us", producer_state_dir=tmp_path)
    assert result["status"] == "MARKET_CLOSED"
    assert not prepared and not configs


@pytest.mark.parametrize("is_session,expected", [(False, "MARKET_CLOSED"), (None, "CALENDAR_UNVERIFIED")])
def test_official_calendar_can_veto_exchange_clock(wired, tmp_path, monkeypatch, is_session, expected):
    runtime, prepared, configs = wired
    monkeypatch.setattr(pre, "automated_market_session_status",
                        lambda **kw: SimpleNamespace(is_session=is_session, source="official"))
    result = pre.prepare_market_report(runtime, "kr", producer_state_dir=tmp_path)
    assert result["status"] == expected
    assert not prepared and not configs


def test_session_ending_during_refresh_does_not_allocate_event(wired, tmp_path, monkeypatch):
    runtime, prepared, configs = wired
    states = iter([True, True, False])
    monkeypatch.setattr(pre, "market_session_state", lambda **kw: {"is_open": next(states), "phase": "regular"})
    result = pre.prepare_market_report(runtime, "us", producer_state_dir=tmp_path)
    assert result["status"] == "FRESH_INPUT_UNAVAILABLE"
    assert "SESSION_ENDED_DURING_REFRESH" in result["blockers"]
    assert not prepared


def test_failed_account_does_not_allocate_event(wired, tmp_path, monkeypatch):
    runtime, prepared, configs = wired
    monkeypatch.setattr(pre, "build_surface_packet", lambda *a, **kw: packet())
    item = packet()
    item["body"]["current"]["freshness_receipt"]["account_snapshot_health"] = "WATCHLIST_ONLY"
    monkeypatch.setattr(pre, "build_surface_packet", lambda *a, **kw: deepcopy(item))
    result = pre.prepare_market_report(runtime, "kr", producer_state_dir=tmp_path)
    assert result["status"] == "FRESH_INPUT_UNAVAILABLE"
    assert "ACCOUNT_NOT_VALID" in result["blockers"]
    assert not prepared


@pytest.mark.parametrize("error", [RuntimeError, TimeoutError])
def test_broker_error_receipt_does_not_leak_request(wired, tmp_path, monkeypatch, error):
    runtime, prepared, configs = wired

    def fail(*a, **kw):
        raise error("secret account request")

    monkeypatch.setattr(pre, "execute_scheduled_run", fail)
    result = pre.prepare_market_report(runtime, "kr", producer_state_dir=tmp_path)
    assert result["status"] == "FRESH_INPUT_UNAVAILABLE"
    assert "secret" not in str(result)
    assert not prepared
