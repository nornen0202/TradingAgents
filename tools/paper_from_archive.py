"""Consume one canonical archived KIS decision bundle into a local paper ledger.

Run after a producer finishes, not during its writes. Existing gates and explicit
whole-share proposals are required. Missing quantity is recorded, never inferred.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from tradingagents.execution.paper import PaperBroker, PaperLimits, stamp


def build_step(run: Path, now: str):
    def read(name):
        return json.loads((run / name).read_text(encoding="utf-8-sig"))

    meta = read("run.json")
    if meta.get("status") != "success":
        raise ValueError("Only a completed successful producer may be consumed")
    bundle = read("decision_bundle_v2.json")
    snapshot = read("portfolio-private/account_snapshot.json")
    proposals = read("portfolio-private/proposed_orders.json").get("orders", [])
    market = str(bundle["market"]).lower()
    if market not in {"kr", "us"}:
        raise ValueError("KR/US required")
    local_now = (
        stamp(now)
        .astimezone(ZoneInfo("Asia/Seoul" if market == "kr" else "America/New_York"))
        .isoformat()
    )
    quotes, signals = {}, []
    mapping = {
        "STARTER_NOW": "BUY",
        "ADD_NOW": "BUY",
        "BUY_NOW": "BUY",
        "REDUCE_NOW": "REDUCE",
        "EXIT_NOW": "SELL",
        "TAKE_PROFIT_NOW": "REDUCE",
    }
    for row in bundle.get("strategy_table", []):
        ticker = row["ticker"]
        quality = row.get("quality", {})
        raw = row.get("raw_codes", {})
        asof = row.get("market_data_asof")
        ready = (
            quality.get("execution_ready") is True
            and quality.get("generated_in_current_run") is True
        )
        # KR prices are already in the paper base currency. US conversion needs
        # an independently timestamped FX adapter, deliberately unavailable here.
        if asof and market == "kr":
            quotes[ticker] = {
                "as_of": asof,
                "price_krw": row.get("last_price"),
                "session": "regular"
                if row.get("market_session") == "regular"
                else row.get("market_session"),
                "executable": ready,
                "spread_bps": row.get("spread_bps"),
            }
        action = mapping.get(raw.get("decision_now")) or mapping.get(
            raw.get("portfolio_action_now")
        )
        if not action:
            continue
        proposal = next(
            (
                p
                for p in proposals
                if p.get("canonical_ticker") == ticker
                and p.get("side", "").upper() == ("BUY" if action == "BUY" else "SELL")
            ),
            {},
        )
        qty = proposal.get("estimated_qty")
        qty = (
            int(qty)
            if isinstance(qty, (int, float)) and qty > 0 and int(qty) == qty
            else None
        )
        signals.append(
            {
                "signal_id": f"{bundle.get('analysis_source_run_id')}:{ticker}:{action}",
                "ticker": ticker,
                "action": action,
                "quantity": qty,
                "execution_ready": ready,
                "available_at": bundle["generated_at"],
                "valid_until": (stamp(asof) + timedelta(seconds=120)).isoformat()
                if asof
                else bundle["generated_at"],
            }
        )
    return snapshot, {"now": local_now, "quotes": quotes, "signals": signals}, market


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--ledger", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--seed", action="store_true")
    a = p.parse_args()
    now = datetime.now().astimezone().isoformat()
    snapshot, step, market = build_step(a.run, now)
    broker = PaperBroker(a.ledger, PaperLimits())
    try:
        if a.seed:
            broker.seed(snapshot)
        result = broker.step(**step)
        result["market"] = market
        result["source_run"] = a.run.name
        result["limitations"] = [
            "US price/FX adapter not connected; no US fills",
            "No fresh quote or explicit integer proposal means no paper order",
            "No KIS VTS/real order transport",
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
