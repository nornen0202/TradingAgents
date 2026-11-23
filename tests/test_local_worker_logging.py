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


def test_legacy_utf16_is_rotated_before_utf8_and_marks_worker_started(tmp_path):
    path = tmp_path / "lane.log"
    start = tmp_path / "worker.started"
    path.write_text("old worker", encoding="utf-16")
    assert capture_worker(path, ["-c", "print('new worker')"], max_bytes=128, backups=2, started_marker=start) == 0
    assert path.read_text(encoding="utf-8").strip() == "new worker"
    assert path.with_name("lane.log.1").read_text(encoding="utf-16") == "old worker"
    assert start.read_text(encoding="ascii") == "STARTED"


def test_rotation_lock_moves_output_to_one_bounded_fallback(tmp_path, monkeypatch, capsys):
    from tradingagents.local_worker_logging import _Utf8RotatingFileHandler
    rotate = _Utf8RotatingFileHandler.doRollover
    path = tmp_path / "lane.log"

    def locked(self):
        if self.baseFilename == str(path):
            raise PermissionError("fixture keeps original log open")
        return rotate(self)

    monkeypatch.setattr(_Utf8RotatingFileHandler, "doRollover", locked)
    code = "for i in range(10): print('fixture-' + 'x' * 30); print('last-line')"
    assert capture_worker(path, ["-u", "-c", code], max_bytes=128, backups=2) == 0
    fallback = tmp_path / "lane-fallback.log"
    assert "last-line" in fallback.read_text(encoding="utf-8")
    assert "bounded fallback" in capsys.readouterr().err
    assert all(item.stat().st_size <= 128 for item in tmp_path.glob("lane*.log*") if item.suffix != ".lock")


def test_unopenable_log_does_not_claim_that_worker_started(tmp_path):
    path = tmp_path / "lane.log"
    path.mkdir()
    started = tmp_path / "worker.started"
    with pytest.raises(OSError):
        capture_worker(path, ["-c", "pass"], started_marker=started)
    assert not started.exists()


def test_both_sinks_failing_drains_child_and_reports_controlled_failure(tmp_path, monkeypatch, capsys):
    import sys
    from tradingagents.local_worker_logging import _Utf8RotatingFileHandler

    def locked(self):
        raise PermissionError("fixture sinks cannot rotate")

    monkeypatch.setattr(_Utf8RotatingFileHandler, "doRollover", locked)
    finished = tmp_path / "finished"
    code = "from pathlib import Path; import sys; [print('x' * 40) for i in range(30)]; Path(sys.argv[1]).touch()"
    assert capture_worker(tmp_path / "lane.log", ["-u", "-c", code, str(finished)], max_bytes=96, backups=2) == 74
    assert finished.exists()
    assert capsys.readouterr().err.count("Worker output sink failed") == 1
