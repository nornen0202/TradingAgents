"""A released producer lock cannot turn unverified data into a Work event."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone

import pytest

from tradingagents.work import pre_report, runtime as work_runtime
from tradingagents.work.packet import seal_packet
from tradingagents.work.runtime import WorkRuntime, WorkRuntimeError


AT = datetime(2026, 10, 21, 14, 0, tzinfo=timezone.utc)


def source_packet():
    return seal_packet("us", body={"kind": "market", "source_health": "OK", "current": {
        "universe_coverage": {"status": "COMPLETE"}, "freshness_receipt": {
            "producer_run_id": "verified-run", "market_data_status": "FRESH",
            "market_data_oldest_at": AT.isoformat(), "market_data_latest_at": AT.isoformat(),
            "account_as_of": AT.isoformat(), "account_snapshot_health": "VALID",
            "analysis_lineage_status": "RESOLVED", "analysis_completed_at": AT.isoformat()}}})


@pytest.mark.parametrize("case", ["same", "new_source", "missing", "malformed", "future", "expired", "closed"])
def test_changed_or_expired_source_never_allocates_or_acknowledges_event(tmp_path, monkeypatch, case):
    packet = source_packet()
    receipt = packet["body"]["current"]["freshness_receipt"]
    if case == "new_source":
        receipt["producer_run_id"] = "published-during-read"
    elif case in {"missing", "malformed", "future"}:
        receipt["market_data_oldest_at"] = {"missing": None, "malformed": "bad",
            "future": (AT + timedelta(seconds=1)).isoformat()}[case]
    packet = seal_packet("us", body=packet["body"])
    original = deepcopy(packet)
    monkeypatch.setattr(work_runtime, "build_surface_packet", lambda *a, **k: packet)
    monkeypatch.setattr(pre_report, "market_session_state", lambda **k: {"is_open": case != "closed"})
    runtime = WorkRuntime(tmp_path)
    options = dict(now=AT + timedelta(minutes=11) if case == "expired" else AT, fresh_report=True,
        expected_producer_run_id="verified-run", refresh_started_at=AT)
    if case == "same":
        assert runtime.prepare("us", **options)["result"] == "NEW"
        assert runtime.ledger_path.exists()
    else:
        with pytest.raises(WorkRuntimeError, match="failed revalidation"):
            runtime.prepare("us", **options)
        assert not runtime.ledger_path.exists()
        assert not runtime.state_path.exists()
        assert not runtime.outbox_dir.exists()
    assert packet == original


@pytest.mark.parametrize("slow_read", ["packet", "calendar"])
def test_validation_uses_clock_after_packet_and_calendar_reads(tmp_path, monkeypatch, slow_read):
    now = [AT]
    def build(*args, **kwargs):
        if slow_read == "packet":
            now[0] += timedelta(minutes=11)
        return source_packet()
    def session(**kwargs):
        if slow_read == "calendar":
            now[0] += timedelta(minutes=11)
        return {"is_open": True}
    monkeypatch.setattr(work_runtime, "build_surface_packet", build)
    monkeypatch.setattr(work_runtime, "_now", lambda value: now[0].isoformat())
    monkeypatch.setattr(pre_report, "market_session_state", session)
    runtime = WorkRuntime(tmp_path)
    with pytest.raises(WorkRuntimeError, match="failed revalidation"):
        runtime.prepare("us", fresh_report=True, expected_producer_run_id="verified-run", refresh_started_at=AT)
    assert not runtime.state_path.exists()
    assert not runtime.ledger_path.exists()


@pytest.mark.parametrize("run_id,started,fresh", [
    (None, AT, True), ("", AT, True), ("verified-run", None, True),
    ("verified-run", AT.replace(tzinfo=None), True), ("verified-run", AT, False),
])
def test_incomplete_refresh_identity_fails_before_read(tmp_path, monkeypatch, run_id, started, fresh):
    monkeypatch.setattr(work_runtime, "build_surface_packet", lambda *a, **k: pytest.fail("invalid handoff"))
    with pytest.raises(WorkRuntimeError, match="exact producer run"):
        WorkRuntime(tmp_path).prepare("us", expected_producer_run_id=run_id,
            refresh_started_at=started, fresh_report=fresh)


@pytest.mark.parametrize("command,enabled,release_after,expected", [
    ("run-due", True, 40, True), ("run-due", True, 70, False),
    ("run-due", False, 40, False), ("publish", True, 40, False),
])
def test_minute_producer_waits_for_short_report_writer_without_overlapping(tmp_path, monkeypatch,
        publication_contention, command, enabled, release_after, expected):
    import json
    import sys
    from tradingagents import local_automation as local
    from tradingagents.notifications import local as notifications
    if enabled:
        p = tmp_path / "paper/enabled.json"
        p.parent.mkdir()
        p.write_text(json.dumps({"enabled": True, "mode": "LOCAL_PAPER_ONLY", "real_orders_enabled": False}))
    clock = publication_contention(release_after=release_after)
    calls = []
    monkeypatch.setattr(sys, "argv", ["local", command, "--archive-dir", str(tmp_path / "archive"),
        "--state-dir", str(tmp_path), "--runtime-dir", str(tmp_path / "runtime")])
    monkeypatch.setattr(local, "prepare_environment", lambda: None)
    monkeypatch.setattr(local, "drain_actions", lambda *a, **k: [])
    monkeypatch.setattr(local, "run_due", lambda *a, **k: calls.append(clock.elapsed) or [])
    monkeypatch.setattr(local, "publish", lambda *a, **k: pytest.fail("busy publisher must not enter"))
    monkeypatch.setattr(notifications, "reconcile_safely", lambda *a, **k: None)
    assert local.main() == 0
    assert bool(calls) is expected
    if expected:
        assert len(calls) == 1 and 40 <= calls[0] <= 40.1
    else:
        assert clock.elapsed <= 60
