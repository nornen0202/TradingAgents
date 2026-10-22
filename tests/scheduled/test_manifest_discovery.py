import json
from pathlib import Path

import pytest

from tradingagents.scheduled import manifest_discovery as discovery


def write(root, identity, mode="full", **extra):
    path = root / "runs" / "2026" / identity / "run.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"run_id": identity, "settings": {"run_mode": mode}, **extra}), encoding="utf-8")
    return path


def test_unchanged_overlays_are_not_reparsed_but_full_sources_are(tmp_path, monkeypatch):
    write(tmp_path, "01-full")
    overlays = [write(tmp_path, f"02-overlay-{i}", "overlay_only") for i in range(20)]
    first = discovery.full_manifests_desc(tmp_path)
    first[0][0]["run_id"] = "caller mutation"
    read = Path.read_text
    reads = []

    def tracked(path, *args, **kwargs):
        reads.append(path)
        return read(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", tracked)
    second = discovery.full_manifests_desc(tmp_path)
    assert second[0][0]["run_id"] == "01-full"
    assert all(path not in reads for path in overlays)
    assert tmp_path / "runs/2026/01-full/run.json" in reads


def test_new_changed_and_deleted_files_are_rediscovered(tmp_path):
    overlay = write(tmp_path, "01-change", "overlay_only")
    old_full = write(tmp_path, "02-delete")
    discovery.full_manifests_desc(tmp_path)
    write(tmp_path, "01-change", "full", revision="changed")
    write(tmp_path, "03-new")
    old_full.unlink()
    results = discovery.full_manifests_desc(tmp_path)
    assert [m["run_id"] for m, _ in results] == ["03-new", "01-change"]
    overlay.write_text("broken", encoding="utf-8")
    with pytest.raises(ValueError):
        discovery.full_manifests_desc(tmp_path)


@pytest.mark.parametrize("broken", ["{", "null", "[]", '{"schema":"old","entries":{}}'])
def test_corrupt_index_falls_back_to_original_files(tmp_path, broken):
    write(tmp_path, "full")
    (tmp_path / ".run-mode-discovery.json").write_text(broken, encoding="utf-8")
    assert len(discovery.full_manifests_desc(tmp_path)) == 1


def test_failed_cache_write_does_not_change_candidates(tmp_path, monkeypatch):
    write(tmp_path, "full", status="failed", started_at="2099-01-01")
    def denied(*args):
        raise PermissionError("read-only index")
    monkeypatch.setattr(discovery, "atomic_write_json", denied)
    # Discovery does not approve failed/future data: return the unchanged full
    # manifest so the existing baseline selector applies every original gate.
    result = discovery.full_manifests_desc(tmp_path)
    assert result[0][0]["status"] == "failed"
    assert result[0][0]["started_at"] == "2099-01-01"


def test_malformed_entry_is_reloaded(tmp_path):
    path = write(tmp_path, "full")
    cache = {"schema": discovery.SCHEMA, "entries": {
        "2026/full/run.json": {"signature": discovery._signature(path), "mode": []},
    }}
    (tmp_path / ".run-mode-discovery.json").write_text(json.dumps(cache), encoding="utf-8")
    assert discovery.full_manifests_desc(tmp_path)[0][0]["run_id"] == "full"


def test_file_replacement_during_read_is_not_negative_cached(tmp_path, monkeypatch):
    target = write(tmp_path, "changing", "overlay_only")
    original = Path.read_text
    changed = False
    def replace_after_read(path, *args, **kwargs):
        nonlocal changed
        value = original(path, *args, **kwargs)
        if path == target and not changed:
            changed = True
            write(tmp_path, "changing", "full", revision="new-completion")
        return value
    monkeypatch.setattr(Path, "read_text", replace_after_read)
    assert discovery.full_manifests_desc(tmp_path) == []
    assert discovery.full_manifests_desc(tmp_path)[0][0]["revision"] == "new-completion"


def test_legacy_missing_mode_and_empty_archive(tmp_path):
    assert discovery.full_manifests_desc(tmp_path) == []
    path = write(tmp_path, "legacy")
    path.write_text('{"run_id":"legacy"}', encoding="utf-8")
    assert discovery.full_manifests_desc(tmp_path)[0][0]["run_id"] == "legacy"
