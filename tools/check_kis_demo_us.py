"""Masked US-only VTS readiness or read-only authentication/balance/order probe."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from tradingagents.atomic_io import atomic_write_json
from tradingagents.execution.demo_secrets import SecretStoreError
from tradingagents.execution.kis_demo import DEMO_HOST, DemoError
from tradingagents.execution.kis_demo_us import (
    EXCHANGES, NEW_YORK, KisDemoUSReadClient, configuration_status, credentials_from_settings,
)


def check(*, connect=False):
    result = {"mode": "KIS_DEMO", "market": "US", "host": DEMO_HOST,
              "orders_submitted": 0, "live_orders_enabled": False,
              "real_account_access": False, "us_order_execution_enabled": False,
              "paper_order_connection_verified": False,
              "checked_at": datetime.now(timezone.utc).isoformat()}
    try:
        configured = configuration_status()
    except SecretStoreError:
        return {**result, "status": "CONFIGURATION_UNREADABLE"}
    result.update(configured=configured, status="READY_TO_PROBE" if all(configured.values()) else "MISSING_DEMO_SETTINGS")
    if not connect or not all(configured.values()):
        return result
    client = None
    try:
        client = KisDemoUSReadClient(credentials_from_settings())
        counts = {exchange: len(client.balance(exchange)[0]) for exchange in EXCHANGES}
        trade_date = datetime.now(NEW_YORK).strftime("%Y%m%d")
        orders = client.orders(trade_date)
        result.update(status="READ_CONNECTION_VERIFIED", position_rows_by_exchange=counts,
                      order_rows=len(orders), order_trade_date=trade_date,
                      checked_at=datetime.now(timezone.utc).isoformat(),
                      balance_time_basis="CURRENT_RECEIPT_ONLY_NOT_HISTORICAL_EVIDENCE")
    except (DemoError, SecretStoreError, ValueError, TypeError):
        result.update(status="CONNECTION_UNVERIFIED", reason="US VTS authentication, scope or response validation failed")
    finally:
        if client:
            client.close()
    result["checked_at"] = datetime.now(timezone.utc).isoformat()
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--connect", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    result = check(connect=args.connect)
    atomic_write_json(args.output, result)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] in {"READY_TO_PROBE", "READ_CONNECTION_VERIFIED"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
