"""Check KIS virtual-account notice subscriptions and REST availability safely."""
import argparse
import asyncio
from dataclasses import asdict
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from zoneinfo import ZoneInfo

from websockets.asyncio.client import connect
from websockets.exceptions import InvalidHandshake

from tradingagents.atomic_io import atomic_write_json, interprocess_file_lock
from tradingagents.dataflows.api_keys import get_api_key
from tradingagents.execution.kis_demo import DEMO_HOST, DemoCredentials, DemoError, KisDemoClient
from tradingagents.execution.kis_demo_us import KisDemoUSReadClient, credentials_from_settings
from tradingagents.execution.kis_vts_feed import VtsScope, run_event_feed, subscription_plan


DEMO_WEBSOCKET = "ws://ops.koreainvestment.com:31000/tryitout"
_MARKETS = {"KR": ("Asia/Seoul", "H0STCNI9"), "US": ("America/New_York", "H0GSCNI9")}
_LOG = logging.getLogger("tradingagents.private_vts_websocket")
_LOG.addHandler(logging.NullHandler())
_LOG.propagate = False
_ATTEMPT_SECONDS = 20


class _FixedHostConnection(connect):
    def process_redirect(self, exc):
        return exc


async def _read_feed(clients, hts_ids, *, state, approval, attempts):
    scopes = tuple(VtsScope(market, hts_ids[market], client.credentials.account_no + client.credentials.product_code)
                   for market, client in clients.items())
    calls = {market: 0 for market in clients}

    async def resynchronize():
        now = datetime.now(timezone.utc)
        for market, client in clients.items():
            date = now.astimezone(ZoneInfo(_MARKETS[market][0])).strftime("%Y%m%d")
            # Keep the shared broker locks through completion of the bounded
            # HTTP call, including when the WebSocket observation is cancelled.
            client.orders(date)
            calls[market] += 1

    async def ignore(_event):
        return None

    async def key():
        return approval

    try:
        async with asyncio.timeout(attempts * _ATTEMPT_SECONDS):
            result = await run_event_feed(state / "vts-notice-feed.lock", scopes, subscription_plan(scopes),
                open_vts=lambda: _FixedHostConnection(DEMO_WEBSOCKET, proxy=None, open_timeout=8, close_timeout=3, logger=_LOG),
                approval=key, resynchronize=resynchronize, on_hint=ignore, on_quote=ignore,
                sleep=asyncio.sleep, attempts=attempts, idle_seconds=5, stop_after_recovery=True)
    except TimeoutError:
        raise ValueError("VTS notice observation did not complete before the deadline") from None
    return asdict(result) | {"rest_order_inquiries": calls}


def check(state, *, connect_to_broker=False, attempts=1):
    result = {"mode": "KIS_DEMO", "rest_host": DEMO_HOST, "websocket_host": DEMO_WEBSOCKET,
              "order_notice_tr": {market: terms[1] for market, terms in _MARKETS.items()},
              "checked_at": datetime.now(timezone.utc).isoformat(), "real_orders_enabled": False,
              "orders_submitted": 0, "status": "READY_TO_PROBE"}
    common = get_api_key("KIS_DEMO_HTS_ID")
    hts_ids = {"KR": common, "US": get_api_key("KIS_DEMO_US_HTS_ID") or common}
    result["hts_configured"] = {market: bool(value) for market, value in hts_ids.items()}
    if not connect_to_broker:
        if not all(hts_ids.values()):
            result["status"] = "MISSING_DEMO_HTS_ID"
        return result
    clients = []
    try:
        with (interprocess_file_lock(state / "strategy.lock", timeout=0),
              interprocess_file_lock(state.parent / "kis-validation/campaign.lock", timeout=0)):
            credentials = {"KR": DemoCredentials.from_local_settings(), "US": credentials_from_settings()}
            shared = credentials["KR"] == credentials["US"]
            kr = KisDemoClient(credentials["KR"])
            clients.append(kr)
            approvals = {"KR": kr.websocket_approval()}
            result["approval_verified_by_market"] = {"KR": True, "US": False}
            if shared:
                approvals["US"] = approvals["KR"]
            else:
                us_auth = KisDemoClient(credentials["US"])
                clients.append(us_auth)
                approvals["US"] = us_auth.websocket_approval()
            result["approval_verified_by_market"]["US"] = True
            result["approval_verified"] = True
            if not all(hts_ids.values()):
                result["status"] = "MISSING_DEMO_HTS_ID"
                return result
            us = KisDemoUSReadClient(credentials["US"])
            clients.append(us)
            read_clients = {"KR": kr, "US": us}
            if shared:
                result["feed"] = asyncio.run(_read_feed(read_clients, hts_ids, state=state, approval=approvals["KR"], attempts=attempts))
                verified = result["feed"]["verified_notice_sessions"] > 0
            else:
                result["feed_by_market"] = {market: asyncio.run(_read_feed({market: client}, hts_ids, state=state,
                    approval=approvals[market], attempts=attempts)) for market, client in read_clients.items()}
                verified = all(row["verified_notice_sessions"] > 0 for row in result["feed_by_market"].values())
            result["status"] = "SUBSCRIPTIONS_VERIFIED" if verified else "SUBSCRIPTIONS_UNVERIFIED"
    except TimeoutError:
        result["status"] = "BROKER_LANE_BUSY"
    except (DemoError, InvalidHandshake, OSError, ValueError):
        result["status"] = "VTS_FEED_UNVERIFIED"
    finally:
        for client in clients:
            client.close()
        result["checked_at"] = datetime.now(timezone.utc).isoformat()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, required=True, help="Existing strategy state directory")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--connect", action="store_true")
    parser.add_argument("--attempts", type=int, choices=range(1, 4), default=1)
    args = parser.parse_args()
    result = check(args.state_dir, connect_to_broker=args.connect, attempts=args.attempts)
    atomic_write_json(args.output, result)
    print(json.dumps(result, ensure_ascii=True))
    return 0 if result["status"] in {"READY_TO_PROBE", "SUBSCRIPTIONS_VERIFIED"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
