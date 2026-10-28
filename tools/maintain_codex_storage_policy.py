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


def audit_relocations(config: dict) -> bool:
    """Observe registered aliases without repairing or deleting changed paths."""
    healthy = True
    for item in config.get("relocations", []):
        source, destination = Path(item["source"]), Path(item["destination"])
        try:
            matches = (source.is_dir() and destination.is_dir() and storage.is_reparse(source)
                       and source.resolve() == destination.resolve())
        except OSError:
            matches = False
        storage.emit("relocation-health", id=item["id"], healthy=matches,
                     source=str(source), destination=str(destination))
        healthy = healthy and matches
    return healthy


def completed_runs(archive_roots: list[str], run_ids: set[str] | None = None) -> dict[str, dict]:
    completed = {}
    for root in archive_roots:
        path = Path(root)
        if not path.exists() or storage.is_reparse(path):
            continue
        # Retention only needs manifests for worker folders that actually exist.
        # Avoid walking every archived overlay on every PC maintenance run.
        manifests = path.glob("*/*/run.json") if run_ids is None else (
            year / run_id / "run.json" for year in path.iterdir() if year.is_dir()
            for run_id in sorted(run_ids)
        )
        for manifest in manifests:
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
                    if child.is_dir() and not child.name.endswith(".storage-original")
                    and not storage.is_reparse(child) and not (target / child.name).exists()
                ]
                for source, bound, target in sources:
                    key = re.sub(r"[^A-Za-z0-9_.-]", "-", str(source.relative_to(root)))
                    items.append({"id": "documents-" + key, "source": str(source), "source_root": str(bound),
                                  "destination": str(target), "destination_root": str(destination), "quiet_hours": 48})
    worker_folders = {}
    for specification in config.get("workers", []):
        root = Path(specification["root"])
        if root.exists() and not storage.is_reparse(root):
            worker_folders[str(root)] = [p for p in root.iterdir() if p.is_dir() and not storage.is_reparse(p)]
    wanted = {p.name for folders in worker_folders.values() for p in folders}
    completed = completed_runs(config.get("archive_roots", []), wanted) if wanted else {}
    for specification in config.get("workers", []):
        root = Path(specification["root"])
        if not root.exists() or storage.is_reparse(root):
            continue
        folders = sorted((p for p in worker_folders.get(str(root), []) if p.name in completed),
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


def run_policy(config: dict, *, apply: bool, preflight_only: bool = False) -> int:
    if not config.get("enabled", False):
        storage.emit("policy-disabled")
        return 0
    aliases_ok = audit_relocations(config)
    storage.validate_volumes(config)
    if not aliases_ok:
        storage.emit("policy-blocked", reason="relocation-mismatch")
        return 2
    if preflight_only or config.get("observe_only", False):
        return 0
    # Mutations keep the original backup-first and active-writer checks.
    journal = Path(config["journal_root"])
    backup = Path(config["backup_root"])
    processes = storage.process_references()
    if apply and journal.exists():
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
            record = storage.prepare(item, backup, journal, apply=apply, processes=processes)
        except ValueError as error:
            storage.emit("candidate-retained", id=item["id"], reason=str(error))
            continue
        storage.emit("retention-operation", id=record["id"], phase=record["phase"], reason=record.get("reason"))
        if apply and record["phase"] == "prepared":
            storage.finalize(record, journal)
    archive_old_dumps(config, apply=apply, processes=processes)
    uv = config.get("uv_cache")
    if uv and apply:
        environment = {**os.environ, "UV_LOCK_TIMEOUT": "10"}
        result = subprocess.run([uv["executable"], "cache", "prune", "--cache-dir", uv["root"]],
                                capture_output=True, text=True, timeout=180, env=environment)
        if result.returncode:
            raise RuntimeError("uv cache prune failed or was busy; cache was preserved")
        storage.emit("uv-cache-pruned", root=uv["root"])
    free = shutil.disk_usage(config["system_drive"]).free
    critical = free < config.get("critical_free_bytes", 0)
    storage.emit("storage-headroom", free_bytes=free,
                 warning=free < config.get("warning_free_bytes", 30 * 1024**3), critical=critical)
    return 2 if critical else 0


def domain_policy(config: dict, *, apply: bool, preflight_only: bool = False) -> int:
    """Fail closed within each domain while retaining a failed overall result.

    Exit 3 is only a degraded preflight: shared wrapper dependencies passed,
    but a separate domain failed. The wrapper may continue once; final status
    remains failed. Dry runs never write monitoring receipts.
    """
    observed = datetime.now().astimezone().isoformat()
    results, headroom = [], []
    shared_ok = True
    try:
        storage.validate_volumes(config)
        if not audit_relocations(config):
            shared_ok = False
    except (OSError, RuntimeError, ValueError) as exc:
        shared_ok = False
        storage.emit("shared-preflight-failed", error_type=type(exc).__name__)
    for item in config.get("capacity_checks", []):
        row = {"id": item["id"], "path": item["path"], "observed_at": observed}
        try:
            resolved = Path(item["path"]).resolve(strict=True)
            usage = shutil.disk_usage(resolved)
            row.update(available=True, resolved_path=str(resolved), free_bytes=usage.free,
                       warning=usage.free < item.get("warning_free_bytes", 0),
                       critical=usage.free < item.get("critical_free_bytes", 0))
            if row["critical"] and item.get("required_for_shared", False):
                shared_ok = False
        except OSError as exc:
            row.update(available=False, free_bytes=None, error_type=type(exc).__name__)
            if item.get("required_for_shared", False):
                shared_ok = False
        headroom.append(row)
        storage.emit("capacity-health", **row)
    # Reject duplicate configured mutation roots before any domain can write.
    roots = []
    for domain in config.get("domains", []):
        children = [x["root"] for x in domain.get("workers", [])]
        children += [domain[k]["root"] for k in ("documents", "crash_dumps", "uv_cache") if domain.get(k)]
        for root in children:
            normalized = os.path.normcase(os.path.abspath(root)).rstrip("/\\")
            if any(normalized == prior or normalized.startswith(prior + os.sep) or prior.startswith(normalized + os.sep) for prior in roots):
                raise ValueError("Duplicate or overlapping mutation roots across domains")
            roots.append(normalized)
    for domain in config.get("domains", []):
        row = {"id": domain["id"], "observed_at": observed}
        try:
            code = run_policy(domain, apply=apply and shared_ok, preflight_only=preflight_only or not shared_ok)
            row.update(status="HEALTHY" if code == 0 else "BLOCKED", exit_code=code)
        except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as exc:
            row.update(status="BLOCKED", exit_code=2, error_type=type(exc).__name__)
        results.append(row)
        storage.emit("domain-health", **row)
    failed = not shared_ok or any(x["exit_code"] for x in results)
    receipt = {"observed_at": observed, "shared_ok": shared_ok, "domains": results,
               "capacity": headroom, "healthy": not failed, "mode": "apply" if apply else "dry-run"}
    if apply and not preflight_only and config.get("health_receipt"):
        path = Path(config["health_receipt"])
        previous = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        old = {x["id"]: x for x in previous.get("capacity", [])}
        for row in headroom:
            before = old.get(row["id"], {}).get("free_bytes")
            row["delta_free_bytes"] = row.get("free_bytes") - before if row.get("free_bytes") is not None and before is not None else None
        receipt["consecutive_failed_runs"] = previous.get("consecutive_failed_runs", 0) + 1 if failed else 0
        receipt["alert_signature"] = sorted(["domain:" + x["id"] for x in results if x["exit_code"]] + ["capacity:" + x["id"] for x in headroom if not x.get("available") or x.get("warning") or x.get("critical")])
        receipt["alert_state_changed"] = previous.get("alert_signature") != receipt["alert_signature"]
        receipt["notification_delivery"] = "UNVERIFIED_EXISTING_MONITOR"
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(temporary, path)
    storage.emit("domain-policy-summary", **receipt)
    return (3 if preflight_only and shared_ok else 2) if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8-sig"))
    if not config.get("enabled", False):
        return 0
    runner = domain_policy if config.get("domains") else run_policy
    return runner(config, apply=args.apply, preflight_only=args.preflight_only)


if __name__ == "__main__":
    raise SystemExit(main())
