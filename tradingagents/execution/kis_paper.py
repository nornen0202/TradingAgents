"""Guarded KIS VTS execution. This module cannot select a live host or account.

The VTS request journal is reused rather than adding an independent HTTP stack.
Broker acknowledgements and cumulative fill observations never become invented
settled fills. Explicit settlement evidence has a separate demo-only import path.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any, Mapping
from zoneinfo import ZoneInfo

from tradingagents.atomic_io import interprocess_file_lock
from tradingagents.dataflows.market_policy import aware_datetime, observation_status
from tradingagents.performance.lifecycle import append_lifecycle_event, initialize_lifecycle
from tradingagents.scheduled.market_calendar import market_session_state
from .kis_demo import DEMO_HOST, DemoError, DemoOrderJournal, KisDemoClient
from .paper import kis_demo_order_preview


KST = ZoneInfo("Asia/Seoul")
SCHEMA = "tradingagents.kis-paper/v1"


def _clock(value: Any) -> datetime:
    parsed = aware_datetime(value)
    if parsed is None:
        raise DemoError("Explicit aware timestamp required")
    return parsed.astimezone(timezone.utc)


def _number(value: Any, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or (value <= 0 if positive else value < 0):
        raise DemoError("Finite explicit nonnegative amounts required")
    return float(value)


def _integer(value: Any, *, positive: bool = False) -> int:
    if type(value) is not int or (value <= 0 if positive else value < 0):
        raise DemoError("Explicit nonnegative integer quantity required")
    return value


def _broker_number(value: Any, *, integer: bool = False) -> int | float:
    # Broker strings are intentionally handled only at the response boundary.
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", value):
        raise DemoError("VTS amount missing or malformed")
    number = float(value)
    if not math.isfinite(number) or (integer and int(number) != number):
        raise DemoError("VTS amount missing or malformed")
    return int(number) if integer else number


def _stable(value: Any) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 180:
        raise DemoError("Stable signal and intent identifiers required")
    return value


def execution_notional(row, quantity, terms, *, market):
    """Optional broker cumulative cash amount; never substitute the limit price.

    Missing/malformed amounts preserve quantity reconciliation but make monetary
    performance unavailable. This is gross execution cash flow, not settlement.
    """
    if not quantity:
        return 0.0
    try:
        amount = _broker_number(row.get("tot_ccld_amt" if market == "KR" else "ft_ccld_amt3"))
        limit = quantity * terms["limit_price"]
        if amount <= 0 or (terms["side"] == "BUY" and amount > limit + .01) or (terms["side"] == "SELL" and amount < limit - .01):
            return None
        return amount
    except (DemoError, TypeError, KeyError):
        return None


def _fresh(mapping: Mapping, *, now: datetime, seconds: int) -> None:
    observed, ingested = _clock(mapping.get("observed_at")), _clock(mapping.get("ingested_at"))
    if observed > ingested or ingested > now or not observation_status(observed, as_of=now, max_age=timedelta(seconds=seconds))["eligible"]:
        raise DemoError("Future, stale or invalid source clocks")


def _tick(price: int, kind: str) -> int:
    if kind == "ETF":
        return 5
    for ceiling, tick in ((2000, 1), (5000, 5), (20000, 10), (50000, 50), (200000, 100), (500000, 500)):
        if price < ceiling:
            return tick
    return 1000


@dataclass(frozen=True)
class PaperOrderPolicy:
    """A policy is immutable for one journal; revised policies use a new journal."""
    allowed_tickers: tuple[str, ...]
    max_order_krw: int = 100_000
    max_daily_buy_krw: int = 300_000
    max_daily_orders: int = 3
    cash_floor_krw: int = 0
    max_position_fraction: float = 0.35
    max_quote_age_seconds: int = 120
    max_account_age_seconds: int = 120
    max_limit_distance_bps: int = 100
    reserve_cost_bps: int = 30

    def __post_init__(self):
        if not isinstance(self.allowed_tickers, tuple) or not self.allowed_tickers or len(set(self.allowed_tickers)) != len(self.allowed_tickers) or any(not isinstance(t, str) or re.fullmatch(r"[0-9]{6}", t) is None for t in self.allowed_tickers):
            raise DemoError("Explicit unique KR ticker allowlist required")
        for key in ("max_order_krw", "max_daily_buy_krw", "max_daily_orders", "max_quote_age_seconds", "max_account_age_seconds", "max_limit_distance_bps", "reserve_cost_bps"):
            _integer(getattr(self, key), positive=True)
        _integer(self.cash_floor_krw)
        if self.max_quote_age_seconds > 120 or self.max_account_age_seconds > 120 or self.max_limit_distance_bps > 1000 or self.reserve_cost_bps > 1000:
            raise DemoError("Paper clock/collar policy exceeds hard limits")
        if not 0 < _number(self.max_position_fraction, positive=True) <= 1:
            raise DemoError("Invalid paper position limit")


def read_paper_account(client: KisDemoClient, *, ticker: str, limit_price: int, clock=None) -> dict:
    """Read complete VTS holdings and cash-only capacity for this exact order.

    Stamps mean local observation of broker responses, not an invented exchange
    quote or settlement timestamp. Cash-only buying capacity is queried per symbol.
    """
    now_fn = clock or (lambda: datetime.now(timezone.utc))
    started = _clock(now_fn())
    rows, raw_totals = client.balance()
    totals = raw_totals if isinstance(raw_totals, dict) else raw_totals[0] if len(raw_totals) == 1 else None
    if not isinstance(totals, dict):
        raise DemoError("VTS single complete account totals required")
    positions, seen = [], set()
    for row in rows:
        symbol = row.get("pdno")
        if not isinstance(symbol, str) or not re.fullmatch(r"[0-9]{6}", symbol) or symbol in seen:
            raise DemoError("VTS duplicate or unknown position identity")
        seen.add(symbol)
        quantity = _broker_number(row.get("hldg_qty"), integer=True)
        available = _broker_number(row.get("ord_psbl_qty"), integer=True)
        if available > quantity:
            raise DemoError("VTS sellable amount exceeds holdings")
        positions.append({"ticker": symbol, "quantity": quantity, "sellable_quantity": available,
                          "market_value_krw": _broker_number(row.get("evlu_amt"))})
    capacity = client.buying_power(ticker=ticker, limit_price=limit_price)
    ingested = _clock(now_fn())
    return {"environment": "demo", "account_scope": client.credentials.scope(), "complete": True,
            "observed_at": started.isoformat(), "ingested_at": ingested.isoformat(),
            "cash_krw": _broker_number(totals.get("dnca_tot_amt")),
            "nav_krw": _broker_number(totals.get("tot_evlu_amt")), "positions": positions,
            "cash_only_buying_power_krw": _broker_number(capacity.get("nrcvb_buy_amt")),
            "cash_only_buying_quantity": _broker_number(capacity.get("nrcvb_buy_qty"), integer=True),
            "capacity_ticker": ticker, "capacity_limit_price": limit_price}


class KisPaperBroker:
    """Explicit opt-in paper bridge, serialized across local cooperating runners.

    ``clock`` is a test seam. Production callers leave it unset; order submission
    has no caller-supplied historical ``now`` and cannot backdate a live request.
    """
    def __init__(self, path: Path | str, client: KisDemoClient, policy: PaperOrderPolicy,
                 *, paper_enabled: bool = False, clock=None):
        if type(client) is not KisDemoClient or client.credentials.product_code != "01" or type(paper_enabled) is not bool or not isinstance(policy, PaperOrderPolicy):
            raise DemoError("Dedicated VTS client, explicit policy and boolean opt-in required")
        self.path, self.client, self.policy = Path(path), client, policy
        self.enabled, self.clock = paper_enabled, clock or (lambda: datetime.now(timezone.utc))
        self.journal = DemoOrderJournal(self.path, client, issue_clock=self.clock)
        self.db = self.journal.db
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS paper_policy(scope TEXT PRIMARY KEY, policy TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS paper_intents(id TEXT PRIMARY KEY, terms TEXT NOT NULL,
                signal_id TEXT NOT NULL, created_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS paper_observations(id TEXT NOT NULL, observed_at TEXT NOT NULL,
                evidence TEXT NOT NULL, PRIMARY KEY(id,observed_at,evidence));
            CREATE TRIGGER IF NOT EXISTS paper_intents_no_update BEFORE UPDATE ON paper_intents
                BEGIN SELECT RAISE(ABORT,'Paper intent is immutable'); END;
            CREATE TRIGGER IF NOT EXISTS paper_intents_no_delete BEFORE DELETE ON paper_intents
                BEGIN SELECT RAISE(ABORT,'Paper intent is immutable'); END;
        """)
        initialize_lifecycle(self.db)
        encoded = json.dumps(asdict(policy), sort_keys=True)
        with interprocess_file_lock(self.path.with_suffix(self.path.suffix + ".paper.lock")):
            previous = self.db.execute("SELECT policy FROM paper_policy WHERE scope=?", (client.credentials.scope(),)).fetchone()
            if previous and previous[0] != encoded:
                self.close()
                raise DemoError("Policy changed; use a separately named paper journal")
            self.db.execute("INSERT OR IGNORE INTO paper_policy VALUES (?,?)", (client.credentials.scope(), encoded))

    def close(self):
        self.journal.close()

    def _session(self, now):
        session = market_session_state(market="KR", now_local=now)
        if session.get("source") != "exchange_calendars" or session.get("phase") != "regular" or session.get("is_open") is not True or not _clock(session.get("session_open")) <= now < _clock(session.get("session_close")):
            raise DemoError("Verified current KRX regular session required")
        return session

    def _validate(self, terms, signal, quote, account, now):
        if not self.enabled:
            raise DemoError("Paper trading requires explicit VTS opt-in")
        session = self._session(now)
        ticker, side, quantity, price = (terms[k] for k in ("ticker", "side", "quantity", "limit_price"))
        if ticker not in self.policy.allowed_tickers:
            raise DemoError("Ticker is outside paper allowlist")
        if not all(isinstance(item, Mapping) for item in (signal, quote, account)):
            raise DemoError("Explicit signal, quote and account evidence required")
        expected = {"BUY": {"STARTER_NOW", "ADD_NOW"}, "SELL": {"REDUCE_NOW", "EXIT_NOW"}}
        if signal.get("ticker") != ticker or signal.get("execution_ready") is not True or signal.get("decision_now") not in expected[side]:
            raise DemoError("Existing execution verdict does not authorize this side")
        available, expiry = _clock(signal.get("available_at")), _clock(signal.get("valid_until"))
        if not available <= now < expiry or (now - available).total_seconds() >= self.policy.max_quote_age_seconds:
            raise DemoError("Signal future, stale or expired")
        if quote.get("ticker") != ticker or quote.get("provider") not in {"kis", "kis_quote", "kis_microstructure"} or quote.get("currency") != "KRW" or quote.get("session") != "regular" or quote.get("execution_ready") is not True or quote.get("instrument_type") not in {"STOCK", "ETF"}:
            raise DemoError("Verified same-symbol KIS KRW regular quote required")
        _fresh(quote, now=now, seconds=self.policy.max_quote_age_seconds)
        last = _number(quote.get("last_price"), positive=True)
        if price % _tick(price, quote["instrument_type"]) or abs(price / last - 1) * 10000 > self.policy.max_limit_distance_bps + 1e-8:
            raise DemoError("Limit violates quote collar or KRX tick unit")
        if account.get("environment") != "demo" or account.get("account_scope") != self.client.credentials.scope() or account.get("complete") is not True:
            raise DemoError("Complete account from the same VTS scope required")
        _fresh(account, now=now, seconds=self.policy.max_account_age_seconds)
        nav = _number(account.get("nav_krw"), positive=True)
        cash = _number(account.get("cash_krw"))
        rows = account.get("positions")
        if not isinstance(rows, list):
            raise DemoError("Explicit complete positions list required")
        positions = {}
        for row in rows:
            if not isinstance(row, Mapping) or not isinstance(row.get("ticker"), str) or not re.fullmatch(r"[0-9]{6}", row["ticker"]) or row["ticker"] in positions:
                raise DemoError("Duplicate or invalid account position")
            held, sellable = _integer(row.get("quantity")), _integer(row.get("sellable_quantity"))
            if sellable > held:
                raise DemoError("Sellable amount exceeds holdings")
            _number(row.get("market_value_krw"))
            positions[row["ticker"]] = row
        notional = quantity * price
        if notional > self.policy.max_order_krw:
            raise DemoError("Per-order paper notional limit exceeded")
        requests = self.db.execute("""SELECT p.*,r.status,i.body,s.filled,s.remaining,s.status AS order_status
            FROM paper_intents p LEFT JOIN requests r ON p.id=r.id
            LEFT JOIN intents i ON p.id=i.id LEFT JOIN order_state s ON p.id=s.id""").fetchall()
        count, bought, reserved_buy, reserved_sell = 0, 0, 0, 0
        held_symbol_reserve = 0
        for row in requests:
            original = json.loads(row["terms"])
            if row["status"] in {"NOT_SENT", "REJECTED"}:
                continue
            if _clock(row["created_at"]).astimezone(KST).date() == now.astimezone(KST).date():
                count += 1
                if original["side"] == "BUY":
                    bought += original["quantity"] * original["limit_price"]
            remainder = row["remaining"] if row["remaining"] is not None else original["quantity"]
            if row["order_status"] in {"FILLED", "CANCELLED"}:
                remainder = 0
            if original["side"] == "BUY":
                reserved_buy += remainder * original["limit_price"]
                if original["ticker"] == ticker:
                    held_symbol_reserve += remainder * original["limit_price"]
            elif original["ticker"] == ticker:
                reserved_sell += remainder
        if count >= self.policy.max_daily_orders:
            raise DemoError("Daily paper order limit exceeded")
        if side == "BUY":
            if bought + notional > self.policy.max_daily_buy_krw:
                raise DemoError("Daily paper buy limit exceeded")
            if account.get("capacity_ticker") != ticker or account.get("capacity_limit_price") != price:
                raise DemoError("Cash-only capacity must match ticker and limit")
            capacity = _number(account.get("cash_only_buying_power_krw"))
            capacity_qty = _integer(account.get("cash_only_buying_quantity"))
            reserve = (reserved_buy + notional) * (1 + self.policy.reserve_cost_bps / 10000)
            if quantity > capacity_qty or reserve > min(cash - self.policy.cash_floor_krw, capacity):
                raise DemoError("Cash-only capacity or reserved cash floor exceeded")
            position_value = _number(positions.get(ticker, {}).get("market_value_krw", 0))
            if position_value + held_symbol_reserve + notional > nav * self.policy.max_position_fraction:
                raise DemoError("Paper concentration limit exceeded")
        elif quantity + reserved_sell > positions.get(ticker, {}).get("sellable_quantity", 0):
            # Protective reductions ignore buy cash/concentration caps but never
            # create a short sale or bypass explicit sell/order/session limits.
            raise DemoError("Sell exceeds unreserved sellable holdings")
        return min(expiry, _clock(session["session_close"]))

    def submit(self, *, intent_id: str, ticker: str, side: str, quantity: int, limit_price: int,
               signal: Mapping, quote: Mapping, account: Mapping) -> dict:
        _stable(intent_id)
        signal_id = _stable(signal.get("signal_id") if isinstance(signal, Mapping) else None)
        try:
            kis_demo_order_preview(ticker=ticker, side=side, quantity=quantity, limit_price=limit_price)
        except (ValueError, TypeError):
            raise DemoError("Explicit KR ticker, side and integer quantity/limit required") from None
        terms = {"ticker": ticker, "side": side, "quantity": quantity, "limit_price": limit_price}
        encoded = json.dumps(terms, sort_keys=True)
        with interprocess_file_lock(self.path.with_suffix(self.path.suffix + ".paper.lock"), timeout=60):
            previous = self.db.execute("SELECT * FROM paper_intents WHERE id=?", (intent_id,)).fetchone()
            if previous:
                if previous["terms"] != encoded or previous["signal_id"] != signal_id:
                    raise DemoError("Intent identity reused with different signal or terms")
                receipt = self.db.execute("SELECT status,response FROM requests WHERE id=?", (intent_id,)).fetchone()
                # A crash before transport persistence also stays unresolved. An
                # operator must investigate it instead of recreating its ID.
                result = {"status": receipt["status"], **json.loads(receipt["response"])} if receipt else {"status": "UNKNOWN"}
                return {**result, "mode": "demo", "duplicate": True, "live_orders_enabled": False}
            now = _clock(self.clock())
            expiry = self._validate(terms, signal, quote, account, now)
            if self.db.execute("""SELECT 1 FROM requests r LEFT JOIN paper_intents p ON p.id=r.id
                WHERE r.id NOT LIKE 'cancel:%' AND p.id IS NULL""").fetchone():
                raise DemoError("Legacy VTS requests require a separately reconciled migration")
            if self.db.execute("SELECT 1 FROM paper_intents p LEFT JOIN requests r ON p.id=r.id WHERE r.id IS NULL OR r.status='UNKNOWN'").fetchone():
                raise DemoError("Resolve ambiguous paper intent before another submission")
            if not self.db.execute("SELECT 1 FROM lifecycle_events WHERE kind='ACCOUNT_SEED' AND mode='demo'").fetchone():
                append_lifecycle_event(self.db, event_id="account:demo:" + self.client.credentials.scope(),
                    signal_id="account:demo:" + self.client.credentials.scope(), kind="ACCOUNT_SEED", mode="demo",
                    occurred_at=account["observed_at"], available_at=account["ingested_at"], ingested_at=now.isoformat(),
                    payload={"cash": account["cash_krw"], "currency": "KRW",
                             "positions": {p["ticker"]: p["quantity"] for p in account["positions"]}})
            self.db.execute("INSERT INTO paper_intents VALUES (?,?,?,?)", (intent_id, encoded, signal_id, now.isoformat()))
            append_lifecycle_event(self.db, event_id="intent:demo:" + intent_id, signal_id=signal_id,
                intent_id=intent_id, kind="INTENT", mode="demo", occurred_at=now.isoformat(),
                available_at=now.isoformat(), ingested_at=now.isoformat(), payload={**terms, "status": "VTS_SUBMISSION_INTENT"})
            deadline = min(expiry, _clock(quote["observed_at"]) + timedelta(seconds=self.policy.max_quote_age_seconds),
                           _clock(account["observed_at"]) + timedelta(seconds=self.policy.max_account_age_seconds))
            result = self.journal.submit(intent_id=intent_id, **terms, available_at=signal["available_at"],
                                         valid_until=deadline.isoformat(), now=now.isoformat())
            return {**result, "mode": "demo", "duplicate": False, "live_orders_enabled": False}

    def _validate_order_clocks(self, intent_id, rows, now):
        request = self.db.execute("SELECT * FROM requests WHERE id=?", (intent_id,)).fetchone()
        if not request:
            raise DemoError("Unknown paper intent")
        broker_id = json.loads(request["response"]).get("broker_order_id")
        matches = [row for row in rows if str(row.get("odno")) == broker_id]
        if len(matches) != 1:
            raise DemoError("Missing or duplicate VTS order report")
        row = matches[0]
        raw = str(row.get("ord_dt", "")) + str(row.get("ord_tmd", ""))
        try:
            if not re.fullmatch(r"[0-9]{14}", raw):
                raise ValueError()
            ordered = datetime.strptime(raw, "%Y%m%d%H%M%S").replace(tzinfo=KST)
        except ValueError:
            raise DemoError("Missing or invalid VTS order date/time") from None
        created = _clock(request["created_at"])
        if ordered < created.replace(microsecond=0) or ordered > now or ordered.astimezone(KST).date() != created.astimezone(KST).date():
            raise DemoError("Future or conflicting VTS order time")
        return row

    def reconcile(self, *, intent_id: str) -> dict:
        with interprocess_file_lock(self.path.with_suffix(self.path.suffix + ".paper.lock"), timeout=60):
            return self._reconcile(intent_id)

    def _reconcile(self, intent_id):
        now = _clock(self.clock())
        request = self.db.execute("SELECT * FROM requests WHERE id=?", (intent_id,)).fetchone()
        if not request:
            raise DemoError("Unknown paper intent")
        if not json.loads(request["response"]).get("broker_order_id"):
            return {"status": request["status"], "mode": "demo", "requires_manual_reconciliation": request["status"] == "UNKNOWN"}
        trade_date = _clock(request["created_at"]).astimezone(KST).strftime("%Y%m%d")
        try:
            rows = self.client.orders(trade_date)
            received_at = _clock(self.clock())
            if received_at < now:
                raise DemoError("VTS observation clock regressed during the read")
            report = self._validate_order_clocks(intent_id, rows, received_at)
            # Reuse exactly this verified response instead of a second network
            # call that could change underneath validation.
            result = self.journal.reconcile(intent_id=intent_id, trade_date=trade_date, reports=rows)
            terms = json.loads(self.db.execute("SELECT terms FROM paper_intents WHERE id=?", (intent_id,)).fetchone()[0])
            result["fill_notional"] = execution_notional(report, result.get("filled_qty", 0), terms, market="KR")
            ingested_at = _clock(self.clock())
            if ingested_at < received_at:
                raise DemoError("VTS ingestion clock precedes the received observation")
        except DemoError:
            self.journal._block(intent_id, "unverified_paper_reconciliation")
            raise
        # A current order report becomes known only after the response arrives.
        # Starting the request does not make its later contents available then.
        result = {**result, "mode": "demo", "observed_at": received_at.isoformat(),
                  "ingested_at": ingested_at.isoformat(), "fill_time_known": False,
                  "settlement_known": False, "cumulative_observation_only": True}
        self.db.execute("INSERT OR IGNORE INTO paper_observations VALUES (?,?,?)", (intent_id, received_at.isoformat(), json.dumps(result, sort_keys=True)))
        cancellation_id = "cancel:demo:" + intent_id
        if result["status"] == "CANCELLED" and not self.db.execute("SELECT 1 FROM lifecycle_events WHERE event_id=?", (cancellation_id,)).fetchone():
            intent = self.db.execute("SELECT signal_id,terms FROM paper_intents WHERE id=?", (intent_id,)).fetchone()
            if intent:
                terms = json.loads(intent["terms"])
                append_lifecycle_event(self.db, event_id=cancellation_id, signal_id=intent["signal_id"], intent_id=intent_id,
                    kind="CANCEL", mode="demo", occurred_at=received_at.isoformat(), available_at=ingested_at.isoformat(), ingested_at=ingested_at.isoformat(),
                    payload={"ticker": terms["ticker"], "side": terms["side"], "status": "CANCELLED",
                             "exact_cancellation_time_known": False, "observation_time_only": True})
        return result

    def cancel(self, *, intent_id: str) -> dict:
        with interprocess_file_lock(self.path.with_suffix(self.path.suffix + ".paper.lock"), timeout=60):
            previous = self.db.execute("SELECT status,response FROM requests WHERE id=?", ("cancel:" + intent_id,)).fetchone()
            if previous:
                return {"status": previous["status"], **json.loads(previous["response"]), "mode": "demo", "duplicate": True}
            if not self.enabled:
                raise DemoError("Paper cancellation requires explicit VTS opt-in")
            now = _clock(self.clock())
            session = self._session(now)
            result = self._reconcile(intent_id)
            # The official cancel-capacity query has no documented VTS TR ID.
            # Use verified daily-ccld remainder and await broker confirmation;
            # there is no fallback to the real-only cancel-capacity endpoint.
            deadline = min(now + timedelta(seconds=120), _clock(session["session_close"]))
            response = self.journal.cancel(intent_id=intent_id, trade_date=now.astimezone(KST).strftime("%Y%m%d"),
                now=now.isoformat(), reconciled_receipt=result, deadline=deadline.isoformat())
            return {**response, "mode": "demo", "cancellation_confirmed": False, "live_orders_enabled": False}

    def status(self) -> dict:
        requests = [dict(row) for row in self.db.execute("""SELECT r.id,r.status,r.created_at,
            s.status AS reconciled_status,s.filled,s.remaining FROM requests r
            LEFT JOIN order_state s ON r.id=s.id ORDER BY r.created_at,r.id""")]
        return {"schema": SCHEMA, "mode": "demo", "host": DEMO_HOST,
                "paper_writes_enabled": self.enabled, "live_orders_enabled": False,
                "requests": requests, "unresolved_count": self.db.execute("SELECT count(*) FROM reconciliation_issues").fetchone()[0],
                "observed_at": _clock(self.clock()).isoformat()}


def _import_cashflow_checkpoints(broker, row, state, receipt, now, *, market="KR"):
    """Read same-owner ACK/reconciliation proof, without making broker requests.

    A cumulative report proves an aggregate cash flow, not each execution's
    price. Incremental receipts can only reach an actually observed checkpoint;
    missing checkpoints must not be replaced by an inferred average fill price.
    """
    owners = broker.db.execute("SELECT scope FROM owner").fetchall()
    request = broker.db.execute("SELECT * FROM requests WHERE id=?", (row["id"],)).fetchone()
    original = broker.db.execute("SELECT * FROM intents WHERE id=?", (row["id"],)).fetchone()
    if (len(owners) != 1 or owners[0][0] != broker.client.credentials.scope()
            or not request or request["status"] != "ACKNOWLEDGED" or not original
            or broker.db.execute("SELECT 1 FROM reconciliation_issues WHERE id=?", (row["id"],)).fetchone()):
        raise DemoError("Same-owner acknowledged VTS order proof required")
    response, terms, body = json.loads(request["response"]), json.loads(row["terms"]), json.loads(original["body"])
    broker_id = _stable(response.get("broker_order_id"))
    created = _clock(row["created_at"])
    if market not in {"KR", "US"}:
        raise DemoError("Explicit settlement market required")
    endpoint, buy_tr, sell_tr, price_key = (("order-cash", "VTTC0012U", "VTTC0011U", "ORD_UNPR")
        if market == "KR" else ("order", "VTTT1002U", "VTTT1001U", "OVRS_ORD_UNPR"))
    if (not created <= _clock(request["created_at"]) <= _clock(receipt["executed_at"]) <= now
            or original["endpoint"] != endpoint
            or original["tr_id"] != (buy_tr if terms["side"] == "BUY" else sell_tr)
            or body.get("PDNO") != terms["ticker"]
            or _broker_number(body.get("ORD_QTY"), integer=True) != terms["quantity"]
            or _broker_number(body.get(price_key)) != terms["limit_price"]
            or (market == "US" and body.get("OVRS_EXCG_CD") != terms.get("exchange"))
            or ("broker_order_id" in receipt and receipt["broker_order_id"] != broker_id)
            or ("source" in receipt and receipt["source"] != "kis_vts")):
        raise DemoError("VTS receipt provenance conflicts with original order")
    reconciliations = []
    for item in broker.db.execute("SELECT observed_at,evidence FROM reconciliations WHERE id=?", (row["id"],)):
        observed = _clock(item[0])
        if not created <= observed <= now:
            raise DemoError("Invalid VTS reconciliation proof clock")
        reconciliations.append((observed, json.loads(item[1])))
    observations = []
    for item in broker.db.execute("SELECT observed_at,evidence FROM paper_observations WHERE id=?", (row["id"],)):
        observed, evidence = _clock(item[0]), json.loads(item[1])
        ingested = _clock(evidence.get("ingested_at"))
        if (not _clock(request["created_at"]) <= observed <= ingested <= now
                or observed != _clock(evidence.get("observed_at"))
                or evidence.get("broker_order_id") != broker_id or evidence.get("mode") != "demo"
                or evidence.get("live_orders_enabled") is True or evidence.get("real_orders_enabled") is True
                or evidence.get("cumulative_observation_only") is not True
                or evidence.get("fill_time_known") is not False or evidence.get("settlement_known") is not False):
            raise DemoError("Invalid VTS cash-flow observation provenance")
        qty = _integer(evidence.get("filled_qty"))
        remaining = _integer(evidence.get("remaining_qty"))
        status = evidence.get("status")
        if (not 0 <= qty <= terms["quantity"] or remaining > terms["quantity"] - qty
                or status not in {"OPEN", "PARTIAL", "FILLED", "CANCELLED"}
                or (status == "OPEN" and (qty != 0 or remaining != terms["quantity"]))
                or (status == "PARTIAL" and (not 0 < qty < terms["quantity"] or remaining != terms["quantity"] - qty))
                or (status == "FILLED" and (qty != terms["quantity"] or remaining != 0))
                or (status == "CANCELLED" and remaining != 0)
                or not any(observed <= at <= ingested and all(proof.get(key) == evidence.get(key)
                    for key in ("broker_order_id", "status", "filled_qty", "remaining_qty"))
                    for at, proof in reconciliations)):
            raise DemoError("VTS cash-flow observation lacks matching reconciliation")
        amount = evidence.get("fill_notional")
        amount = None if amount is None else Decimal(str(_number(amount, positive=qty > 0)))
        if (amount is not None and (qty == 0 and amount != 0
                or terms["side"] == "BUY" and amount > Decimal(str(terms["limit_price"])) * qty
                or terms["side"] == "SELL" and amount < Decimal(str(terms["limit_price"])) * qty)):
            raise DemoError("VTS observed cash flow conflicts with order price")
        observations.append((observed, ingested, qty, amount, remaining, status))
    observations.sort(key=lambda item: (item[0], item[1]))
    last_qty, last_amount, amount_qty = 0, Decimal(0), 0
    for _, _, qty, amount, _, _ in observations:
        if qty < last_qty or amount is not None and (amount < last_amount or qty == amount_qty and amount != last_amount):
            raise DemoError("VTS cash-flow proof regressed or was corrected")
        last_qty = qty
        if amount is not None:
            last_amount, amount_qty = amount, qty
    if not observations or (observations[-1][2], observations[-1][4], observations[-1][5]) != (state["filled"], state["remaining"], state["status"]):
        raise DemoError("VTS state lacks a matching current observation")
    return observations


def import_demo_fill(broker: KisPaperBroker, receipt: Mapping) -> bool:
    """Append explicit incremental, settled VTS evidence as mode demo only.

    Daily cumulative order reports are insufficient input. Costs, execution,
    confirmation and settlement must be independently supplied and known by now.
    Imported gross cash flows must match same-order broker observations. This
    validates their provenance, not the independently supplied settlement cost.
    """
    if not isinstance(receipt, Mapping) or receipt.get("environment") != "demo" or receipt.get("account_scope") != broker.client.credentials.scope():
        raise DemoError("Explicit same-scope VTS fill receipt required")
    intent_id, fill_id = _stable(receipt.get("intent_id")), _stable(receipt.get("fill_id"))
    now = _clock(broker.clock())
    executed, confirmed, settled = (_clock(receipt.get(k)) for k in ("executed_at", "confirmed_at", "settled_at"))
    if not executed <= confirmed <= settled <= now:
        raise DemoError("Future or invalid VTS fill clocks")
    quantity = _integer(receipt.get("quantity"), positive=True)
    price, cost = _number(receipt.get("price"), positive=True), _number(receipt.get("cost"))
    if receipt.get("currency") != "KRW":
        raise DemoError("VTS fill currency must be explicit KRW")
    with interprocess_file_lock(broker.path.with_suffix(broker.path.suffix + ".paper.lock")):
        row = broker.db.execute("SELECT * FROM paper_intents WHERE id=?", (intent_id,)).fetchone()
        state = broker.db.execute("SELECT * FROM order_state WHERE id=?", (intent_id,)).fetchone()
        if not row or not state:
            raise DemoError("Verified reconciled VTS intent required")
        checkpoints = _import_cashflow_checkpoints(broker, row, state, receipt, now)
        terms = json.loads(row["terms"])
        if receipt.get("ticker") != terms["ticker"] or receipt.get("side") != terms["side"] or executed < _clock(row["created_at"]) or (terms["side"] == "BUY" and price > terms["limit_price"]) or (terms["side"] == "SELL" and price < terms["limit_price"]):
            raise DemoError("VTS fill conflicts with immutable intent")
        event_id = "fill:demo:" + hashlib.sha256((broker.client.credentials.scope() + ":" + fill_id).encode()).hexdigest()
        previous = broker.db.execute("SELECT event_id FROM lifecycle_events WHERE event_id=?", (event_id,)).fetchone()
        prior = [json.loads(r[0]) for r in broker.db.execute("SELECT payload_json FROM lifecycle_events WHERE intent_id=? AND mode='demo' AND kind='FILL'", (intent_id,))]
        already = sum(item["quantity"] for item in prior)
        if not previous and already + quantity > state["filled"]:
            raise DemoError("Incremental fill exceeds broker-observed cumulative fill")
        imported_quantity = already + (0 if previous else quantity)
        imported_amount = sum((Decimal(str(item["quantity"])) * Decimal(str(item["price"])) for item in prior), Decimal(0))
        if not previous:
            imported_amount += Decimal(quantity) * Decimal(str(price))
        if not any(executed <= observed and qty == imported_quantity and amount == imported_amount
                   for observed, _, qty, amount, _, _ in checkpoints):
            raise DemoError("Imported fill cash flow lacks an equal broker-observed checkpoint")
        broker.db.execute("BEGIN IMMEDIATE")
        try:
            inserted = append_lifecycle_event(broker.db, event_id=event_id, signal_id=row["signal_id"], intent_id=intent_id,
                kind="FILL", mode="demo", occurred_at=executed.isoformat(), available_at=confirmed.isoformat(),
                confirmed_at=confirmed.isoformat(), settled_at=settled.isoformat(), ingested_at=now.isoformat(),
                payload={"ticker": terms["ticker"], "side": terms["side"], "quantity": quantity, "price": price,
                         "cost": cost, "currency": "KRW", "broker_fill_id": fill_id, "source": "kis_vts"})
            from tradingagents.performance.journal import record_fill_retrospectives
            # Out-of-order imports may provide an earlier entry after its exit.
            # Reconcile every now-known demo exit without crossing modes.
            for exit_row in broker.db.execute("SELECT event_id,payload_json FROM lifecycle_events WHERE mode='demo' AND kind='FILL'").fetchall():
                candidate = json.loads(exit_row[1])
                if candidate.get("side") == "SELL" and candidate.get("ticker") == terms["ticker"]:
                    record_fill_retrospectives(broker.db, exit_event_id=exit_row[0], evaluated_at=now.isoformat(), clock=lambda: now)
            broker.db.execute("COMMIT")
            return inserted
        except Exception:
            broker.db.execute("ROLLBACK")
            raise
