"""KIS VTS-only readiness, guarded orders and reconciliation.

Readiness is offline by default. ``probe`` performs demo authentication/account
reads only. Every write requires --paper-enabled; there is no live mode or host
argument. Dedicated credentials are loaded by the existing protected local setup.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from tradingagents.atomic_io import atomic_write_json
from tradingagents.execution.demo_secrets import SecretStoreError
from tradingagents.execution.kis_demo import DEMO_HOST, DemoCredentials, DemoError, KisDemoClient
from tradingagents.execution.kis_paper import KisPaperBroker, PaperOrderPolicy, read_paper_account
from tools.check_kis_demo import check


def _load(path):
    value = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError("Input must be a JSON object")
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("readiness", help="Offline masked configuration only")
    sub.add_parser("probe", help="VTS authentication, balance and order reads only")
    for command in ("submit", "reconcile", "cancel", "status"):
        item = sub.add_parser(command)
        item.add_argument("--journal", type=Path, required=True)
        item.add_argument("--policy", type=Path, required=True)
        item.add_argument("--paper-enabled", action="store_true")
        if command == "submit":
            item.add_argument("--input", type=Path, required=True)
        elif command in {"reconcile", "cancel"}:
            item.add_argument("--intent-id", required=True)
    args = parser.parse_args(argv)
    client = broker = None
    try:
        if args.command in {"readiness", "probe"}:
            result = {**check(connect=args.command == "probe"), "host": DEMO_HOST,
                      "market": "KR", "checked_at": datetime.now(timezone.utc).isoformat(),
                      "live_orders_enabled": False, "paper_order_connection_verified": False}
        else:
            if args.command in {"submit", "cancel"} and not args.paper_enabled:
                raise DemoError("--paper-enabled is required for VTS writes")
            policy_data = _load(args.policy)
            tickers = policy_data.get("allowed_tickers")
            if not isinstance(tickers, list):
                raise ValueError("Policy requires allowed_tickers list")
            policy_data["allowed_tickers"] = tuple(tickers)
            policy = PaperOrderPolicy(**policy_data)
            client = KisDemoClient(DemoCredentials.from_local_settings())
            broker = KisPaperBroker(args.journal, client, policy, paper_enabled=args.paper_enabled)
            if args.command == "submit":
                payload = _load(args.input)
                required = {"intent_id", "ticker", "side", "quantity", "limit_price", "signal", "quote"}
                if set(payload) != required:
                    raise ValueError("Order input requires exact terms, signal and quote; account is read from VTS")
                # Duplicate IDs do not need a new balance query, authentication
                # or order POST. The facade validates immutable terms itself.
                previous = broker.db.execute("SELECT 1 FROM paper_intents WHERE id=?", (payload["intent_id"],)).fetchone()
                account = {} if previous else read_paper_account(client, ticker=payload["ticker"], limit_price=payload["limit_price"])
                result = broker.submit(**payload, account=account)
            elif args.command == "reconcile":
                result = broker.reconcile(intent_id=args.intent_id)
            elif args.command == "cancel":
                result = broker.cancel(intent_id=args.intent_id)
            else:
                result = broker.status()
    except (DemoError, SecretStoreError, OSError, ValueError, TypeError):
        # Never serialize exception text, broker error bodies or credential paths.
        result = {"mode": "demo", "status": "BLOCKED", "reason": "VTS configuration, policy or evidence validation failed",
                  "live_orders_enabled": False}
        if args.output:
            atomic_write_json(args.output, result)
        print(json.dumps(result, ensure_ascii=False))
        return 2
    finally:
        if broker:
            broker.close()
        if client:
            client.close()
    if args.output:
        atomic_write_json(args.output, result)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
