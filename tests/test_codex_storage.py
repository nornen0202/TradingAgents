from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import time
import sys
from datetime import datetime, timedelta, timezone
import zipfile
import io
import hashlib

import pytest

spec = importlib.util.spec_from_file_location("codex_storage", Path(__file__).parents[1] / "tools" / "maintain_codex_storage.py")
storage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(storage)
sys.path.insert(0, str(Path(__file__).parents[1] / "tools"))
import maintain_codex_storage_policy as policy


def fixture(tmp_path):
    source = tmp_path / "source" / "closed"
    source.mkdir(parents=True)
    (source / "payload.bin").write_bytes(b"preserve me" * 4096)
    (source / "nested").mkdir()
    (source / "nested" / "settings.json").write_text('{"local":true}')
    item = {"id": "fixture", "source": str(source), "source_root": str(source.parent),
            "destination": str(tmp_path / "target" / "closed"), "destination_root": str(tmp_path / "target"), "quiet_hours": 0}
    return source, item, tmp_path / "backups", tmp_path / "journal"


def test_boundary_refuses_root_and_sibling(tmp_path):
    with pytest.raises(ValueError):
        storage.assert_child(tmp_path, tmp_path)
    with pytest.raises(ValueError):
        storage.assert_child(tmp_path.parent / "sibling", tmp_path)


def test_active_process_is_preserved(tmp_path):
    source, item, backup, journal = fixture(tmp_path)
    record = storage.prepare(item, backup, journal, apply=True,
                             processes=[{"Name": "python.exe", "ProcessId": 99, "cwd": str(source), "CommandLine": "python job.py"}])
    assert record["reason"] == "active-process"
    assert source.exists() and not backup.exists()


def test_recent_writes_are_preserved(tmp_path):
    source, item, backup, journal = fixture(tmp_path)
    item["quiet_hours"] = 48
    assert storage.prepare(item, backup, journal, apply=True, processes=[])["reason"] == "recent-write"
    assert source.exists()


def test_dry_run_writes_nothing(tmp_path):
    source, item, backup, journal = fixture(tmp_path)
    record = storage.prepare(item, backup, journal, apply=False, processes=[])
    assert record["phase"] == "planned"
    assert not backup.exists() and not journal.exists() and source.exists()


def test_verified_offload_keeps_original_until_finalize(tmp_path, monkeypatch):
    source, item, backup, journal = fixture(tmp_path)
    monkeypatch.setattr(storage, "process_references", lambda: [])
    record = storage.prepare(item, backup, journal, apply=True, processes=[])
    assert record["phase"] == "prepared"
    assert storage.is_reparse(source)
    assert Path(record["stage"]).is_dir()
    assert (source / "payload.bin").read_bytes() == b"preserve me" * 4096
    storage.finalize(record, journal)
    assert not Path(record["stage"]).exists()
    assert (source / "nested" / "settings.json").read_text() == '{"local":true}'
    assert json.loads((journal / "fixture.json").read_text())["phase"] == "finalized"


def test_corrupt_backup_prevents_original_removal(tmp_path, monkeypatch):
    source, item, backup, journal = fixture(tmp_path)
    monkeypatch.setattr(storage, "process_references", lambda: [])
    record = storage.prepare(item, backup, journal, apply=True, processes=[])
    Path(record["archive"]).write_bytes(b"corrupt")
    with pytest.raises(Exception):
        storage.finalize(record, journal)
    assert Path(record["stage"]).exists()


def test_nested_junction_is_refused(tmp_path):
    source, item, backup, journal = fixture(tmp_path)
    external = tmp_path / "external"
    external.mkdir()
    (external / "keep.txt").write_text("safe")
    storage.make_junction(source / "linked", external)
    with pytest.raises(ValueError, match="reparse"):
        storage.prepare(item, backup, journal, apply=True, processes=[])
    assert (external / "keep.txt").read_text() == "safe"


def test_changed_original_blocks_finalization(tmp_path, monkeypatch):
    source, item, backup, journal = fixture(tmp_path)
    monkeypatch.setattr(storage, "process_references", lambda: [])
    record = storage.prepare(item, backup, journal, apply=True, processes=[])
    stage = Path(record["stage"])
    (stage / "payload.bin").write_bytes(b"changed after verification")
    with pytest.raises(RuntimeError, match="verification failed"):
        storage.finalize(record, journal)
    assert (stage / "payload.bin").read_bytes() == b"changed after verification"


def test_worker_retention_requires_success_and_keeps_latest_two(tmp_path):
    archive = tmp_path / "runs"
    workers = tmp_path / "workers"
    workers.mkdir()
    now = datetime.now(timezone.utc)
    for index, status in enumerate(["success", "success", "success", "running", "failed"]):
        name = f"2026090{index+1}T010101_local-scheduler-kr-full"
        folder = archive / "2026" / name
        folder.mkdir(parents=True)
        (folder / "run.json").write_text(json.dumps({"run_id": name, "status": status,
                                                     "finished_at": (now - timedelta(days=30-index)).isoformat()}))
        (workers / name).mkdir()
    config = {"archive_roots": [str(archive)], "workers": [{"id": "worker", "root": str(workers), "retention_days": 7, "keep_latest": 2}]}
    items = policy.candidates(config)
    assert len(items) == 1
    assert Path(items[0]["source"]).name.startswith("20260901")


def test_partial_date_does_not_overwrite_existing_destination(tmp_path):
    root = tmp_path / "documents"
    destination = tmp_path / "offloaded"
    date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    (root / date / "closed-chat").mkdir(parents=True)
    (destination / date).mkdir(parents=True)
    items = policy.candidates({"documents": {"root": str(root), "destination_root": str(destination)}})
    assert len(items) == 1
    assert Path(items[0]["source"]).name == "closed-chat"


def test_partial_date_preserves_another_transactions_staged_original(tmp_path):
    root, destination = tmp_path / "documents", tmp_path / "offloaded"
    date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    stage = root / date / "closed-chat.storage-original"
    stage.mkdir(parents=True)
    (stage / "payload.txt").write_text("owned by another migration")
    (destination / date).mkdir(parents=True)
    assert policy.candidates({"documents": {"root": str(root), "destination_root": str(destination)}}) == []
    assert (stage / "payload.txt").read_text() == "owned by another migration"


def test_wrong_volume_blocks_changes(monkeypatch):
    monkeypatch.setattr(storage, "volume_serial", lambda path: "WRONG")
    with pytest.raises(RuntimeError, match="not mounted"):
        storage.validate_volumes({"volumes": {"G:\\": "EXPECTED"}})


def test_registered_relocation_audit_reports_replaced_alias_without_repair(tmp_path):
    source, destination = tmp_path / "old-path", tmp_path / "offloaded"
    destination.mkdir()
    (destination / "saved.txt").write_text("keep")
    storage.make_junction(source, destination)
    config = {"relocations": [{"id": "saved", "source": str(source), "destination": str(destination)}]}
    assert policy.audit_relocations(config)
    if source.is_symlink():
        source.unlink()
    else:
        source.rmdir()
    source.mkdir()
    (source / "new.txt").write_text("new application data")
    assert not policy.audit_relocations(config)
    assert (source / "new.txt").read_text() == "new application data"
    assert (destination / "saved.txt").read_text() == "keep"


def test_relocation_mismatch_fails_task_without_removing_either_copy(tmp_path, monkeypatch):
    source, destination = tmp_path / "old-path", tmp_path / "offloaded"
    source.mkdir()
    destination.mkdir()
    (source / "new.txt").write_text("new data")
    (destination / "saved.txt").write_text("saved data")
    config = tmp_path / "policy.json"
    config.write_text(json.dumps({"enabled": True, "system_drive": str(tmp_path),
                                  "backup_root": str(tmp_path / "backups"), "journal_root": str(tmp_path / "journal"),
                                  "relocations": [{"id": "saved", "source": str(source), "destination": str(destination)}]}))
    monkeypatch.setattr(sys, "argv", ["policy", "--config", str(config)])
    monkeypatch.setattr(policy.storage, "process_references", lambda: [])
    assert policy.main() == 2
    assert (source / "new.txt").read_text() == "new data"
    assert (destination / "saved.txt").read_text() == "saved data"


@pytest.mark.parametrize("free,critical,expected", [(20, 12, 0), (8, 12, 2), (8, 0, 0)])
def test_critical_capacity_is_visible_as_task_failure_but_warning_is_not(tmp_path, monkeypatch, free, critical, expected):
    from types import SimpleNamespace
    config = tmp_path / "policy.json"
    config.write_text(json.dumps({"enabled": True, "system_drive": str(tmp_path),
                                  "backup_root": str(tmp_path / "backups"), "journal_root": str(tmp_path / "journal"),
                                  "warning_free_bytes": 30, "critical_free_bytes": critical}))
    monkeypatch.setattr(sys, "argv", ["policy", "--config", str(config)])
    monkeypatch.setattr(policy.storage, "process_references", lambda: [])
    monkeypatch.setattr(policy.shutil, "disk_usage", lambda path: SimpleNamespace(free=free))
    assert policy.main() == expected


def test_forward_archive_has_standard_readable_data_descriptors(tmp_path):
    path = tmp_path / "stream.zip"
    with path.open("xb", buffering=1024 * 1024) as handle, zipfile.ZipFile(storage.ForwardOnlyArchive(handle), "w") as saved:
        saved.writestr("first.txt", b"first")
        saved.writestr("second.txt", b"second")
    with zipfile.ZipFile(path) as saved:
        assert saved.testzip() is None
        assert saved.read("first.txt") == b"first"
        assert saved.read("second.txt") == b"second"
        assert all(item.flag_bits & 8 for item in saved.infolist())


@pytest.mark.parametrize("size", [0, 1, 65537, 300001])
def test_reused_hash_buffer_handles_short_reads_and_empty_files(size):
    payload = (b"checksums remain exact" * ((size // 22) + 1))[:size]
    reusable = bytearray(256 * 1024)
    assert storage.stream_sha256(io.BytesIO(payload), buffer=reusable) == hashlib.sha256(payload).hexdigest()
    assert storage.stream_sha256(io.BytesIO(b"next file"), buffer=reusable) == hashlib.sha256(b"next file").hexdigest()
