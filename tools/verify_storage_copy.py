"""Verify a quiesced directory copy before a storage cutover. Never deletes files.

Both roots must remain frozen during verification and cutover. Reparse points,
unreadable files, concurrent changes, extra files and corrupt SQLite DBs fail closed.
The receipt is evidence, not an authorization to delete an active destination.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import shutil
import tempfile
import time


def inventory(root):
    root = Path(root)
    files, directories = {}, set()
    pending = [(str(root), "")]
    while pending:
        directory, prefix = pending.pop()
        with os.scandir(directory) as entries:
            for entry in entries:
                # Windows scandir already supplies metadata; avoid millions of
                # additional stat/open calls on the archive's small files.
                stat = entry.stat(follow_symlinks=False)
                if entry.is_symlink() or getattr(stat, "st_file_attributes", 0) & 0x400:
                    raise ValueError(f"Linked entry is not a plain copy: {entry.path}")
                relative = prefix + entry.name
                if entry.is_dir(follow_symlinks=False):
                    directories.add(relative)
                    pending.append((entry.path, relative + "/"))
                else:
                    files[relative] = (stat.st_size, stat.st_mtime_ns)
    return files, directories


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def verify(source, destination, receipt, *, workers=8):
    source, destination = Path(source).resolve(strict=True), Path(destination).resolve(strict=True)
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError("Copy roots must be separate, non-overlapping directories")
    started = time.time()
    original, directories = inventory(source)
    copied, copied_directories = inventory(destination)
    errors = []
    extras = sorted((copied.keys() - original.keys()) | (copied_directories - directories))
    missing = sorted((original.keys() - copied.keys()) | (directories - copied_directories))
    def check(relative):
        left, right = source / relative, destination / relative
        if original[relative][0] != copied.get(relative, (None,))[0]:
            return relative, "size-or-missing"
        try:
            if digest(left) != digest(right):
                return relative, "content-mismatch"
            # SQLite magic avoids mistaking other .db files for SQLite.
            with left.open("rb") as stream:
                sqlite = stream.read(16) == b"SQLite format 3\x00"
            if sqlite:
                # Even mode=ro may update/remove WAL shared-memory sidecars.
                # Validate a private clone, never open either frozen tree as a
                # SQLite connection while other threads hash its sidecars.
                with tempfile.TemporaryDirectory(dir=Path(receipt).parent) as scratch:
                    clone = Path(scratch) / "check.sqlite"
                    shutil.copyfile(left, clone)
                    for suffix in ("-wal", "-journal"):
                        sidecar = Path(str(left) + suffix)
                        if sidecar.exists():
                            shutil.copyfile(sidecar, Path(str(clone) + suffix))
                    with closing(sqlite3.connect(clone.as_uri() + "?mode=ro", uri=True, timeout=10)) as db:
                        if db.execute("PRAGMA quick_check").fetchall() != [("ok",)]:
                            return relative, "sqlite-integrity"
        except (OSError, sqlite3.Error) as exc:
            return relative, type(exc).__name__
        return None
    names = list(original)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for offset in range(0, len(names), 2000):
            for result in pool.map(check, names[offset:offset + 2000]):
                if result:
                    errors.append(result)
                    print(json.dumps({"mismatch": result}), flush=True)
            if offset % 20000 == 0:
                print(json.dumps({"verified": min(offset + 2000, len(names)), "total": len(names),
                                  "errors": len(errors)}), flush=True)
    unchanged = inventory(source) == (original, directories) and inventory(destination) == (copied, copied_directories)
    result = {"source": str(source), "destination": str(destination), "files": len(original),
              "bytes": sum(row[0] for row in original.values()), "errors": errors,
              "missing": missing, "extras": extras, "unchanged": unchanged,
              "verified": not errors and not missing and not extras and unchanged,
              "started_at": started, "finished_at": time.time()}
    Path(receipt).write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    result = verify(args.source, args.destination, args.receipt, workers=args.workers)
    print(json.dumps({key: result[key] for key in ("verified", "files", "bytes", "unchanged")}))
    raise SystemExit(0 if result["verified"] else 1)
