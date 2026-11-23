"""Shared broker contract and a fenced, read/reconcile-first paper dispatcher."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re
import sqlite3
from typing import Protocol

from tradingagents.atomic_io import interprocess_file_lock

from .experiments import _stamp


@dataclass(frozen=True)
class BrokerCapabilities:
    markets: tuple[str, ...]
    modes: tuple[str, ...]
    fractional: bool
    websocket: bool
    rest_interval_seconds: int
    subscription_limit: int


CAPABILITIES = {
    "backtest": BrokerCapabilities(("KR", "US"), ("fixture",), False, False, 0, 0),
    "local": BrokerCapabilities(("KR", "US"), ("paper", "fixture"), False, False, 0, 0),
    "kis_vts": BrokerCapabilities(("KR", "US"), ("paper", "fixture"), False, True, 1, 41),
    "alpaca_paper": BrokerCapabilities(("US",), ("paper", "fixture"), True, True, 0, 0),
    "kis_live": BrokerCapabilities(("KR", "US"), ("fixture",), False, True, 1, 0),
}


def subscription_budget(*, pinned: list[str], optional: list[str], limit: int = 41) -> tuple[str, ...]:
    """Reserve capacity for account notices, open orders and owned positions."""
    required = tuple(dict.fromkeys(pinned))
    if type(limit) is not int or not 1 <= limit <= 41 or len(required) > limit:
        raise ValueError("Broker subscriptions cannot cover all required evidence")
    if any(not isinstance(item, str) or not item.strip() for item in (*required, *optional)):
        raise ValueError("Invalid subscription key")
    return tuple(dict.fromkeys((*required, *optional)))[:limit]


def _money(value: str) -> Decimal:
    try:
        result = Decimal(value)
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError("Expected finite decimal amount") from exc
    if not result.is_finite() or result < 0:
        raise ValueError("Expected finite nonnegative decimal amount")
    return result


def _clock_floor(local, provider_timestamp):
    """Compare a local instant at the precision actually reported by the broker."""
    match = re.search(r"T\d{2}:\d{2}:\d{2}(?:[.,](\d{1,6}))?", provider_timestamp)
    if not match:
        return local
    digits = len(match[1] or "")
    step = 10 ** (6 - digits)
    return local.replace(microsecond=local.microsecond // step * step)


@dataclass(frozen=True)
class Intent:
    id: str
    ticker: str
    side: str
    quantity: str
    limit: str
    currency: str
    expires_at: str


@dataclass(frozen=True)
class Account:
    scope: str
    currency: str
    observed_at: str
    settled_cash: str
    sellable: dict[str, str]


@dataclass(frozen=True)
class ExecutionFill:
    id: str
    quantity: str
    native_price: str
    currency: str
    occurred_at: str


@dataclass(frozen=True)
class Order:
    scope: str
    client_id: str
    order_id: str
    status: str
    filled_quantity: str
    observed_at: str
    fills: tuple[ExecutionFill, ...] = ()


class BrokerAdapter(Protocol):
    kind: str
    mode: str
    market: str
    scope: str

    def account(self) -> Account: ...
    def submit(self, intent: Intent) -> Order: ...
    def find(self, client_id: str) -> Order | None: ...


class BrokerDispatcher:
    """Use one journal and lock per account. Unknown submissions only reconcile."""

    def __init__(self, path: Path, adapter: BrokerAdapter, *, clock=None):
        capability = CAPABILITIES.get(adapter.kind)
        if (capability is None or adapter.mode not in capability.modes or adapter.market not in capability.markets
                or adapter.kind == "kis_live" or not adapter.scope):
            raise ValueError("Only admitted, isolated broker adapters may dispatch")
        self._broker = adapter
        self._capability = capability
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        path = path.resolve()
        self._lock = path.with_suffix(".dispatch.lock")
        path.parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(path, timeout=20)
        self._db.row_factory = sqlite3.Row
        self._db.executescript("""
            CREATE TABLE IF NOT EXISTS broker_scope (
                id INTEGER PRIMARY KEY CHECK(id=1), scope TEXT NOT NULL, kind TEXT NOT NULL,
                mode TEXT NOT NULL, market TEXT NOT NULL, epoch INTEGER NOT NULL,
                owner TEXT, lease_expires TEXT, next_rest TEXT
            );
            CREATE TABLE IF NOT EXISTS dispatch_intents(
                id TEXT PRIMARY KEY, payload TEXT NOT NULL, status TEXT NOT NULL, order_id TEXT UNIQUE,
                filled TEXT NOT NULL DEFAULT '0', observed_at TEXT, submitted_at TEXT, last_fill_seen_at TEXT
            );
            CREATE TABLE IF NOT EXISTS dispatch_observations(
                intent_id TEXT NOT NULL, observed_at TEXT NOT NULL, payload TEXT NOT NULL,
                PRIMARY KEY(intent_id, observed_at)
            );
            CREATE TABLE IF NOT EXISTS dispatch_fills(
                fill_id TEXT PRIMARY KEY, intent_id TEXT NOT NULL, payload TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS dispatch_observation_events(
                intent_id TEXT NOT NULL, observed_at TEXT NOT NULL, payload TEXT NOT NULL,
                PRIMARY KEY(intent_id, observed_at, payload)
            );
        """)
        binding = (adapter.scope, adapter.kind, adapter.mode, adapter.market)
        with self._db:
            self._db.execute("BEGIN IMMEDIATE")
            columns = {row[1] for row in self._db.execute("PRAGMA table_info(dispatch_intents)")}
            if "submitted_at" not in columns:
                self._db.execute("ALTER TABLE dispatch_intents ADD COLUMN submitted_at TEXT")
            if "last_fill_seen_at" not in columns:
                self._db.execute("ALTER TABLE dispatch_intents ADD COLUMN last_fill_seen_at TEXT")
                self._db.execute("UPDATE dispatch_intents SET last_fill_seen_at=observed_at WHERE CAST(filled AS REAL)>0")
            self._db.execute("INSERT OR IGNORE INTO dispatch_observation_events SELECT * FROM dispatch_observations")
            self._db.execute("INSERT OR IGNORE INTO broker_scope (id,scope,kind,mode,market,epoch) VALUES (1,?,?,?,?,0)",
                             binding)
            if tuple(self._db.execute("SELECT scope,kind,mode,market FROM broker_scope").fetchone()) != binding:
                raise ValueError("Broker journal belongs to a different account or transport")

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self._db.close()

    def _now(self):
        return _stamp(self._clock())

    def claim(self, owner: str, *, seconds=30) -> int:
        if not owner or type(seconds) is not int or not 1 <= seconds <= 120:
            raise ValueError("Invalid lease")
        with interprocess_file_lock(self._lock), self._db:
            self._db.execute("BEGIN IMMEDIATE")
            now = self._now()
            current = self._db.execute("SELECT * FROM broker_scope").fetchone()
            if current["lease_expires"] and _stamp(current["lease_expires"]) > now:
                if owner != current["owner"]:
                    raise RuntimeError("Another producer holds the account lease")
                epoch = current["epoch"]
            else:
                epoch = current["epoch"] + 1
                self._db.execute("UPDATE dispatch_intents SET status='UNKNOWN' WHERE status='DISPATCHING'")
            self._db.execute("UPDATE broker_scope SET epoch=?, owner=?, lease_expires=? WHERE id=1",
                             (epoch, owner, (now + timedelta(seconds=seconds)).isoformat()))
        return epoch

    def _fence(self, owner, epoch):
        current = self._db.execute("SELECT * FROM broker_scope").fetchone()
        if (not current["lease_expires"] or _stamp(current["lease_expires"]) <= self._now()
                or current["epoch"] != epoch or current["owner"] != owner):
            raise RuntimeError("Account lease is stale")
        return current

    def _reserve_rest(self, owner, epoch):
        now = self._now()
        with self._db:
            self._db.execute("BEGIN IMMEDIATE")
            current = self._fence(owner, epoch)
            if current["next_rest"] and _stamp(current["next_rest"]) > now:
                raise RuntimeError("REST budget exhausted until the next account slot")
            available = now + timedelta(seconds=self._capability.rest_interval_seconds)
            self._db.execute("UPDATE broker_scope SET next_rest=? WHERE id=1", (available.isoformat(),))

    def dispatch(self, owner, epoch, intent: Intent, account: Account, *, max_age_seconds=30):
        quantity, limit = _money(intent.quantity), _money(intent.limit)
        if (not intent.id or not intent.ticker or intent.side not in ("BUY", "SELL") or not quantity or not limit
                or (quantity % 1 and not self._capability.fractional) or account.scope != self._broker.scope
                or account.currency != intent.currency or intent.currency != self._native_currency()
                or type(max_age_seconds) is not int or not 1 <= max_age_seconds <= 120):
            raise ValueError("Intent or account cannot be submitted")
        payload = json.dumps(asdict(intent), sort_keys=True)
        with interprocess_file_lock(self._lock):
            self._fence(owner, epoch)
            previous = self._db.execute("SELECT * FROM dispatch_intents WHERE id=?", (intent.id,)).fetchone()
            if previous is not None:
                if previous["payload"] != payload:
                    raise ValueError("Intent ID already belongs to different terms")
                return previous["status"]
            now, observed = self._now(), _stamp(account.observed_at)
            if not timedelta(0) <= now - observed <= timedelta(seconds=max_age_seconds) or _stamp(intent.expires_at) <= now:
                raise ValueError("Account proof or intent is stale")
            last_fill = self._db.execute("SELECT MAX(last_fill_seen_at) FROM dispatch_intents").fetchone()[0]
            if last_fill and observed <= _stamp(last_fill):
                raise ValueError("Account proof must follow the latest fill")
            rows = self._db.execute("SELECT payload,status,filled FROM dispatch_intents WHERE status NOT IN ('FILLED','CANCELED','REJECTED')").fetchall()
            reserved = Decimal(0)
            for row in rows:
                if row["status"] in {"DISPATCHING", "UNKNOWN"}:
                    raise RuntimeError("Reconcile the unknown submission before dispatch")
                other = Intent(**json.loads(row["payload"]))
                if other.side == intent.side and (intent.side == "BUY" or intent.ticker == other.ticker):
                    pending = _money(other.quantity) - _money(row["filled"])
                    reserved += pending * _money(other.limit) if intent.side == "BUY" else pending
            available = _money(account.settled_cash) if intent.side == "BUY" else _money(account.sellable.get(intent.ticker, "0"))
            required = quantity * limit if intent.side == "BUY" else quantity
            if required + reserved > available:
                raise ValueError("Intent exceeds available inventory or settled cash")
            self._reserve_rest(owner, epoch)
            with self._db:
                self._db.execute("INSERT INTO dispatch_intents (id,payload,status,submitted_at) VALUES (?,?,'DISPATCHING',?)",
                                 (intent.id, payload, self._now().isoformat()))
            try:
                order = self._broker.submit(intent)
                return self._accept(intent.id, order)
            except Exception:
                with self._db:
                    self._db.execute("UPDATE dispatch_intents SET status='UNKNOWN' WHERE id=?", (intent.id,))
                return "UNKNOWN"

    def reconcile(self, owner, epoch, intent_id):
        with interprocess_file_lock(self._lock):
            return self._reconcile(owner, epoch, intent_id)

    def _reconcile(self, owner, epoch, intent_id):
        if self._db.execute("SELECT 1 FROM dispatch_intents WHERE id=?", (intent_id,)).fetchone() is None:
            raise ValueError("Unknown intent cannot be reconciled")
        self._reserve_rest(owner, epoch)
        order = self._broker.find(intent_id)
        return "UNKNOWN" if order is None else self._accept(intent_id, order)

    def reconcile_broker_hint(self, owner, epoch, *, scope, market, order_id):
        """Resolve a scoped WS hint through a known order and the shared REST slot."""
        if scope != self._broker.scope or market != self._broker.market:
            raise ValueError("Hint has the wrong account or market scope")
        with interprocess_file_lock(self._lock):
            self._fence(owner, epoch)
            row = self._db.execute("SELECT id FROM dispatch_intents WHERE order_id=?", (order_id,)).fetchone()
            return self._reconcile(owner, epoch, row[0]) if row else "ORDER_NOT_BOUND"

    def account_snapshot(self, owner, epoch):
        """Read a native-currency account from the same lane used for writes and reconciliation."""
        with interprocess_file_lock(self._lock):
            self._reserve_rest(owner, epoch)
            snapshot = self._broker.account()
            now, at = self._now(), _stamp(snapshot.observed_at)
            if (snapshot.scope != self._broker.scope or snapshot.currency != self._native_currency()
                    or not timedelta() <= now - at <= timedelta(seconds=30)):
                raise ValueError("Broker account evidence has invalid scope, currency, or age")
            _money(snapshot.settled_cash)
            for quantity in snapshot.sellable.values():
                _money(quantity)
            return snapshot

    def _native_currency(self):
        return "KRW" if self._broker.market == "KR" else "USD"

    def notice(self, owner, epoch, order: Order):
        """Apply order evidence fetched by an authenticated REST reconciliation."""
        with interprocess_file_lock(self._lock):
            self._fence(owner, epoch)
            return self._accept(order.client_id, order)

    def _accept(self, intent_id, order: Order):
        status = order.status
        if (order.scope != self._broker.scope or order.client_id != intent_id or not order.order_id
                or status not in {"OPEN", "PARTIAL", "FILLED", "CANCELED", "REJECTED"}):
            raise ValueError("Order evidence does not match the account or intent")
        observed = _stamp(order.observed_at)
        if observed > self._now():
            raise ValueError("Future broker evidence")
        row = self._db.execute("SELECT * FROM dispatch_intents WHERE id=?", (intent_id,)).fetchone()
        if row is None or (row["order_id"] and row["order_id"] != order.order_id):
            raise ValueError("Unbound broker order")
        submitted = _stamp(row["submitted_at"]) if row["submitted_at"] else None
        if submitted is not None and observed < _clock_floor(submitted, order.observed_at):
            raise ValueError("Broker evidence predates the durable submission clock")
        quantity = _money(json.loads(row["payload"])["quantity"])
        filled = _money(order.filled_quantity)
        if (filled > quantity or (status == "FILLED") != (filled == quantity)
                or (status == "PARTIAL" and not filled) or (status in {"OPEN", "REJECTED"} and filled)):
            raise ValueError("Order fill is inconsistent with its requested quantity")
        data = asdict(order)
        data["observed_at"] = observed.isoformat()
        data["filled_quantity"] = str(filled)
        data["fills"] = sorted(data["fills"], key=lambda fill: fill["id"])
        encoded = json.dumps(data, sort_keys=True)
        if row["observed_at"] and observed <= _stamp(row["observed_at"]):
            old = self._db.execute("SELECT 1 FROM dispatch_observation_events WHERE intent_id=? AND observed_at=? AND payload=?",
                                   (intent_id, observed.isoformat(), encoded)).fetchone()
            if old:
                return row["status"]
            if observed < _stamp(row["observed_at"]):
                raise ValueError("Conflicting or out-of-order broker evidence")
        previous_fill = _money(row["filled"])
        same_execution = (status, filled) == (row["status"], previous_fill)
        if filled < previous_fill or (row["status"] in {"FILLED", "CANCELED", "REJECTED"} and not same_execution):
            raise ValueError("Broker execution state cannot regress")
        with self._db:
            self._db.execute("BEGIN IMMEDIATE")
            for fill in order.fills:
                self._record_fill(intent_id, submitted, observed, fill)
            evidence = self._db.execute("SELECT payload FROM dispatch_fills WHERE intent_id=?", (intent_id,))
            cumulative = sum((_money(json.loads(row[0])["quantity"]) for row in evidence), Decimal())
            if cumulative != filled:
                raise ValueError("Order cumulative quantity lacks matching durable fill identifiers")
            self._db.execute("INSERT INTO dispatch_observation_events VALUES (?,?,?)",
                             (intent_id, observed.isoformat(), encoded))
            last_fill = observed.isoformat() if filled > previous_fill else row["last_fill_seen_at"]
            self._db.execute("UPDATE dispatch_intents SET status=?,order_id=?,filled=?,observed_at=?,last_fill_seen_at=? WHERE id=?",
                             (status, order.order_id, str(filled), observed.isoformat(), last_fill, intent_id))
        return status

    def _record_fill(self, intent_id, submitted, observed, fill):
        if (not isinstance(fill.id, str) or not fill.id.strip() or fill.currency != self._native_currency()
                or not _money(fill.quantity) or not _money(fill.native_price)
                or submitted is None or not _clock_floor(submitted, fill.occurred_at) <= _stamp(fill.occurred_at) <= observed):
            raise ValueError("Broker fill is missing native amount, time, or stable identity")
        encoded = json.dumps(asdict(fill), sort_keys=True)
        previous = self._db.execute("SELECT intent_id,payload FROM dispatch_fills WHERE fill_id=?", (fill.id,)).fetchone()
        if previous is not None and tuple(previous) != (intent_id, encoded):
            raise ValueError("Broker fill ID is already bound to different evidence")
        self._db.execute("INSERT OR IGNORE INTO dispatch_fills VALUES (?,?,?)", (fill.id, intent_id, encoded))
