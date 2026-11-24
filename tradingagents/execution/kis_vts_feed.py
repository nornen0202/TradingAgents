"""Read-only KIS VTS WebSocket event handling and reconciliation triggers."""

from __future__ import annotations

import asyncio
import base64
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import AsyncContextManager, AsyncIterator, Awaitable, Callable, Protocol
from zoneinfo import ZoneInfo

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from websockets.exceptions import ConnectionClosed

from tradingagents.atomic_io import interprocess_file_lock

# KIS open-trading-api legacy/websocket/python/ws_domestic+overseas_stock.py
_NOTICE = {"KR": "H0STCNI9", "US": "H0GSCNI9"}
_QUOTES = {"KR": "H0STCNT0", "US": "HDFSCNT0"}
_NOTICE_WIDTH = {"KR": 26, "US": 25}
_QUOTE_WIDTH = {"KR": 46, "US": 26}
_WS_CAPACITY = 41


@dataclass(frozen=True)
class VtsScope:
    market: str
    hts_id: str = field(repr=False)
    account: str = field(repr=False)

    def __post_init__(self):
        if self.market not in _NOTICE or not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", self.hts_id):
            raise ValueError("Unsupported KIS VTS scope")
        if not re.fullmatch(r"[0-9]{8,10}", self.account):
            raise ValueError("Exact KIS VTS account field required")


@dataclass(frozen=True)
class QuoteObservation:
    market: str
    feed_key: str
    ticker: str
    source_at: datetime
    received_at: datetime
    native_price: Decimal
    currency: str
    cumulative_volume: int | None = None
    tradable: bool = False


@dataclass(frozen=True)
class OrderHint:
    market: str
    order_number: str = field(repr=False)
    original_order_number: str | None = field(repr=False)
    received_at: datetime
    content_digest: str = field(repr=False)


def subscription_plan(scopes, *, active_orders=(), held=(), watchlist=()):
    scopes = tuple(scopes)
    if not scopes or not all(isinstance(scope, VtsScope) for scope in scopes):
        raise ValueError("Explicit KIS VTS scopes are required")
    markets = {scope.market for scope in scopes}
    if len(markets) != len(scopes):
        raise ValueError("Use one explicitly scoped VTS notice stream per market")
    notice_streams = tuple((_NOTICE[scope.market], scope.hts_id) for scope in scopes)
    orders_and_holdings = dict.fromkeys(_quote_streams((*active_orders, *held), markets))
    if len(notice_streams) + len(orders_and_holdings) > _WS_CAPACITY:
        raise ValueError("Active orders and holdings exceed the KIS VTS session capacity")
    available = _WS_CAPACITY - len(notice_streams) - len(orders_and_holdings)
    extra = [pair for pair in dict.fromkeys(_quote_streams(watchlist, markets)) if pair not in orders_and_holdings]
    return notice_streams + tuple(orders_and_holdings) + tuple(extra[:available])


def _quote_streams(requested, markets):
    for market, key in requested:
        pattern = r"[0-9]{6}" if market == "KR" else r"[DR](?:NAS|NYS|AMS)[A-Z0-9.]{1,12}"
        if market not in markets or not re.fullmatch(pattern, key):
            raise ValueError("Unrecognized KIS market subscription")
        yield _QUOTES[market], key


def _decrypt(payload, key, iv):
    step = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
    data = step.update(base64.b64decode(payload, validate=True)) + step.finalize()
    unpad = PKCS7(128).unpadder()
    return (unpad.update(data) + unpad.finalize()).decode("utf-8")


class VtsFrameDecoder:
    def __init__(self, scopes, plan, *, quote_max_age_seconds=30):
        self._scopes = {scope.market: scope for scope in scopes}
        self._plan = frozenset(plan)
        if type(quote_max_age_seconds) is not int or not 1 <= quote_max_age_seconds <= 120:
            raise ValueError("Invalid quote age policy")
        self._max_age = timedelta(seconds=quote_max_age_seconds)
        self._crypto: dict[str, tuple[bytes, bytes]] = {}

    @property
    def notices_active(self):
        return all(_NOTICE[market] in self._crypto for market in self._scopes)

    def control(self, raw):
        """Consume an ACK. Return true when the client must mirror a heartbeat."""
        if len(raw) > 32_768:
            raise ValueError("Oversized KIS VTS control frame")
        data = json.loads(raw)
        header = data["header"]
        report_type = header.get("tr_id")
        if report_type == "PINGPONG":
            return True
        if (report_type, header.get("tr_key")) not in self._plan:
            raise ValueError("Unexpected KIS VTS subscription acknowledgement")
        if data["body"].get("rt_cd") != "0":
            raise ValueError("KIS VTS subscription was not acknowledged")
        if report_type in _NOTICE.values():
            output = data["body"]["output"]
            key, iv = output["key"].encode(), output["iv"].encode()
            if len(key) != 32 or len(iv) != 16:
                raise ValueError("KIS VTS notice session key is invalid")
            self._crypto[report_type] = key, iv
        return False

    def events(self, raw, received_at):
        if received_at.tzinfo is None or received_at.utcoffset() is None:
            raise ValueError("Aware receive clock required")
        if len(raw) > 131_072:
            raise ValueError("Oversized KIS VTS data frame")
        encoding, report_type, count_text, payload = raw.split("|", 3)
        if not re.fullmatch(r"[0-9]{1,3}", count_text) or not 1 <= (count := int(count_text)) <= 100:
            raise ValueError("Invalid KIS VTS frame record count")
        if report_type in _NOTICE.values() and encoding == "1":
            market = next(item for item, tr in _NOTICE.items() if tr == report_type)
            if market not in self._scopes or report_type not in self._crypto:
                raise ValueError("KIS VTS notice arrived before scoped acknowledgement")
            plain = _decrypt(payload, *self._crypto[report_type])
            width = _NOTICE_WIDTH[market]
            parts = plain.split("^")
            if len(parts) != count * width:
                raise ValueError("Unexpected KIS VTS notice width")
            return tuple(hint for offset in range(0, len(parts), width)
                         if (hint := self._notice(market, parts[offset:offset + width], received_at)) is not None)
        if report_type in _QUOTES.values() and encoding == "0":
            market = next(item for item, tr in _QUOTES.items() if tr == report_type)
            width = _QUOTE_WIDTH[market]
            parts = payload.split("^")
            if len(parts) != count * width:
                raise ValueError("Unexpected KIS VTS quote width")
            return tuple(item for offset in range(0, len(parts), width)
                         if (item := self._quote(market, parts[offset:offset + width], received_at)) is not None)
        raise ValueError("Unexpected KIS VTS frame type")

    def _notice(self, market, parts, received_at):
        scope = self._scopes[market]
        if parts[0] != scope.hts_id or parts[1] != scope.account:
            return None
        if not re.fullmatch(r"[0-9]{1,20}", parts[2]) or int(parts[2]) == 0:
            raise ValueError("Unverified KIS VTS order identifier")
        original = parts[3].strip()
        original = original if re.fullmatch(r"[0-9]{1,20}", original) and int(original) else None
        # A notice is only a wakeup hint. Only REST cumulative quantities and
        # durable broker fill identifiers can advance the execution journal.
        digest = sha256("^".join(parts).encode()).hexdigest()
        return OrderHint(market, parts[2], original, received_at, digest)

    def _quote(self, market, parts, received_at):
        feed_key = parts[0]
        if (_QUOTES[market], feed_key) not in self._plan:
            return None
        if market == "KR":
            day, clock, price, ticker, currency = parts[33], parts[1], parts[2], feed_key, "KRW"
            volume = parts[13]
        else:
            day, clock, price, ticker, currency = parts[6], parts[7], parts[11], parts[1], "USD"
            volume = parts[20]
            if feed_key[4:] != ticker:
                return None
        if not re.fullmatch(r"[0-9]{14}", day + clock) or len(day) != 8 or len(clock) != 6:
            return None
        try:
            at = datetime.strptime(day + clock, "%Y%m%d%H%M%S").replace(tzinfo=ZoneInfo("Asia/Seoul"))
            value = Decimal(price)
        except (ValueError, InvalidOperation):
            return None
        if not value.is_finite() or value <= 0 or not timedelta() <= received_at - at <= self._max_age:
            return None
        cumulative = int(volume) if re.fullmatch(r"[0-9]{1,20}", volume) else None
        return QuoteObservation(market, feed_key, ticker, at, received_at, value, currency, cumulative)


@dataclass(frozen=True)
class FeedResult:
    connection_attempts: int
    disconnects: int
    delivered_order_hints: int
    delivered_quotes: int
    stopped: str = "RECONNECT_BUDGET_EXHAUSTED"
    verified_notice_sessions: int = 0


class VtsSocket(Protocol):
    def __aiter__(self) -> AsyncIterator[str]: ...
    async def send(self, text: str): ...
    async def pong(self, payload: bytes): ...


async def run_event_feed(
    lock_path: Path, scopes, plan, *, open_vts: Callable[[], AsyncContextManager[VtsSocket]],
    approval: Callable[[], Awaitable[str]], resynchronize: Callable[[], Awaitable[None]],
    on_hint: Callable[[OrderHint], Awaitable[None]], on_quote: Callable[[QuoteObservation], Awaitable[None]],
    sleep: Callable[[float], Awaitable[None]], attempts: int = 3, idle_seconds: int = 40,
    clock=lambda: datetime.now(timezone.utc),
):
    """Consume a VTS stream. REST callbacks share the account's request limiter."""
    scopes = tuple(scopes)
    plan = tuple(plan)
    expected = set(subscription_plan(scopes))
    if (not expected <= set(plan) or len(set(plan)) != len(plan) or len(plan) > _WS_CAPACITY
            or type(attempts) is not int or not 1 <= attempts <= 10
            or type(idle_seconds) is not int or not 5 <= idle_seconds <= 120):
        raise ValueError("Invalid KIS VTS feed policy")
    for report_type, key in set(plan) - expected:
        market = next((m for m, kind in _QUOTES.items() if report_type == kind), None)
        list(_quote_streams(((market, key),), {scope.market for scope in scopes}))
    hints_seen: OrderedDict[str, None] = OrderedDict()
    last_quote: dict[tuple[str, str], QuoteObservation] = {}
    disconnects = hint_count = quote_count = verified = 0
    with interprocess_file_lock(lock_path, timeout=0):
        for attempt in range(attempts):
            if attempt:
                await sleep(min(30, 2 ** (attempt - 1)))
            decoder = VtsFrameDecoder(scopes, plan)
            recovered = False
            pending_events = []
            try:
                token = await approval()
                if not isinstance(token, str) or not token.strip():
                    raise ValueError("Missing KIS VTS approval")
                async with open_vts() as socket:
                    for report_type, key in plan:
                        await socket.send(json.dumps({
                            "header": {"approval_key": token, "custtype": "P", "tr_type": "1",
                                       "content-type": "utf-8"},
                            "body": {"input": {"tr_id": report_type, "tr_key": key}},
                        }))
                    messages = aiter(socket)
                    while True:
                        try:
                            raw = await asyncio.wait_for(anext(messages), timeout=idle_seconds)
                        except StopAsyncIteration:
                            break
                        if raw.startswith("{"):
                            if decoder.control(raw):
                                await socket.pong(raw.encode())
                            if recovered or not decoder.notices_active:
                                continue
                            verified += 1
                            # Acknowledgement precedes the authoritative REST
                            # snapshot so no new executions fall in the gap.
                            await resynchronize()
                            recovered = True
                            events, pending_events = pending_events, []
                        else:
                            events = decoder.events(raw, clock())
                            if not recovered:
                                pending_events.extend(events)
                                if len(pending_events) > 512:
                                    raise ValueError("KIS VTS subscription recovery buffer full")
                                continue
                        for event in events:
                            if isinstance(event, OrderHint):
                                if event.content_digest not in hints_seen:
                                    await on_hint(event)
                                    hint_count += 1
                                    hints_seen[event.content_digest] = None
                                    if len(hints_seen) > 2048:
                                        hints_seen.popitem(last=False)
                            else:
                                key = event.market, event.feed_key
                                previous = last_quote.get(key)
                                if previous is not None and not _advances_quote(previous, event):
                                    continue
                                await on_quote(event)
                                quote_count += 1
                                last_quote[key] = event
            except (OSError, ConnectionClosed, ValueError, KeyError, AttributeError, TypeError):
                # Inputs can contain account fields and session key material.
                # Reconcile again on reconnect without retaining exception details.
                pass
            disconnects += 1
        await resynchronize()
    return FeedResult(attempts, disconnects, hint_count, quote_count, verified_notice_sessions=verified)


def _advances_quote(previous, current):
    if current.source_at != previous.source_at:
        return current.source_at > previous.source_at
    if current.cumulative_volume is not None and previous.cumulative_volume is not None:
        return current.cumulative_volume > previous.cumulative_volume
    return current.native_price != previous.native_price
