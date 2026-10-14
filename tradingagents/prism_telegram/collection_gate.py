"""Recheck canonical session coverage while the PRISM workflow owns its lane."""
from __future__ import annotations

from datetime import datetime, timedelta
import os
from pathlib import Path
from zoneinfo import ZoneInfo

from tradingagents.local_advisory_recovery import RecoveryDiagnostic, read, timestamp
from tradingagents.prism_telegram.config import load_prism_telegram_config


def should_collect(*, archive: Path, channel: str, now: datetime, automatic: bool) -> bool:
    if not automatic:
        return True
    now = now.astimezone(ZoneInfo("Asia/Seoul"))
    window = now.replace(hour=7, minute=35, second=0, microsecond=0)
    if now < window:
        window -= timedelta(days=1)
    for path in (archive / "runs").glob("*/prism_telegram_*/prism_telegram_run.json"):
        try:
            began = datetime.strptime(path.parent.name.removeprefix("prism_telegram_"), "%Y%m%d_%H%M%S").replace(tzinfo=now.tzinfo)
        except ValueError:
            continue
        if not window <= began <= now:
            continue
        manifest = read(path, reason="CANONICAL_INVALID")
        if manifest.get("status") != "success":
            continue
        source = manifest.get("source")
        if not isinstance(source, dict) or not source.get("channel"):
            raise RecoveryDiagnostic("CANONICAL_SCOPE_UNVERIFIED")
        if source["channel"] != channel:
            continue
        try:
            started, finished = timestamp(manifest["started_at"]), timestamp(manifest["finished_at"])
            summary = manifest["summary"]
            if (manifest["run_id"] != path.parent.name or type(summary["messages"]) is not int
                    or summary["messages"] < 0 or summary["warnings"] != 0
                    or not window <= started <= finished <= now):
                raise ValueError("Incomplete session evidence")
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            raise RecoveryDiagnostic("CANONICAL_INCOMPLETE") from exc
        # A successful empty collection still consumed this session's probe.
        # Publication failure must not cause another collection.
        return False
    return True


def main() -> None:
    config = load_prism_telegram_config(Path("config/prism_telegram_daily.toml"))
    automatic = (os.environ.get("GH_EVENT_NAME") == "schedule"
                 or os.environ.get("RECOVERY_SOURCE") in {"cloud_watchdog", "local_watchdog"})
    collect = should_collect(archive=config.storage.archive_dir, channel=config.source.channel,
                             now=datetime.now(ZoneInfo("Asia/Seoul")), automatic=automatic)
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as handle:
        handle.write(f"should_run={'true' if collect else 'false'}\n")
    print("PRISM collection is due." if collect else "PRISM session collection is already complete; skipping duplicate.")


if __name__ == "__main__":
    main()
