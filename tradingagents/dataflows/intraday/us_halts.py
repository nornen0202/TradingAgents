"""Current Nasdaq halt/pause feed, with original publication/event clocks.

The official feed covers Nasdaq and other exchange-listed securities and is
updated once a minute. It is not a historical replay service or Reg SHO feed.
https://www.nasdaqtrader.com/Trader.aspx?id=TradeHaltRSS
"""
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from threading import Lock
import time
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

import requests

from tradingagents.charting.bars import instant
from .us_symbols import canonical_symbol

URL = "https://www.nasdaqtrader.com/rss.aspx?feed=tradehalts"
NS = {"n": "http://www.nasdaqtrader.com/"}
NY = ZoneInfo("America/New_York")


def _event(day, hour):
    if not day or not hour:
        raise ValueError("HALT_EVENT_CLOCK_MISSING")
    try:
        return datetime.strptime(day + " " + hour, "%m/%d/%Y %H:%M:%S.%f").replace(tzinfo=NY)
    except ValueError:
        return datetime.strptime(day + " " + hour, "%m/%d/%Y %H:%M:%S").replace(tzinfo=NY)


def parse_feed(content, *, observed_at):
    """Reject incomplete evidence; never infer 'clear' from an unreadable row."""
    if observed_at.tzinfo is None or len(content) > 2_000_000:
        raise ValueError("HALT_FEED_INVALID")
    if b"<!DOCTYPE" in content.upper() or b"<!ENTITY" in content.upper():
        raise ValueError("HALT_FEED_INVALID")
    root = ET.fromstring(content)
    channel = root.find("channel")
    if root.tag != "rss" or channel is None or channel.findtext("description") != "NASDAQ Trade Halts":
        raise ValueError("HALT_FEED_INVALID")
    published = parsedate_to_datetime(channel.findtext("pubDate") or "")
    if published.tzinfo is None or not 0 <= (observed_at - published).total_seconds() < 120:
        raise ValueError("HALT_FEED_STALE_OR_FUTURE")
    items = channel.findall("item")
    count = channel.findtext("n:numItems", namespaces=NS)
    if count is None or not count.isdigit() or int(count) != len(items):
        raise ValueError("HALT_FEED_INCOMPLETE")
    events, seen = [], {}
    for item in items:
        def field(name):
            return (item.findtext("n:" + name, namespaces=NS) or "").strip()
        symbol, reason = canonical_symbol(field("IssueSymbol")), field("ReasonCode")
        if not symbol or not reason:
            raise ValueError("HALT_EVENT_IDENTITY_MISSING")
        halted_at = _event(field("HaltDate"), field("HaltTime"))
        if halted_at > published:
            raise ValueError("HALT_EVENT_FUTURE")
        resume_day, resume_time = field("ResumptionDate"), field("ResumptionTradeTime")
        # Quote resumption is not trading resumption. A scheduled future
        # resumption remains halted until a later published feed confirms it.
        resumed_at = _event(resume_day, resume_time) if resume_day and resume_time else None
        if resume_time and not resume_day or resumed_at is not None and resumed_at < halted_at:
            raise ValueError("HALT_RESUMPTION_INVALID")
        key = (symbol, halted_at)
        if key in seen and seen[key] != (resumed_at, reason):
            raise ValueError("HALT_FEED_CONFLICTING_EVENTS")
        seen[key] = (resumed_at, reason)
        events.append({"symbol": symbol, "halted_at": halted_at,
                       "resumed_at": resumed_at, "reason": reason})
    return {"published_at": published, "observed_at": observed_at, "events": events}


def status_for(feed, symbol, *, analysis_as_of, traded_bars=()):
    symbol = canonical_symbol(symbol)
    published, observed = feed["published_at"], feed["observed_at"]
    if (analysis_as_of.tzinfo is None or not published <= observed <= analysis_as_of
            or not 0 <= (analysis_as_of - published).total_seconds() < 120):
        raise ValueError("HALT_FEED_STALE_OR_FUTURE")
    matching = [row for row in feed["events"] if canonical_symbol(row["symbol"]) == symbol]
    # Multiple halts per day are common. The latest halt governs; future
    # resumption announcements do not clear it.
    latest = max(matching, key=lambda row: row["halted_at"], default=None)
    active = latest is not None and (latest["resumed_at"] is None or latest["resumed_at"] > published)
    # The default RSS query contains only the current halt day's events, NOT
    # every multi-day halt. Absence alone can never establish clear status.
    # A dated completed bar with actual volume on this NY day rules out an
    # uninterrupted earlier-day halt; the feed then covers subsequent halts.
    traded = False
    for bar in traded_bars:
        start, end, known = (instant(bar.get(k)) for k in ("timestamp", "available_at", "observed_at"))
        volume = bar.get("volume")
        if (start is not None and end is not None and known is not None
                and start < end <= known <= analysis_as_of and end <= published
                and start.astimezone(NY).date() == published.astimezone(NY).date()
                and 0 <= (published - end).total_seconds() < 120
                and isinstance(volume, (int, float)) and not isinstance(volume, bool)
                and 0 < volume < float("inf")):
            traded = True
    clear = not active and traded
    return {"status": "clear" if clear else "halted" if active else "unknown", "is_clear": clear,
            "source": "nasdaq.current_trade_halts", "published_at": published.isoformat(),
            "observed_at": observed.isoformat(), "as_of": analysis_as_of.isoformat(),
            "basis": "CURRENT_DAY_HALT_FEED_PLUS_DATED_TRADED_BAR", "symbol": symbol,
            "reason_code": latest["reason"] if latest else None}


class NasdaqHaltProvider:
    def __init__(self, *, get=None, clock=None, monotonic=None):
        self._get = get or requests.get
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._monotonic = monotonic or time.monotonic
        self._lock = Lock()
        self._attempt = None
        self._feed = None

    def fetch(self, symbol, *, traded_bars=()):
        with self._lock:
            elapsed = self._monotonic()
            if self._attempt is None or elapsed - self._attempt >= 60:
                self._attempt = elapsed
                self._feed = None
                response = self._get(URL, timeout=10, allow_redirects=False)
                if response.status_code != 200:
                    raise ValueError("HALT_FEED_UNAVAILABLE")
                self._feed = parse_feed(response.content, observed_at=self._clock())
            if self._feed is None:
                raise ValueError("HALT_FEED_UNAVAILABLE")
            return status_for(self._feed, symbol, analysis_as_of=self._clock(), traded_bars=traded_bars)


# One request per minute across symbols/provider instances in this producer.
current_halts = NasdaqHaltProvider()


def long_only_market_statuses(halt, *, analysis_as_of):
    """Scope available evidence to the supported long-only limit-order path.

    RSS verifies trading pauses (including LUDP/T5 and news halts), not live
    LULD price bands. Reg SHO Rule 201 restricts short sales, which both paper
    brokers forbid by checking broker-reported unreserved sellable holdings.
    Do not claim that a symbol's short-sale restriction is clear.
    """
    reg_sho = {"status": "not_applicable_long_only", "is_clear": None,
               "source": "SEC_RULE_201_ORDER_SCOPE", "short_sale_status": "unknown",
               "order_scope": "BUY_OR_VERIFIED_LONG_SELL", "short_sales_supported": False}
    published, observed, evaluated = (instant(halt.get(k)) for k in ("published_at", "observed_at", "as_of"))
    verified = (halt.get("source") == "nasdaq.current_trade_halts"
                and halt.get("basis") == "CURRENT_DAY_HALT_FEED_PLUS_DATED_TRADED_BAR"
                and published is not None and observed is not None and evaluated is not None
                and published <= observed <= evaluated <= analysis_as_of
                and 0 <= (analysis_as_of - published).total_seconds() < 120
                and halt.get("status") in {"clear", "halted"}
                and halt.get("is_clear") is (halt.get("status") == "clear"))
    common = {k: halt.get(k) for k in ("source", "published_at", "observed_at", "as_of", "basis", "symbol", "reason_code")}
    # Any reported halt blocks both paths, even when its reason is not one of
    # the common LUDP/T5 or T1/T2 codes. Unknown/absent evidence stays unknown.
    common.update(status=halt["status"] if verified else "not_available_by_provider",
                  is_clear=halt["is_clear"] if verified else None,
                  order_scope="LONG_ONLY_LIMIT_ORDERS")
    luld = {**common, "scope": "REPORTED_TRADING_PAUSES", "price_bands_available": False,
            "limitation": "Live LULD bands are not supplied; execution venue enforces price bands."}
    news = {**common, "scope": "REPORTED_NEWS_AND_OTHER_TRADING_HALTS"}
    return luld, reg_sho, news
