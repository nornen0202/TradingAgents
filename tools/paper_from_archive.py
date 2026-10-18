"""Consume one canonical archived KIS decision bundle into a local paper ledger.

Run after a producer finishes, not during its writes. Existing gates and explicit
whole-share quantities or explicit budgets are required; prose is never sized.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path

from tradingagents.execution.paper import PaperBroker, PaperLimits
from tradingagents.execution.archive_paper import build_step




def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--ledger", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--seed", action="store_true")
    p.add_argument("--limits", type=Path)
    a = p.parse_args()
    now = datetime.now().astimezone().isoformat()
    limits = (
        PaperLimits(**json.loads(a.limits.read_text(encoding="utf-8-sig")))
        if a.limits
        else PaperLimits()
    )
    snapshot, step, market = build_step(a.run, now, limits)
    broker = PaperBroker(a.ledger, limits)
    try:
        if a.seed:
            broker.seed(snapshot)
        result = broker.step(**step)
        result["market"] = market
        result["source_run"] = a.run.name
        result["limitations"] = [
            "US price/FX adapter not connected; no US fills",
            "Fresh quote and explicit integer quantity or sufficient budget required",
            "This local adapter does not send KIS VTS/real orders",
            "Local paper fee/tax assumptions; immediate reusable proceeds; no partial fills",
        ]
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(
            json.dumps(
                {
                    k: v
                    for k, v in result.items()
                    if k not in {"orders", "nav_krw", "cash_krw"}
                },
                ensure_ascii=True,
            )
        )
    finally:
        broker.close()


if __name__ == "__main__":
    main()
