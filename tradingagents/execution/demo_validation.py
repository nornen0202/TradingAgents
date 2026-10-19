"""Finite, restart-safe VTS session validation; never a strategy or live broker.

Two one-share buys per market are the entire campaign budget. Acknowledgement,
cumulative fill observation and confirmed cancellation remain separate evidence.
Minute invocations advance existing requests before considering a new request.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_DOWN, ROUND_UP
import json
import math
from pathlib import Path
import re
import sqlite3
from zoneinfo import ZoneInfo

from tradingagents.atomic_io import atomic_write_json, interprocess_file_lock
from tradingagents.charting.bars import instant
from tradingagents.charting.capture import normalize_kis_bars
from tradingagents.execution.kis_demo import DemoCredentials, KisDemoClient
from tradingagents.execution.kis_paper import KisPaperBroker, PaperOrderPolicy, read_paper_account
from tradingagents.execution.paper_runtime import _runtime_session
from tradingagents.execution.paper_quotes import normalized_orderbook


SCHEMA = "tradingagents.kis-session-validation/v1"
CAMPAIGN = "regular-session-validation-v1"
MARKETS = {
    "KR": {"ticker": "069500", "currency": "KRW", "cap": 100_000, "zone": "Asia/Seoul"},
    "US": {"ticker": "AAPL", "exchange": "NASD", "currency": "USD", "cap": 500, "zone": "America/New_York"},
}
STAGES = ("submitted", "filled", "cancelled")
BLOCKERS = {
    "MARKET_CLOSED", "CALENDAR_UNVERIFIED", "SESSION_EDGE", "HALTED", "EVIDENCE_UNAVAILABLE",
    "AMBIGUOUS_ORDER", "AMBIGUOUS_CANCELLATION", "ORDER_REJECTED", "ORDER_NOT_SENT",
    "CAMPAIGN_BUDGET_EXHAUSTED", "CANCELLATION_RACE", "FILL_NOT_OBSERVED", "STATE_INVALID",
    "JOURNAL_RECOVERY_REQUIRED", "DAY_ORDER_REQUIRES_REVIEW", "CANCELLATION_REJECTED",
    "ORDER_REPORT_UNVERIFIED", "CANCELLATION_NOT_CONFIRMED", "",
}


def _at(value):
    result = instant(value)
    if result is None:
        raise ValueError("Aware observation clock required")
    return result


def _read(path, default):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return default


def _new(market, now):
    return {"campaign_id": CAMPAIGN, "market": market, "configuration": MARKETS[market],
            "status": "WAITING_SESSION", "blocker": "MARKET_CLOSED", "checked_at": now.isoformat(),
            "stages": {name: {"verified": False} for name in STAGES}, "orders": [], "finished": False}


def _valid_state(value, market, now):
    if (not isinstance(value, dict) or value.get("campaign_id") != CAMPAIGN
            or value.get("market") != market or value.get("configuration") != MARKETS[market]
            or type(value.get("finished")) is not bool or _at(value.get("checked_at")) > now
            or value.get("status") not in {"WAITING_SESSION", "RUNNING", "VERIFIED", "BLOCKED", "ATTENTION"}
            or value.get("blocker") not in BLOCKERS or not isinstance(value.get("orders"), list)
            or len(value["orders"]) > 2):
        raise ValueError("Campaign state invalid")
    for name in STAGES:
        stage = value.get("stages", {}).get(name)
        if not isinstance(stage, dict) or type(stage.get("verified")) is not bool:
            raise ValueError("Stage invalid")
        if stage["verified"]:
            expected_source = "KIS_DEMO_BROKER_ACK" if name == "submitted" else "KIS_DEMO_BROKER_REPORT"
            if not _at(stage.get("observed_at")) <= _at(value["checked_at"]) or stage.get("source") != expected_source:
                raise ValueError("Stage clock or source invalid")
    if value["status"] == "VERIFIED" and (value["finished"] is not True or not all(value["stages"][name]["verified"] for name in STAGES)):
        raise ValueError("Completion evidence missing")
    if value["finished"] and value["status"] not in {"VERIFIED", "ATTENTION"}:
        raise ValueError("Finished campaign has an inconsistent status")
    for number, order in enumerate(value["orders"], start=1):
        if (not isinstance(order, dict) or order.get("intent_id") != f"{CAMPAIGN}:{market}:{number}"
                or order.get("purpose") not in {"cancel", "fill"}
                or not _at(order.get("prepared_at")) <= _at(value["checked_at"])
                or type(order.get("done")) is not bool or type(order.get("cancel_attempted")) is not bool
                or not isinstance(order.get("terms"), dict)):
            raise ValueError("Order state invalid")
        terms = order["terms"]
        expected = {"ticker", "side", "quantity", "limit_price"} | ({"exchange"} if market == "US" else set())
        if (set(terms) != expected or terms.get("ticker") != MARKETS[market]["ticker"]
                or terms.get("side") != "BUY" or type(terms.get("quantity")) is not int or terms["quantity"] != 1
                or (market == "US" and terms.get("exchange") != "NASD")
                or not 0 < _number(terms.get("limit_price")) <= MARKETS[market]["cap"]):
            raise ValueError("Immutable campaign terms invalid")
    return value


def _number(value):
    if isinstance(value, bool):
        raise ValueError("Invalid price")
    try:
        result = float(value)
    except (TypeError, ValueError):
        raise ValueError("Invalid price") from None
    if not math.isfinite(result) or result <= 0:
        raise ValueError("Invalid price")
    return result


def _journal_evidence(state, path):
    """A status JSON claim is never sufficient proof of a genuine broker step.

    Read-only checks also apply to finished campaigns and offline status views.
    The immutable request terms and cumulative observations must support every
    asserted proof and every completed-order flag; missing history fails closed.
    """
    if not any(stage["verified"] for stage in state["stages"].values()) and not any(order["done"] for order in state["orders"]):
        return
    if not Path(path).is_file():
        raise ValueError("Persistent VTS evidence missing")
    db = sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    supported = {name: False for name in STAGES}
    try:
        for order in state["orders"]:
            identity = order["intent_id"]
            request = db.execute("SELECT status,response,created_at FROM requests WHERE id=?", (identity,)).fetchone()
            original = db.execute("SELECT terms FROM paper_intents WHERE id=?", (identity,)).fetchone()
            row = db.execute("SELECT status,filled,remaining FROM order_state WHERE id=?", (identity,)).fetchone()
            if not request or not original or json.loads(original["terms"]) != order["terms"]:
                raise ValueError("Immutable request evidence missing")
            response = json.loads(request["response"])
            ack = request["status"] == "ACKNOWLEDGED" and isinstance(response.get("broker_order_id"), str) and bool(response["broker_order_id"])
            if ack and state["stages"]["submitted"]["verified"] and _at(request["created_at"]) <= _at(state["stages"]["submitted"]["observed_at"]):
                supported["submitted"] = True
            if order["done"] and request["status"] not in {"NOT_SENT", "REJECTED"} and (not row or row["status"] not in {"FILLED", "CANCELLED"}):
                raise ValueError("Completed intent lacks terminal broker evidence")
            if not ack or not row:
                continue
            for name, status, quantity in (("filled", "FILLED", 1), ("cancelled", "CANCELLED", 0)):
                stage = state["stages"][name]
                if not stage["verified"] or row["status"] != status or row["filled"] != quantity or row["remaining"] != 0:
                    continue
                if name == "cancelled":
                    cancellation = db.execute("SELECT status FROM requests WHERE id=?", ("cancel:" + identity,)).fetchone()
                    if not cancellation or cancellation["status"] != "ACKNOWLEDGED":
                        continue
                for observed in db.execute("SELECT observed_at,evidence FROM paper_observations WHERE id=?", (identity,)):
                    evidence = json.loads(observed["evidence"])
                    if (_at(request["created_at"]) <= _at(observed["observed_at"]) <= _at(stage["observed_at"])
                            and evidence.get("status") == status and type(evidence.get("filled_qty")) is int
                            and evidence["filled_qty"] == quantity and type(evidence.get("remaining_qty")) is int
                            and evidence["remaining_qty"] == 0):
                        supported[name] = True
        if any(state["stages"][name]["verified"] and not supported[name] for name in STAGES):
            raise ValueError("Claimed stage lacks persistent broker evidence")
        if state["status"] == "VERIFIED" and (len(state["orders"]) != 2 or not all(order["done"] for order in state["orders"])):
            raise ValueError("Campaign completion requires both terminal probes")
    finally:
        db.close()


def normalize_validation_quote(*, market, chart, orderbook, observed_at, instrument=None):
    """Use dated completed bars and dated books; USD validation needs no FX."""
    config, now = instrument or MARKETS[market], _at(observed_at)
    zone = ZoneInfo(config["zone"])
    for payload in (chart,) if market == "KR" else (chart, orderbook):
        if not isinstance(payload, dict) or str(payload.get("rt_cd")) != "0":
            raise ValueError("Invalid broker response")
    rows = chart.get("output2")
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError("Dated bars required")
    bars = normalize_kis_bars(rows, observed_at=now, timezone_name=config["zone"])
    bars = [row for row in bars if _at(row["available_at"]).astimezone(zone).date() == now.astimezone(zone).date()]
    if not bars:
        raise ValueError("Dated completed price required")
    bar = max(bars, key=lambda row: _at(row["available_at"]))
    price_at = _at(bar["available_at"])
    if not 0 <= (now - price_at).total_seconds() <= 120:
        raise ValueError("Stale price")
    result = {"ticker": config["ticker"], "provider": "kis", "currency": config["currency"],
              "session": "regular", "execution_ready": True, "instrument_type": config.get("instrument_type", "ETF" if market == "KR" else "STOCK"),
              "last_price": _number(bar["close"]), "observed_at": price_at.isoformat(),
              "ingested_at": now.isoformat(), "price_basis": "DATED_COMPLETED_BAR"}
    book = normalized_orderbook(orderbook, market.lower()) if isinstance(orderbook, dict) else None
    day = (book.get("dymd") or book.get("stck_bsop_date")) if isinstance(book, dict) else None
    if market == "KR" and not day:
        # A time-only book is not evidence for any date. The independently dated
        # completed bar supplies the limit anchor; no bid/ask/date is invented.
        result["quote_basis"] = "BAR_ONLY"
        return result
    if not isinstance(book, dict):
        raise ValueError("Book required")
    if any(str(book[key]).strip().upper() != config["ticker"] for key in ("code", "symbol", "pdno", "stck_shrn_iscd")
           if book.get(key) not in (None, "")):
        raise ValueError("Book identity mismatch")
    bid = _number(next((book[k] for k in ("bidp1", "pbid1", "PBID", "bid") if k in book), None))
    ask = _number(next((book[k] for k in ("askp1", "pask1", "PASK", "ask") if k in book), None))
    if ask < bid or (ask - bid) / ((ask + bid) / 2) * 10000 > 100:
        raise ValueError("Unusable spread")
    raw_time = book.get("dhms") or book.get("aspr_acpt_hour") or book.get("bsop_hour")
    if market == "US" and not day:
        raise ValueError("Explicit US book date required")
    raw = str(day or "") + str(raw_time or "")
    if not re.fullmatch(r"[0-9]{14}", raw):
        raise ValueError("Book date/time required")
    from .paper_quotes import KIS_ORDERBOOK_ZONE
    book_at = datetime.strptime(raw, "%Y%m%d%H%M%S").replace(tzinfo=KIS_ORDERBOOK_ZONE)
    if not 0 <= (now - book_at).total_seconds() <= 120:
        raise ValueError("Book future or stale")
    result.update(bid=bid, ask=ask, observed_at=min(price_at, book_at).isoformat(),
                  quote_basis="DATED_BOOK", orderbook_date_basis="EXPLICIT")
    if market == "US":
        result["exchange"] = config["exchange"]
    return result


def current_quote(market, clock):
    # This client has read-only endpoints. No real account is queried for sizing.
    from tradingagents.portfolio.kis import KisClient
    client = KisClient.from_api_keys(environment="real")
    try:
        if market == "KR":
            chart = client.domestic_time_itemchartprice("069500", input_hour=clock().astimezone(ZoneInfo("Asia/Seoul")).strftime("%H%M%S"), include_past_data="N")
            book = client.domestic_asking_price("069500")
        else:
            payload = client.overseas_time_itemchartprice("AAPL", exchange="NAS", nmin="1", include_previous="0")
            chart = payload[0] if isinstance(payload, tuple) else payload
            book = client.overseas_asking_price("AAPL", exchange="NAS")
        return normalize_validation_quote(market=market, chart=chart, orderbook=book, observed_at=clock())
    finally:
        client.session.close()


@contextmanager
def broker_context(market, path, clock):
    from tradingagents.execution.demo_token_cache import cache_demo_authentication
    client = broker = None
    try:
        if market == "KR":
            client = KisDemoClient(DemoCredentials.from_local_settings(), utcnow=clock)
            cache_demo_authentication(client, market=market)
            broker = KisPaperBroker(path, client, PaperOrderPolicy(("069500",), max_order_krw=100_000,
                max_daily_buy_krw=200_000, max_daily_orders=2), paper_enabled=True, clock=clock)
        else:
            from tradingagents.execution.kis_demo_us import KisDemoUSClient, credentials_from_settings
            from tradingagents.execution.kis_paper_us import KisPaperUSBroker, USPaperOrderPolicy
            client = KisDemoUSClient(credentials_from_settings(), utcnow=clock)
            cache_demo_authentication(client, market=market)
            broker = KisPaperUSBroker(path, client, USPaperOrderPolicy(allowed_instruments=(("AAPL", "NASD"),),
                max_order_usd=500, max_daily_buy_usd=1000, max_daily_orders=2), paper_enabled=True, clock=clock)
        yield broker
    finally:
        if broker:
            broker.close()
        if client:
            client.close()


def current_account(market, broker, terms, clock):
    args = {key: terms[key] for key in ("ticker", "limit_price")}
    if market == "KR":
        return read_paper_account(broker.client, **args, clock=clock)
    from tradingagents.execution.kis_paper_us import read_paper_us_account
    return read_paper_us_account(broker.client, **args, exchange=terms["exchange"], clock=clock)


def _prove(state, name, now):
    state["stages"][name] = {"verified": True, "observed_at": now.isoformat(),
        "source": "KIS_DEMO_BROKER_ACK" if name == "submitted" else "KIS_DEMO_BROKER_REPORT"}


def _request(broker, intent_id):
    row = broker.db.execute("SELECT status FROM requests WHERE id=?", (intent_id,)).fetchone()
    return row["status"] if row else None


def _terms(market, quote, purpose):
    tick = Decimal("5") if market == "KR" else Decimal(".01")
    anchor = quote.get("ask", quote["last_price"] + float(tick)) if purpose == "fill" else min(quote.get("bid", quote["last_price"]), quote["last_price"] * .992)
    price = Decimal(str(anchor))
    price = (price / tick).to_integral_value(rounding=ROUND_UP if purpose == "fill" else ROUND_DOWN) * tick
    result = {"ticker": MARKETS[market]["ticker"], "side": "BUY", "quantity": 1,
              "limit_price": int(price) if market == "KR" else float(price)}
    if not 0 < result["limit_price"] <= MARKETS[market]["cap"]:
        raise ValueError("Price outside campaign cap")
    if market == "US":
        result["exchange"] = "NASD"
    return result


def _advance(state, *, market, now, clock, broker, persist, quote_loader, account_loader, session, halted):
    def finish(status, blocker="", final=False):
        state.update(status=status, blocker=blocker, finished=final)

    active = next((order for order in state["orders"] if not order["done"]), None)
    # Unknown pre-existing requests cannot disappear by deleting campaign JSON.
    expected = {order["intent_id"] for order in state["orders"]}
    existing = {row[0] for row in broker.db.execute("SELECT id FROM requests WHERE id NOT LIKE 'cancel:%'")}
    writes = {row[0] for row in broker.db.execute("SELECT id FROM requests")}
    if not existing.issubset(expected) or not writes.issubset(expected | {"cancel:" + item for item in expected}) or len(writes) > 4:
        return finish("ATTENTION", "JOURNAL_RECOVERY_REQUIRED", True)
    if active:
        identity = active["intent_id"]
        request_status = _request(broker, identity)
        if request_status is None:
            return finish("ATTENTION", "JOURNAL_RECOVERY_REQUIRED", True)
        if request_status in {"UNKNOWN", "UNRESOLVED"}:
            return finish("ATTENTION", "AMBIGUOUS_ORDER", True)
        if request_status in {"NOT_SENT", "REJECTED"}:
            active["done"] = True
            return finish("ATTENTION", "ORDER_NOT_SENT" if request_status == "NOT_SENT" else "ORDER_REJECTED", True)
        if request_status != "ACKNOWLEDGED":
            raise ValueError("Unknown journal status")
        _prove(state, "submitted", _at(clock()))
        report = broker.reconcile(intent_id=identity)
        observed = _at(clock())
        status, filled, remaining = report.get("status"), report.get("filled_qty"), report.get("remaining_qty")
        if status == "FILLED" and type(filled) is int and filled == 1 and type(remaining) is int and remaining == 0:
            _prove(state, "filled", observed)
            active["done"] = True
            if active["purpose"] == "cancel" and not state["stages"]["cancelled"]["verified"]:
                # Never chase a cancellation race with additional orders.
                return finish("ATTENTION", "CANCELLATION_RACE", True)
        elif status == "CANCELLED" and type(remaining) is int and remaining == 0 and type(filled) is int and filled == 0:
            if _request(broker, "cancel:" + identity) != "ACKNOWLEDGED":
                return finish("ATTENTION", "CANCELLATION_NOT_CONFIRMED", True)
            _prove(state, "cancelled", observed)
            active["done"] = True
            if active["purpose"] == "fill":
                return finish("ATTENTION", "FILL_NOT_OBSERVED", True)
        elif status in {"OPEN", "PARTIAL"} and type(remaining) is int and remaining > 0:
            zone = ZoneInfo(MARKETS[market]["zone"])
            if _at(active["prepared_at"]).astimezone(zone).date() != observed.astimezone(zone).date():
                return finish("ATTENTION", "DAY_ORDER_REQUIRES_REVIEW", True)
            cancel_status = _request(broker, "cancel:" + identity)
            if cancel_status in {"UNKNOWN", "UNRESOLVED"}:
                return finish("ATTENTION", "AMBIGUOUS_CANCELLATION")
            if cancel_status in {"REJECTED", "NOT_SENT"}:
                return finish("ATTENTION", "CANCELLATION_REJECTED", True)
            expired = (observed - _at(active["prepared_at"])).total_seconds() >= 300
            should_cancel = active["purpose"] == "cancel" or expired or halted or _at(session["session_close"]) - observed < timedelta(minutes=5)
            if should_cancel and not active["cancel_attempted"]:
                active["cancel_attempted"] = True
                persist()  # Crash before/after cancel cannot cause a second POST.
                response = broker.cancel(intent_id=identity)
                if response.get("status") == "UNKNOWN":
                    return finish("ATTENTION", "AMBIGUOUS_CANCELLATION")
            elif should_cancel and not cancel_status:
                return finish("ATTENTION", "JOURNAL_RECOVERY_REQUIRED", True)
            return finish("RUNNING")
        else:
            return finish("ATTENTION", "ORDER_REPORT_UNVERIFIED")
        if all(state["stages"][name]["verified"] for name in STAGES):
            return finish("VERIFIED", final=True)
        return finish("RUNNING")  # One submission/reconciliation step per tick.

    if halted:
        return finish("BLOCKED", "HALTED")
    if len(state["orders"]) >= 2:
        return finish("ATTENTION", "CAMPAIGN_BUDGET_EXHAUSTED", True)
    if now - _at(session["session_open"]) < timedelta(minutes=2) or _at(session["session_close"]) - now < timedelta(minutes=10):
        return finish("WAITING_SESSION", "SESSION_EDGE")
    purpose = "fill" if state["stages"]["cancelled"]["verified"] else "cancel"
    quote = quote_loader(market, clock)
    terms = _terms(market, quote, purpose)
    account = account_loader(market, broker, terms, clock)
    prepared = _at(clock())
    identity = f"{CAMPAIGN}:{market}:{len(state['orders']) + 1}"
    order = {"intent_id": identity, "purpose": purpose, "prepared_at": prepared.isoformat(),
             "terms": terms, "done": False, "cancel_attempted": False}
    state["orders"].append(order)
    finish("RUNNING")
    persist()  # Immutable identity and terms precede the transport journal.
    # Explicit connectivity test authorization, kept out of strategy archives.
    signal = {"signal_id": identity, "ticker": terms["ticker"], "decision_now": "STARTER_NOW",
              "execution_ready": True, "available_at": prepared.isoformat(),
              "valid_until": min(prepared + timedelta(seconds=90), _at(session["session_close"])).isoformat(),
              "purpose": "USER_AUTHORIZED_VTS_CONNECTIVITY_VALIDATION"}
    response = broker.submit(intent_id=identity, **terms, signal=signal, quote=quote, account=account)
    if response.get("status") == "ACKNOWLEDGED":
        _prove(state, "submitted", _at(clock()))
    elif response.get("status") == "UNKNOWN":
        finish("ATTENTION", "AMBIGUOUS_ORDER", True)
    elif response.get("status") in {"REJECTED", "NOT_SENT"}:
        order["done"] = True
        finish("ATTENTION", "ORDER_REJECTED" if response["status"] == "REJECTED" else "ORDER_NOT_SENT", True)
    else:
        finish("ATTENTION", "ORDER_REPORT_UNVERIFIED", True)


def local_paper_health(archive, now):
    try:
        receipt = _read(Path(archive) / "paper/status.json", {})
        checked = _at(receipt.get("checked_at"))
        if (receipt.get("mode") != "LOCAL_PAPER_ONLY" or receipt.get("enabled") is not True
                or receipt.get("real_orders_enabled") is not False
                or type(receipt.get("broker_orders_sent")) is not int or receipt["broker_orders_sent"] != 0
                or not 0 <= (now - checked).total_seconds() <= 180):
            return {"status": "UNVERIFIED"}
        result = {"status": "RECENT_TICK_CONFIRMED", "checked_at": checked.isoformat(), "markets": {}}
        for market in ("kr", "us"):
            row = receipt.get("markets", {}).get(market, {})
            if (not isinstance(row, dict) or not 0 <= (checked - _at(row.get("checked_at"))).total_seconds() <= 180
                    or row.get("real_orders_enabled") is not False or type(row.get("broker_orders_sent")) is not int
                    or row["broker_orders_sent"] != 0):
                return {"status": "UNVERIFIED"}
            status = row.get("status")
            allowed = {"ACTIVE", "VALUATION_ONLY", "MARKET_CLOSED", "BLOCKED", "WAITING_SOURCE", "ERROR"}
            projected = {"status": status if status in allowed else "UNVERIFIED", "checked_at": row["checked_at"]}
            counts = row.get("order_counts", {})
            if isinstance(counts, dict) and all(type(counts.get(key, 0)) is int and counts.get(key, 0) >= 0 for key in ("PENDING", "FILLED", "REJECTED", "CANCELLED")):
                projected["order_counts"] = {key: counts.get(key, 0) for key in ("PENDING", "FILLED", "REJECTED", "CANCELLED")}
            for key in ("last_observation_at", "last_fill_at"):
                if row.get(key) is not None and _at(row[key]) <= _at(row["checked_at"]):
                    projected[key] = row[key]
            result["markets"][market.upper()] = projected
        return result
    except (ValueError, TypeError, AttributeError, OSError):
        return {"status": "UNVERIFIED"}


def run_campaign(archive, state_root, *, run=False, clock=None, broker_factory=None,
                 quote_loader=None, account_loader=None, session_resolver=None):
    """At most one bounded step per market; default performs no network access."""
    if type(run) is not bool:
        raise ValueError("Explicit boolean run flag required")
    archive, root = Path(archive), Path(state_root)
    clock = clock or (lambda: datetime.now(timezone.utc))
    broker_factory, quote_loader = broker_factory or broker_context, quote_loader or current_quote
    account_loader, session_resolver = account_loader or current_account, session_resolver or _runtime_session
    with interprocess_file_lock(root / "campaign.lock", timeout=0):
        results = {}
        for market in MARKETS:
            now = _at(clock())
            path = root / f"{market.lower()}-campaign.json"
            state = _new(market, now)
            valid = False
            try:
                state = _valid_state(_read(path, state), market, now)
                _journal_evidence(state, root / f"{market.lower()}-vts.sqlite")
                valid = True
                if run and not state["finished"]:
                    session = session_resolver(market=market, now_local=now)
                    if session.get("source") != "exchange_calendars":
                        state.update(status="BLOCKED", blocker="CALENDAR_UNVERIFIED")
                    elif session.get("is_open") is not True or session.get("phase") != "regular":
                        state.update(status="WAITING_SESSION", blocker="MARKET_CLOSED")
                    elif not _at(session.get("session_open")) <= now < _at(session.get("session_close")):
                        state.update(status="BLOCKED", blocker="CALENDAR_UNVERIFIED")
                    else:
                        def persist():
                            state["checked_at"] = _at(clock()).isoformat()
                            atomic_write_json(path, state)
                        with broker_factory(market, root / f"{market.lower()}-vts.sqlite", clock) as broker:
                            _advance(state, market=market, now=now, clock=clock, broker=broker, persist=persist,
                                     quote_loader=quote_loader, account_loader=account_loader, session=session,
                                     halted=(root / "HALT").exists())
            except Exception:
                # Never serialize credentials, broker error bodies or paths.
                if valid:
                    state.update(status="BLOCKED", blocker="EVIDENCE_UNAVAILABLE")
                else:
                    # Corruption never silently resets the one-time campaign.
                    state = _new(market, now)
                    state.update(status="ATTENTION", blocker="STATE_INVALID", finished=True)
            completed = _at(clock())
            if completed < now:
                raise ValueError("Campaign completion clock regressed")
            state["checked_at"] = completed.isoformat()
            if run:
                atomic_write_json(path, state)
            results[market] = {key: state[key] for key in ("status", "blocker", "checked_at", "stages")}
        completed = _at(clock())
        if any(completed < _at(row["checked_at"]) for row in results.values()):
            raise ValueError("Receipt clock precedes market observations")
        receipt = {"schema": SCHEMA, "mode": "KIS_DEMO", "checked_at": completed.isoformat(),
                   "live_orders_enabled": False, "markets": results,
                   "local_paper": local_paper_health(archive, completed)}
        atomic_write_json(archive / "paper/kis-session-validation.json", receipt)
        return receipt
