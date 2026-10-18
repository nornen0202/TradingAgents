"""Guarded US KIS VTS execution (USD, US regular sessions only). This module cannot select a live host or account.

The VTS request journal is reused rather than adding an independent HTTP stack.
Broker acknowledgements and cumulative fill observations never become invented
settled fills or exact execution timestamps.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re
from typing import Mapping

from tradingagents.atomic_io import interprocess_file_lock
from tradingagents.performance.lifecycle import append_lifecycle_event, initialize_lifecycle
from tradingagents.scheduled.market_calendar import market_session_state
from .kis_demo import DEMO_HOST, DemoError, DemoOrderJournal
from .kis_demo_us import KisDemoUSClient, EXCHANGES, NEW_YORK, SEOUL
from .kis_paper import _clock, _number, _integer, _broker_number, _stable, _fresh, execution_notional
from .paper import stamp


SCHEMA = "tradingagents.kis-us-paper/v1"


def _instrument(ticker, exchange):
    if not isinstance(ticker, str) or not re.fullmatch(r"[A-Z][A-Z0-9.]{0,9}", ticker) or exchange not in EXCHANGES:
        raise DemoError("Explicit supported US ticker and exchange required")


def _price(value):
    # Whole-share US securities >= $1; conservative penny increments remain
    # valid for finer-tick securities. Sub-dollar/fractional orders are excluded.
    _number(value, positive=True)
    try:
        price = Decimal(str(value))
        if price < 1 or price != price.quantize(Decimal("0.01")):
            raise DemoError("US limit must be at least USD 1 at a penny increment")
    except InvalidOperation:
        raise DemoError("Invalid US limit price") from None
    return format(price, ".2f")


@dataclass(frozen=True)
class USPaperOrderPolicy:
    """A policy is immutable for one journal; revised policies use a new journal."""
    allowed_instruments: tuple[tuple[str, str], ...]
    max_order_usd: int = 500
    max_daily_buy_usd: int = 1000
    max_daily_orders: int = 3
    cash_floor_usd: int = 0
    max_position_fraction: float = 0.35
    max_quote_age_seconds: int = 120
    max_account_age_seconds: int = 120
    max_limit_distance_bps: int = 100
    reserve_cost_bps: int = 30
    # Strategy universes can resolve the venue from a current dated quote.
    # The ticker allowlist stays immutable; quote and order venue must agree.
    allowed_tickers: tuple[str, ...] = ()

    def __post_init__(self):
        if not isinstance(self.allowed_instruments, tuple) or not (self.allowed_instruments or self.allowed_tickers) or len(set(self.allowed_instruments)) != len(self.allowed_instruments):
            raise DemoError("Explicit unique US ticker/exchange allowlist required")
        if not isinstance(self.allowed_tickers, tuple) or len(set(self.allowed_tickers)) != len(self.allowed_tickers):
            raise DemoError("Explicit unique strategy universe required")
        for ticker in self.allowed_tickers:
            _instrument(ticker, "NASD")
        for item in self.allowed_instruments:
            if not isinstance(item, tuple) or len(item) != 2:
                raise DemoError("Explicit ticker/exchange tuple required")
            _instrument(*item)
        if len({symbol for symbol, _ in self.allowed_instruments}) != len(self.allowed_instruments):
            raise DemoError("A symbol must have one verified US exchange")
        for key in ("max_order_usd", "max_daily_buy_usd", "max_daily_orders", "max_quote_age_seconds", "max_account_age_seconds", "max_limit_distance_bps", "reserve_cost_bps"):
            _integer(getattr(self, key), positive=True)
        _integer(self.cash_floor_usd)
        if self.max_quote_age_seconds > 120 or self.max_account_age_seconds > 120 or self.max_limit_distance_bps > 1000 or self.reserve_cost_bps > 1000:
            raise DemoError("Paper clock/collar policy exceeds hard limits")
        if not 0 < _number(self.max_position_fraction, positive=True) <= 1:
            raise DemoError("Invalid paper position limit")


def read_paper_us_account(client: KisDemoUSClient, *, ticker, exchange, limit_price, clock=None):
    """Complete US holdings plus USD capacity; never use after-conversion limits.

    nav_usd is a conservative risk denominator, not a performance/NAV report:
    current USD cash capacity plus marked US stock holdings. No KRW conversion
    or automatic FX funds increase the available USD cash.
    """
    _instrument(ticker, exchange)
    _price(limit_price)
    now_fn = clock or (lambda: datetime.now(timezone.utc))
    started = _clock(now_fn())
    positions, seen = [], set()
    for venue in EXCHANGES:
        rows, _ = client.balance(venue)
        for row in rows:
            symbol, actual_exchange = row.get("ovrs_pdno"), row.get("ovrs_excg_cd")
            _instrument(symbol, actual_exchange)
            if actual_exchange != venue or symbol in seen or row.get("tr_crcy_cd") != "USD":
                raise DemoError("US VTS duplicate, foreign or inconsistent position")
            if row.get("loan_type_cd") not in {"", "00", None}:
                raise DemoError("US VTS margin positions are not supported")
            seen.add(symbol)
            quantity = _broker_number(row.get("ovrs_cblc_qty"), integer=True)
            available = _broker_number(row.get("ord_psbl_qty"), integer=True)
            if available > quantity:
                raise DemoError("US VTS sellable amount exceeds holdings")
            positions.append({"ticker": symbol, "exchange": venue, "quantity": quantity,
                "sellable_quantity": available, "market_value_usd": _broker_number(row.get("ovrs_stck_evlu_amt"))})
    capacity = client.buying_power(ticker=ticker, exchange=exchange, limit_price=limit_price)
    if capacity.get("tr_crcy_cd") != "USD":
        raise DemoError("Explicit USD-only cash capacity required")
    cash = _broker_number(capacity.get("ord_psbl_frcr_amt"))
    buying = min(cash, _broker_number(capacity.get("ovrs_ord_psbl_amt")))
    ingested = _clock(now_fn())
    if ingested < started:
        raise DemoError("US VTS account observation clock regressed")
    return {"environment": "demo", "account_scope": client.credentials.scope(), "market": "US", "currency": "USD",
            "complete": True, "observed_at": started.isoformat(), "ingested_at": ingested.isoformat(),
            "cash_usd": cash, "nav_usd": cash + sum(p["market_value_usd"] for p in positions),
            "nav_basis": "usd_capacity_plus_us_positions", "positions": positions,
            "cash_only_buying_power_usd": buying,
            "cash_only_buying_quantity": _broker_number(capacity.get("ord_psbl_qty"), integer=True),
            "capacity_ticker": ticker, "capacity_exchange": exchange, "capacity_limit_price": limit_price}


class USOrderJournal(DemoOrderJournal):
    """Reuse the request-before-transport UNKNOWN journal, with US report rules."""

    def __init__(self, path, client):
        super().__init__(path, client)
        self.db.execute("CREATE TABLE IF NOT EXISTS market_scope(market TEXT PRIMARY KEY)")
        rows = self.db.execute("SELECT market FROM market_scope").fetchall()
        if (rows and rows[0][0] != "US") or self.db.execute(
                "SELECT 1 FROM intents WHERE endpoint NOT IN ('order','order-rvsecncl') OR tr_id NOT IN ('VTTT1002U','VTTT1001U','VTTT1004U')").fetchone():
            self.close()
            raise DemoError("US execution requires a separate US journal")
        self.db.execute("INSERT OR IGNORE INTO market_scope VALUES ('US')")

    def submit(self, *, intent_id, ticker, exchange, side, quantity, limit_price,
               available_at, valid_until, now):
        if not stamp(available_at) <= stamp(now) < stamp(valid_until):
            raise DemoError("US intent expired or not yet available")
        _instrument(ticker, exchange)
        _integer(quantity, positive=True)
        price = _price(limit_price)
        if side not in {"BUY", "SELL"}:
            raise DemoError("Explicit US order side required")
        body = {**self.client._account(), "OVRS_EXCG_CD": exchange, "PDNO": ticker,
                "ORD_QTY": str(quantity), "OVRS_ORD_UNPR": price,
                "CTAC_TLNO": "", "MGCO_APTM_ODNO": "", "ORD_SVR_DVSN_CD": "0",
                "SLL_TYPE": "00" if side == "SELL" else "", "ORD_DVSN": "00"}
        return self._write_once(intent_id, "order", "VTTT1002U" if side == "BUY" else "VTTT1001U",
                                body, now, deadline=valid_until)

    def reconcile(self, *, intent_id, trade_date, reports=None):
        request = self.db.execute("SELECT * FROM requests WHERE id=?", (intent_id,)).fetchone()
        if not request or _clock(request["created_at"]).astimezone(NEW_YORK).strftime("%Y%m%d") != trade_date:
            raise DemoError("US report requires the original NY order date")
        broker_id = json.loads(request["response"]).get("broker_order_id")
        if not broker_id:
            return {"status": request["status"], "requires_manual_reconciliation": request["status"] == "UNKNOWN"}
        reports = self.client.orders(trade_date) if reports is None else reports
        if not isinstance(reports, list) or any(not isinstance(row, dict) for row in reports):
            self._block(intent_id, "invalid_us_order_rows")
            raise DemoError("US VTS invalid order rows")
        matches = [row for row in reports if str(row.get("odno")) == broker_id]
        if len(matches) != 1:
            self._block(intent_id, "missing_or_duplicate_us_order")
            return {"status": "UNRESOLVED", "requires_manual_reconciliation": True}
        row = matches[0]
        intent = self.db.execute("SELECT * FROM intents WHERE id=?", (intent_id,)).fetchone()
        if not intent or intent["endpoint"] != "order":
            self._block(intent_id, "missing_us_original_terms")
            raise DemoError("US original terms unavailable")
        terms = json.loads(intent["body"])
        try:
            ordered, filled, remaining = [_broker_number(row.get(key), integer=True)
                                         for key in ("ft_ord_qty", "ft_ccld_qty", "nccs_qty")]
            if (ordered != int(terms["ORD_QTY"]) or not 0 <= filled <= ordered
                    or not 0 <= remaining <= ordered - filled
                    or row.get("pdno") != terms["PDNO"] or row.get("ovrs_excg_cd") != terms["OVRS_EXCG_CD"]
                    or row.get("tr_crcy_cd") != "USD"
                    or row.get("sll_buy_dvsn_cd") != ("02" if intent["tr_id"] == "VTTT1002U" else "01")
                    or _broker_number(row.get("ft_ord_unpr3")) != float(terms["OVRS_ORD_UNPR"])):
                raise DemoError("US report conflicts with original terms")
            # An original order marked explicitly cancelled is evidence. Generic
            # 'complete' or a zero remainder alone never implies cancellation.
            cancelled = row.get("prcs_stat_name") in {"취소", "취소완료"} and row.get("rjct_rson") in {"", "0", "0000"}
            cancel = self.db.execute("SELECT response,status FROM requests WHERE id=?", ("cancel:" + intent_id,)).fetchone()
            if not cancelled and cancel and cancel["status"] == "ACKNOWLEDGED":
                cancel_id = json.loads(cancel["response"]).get("broker_order_id")
                children = [r for r in reports if str(r.get("odno")) == cancel_id and str(r.get("orgn_odno")) == broker_id]
                if len(children) == 1:
                    child = children[0]
                    cancelled = (child.get("rvse_cncl_dvsn") == "02"
                                 and child.get("prcs_stat_name") in {"완료", "취소완료"}
                                 and child.get("rjct_rson") in {"", "0", "0000"}
                                 and child.get("pdno") == terms["PDNO"]
                                 and child.get("ovrs_excg_cd") == terms["OVRS_EXCG_CD"]
                                 and child.get("tr_crcy_cd") == "USD"
                                 and _broker_number(child.get("ft_ord_qty"), integer=True) == ordered - filled)
            if cancelled and remaining:
                raise DemoError("Cancelled US order still has a remainder")
            status = ("FILLED" if filled == ordered else "CANCELLED" if cancelled else
                      "UNRESOLVED" if filled + remaining != ordered else "PARTIAL" if filled else "OPEN")
        except (DemoError, KeyError, TypeError, ValueError):
            self._block(intent_id, "us_terms_or_fill_mismatch")
            raise DemoError("US VTS invalid or inconsistent order report") from None
        receipt = {"status": status, "filled_qty": filled, "remaining_qty": remaining, "broker_order_id": broker_id}
        self.db.execute("BEGIN IMMEDIATE")
        try:
            previous = self.db.execute("SELECT * FROM order_state WHERE id=?", (intent_id,)).fetchone()
            if previous and (filled < previous["filled"] or (previous["status"] in {"FILLED", "CANCELLED"}
                    and (status != previous["status"] or filled != previous["filled"] or remaining != previous["remaining"]))):
                raise DemoError("US VTS reconciliation regressed")
            self.db.execute("INSERT INTO reconciliations VALUES (?,?,?)",
                            (intent_id, self.client._now().isoformat(), json.dumps(receipt)))
            if status == "UNRESOLVED":
                self._block(intent_id, "unresolved_us_fill_arithmetic")
            else:
                self.db.execute("INSERT OR REPLACE INTO order_state VALUES (?,?,?,?)", (intent_id, status, filled, remaining))
                self.db.execute("DELETE FROM reconciliation_issues WHERE id=?", (intent_id,))
            self.db.execute("COMMIT")
        except Exception:
            self.db.execute("ROLLBACK")
            self._block(intent_id, "us_reconciliation_regressed_or_failed")
            raise
        return receipt

    def cancel(self, *, intent_id, trade_date, now, reconciled_receipt=None, deadline=None):
        request = self.db.execute("SELECT created_at FROM requests WHERE id=?", (intent_id,)).fetchone()
        if (not request or _clock(request[0]).astimezone(NEW_YORK).strftime("%Y%m%d") != trade_date
                or _clock(now).astimezone(NEW_YORK).strftime("%Y%m%d") != trade_date
                or self.client._now().astimezone(NEW_YORK).strftime("%Y%m%d") != trade_date):
            raise DemoError("US DAY cancellation requires the original NY session")
        previous = self.db.execute("SELECT status,response FROM requests WHERE id=?", ("cancel:" + intent_id,)).fetchone()
        if previous:
            return {"status": previous["status"], **json.loads(previous["response"])}
        receipt = self.reconcile(intent_id=intent_id, trade_date=trade_date) if reconciled_receipt is None else reconciled_receipt
        if receipt.get("status") not in {"OPEN", "PARTIAL"} or receipt.get("remaining_qty", 0) <= 0:
            raise DemoError("No reconciled US cancellable remainder")
        intent = self.db.execute("SELECT body FROM intents WHERE id=?", (intent_id,)).fetchone()
        terms = json.loads(intent[0])
        body = {**self.client._account(), "OVRS_EXCG_CD": terms["OVRS_EXCG_CD"], "PDNO": terms["PDNO"],
                "ORGN_ODNO": receipt["broker_order_id"], "RVSE_CNCL_DVSN_CD": "02",
                "ORD_QTY": str(receipt["remaining_qty"]), "OVRS_ORD_UNPR": "0", "MGCO_APTM_ODNO": "", "ORD_SVR_DVSN_CD": "0"}
        return self._write_once("cancel:" + intent_id, "order-rvsecncl", "VTTT1004U", body, now, deadline=deadline)


class KisPaperUSBroker:
    """Explicit opt-in paper bridge, serialized across local cooperating runners.

    ``clock`` is a test seam. Production callers leave it unset; order submission
    has no caller-supplied historical ``now`` and cannot backdate a live request.
    """
    def __init__(self, path: Path | str, client: KisDemoUSClient, policy: USPaperOrderPolicy,
                 *, paper_enabled: bool = False, clock=None):
        if type(client) is not KisDemoUSClient or client.credentials.product_code != "01" or type(paper_enabled) is not bool or not isinstance(policy, USPaperOrderPolicy):
            raise DemoError("Dedicated VTS client, explicit policy and boolean opt-in required")
        self.path, self.client, self.policy = Path(path), client, policy
        self.enabled, self.clock = paper_enabled, clock or (lambda: datetime.now(timezone.utc))
        self.journal = USOrderJournal(self.path, client)
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
        policy_fields = asdict(policy)
        if not policy.allowed_tickers:
            policy_fields.pop("allowed_tickers")  # Preserve existing journal identities.
        encoded = json.dumps(policy_fields, sort_keys=True)
        with interprocess_file_lock(self.path.with_suffix(self.path.suffix + ".paper.lock")):
            previous = self.db.execute("SELECT policy FROM paper_policy WHERE scope=?", (client.credentials.scope(),)).fetchone()
            if previous and previous[0] != encoded:
                self.close()
                raise DemoError("Policy changed; use a separately named paper journal")
            self.db.execute("INSERT OR IGNORE INTO paper_policy VALUES (?,?)", (client.credentials.scope(), encoded))

    def close(self):
        self.journal.close()

    def _session(self, now):
        session = market_session_state(market="US", now_local=now)
        if session.get("source") != "exchange_calendars" or session.get("phase") != "regular" or session.get("is_open") is not True or not _clock(session.get("session_open")) <= now < _clock(session.get("session_close")):
            raise DemoError("Verified current US regular session required")
        return session

    def _validate(self, terms, signal, quote, account, now):
        if not self.enabled:
            raise DemoError("Paper trading requires explicit VTS opt-in")
        session = self._session(now)
        ticker, exchange, side, quantity, price = (terms[k] for k in ("ticker", "exchange", "side", "quantity", "limit_price"))
        if (ticker, exchange) not in self.policy.allowed_instruments and ticker not in self.policy.allowed_tickers:
            raise DemoError("Ticker is outside paper allowlist")
        if not all(isinstance(item, Mapping) for item in (signal, quote, account)):
            raise DemoError("Explicit signal, quote and account evidence required")
        expected = {"BUY": {"STARTER_NOW", "ADD_NOW"}, "SELL": {"REDUCE_NOW", "EXIT_NOW"}}
        if signal.get("ticker") != ticker or signal.get("execution_ready") is not True or signal.get("decision_now") not in expected[side]:
            raise DemoError("Existing execution verdict does not authorize this side")
        available, expiry = _clock(signal.get("available_at")), _clock(signal.get("valid_until"))
        if not available <= now < expiry or (now - available).total_seconds() >= self.policy.max_quote_age_seconds:
            raise DemoError("Signal future, stale or expired")
        if quote.get("ticker") != ticker or quote.get("exchange") != exchange or quote.get("provider") not in {"kis", "kis_quote", "kis_microstructure"} or quote.get("currency") != "USD" or quote.get("session") != "regular" or quote.get("execution_ready") is not True or quote.get("instrument_type") not in {"STOCK", "ETF"}:
            raise DemoError("Verified same-symbol KIS USD regular quote required")
        _fresh(quote, now=now, seconds=self.policy.max_quote_age_seconds)
        last = _number(quote.get("last_price"), positive=True)
        if abs(price / last - 1) * 10000 > self.policy.max_limit_distance_bps + 1e-8:
            raise DemoError("Limit violates US quote collar")
        if account.get("environment") != "demo" or account.get("account_scope") != self.client.credentials.scope() or account.get("complete") is not True or account.get("currency") != "USD" or account.get("market") != "US":
            raise DemoError("Complete account from the same VTS scope required")
        _fresh(account, now=now, seconds=self.policy.max_account_age_seconds)
        nav = _number(account.get("nav_usd"), positive=True)
        cash = _number(account.get("cash_usd"))
        rows = account.get("positions")
        if not isinstance(rows, list):
            raise DemoError("Explicit complete positions list required")
        positions = {}
        for row in rows:
            if not isinstance(row, Mapping) or not isinstance(row.get("ticker"), str) or not re.fullmatch(r"[A-Z][A-Z0-9.]{0,9}", row["ticker"]) or row.get("exchange") not in EXCHANGES or row["ticker"] in positions:
                raise DemoError("Duplicate or invalid account position")
            held, sellable = _integer(row.get("quantity")), _integer(row.get("sellable_quantity"))
            if sellable > held:
                raise DemoError("Sellable amount exceeds holdings")
            if row["ticker"] == ticker and row["exchange"] != exchange:
                raise DemoError("US held symbol exchange conflicts with order exchange")
            _number(row.get("market_value_usd"))
            positions[row["ticker"]] = row
        notional = quantity * price
        if notional > self.policy.max_order_usd:
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
            if _clock(row["created_at"]).astimezone(NEW_YORK).date() == now.astimezone(NEW_YORK).date():
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
            if bought + notional > self.policy.max_daily_buy_usd:
                raise DemoError("Daily paper buy limit exceeded")
            if account.get("capacity_ticker") != ticker or account.get("capacity_exchange") != exchange or account.get("capacity_limit_price") != price:
                raise DemoError("Cash-only capacity must match ticker and limit")
            capacity = _number(account.get("cash_only_buying_power_usd"))
            capacity_qty = _integer(account.get("cash_only_buying_quantity"))
            reserve = (reserved_buy + notional) * (1 + self.policy.reserve_cost_bps / 10000)
            if quantity > capacity_qty or reserve > min(cash - self.policy.cash_floor_usd, capacity):
                raise DemoError("Cash-only capacity or reserved cash floor exceeded")
            position_value = _number(positions.get(ticker, {}).get("market_value_usd", 0))
            if position_value + held_symbol_reserve + notional > nav * self.policy.max_position_fraction:
                raise DemoError("Paper concentration limit exceeded")
        elif quantity + reserved_sell > positions.get(ticker, {}).get("sellable_quantity", 0):
            # Protective reductions ignore buy cash/concentration caps but never
            # create a short sale or bypass explicit sell/order/session limits.
            raise DemoError("Sell exceeds unreserved sellable holdings")
        return min(expiry, _clock(session["session_close"]))

    def submit(self, *, intent_id: str, ticker: str, exchange: str, side: str, quantity: int, limit_price: float,
               signal: Mapping, quote: Mapping, account: Mapping) -> dict:
        _stable(intent_id)
        signal_id = _stable(signal.get("signal_id") if isinstance(signal, Mapping) else None)
        _instrument(ticker, exchange)
        _integer(quantity, positive=True)
        _price(limit_price)
        if side not in {"BUY", "SELL"}:
            raise DemoError("Explicit BUY or SELL required")
        terms = {"ticker": ticker, "exchange": exchange, "side": side, "quantity": quantity, "limit_price": float(limit_price)}
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
            if self.db.execute("SELECT 1 FROM requests WHERE status='UNKNOWN'").fetchone() or self.db.execute("SELECT 1 FROM reconciliation_issues").fetchone():
                raise DemoError("Resolve ambiguous US VTS request before another submission")
            if not self.db.execute("SELECT 1 FROM lifecycle_events WHERE kind='ACCOUNT_SEED' AND mode='demo'").fetchone():
                append_lifecycle_event(self.db, event_id="account:demo:" + self.client.credentials.scope(),
                    signal_id="account:demo:" + self.client.credentials.scope(), kind="ACCOUNT_SEED", mode="demo",
                    occurred_at=account["observed_at"], available_at=account["ingested_at"], ingested_at=now.isoformat(),
                    payload={"cash": account["cash_usd"], "currency": "USD",
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
        raw = str(row.get("dmst_ord_dt", "")) + str(row.get("thco_ord_tmd", ""))
        try:
            if not re.fullmatch(r"[0-9]{14}", raw):
                raise ValueError()
            ordered = datetime.strptime(raw, "%Y%m%d%H%M%S").replace(tzinfo=SEOUL)
        except ValueError:
            raise DemoError("Missing or invalid VTS order date/time") from None
        created = _clock(request["created_at"])
        if ordered < created.replace(microsecond=0) or ordered > now or ordered.astimezone(NEW_YORK).date() != created.astimezone(NEW_YORK).date():
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
            return {"status": request["status"], "mode": "demo", "live_orders_enabled": False,
                    "requires_manual_reconciliation": request["status"] == "UNKNOWN"}
        trade_date = _clock(request["created_at"]).astimezone(NEW_YORK).strftime("%Y%m%d")
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
            result["fill_notional"] = execution_notional(report, result.get("filled_qty", 0), terms, market="US")
            ingested_at = _clock(self.clock())
            if ingested_at < received_at:
                raise DemoError("VTS ingestion clock precedes the received observation")
        except DemoError:
            self.journal._block(intent_id, "unverified_paper_reconciliation")
            raise
        # A current order report becomes known only after the response arrives.
        # Starting the request does not make its later contents available then.
        result = {**result, "mode": "demo", "live_orders_enabled": False, "observed_at": received_at.isoformat(),
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
                return {"status": previous["status"], **json.loads(previous["response"]), "mode": "demo",
                        "duplicate": True, "live_orders_enabled": False}
            if not self.enabled:
                raise DemoError("Paper cancellation requires explicit VTS opt-in")
            now = _clock(self.clock())
            session = self._session(now)
            result = self._reconcile(intent_id)
            # Cancel only the broker-observed remaining quantity. An ACK is
            # not cancellation confirmation; a later order report must prove it.
            deadline = min(now + timedelta(seconds=120), _clock(session["session_close"]))
            response = self.journal.cancel(intent_id=intent_id, trade_date=now.astimezone(NEW_YORK).strftime("%Y%m%d"),
                now=now.isoformat(), reconciled_receipt=result, deadline=deadline.isoformat())
            return {**response, "mode": "demo", "cancellation_confirmed": False, "live_orders_enabled": False}

    def status(self) -> dict:
        requests = [dict(row) for row in self.db.execute("""SELECT r.id,r.status,r.created_at,
            s.status AS reconciled_status,s.filled,s.remaining FROM requests r
            LEFT JOIN order_state s ON r.id=s.id ORDER BY r.created_at,r.id""")]
        return {"schema": SCHEMA, "mode": "demo", "host": DEMO_HOST,
                "market": "US", "currency": "USD", "paper_writes_enabled": self.enabled, "live_orders_enabled": False,
                "requests": requests, "unresolved_count": self.db.execute("SELECT count(*) FROM reconciliation_issues").fetchone()[0],
                "observed_at": _clock(self.clock()).isoformat()}
