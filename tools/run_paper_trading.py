"""Seed/advance a persistent local paper ledger; no network or real orders.

Input: {now, quotes, signals, optional halted}, using PaperBroker.step's contract.
"""

import argparse
import json
from pathlib import Path

from tradingagents.execution.paper import PaperBroker, PaperLimits


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ledger", required=True, type=Path)
    p.add_argument("--seed-snapshot", type=Path)
    p.add_argument("--input", type=Path)
    p.add_argument("--limits", type=Path)
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    limits = (
        PaperLimits(**json.loads(a.limits.read_text(encoding="utf-8")))
        if a.limits
        else PaperLimits()
    )
    broker = PaperBroker(a.ledger, limits)
    try:
        if a.seed_snapshot:
            broker.seed(json.loads(a.seed_snapshot.read_text(encoding="utf-8")))
        result = {
            "mode": "LOCAL_PAPER_ONLY",
            "broker_orders_sent": 0,
            "seeded": bool(a.seed_snapshot),
        }
        if a.input:
            result = broker.step(**json.loads(a.input.read_text(encoding="utf-8")))
        payload = json.dumps(result, ensure_ascii=False, indent=2)
        if a.output:
            a.output.parent.mkdir(parents=True, exist_ok=True)
            a.output.write_text(payload, encoding="utf-8")
        else:
            print(payload)
    finally:
        broker.close()


if __name__ == "__main__":
    main()
