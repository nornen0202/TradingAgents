"""Read-only audit of source clocks and recent Work reports; never ACKs."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from tradingagents.work.packet import build_surface_packet, load_json


def audit(archive: Path, *, count: int = 6) -> dict:
    result = {"checked_at": datetime.now(timezone.utc).isoformat(), "markets": {}}
    for market in ("kr", "us"):
        packet = build_surface_packet(market, archive_dir=archive)
        body = packet["body"]
        current = body.get("current") or {}
        reports = []
        root = archive / "work-reports" / market / "events"
        candidates = [load_json(path) for path in root.glob("*.json")]
        candidates.sort(key=lambda item: str(item.get("published_at") or ""), reverse=True)
        for report in candidates[:count]:
            structured = report.get("structured_report") or {}
            strategies = structured.get("strategies") or []
            reports.append({
                "event_id": report.get("event_id"),
                "published_at": report.get("published_at"),
                "input_as_of": structured.get("as_of"),
                "has_freshness_receipt": bool((structured.get("source_summary") or {}).get("freshness_receipt")),
                "strategy_count": len(strategies),
                "thesis_counts": dict(Counter((row.get("thesis") or {}).get("stance", "MISSING") for row in strategies)),
            })
        result["markets"][market] = {
            "source_health": body.get("source_health"),
            "freshness_receipt": current.get("freshness_receipt"),
            "prepared_thesis_counts": dict(Counter((row.get("thesis") or {}).get("stance", "MISSING") for row in (current.get("bundle") or {}).get("strategy_table", []))),
            "recent_reports": reports,
        }
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    content = json.dumps(audit(args.archive_dir), ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8")
    else:
        print(content)
