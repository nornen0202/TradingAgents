from datetime import datetime, timedelta, timezone
import weakref

import pytest

from tradingagents.work import packet


class Manifest(dict):
    pass


def history(tmp_path, monkeypatch, *, ready=None):
    base = datetime(2026, 10, 22, tzinfo=timezone.utc)
    manifests, bundles, refs = {}, {}, []
    peak = 0
    for i in range(80):
        directory = tmp_path / "runs/2026" / f"run-{i:03}"
        directory.mkdir(parents=True)
        (directory / "run.json").touch()
        manifests[directory / "run.json"] = {
            "run_id": directory.name, "started_at": (base + timedelta(minutes=i)).isoformat(),
            "settings": {"market": "US"},
        }
        bundles[directory / "decision_bundle_v2.json"] = {"quality": {"decision_ready": i == ready}}

    def load(path):
        nonlocal peak
        if path in manifests:
            result = Manifest(manifests[path])
            refs.append(weakref.ref(result))
            peak = max(peak, sum(ref() is not None for ref in refs))
            return result
        return bundles.get(path, {})

    monkeypatch.setattr(packet, "load_json", load)
    return manifests, lambda: peak


@pytest.mark.parametrize("ready,expected", [(None, [79]), (42, [79, 42]), (79, [79])])
def test_work_discovery_keeps_only_current_and_first_ready_source(tmp_path, monkeypatch, ready, expected):
    _, peak = history(tmp_path, monkeypatch, ready=ready)
    selected = packet._market_sources(tmp_path, "us")
    assert [row["manifest"]["run_id"] for row in selected] == [f"run-{i:03}" for i in expected]
    assert peak() <= 3  # Retention stays bounded as the archive grows.


def test_discovery_uses_actual_producer_clock_not_directory_or_modified_order(tmp_path, monkeypatch):
    manifests, _ = history(tmp_path, monkeypatch)
    first = next(p for p in manifests if p.parent.name == "run-000")
    manifests[first]["started_at"] = "2026-10-22T10:00:00Z"
    selected = packet._market_sources(tmp_path, "us")
    assert selected[0]["manifest"]["run_id"] == "run-000"


def test_changed_producer_clock_cannot_reorder_sources_silently(tmp_path, monkeypatch):
    manifests, _ = history(tmp_path, monkeypatch)
    load = packet.load_json
    calls = {}

    def changing(path):
        result = load(path)
        if path in manifests:
            calls[path] = calls.get(path, 0) + 1
            if calls[path] == 2:
                result["started_at"] = "2026-10-23T00:00:00Z"
        return result

    monkeypatch.setattr(packet, "load_json", changing)
    with pytest.raises(ValueError, match="changed during discovery"):
        packet._market_sources(tmp_path, "us")


def test_empty_archive_has_no_sources(tmp_path):
    assert packet._market_sources(tmp_path, "us") == []


def test_discovery_overlaps_two_reads_without_changing_selection_or_retention(tmp_path, monkeypatch):
    from threading import Barrier, Lock
    _, peak = history(tmp_path, monkeypatch, ready=42)
    load = packet.load_json
    barrier, lock = Barrier(2), Lock()
    calls = 0
    def overlapping(path):
        nonlocal calls
        with lock:
            calls += 1
            position = calls
        if position <= 2:
            barrier.wait(timeout=5)
        return load(path)
    monkeypatch.setattr(packet, "load_json", overlapping)
    selected = packet._market_sources(tmp_path, "us")
    assert [row["manifest"]["run_id"] for row in selected] == ["run-079", "run-042"]
    assert peak() <= 3
