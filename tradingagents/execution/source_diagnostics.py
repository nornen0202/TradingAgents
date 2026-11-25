"""Explain an idle strategy without turning unallocated opinions into orders."""
from collections import Counter
import json
import re

from tradingagents.charting.bars import instant


ACTION_STATUSES = {"ACTION_SIGNAL_PRESENT", "DATA_RECHECK_REQUIRED", "WAITING_TRIGGER", "NO_EXECUTION_ACTION"}


def diagnose_source(source, now, *, include_proposals=True):
    if source is None:
        return {"status": "NO_SOURCE", "blockers": ["NO_RECENT_COMPLETED_SOURCE"]}
    bundle = json.loads((source / "decision_bundle_v2.json").read_text(encoding="utf-8-sig"))
    proposals = (json.loads((source / "portfolio-private/proposed_orders.json").read_text(encoding="utf-8-sig")).get("orders", [])
                 if include_proposals else None)
    generated = instant(bundle.get("generated_at"))
    rows = bundle.get("strategy_table", [])
    reasons = Counter()
    ready = fresh = classified_fresh = fresh_actions = 0
    observation_times, receipt_times = [], []
    for row in rows:
        quality = row.get("quality") or {}
        clock = instant(row.get("market_data_asof"))
        if clock is not None and generated is not None and clock <= generated <= now:
            observation_times.append(clock)
            received = instant(row.get("snapshot_received_at"))
            if quality.get("generated_in_current_run") is True and received is not None and clock <= received <= generated:
                receipt_times.append(received)
            if (now - clock).total_seconds() < 120:
                fresh += 1
                current_and_ready = quality.get("execution_ready") is True and quality.get("generated_in_current_run") is True
                ready += current_and_ready
                action_status = quality.get("action_status")
                if isinstance(action_status, str) and action_status in ACTION_STATUSES:
                    classified_fresh += 1
                    fresh_actions += current_and_ready and action_status == "ACTION_SIGNAL_PRESENT"
        for reason in quality.get("blocking_reasons", []):
            if isinstance(reason, str) and re.fullmatch(r"[A-Za-z0-9_:.-]{1,100}", reason):
                reasons[reason] += 1
    blockers = []
    if generated is None or not 0 <= (now - generated).total_seconds() < 600:
        blockers.append("SOURCE_EXECUTION_EXPIRED")
    elif rows and not fresh:
        blockers.append("SOURCE_SIGNALS_EXPIRED_OR_UNDATED")
    elif rows and not ready:
        blockers.append("SOURCE_DATA_NOT_EXECUTION_READY")
    return {"status": "BLOCKED" if blockers else "EXECUTION_OBSERVATIONS_AVAILABLE" if proposals is None else "NO_ALLOCATED_ORDERS" if not proposals else "PROPOSALS_AVAILABLE",
            "blockers": blockers, "strategy_rows": len(rows), "fresh_rows": fresh,
            "fresh_engine_action_rows": fresh_actions if observation_times and classified_fresh == fresh else None,
            "execution_ready_rows": ready, "allocated_orders": len(proposals) if proposals is not None else None,
            "generated_at": generated.isoformat() if generated and generated <= now else None,
            "newest_market_data_at": max(observation_times).isoformat() if observation_times else None,
            "newest_snapshot_received_at": max(receipt_times).isoformat() if receipt_times else None,
            "reason_counts": dict(sorted(reasons.items()))}
