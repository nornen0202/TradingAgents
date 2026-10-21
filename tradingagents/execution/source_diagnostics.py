"""Explain an idle strategy without turning unallocated opinions into orders."""
from collections import Counter
import json
import re

from tradingagents.charting.bars import instant


def diagnose_source(source, now):
    if source is None:
        return {"status": "NO_SOURCE", "blockers": ["NO_RECENT_COMPLETED_SOURCE"]}
    bundle = json.loads((source / "decision_bundle_v2.json").read_text(encoding="utf-8-sig"))
    proposals = json.loads((source / "portfolio-private/proposed_orders.json").read_text(encoding="utf-8-sig")).get("orders", [])
    generated = instant(bundle.get("generated_at"))
    rows = bundle.get("strategy_table", [])
    reasons = Counter()
    ready = fresh = 0
    for row in rows:
        quality = row.get("quality") or {}
        clock = instant(row.get("market_data_asof"))
        if clock is not None and generated is not None and clock <= generated <= now and 0 <= (now - clock).total_seconds() < 120:
            fresh += 1
            ready += quality.get("execution_ready") is True and quality.get("generated_in_current_run") is True
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
    return {"status": "BLOCKED" if blockers else "NO_ALLOCATED_ORDERS" if not proposals else "PROPOSALS_AVAILABLE",
            "blockers": blockers, "strategy_rows": len(rows), "fresh_rows": fresh,
            "execution_ready_rows": ready, "allocated_orders": len(proposals),
            "reason_counts": dict(sorted(reasons.items()))}
