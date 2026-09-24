"""Refuse to start a heavy self-hosted Windows job without safe headroom."""

from __future__ import annotations

import argparse
import ctypes
import shutil
import time
from ctypes import wintypes
from dataclasses import dataclass


GIB = 1024**3
# The self-hosted runners normally have 6-8 GiB free on C:. Requiring 12 GiB
# made every analysis and Pages run time out even with ample memory. Keep a
# 4 GiB reserve for job output; the runner preflight also refuses work below 2 GiB.
DEFAULT_MIN_C_FREE_GIB = 4.0


class PerformanceInformation(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("commit_total", ctypes.c_size_t),
        ("commit_limit", ctypes.c_size_t),
        ("commit_peak", ctypes.c_size_t),
        ("physical_total", ctypes.c_size_t),
        ("physical_available", ctypes.c_size_t),
        ("system_cache", ctypes.c_size_t),
        ("kernel_total", ctypes.c_size_t),
        ("kernel_paged", ctypes.c_size_t),
        ("kernel_nonpaged", ctypes.c_size_t),
        ("page_size", ctypes.c_size_t),
        ("handle_count", wintypes.DWORD),
        ("process_count", wintypes.DWORD),
        ("thread_count", wintypes.DWORD),
    ]


@dataclass(frozen=True)
class ResourceSnapshot:
    commit_free: int
    commit_total: int
    commit_limit: int
    physical_free: int
    c_drive_free: int
    process_count: int


def read_snapshot() -> ResourceSnapshot:
    info = PerformanceInformation()
    info.cb = ctypes.sizeof(info)
    if not ctypes.windll.psapi.GetPerformanceInfo(ctypes.byref(info), info.cb):
        raise ctypes.WinError()

    page_size = info.page_size
    commit_total = info.commit_total * page_size
    commit_limit = info.commit_limit * page_size
    return ResourceSnapshot(
        commit_free=max(0, commit_limit - commit_total),
        commit_total=commit_total,
        commit_limit=commit_limit,
        physical_free=info.physical_available * page_size,
        c_drive_free=shutil.disk_usage("C:/").free,
        process_count=info.process_count,
    )


def format_snapshot(snapshot: ResourceSnapshot) -> str:
    return (
        f"commit={snapshot.commit_total / GIB:.2f}/"
        f"{snapshot.commit_limit / GIB:.2f} GiB "
        f"(free={snapshot.commit_free / GIB:.2f} GiB), "
        f"physical_free={snapshot.physical_free / GIB:.2f} GiB, "
        f"C_free={snapshot.c_drive_free / GIB:.2f} GiB, "
        f"processes={snapshot.process_count}"
    )


def has_headroom(
    snapshot: ResourceSnapshot,
    *,
    min_commit_free: int,
    min_physical_free: int,
    min_c_drive_free: int,
) -> bool:
    return (
        snapshot.commit_free >= min_commit_free
        and snapshot.physical_free >= min_physical_free
        and snapshot.c_drive_free >= min_c_drive_free
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-commit-free-gib", type=float, default=8.0)
    parser.add_argument("--min-physical-free-gib", type=float, default=2.0)
    parser.add_argument("--min-c-free-gib", type=float, default=DEFAULT_MIN_C_FREE_GIB)
    parser.add_argument("--wait-seconds", type=int, default=900)
    parser.add_argument("--poll-seconds", type=int, default=15)
    args = parser.parse_args()

    thresholds = {
        "min_commit_free": int(args.min_commit_free_gib * GIB),
        "min_physical_free": int(args.min_physical_free_gib * GIB),
        "min_c_drive_free": int(args.min_c_free_gib * GIB),
    }
    deadline = time.monotonic() + max(0, args.wait_seconds)

    while True:
        snapshot = read_snapshot()
        print(f"Windows resource guard: {format_snapshot(snapshot)}", flush=True)
        if has_headroom(snapshot, **thresholds):
            print("Windows resource guard passed.", flush=True)
            return 0
        if time.monotonic() >= deadline:
            print(
                "::error::Insufficient Windows memory or disk headroom. "
                "The heavy job was stopped before it could freeze the runner host.",
                flush=True,
            )
            return 1
        time.sleep(max(1, args.poll_seconds))


if __name__ == "__main__":
    raise SystemExit(main())
