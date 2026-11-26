"""Freeze and read the 14 Yahoo chart responses for the #569 retrospective audit."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

PLAN = Path(__file__).resolve().parents[1] / "Docs/hybrid_execution_audit_plan.json"
ZONES = {"KR": "Asia/Seoul", "US": "America/New_York"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def parse_chart(payload, ticker, market, start, end):
    chart = json.loads(payload)["chart"]
    if chart["error"] or not chart["result"]:
        raise ValueError(f"No chart for {ticker}")
    panel = chart["result"][0]
    meta = panel["meta"]
    zone = ZoneInfo(ZONES[market])
    if meta["symbol"] != ticker or meta["exchangeTimezoneName"] != zone.key:
        raise ValueError(f"Wrong instrument or timezone for {ticker}")
    times = panel.get("timestamp") or []
    indicators = panel["indicators"]
    quote = indicators["quote"][0]
    adj = indicators["adjclose"][0]["adjclose"]
    columns = (times, quote["open"], quote["close"], adj, quote["volume"])
    rows, skipped = {}, Counter()
    for stamp, opening, close, adjusted, volume in zip(*columns, strict=True):
        try:
            day = datetime.fromtimestamp(stamp, zone).date().isoformat()
        except (TypeError, ValueError, OverflowError, OSError):
            skipped["invalid_date"] += 1
            continue
        if not start <= day <= end:
            skipped["outside_dates"] += 1
            continue
        if day in rows:
            raise ValueError(f"Duplicate {ticker} bar on {day}")
        if not all(type(p) in (float, int) and math.isfinite(p) and p > 0 for p in (close, adjusted)):
            skipped["invalid_close"] += 1
            continue
        if type(volume) not in (float, int) or not math.isfinite(volume) or volume < 0:
            skipped["invalid_volume"] += 1
            continue
        adj_open = None
        if type(opening) in (float, int) and math.isfinite(opening) and opening > 0:
            adj_open = opening * (adjusted / close)
        else:
            skipped["missing_open"] += 1
        if volume == 0:
            skipped["zero_volume"] += 1
        rows[day] = {"date": day, "open": adj_open, "close": adjusted, "volume": max(1.0, volume),
                     "executable_volume": volume}
    if not rows:
        raise ValueError(f"No dated, valid observations for {ticker}")
    return list(sorted(rows.values(), key=lambda row: row["date"])), dict(skipped)


def collect(root):
    plan = json.loads(PLAN.read_bytes())
    if root.exists():
        raise FileExistsError(f"Choose a new snapshot directory: {root}")
    manifest = {}
    responses = {}
    for market, spec in plan["markets"].items():
        zone = ZoneInfo(ZONES[market])
        start = datetime.fromisoformat(plan["input_start"]).replace(tzinfo=zone)
        end = date.fromisoformat(plan["end"]) + timedelta(days=1)
        stop = datetime.combine(end, datetime.min.time(), tzinfo=zone)
        for ticker in spec["core"] + spec["satellite"]:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
            params = {"period1": int(start.timestamp()), "period2": int(stop.timestamp()),
                      "interval": "1d", "events": "div,splits,capitalGains", "includeAdjustedClose": "true"}
            response = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
            response.raise_for_status()
            receipt = datetime.now(timezone.utc).isoformat()
            rows, gaps = parse_chart(response.content, ticker, market, plan["input_start"], plan["end"])
            responses[ticker] = response.content
            manifest[ticker] = {"sha256": digest(response.content), "url": response.url,
                                "retrieved_at": receipt, "rows": len(rows), "first": rows[0]["date"],
                                "last": rows[-1]["date"], "diagnostics": gaps}
    # Publish the receipt last. A network failure leaves the destination
    # available for a fresh attempt with a consistent acquisition window.
    root.mkdir(exist_ok=False, parents=True)
    for ticker, payload in responses.items():
        (root / f"{ticker}.json").write_bytes(payload)
    (root / "receipts.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("new_directory", type=Path)
    collect(parser.parse_args().new_directory)
