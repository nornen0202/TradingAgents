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

    def handleError(self, record):
        # The standard handler swallows write/rollover errors after printing a
        # traceback for each lost record. Switch sinks or report one failure.
        raise OSError("Worker log emission failed") from None


def capture_worker(destination: Path, arguments: list[str], *, max_bytes: int = 10 * 1024 * 1024,
                   backups: int = 5, started_marker: Path | None = None) -> int:
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
            # The business lane lock still owns execution deduplication.
            destination = destination.with_name(f"{destination.stem}-{os.getpid()}{destination.suffix}")
            stack.enter_context(interprocess_file_lock(destination.with_suffix(".log.lock"), timeout=0))
        return _capture(destination, arguments, max_bytes=max_bytes, backups=backups, started_marker=started_marker)


def _new_handler(destination, max_bytes, backups):
    handler = _Utf8RotatingFileHandler(destination, maxBytes=max_bytes, backupCount=backups, encoding="utf-8")
    try:
        with destination.open("rb") as old:
            bom = old.read(2)
        if bom in (bytes((255, 254)), bytes((254, 255))):
            handler.doRollover()
    except OSError:
        handler.close()
        raise
    return handler


def _capture(destination, arguments, *, max_bytes, backups, started_marker):
    handler = _new_handler(destination, max_bytes, backups)
    switched = failed = False
    try:
        with ExitStack() as startup:
            marker = startup.enter_context(started_marker.open("x", encoding="ascii")) if started_marker else None
            with subprocess.Popen(
                [sys.executable, *arguments], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace",
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            ) as process:
                if marker is not None:
                    marker.write("STARTED")
                    marker.flush()
                if process.stdout is None:
                    raise RuntimeError("Worker output pipe unavailable")
                chunk = min(16384, (max_bytes - 2) // 4)
                while output := process.stdout.readline(chunk):
                    if failed:
                        continue  # Drain the worker pipe through its actual exit.
                    record = logging.LogRecord("local-worker", logging.INFO, "", 0, output.rstrip("\r\n"), (), None)
                    try:
                        handler.handle(record)
                    except OSError:
                        if not switched:
                            switched = True
                            handler.close()
                            fallback = destination.with_name(f"{destination.stem}-fallback{destination.suffix}")
                            try:
                                handler = _new_handler(fallback, max_bytes, backups)
                                handler.handle(record)
                                print("Worker log moved to a bounded fallback file.", file=sys.stderr)
                                continue
                            except OSError:
                                pass
                        failed = True
                        print("Worker output sink failed after launch.", file=sys.stderr)
                result = process.wait()
                return result or (74 if failed else 0)
    finally:
        handler.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--started-marker", type=Path)
    parser.add_argument("worker", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    worker = args.worker[1:] if args.worker[:1] == ["--"] else args.worker
    return capture_worker(args.log, worker, started_marker=args.started_marker)


if __name__ == "__main__":
    raise SystemExit(main())
