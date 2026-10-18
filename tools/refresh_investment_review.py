"""Refresh local candles now while preserving an existing archived judgment."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tradingagents.charting.maintenance import refresh_existing_review, reobserve_existing_evidence
from tradingagents.charting.operations import archive_catalog


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--ticker-dir", type=Path)
    source.add_argument("--archive-dir", type=Path)
    parser.add_argument("--ticker", action="append", default=[])
    parser.add_argument("--tracker-db", type=Path, action="append", default=[])
    parser.add_argument("--reobserve-only", action="store_true", help="Observe legacy execution/contract artifacts now without provider requests")
    args = parser.parse_args(argv)
    if args.ticker_dir:
        directories = [args.ticker_dir]
    else:
        catalog = archive_catalog(args.archive_dir, analysis_as_of=datetime.now(timezone.utc), include_coverage=False)
        names = args.ticker or sorted(catalog)
        if any(name not in catalog for name in names):
            parser.error("Requested ticker has no completed archived analysis")
        directories = [catalog[name]["ticker_dir"] for name in names]
    results = []
    failed = False
    for directory in directories:
        try:
            operation = reobserve_existing_evidence if args.reobserve_only else refresh_existing_review
            results.append({"status": "reobserved" if args.reobserve_only else "refreshed", **operation(directory, db_paths=args.tracker_db)})
        except Exception as exc:
            # Do not print provider exception bodies, which can contain URLs or
            # credentials. Existing archive remains a valid prior observation.
            results.append({"ticker": directory.name, "status": "unavailable", "error_type": type(exc).__name__})
            failed = True
    print(json.dumps({"results": results, "real_orders_enabled": False}, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
