"""Signed Telegram-compatible callbacks for isolated paper proposals."""

from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, ROUND_DOWN
import hashlib
import hmac
import json
from pathlib import Path
import re
import secrets
import sqlite3

from .experiments import _stamp


def _num(value):
    try:
        value = Decimal(value)
    except (TypeError, ValueError, InvalidOperation) as exc:
        raise ValueError("Invalid proposal amount") from exc
    if not value.is_finite() or value <= 0:
        raise ValueError("Proposal amount must be positive and finite")
    return value


def _token(value):
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _encode(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False)


def apply_telegram_paper_callback(ledger, update, *, supplied_secret, webhook_secret, bot_id, allowed_chats):
    """Verify one ingress payload and forward only its isolated decision."""
    secret_pattern = r"[A-Za-z0-9_-]{32,256}"
    if (not isinstance(webhook_secret, str) or not re.fullmatch(secret_pattern, webhook_secret)
            or not isinstance(supplied_secret, str) or not re.fullmatch(secret_pattern, supplied_secret)
            or not hmac.compare_digest(webhook_secret, supplied_secret)
            or type(bot_id) is not int or bot_id <= 0):
        raise ValueError("Unauthorized Telegram webhook")
    try:
        callback = update["callback_query"]
        sender = callback["from"]
        message = callback["message"]
        actor_id, origin_id, chat_id = sender["id"], message["from"]["id"], message["chat"]["id"]
        query_id = callback["id"]
        if (type(update["update_id"]) is not int or update["update_id"] <= 0
                or type(actor_id) is not int or actor_id <= 0 or sender.get("is_bot") is not False
                or type(origin_id) is not int or origin_id != bot_id or message["from"].get("is_bot") is not True
                or type(chat_id) is not int or chat_id not in allowed_chats
                or not isinstance(query_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", query_id)
                or "inline_message_id" in callback or "game_short_name" in callback):
            raise ValueError("Unverified Telegram callback scope")
        data = callback["data"]
    except (TypeError, KeyError, AttributeError) as exc:
        raise ValueError("Unverified Telegram callback scope") from exc
    recorded = ledger.decide(data, actor_id=str(actor_id), delivery_id=f"telegram:{bot_id}:{query_id}")
    return {"status": "RECORDED" if recorded else "REPLAY", "live_order_authority": False}


class PaperApproval:
    """Keep callback authentication separate from transport and broker execution."""

    def __init__(self, path: Path, *, secret: bytes, authorized: frozenset[str], clock=None):
        if not isinstance(secret, bytes) or len(secret) < 32 or not authorized:
            raise ValueError("Local signing key and explicit approvers are required")
        self._secret = secret
        self._authorized = authorized
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        path.parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(path, timeout=20)
        self._db.row_factory = sqlite3.Row
        self._db.executescript("""
            CREATE TABLE IF NOT EXISTS paper_approval_proposals(
                intent TEXT PRIMARY KEY, nonce TEXT NOT NULL UNIQUE, payload TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS paper_approval_events(
                id INTEGER PRIMARY KEY, intent TEXT NOT NULL, actor TEXT NOT NULL, action TEXT NOT NULL,
                delivery TEXT UNIQUE, occurred_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS paper_approval_admissions(
                intent TEXT PRIMARY KEY, payload TEXT NOT NULL
            );
            CREATE TRIGGER IF NOT EXISTS paper_proposal_no_update BEFORE UPDATE ON paper_approval_proposals
                BEGIN SELECT RAISE(ABORT, 'Proposal is immutable'); END;
            CREATE TRIGGER IF NOT EXISTS paper_proposal_no_delete BEFORE DELETE ON paper_approval_proposals
                BEGIN SELECT RAISE(ABORT, 'Proposal is immutable'); END;
            CREATE TRIGGER IF NOT EXISTS paper_event_no_update BEFORE UPDATE ON paper_approval_events
                BEGIN SELECT RAISE(ABORT, 'Approval is append-only'); END;
            CREATE TRIGGER IF NOT EXISTS paper_event_no_delete BEFORE DELETE ON paper_approval_events
                BEGIN SELECT RAISE(ABORT, 'Approval is append-only'); END;
            CREATE TRIGGER IF NOT EXISTS paper_admission_no_update BEFORE UPDATE ON paper_approval_admissions
                BEGIN SELECT RAISE(ABORT, 'Paper admission is immutable'); END;
            CREATE TRIGGER IF NOT EXISTS paper_admission_no_delete BEFORE DELETE ON paper_approval_admissions
                BEGIN SELECT RAISE(ABORT, 'Paper admission is immutable'); END;
        """)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self._db.close()

    def _now(self):
        return _stamp(self._clock())

    def _callback(self, nonce, command):
        value = f"{command}.{nonce}"
        digest = _token(hmac.new(self._secret, f"paper-approval-v1:{value}".encode(), hashlib.sha256).digest()[:16])
        return f"{value}.{digest}"

    def propose(self, proposal):
        required = {"intent", "scope", "mode", "ticker", "market", "currency", "side",
                    "quantity", "quantity_step", "limit", "expires_at"}
        if (not isinstance(proposal, dict) or set(proposal) != required
                or proposal["mode"] != "isolated_paper" or proposal["side"] not in ("BUY", "SELL")
                or proposal["market"] not in ("KR", "US")
                or any(not isinstance(proposal[key], str) or not proposal[key].strip()
                       for key in ("intent", "scope", "ticker", "currency"))
                or not re.fullmatch("[A-Z]{3}", proposal["currency"])):
            raise ValueError("An isolated paper proposal with explicit identity is required")
        quantity, step = _num(proposal["quantity"]), _num(proposal["quantity_step"])
        _num(proposal["limit"])
        if quantity % step:
            raise ValueError("Quantity must meet its broker lot step")
        now, expiry = self._now(), _stamp(proposal["expires_at"])
        if not timedelta(0) < expiry - now <= timedelta(minutes=30):
            raise ValueError("Proposal expiry is outside the admission window")
        encoded = _encode(proposal)
        with self._db:
            self._db.execute("BEGIN IMMEDIATE")
            row = self._db.execute("SELECT * FROM paper_approval_proposals WHERE intent=?", (proposal["intent"],)).fetchone()
            if row is not None and row["payload"] != encoded:
                raise ValueError("Intent is already bound to different proposal terms")
            nonce = row["nonce"] if row else _token(secrets.token_bytes(16))
            self._db.execute("INSERT OR IGNORE INTO paper_approval_proposals VALUES (?,?,?)",
                             (proposal["intent"], nonce, encoded))
        return {
            "approve": self._callback(nonce, "A"), "reject": self._callback(nonce, "X"),
            "reduce": self._callback(nonce, "H"), "revoke": self._callback(nonce, "R"),
        }

    def decide(self, callback, *, actor_id, delivery_id):
        if actor_id not in self._authorized or not isinstance(delivery_id, str) or not delivery_id.strip():
            raise ValueError("Unauthorized or undated callback")
        if not isinstance(callback, str) or not re.fullmatch(r"[AXHR]\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{22}", callback):
            raise ValueError("Invalid callback")
        command, nonce, _ = callback.split(".")
        if not hmac.compare_digest(callback, self._callback(nonce, command)):
            raise ValueError("Invalid callback signature")
        with self._db:
            self._db.execute("BEGIN IMMEDIATE")
            row = self._db.execute("SELECT * FROM paper_approval_proposals WHERE nonce=?", (nonce,)).fetchone()
            if row is None:
                raise ValueError("Unknown callback nonce")
            prior = self._db.execute("SELECT intent,actor,action FROM paper_approval_events WHERE delivery=?",
                                     (delivery_id,)).fetchone()
            if prior is not None:
                if tuple(prior) != (row["intent"], actor_id, command):
                    raise ValueError("Delivery ID is already bound to a different decision")
                return False
            proposal = json.loads(row["payload"])
            if _stamp(proposal["expires_at"]) <= self._now():
                raise ValueError("Proposal has expired")
            last = self._last(row["intent"])
            if command == "R":
                if last is None or last["action"] not in ("A", "H") or last["actor"] != actor_id:
                    raise ValueError("Only the approving actor can revoke an unused approval")
            elif last is not None:
                raise ValueError("The proposal already has a decision")
            if command == "H" and _num(proposal["quantity"]) / 2 < _num(proposal["quantity_step"]):
                raise ValueError("Reduced size is below one lot")
            self._append(row["intent"], actor_id, command, delivery_id)
        return True

    def _last(self, intent):
        return self._db.execute("SELECT * FROM paper_approval_events WHERE intent=? ORDER BY id DESC LIMIT 1",
                                (intent,)).fetchone()

    def _append(self, intent, actor, action, delivery=None):
        self._db.execute("INSERT INTO paper_approval_events(intent,actor,action,delivery,occurred_at) VALUES (?,?,?,?,?)",
                         (intent, actor, action, delivery, self._now().isoformat()))

    def consume(self, intent, *, quote, scope, age_seconds=30):
        """Issue one local paper admission after current quote revalidation."""
        if type(age_seconds) is not int or not 1 <= age_seconds <= 120:
            raise ValueError("Invalid quote age policy")
        with self._db:
            self._db.execute("BEGIN IMMEDIATE")
            row = self._db.execute("SELECT payload FROM paper_approval_proposals WHERE intent=?", (intent,)).fetchone()
            last = self._last(intent)
            if row is None or last is None or last["action"] not in ("A", "H"):
                raise ValueError("No unused approval")
            proposal = json.loads(row["payload"])
            now = self._now()
            if proposal["scope"] != scope or _stamp(proposal["expires_at"]) <= now:
                raise ValueError("Approval is expired or belongs to a different account scope")
            if (not isinstance(quote, dict) or quote.get("session_open") is not True
                    or any(quote.get(key) != proposal[key] for key in ("market", "ticker", "currency"))):
                raise ValueError("Fresh same-instrument quote in an open session is required")
            observed = _stamp(quote.get("observed_at"))
            if not _stamp(last["occurred_at"]) <= observed <= now or now - observed > timedelta(seconds=age_seconds):
                raise ValueError("Quote is stale or predates the approval")
            price = _num(quote.get("ask") if proposal["side"] == "BUY" else quote.get("bid"))
            limit = _num(proposal["limit"])
            if (proposal["side"] == "BUY" and price > limit) or (proposal["side"] == "SELL" and price < limit):
                raise ValueError("Updated quote violates the approved limit")
            quantity, step = _num(proposal["quantity"]), _num(proposal["quantity_step"])
            if last["action"] == "H":
                quantity = ((quantity / 2) / step).to_integral_value(rounding=ROUND_DOWN) * step
            admission = {**proposal, "quantity": str(quantity), "live_order_authority": False}
            self._db.execute("INSERT INTO paper_approval_admissions VALUES (?,?)", (intent, _encode(admission)))
            self._append(intent, last["actor"], "CONSUMED")
        return admission

    def recover_admission(self, intent, *, scope):
        """Read the durable handoff for reconciliation. The caller must refresh quotes before dispatch."""
        row = self._db.execute("SELECT payload FROM paper_approval_admissions WHERE intent=?", (intent,)).fetchone()
        if row is None:
            return None
        admission = json.loads(row["payload"])
        return admission if admission["scope"] == scope else None


def render_telegram_approval_card(proposal: dict, callbacks: dict[str, str]) -> dict:
    """Format an isolated paper proposal with HMAC-signed inline keyboard buttons."""
    text = (
        f"🧾 모의매매 승인 요청 [{proposal['market']}]\n"
        f"• 종목: {proposal['ticker']} ({proposal['side']})\n"
        f"• 수량: {proposal['quantity']} (단위 {proposal['quantity_step']})\n"
        f"• 지정가 한도: {proposal['limit']} {proposal['currency']}\n"
        f"• 만료 시각: {proposal['expires_at']}"
    )
    return {
        "text": text,
        "reply_markup": {
            "inline_keyboard": [
                [
                    {"text": "✅ 승인", "callback_data": callbacks["approve"]},
                    {"text": "½ 축소 승인", "callback_data": callbacks["reduce"]},
                ],
                [
                    {"text": "❌ 거절", "callback_data": callbacks["reject"]},
                    {"text": "↩️ 승인 철회", "callback_data": callbacks["revoke"]},
                ],
            ]
        },
    }
