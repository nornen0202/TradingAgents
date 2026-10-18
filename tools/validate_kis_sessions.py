"""Advance the finite VTS-only session campaign; default is offline status."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tradingagents.execution.demo_validation import run_campaign


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive-root", type=Path, required=True)
    parser.add_argument("--state-root", type=Path, required=True)
    parser.add_argument("--run", action="store_true", help="Explicitly allow bounded VTS-only campaign steps")
    args = parser.parse_args(argv)
    try:
        result = run_campaign(args.archive_root, args.state_root, run=args.run)
    except (OSError, ValueError, TimeoutError):
        print(json.dumps({"mode": "KIS_DEMO", "status": "BLOCKED", "live_orders_enabled": False}))
        return 2
    print(json.dumps(result, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
