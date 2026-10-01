"""Non-broker readiness probe for an explicitly configured Windows archive.

Never opens account files, credential stores, or provider endpoints. The only
writes are constant test bytes inside one new, uniquely named archive child.
This is a diagnostic, not permission to reroute a producer to this runner.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Mapping


def credential_checks(env: Mapping[str, str], market: str) -> dict[str, bool]:
    def configured(*names: str) -> bool:
        return any(bool(env.get(name, "").strip()) for name in names)

    # Names match the existing producer's environment aliases. Values never
    # leave this function and are neither hashed nor included in diagnostics.
    kis_api = all(configured(a, b) for a, b in (
        ("KIS_APP_KEY", "KIS_Developers_APP_KEY"),
        ("KIS_APP_SECRET", "KIS_Developers_APP_SECRET"),
    ))
    kis_account = all(configured(a, b) for a, b in (
        ("KIS_ACCOUNT_NO", "KIS_Developers_ACCOUNT_NO"),
        ("KIS_PRODUCT_CODE", "KIS_Developers_PRODUCT_CODE"),
    ))
    result = {"kis_api_configuration_present": kis_api,
              "kis_account_configuration_present": kis_account}
    if market in {"us", "all"}:
        result["us_market_data_configuration_present"] = (
            configured("MASSIVE_API_KEY", "POLYGON_API_KEY")
            or (configured("ALPACA_API_KEY_ID") and configured("ALPACA_SECRET_KEY"))
        )
    return result


def _set_lock(stream, *, lock: bool) -> None:
    stream.seek(0)
    if os.name == "nt":
        import msvcrt

        msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK if lock else msvcrt.LK_UNLCK, 1)
    else:
        import fcntl

        fcntl.flock(stream.fileno(), (fcntl.LOCK_EX | fcntl.LOCK_NB) if lock else fcntl.LOCK_UN)


def lock_child(path: Path) -> int:
    # Private subprocess mode. The caller passes only its newly created probe
    # file; this branch performs no file creation and emits no text.
    try:
        with path.open("r+b") as stream:
            try:
                _set_lock(stream, lock=True)
            except (OSError, BlockingIOError):
                return 2
            _set_lock(stream, lock=False)
        return 0
    except OSError:
        return 3


def probe_archive(raw_path: str) -> dict[str, bool]:
    checks = {name: False for name in (
        "archive_explicit_absolute", "archive_directory_present", "archive_readable",
        "isolated_write", "atomic_replace", "exclusive_lock", "probe_cleanup",
    )}
    if not raw_path.strip():
        return checks
    root = Path(raw_path)
    # Refuse filesystem roots and symlink roots; never delete recursively.
    if not root.is_absolute() or root == Path(root.anchor) or root.is_symlink():
        return checks
    checks["archive_explicit_absolute"] = True
    checks["archive_directory_present"] = root.is_dir()
    if not checks["archive_directory_present"]:
        return checks
    try:
        with os.scandir(root) as entries:
            next(entries, None)  # Access only the listing, never account bytes.
        checks["archive_readable"] = True
    except OSError:
        return checks

    temporary: Path | None = None
    known_files: list[Path] = []
    try:
        temporary = Path(tempfile.mkdtemp(prefix=".overlay-preflight-", dir=root))
        source, destination, lock_path = (temporary / name for name in ("source", "target", "lock"))
        known_files = [source, destination, lock_path]
        source.write_bytes(b"preflight-new\n")
        destination.write_bytes(b"preflight-old\n")
        checks["isolated_write"] = source.read_bytes() == b"preflight-new\n"
        os.replace(source, destination)
        checks["atomic_replace"] = destination.read_bytes() == b"preflight-new\n" and not source.exists()
        lock_path.write_bytes(b"1")
        command = [sys.executable, str(Path(__file__).resolve()), "--lock-child", str(lock_path)]
        kwargs = dict(stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL, timeout=5, check=False)
        with lock_path.open("r+b") as stream:
            _set_lock(stream, lock=True)
            try:
                denied = subprocess.run(command, **kwargs).returncode == 2
            finally:
                _set_lock(stream, lock=False)
        released = subprocess.run(command, **kwargs).returncode == 0
        checks["exclusive_lock"] = denied and released
    except (OSError, subprocess.SubprocessError):
        pass
    finally:
        if temporary is not None:
            try:
                for path in known_files:
                    path.unlink(missing_ok=True)
                temporary.rmdir()
                checks["probe_cleanup"] = True
            except OSError:
                # Do not dump exception text: it may include a configured path.
                checks["probe_cleanup"] = False
    return checks


def probe_codex(env: Mapping[str, str]) -> dict[str, bool]:
    explicit = env.get("CODEX_BINARY", "").strip()
    binary = explicit or shutil.which("codex")
    present = bool(binary and Path(binary).is_file())
    checks = {"codex_binary_present": present, "codex_login_ready": False}
    if not present:
        return checks
    try:
        # Status only: no login, credential extraction, or model invocation.
        completed = subprocess.run(
            [binary, "login", "status"], stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            timeout=10, check=False,
        )
        checks["codex_login_ready"] = completed.returncode == 0
    except (OSError, subprocess.SubprocessError):
        pass
    return checks


def collect_preflight(env: Mapping[str, str], market: str) -> dict:
    checks = {"windows_runner": os.name == "nt"}
    checks.update(probe_archive(env.get("TRADINGAGENTS_ARCHIVE_DIR", "")))
    basic_checks_pass = all(checks.values())
    return {
        "schema": "tradingagents.overlay-runner-preflight/v1",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "market": market,
        "status": "basic_checks_pass" if basic_checks_pass else "basic_checks_failed",
        "basic_checks_pass": basic_checks_pass,
        "ready_for_live_routing": False,
        "configuration_scope": "this_job_environment_only",
        "checks": checks,
        "configuration_diagnostics": credential_checks(env, market),
        "codex_diagnostics": probe_codex(env),
        "limitations": ["no_provider_or_broker_request", "no_model_availability_check",
                        "shared_archive_writer_safety_not_proven", "no_runner_rerouting"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--market", choices=("kr", "us", "all"), default="all")
    parser.add_argument("--lock-child", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.lock_child is not None:
        return lock_child(args.lock_child)
    result = collect_preflight(os.environ, args.market)
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return 0 if result["basic_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
