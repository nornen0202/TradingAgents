"""Wake already-enabled paper consumers after atomic producer completion.

No signal is retimestamped or resubmitted here. The normal consumers select a
completed source and enforce their original freshness, ownership and order gates.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
from pathlib import Path

from tradingagents.atomic_io import atomic_write_json


def handoff_completed_run(archive, manifest, *, state_root=None):
    configured = state_root or os.getenv("TRADINGAGENTS_LOCAL_PAPER_STATE_DIR")
    if (not configured or manifest.get("status") != "success"
            or (manifest.get("settings") or {}).get("run_mode") not in {"overlay_only", "selective_rerun_only"}):
        return None
    root = Path(configured)
    from tradingagents.execution import demo_runtime, paper_runtime

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
    with ThreadPoolExecutor(max_workers=2) as pool:
        paper = pool.submit(consume, "paper", "LOCAL_PAPER_ONLY",
                            lambda: paper_runtime.tick(archive, root / "paper"))
        strategy = pool.submit(consume, "kis-strategy", "KIS_DEMO_STRATEGY",
                               lambda: demo_runtime.tick(archive, root / "kis-strategy", root / "kis-validation"))
        results = {"paper": paper.result(), "kis_strategy": strategy.result()}
    receipt = {"source_run_id": manifest.get("run_id"), "source_completed_at": manifest.get("finished_at"),
               "started_at": started.isoformat(), "finished_at": datetime.now(timezone.utc).isoformat(),
               "real_orders_enabled": False, "consumers": results}
    # Audit failure must not turn an already-published successful run into a
    # failed producer retry (which could generate a second source identity).
    try:
        atomic_write_json(root / "execution-handoff" / "latest.json", receipt)
    except OSError:
        pass
    return receipt
