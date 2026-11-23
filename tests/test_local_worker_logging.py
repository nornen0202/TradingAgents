import os

import pytest

from tradingagents.atomic_io import interprocess_file_lock
from tradingagents.local_worker_logging import capture_worker


def test_rotates_combined_output_and_preserves_child_exit(tmp_path):
    path = tmp_path / "lane.log"
    code = "import sys; [print('fixture-' + 'z' * 30) for i in range(20)]; print('last-marker', file=sys.stderr); sys.exit(7)"
    assert capture_worker(path, ["-u", "-c", code], max_bytes=128, backups=2) == 7
    assert "last-marker" in path.read_text(encoding="utf-8")
    assert len(list(tmp_path.glob("lane.log.[0-9]"))) == 2
    assert all(item.stat().st_size <= 128 for item in tmp_path.glob("lane.log*") if item.suffix != ".lock")


def test_overlap_keeps_original_stream_and_separate_log(tmp_path):
    path = tmp_path / "lane.log"
    path.write_text("original")
    with interprocess_file_lock(path.with_suffix(".log.lock"), timeout=0):
        assert capture_worker(path, ["-c", "print('overlap')"], max_bytes=128, backups=2) == 0
    assert path.read_text() == "original"
    assert "overlap" in (tmp_path / f"lane-{os.getpid()}.log").read_text()


def test_unicode_rotation_counts_encoded_bytes_and_preserves_tail(tmp_path):
    path = tmp_path / "lane.log"
    script = "import sys; sys.stdout.buffer.write(('한' * 80 + '\\n끝\\n').encode('utf-8'))"
    assert capture_worker(path, ["-c", script], max_bytes=64, backups=3) == 0
    assert path.read_text(encoding="utf-8").splitlines()[-1] == "끝"
    assert all(item.stat().st_size <= 64 for item in tmp_path.glob("lane.log*") if item.suffix != ".lock")


def test_capture_failure_does_not_relaunch_worker(tmp_path, monkeypatch):
    calls = []

    def fail(*args, **kwargs):
        calls.append("ran")
        raise TimeoutError

    monkeypatch.setattr("tradingagents.local_worker_logging._capture", fail)
    with pytest.raises(TimeoutError):
        capture_worker(tmp_path / "log", ["-c", "pass"])
    assert calls == ["ran"]
