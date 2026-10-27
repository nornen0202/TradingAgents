import importlib.util
from pathlib import Path
import sqlite3
import shutil

import pytest

spec = importlib.util.spec_from_file_location("verify_storage_copy", Path(__file__).parents[1] / "tools/verify_storage_copy.py")
copy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(copy)


@pytest.mark.parametrize("fault", [None, "missing", "extra", "changed"])
def test_frozen_copy_verifies_bytes_and_inventory(tmp_path, fault):
    source, destination = tmp_path / "source", tmp_path / "destination"
    source.mkdir(); destination.mkdir()
    (source / "report.json").write_text("original")
    (destination / "report.json").write_text("modified" if fault == "changed" else "original")
    if fault == "missing":
        (destination / "report.json").unlink()
    if fault == "extra":
        (destination / "stale.json").write_text("stale")
    result = copy.verify(source, destination, tmp_path / "receipt.json")
    assert result["verified"] is (fault is None)
    assert (source / "report.json").read_text() == "original"


def test_sqlite_and_changed_source_fail_closed(tmp_path, monkeypatch):
    source, destination = tmp_path / "source", tmp_path / "destination"
    source.mkdir(); destination.mkdir()
    with sqlite3.connect(source / "ledger.sqlite") as db:
        db.execute("CREATE TABLE ledger (value INTEGER)")
    (destination / "ledger.sqlite").write_bytes((source / "ledger.sqlite").read_bytes())
    assert copy.verify(source, destination, tmp_path / "receipt.json")["verified"]
    real = copy.digest
    def changing(path):
        value = real(path)
        (source / "new-report.json").write_text("concurrent write")
        return value
    monkeypatch.setattr(copy, "digest", changing)
    assert not copy.verify(source, destination, tmp_path / "receipt.json")["verified"]


def test_overlapping_roots_rejected(tmp_path):
    destination = tmp_path / "copy"
    destination.mkdir()
    with pytest.raises(ValueError, match="non-overlapping"):
        copy.verify(tmp_path, destination, tmp_path / "receipt.json")


def test_wal_integrity_check_never_opens_original_database(tmp_path):
    source, destination = tmp_path / "source", tmp_path / "destination"
    source.mkdir(); destination.mkdir()
    with sqlite3.connect(source / "ledger.sqlite") as db:
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA wal_autocheckpoint=0")
        db.execute("CREATE TABLE ledger (value INTEGER)")
        db.execute("INSERT INTO ledger VALUES (7)")
        db.commit()
        for path in source.iterdir():
            shutil.copy2(path, destination / path.name)
        before = {p.name: p.read_bytes() for p in source.iterdir()}
        result = copy.verify(source, destination, tmp_path / "receipt.json")
        assert result["verified"]
        assert before == {p.name: p.read_bytes() for p in source.iterdir()}
