"""Dated broker observations for local simulation; the client can only read.

The simulated price is a completed one-minute close, never a retrieval-time
timestamp attached to an undated last price. USD conversion is explicitly a
broker reference valuation, not a simulated foreign-exchange transaction.
"""
from __future__ import annotations

from datetime import datetime, timezone
import math
import re
from zoneinfo import ZoneInfo

from tradingagents.charting.bars import instant
from tradingagents.charting.capture import normalize_kis_bars
from tradingagents.portfolio.kis import KisClient


def _number(value):
    if isinstance(value, bool):
        raise ValueError("INVALID_PRICE")
    try:
        result = float(str(value).replace(",", ""))
    except (ValueError, TypeError):
        raise ValueError("INVALID_PRICE") from None
    if not math.isfinite(result) or result <= 0:
        raise ValueError("INVALID_PRICE")
    return result


def normalized_orderbook(payload, market):
    """Join identity/clock and price fields from one current broker response.

    The US API returns dymd/dhms/code in output1 and pbid1/pask1 in output2.
    Domestic identity is in output2. Neither response part may silently replace
    conflicting fields from the other part; vbid/vask remain volume only.
    """
    if market not in {"kr", "us"} or not isinstance(payload, dict):
        raise ValueError("ORDERBOOK_MISSING")
    merged = {}
    for field in ("output1", "output2"):
        item = payload.get(field)
        if item is None:
            continue
        if not isinstance(item, dict):
            raise ValueError("ORDERBOOK_INVALID_PART")
        for key, value in item.items():
            if key in merged and merged[key] != value:
                raise ValueError("ORDERBOOK_CONFLICTING_PARTS")
            merged[key] = value
    if not merged:
        raise ValueError("ORDERBOOK_MISSING")
    if market == "us" and merged.get("curr") not in {None, "", "USD"}:
        raise ValueError("ORDERBOOK_CURRENCY_MISMATCH")
    return merged


def normalize_quote(*, ticker, market, chart, orderbook, observed_at, fx_quote=None):
    at = instant(observed_at)
    if at is None or market not in {"kr", "us"}:
        raise ValueError("INVALID_OBSERVATION_CLOCK_OR_MARKET")
    zone = "Asia/Seoul" if market == "kr" else "America/New_York"
    day = at.astimezone(ZoneInfo(zone)).date()
    for payload in (chart, orderbook):
        if not isinstance(payload, dict) or str(payload.get("rt_cd")) != "0":
            raise ValueError("BROKER_RESPONSE_UNVERIFIED")
    rows = chart.get("output2")
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError("DATED_MINUTE_BARS_MISSING")
    bars = normalize_kis_bars(rows, observed_at=at, timezone_name=zone)
    bars = [b for b in bars if instant(b["available_at"]).astimezone(ZoneInfo(zone)).date() == day]
    if not bars:
        raise ValueError("DATED_COMPLETED_PRICE_MISSING")
    bar = max(bars, key=lambda b: instant(b["available_at"]))
    quote_at = instant(bar["available_at"])
    if not 0 <= (at - quote_at).total_seconds() <= 120:
        raise ValueError("QUOTE_STALE")
    from tradingagents.scheduled.market_calendar import market_session_state
    if not market_session_state(market=market, now_local=quote_at).get("is_open"):
        raise ValueError("PRICE_OUTSIDE_REGULAR_SESSION")
    book = normalized_orderbook(orderbook, market)
    expected_symbol = ticker[:6] if market == "kr" else ticker
    if any(str(book[key]).strip().upper() != expected_symbol for key in ("code", "symbol", "pdno", "stck_shrn_iscd")
           if book.get(key) not in (None, "")):
        raise ValueError("ORDERBOOK_IDENTITY_MISMATCH")
    # KIS vbid1/vask1 are VOLUMES, never price fallbacks.
    bid = next((book[k] for k in ("bidp1", "pbid1", "PBID", "bid") if k in book), None)
    ask = next((book[k] for k in ("askp1", "pask1", "PASK", "ask") if k in book), None)
    bid, ask = _number(bid), _number(ask)
    if ask < bid:
        raise ValueError("CROSSED_ORDERBOOK")
    spread = (ask - bid) / ((ask + bid) / 2) * 10000
    if spread > 100:
        raise ValueError("SPREAD_TOO_WIDE")
    book_day = book.get("dymd") or book.get("stck_bsop_date")
    book_time = book.get("dhms") or book.get("aspr_acpt_hour") or book.get("bsop_hour")
    if not book_time or (market == "us" and not book_day):
        raise ValueError("ORDERBOOK_CLOCK_MISSING")
    # The domestic current-asking-price endpoint supplies a time of day only.
    # Its date is tied to the independently dated, <=120s completed bar from
    # this same live request, and this derivation is retained in the receipt.
    book_date_basis = "EXPLICIT" if book_day else "CURRENT_ENDPOINT_DATED_BAR_CONTEXT"
    book_day = str(book_day or day.strftime("%Y%m%d"))
    if not re.fullmatch(r"\d{8}", book_day) or not re.fullmatch(r"\d{6}", str(book_time)):
        raise ValueError("ORDERBOOK_CLOCK_INVALID")
    try:
        book_at = datetime.strptime(book_day + str(book_time), "%Y%m%d%H%M%S").replace(tzinfo=ZoneInfo(zone))
    except ValueError:
        raise ValueError("ORDERBOOK_CLOCK_INVALID") from None
    if not 0 <= (at - book_at).total_seconds() <= 120:
        raise ValueError("ORDERBOOK_CLOCK_STALE_OR_FUTURE")
    price = _number(bar["close"])
    result = {"as_of": quote_at.isoformat(), "observed_at": at.isoformat(),
              "price_krw": price, "session": "regular", "executable": True,
              "spread_bps": spread, "source": "kis.completed_minute_close+observed_orderbook",
              "price_basis": "COMPLETED_MINUTE_CLOSE", "ticker": ticker,
              "orderbook_event_at": book_at.isoformat(), "orderbook_date_basis": book_date_basis}
    if market == "us":
        fx = fx_quote or {}
        fx_at = instant(fx.get("observed_at"))
        if (fx_at is None or not 0 <= (at - fx_at).total_seconds() <= 120
                or fx.get("base_currency") != "USD" or fx.get("quote_currency") != "KRW"
                or fx.get("kind") != "BROKER_REFERENCE_RATE"
                or fx.get("source") != "kis.inquire_present_balance.output2.frst_bltn_exrt"):
            raise ValueError("FX_REFERENCE_MISSING_OR_STALE")
        rate = _number(fx.get("rate"))
        result.update(price_krw=price * rate, price_usd=price, fx_rate=rate,
                      fx_observed_at=fx_at.isoformat(), fx_kind="BROKER_REFERENCE_RATE",
                      fx_limitation="Reference KRW valuation only; not real-time FX execution")
    return result


class ReadOnlyPaperQuotes:
    def __init__(self, *, client=None, clock=None):
        self.client = client or KisClient.from_api_keys(environment="real")
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def close(self):
        self.client.session.close()

    def fetch(self, tickers, *, market, fx_quote=None):
        quotes, blockers = {}, {}
        for ticker in sorted(set(tickers)):
            try:
                if market == "kr":
                    if not re.fullmatch(r"\d{6}\.(?:KS|KQ)", ticker):
                        raise ValueError("INVALID_DOMESTIC_IDENTITY")
                    code = ticker[:6]
                    chart = self.client.domestic_time_itemchartprice(
                        code, input_hour=self.clock().astimezone(ZoneInfo("Asia/Seoul")).strftime("%H%M%S"),
                        include_past_data="N")
                    book = self.client.domestic_asking_price(code)
                else:
                    if market != "us" or not re.fullmatch(r"[A-Z][A-Z0-9.\-]{0,14}", ticker):
                        raise ValueError("INVALID_OVERSEAS_IDENTITY")
                    chart = book = None
                    for exchange in ("NAS", "NYS", "AMS"):
                        payload = self.client.overseas_time_itemchartprice(ticker, exchange=exchange, nmin="1", include_previous="0")
                        candidate = payload[0] if isinstance(payload, tuple) else payload
                        if isinstance(candidate, dict) and candidate.get("output2"):
                            chart = candidate
                            book = self.client.overseas_asking_price(ticker, exchange=exchange)
                            break
                quotes[ticker] = normalize_quote(ticker=ticker, market=market, chart=chart, orderbook=book,
                                                observed_at=self.clock(), fx_quote=fx_quote)
            except ValueError as exc:
                code = str(exc)
                blockers[ticker] = code if re.fullmatch(r"[A-Z_]+", code) else "INVALID_BROKER_OBSERVATION"
            except Exception:
                blockers[ticker] = "BROKER_READ_UNAVAILABLE"
        return quotes, blockers
