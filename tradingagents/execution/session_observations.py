"""Capture regular-session prices and monitoring receipts without order access."""
from __future__ import annotations

import argparse
from contextlib import closing as closing_connection
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import sqlite3
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

import requests

from tradingagents.atomic_io import atomic_write_json, interprocess_file_lock
from tradingagents.charting.bars import instant
from .promotion import _sessions
from .session_confirmation import RECEIPT_SCHEMA, _official_observations, _schedule
from .kis_demo import DEMO_HOST, DemoError, _pacer

SCHEMA = "tradingagents.forward-market-observation/v1"
ZONES = {"KR": "Asia/Seoul", "US": "America/New_York"}
CURRENCIES = {"KR": "KRW", "US": "USD"}
KINDS = {"open": "official_regular_open", "close": "final_regular_close"}
VENUES = {"KR": {"J"}, "US": {"NAS", "NYS", "AMS"}}
MAX_WATCHLIST_SIZE = 50
MAX_REQUESTS_PER_PASS = 4
_QUOTATION_TRANSPORT = {
    ("POST", "/oauth2/tokenP", None),
    ("GET", "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice", "FHKST03010100"),
    ("GET", "/uapi/overseas-price/v1/quotations/dailyprice", "HHDFS76240000"),
}


class _QuotationSession(requests.Session):
    def __init__(self, pacer):
        super().__init__()
        self.trust_env = False
        self._pacer = pacer

    def request(self, method, url, **kwargs):
        target = urlsplit(url)
        key = (method, target.path, (kwargs.get("headers") or {}).get("tr_id"))
        if (f"{target.scheme}://{target.netloc}" != DEMO_HOST or target.query or target.fragment
                or key not in _QUOTATION_TRANSPORT or kwargs.get("allow_redirects") is not False):
            raise DemoError("Outside the dedicated quote route.")
        self._pacer.wait()
        return super().request(method, url, **kwargs)


def _now():
    return datetime.now(timezone.utc)


def _watchlist(path):
    with path.open("rb") as stream:
        data = json.load(stream)
    if (not isinstance(data, dict) or set(data) != {"schema", "instruments"}
            or data["schema"] != SCHEMA or not isinstance(data["instruments"], list)
            or not 1 <= len(data["instruments"]) <= MAX_WATCHLIST_SIZE):
        raise ValueError("Provide a versioned watchlist of up to fifty read-only symbols.")
    symbols = set()
    for item in data["instruments"]:
        if not isinstance(item, dict) or set(item) != {"ticker", "market", "venue"}:
            raise ValueError("Market, ticker and venue are required.")
        ticker, market, venue = item["ticker"], item["market"], item["venue"]
        if (not all(isinstance(v, str) for v in (ticker, market, venue))
                or venue not in VENUES.get(market, ())
                or not re.fullmatch(r"[0-9]{6}\.(?:KS|KQ)" if market == "KR"
                                    else r"[A-Z][A-Z0-9.-]{0,14}", ticker)
                or ticker in symbols):
            raise ValueError("Invalid or duplicated watchlist instrument.")
        symbols.add(ticker)
    return data["instruments"]


def _new_client(market):
    # Only dedicated, protected demo bundles are accepted here. Existing
    # read-only research providers keep their own separately configured routes.
    from tradingagents.portfolio.kis import KisClient
    if market == "US":
        from .kis_demo_us import credentials_from_settings
        credentials = credentials_from_settings()
    else:
        from .kis_demo import DemoCredentials
        credentials = DemoCredentials.from_local_settings()
    return KisClient(app_key=credentials.app_key, app_secret=credentials.app_secret,
                     environment="demo", timeout_seconds=5, token_file_cache_enabled=False,
                     session=_QuotationSession(_pacer(credentials)))


def _download(item, session, client):
    if item["market"] == "KR":
        return client.domestic_daily_itemchartprice(item["ticker"][:6], start_date=session, end_date=session,
            market_division="J", period_division="D", adjusted_price="1")
    from tradingagents.dataflows.intraday.us_symbols import kis_symbol
    body, _ = client.request_json(method="GET", path="/uapi/overseas-price/v1/quotations/dailyprice",
        tr_id="HHDFS76240000", params={"AUTH": "", "EXCD": item["venue"], "SYMB": kis_symbol(item["ticker"]),
                                      "GUBN": "0", "BYMD": session.replace("-", ""), "MODP": "0"})
    return body


def _prices(payload, item, day):
    fields = ("stck_bsop_date", "stck_oprc", "stck_clpr", "stck_hgpr", "stck_lwpr", "acml_vol") if item["market"] == "KR" else (
        "xymd", "open", "clos", "high", "low", "tvol")
    rows = payload.get("output2") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        raise ValueError("Missing source rows.")
    selected = [row for row in rows if isinstance(row, dict) and row.get(fields[0]) == day.replace("-", "")]
    if len(selected) != 1:
        raise ValueError("Exact requested daily row or unambiguous identity unavailable.")
    row = selected[0]
    opening, closing, high, low, volume = (float(row[field]) for field in fields[1:])
    if (not all(math.isfinite(v) and v > 0 for v in (opening, closing, high, low, volume))
            or not low <= min(opening, closing) <= max(opening, closing) <= high):
        raise ValueError("Invalid or untraded regular-session bar.")
    return {"open": opening, "close": closing, "high": high, "low": low, "volume": volume}


def _evidence(item, day, kind, event, observed, price):
    market, venue = item["market"], item["venue"]
    return {"kind": KINDS[kind], "event_at": event.isoformat(), "observed_at": observed.isoformat(),
            "price": price, "ticker": item["ticker"], "market": item["market"], "currency": CURRENCIES[item["market"]],
            "session": day, "venue": venue, "session_id": f"{market}:{venue}:regular:{day}",
            "price_basis": "unadjusted", "revised_at": None,
            "source": "KIS_DOMESTIC_REGULAR_SESSION" if market == "KR" else "KIS_US_REGULAR_SESSION"}


def load_collected_observations(path, ticker, market, *, now):
    """Read verified market evidence directly from the collector's append-only store."""
    if path is None or market not in ZONES or (cutoff := instant(now)) is None:
        return {}
    day = cutoff.astimezone(ZoneInfo(ZONES[market])).date().isoformat()
    try:
        with closing_connection(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)) as db:
            rows = db.execute("""
                SELECT session, stage, observed_at, source_sha256, raw_response, evidence FROM observations
                WHERE ticker=? AND market=? AND observed_at<=? AND evidence IS NOT NULL AND
                      ((stage='open' AND session=?) OR (stage='close' AND session<=?))
                ORDER BY session DESC LIMIT 3
                """, (ticker, market, cutoff.isoformat(), day, day)).fetchall()
        observations = {}
        for session, stage, observed_at, digest, raw, evidence in rows:
            key = {"open": "official_open", "close": "regular_close"}[stage]
            if key in observations or hashlib.sha256(raw).hexdigest() != digest:
                continue
            record = json.loads(evidence)
            venue = record.get("venue")
            if (venue not in VENUES[market] or record.get("session_id") != f"{market}:{venue}:regular:{session}"
                    or record.get("kind") != KINDS[stage] or record.get("session") != session
                    or record.get("observed_at") != observed_at
                    or record.get("price_basis") != "unadjusted" or record.get("ticker") != ticker
                    or record.get("market") != market or record.get("currency") != CURRENCIES[market]):
                continue
            if stage == "open" and market == "US":
                continue  # KIS US opening values are provisional and may be corrected the next day.
            if _prices(json.loads(raw), {"market": market}, session)[stage] == record.get("price"):
                observations[key] = record
        return _official_observations(observations, market)
    except (OSError, sqlite3.Error, AttributeError, KeyError, TypeError, ValueError):
        return {}


def _latest_confirmation(db, ticker, stage, before_session):
    operator = "<" if stage == "close" else "="
    row = db.execute(f"""SELECT evidence FROM observations WHERE ticker=? AND stage=? AND session {operator} ?
                         AND evidence IS NOT NULL ORDER BY session DESC LIMIT 1""", (ticker, stage, before_session)).fetchone()
    return json.loads(row[0]) if row else None


def _confirmation(db, root, item, day, stage, evidence):
    if stage == "open":
        closing = _latest_confirmation(db, item["ticker"], "close", day)
        opening = evidence if evidence and evidence.get("kind") == KINDS["open"] else None
    else:
        closing = evidence
        opening = None
    if closing or opening:
        path = root / "confirmations" / f"{item['ticker']}.json"
        document = {
            "schema": RECEIPT_SCHEMA, "ticker": item["ticker"], "market": item["market"],
            "price_basis": "unadjusted", "regular_close": closing, "official_open": opening}
        if not path.is_file() or json.loads(path.read_bytes()) != document:
            atomic_write_json(path, document)


def _strategy_state(operations):
    if operations is None:
        return "OPERATING_STATE_NOT_ATTACHED"
    try:
        settings = json.loads((Path(operations) / "kis-strategy/enabled.json").read_bytes())
        if settings.get("mode") == "KIS_DEMO_STRATEGY" and settings.get("enabled") is False:
            return "PAPER_STRATEGY_DISABLED"
    except (OSError, ValueError, AttributeError):
        return "OPERATING_STATE_UNVERIFIED"
    return "BROKER_EVIDENCE_NOT_EVALUATED"


def capture_due(root, *, operations=None, clock=_now, sessions=_schedule, download=None, confirmation_writer=_confirmation):
    """One pass at the actual clock. Re-observation never replaces accepted bytes."""
    root = Path(root)
    if not (root / "policy.json").is_file():
        return []
    watchlist = _watchlist(root / "policy.json")
    watchlist_hash = hashlib.sha256(json.dumps(watchlist, sort_keys=True).encode()).hexdigest()
    start = instant(clock())
    if start is None:
        raise ValueError("Collector requires an aware clock.")
    clients = {}
    out = []
    requests_used = 0
    try:
        with interprocess_file_lock(root / "capture.lock", timeout=0), closing_connection(sqlite3.connect(root / "observations.sqlite")) as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS observations (
                ticker TEXT, market TEXT, session TEXT, stage TEXT, observed_at TEXT, status TEXT,
                source_sha256 TEXT, raw_response BLOB, price_json TEXT, evidence TEXT,
                PRIMARY KEY(ticker, session, stage));
            CREATE TABLE IF NOT EXISTS observation_failures (
                ticker TEXT, market TEXT, session TEXT, stage TEXT, observed_at TEXT, status TEXT,
                PRIMARY KEY(ticker, session, stage, observed_at));
            CREATE TABLE IF NOT EXISTS observation_registration (
                singleton INTEGER PRIMARY KEY CHECK(singleton=1), watchlist_hash TEXT NOT NULL, started_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS monitor_days (
                market TEXT, session TEXT, checked_at TEXT, reason TEXT, PRIMARY KEY(market,session));
            CREATE TRIGGER IF NOT EXISTS immutable_observations_update BEFORE UPDATE ON observations
                BEGIN SELECT RAISE(ABORT, 'Market observation is append-only'); END;
            CREATE TRIGGER IF NOT EXISTS immutable_observations_delete BEFORE DELETE ON observations
                BEGIN SELECT RAISE(ABORT, 'Market observation is append-only'); END;
            """)
            with db:
                db.execute("INSERT OR IGNORE INTO observation_registration VALUES (1,?,?)", (watchlist_hash, start.isoformat()))
            registered = db.execute("SELECT watchlist_hash FROM observation_registration").fetchone()[0]
            if watchlist_hash != registered:
                raise ValueError("Register a new private root to change the frozen watchlist.")
            for item in watchlist:
                market, ticker = item["market"], item["ticker"]
                day = start.astimezone(ZoneInfo(ZONES[market])).date().isoformat()
                session = next(iter(sessions(market, day)), None)
                if session is None or session[0] != day or start < session[1]:
                    continue
                _, opening, closing = session
                stage, event = ("open", opening) if start < closing else ("close", closing)
                if stage == "close" and start < closing + timedelta(minutes=5):
                    continue  # the provider needs to publish its post-close daily record
                if stage == "close":
                    with db:
                        db.execute("INSERT OR IGNORE INTO monitor_days VALUES(?,?,?,?)",
                            (market, day, start.isoformat(), _strategy_state(operations)))
                existing = db.execute("SELECT evidence FROM observations WHERE ticker=? AND session=? AND stage=?",
                                      (ticker, day, stage)).fetchone()
                if existing:
                    # A crash after SQLite commit may have preceded the consumer file.
                    confirmation_writer(db, root, item, day, stage, json.loads(existing[0]) if existing[0] else None)
                    continue
                opening_window = stage == "open" and start <= opening + timedelta(seconds=30)
                cooldown = timedelta(seconds=4) if opening_window else timedelta(minutes=10)
                if db.execute("""SELECT 1 FROM observation_failures WHERE ticker=? AND session=? AND stage=?
                                 AND observed_at>?""", (ticker, day, stage, (start-cooldown).isoformat())).fetchone():
                    continue
                if requests_used >= MAX_REQUESTS_PER_PASS:
                    continue
                requests_used += 1
                try:
                    if download is None:
                        if market not in clients:
                            clients[market] = _new_client(market)
                        payload = _download(item, day, clients[market])
                    else:
                        payload = download(item, day)
                    received = instant(clock())
                    if received is None or received < start:
                        raise ValueError("Provider reception clock regressed.")
                    if received.astimezone(ZoneInfo(ZONES[market])).date().isoformat() != day or (
                        stage == "open" and received >= closing
                    ):
                        raise ValueError("Provider response outside the requested capture session.")
                    prices = _prices(payload, item, day)
                    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, allow_nan=False).encode("utf-8")
                except (OSError, RuntimeError, TypeError, ValueError, KeyError):
                    with db:
                        db.execute("INSERT OR IGNORE INTO observation_failures VALUES(?,?,?,?,?,?)",
                                   (ticker, market, day, stage, start.isoformat(), "SOURCE_UNVERIFIED"))
                    out.append({"market": market, "session": day, "stage": stage, "status": "SOURCE_UNVERIFIED"})
                    continue
                late = stage == "open" and received > opening + timedelta(seconds=30)
                # The missed opening is still a real observed daily price. It
                # cannot satisfy the next-open execution proof retroactively.
                status = ("OBSERVED_LATE_OPEN" if late else "OBSERVED_PROVISIONAL_OPEN"
                          if stage == "open" and market == "US" else "OBSERVED")
                # A proved opening print was available by receipt; using that
                # clock is conservative when the precise exchange tick is absent.
                evidence = _evidence(item, day, stage, received if stage == "open" else event, received, prices[stage])
                evidence["scheduled_event_at"] = event.isoformat()
                if stage == "open":
                    evidence["kind"] = ("provisional_regular_open" if market == "US"
                                        else "late_regular_open" if late else KINDS[stage])
                if stage == "close":
                    status = "OBSERVED_MARKET_ONLY"
                with db:
                    db.execute("INSERT INTO observations VALUES(?,?,?,?,?,?,?,?,?,?)",
                        (ticker, market, day, stage, received.isoformat(), status, hashlib.sha256(raw).hexdigest(),
                         raw, json.dumps(prices), json.dumps(evidence) if evidence else None))
                confirmation_writer(db, root, item, day, stage, evidence)
                out.append({"market": market, "session": day, "stage": stage, "status": status})
    finally:
        for client in clients.values():
            client.session.close()
    return out


def scheduled_capture(state):
    try:
        return capture_due(Path(state) / "forward-observation", operations=state)
    except (OSError, RuntimeError, ValueError, TimeoutError, sqlite3.Error):
        return [{"status": "COLLECTION_UNAVAILABLE"}]


def observation_status(root, *, clock=_now):
    root = Path(root)
    with closing_connection(sqlite3.connect((root / "observations.sqlite").resolve().as_uri() + "?mode=ro", uri=True)) as db:
        watchlist = _watchlist(root / "policy.json")
        registered, since = db.execute("SELECT watchlist_hash,started_at FROM observation_registration").fetchone()
        if registered != hashlib.sha256(json.dumps(watchlist, sort_keys=True).encode()).hexdigest():
            raise ValueError("Watchlist differs from the registration.")
        now = instant(clock())
        if now is None:
            raise ValueError("Collector requires an aware clock.")
        count = len(watchlist)
        read = {(ticker, day): status for ticker, day, status in db.execute(
            "SELECT ticker, session, status FROM observations WHERE stage='close' AND observed_at<=?", (now.isoformat(),))}
        monitoring = {(market, day): reason for market, day, reason in db.execute(
            "SELECT market, session, reason FROM monitor_days WHERE checked_at<=?", (now.isoformat(),))}
    markets = {}
    for market in sorted({item["market"] for item in watchlist}):
        days = list(_sessions(market, instant(since), now))
        tickers = [item["ticker"] for item in watchlist if item["market"] == market]
        markets[market] = {"completed_sessions": len(days),
            "observation_slots": len(days) * len(tickers),
            "observed_market_only": sum((ticker, day) in read for day, _, _ in days for ticker in tickers),
            "qualification": "TRADING_EVIDENCE_UNVERIFIED"}
    return {"observed_at": now.isoformat(), "markets": markets, "watchlist_size": count,
            "monitoring_reasons": [{"market": market, "session": day, "reason": reason}
                                   for (market, day), reason in sorted(monitoring.items())],
            "scope": "MARKET_DATA_ONLY", "eligible_for_promotion": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Dedicated private directory with policy.json.")
    parser.add_argument("--status", action="store_true", help="Show completed sessions and observation coverage.")
    parser.add_argument("--operations-state", type=Path, help="Optional read-only paper strategy settings for monitoring reasons.")
    args = parser.parse_args(argv)
    result = observation_status(args.root) if args.status else {
        "scope": "MARKET_DATA_ONLY", "observations": capture_due(args.root, operations=args.operations_state),
        "broker_orders_sent": 0}
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
