"""Explicitly authorized, finite one-share BUY then SELL on KIS VTS only.

This is separate from strategy results and the historical connectivity campaign.
Only a cumulative broker fill report completes a leg. Persistent preparation and
the existing request journal prevent restart duplicates and ambiguous retries.
"""
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_DOWN, ROUND_UP
import json
from pathlib import Path
import re
import sqlite3

from tradingagents.atomic_io import atomic_write_json, interprocess_file_lock
from tradingagents.execution import demo_validation as dv


MODE = "KIS_DEMO_ROUNDTRIP"


def _valid_terms(terms, market, side):
    expected = {"ticker", "side", "quantity", "limit_price"} | ({"exchange"} if market == "US" else set())
    if (set(terms) != expected or terms["ticker"] != dv.MARKETS[market]["ticker"]
            or terms["side"] != side or type(terms["quantity"]) is not int or terms["quantity"] != 1
            or (market == "US" and terms["exchange"] != "NASD")
            or not 0 < dv._number(terms["limit_price"]) <= dv.MARKETS[market]["cap"]):
        raise ValueError("INVALID_ROUNDTRIP_TERMS")


def _completed(path, market, config, now):
    """Prove terminal fills from immutable broker journals, even after closing."""
    if not path.is_file():
        return None
    db = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    try:
        authorization = db.execute("SELECT value FROM roundtrip_control WHERE key='authorization'").fetchone()
        if not authorization or json.loads(authorization[0]) != config:
            raise ValueError("AUTHORIZATION_CHANGED")
        identities = {f"{config['campaign_id']}:{market}:{side}" for side in ("BUY", "SELL")}
        if any(row[0] not in identities for row in db.execute("SELECT id FROM paper_intents")):
            raise ValueError("UNEXPECTED_INTENT")
        legs = []
        for side in ("BUY", "SELL"):
            identity = f"{config['campaign_id']}:{market}:{side}"
            state = db.execute("SELECT status,filled,remaining FROM order_state WHERE id=?", (identity,)).fetchone()
            if not state or tuple(state) != ("FILLED", 1, 0):
                return None
            prepared = db.execute("SELECT value FROM roundtrip_control WHERE key=?", (identity,)).fetchone()
            intent = db.execute("SELECT terms FROM paper_intents WHERE id=?", (identity,)).fetchone()
            request = db.execute("SELECT status,response,created_at FROM requests WHERE id=?", (identity,)).fetchone()
            if not prepared or not intent or not request or request["status"] != "ACKNOWLEDGED":
                raise ValueError("FILL_WITHOUT_REQUEST_EVIDENCE")
            terms = json.loads(intent[0])
            _valid_terms(terms, market, side)
            preparation = json.loads(prepared[0])
            if (preparation["terms"] != terms or not json.loads(request["response"]).get("broker_order_id")
                    or not dv._at(config["authorized_at"]) <= dv._at(preparation["prepared_at"]) <= dv._at(request["created_at"]) <= now):
                raise ValueError("IMMUTABLE_TERMS_CONFLICT")
            proof = None
            for observation in db.execute("SELECT observed_at,evidence FROM paper_observations WHERE id=? ORDER BY observed_at", (identity,)):
                evidence = json.loads(observation["evidence"])
                if (dv._at(request["created_at"]) <= dv._at(observation["observed_at"]) <= now
                        and evidence.get("status") == "FILLED" and evidence.get("mode") == "demo"
                        and type(evidence.get("filled_qty")) is int and evidence["filled_qty"] == 1
                        and type(evidence.get("remaining_qty")) is int and evidence["remaining_qty"] == 0):
                    proof = {"side": side, "ticker": terms["ticker"], "quantity": 1, "status": "FILLED",
                             "filled_quantity": 1, "remaining_quantity": 0, "fill_notional": evidence.get("fill_notional"),
                             "observed_at": observation["observed_at"], "source": "KIS_DEMO_BROKER_REPORT"}
                    break
            if proof is None:
                raise ValueError("FILL_WITHOUT_OBSERVATION_EVIDENCE")
            if legs and dv._at(preparation["prepared_at"]) < dv._at(legs[0]["observed_at"]):
                raise ValueError("SELL_BEFORE_BUY_FILL")
            legs.append(proof)
        return {"status": "VERIFIED", "legs": legs, "strategy_performance": False}
    finally:
        db.close()


def _config(root, now):
    value = dv._read(root / "roundtrip-enabled.json", {})
    if value.get("enabled") is not True or value.get("mode") != MODE or value.get("real_orders_enabled") is not False:
        return None
    if (not re.fullmatch(r"[a-z0-9-]{1,50}", str(value.get("campaign_id", "")))
            or not dv._at(value.get("authorized_at")) <= now
            or not timedelta(0) < dv._at(value.get("expires_at")) - dv._at(value["authorized_at"]) <= timedelta(days=3)):
        raise ValueError("INVALID_OR_EXPIRED_AUTHORIZATION")
    return value


def _advance(market, root, config, clock, factory, quote_loader, account_loader, session_resolver):
    now = dv._at(clock())
    path = root / "roundtrips" / config["campaign_id"] / f"{market.lower()}.sqlite"
    completed = _completed(path, market, config, now)
    if completed:
        return completed
    if now >= dv._at(config["expires_at"]):
        return {"status": "ATTENTION", "blocker": "AUTHORIZATION_EXPIRED"}
    session = session_resolver(market=market, now_local=now)
    if session.get("source") != "exchange_calendars":
        return {"status": "BLOCKED", "blocker": "CALENDAR_UNVERIFIED"}
    if session.get("is_open") is not True or session.get("phase") != "regular":
        return {"status": "WAITING_SESSION", "blocker": "MARKET_CLOSED"}
    path.parent.mkdir(parents=True, exist_ok=True)
    with factory(market, path, clock) as broker:
        db = broker.db
        db.execute("CREATE TABLE IF NOT EXISTS roundtrip_control (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        authority = json.dumps(config, sort_keys=True)
        db.execute("INSERT OR IGNORE INTO roundtrip_control VALUES ('authorization',?)", (authority,))
        if db.execute("SELECT value FROM roundtrip_control WHERE key='authorization'").fetchone()[0] != authority:
            raise ValueError("AUTHORIZATION_CHANGED")
        legs = []
        ids = {side: f"{config['campaign_id']}:{market}:{side}" for side in ("BUY", "SELL")}
        if any(row[0] not in set(ids.values()) for row in db.execute("SELECT id FROM paper_intents")):
            raise ValueError("UNEXPECTED_INTENT")
        for side in ("BUY", "SELL"):
            identity = ids[side]
            prepared = db.execute("SELECT value FROM roundtrip_control WHERE key=?", (identity,)).fetchone()
            request = db.execute("SELECT status FROM requests WHERE id=?", (identity,)).fetchone()
            intent = db.execute("SELECT terms FROM paper_intents WHERE id=?", (identity,)).fetchone()
            if prepared and (not intent or not request):
                return {"status": "ATTENTION", "blocker": "PREPARED_WITHOUT_BROKER_REQUEST", "legs": legs}
            if request:
                if not prepared or not intent or json.loads(prepared[0])["terms"] != json.loads(intent[0]):
                    raise ValueError("IMMUTABLE_TERMS_CONFLICT")
                _valid_terms(json.loads(intent[0]), market, side)
                if request[0] != "ACKNOWLEDGED":
                    return {"status": "ATTENTION", "blocker": "ORDER_" + request[0], "legs": legs}
                report = broker.reconcile(intent_id=identity)
                leg = {"side": side, "ticker": dv.MARKETS[market]["ticker"], "quantity": 1,
                       "status": report.get("status"), "filled_quantity": report.get("filled_qty"),
                       "remaining_quantity": report.get("remaining_qty"),
                       "fill_notional": report.get("fill_notional"), "observed_at": dv._at(clock()).isoformat(),
                       "source": "KIS_DEMO_BROKER_REPORT"}
                legs.append(leg)
                if report.get("status") == "FILLED" and type(report.get("filled_qty")) is int and report["filled_qty"] == 1 and type(report.get("remaining_qty")) is int and report["remaining_qty"] == 0:
                    continue
                if report.get("status") in {"OPEN", "PARTIAL"}:
                    prepared_at = dv._at(json.loads(prepared[0])["prepared_at"])
                    if (dv._at(clock()) - prepared_at >= timedelta(minutes=5)
                            or (root / "HALT").exists()):
                        # Existing journal ensures cancellation POST is at most once.
                        if not db.execute("SELECT 1 FROM requests WHERE id=?", ("cancel:"+identity,)).fetchone():
                            broker.cancel(intent_id=identity)
                    return {"status": "RUNNING", "legs": legs}
                return {"status": "ATTENTION", "blocker": "ORDER_REPORT_" + str(report.get("status")), "legs": legs}
            if (root / "HALT").exists():
                return {"status": "BLOCKED", "blocker": "HALTED", "legs": legs}
            quote = quote_loader(market, clock)
            tick = Decimal("5") if market == "KR" else Decimal("0.01")
            anchor = quote.get("ask", quote["last_price"] + float(tick)) if side == "BUY" else quote.get("bid", quote["last_price"] - float(tick))
            price = (Decimal(str(anchor)) / tick).to_integral_value(rounding=ROUND_UP if side == "BUY" else ROUND_DOWN) * tick
            if not 0 < price <= dv.MARKETS[market]["cap"]:
                raise ValueError("PRICE_OUTSIDE_VALIDATION_CAP")
            terms = {"ticker": dv.MARKETS[market]["ticker"], "side": side, "quantity": 1,
                     "limit_price": int(price) if market == "KR" else float(price)}
            if market == "US":
                terms["exchange"] = dv.MARKETS[market]["exchange"]
            account = account_loader(market, broker, terms, clock)
            at = dv._at(clock())
            if (at - dv._at(session["session_open"]) < timedelta(minutes=2)
                    or dv._at(session["session_close"]) - at < timedelta(minutes=10)
                    or at >= dv._at(config["expires_at"]) or (root / "HALT").exists()):
                return {"status": "WAITING_SESSION", "blocker": "SESSION_EDGE_OR_HALT", "legs": legs}
            # SELL exists only after this campaign's one-share BUY was filled;
            # the broker independently checks current sellable long holdings.
            signal = {"signal_id": identity, "ticker": terms["ticker"],
                      "decision_now": "STARTER_NOW" if side == "BUY" else "EXIT_NOW",
                      "execution_ready": True, "available_at": at.isoformat(),
                      "valid_until": min(at+timedelta(seconds=60), dv._at(config["expires_at"])).isoformat(),
                      "purpose": "USER_AUTHORIZED_VTS_ROUNDTRIP_VALIDATION"}
            db.execute("INSERT INTO roundtrip_control VALUES (?,?)", (identity, json.dumps({"terms": terms, "prepared_at": at.isoformat()})))
            response = broker.submit(intent_id=identity, **terms, signal=signal, quote=quote, account=account)
            return {"status": "RUNNING" if response.get("status") == "ACKNOWLEDGED" else "ATTENTION",
                    "submitted_side": side, "submission_status": response.get("status"), "legs": legs}
        return _completed(path, market, config, dv._at(clock()))


def run_roundtrip(archive, state_root, *, clock=None, broker_factory=None, quote_loader=None,
                  account_loader=None, session_resolver=None):
    root = Path(state_root)
    clock = clock or (lambda: datetime.now(timezone.utc))
    now = dv._at(clock())
    config = _config(root, now)
    if config is None:
        return {"status": "DISABLED", "real_orders_enabled": False}
    # Share the existing validation/strategy lock for one account mutation lane.
    with interprocess_file_lock(root / "campaign.lock", timeout=0):
        markets = {}
        for market in dv.MARKETS:
            try:
                markets[market] = _advance(market, root, config, clock, broker_factory or dv.broker_context,
                    quote_loader or (lambda m, c: dv.current_quote(m, c, require_us_halt=True)), account_loader or dv.current_account,
                    session_resolver or dv._runtime_session)
            except Exception as exc:
                markets[market] = {"status": "BLOCKED", "blocker": "EVIDENCE_UNVERIFIED", "error_type": type(exc).__name__}
            markets[market]["checked_at"] = dv._at(clock()).isoformat()
        receipt = {"mode": MODE, "campaign_id": config["campaign_id"], "real_orders_enabled": False,
                   "checked_at": dv._at(clock()).isoformat(), "markets": markets}
        atomic_write_json(root / "roundtrip-status.json", receipt)
        atomic_write_json(Path(archive) / "paper/kis-roundtrip-validation.json", receipt)
        return receipt
