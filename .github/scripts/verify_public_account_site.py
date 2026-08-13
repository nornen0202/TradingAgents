from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from tradingagents.scheduled.account_site import PUBLIC_ACCOUNT_SCHEMA


SENSITIVE_PATTERNS = (
    re.compile(r"\b\d{8}-\d{2}\b"),
    re.compile(r"\bkis_\d{8}-\d{2}\b", re.IGNORECASE),
)
FORBIDDEN_KEYS = {
    "account_id",
    "account_no",
    "snapshot_id",
    "pending_orders",
    "cash_diagnostics",
    "broker_raw_response",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify the public account snapshot Pages surface.")
    parser.add_argument("--site-dir", required=True)
    parser.add_argument("--require-markets", choices=("all", "kr", "us"), default="all")
    args = parser.parse_args()

    site_dir = Path(args.site_dir).resolve()
    html_path = site_dir / "account" / "index.html"
    json_path = site_dir / "account" / "public.json"
    llms_path = site_dir / "account" / "llms.txt"
    for path in (html_path, json_path, llms_path, site_dir / "robots.txt"):
        _assert(path.is_file(), f"Missing public account site artifact: {path}")
    homepage = (site_dir / "index.html").read_text(encoding="utf-8")
    _assert("account/index.html" in homepage, "Homepage is missing the public account snapshot link.")

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    _assert(isinstance(payload, dict), "Public account JSON must be an object.")
    _assert(payload.get("schema") == PUBLIC_ACCOUNT_SCHEMA, "Unexpected public account schema.")
    _assert(not (FORBIDDEN_KEYS & _all_keys(payload)), "Public account JSON contains private field names.")
    text = json.dumps(payload, ensure_ascii=False)
    for pattern in SENSITIVE_PATTERNS:
        _assert(pattern.search(text) is None, f"Public account JSON leaked {pattern.pattern!r}.")

    markets = payload.get("markets") if isinstance(payload.get("markets"), dict) else {}
    required = ("kr", "us") if args.require_markets == "all" else (args.require_markets,)
    for market in required:
        value = markets.get(market) if isinstance(markets.get(market), dict) else {}
        _assert(value.get("status") == "available", f"Required {market.upper()} account snapshot is unavailable.")
        positions = value.get("positions") if isinstance(value.get("positions"), list) else []
        summary = value.get("summary") if isinstance(value.get("summary"), dict) else {}
        _assert(int(summary.get("position_count") or 0) == len(positions), f"{market.upper()} position count mismatch.")
        for position in positions:
            _assert(isinstance(position, dict), f"{market.upper()} position must be an object.")
            for key in (
                "ticker",
                "name",
                "quantity",
                "sellable_quantity",
                "average_cost_krw",
                "current_price_krw",
                "purchase_amount_krw",
                "market_value_krw",
                "unrealized_pnl_krw",
                "unrealized_return_pct",
            ):
                _assert(key in position, f"{market.upper()} position is missing {key}.")

    html_text = html_path.read_text(encoding="utf-8")
    for fragment in ("주식 잔고 · 손익", "국내", "해외", "public.json", PUBLIC_ACCOUNT_SCHEMA):
        _assert(fragment in html_text, f"Public account page is missing {fragment!r}.")

    print(
        "Verified public account site:",
        json.dumps(
            {
                "schema": payload["schema"],
                "required_markets": list(required),
                "positions": {
                    key: len((markets.get(key) or {}).get("positions") or []) for key in ("kr", "us")
                },
                "page": str(html_path),
                "json": str(json_path),
            },
            ensure_ascii=False,
        ),
    )


def _all_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        result = {str(key).lower() for key in value}
        for item in value.values():
            result.update(_all_keys(item))
        return result
    if isinstance(value, list):
        result: set[str] = set()
        for item in value:
            result.update(_all_keys(item))
        return result
    return set()


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


if __name__ == "__main__":
    main()
