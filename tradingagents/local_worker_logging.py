"""Capture one local worker's output in bounded, rotating files."""

from __future__ import annotations

import argparse
from contextlib import ExitStack
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import subprocess
import sys

from tradingagents.atomic_io import interprocess_file_lock


class _Utf8RotatingFileHandler(RotatingFileHandler):
    def shouldRollover(self, record):
        if self.stream is None:
            self.stream = self._open()
        self.stream.seek(0, os.SEEK_END)
        position = self.stream.tell()
        size = len(self.format(record).encode("utf-8")) + len(os.linesep)
        return bool(position and position + size > self.maxBytes)


def capture_worker(destination: Path, arguments: list[str], *, max_bytes: int = 10 * 1024 * 1024,
                   backups: int = 5) -> int:
    if not arguments or type(max_bytes) is not int or max_bytes < 32 or type(backups) is not int or not 1 <= backups <= 20:
        raise ValueError("A worker command and bounded rotation policy are required")
    if destination.is_symlink():
        raise ValueError("Worker log cannot be a linked file")
    destination = destination.parent.resolve() / destination.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    with ExitStack() as stack:
        try:
            stack.enter_context(interprocess_file_lock(destination.with_suffix(".log.lock"), timeout=0))
        except TimeoutError:
            # An overlapping caller gets its own file while the lane's
            # producer lock determines whether it has work to run.
            destination = destination.with_name(f"{destination.stem}-{os.getpid()}{destination.suffix}")
            stack.enter_context(interprocess_file_lock(destination.with_suffix(".log.lock"), timeout=0))
        return _capture(destination, arguments, max_bytes=max_bytes, backups=backups)


def _capture(destination, arguments, *, max_bytes, backups):
    handler = _Utf8RotatingFileHandler(destination, maxBytes=max_bytes, backupCount=backups, encoding="utf-8")
    try:
        with subprocess.Popen(
            [sys.executable, *arguments], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace",
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        ) as process:
            if process.stdout is None:
                raise RuntimeError("Worker output pipe unavailable")
            # Limit even a message written without a newline. A UTF-8 code
            # point is at most four bytes, with one extra line delimiter.
            chunk = min(16384, (max_bytes - 2) // 4)
            while output := process.stdout.readline(chunk):
                record = logging.LogRecord("local-worker", logging.INFO, "", 0, output.rstrip("\r\n"), (), None)
                handler.handle(record)
            return process.wait()
    finally:
        handler.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("worker", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    worker = args.worker[1:] if args.worker[:1] == ["--"] else args.worker
    return capture_worker(args.log, worker)


if __name__ == "__main__":
    raise SystemExit(main())
