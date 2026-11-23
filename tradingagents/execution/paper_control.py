"""Signed controls and fenced operator handoff for a separate paper journal."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import hmac
import json
from pathlib import Path
import re
import sqlite3

from .experiments import _stamp

_COMMAND_LEVEL = {"status": "observe", "positions": "observe", "halt": "halt", "flatten": "flatten"}
_FIELDS = {"actor", "action", "scope", "mode", "nonce", "expires_at"}


def _encoded(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sign_paper_control(secret, payload):
    return hmac.new(secret, b"paper-control-v1:" + _encoded(payload).encode(), hashlib.sha256).hexdigest()


def _number(value):
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("Invalid isolated position or quote value") from exc
    if not result.is_finite() or result <= 0:
        raise ValueError("Positive isolated position or quote value required")
    return result


class PaperControlLedger:
    def __init__(self, path: Path, *, scope: str, market: str, secret: bytes, rights, clock=None):
        if not scope or market not in {"KR", "US"} or not isinstance(secret, bytes) or len(secret) < 32:
            raise ValueError("An explicit paper scope, market and signing key are required")
        self._scope, self._market, self._key = scope, market, secret
        self._rights = {permission: frozenset(actors) for permission, actors in rights.items()}
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        path.parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(path, timeout=20)
        self._db.row_factory = sqlite3.Row
        self._db.executescript("""
            CREATE TABLE IF NOT EXISTS paper_control_state(
                id INTEGER PRIMARY KEY CHECK(id=1), scope TEXT NOT NULL, market TEXT NOT NULL,
                halted INTEGER NOT NULL DEFAULT 0, owner TEXT, epoch INTEGER NOT NULL DEFAULT 0, expires_at TEXT
            );
            CREATE TABLE IF NOT EXISTS paper_control_commands(
                nonce TEXT PRIMARY KEY, digest TEXT NOT NULL, result TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS paper_flatten_batches(
                id INTEGER PRIMARY KEY CHECK(id=1), nonce TEXT NOT NULL UNIQUE, state TEXT NOT NULL,
                payload TEXT NOT NULL, execution_receipt TEXT
            );
        """)
        with self._db:
            self._db.execute("INSERT OR IGNORE INTO paper_control_state(id,scope,market) VALUES (1,?,?)", (scope, market))
            row = self._state()
            if (row["scope"], row["market"]) != (scope, market):
                raise ValueError("Paper controls belong to another isolated scope")

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self._db.close()

    def _now(self):
        return _stamp(self._clock())

    def _state(self):
        return self._db.execute("SELECT * FROM paper_control_state WHERE id=1").fetchone()

    def claim(self, writer, *, seconds=30):
        if not isinstance(writer, str) or not writer or type(seconds) is not int or not 1 <= seconds <= 120:
            raise ValueError("Unique writer and a bounded paper lease required")
        with self._db:
            self._db.execute("BEGIN IMMEDIATE")
            row, now = self._state(), self._now()
            active = row["expires_at"] and now < _stamp(row["expires_at"])
            if active and row["owner"] != writer:
                raise RuntimeError("Another paper writer owns the lease")
            epoch = row["epoch"] if active else row["epoch"] + 1
            self._db.execute("UPDATE paper_control_state SET owner=?,epoch=?,expires_at=? WHERE id=1",
                             (writer, epoch, (now + timedelta(seconds=seconds)).isoformat()))
            return epoch

    def _fence(self, writer, epoch):
        row = self._state()
        if (row["owner"] != writer or row["epoch"] != epoch or not row["expires_at"]
                or _stamp(row["expires_at"]) <= self._now()):
            raise RuntimeError("Stale paper writer")
        return row

    def execute(self, request, signature, *, actor, writer, epoch, snapshot=None, quotes=None):
        if not isinstance(request, dict) or set(request) != _FIELDS or not isinstance(signature, str):
            raise ValueError("Invalid signed command")
        action = request["action"]
        level = _COMMAND_LEVEL.get(action) if isinstance(action, str) else None
        nonce = request["nonce"]
        if (level is None or not isinstance(actor, str) or request["actor"] != actor or actor not in self._rights.get(level, ())
                or request["mode"] != "isolated_paper" or request["scope"] != self._scope
                or not isinstance(nonce, str) or not re.fullmatch(r"[A-Za-z0-9_-]{16,64}", nonce)
                or not hmac.compare_digest(signature, sign_paper_control(self._key, request))):
            raise ValueError("Unauthorized paper control")
        digest = hashlib.sha256(_encoded(request).encode()).hexdigest()
        with self._db:
            self._db.execute("BEGIN IMMEDIATE")
            now = self._now()
            row = self._fence(writer, epoch)
            expiry = _stamp(request["expires_at"])
            if not timedelta() < expiry - now <= timedelta(minutes=2):
                raise ValueError("Paper control command expired or outside its window")
            previous = self._db.execute("SELECT digest,result FROM paper_control_commands WHERE nonce=?", (nonce,)).fetchone()
            if previous:
                if previous["digest"] != digest:
                    raise ValueError("Paper command nonce is already bound")
                return json.loads(previous["result"])
            result = self._execute(action, row, request, snapshot, quotes, now, expiry)
            self._db.execute("INSERT INTO paper_control_commands VALUES (?,?,?)", (nonce, digest, _encoded(result)))
        return result

    def _execute(self, action, row, request, snapshot, quotes, now, expiry):
        result = {"mode": "isolated_paper", "action": action, "halted": bool(row["halted"]),
                  "live_order_authority": False}
        batch = self._db.execute("SELECT nonce,state,payload FROM paper_flatten_batches WHERE id=1").fetchone()
        if action == "status":
            return result | {"flatten_status": batch["state"] if batch else "NONE"}
        if action == "halt":
            self._db.execute("UPDATE paper_control_state SET halted=1 WHERE id=1")
            return result | {"halted": True}
        if action == "flatten" and not row["halted"]:
            raise ValueError("Flatten requires a halt and an unused isolated flatten lane")
        prior_intents = []
        if action == "flatten" and batch:
            prior_intents = json.loads(batch["payload"])["paper_intents"]
            has_terminal_proof = isinstance(snapshot, dict) and "terminal_flatten_orders" in snapshot
            if batch["state"] != "READY" or (not has_terminal_proof and any(
                now < _stamp(item["expires_at"]) for item in prior_intents
            )):
                raise ValueError("Flatten requires an unused or expired isolated flatten lane")
        positions, sellable = self._positions(snapshot, now)
        if action == "positions":
            return result | {"positions": positions}
        if snapshot.get("pending_orders_reconciled_empty") is not True:
            raise ValueError("Pending paper orders must be cancelled and reconciled first")
        if positions != sellable:
            raise ValueError("Flatten requires all owned paper shares to be sellable")
        recovered_ids = {}
        if batch and "terminal_flatten_orders" in snapshot:
            recovered_ids = self._remaining_intents(prior_intents, positions, snapshot["terminal_flatten_orders"], now)
        elif batch:
            unsubmitted = snapshot.get("unsubmitted_intent_ids")
            if (not isinstance(unsubmitted, list) or not all(isinstance(item, str) for item in unsubmitted)
                    or sorted(unsubmitted) != sorted(item["id"] for item in prior_intents)
                    or positions != {item["ticker"]: item["quantity"] for item in prior_intents}):
                raise ValueError("Expired flatten requires exact unsubmitted intent and inventory proof")
            recovered_ids = {item["ticker"]: item["id"] for item in prior_intents}
        if not isinstance(quotes, dict):
            raise ValueError("Fresh paper quotes are required")
        intents = []
        batch_nonce = batch["nonce"] if batch else request["nonce"]
        for ticker, quantity in sorted(positions.items()):
            quote = quotes.get(ticker, {})
            if (quote.get("scope") != self._scope or quote.get("market") != self._market
                    or quote.get("currency") != ("KRW" if self._market == "KR" else "USD")
                    or quote.get("regular_executable") is not True
                    or not timedelta() <= now - _stamp(quote.get("observed_at")) <= timedelta(seconds=15)):
                raise ValueError("Flatten quote is not fresh and scoped")
            identity = recovered_ids.get(ticker) or hashlib.sha256((batch_nonce + ":" + ticker).encode()).hexdigest()
            intents.append({"id": identity, "ticker": ticker, "side": "SELL", "quantity": quantity,
                            "limit": str(_number(quote.get("bid"))), "currency": quote["currency"],
                            "expires_at": expiry.isoformat()})
        record = result | {"flatten_status": "READY" if intents else "ALREADY_FLAT",
                           "paper_intents": intents, "flatten_nonce": batch_nonce, "requires_broker_revalidation": True}
        if batch:
            self._db.execute("UPDATE paper_flatten_batches SET state=?,payload=? WHERE id=1",
                             (record["flatten_status"], _encoded(record)))
        else:
            self._db.execute("INSERT INTO paper_flatten_batches(id,nonce,state,payload) VALUES (1,?,?,?)",
                             (batch_nonce, record["flatten_status"], _encoded(record)))
        return record

    def _remaining_intents(self, previous, positions, evidence, now):
        if not isinstance(evidence, dict) or set(evidence) != {item["id"] for item in previous}:
            raise ValueError("Partial recovery requires exact terminal broker proof")
        quantities, identities = {}, {}
        for item in previous:
            record = evidence[item["id"]]
            if not isinstance(record, dict) or set(record) != {"status", "filled_quantity", "receipt_id"}:
                raise ValueError("Partial recovery requires an accountable terminal receipt")
            status = record["status"]
            if (not isinstance(status, str) or status not in {"CANCELED", "FILLED", "REJECTED", "UNSUBMITTED"}
                    or not isinstance(record["receipt_id"], str) or not record["receipt_id"].strip()):
                raise ValueError("Partial recovery requires an accountable terminal receipt")
            if status == "UNSUBMITTED" and now < _stamp(item["expires_at"]):
                raise ValueError("Unsubmitted flatten intent must expire before renewal")
            try:
                if type(record["filled_quantity"]) not in (str, int):
                    raise ValueError("Explicit terminal quantity required")
                filled = Decimal(record["filled_quantity"])
            except (InvalidOperation, TypeError, ValueError) as exc:
                raise ValueError("Invalid terminal filled quantity") from exc
            requested = _number(item["quantity"])
            if (not filled.is_finite() or not 0 <= filled <= requested or filled % 1
                    or (status == "FILLED") != (filled == requested)
                    or (status in {"REJECTED", "UNSUBMITTED"} and filled)):
                raise ValueError("Invalid terminal filled quantity")
            remaining = requested - filled
            if remaining:
                ticker = item["ticker"]
                quantities[ticker] = str(remaining.quantize(Decimal("1")))
                source = _encoded([item["id"], record["receipt_id"], quantities[ticker]])
                identities[ticker] = item["id"] if status == "UNSUBMITTED" else hashlib.sha256(source.encode()).hexdigest()
        if positions != quantities:
            raise ValueError("Current inventory does not match the verified unfilled quantity")
        return identities

    def _positions(self, snapshot, now):
        if (not isinstance(snapshot, dict) or snapshot.get("mode") != "isolated_paper"
                or snapshot.get("scope") != self._scope or snapshot.get("market") != self._market
                or snapshot.get("reconciled") is not True
                or not timedelta() <= now - _stamp(snapshot.get("observed_at")) <= timedelta(seconds=30)
                or not isinstance(snapshot.get("owned"), dict) or not isinstance(snapshot.get("sellable"), dict)):
            raise ValueError("A fresh reconciled paper position snapshot is required")
        owned, sellable = (self._quantities(snapshot[field]) for field in ("owned", "sellable"))
        if any(ticker not in owned or Decimal(quantity) > Decimal(owned[ticker]) for ticker, quantity in sellable.items()):
            raise ValueError("Sellable paper shares exceed owned shares")
        return owned, sellable

    def _quantities(self, values):
        positions = {}
        for ticker, quantity in values.items():
            if not re.fullmatch(r"[A-Z0-9.-]{1,16}", ticker):
                raise ValueError("Invalid canonical paper ticker")
            qty = _number(quantity)
            if qty % 1:
                raise ValueError("Whole-share isolated positions required")
            positions[ticker] = str(qty.quantize(Decimal("1")))
        return positions

    def finish_flatten(self, writer, epoch, *, nonce, flat_snapshot, receipt_id):
        """A new worker can reconcile a completed handoff without another sell."""
        if not isinstance(receipt_id, str) or not receipt_id.strip():
            raise ValueError("A durable reconciliation receipt is required")
        with self._db:
            self._db.execute("BEGIN IMMEDIATE")
            self._fence(writer, epoch)
            positions, _ = self._positions(flat_snapshot, self._now())
            if positions or flat_snapshot.get("pending_orders_reconciled_empty") is not True:
                raise ValueError("Flatten completion needs fresh flat and settled evidence")
            row = self._db.execute("SELECT state,execution_receipt FROM paper_flatten_batches WHERE nonce=?",
                                   (nonce,)).fetchone()
            if row is None or row["state"] not in {"READY", "ALREADY_FLAT", "DONE"}:
                raise ValueError("No eligible flatten handoff exists")
            if row["state"] == "DONE":
                if row["execution_receipt"] != receipt_id:
                    raise ValueError("Flatten handoff already reconciled with a different receipt")
                return False
            self._db.execute("UPDATE paper_flatten_batches SET state='DONE',execution_receipt=? WHERE nonce=?",
                             (receipt_id, nonce))
        return True

    def flatten_recovery(self, writer, epoch):
        """Read durable intent identities for reconciliation after takeover."""
        with self._db:
            self._db.execute("BEGIN IMMEDIATE")
            self._fence(writer, epoch)
            row = self._db.execute("SELECT nonce,state,payload FROM paper_flatten_batches WHERE id=1").fetchone()
            if row is None:
                return {"state": "NONE", "intent_ids": []}
            return {"state": row["state"], "nonce": row["nonce"],
                    "intent_ids": [intent["id"] for intent in json.loads(row["payload"])["paper_intents"]]}
