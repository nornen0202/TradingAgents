from datetime import datetime, timedelta
import json

import pytest

from tradingagents.prism_telegram import collection_gate as gate
from tradingagents.local_advisory_recovery import RecoveryDiagnostic


NOW = datetime.fromisoformat("2026-10-14T14:30:00+09:00")


def manifest(archive, *, start=NOW - timedelta(hours=1), channel="stock_ai_agent", **changes):
    run_id = "prism_telegram_" + start.strftime("%Y%m%d_%H%M%S")
    path = archive / "runs" / str(start.year) / run_id / "prism_telegram_run.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"run_id": run_id, "status": "success", "source": {"channel": channel},
               "started_at": start.isoformat(), "finished_at": (start + timedelta(minutes=10)).isoformat(),
               "summary": {"messages": 4, "warnings": 0}, **changes}
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def collect(archive, *, automatic=True, now=NOW):
    return gate.should_collect(archive=archive, channel="stock_ai_agent", now=now, automatic=automatic)


@pytest.mark.parametrize("messages", [0, 4])
def test_late_native_and_recovery_probe_skip_completed_collection_even_without_publication(tmp_path, messages):
    manifest(tmp_path, summary={"messages": messages, "warnings": 0})
    assert not collect(tmp_path)
    assert collect(tmp_path, automatic=False)  # Explicit manual collection stays available.


def test_current_session_remains_due_after_failed_or_other_source_or_previous_day_collection(tmp_path):
    manifest(tmp_path, status="partial_failure")
    manifest(tmp_path, start=NOW - timedelta(hours=2), channel="other")
    old = manifest(tmp_path, start=NOW - timedelta(days=1))
    old.write_text("damaged old evidence")
    assert collect(tmp_path)


def test_concurrent_incomplete_manifest_does_not_claim_completion(tmp_path):
    manifest(tmp_path, status="running")
    assert collect(tmp_path)


@pytest.mark.parametrize("changes", [
    {"summary": {"messages": 4, "warnings": 1}},
    {"source": {}}, {"finished_at": "broken"}, {"run_id": "wrong"},
    {"finished_at": (NOW + timedelta(hours=1)).isoformat()},
])
def test_unverified_success_stops_automatic_collection_without_overwriting_evidence(tmp_path, changes):
    path = manifest(tmp_path, **changes)
    before = path.read_bytes()
    with pytest.raises(RecoveryDiagnostic):
        collect(tmp_path)
    assert path.read_bytes() == before


def test_corrupt_current_manifest_fails_closed(tmp_path):
    path = manifest(tmp_path)
    path.write_text("broken")
    with pytest.raises(RecoveryDiagnostic, match="CANONICAL_INVALID"):
        collect(tmp_path)


def test_midnight_gate_uses_previous_0735_session(tmp_path):
    manifest(tmp_path)
    assert not collect(tmp_path, now=NOW.replace(day=15, hour=0, minute=30))
    assert collect(tmp_path, now=NOW.replace(day=15, hour=8, minute=0))


@pytest.mark.parametrize("event,source,expected", [
    ("schedule", "native", False), ("workflow_dispatch", "local_watchdog", False),
    ("workflow_dispatch", "cloud_watchdog", False), ("workflow_dispatch", "manual", True),
])
def test_entrypoint_uses_configured_archive_and_keeps_recovery_gate_enabled(tmp_path, monkeypatch, event, source, expected):
    from types import SimpleNamespace
    manifest(tmp_path)
    output = tmp_path / "output.txt"
    monkeypatch.setattr(gate, "load_prism_telegram_config", lambda _: SimpleNamespace(
        storage=SimpleNamespace(archive_dir=tmp_path), source=SimpleNamespace(channel="stock_ai_agent")))
    class Clock:
        @staticmethod
        def now(zone):
            return NOW.astimezone(zone)
    monkeypatch.setattr(gate, "datetime", type("Clock", (Clock,), {"strptime": datetime.strptime}))
    for key, value in {"GH_EVENT_NAME": event, "RECOVERY_SOURCE": source, "GITHUB_OUTPUT": str(output)}.items():
        monkeypatch.setenv(key, value)
    gate.main()
    assert output.read_text().strip() == f"should_run={'true' if expected else 'false'}"
