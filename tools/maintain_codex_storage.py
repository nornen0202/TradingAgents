"""Verified, resumable offload of closed Codex workspaces; never deletes backups."""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import time
import zipfile

REPARSE = 0x400


class ForwardOnlyArchive:
    """Avoid a header rewrite/seek for every file on external backup drives."""

    def __init__(self, handle):
        self.handle = handle
        self.position = 0

    def write(self, block):
        written = self.handle.write(block)
        self.position += written
        return written

    def tell(self):
        return self.position

    def flush(self):
        self.handle.flush()
        os.fsync(self.handle.fileno())


def native(path: Path | str) -> str:
    value = os.path.abspath(path)
    return "\\\\?\\" + value if os.name == "nt" else value


def emit(event: str, **values) -> None:
    print(json.dumps({"event": event, **values}, ensure_ascii=False), flush=True)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def is_reparse(path: Path) -> bool:
    return bool(getattr(os.lstat(native(path)), "st_file_attributes", 0) & REPARSE) or path.is_symlink()


def assert_child(path: Path, root: Path) -> Path:
    target = Path(os.path.abspath(path))
    bound = Path(os.path.abspath(root))
    if target == bound or bound not in target.parents:
        raise ValueError(f"Target must be a strict child of configured root: {target}")
    current = bound
    for part in target.relative_to(bound).parts:
        if current.exists() and is_reparse(current):
            raise ValueError(f"Reparse ancestor is not allowed: {current}")
        current /= part
    return target


def snapshot(root: Path) -> tuple[dict, list[str]]:
    if is_reparse(root):
        raise ValueError(f"Refusing reparse tree: {root}")
    files, directories = {}, [""]
    pending = [root]
    while pending:
        current = pending.pop()
        with os.scandir(native(current)) as entries:
            for entry in entries:
                full = current / entry.name
                stat = entry.stat(follow_symlinks=False)
                if getattr(stat, "st_file_attributes", 0) & REPARSE or entry.is_symlink():
                    raise ValueError(f"Refusing nested reparse point: {full}")
                relative = full.relative_to(root).as_posix()
                if entry.is_dir(follow_symlinks=False):
                    directories.append(relative)
                    pending.append(full)
                else:
                    files[relative] = {"bytes": stat.st_size, "mtime_ns": stat.st_mtime_ns}
    return files, directories


def sha256(path: Path) -> str:
    with open(native(path), "rb") as handle:
        return stream_sha256(handle)


def stream_sha256(handle) -> str:
    digest = hashlib.sha256()
    while block := handle.read(4 * 1024 * 1024):
        digest.update(block)
    return digest.hexdigest()


def process_references() -> list[dict]:
    if os.name != "nt":
        return []
    # Command lines are examined only in memory and are never written to logs.
    command = "Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId,Name,CommandLine,ExecutablePath | ConvertTo-Json -Compress"
    result = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
                            capture_output=True, encoding="utf-8", errors="replace", timeout=45,
                            creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:
        raise RuntimeError("Process inventory unavailable; refusing storage changes")
    data = json.loads(result.stdout or "[]")
    data = data if isinstance(data, list) else [data]
    own = {os.getpid(), os.getppid()}
    return [item for item in data if item["ProcessId"] not in own]


def process_cwd(pid: int) -> str | None:
    """Read only the current-directory field of an accessible 64-bit process."""
    if os.name != "nt":
        return None
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    ntdll = ctypes.WinDLL("ntdll")
    kernel.OpenProcess.restype = ctypes.c_void_p
    kernel.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
    kernel.ReadProcessMemory.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    ntdll.NtQueryInformationProcess.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_void_p, ctypes.c_ulong, ctypes.c_void_p]
    handle = kernel.OpenProcess(0x410, False, pid)
    if not handle:
        return None
    try:
        info = ctypes.create_string_buffer(48)
        if ntdll.NtQueryInformationProcess(handle, 0, info, 48, None):
            return None
        peb = struct.unpack_from("<Q", info.raw, 8)[0]
        def read(address, length):
            buf = ctypes.create_string_buffer(length)
            got = ctypes.c_size_t()
            if not kernel.ReadProcessMemory(handle, address, buf, length, ctypes.byref(got)) or got.value != length:
                return None
            return buf.raw
        raw = read(peb + 0x20, 8)
        if not raw:
            return None
        params = struct.unpack("<Q", raw)[0]
        value = read(params + 0x38, 16)
        if not value:
            return None
        length = struct.unpack_from("<H", value)[0]
        pointer = struct.unpack_from("<Q", value, 8)[0]
        if not 0 < length < 65536:
            return None
        raw = read(pointer, length)
        return raw.decode("utf-16-le") if raw else None
    finally:
        kernel.CloseHandle(handle)


def busy(path: Path, processes: list[dict]) -> list[dict]:
    needle = str(path).rstrip("\\/").lower()
    alternatives = (needle, needle.replace("\\", "/"))
    matches = []
    for process in processes:
        text = (process.get("CommandLine") or "").lower()
        executable = (process.get("ExecutablePath") or "").lower()
        cwd = process.get("cwd")
        if cwd is None and re.search(r"python|node|codex|jasna|ffmpeg|git|uv|powershell|pwsh", process.get("Name", ""), re.I):
            cwd = process_cwd(process["ProcessId"])
            process["cwd"] = cwd or ""
        cwd = (cwd or "").rstrip("\\/").lower()
        if any(a in text for a in alternatives) or executable.startswith(needle + "\\") or cwd == needle or cwd.startswith(needle + "\\"):
            matches.append({"name": process["Name"], "pid": process["ProcessId"]})
    return matches


def make_junction(link: Path, destination: Path) -> None:
    if os.name != "nt":
        link.symlink_to(destination, target_is_directory=True)
        return
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateFileW.restype = ctypes.c_void_p
    kernel.CreateFileW.argtypes = [ctypes.c_wchar_p, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_void_p, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_void_p]
    kernel.DeviceIoControl.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_void_p, ctypes.c_ulong, ctypes.c_void_p, ctypes.c_ulong, ctypes.c_void_p, ctypes.c_void_p]
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    os.mkdir(native(link))
    handle = kernel.CreateFileW(native(link), 0x40000000, 3, None, 3, 0x02200000, None)
    if handle == ctypes.c_void_p(-1).value:
        os.rmdir(native(link))
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        substitute = ("\\??\\" + str(destination)).encode("utf-16-le")
        printed = str(destination).encode("utf-16-le")
        paths = substitute + b"\0\0" + printed + b"\0\0"
        buffer = struct.pack("<IHHHHHH", 0xA0000003, len(paths) + 8, 0, 0, len(substitute), len(substitute) + 2, len(printed)) + paths
        returned = ctypes.c_ulong()
        if not kernel.DeviceIoControl(handle, 0x900A4, buffer, len(buffer), None, 0, ctypes.byref(returned), None):
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        kernel.CloseHandle(handle)


def verify_tree(root: Path, manifest: dict) -> None:
    current, _ = snapshot(root)
    if current.keys() != manifest.keys():
        raise RuntimeError(f"File set changed: {root}")
    for relative, expected in manifest.items():
        if current[relative]["bytes"] != expected["bytes"] or sha256(root / relative) != expected["sha256"]:
            raise RuntimeError(f"File verification failed: {root / relative}")


def verify_zip(archive: Path, manifest: dict) -> None:
    with zipfile.ZipFile(native(archive)) as saved:
        if set(saved.namelist()) != set(manifest):
            raise RuntimeError("Backup archive file set mismatch")
        for relative, expected in manifest.items():
            with saved.open(relative) as handle:
                if stream_sha256(handle) != expected["sha256"]:
                    raise RuntimeError(f"Backup hash mismatch: {relative}")


def remove_verified_tree(root: Path, allowed_root: Path, manifest: dict) -> None:
    assert_child(root, allowed_root)
    verify_tree(root, manifest)
    # Refuse junctions before deleting; never traverse a link during removal.
    _, directories = snapshot(root)
    for relative in manifest:
        file = root / relative
        os.chmod(native(file), 0o600)
        os.unlink(native(file))
    for relative in sorted(directories, key=lambda item: len(Path(item).parts), reverse=True):
        os.rmdir(native(root / relative))


def prepare(item: dict, backup_root: Path, journal_root: Path, *, apply: bool, processes: list[dict]) -> dict:
    source, source_root = Path(item["source"]), Path(item["source_root"])
    assert_child(source, source_root)
    identifier = item["id"]
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", identifier):
        raise ValueError("Unsafe operation identifier")
    record_path = journal_root / (identifier + ".json")
    if record_path.exists():
        record = json.loads(record_path.read_text(encoding="utf-8"))
        if record["source"] != str(source) or record.get("destination") != item.get("destination"):
            raise RuntimeError(f"Operation configuration changed: {identifier}")
        if record["phase"] in {"prepared", "finalized"}:
            return record
        raise RuntimeError(f"Interrupted operation needs review: {identifier}")
    if not source.exists() or is_reparse(source):
        return {"id": identifier, "phase": "skipped", "reason": "absent-or-already-linked"}
    references = busy(source, processes)
    if references:
        return {"id": identifier, "phase": "skipped", "reason": "active-process", "processes": references}
    files, directories = snapshot(source)
    if not files:
        return {"id": identifier, "phase": "skipped", "reason": "empty"}
    quiet = item.get("quiet_hours", 48)
    if max(record["mtime_ns"] for record in files.values()) / 1e9 > time.time() - quiet * 3600:
        return {"id": identifier, "phase": "skipped", "reason": "recent-write"}
    destination = Path(item["destination"]) if item.get("destination") else None
    if destination:
        assert_child(destination, Path(item["destination_root"]))
        if destination.exists():
            raise FileExistsError(f"Destination already exists: {destination}")
    archive = assert_child(backup_root / (identifier + ".zip"), backup_root)
    stage = source.with_name(source.name + ".storage-original")
    assert_child(stage, source_root)
    if stage.exists() or archive.exists():
        raise FileExistsError(f"Staging or backup already exists: {identifier}")
    record = {"id": identifier, "source": str(source), "source_root": str(source_root),
              "destination": str(destination) if destination else None, "stage": str(stage),
              "archive": str(archive), "phase": "planned", "logical_bytes": sum(f["bytes"] for f in files.values()), "files": len(files)}
    if not apply:
        return record
    write_json(record_path, record)
    backup_root.mkdir(parents=True, exist_ok=True)
    if destination:
        destination.mkdir(parents=True)
        if item.get("private_sid") and os.name == "nt":
            subprocess.run(["icacls.exe", str(destination), "/inheritance:r", "/grant:r",
                            "*" + item["private_sid"] + ":(OI)(CI)F", "*S-1-5-18:(OI)(CI)F"],
                           check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        for relative in directories:
            os.makedirs(native(destination / relative), exist_ok=True)
    manifest = {}
    start = last_report = time.monotonic()
    with open(native(archive), "xb", buffering=8 * 1024 * 1024) as archive_handle, zipfile.ZipFile(
        ForwardOnlyArchive(archive_handle), "w", compression=zipfile.ZIP_DEFLATED,
        compresslevel=1, allowZip64=True,
    ) as saved:
        for index, (relative, metadata) in enumerate(files.items(), 1):
            original = source / relative
            digest = hashlib.sha256()
            with open(native(original), "rb") as read, saved.open(relative, "w", force_zip64=True) as archived:
                target = open(native(destination / relative), "xb") if destination else None
                try:
                    while block := read.read(4 * 1024 * 1024):
                        digest.update(block); archived.write(block)
                        if target:
                            target.write(block)
                finally:
                    if target:
                        target.close()
            manifest[relative] = {**metadata, "sha256": digest.hexdigest()}
            if destination:
                shutil.copystat(native(original), native(destination / relative))
            if time.monotonic() - last_report > 25:
                emit("copy-progress", id=identifier, copied_files=index, total_files=len(files))
                last_report = time.monotonic()
    write_json(journal_root / (identifier + ".manifest.json"), manifest)
    verify_zip(archive, manifest)
    if destination:
        verify_tree(destination, manifest)
    verify_tree(source, manifest)
    if busy(source, process_references()):
        raise RuntimeError(f"Source became active during copying: {source}")
    current, _ = snapshot(source)
    if current != files:
        raise RuntimeError(f"Source metadata changed during copying: {source}")
    record["phase"] = "verified"
    write_json(record_path, record)
    # Atomic rename protects against open handles; failure leaves the source intact.
    os.rename(native(source), native(stage))
    if destination:
        try:
            make_junction(source, destination)
            for relative, metadata in manifest.items():
                if os.stat(native(source / relative)).st_size != metadata["bytes"]:
                    raise RuntimeError("Old path cannot resolve verified destination")
        except BaseException:
            if source.exists() and is_reparse(source):
                os.rmdir(native(source))
            elif source.exists() and not list(source.iterdir()):
                os.rmdir(native(source))
            os.rename(native(stage), native(source))
            raise
    else:
        source.mkdir()
    record.update(phase="prepared", prepared_at=time.time(), duration_seconds=round(time.monotonic() - start, 1))
    write_json(record_path, record)
    emit("prepared", id=identifier, files=len(files), logical_bytes=record["logical_bytes"])
    return record


def finalize(record: dict, journal_root: Path) -> None:
    if record["phase"] == "finalized":
        return
    if record["phase"] != "prepared":
        raise RuntimeError("Only prepared, verified operations may be finalized")
    manifest = json.loads((journal_root / (record["id"] + ".manifest.json")).read_text(encoding="utf-8"))
    verify_zip(Path(record["archive"]), manifest)
    if record.get("destination"):
        verify_tree(Path(record["destination"]), manifest)
        source = Path(record["source"])
        if not is_reparse(source) or source.resolve() != Path(record["destination"]).resolve():
            raise RuntimeError("Original path no longer points to the verified destination")
    if busy(Path(record["stage"]), process_references()):
        raise RuntimeError("Staged original is active")
    remove_verified_tree(Path(record["stage"]), Path(record["source_root"]), manifest)
    record.update(phase="finalized", finalized_at=time.time())
    write_json(journal_root / (record["id"] + ".json"), record)
    emit("finalized", id=record["id"], logical_bytes=record["logical_bytes"])


def volume_serial(path: Path) -> str:
    if os.name != "nt":
        return ""
    serial = ctypes.c_ulong()
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    if not kernel.GetVolumeInformationW(str(path.anchor), None, 0, ctypes.byref(serial), None, None, None, 0):
        raise ctypes.WinError(ctypes.get_last_error())
    return f"{serial.value:08X}"


def validate_volumes(config: dict) -> None:
    for root, serial in config.get("volumes", {}).items():
        if volume_serial(Path(root)) != serial:
            raise RuntimeError(f"Expected storage volume not mounted: {root}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--finalize-receipt", type=Path)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8-sig"))
    validate_volumes(config)
    journal_root, backup_root = Path(config["journal_root"]), Path(config["backup_root"])
    processes = process_references()
    records = []
    for item in config["items"]:
        record = prepare(item, backup_root, journal_root, apply=args.apply, processes=processes)
        records.append(record)
        emit("operation", **{k: v for k, v in record.items() if k != "manifest"})
    if args.finalize_receipt:
        if not args.apply:
            raise ValueError("Finalization requires --apply")
        receipt = json.loads(args.finalize_receipt.read_text(encoding="utf-8"))
        if not receipt.get("codex_ok") or not receipt.get("tradingagents_ok"):
            raise ValueError("Successful Codex and TradingAgents verification required")
        for record in records:
            if record["phase"] == "prepared":
                if receipt["verified_at"] < record["prepared_at"]:
                    raise ValueError("Verification predates offload")
                finalize(record, journal_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
