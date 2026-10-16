"""Render an existing ticker archive; no network, data refresh or broker orders."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tradingagents.charting.report import render_review
from tradingagents.charting.snapshot import get_replay_snapshot
from tradingagents.atomic_io import atomic_write_json


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ticker_dir", type=Path)
    parser.add_argument("--as-of", required=True, help="Timezone-aware cutoff (future information is excluded)")
    parser.add_argument("--anchor", help="Timezone-aware Anchored VWAP start")
    parser.add_argument("--tracker-db", type=Path, action="append", default=[])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        review = get_replay_snapshot(args.ticker_dir.name, args.as_of, ticker_dir=args.ticker_dir,
                                     anchor=args.anchor, db_paths=args.tracker_db)
    except (ValueError, TypeError, KeyError, OSError) as exc:
        parser.error(str(exc))
    output = args.output or args.ticker_dir / "investment_review.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_review(review), encoding="utf-8")
    atomic_write_json(output.with_suffix(".json"), review)
    print(output)
    return 0


if __name__ == "__main__":
    main()
