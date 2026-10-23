from datetime import datetime, timedelta
import json
import subprocess
import sys

import pytest

from tradingagents.execution.strategy_diagnostics import allocation_view, refresh_attempt_health
from tests.execution.test_demo_strategy_plan import Harness, native_source, regular_session

NOW = datetime.fromisoformat("2026-10-23T01:00:00+09:00")


def test_diagnostics_import_does_not_load_producers_or_performance_models():
    # The threaded viewer imports these diagnostics concurrently with charts.
    # Loading the producer here previously deadlocked lazy performance imports.
    subprocess.run([sys.executable, "-c", "import sys; import tradingagents.execution.strategy_diagnostics; "
        "assert 'tradingagents.execution.paper_runtime' not in sys.modules; "
        "assert 'tradingagents.performance' not in sys.modules"], check=True, timeout=30)


def attempt():
    return {"market": "us", "session_date": "2026-10-22", "started_at": (NOW-timedelta(minutes=6)).isoformat(),
            "finished_at": (NOW-timedelta(minutes=5)).isoformat(), "status": "FAILED",
            "consecutive_failures": 3, "real_orders_enabled": False,
            "error_type": "LocalStorageHeadroomError", "private": "PRIVATE_SECRET"}


def test_exchange_day_failure_visible_without_reset_or_claiming_recovery():
    raw = attempt()
    assert refresh_attempt_health(raw, market="US", now=NOW)["status"] == "RETRY_LIMIT_REACHED"
    assert refresh_attempt_health(raw, market="US", now=NOW+timedelta(days=1))["status"] == "PREVIOUS_SESSION"
    assert raw == attempt()
    assert "PRIVATE" not in json.dumps(refresh_attempt_health(raw, market="US", now=NOW))


@pytest.mark.parametrize("changes", [{"started_at": None}, {"finished_at": "bad"},
    {"started_at": "2026-10-23T01:00:01+09:00"}, {"finished_at": "2026-10-23T01:01:00+09:00"},
    {"started_at": "2026-10-22T00:00:00"}, {"session_date": "2026-10-23"}, {"session_date": "bad"},
    {"consecutive_failures": True}, {"consecutive_failures": -1}, {"status": "COMPLETED"},
    {"market": "kr"}, {"real_orders_enabled": True}, {"status": "STARTED"}, {"status": []}])
def test_unverified_attempt_is_not_operational_success(changes):
    assert refresh_attempt_health({**attempt(), **changes}, market="US", now=NOW) == {"status": "UNVERIFIED"}


def test_empty_and_running_are_not_success():
    assert refresh_attempt_health(None, market="US", now=NOW)["status"] == "UNAVAILABLE"
    assert refresh_attempt_health({}, market="US", now=NOW)["status"] == "UNVERIFIED"
    raw = {**attempt(), "status": "STARTED", "finished_at": None}
    assert refresh_attempt_health(raw, market="US", now=NOW)["status"] == "RUNNING"
    raw.update(status="COMPLETED", finished_at=NOW.isoformat(), consecutive_failures=0)
    assert refresh_attempt_health(raw, market="US", now=NOW)["status"] == "LAST_ATTEMPT_COMPLETED"
    raw["error_type"] = {"message": "PRIVATE_SECRET"}
    assert refresh_attempt_health(raw, market="US", now=NOW)["error_type"] == "OTHER"


def allocation():
    return {"allocation_mode": "DEMO_NATIVE_ONE_SHARE_V1", "eligible_candidates": 0,
            "strategy_owned_positions": 0, "real_account_allocation_used": False,
            "reason_counts": {"NO_AUTHORIZED_EXECUTION_ACTION": 30},
            "research_entry_actions": {"WAIT": 30}, "research_conditional_entries": {"NONE": 30},
            "ticker_blockers": {"PRIVATE_TICKER": "PRIVATE_SECRET"}}


def test_actual_reason_counts_survive_projection_without_private_details():
    projected = allocation_view(allocation())
    assert projected["reason_counts"] == {"NO_AUTHORIZED_EXECUTION_ACTION": 30}
    assert "PRIVATE" not in json.dumps(projected)
    for key, value in (("eligible_candidates", True), ("reason_counts", {"PRIVATE_SECRET": 1}),
                       ("research_entry_actions", {"BUY": -1}), ("real_account_allocation_used", True)):
        assert allocation_view({**allocation(), key: value}) is None


def test_every_valid_research_entry_action_preserves_blocker_counts():
    from tradingagents.schemas.decision import EntryAction
    raw = allocation()
    raw["research_entry_actions"] = {action.value: 1 for action in EntryAction}
    raw["research_entry_actions"]["MISSING"] = 1
    projected = allocation_view(raw)
    assert projected is not None
    assert projected["research_entry_actions"] == raw["research_entry_actions"]
    assert projected["reason_counts"] == raw["reason_counts"]
    assert "PRIVATE" not in json.dumps(projected)


@pytest.mark.parametrize("action", ["REDUCE", "EXIT", "UNKNOWN"])
def test_research_conditional_entry_does_not_accept_execution_exit_codes(action):
    assert allocation_view({**allocation(), "research_conditional_entries": {action: 1}}) is None


@pytest.mark.parametrize("market", ["KR", "US"])
def test_closed_market_still_records_producer_failure_without_broker_calls(tmp_path, market):
    h = Harness(tmp_path, market)
    native_source(h)
    path = h.root.parent / "execution-refresh" / f"{market.lower()}.json"
    path.parent.mkdir(parents=True)
    original = json.dumps(attempt()).encode()
    path.write_bytes(original)
    result = h.tick(session_resolver=lambda **kwargs: {**regular_session(**kwargs), "is_open": False})
    assert result["status"] == "MARKET_CLOSED"
    assert result["refresh_attempt"]["status"] == "FAILED"
    assert "private" not in result["refresh_attempt"]
    assert path.read_bytes() == original and h.calls == []
