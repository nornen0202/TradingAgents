"""Wake already-enabled paper consumers after atomic producer completion.

No signal is retimestamped or resubmitted here. The normal consumers select a
completed source and enforce their original freshness, ownership and order gates.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess

from tradingagents.atomic_io import atomic_write_json


PAPER_HANDOFF_LOCK_TIMEOUT_SECONDS = 15


def _scheduled_worker_root_matches(root):
    configured = os.getenv("TRADINGAGENTS_SCHEDULED_CONSUMER_STATE_ROOT")
    return bool(os.name == "nt" and configured and Path(configured).resolve() == root.resolve())


def handoff_completed_run(archive, manifest, *, state_root=None):
    configured = state_root or os.getenv("TRADINGAGENTS_LOCAL_PAPER_STATE_DIR")
    if (not configured or manifest.get("status") != "success"
            or (manifest.get("settings") or {}).get("run_mode") not in {"overlay_only", "selective_rerun_only"}):
        return None
    root = Path(configured)
    from tradingagents.execution import demo_runtime, paper_runtime

    def wake(lane, mode, task):
        try:
            config = json.loads((root / lane / "enabled.json").read_text(encoding="utf-8-sig"))
            if (not isinstance(config, dict) or config.get("mode") != mode or config.get("enabled") is not True
                    or config.get("real_orders_enabled") is not False):
                return {"status": "DISABLED"}
            result = subprocess.run(["schtasks.exe", "/Run", "/TN", "\\TradingAgents\\" + task],
                capture_output=True, timeout=5, check=False,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            # A wake request is not proof that the consumer finished, submitted
            # an order or filled it. Existing tasks keep their own lock and timer.
            return {"status": "WAKE_REQUESTED" if result.returncode == 0 else "SCHEDULED_TICK_PENDING"}
        except (OSError, ValueError, subprocess.TimeoutExpired):
            return {"status": "SCHEDULED_TICK_PENDING"}

    def consume(lane, mode, callback):
        try:
            config = json.loads((root / lane / "enabled.json").read_text(encoding="utf-8-sig"))
            if (config.get("mode") != mode or config.get("enabled") is not True
                    or config.get("real_orders_enabled") is not False):
                return {"status": "DISABLED"}
            result = callback()
            return {"status": "COMPLETED", "checked_at": result.get("checked_at"),
                    "markets": {key: {field: row.get(field) for field in ("status", "source_run_id", "blockers")}
                                for key, row in result.get("markets", {}).items()}}
        except TimeoutError:
            return {"status": "EXISTING_CONSUMER_RUNNING"}
        except (OSError, ValueError, TypeError, AttributeError):
            return {"status": "UNAVAILABLE"}
        except Exception as exc:
            # Neither broker exceptions nor account evidence belong in receipts.
            return {"status": "ERROR", "error_type": type(exc).__name__}

    started = datetime.now(timezone.utc)
    scheduled = (_scheduled_worker_root_matches(root)
                 and (manifest.get("settings") or {}).get("execution_lightweight_refresh") is True)
    with ThreadPoolExecutor(max_workers=2) as pool:
        if scheduled:
            paper = pool.submit(wake, "paper", "LOCAL_PAPER_ONLY", "LocalAutomation-paper")
            strategy = pool.submit(wake, "kis-strategy", "KIS_DEMO_STRATEGY", "LocalAutomation-strategy-kis")
        else:
            paper = pool.submit(consume, "paper", "LOCAL_PAPER_ONLY",
                                lambda: paper_runtime.tick(archive, root / "paper",
                                    lock_timeout=PAPER_HANDOFF_LOCK_TIMEOUT_SECONDS))
            strategy = pool.submit(consume, "kis-strategy", "KIS_DEMO_STRATEGY",
                                   lambda: demo_runtime.tick(archive, root / "kis-strategy", root / "kis-validation"))
        results = {"paper": paper.result(), "kis_strategy": strategy.result()}
    receipt = {"source_run_id": manifest.get("run_id"), "source_completed_at": manifest.get("finished_at"),
               "started_at": started.isoformat(), "finished_at": datetime.now(timezone.utc).isoformat(),
               "delivery_mode": "SCHEDULED_WORKER_WAKE" if scheduled else "INLINE_CONSUMERS",
               "real_orders_enabled": False, "consumers": results}
    # Audit failure must not turn an already-published successful run into a
    # failed producer retry (which could generate a second source identity).
    try:
        atomic_write_json(root / "execution-handoff" / "latest.json", receipt)
    except OSError:
        pass
    return receipt
