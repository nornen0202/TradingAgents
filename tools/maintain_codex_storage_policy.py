"""Conservative daily retention for Codex documents, completed workers and caches."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

import maintain_codex_storage as storage


def completed_runs(archive_roots: list[str]) -> dict[str, dict]:
    completed = {}
    for root in archive_roots:
        path = Path(root)
        if not path.exists() or storage.is_reparse(path):
            continue
        for manifest in path.glob("*/*/run.json"):
            try:
                record = json.loads(manifest.read_text(encoding="utf-8"))
                if record.get("status") == "success" and record.get("finished_at") and record.get("run_id") == manifest.parent.name:
                    completed[manifest.parent.name] = record
            except (OSError, ValueError):
                continue
    return completed


def candidates(config: dict, now: datetime | None = None) -> list[dict]:
    now = now or datetime.now()
    items = []
    docs = config.get("documents", {})
    if docs:
        root, destination = Path(docs["root"]), Path(docs["destination_root"])
        cutoff = (now - timedelta(days=docs.get("retention_days", 7))).date()
        if root.exists() and not storage.is_reparse(root):
            for folder in root.iterdir():
                if not folder.is_dir() or storage.is_reparse(folder) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", folder.name):
                    continue
                if datetime.strptime(folder.name, "%Y-%m-%d").date() >= cutoff:
                    continue
                target = destination / folder.name
                # Preserve partially offloaded dates: move only remaining ordinary
                # chat folders, without traversing the existing child junctions.
                sources = [(folder, root, target)] if not target.exists() else [
                    (child, folder, target / child.name) for child in folder.iterdir()
                    if child.is_dir() and not storage.is_reparse(child) and not (target / child.name).exists()
                ]
                for source, bound, target in sources:
                    key = re.sub(r"[^A-Za-z0-9_.-]", "-", str(source.relative_to(root)))
                    items.append({"id": "documents-" + key, "source": str(source), "source_root": str(bound),
                                  "destination": str(target), "destination_root": str(destination), "quiet_hours": 48})
    completed = completed_runs(config.get("archive_roots", []))
    for specification in config.get("workers", []):
        root = Path(specification["root"])
        if not root.exists() or storage.is_reparse(root):
            continue
        folders = sorted((p for p in root.iterdir() if p.is_dir() and not storage.is_reparse(p) and p.name in completed),
                         key=lambda p: completed[p.name]["finished_at"], reverse=True)
        keep = {p.name for p in folders[:specification.get("keep_latest", 2)]}
        cutoff = now.timestamp() - specification.get("retention_days", 7) * 86400
        for folder in folders:
            finished = datetime.fromisoformat(completed[folder.name]["finished_at"]).timestamp()
            if folder.name in keep or finished >= cutoff:
                continue
            items.append({"id": specification["id"] + "-" + folder.name, "source": str(folder),
                          "source_root": str(root), "quiet_hours": 48})
    return items


def archive_old_dumps(config: dict, *, apply: bool, processes: list[dict]) -> None:
    specification = config.get("crash_dumps")
    if not specification:
        return
    root = Path(specification["root"])
    if not root.exists() or storage.is_reparse(root):
        return
    files = sorted((p for p in root.glob("*.dmp") if not storage.is_reparse(p)), key=lambda p: p.stat().st_mtime, reverse=True)
    keep = set(files[:specification.get("keep_latest", 2)])
    cutoff = time.time() - specification.get("retention_days", 7) * 86400
    destination_root = Path(config["backup_root"]) / "crash-dumps"
    for file in files:
        if file in keep or file.stat().st_mtime >= cutoff or storage.busy(file, processes):
            continue
        storage.assert_child(file, root)
        stat = file.stat()
        storage.emit("dump-candidate", name=file.name, bytes=stat.st_size, apply=apply)
        if not apply:
            continue
        destination_root.mkdir(parents=True, exist_ok=True)
        checksum = storage.sha256(file)
        destination = storage.assert_child(destination_root / (checksum[:16] + "-" + file.name), destination_root)
        if not destination.exists():
            shutil.copy2(storage.native(file), storage.native(destination))
        if storage.sha256(destination) != checksum or storage.sha256(file) != checksum or file.stat().st_mtime_ns != stat.st_mtime_ns:
            raise RuntimeError("Crash dump changed or backup failed")
        if storage.is_reparse(file) or storage.busy(file, storage.process_references()):
            raise RuntimeError("Crash dump became active")
        os.unlink(storage.native(file))
        storage.emit("dump-archived", name=file.name, bytes=stat.st_size)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8-sig"))
    if not config.get("enabled", False):
        storage.emit("policy-disabled")
        return 0
    storage.validate_volumes(config)
    journal = Path(config["journal_root"])
    backup = Path(config["backup_root"])
    processes = storage.process_references()
    if args.apply and journal.exists():
        for record_path in journal.glob("*.json"):
            if record_path.name.endswith(".manifest.json"):
                continue
            record = json.loads(record_path.read_text(encoding="utf-8"))
            if record.get("phase") == "prepared":
                storage.finalize(record, journal)
    for item in candidates(config):
        # A source containing existing junctions is retained, never traversed.
        try:
            item["private_sid"] = config.get("private_sid")
            record = storage.prepare(item, backup, journal, apply=args.apply, processes=processes)
        except ValueError as error:
            storage.emit("candidate-retained", id=item["id"], reason=str(error))
            continue
        storage.emit("retention-operation", id=record["id"], phase=record["phase"], reason=record.get("reason"))
        if args.apply and record["phase"] == "prepared":
            storage.finalize(record, journal)
    archive_old_dumps(config, apply=args.apply, processes=processes)
    uv = config.get("uv_cache")
    if uv and args.apply:
        environment = {**os.environ, "UV_LOCK_TIMEOUT": "10"}
        result = subprocess.run([uv["executable"], "cache", "prune", "--cache-dir", uv["root"]],
                                capture_output=True, text=True, timeout=180, env=environment)
        if result.returncode:
            raise RuntimeError("uv cache prune failed or was busy; cache was preserved")
        storage.emit("uv-cache-pruned", root=uv["root"])
    free = shutil.disk_usage(config["system_drive"]).free
    storage.emit("storage-headroom", free_bytes=free, warning=free < config.get("warning_free_bytes", 30 * 1024**3))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
