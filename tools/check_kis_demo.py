"""Read-only VTS configuration/authentication/balance check. Never submits orders."""

import argparse
from datetime import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from tradingagents.execution.kis_demo import (
    DemoCredentials,
    DemoError,
    KisDemoClient,
    configuration_status,
)


def check(*, connect=False):
    configured = configuration_status()
    result = {
        "mode": "KIS_DEMO",
        "configured": configured,
        "status": "READY_TO_PROBE"
        if all(configured.values())
        else "MISSING_DEMO_SETTINGS",
        "orders_submitted": 0,
        "real_account_access": False,
    }
    if not all(configured.values()) or not connect:
        return result
    client = None
    try:
        client = KisDemoClient(DemoCredentials.from_local_settings())
        positions, _ = client.balance()
        orders = client.orders(datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y%m%d"))
        result.update(
            status="READ_CONNECTION_VERIFIED",
            position_rows=len(positions),
            order_rows=len(orders),
        )
    except (DemoError, ValueError):
        result.update(
            status="CONNECTION_UNVERIFIED",
            reason="VTS authentication, scope or response validation failed",
        )
    finally:
        if client:
            client.close()
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--connect", action="store_true")
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = check(connect=args.connect)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
