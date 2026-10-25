"""Continuous strategy execution on fixed KIS VTS hosts after proven validation.

No live broker routing, model call, fabricated signal or inferred settlement.
The existing strategy supplies direction; explicit allocation policy and the
demo account supply size/capacity. Validation probes and local shadow trades
are never strategy fills.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_DOWN, ROUND_UP
import hashlib
import heapq
import json
import math
from pathlib import Path
import sqlite3
import tomllib
from zoneinfo import ZoneInfo

from tradingagents.atomic_io import atomic_write_json, interprocess_file_lock
from . import demo_validation as validation
from .archive_paper import build_step
from .source_diagnostics import diagnose_source
from .source_handoff import await_completed_source
from . import demo_strategy_plan
from .kis_demo import DemoCredentials, KisDemoClient
from .kis_paper import KisPaperBroker, PaperOrderPolicy, _fresh, _tick
from .paper_runtime import _latest_source, _runtime_session
from .strategy_evaluation import evaluate_strategy_orders

SCHEMA = "tradingagents.kis-strategy-runtime/v1"
MODE = "KIS_DEMO_STRATEGY"
CAPS = {"KR": 100_000, "US": 500}
ZONES = {"KR": "Asia/Seoul", "US": "America/New_York"}
TERMINAL = {"FILLED", "CANCELLED", "REJECTED", "NOT_SENT", "BLOCKED"}
DECISIONS = {"STARTER_NOW": "BUY", "ADD_NOW": "BUY", "BUY_NOW": "BUY",
             "REDUCE_NOW": "SELL", "EXIT_NOW": "SELL", "TAKE_PROFIT_NOW": "SELL",
             "TRIM_NOW": "SELL", "STOP_LOSS_NOW": "SELL"}
at = validation._at


def read(path, default=None):
    return validation._read(path, default)


def universe():
    with (Path(__file__).resolve().parents[2] / "config/portfolio_profiles.toml").open("rb") as stream:
        profiles = tomllib.load(stream)["profiles"]
    return {market: tuple(sorted(profiles[f"{market.lower()}_kis_default"]["watch_tickers"])) for market in ZONES}


def validation_gate(root, market, now):
    """Validate original per-market proofs, journal and owner, not public JSON."""
    state = validation._valid_state(read(root / f"{market.lower()}-campaign.json"), market, now)
    validation._journal_evidence(state, root / f"{market.lower()}-vts.sqlite")
    if state["status"] != "VERIFIED" or state["finished"] is not True:
        raise ValueError("VALIDATION_REQUIRED")
    with sqlite3.connect((root / f"{market.lower()}-vts.sqlite").resolve().as_uri() + "?mode=ro", uri=True) as db:
        owners = db.execute("SELECT scope FROM owner").fetchall()
        if len(owners) != 1 or db.execute("SELECT 1 FROM requests WHERE status='UNKNOWN'").fetchone() or db.execute("SELECT 1 FROM reconciliation_issues").fetchone():
            raise ValueError("VALIDATION_REQUIRED")
    return owners[0][0]


@contextmanager
def broker_context(market, path, clock, tickers, scope):
    from .demo_token_cache import cache_demo_authentication
    client = broker = None
    try:
        if market == "KR":
            client = KisDemoClient(DemoCredentials.from_local_settings(), utcnow=clock)
        else:
            from .kis_demo_us import KisDemoUSClient, credentials_from_settings
            client = KisDemoUSClient(credentials_from_settings(), utcnow=clock)
        if scope != client.credentials.scope():
            raise ValueError("VALIDATED_ACCOUNT_CHANGED")
        cache_demo_authentication(client, market=market)
        if market == "KR":
            broker = KisPaperBroker(path, client, PaperOrderPolicy(tuple(t[:6] for t in tickers)), paper_enabled=True, clock=clock)
        else:
            from .kis_paper_us import KisPaperUSBroker, USPaperOrderPolicy
            broker = KisPaperUSBroker(path, client, USPaperOrderPolicy((), allowed_tickers=tickers), paper_enabled=True, clock=clock)
        yield broker
    finally:
        if broker:
            broker.close()
        if client:
            client.close()


def current_quote(market, ticker, clock):
    """Dated native-currency observations; a venue is resolved by its endpoint."""
    from tradingagents.portfolio.kis import KisClient
    client = KisClient.from_api_keys(environment="real")  # This class exposes reads only.
    code = ticker[:6] if market == "KR" else ticker
    config = {"ticker": code, "currency": "KRW" if market == "KR" else "USD", "zone": ZONES[market], "instrument_type": "STOCK"}
    try:
        if market == "KR":
            chart = client.domestic_time_itemchartprice(code, input_hour=clock().astimezone(ZoneInfo(ZONES[market])).strftime("%H%M%S"), include_past_data="N")
            return validation.normalize_validation_quote(market=market, chart=chart, orderbook=None, observed_at=clock(), instrument=config)
        for venue, exchange in (("NAS", "NASD"), ("NYS", "NYSE"), ("AMS", "AMEX")):
            payload = client.overseas_time_itemchartprice(code, exchange=venue, nmin="1", include_previous="0")
            chart = payload[0] if isinstance(payload, tuple) else payload
            if not isinstance(chart, dict) or not chart.get("output2"):
                continue
            book = client.overseas_asking_price(code, exchange=venue)
            quote = validation.normalize_validation_quote(market=market, chart=chart, orderbook=book, observed_at=clock(), instrument={**config, "exchange": exchange})
            return validation.attach_us_halt_evidence(quote, chart, ticker, clock)
        raise ValueError("QUOTE_UNVERIFIED")
    finally:
        client.session.close()


def candidates(source, market, now, tickers):
    """Consume actual completed strategy/proposal pairs with original clocks."""
    snapshot, step, selected = build_step(source, now.isoformat())
    if selected != market.lower():
        raise ValueError("SOURCE_MARKET_MISMATCH")
    proposals = read(source / "portfolio-private/proposed_orders.json")["orders"]
    rows, seen = [], set()
    for original in step["signals"]:
        ticker, decision = original["ticker"], original["signal_action"]
        if ticker not in tickers or decision not in DECISIONS or original["execution_ready"] is not True:
            continue
        available, expiry = at(original["available_at"]), at(original["valid_until"])
        if not available <= now < expiry or (now - available).total_seconds() >= 120:
            continue
        side = DECISIONS[decision]
        matches = [p for p in proposals if p.get("canonical_ticker") == ticker and str(p.get("side")).upper() == side]
        # An analysis exit/trim can be informational when no explicit order was
        # allocated. It must not block unrelated, explicitly proposed orders.
        if not matches:
            continue
        if len(matches) != 1 or (ticker, side) in seen:
            raise ValueError("AMBIGUOUS_STRATEGY_PROPOSAL")
        seen.add((ticker, side))
        proposal = matches[0]
        delta = proposal.get("delta_krw_now")
        if isinstance(delta, bool) or not isinstance(delta, (int, float)) or not math.isfinite(delta) or (delta <= 0 if side == "BUY" else delta >= 0):
            continue
        identity = "strategy-v1:" + market + ":" + hashlib.sha256(f"{source.name}|{ticker}|{side}".encode()).hexdigest()
        signal = {**original, "ticker": ticker[:6] if market == "KR" else ticker, "signal_id": identity,
                  "decision_now": {"BUY_NOW": "STARTER_NOW", "TAKE_PROFIT_NOW": "REDUCE_NOW",
                                   "TRIM_NOW": "REDUCE_NOW", "STOP_LOSS_NOW": "EXIT_NOW"}.get(decision, decision)}
        rows.append({"id": identity, "ticker": ticker, "side": side, "signal": signal, "proposal": proposal,
                     "fx": (snapshot.get("cash_diagnostics") or {}).get("fx_quote"), "run_id": source.name})
    # Reduce existing strategy risk before allocating cash to a new buy.
    return sorted(rows, key=lambda row: (row["side"] == "BUY", row["ticker"]))


def limit_price(quote, side, market):
    price = quote.get("ask" if side == "BUY" else "bid", quote["last_price"])
    tick = Decimal(str(_tick(int(price), quote["instrument_type"]))) if market == "KR" else Decimal(".01")
    value = (Decimal(str(price)) / tick).to_integral_value(rounding=ROUND_UP if side == "BUY" else ROUND_DOWN) * tick
    return int(value) if market == "KR" else float(value)


def quantity(candidate, price, account, market, owned, now):
    """Apply the selected allocation policy using verified demo capacity."""
    if candidate.get("allocation_mode") == demo_strategy_plan.MODE:
        _fresh(account, now=now, seconds=120)
        if account.get("complete") is not True or account.get("environment") != "demo":
            raise ValueError("STRATEGY_ACCOUNT_UNVERIFIED")
        suffix = "krw" if market == "KR" else "usd"
        if candidate["side"] == "BUY":
            permitted = (account["cash_only_buying_quantity"] >= 1
                         and account[f"cash_only_buying_power_{suffix}"] >= price * 1.003
                         and owned.get(candidate["ticker"], 0) == 0)
        else:
            position = next((p for p in account["positions"] if p["ticker"] == candidate["signal"]["ticker"]), {})
            permitted = owned.get(candidate["ticker"], 0) >= 1 and position.get("sellable_quantity", 0) >= 1
        if not permitted or price > CAPS[market]:
            raise ValueError("NO_STRATEGY_QUANTITY_WITHIN_LIMITS")
        return 1
    proposal = candidate["proposal"]
    qty = proposal.get("estimated_qty")
    if qty is not None and (isinstance(qty, bool) or not isinstance(qty, (int, float)) or not math.isfinite(qty) or qty <= 0 or int(qty) != qty):
        raise ValueError("PROPOSAL_QUANTITY_INVALID")
    budget = abs(proposal["delta_krw_now"])
    if market == "US" and qty is None:
        fx = candidate.get("fx") or {}
        if (fx.get("base_currency") != "USD" or fx.get("quote_currency") != "KRW"
                or fx.get("kind") != "BROKER_REFERENCE_RATE" or fx.get("source") != "kis.inquire_present_balance.output2.frst_bltn_exrt"
                or not 0 <= (now - at(fx.get("observed_at"))).total_seconds() <= 120):
            raise ValueError("BUDGET_FX_UNVERIFIED")
        budget /= validation._number(fx.get("rate"))
    planned = int(qty) if qty is not None else math.floor(budget / price)
    if market == "KR":
        planned = min(planned, math.floor(budget / price))
    result = min(planned, math.floor(CAPS[market] / price))
    if candidate["side"] == "BUY":
        suffix = "krw" if market == "KR" else "usd"
        result = min(result, account["cash_only_buying_quantity"], math.floor(account[f"cash_only_buying_power_{suffix}"] / (price * 1.003)))
    else:
        position = next((p for p in account["positions"] if p["ticker"] == candidate["signal"]["ticker"]), {})
        result = min(result, owned.get(candidate["ticker"], 0), position.get("sellable_quantity", 0))
    if type(result) is not int or result <= 0:
        raise ValueError("NO_STRATEGY_QUANTITY_WITHIN_LIMITS")
    return result


def initialize(db):
    db.execute("""CREATE TABLE IF NOT EXISTS strategy_attempts (
        id TEXT PRIMARY KEY, ticker TEXT NOT NULL, run_id TEXT NOT NULL,
        prepared_at TEXT NOT NULL, terms TEXT NOT NULL, state TEXT NOT NULL)""")
    db.execute("CREATE TABLE IF NOT EXISTS strategy_valuations(observed_at TEXT PRIMARY KEY, payload TEXT NOT NULL)")
    db.execute("CREATE TABLE IF NOT EXISTS strategy_source_evidence(id TEXT PRIMARY KEY, evidence TEXT NOT NULL)")
    db.executescript("""
        CREATE TRIGGER IF NOT EXISTS strategy_terms_no_update BEFORE UPDATE OF id,ticker,run_id,prepared_at,terms ON strategy_attempts
            BEGIN SELECT RAISE(ABORT,'Strategy intent terms are immutable'); END;
        CREATE TRIGGER IF NOT EXISTS strategy_attempts_no_delete BEFORE DELETE ON strategy_attempts
            BEGIN SELECT RAISE(ABORT,'Strategy consumption cannot be reset'); END;
        CREATE TRIGGER IF NOT EXISTS strategy_source_no_update BEFORE UPDATE ON strategy_source_evidence
            BEGIN SELECT RAISE(ABORT,'Strategy source evidence is immutable'); END;
        CREATE TRIGGER IF NOT EXISTS strategy_source_no_delete BEFORE DELETE ON strategy_source_evidence
            BEGIN SELECT RAISE(ABORT,'Strategy source evidence cannot be reset'); END;
    """)


def verify_owned(account, owned, market, scope, now):
    """A reset/manual reduction must not leave fictional strategy holdings."""
    _fresh(account, now=now, seconds=120)
    if account.get("complete") is not True or account.get("environment") != "demo" or account.get("account_scope") != scope:
        raise ValueError("STRATEGY_ACCOUNT_UNVERIFIED")
    positions = account.get("positions")
    if not isinstance(positions, list):
        raise ValueError("STRATEGY_ACCOUNT_UNVERIFIED")
    quantities = {}
    for position in positions:
        code, qty = position.get("ticker"), position.get("quantity")
        if not isinstance(code, str) or code in quantities or type(qty) is not int or qty < 0:
            raise ValueError("STRATEGY_ACCOUNT_UNVERIFIED")
        quantities[code] = qty
    if any(quantities.get(ticker[:6] if market == "KR" else ticker, 0) < qty for ticker, qty in owned.items()):
        raise ValueError("STRATEGY_ACCOUNT_POSITION_MISMATCH")


def _performance_history(db, now):
    """Return the latest 60 dated valuations available at this aware cutoff.

    Stream clock keys only. Future/undated rows do not consume the limit, and
    payloads are decoded only after selecting the bounded UTC-ordered window.
    This display projection never changes stored valuations or order evidence.
    """
    cutoff, selected = at(now), []
    for row in db.execute("SELECT observed_at FROM strategy_valuations"):
        try:
            observed = at(row[0])
        except (TypeError, ValueError):
            continue
        if observed <= cutoff:
            item = (observed, row[0])
            if len(selected) < 60:
                heapq.heappush(selected, item)
            else:
                heapq.heappushpop(selected, item)
    return [json.loads(db.execute("SELECT payload FROM strategy_valuations WHERE observed_at=?", (key,)).fetchone()[0])
            for _, key in sorted(selected)]


def summary(db, now, market, marks=None, *, historical=False):
    """Read cumulative observations once per intent; partial fills never double count.

    Latest report clocks remain freshness evidence. Availability refers to one
    verified report of the current consecutive quantity/notional state, never
    an earlier partial fill or a broker execution timestamp.

    ``historical`` is only for the read-only viewer's dated cost projection.
    Future/unavailable rows are excluded before their contents can affect it.
    The live runtime keeps the default strict whole-input rejection, and a
    mutable request status without a dated observation is never backdated.
    """
    marks = marks or {}
    orders, owned, buy, sell, complete = [], {}, 0.0, 0.0, True
    for row in db.execute("SELECT * FROM strategy_attempts ORDER BY prepared_at,id"):
        try:
            prepared = at(row["prepared_at"])
        except (ValueError, TypeError):
            if historical:
                continue
            raise
        if prepared > now:
            if historical:
                continue
            raise ValueError("FUTURE_STRATEGY_ATTEMPT")
        terms = json.loads(row["terms"])
        request = db.execute("SELECT status,response,created_at FROM requests WHERE id=?", (row["id"],)).fetchone()
        original = db.execute("SELECT terms,created_at FROM paper_intents WHERE id=?", (row["id"],)).fetchone()
        if historical:
            def visible(value):
                try:
                    return value is not None and at(value["created_at"]) <= now
                except (ValueError, TypeError):
                    return False
            request = request if visible(request) else None
            original = original if visible(original) else None
        if (request and not original) or (original and json.loads(original[0]) != terms):
            raise ValueError("STRATEGY_BROKER_TERMS_MISMATCH")
        # The legacy request table timestamps submission, not ACK availability.
        # A visible cumulative observation below witnesses its historical state.
        status = "UNKNOWN" if historical else request[0] if request else row["state"]
        evidence, observed, last_qty, last_amount, last_amount_qty = {}, None, 0, 0, 0
        economic_state, available_pair, first_fill = None, None, None
        observations = []
        for item in db.execute("SELECT observed_at,evidence FROM paper_observations WHERE id=?", (row["id"],)):
            if not historical:
                observations.append((at(item[0]), json.loads(item[1])))
                continue
            try:
                observation_at = at(item[0])
                if observation_at > now:
                    continue
                current = json.loads(item[1])
                if not isinstance(current, dict) or at(current.get("ingested_at")) > now:
                    continue
            except (ValueError, TypeError):
                # No usable availability clock means no historical evidence.
                # Immutable settlement bindings still reject a corrupted or
                # removed prefix that originally supported a known cost.
                continue
            observations.append((observation_at, current))
        observations.sort(key=lambda item: (item[0], at(item[1].get("ingested_at"))))
        for observed_at, current in observations:
            if not at(row["prepared_at"]) <= observed_at <= now:
                raise ValueError("INVALID_STRATEGY_OBSERVATION_CLOCK")
            ingested_at = at(current.get("ingested_at"))
            broker_id = json.loads(request["response"]).get("broker_order_id") if request else None
            if (not request or request["status"] != "ACKNOWLEDGED" or not broker_id
                    or current.get("broker_order_id") != broker_id or current.get("mode") != "demo"
                    or current.get("source", "KIS_DEMO_BROKER_REPORT") != "KIS_DEMO_BROKER_REPORT"
                    or current.get("live_orders_enabled") is True
                    or not at(row["prepared_at"]) <= at(request["created_at"]) <= observed_at
                    or observed_at != at(current.get("observed_at"))
                    or not observed_at <= ingested_at <= now):
                raise ValueError("INVALID_STRATEGY_OBSERVATION_PROOF")
            qty, amount = current.get("filled_qty"), current.get("fill_notional")
            if type(qty) is not int or qty < last_qty or qty > terms["quantity"]:
                raise ValueError("INVALID_STRATEGY_FILL")
            remaining, fill_status = current.get("remaining_qty"), current.get("status")
            if (type(remaining) is not int or not 0 <= remaining <= terms["quantity"] - qty
                    or fill_status not in {"OPEN", "PARTIAL", "FILLED", "CANCELLED", "UNRESOLVED"}
                    or (fill_status == "FILLED" and (qty != terms["quantity"] or remaining != 0))
                    or (fill_status == "CANCELLED" and remaining != 0)
                    or (fill_status == "OPEN" and (qty != 0 or remaining != terms["quantity"]))
                    or (fill_status == "PARTIAL" and (not 0 < qty < terms["quantity"] or remaining != terms["quantity"] - qty))):
                raise ValueError("INVALID_STRATEGY_FILL_STATE")
            if amount is not None and (isinstance(amount, bool) or not isinstance(amount, (int, float)) or not math.isfinite(amount)
                    or amount < 0 or (qty > 0 and amount == 0) or (qty == 0 and amount != 0)
                    or amount < last_amount or (qty == last_amount_qty and amount != last_amount)):
                raise ValueError("INVALID_STRATEGY_CASHFLOW")
            if amount is not None:
                last_amount, last_amount_qty = amount, qty
            state = (qty, None if amount is None else Decimal(str(amount)))
            if observed == observed_at and state != economic_state:
                raise ValueError("AMBIGUOUS_STRATEGY_OBSERVATION_STATE")
            if state != economic_state:
                # Reset even for known -> missing -> known: the later proof
                # cannot borrow availability across a different economic state.
                available_pair = (observed_at, ingested_at)
            elif ingested_at < available_pair[1]:
                available_pair = (observed_at, ingested_at)
            economic_state = state
            if qty and first_fill is None:
                first_fill = observed_at
            last_qty = qty
            evidence, observed = current, observed_at
        filled, amount = evidence.get("filled_qty", 0), evidence.get("fill_notional", 0 if not evidence else None)
        status = evidence.get("status", status)
        if status == "PREPARED":
            status = "UNKNOWN"
        owned[row["ticker"]] = owned.get(row["ticker"], 0) + filled * (1 if terms["side"] == "BUY" else -1)
        if filled and amount is None:
            complete = False
        elif terms["side"] == "BUY":
            buy += amount or 0
        else:
            sell += amount or 0
        cancellation = None if historical else db.execute("SELECT status FROM requests WHERE id=?", ("cancel:" + row["id"],)).fetchone()
        orders.append({"id": row["id"], "ticker": row["ticker"], "run_id": row["run_id"], "side": terms["side"],
            "quantity": terms["quantity"], "limit_price": terms["limit_price"], "filled_quantity": filled,
            "average_fill_price": amount / filled if filled and amount is not None else None,
            "fill_notional": amount, "mode": "demo", "strategy_performance": True,
            "source": "KIS_DEMO_BROKER_REPORT" if evidence else None,
            "status": status, "cancel_status": "CONFIRMED" if status == "CANCELLED" else cancellation[0] if cancellation else None,
            "prepared_at": row["prepared_at"], "observed_at": observed.isoformat() if observed else None,
            "ingested_at": evidence.get("ingested_at"),
            "first_fill_observed_at": first_fill.isoformat() if first_fill else None,
            "fill_availability": {"source": "KIS_DEMO_BROKER_REPORT", "filled_quantity": filled,
                                  "fill_notional": amount, "observed_at": available_pair[0].isoformat(),
                                  "ingested_at": available_pair[1].isoformat()} if available_pair else None})
    if any(qty < 0 for qty in owned.values()):
        raise ValueError("STRATEGY_HOLDINGS_NEGATIVE")
    value, mark_times = 0.0, []
    for ticker, qty in owned.items():
        if not qty:
            continue
        quote = marks.get(ticker)
        try:
            _fresh(quote or {}, now=now, seconds=120)
            if (quote.get("ticker") != (ticker[:6] if market == "KR" else ticker)
                    or quote.get("currency") != ("KRW" if market == "KR" else "USD")
                    or quote.get("provider") != "kis" or quote.get("session") != "regular"):
                raise ValueError("VALUATION_IDENTITY_UNVERIFIED")
            value += qty * validation._number(quote["last_price"])
            mark_times.append(quote["observed_at"])
        except Exception:
            complete = False
    counts = {key: sum(order["status"] == key for order in orders) for key in
              ("ACKNOWLEDGED", "OPEN", "PARTIAL", "FILLED", "CANCELLED", "REJECTED", "NOT_SENT", "BLOCKED", "UNKNOWN", "UNRESOLVED")}
    history = _performance_history(db, now)
    gross_pnl = round(sell - buy + value, 4) if complete and any(o["filled_quantity"] for o in orders) else None
    from .strategy_settlement import strategy_settlement_evidence
    settlements = strategy_settlement_evidence(db, orders, market=market, as_of=now.isoformat(), historical=historical)
    evaluation = evaluate_strategy_orders(orders, market=market, as_of=now.isoformat(), gross_pnl=gross_pnl,
                                          valuation_complete=complete, settlement_evidence=settlements)
    return {"orders": orders[-100:], "order_counts": counts, "owned": owned, "performance_history": history,
            "evaluation": evaluation,
            "performance": {"currency": "KRW" if market == "KR" else "USD", "basis": "STRATEGY_GROSS_CASHFLOWS_PLUS_MARKED_HOLDINGS",
                "status": "NO_FILLS" if not any(o["filled_quantity"] for o in orders) else "AVAILABLE" if complete else "INCOMPLETE",
                "gross_pnl": gross_pnl,
                "net_pnl": evaluation["net_pnl"], "actual_cost": evaluation["actual_cost"],
                "fees_known": evaluation["fees_known"], "settlement_known": evaluation["settlement_known"],
                "observed_at": now.isoformat(), "mark_times": mark_times}}


def advance(archive, root, validation_root, market, *, clock, tickers, broker_factory, quote_loader, account_loader, session_resolver, gate,
            allocation_mode="ARCHIVED_PROPOSALS"):
    now, path = at(clock()), root / f"{market.lower()}-strategy.sqlite"
    result = {"status": "WAITING_VALIDATION", "blockers": [], "gate_passed": False, "orders": [], "order_counts": {}, "performance": None}
    def finish(status, *blockers):
        result.update(status=status, blockers=list(blockers), checked_at=at(clock()).isoformat())
        if at(result["checked_at"]) < now:
            raise ValueError("RUNTIME_CLOCK_REGRESSED")
        return result
    try:
        scope = gate(validation_root, market, now)
        result["gate_passed"] = True
    except Exception:
        scope = None
    if path.exists():
        with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True) as db:
            db.row_factory = sqlite3.Row
            result.update(summary(db, now, market))
            if scope is None:
                scope = db.execute("SELECT scope FROM owner").fetchone()[0]
    if not result["gate_passed"] and not path.exists():
        return finish("WAITING_VALIDATION", "VALIDATION_REQUIRED")
    session = session_resolver(market=market, now_local=now)
    if session.get("source") != "exchange_calendars":
        return finish("BLOCKED", "CALENDAR_UNVERIFIED")
    if session.get("phase") in {None, "unknown"}:
        return finish("BLOCKED", "CALENDAR_UNVERIFIED")
    if session.get("is_open") is not True or session.get("phase") != "regular":
        return finish("MARKET_CLOSED", "MARKET_CLOSED")
    if not at(session["session_open"]) <= now < at(session["session_close"]):
        return finish("BLOCKED", "CALENDAR_UNVERIFIED")
    halted = (root / "HALT").exists() or (validation_root / "HALT").exists()
    near_close = at(session["session_close"]) - now <= timedelta(minutes=10)
    issues, marks = [], {}
    with broker_factory(market, path, clock, tickers, scope) as broker:
        initialize(broker.db)
        # Always reconcile/clean up outstanding requests before considering buys.
        for order in summary(broker.db, at(clock()), market)["orders"]:
            if order["status"] in TERMINAL and not (order["filled_quantity"] and order["average_fill_price"] is None):
                continue
            if order["status"] == "UNKNOWN":
                issues.append("AMBIGUOUS_ORDER")
                continue
            try:
                report = broker.reconcile(intent_id=order["id"])
                if report.get("status") in {"OPEN", "PARTIAL"} and (halted or near_close or not result["gate_passed"] or at(clock()) - at(order["prepared_at"]) >= timedelta(minutes=5)):
                    if at(clock()).astimezone(ZoneInfo(ZONES[market])).date() != at(order["prepared_at"]).astimezone(ZoneInfo(ZONES[market])).date():
                        issues.append("PREVIOUS_SESSION_ORDER_UNRESOLVED")
                    else:
                        broker.cancel(intent_id=order["id"])
                if report.get("status") in {"UNKNOWN", "UNRESOLVED"}:
                    issues.append("AMBIGUOUS_ORDER")
            except Exception:
                issues.append("ORDER_REPORT_UNVERIFIED")
        current = summary(broker.db, at(clock()), market)
        pending = any(o["status"] not in TERMINAL for o in current["orders"])
        holdings_verified = True
        held = next((ticker for ticker, qty in current["owned"].items() if qty), None)
        if held:
            try:
                q = quote_loader(market, held, clock)
                terms = {"ticker": held[:6] if market == "KR" else held, "limit_price": limit_price(q, "BUY", market)}
                if market == "US":
                    terms["exchange"] = q["exchange"]
                account = account_loader(market, broker, terms, clock)
                verify_owned(account, current["owned"], market, scope, at(clock()))
                marks[held] = q
            except Exception:
                holdings_verified = False
                issues.append("STRATEGY_ACCOUNT_POSITION_UNVERIFIED")
        if broker.db.execute("SELECT 1 FROM requests WHERE status='UNKNOWN'").fetchone() or broker.db.execute("SELECT 1 FROM reconciliation_issues").fetchone():
            issues.append("AMBIGUOUS_ORDER")
        source = (_latest_source(archive, market.lower(), at(clock()),
                  required_artifacts=("decision_bundle_v2.json", "portfolio-private/portfolio_candidates.json"))
                  if allocation_mode == demo_strategy_plan.MODE else _latest_source(archive, market.lower(), at(clock())))
        try:
            result["source_diagnostics"] = diagnose_source(source, at(clock()),
                include_proposals=allocation_mode != demo_strategy_plan.MODE)
            if allocation_mode == demo_strategy_plan.MODE and source:
                signals, plan_diagnostics = demo_strategy_plan.plan(source, market, at(clock()), tickers, current["owned"])
                result["allocation_diagnostics"] = plan_diagnostics
            else:
                signals = candidates(source, market, at(clock()), tickers) if source else []
            if not signals and not pending and not issues and not halted and not near_close and result["gate_passed"]:
                required = (("decision_bundle_v2.json", "portfolio-private/portfolio_candidates.json")
                            if allocation_mode == demo_strategy_plan.MODE else None)
                selected, handoff = await_completed_source(archive, root.parent, market, source, clock=clock,
                    selector=lambda archive, market, now: _latest_source(archive, market, now, required_artifacts=required))
                if handoff is not None:
                    result["source_refresh_handoff"] = handoff
                    session = session_resolver(market=market, now_local=at(clock()))
                    after_wait = at(clock())
                    if (session.get("source") != "exchange_calendars" or session.get("is_open") is not True
                            or session.get("phase") != "regular"
                            or not at(session["session_open"]) <= after_wait < at(session["session_close"])):
                        result.update(current)
                        return finish("BLOCKED", "SESSION_ENDED_DURING_SOURCE_WAIT")
                    near_close = at(session["session_close"]) - after_wait <= timedelta(minutes=10)
                    try:
                        result["gate_passed"] = gate(validation_root, market, after_wait) == scope
                    except Exception:
                        result["gate_passed"] = False
                    source = selected
                    result["source_diagnostics"] = diagnose_source(source, at(clock()),
                        include_proposals=allocation_mode != demo_strategy_plan.MODE)
                    if allocation_mode == demo_strategy_plan.MODE:
                        signals, plan_diagnostics = demo_strategy_plan.plan(source, market, at(clock()), tickers, current["owned"])
                        result["allocation_diagnostics"] = plan_diagnostics
                    else:
                        signals = candidates(source, market, at(clock()), tickers)
        except Exception:
            signals = []
            issues.append("SOURCE_EVIDENCE_UNVERIFIED")
        result["source_run_id"] = source.name if source else None
        if not result["gate_passed"]:
            issues.append("VALIDATION_REQUIRED")
        if halted:
            issues.append("HALTED")
        if near_close or at(clock()) - at(session["session_open"]) < timedelta(minutes=2):
            issues.append("SESSION_EDGE")
        if not signals:
            issues.extend(result.get("source_diagnostics", {}).get("blockers") or ["NO_FRESH_EXECUTABLE_STRATEGY"])
        today = at(clock()).astimezone(ZoneInfo(ZONES[market])).date()
        attempts_today = sum(at(row[0]).astimezone(ZoneInfo(ZONES[market])).date() == today
                             for row in broker.db.execute("SELECT prepared_at FROM strategy_attempts"))
        if attempts_today >= 3:
            issues.append("DAILY_ORDER_LIMIT")
        # One intent per tick, and no overlapping strategy orders: account views
        # cannot silently consume the same cash or holdings across symbols.
        if not pending and not issues:
            considered = 0
            for candidate in signals:
                if broker.db.execute("SELECT 1 FROM strategy_attempts WHERE id=?", (candidate["id"],)).fetchone():
                    continue
                if candidate.get("allocation_mode") == demo_strategy_plan.MODE and candidate["side"] == "BUY":
                    # One new entry per session leaves capacity for a legitimate
                    # strategy exit under the unchanged three-order broker cap.
                    if any(at(row[0]).astimezone(ZoneInfo(ZONES[market])).date() == today
                           and json.loads(row[1])["side"] == "BUY"
                           for row in broker.db.execute("SELECT prepared_at,terms FROM strategy_attempts")):
                        issues.append("DAILY_NEW_ENTRY_LIMIT")
                        continue
                considered += 1
                if considered > 3:
                    break
                try:
                    quote = quote_loader(market, candidate["ticker"], clock)
                    _fresh(quote, now=at(clock()), seconds=120)
                    price = limit_price(quote, candidate["side"], market)
                    terms = {"ticker": candidate["signal"]["ticker"], "side": candidate["side"], "limit_price": price}
                    if market == "US":
                        terms["exchange"] = quote["exchange"]
                    account = account_loader(market, broker, terms, clock)
                    terms["quantity"] = quantity(candidate, price, account, market, current["owned"], at(clock()))
                except Exception as exc:
                    reason = str(exc)
                    issues.append(reason if reason in {"NO_STRATEGY_QUANTITY_WITHIN_LIMITS", "BUDGET_FX_UNVERIFIED", "PROPOSAL_QUANTITY_INVALID"} else "CANDIDATE_EVIDENCE_UNVERIFIED")
                    continue
                if (root / "HALT").exists() or (validation_root / "HALT").exists():
                    issues.append("HALTED")
                    break
                entry_deadline = min(at(candidate["signal"]["valid_until"]), at(session["session_close"]) - timedelta(minutes=10))
                if at(clock()) >= at(session["session_close"]) - timedelta(minutes=10):
                    issues.append("SESSION_EDGE")
                    break
                if at(clock()) >= entry_deadline:
                    issues.append("STRATEGY_SIGNAL_EXPIRED_DURING_PREPARATION")
                    continue
                signal = {**candidate["signal"], "valid_until": entry_deadline.isoformat()}
                broker.db.execute("INSERT INTO strategy_attempts VALUES (?,?,?,?,?,?)", (candidate["id"], candidate["ticker"], candidate["run_id"], at(clock()).isoformat(), json.dumps(terms, sort_keys=True), "PREPARED"))
                if candidate.get("evidence"):
                    broker.db.execute("INSERT INTO strategy_source_evidence VALUES (?,?)",
                                      (candidate["id"], json.dumps(candidate["evidence"], sort_keys=True)))
                try:
                    broker.submit(intent_id=candidate["id"], **terms, signal=signal, quote=quote, account=account)
                except Exception:
                    # If no broker intent exists, deterministic validation failed.
                    # A persisted intent without a response remains ambiguous.
                    if not broker.db.execute("SELECT 1 FROM paper_intents WHERE id=?", (candidate["id"],)).fetchone():
                        broker.db.execute("UPDATE strategy_attempts SET state='BLOCKED' WHERE id=?", (candidate["id"],))
                    issues.append("SUBMISSION_BLOCKED_OR_UNRESOLVED")
                break
        current = summary(broker.db, at(clock()), market)
        for ticker, qty in current["owned"].items():
            if qty and holdings_verified:
                try:
                    if ticker not in marks:
                        marks[ticker] = quote_loader(market, ticker, clock)
                except Exception:
                    issues.append("VALUATION_UNVERIFIED")
        result.update(summary(broker.db, at(clock()), market, marks))
        performance = result["performance"]
        if performance["status"] == "AVAILABLE":
            broker.db.execute("INSERT OR IGNORE INTO strategy_valuations VALUES (?,?)", (performance["observed_at"], json.dumps(performance, sort_keys=True)))
            result["performance_history"] = _performance_history(broker.db, at(clock()))
    return finish("BLOCKED" if issues and issues != ["NO_FRESH_EXECUTABLE_STRATEGY"] else "WAITING_SIGNAL" if issues else "ACTIVE", *sorted(set(issues)))


def tick(archive, root, validation_root, *, clock=None, broker_factory=None, quote_loader=None, account_loader=None, session_resolver=None, gate=None, tickers=None):
    archive, root, validation_root = Path(archive), Path(root), Path(validation_root)
    clock = clock or (lambda: datetime.now(timezone.utc))
    start = at(clock())
    with interprocess_file_lock(root / "strategy.lock", timeout=0), interprocess_file_lock(validation_root / "campaign.lock", timeout=0):
        try:
            config = read(root / "enabled.json", {})
        except (ValueError, OSError):
            config = {}
        enabled = isinstance(config, dict) and config.get("mode") == MODE and config.get("enabled") is True and config.get("real_orders_enabled") is False
        allocation_mode = config.get("allocation_mode", "ARCHIVED_PROPOSALS") if isinstance(config, dict) else "ARCHIVED_PROPOSALS"
        if allocation_mode not in {"ARCHIVED_PROPOSALS", demo_strategy_plan.MODE}:
            raise ValueError("INVALID_STRATEGY_ALLOCATION_MODE")
        markets = {}
        for market in ZONES:
            if not enabled:
                markets[market] = {"status": "DISABLED", "checked_at": at(clock()).isoformat(), "blockers": [], "gate_passed": False}
                continue
            try:
                markets[market] = advance(archive, root, validation_root, market, clock=clock, tickers=(tickers or universe())[market],
                    broker_factory=broker_factory or broker_context, quote_loader=quote_loader or current_quote,
                    account_loader=account_loader or validation.current_account, session_resolver=session_resolver or _runtime_session,
                    gate=gate or validation_gate, allocation_mode=allocation_mode)
            except Exception:
                markets[market] = {"status": "BLOCKED", "checked_at": at(clock()).isoformat(), "gate_passed": False, "blockers": ["RUNTIME_EVIDENCE_UNVERIFIED"]}
        finished = at(clock())
        # Preserve the original attempt receipt as diagnostics even when the
        # exchange is closed. This does not reset the producer or spend a slot.
        from .strategy_diagnostics import REFRESH_FIELDS
        for market, row in markets.items():
            try:
                attempt = read(root.parent / "execution-refresh" / f"{market.lower()}.json")
                row["refresh_attempt"] = ({key: attempt.get(key) for key in REFRESH_FIELDS}
                                          if isinstance(attempt, dict) else attempt)
            except (OSError, ValueError):
                row["refresh_attempt"] = {"status": "UNVERIFIED"}
        if finished < start or any(at(row["checked_at"]) > finished for row in markets.values()):
            raise ValueError("RUNTIME_CLOCK_REGRESSED")
        import os
        receipt = {"schema": SCHEMA, "mode": MODE, "enabled": enabled, "real_orders_enabled": False,
                   "checked_at": finished.isoformat(), "source_revision": os.getenv("TRADINGAGENTS_SOURCE_SHA"), "markets": markets}
        atomic_write_json(archive / "paper/kis-strategy-runtime.json", receipt)
        return receipt
