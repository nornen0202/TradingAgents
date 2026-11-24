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


class _FixedHostConnection(connect):
    def process_redirect(self, exc):
        return exc


async def _read_feed(kr, us, credentials, hts_ids, *, state, approval, attempts):
    scopes = tuple(VtsScope(market, hts_ids[market], credentials.account_no + credentials.product_code)
                   for market in _MARKETS)
    calls = {"KR": 0, "US": 0}

    async def resynchronize():
        now = datetime.now(timezone.utc)
        for market, client in (("KR", kr), ("US", us)):
            date = now.astimezone(ZoneInfo(_MARKETS[market][0])).strftime("%Y%m%d")
            await asyncio.to_thread(client.orders, date)
            calls[market] += 1

    async def ignore(_event):
        return None

    async def key():
        return approval

    result = await run_event_feed(state / "vts-notice-feed.lock", scopes, subscription_plan(scopes),
        open_vts=lambda: _FixedHostConnection(DEMO_WEBSOCKET, proxy=None, open_timeout=8, logger=_LOG),
        approval=key, resynchronize=resynchronize, on_hint=ignore, on_quote=ignore,
        sleep=asyncio.sleep, attempts=attempts, idle_seconds=5)
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
            creds = DemoCredentials.from_local_settings()
            us_credentials = credentials_from_settings()
            if creds != us_credentials:
                raise DemoError("Separate subscriptions require explicitly matched VTS scopes")
            kr = KisDemoClient(creds)
            clients.append(kr)
            approval = kr.websocket_approval()
            result["approval_verified"] = True
            if not all(hts_ids.values()):
                result["status"] = "MISSING_DEMO_HTS_ID"
                return result
            us = KisDemoUSReadClient(us_credentials)
            clients.append(us)
            result["feed"] = asyncio.run(_read_feed(kr, us, creds, hts_ids, state=state, approval=approval, attempts=attempts))
            result["status"] = "SUBSCRIPTIONS_VERIFIED" if result["feed"]["verified_notice_sessions"] else "SUBSCRIPTIONS_UNVERIFIED"
    except TimeoutError:
        result["status"] = "BROKER_LANE_BUSY"
    except (DemoError, OSError, ValueError):
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
