"""Strict clocks and response parts for KIS US quotation evidence.

HHDFS76200100: output1 identity/Korea clock, output2 book prices/sizes.
HHDFS76200300: output1 summary, output2 executions; vpow is strength,
khms is Korea time and mtyp is market type (never aggressor side).
"""
from datetime import datetime, timedelta
import math
import re
from zoneinfo import ZoneInfo

from tradingagents.execution.paper_quotes import normalized_orderbook


KOREA = ZoneInfo("Asia/Seoul")


def dated_book(payload, symbol, observed_at):
    book = normalized_orderbook(payload, "us")
    if str(book.get("code") or "").upper() != symbol.upper():
        raise ValueError("ORDERBOOK_IDENTITY_UNVERIFIED")
    at = _clock(book.get("dymd"), book.get("dhms"))
    _fresh(at, observed_at)
    bid, ask = _positive(book.get("pbid1")), _positive(book.get("pask1"))
    if ask < bid:
        raise ValueError("CROSSED_ORDERBOOK")
    return book, at


def dated_strength(payload, *, book_at, observed_at):
    """TDAY=1 time-only rows need the independently dated current book.

    A missing, previous-day, stale or future book cannot date the tape.
    No retrieval clock is substituted for an event clock.
    """
    _fresh(book_at, observed_at)
    rows = payload.get("output2") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        raise ValueError("TRADE_TAPE_MISSING")
    valid = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        try:
            at = _clock(book_at.astimezone(KOREA).strftime("%Y%m%d"), row.get("khms"))
            _fresh(at, observed_at)
            strength = _positive(row.get("vpow"), allow_zero=True)
        except ValueError:
            continue
        valid.append((at, strength, row))
    if not valid:
        raise ValueError("TRADE_STRENGTH_CLOCK_UNVERIFIED")
    at, strength, _ = max(valid, key=lambda item: item[0])
    return strength, at, {
        "rows": len(valid), "source": "kis.quot_inquire_ccnl.output2.vpow",
        "event_at": at.isoformat(),
        "date_basis": "TDAY_1_DATED_CURRENT_ORDERBOOK",
    }


def prior_daily_volume(rows, *, as_of):
    """Only dated, completed prior sessions; no future/current/undated rows."""
    values = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        raw = str(row.get("xymd") or row.get("XYMD") or "")
        try:
            if not re.fullmatch(r"\d{8}", raw):
                continue
            day = datetime.strptime(raw, "%Y%m%d").date()
            value = _positive(row.get("tvol", row.get("TVOL")))
        except ValueError:
            continue
        if as_of - timedelta(days=90) <= day < as_of:
            if day in values and values[day] != value:
                return None
            values[day] = value
    latest = sorted(values, reverse=True)[:20]
    return sum(values[day] for day in latest) / 20 if len(latest) == 20 else None


def _positive(value, *, allow_zero=False):
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError("INVALID_VALUE") from None
    if isinstance(value, bool) or not math.isfinite(number) or number < 0 or (number == 0 and not allow_zero):
        raise ValueError("INVALID_VALUE")
    return number


def _clock(day, hour):
    if not re.fullmatch(r"\d{8}", str(day)) or not re.fullmatch(r"\d{6}", str(hour)):
        raise ValueError("EVIDENCE_CLOCK_MISSING")
    try:
        return datetime.strptime(str(day) + str(hour), "%Y%m%d%H%M%S").replace(tzinfo=KOREA)
    except ValueError:
        raise ValueError("EVIDENCE_CLOCK_INVALID") from None


def _fresh(at, now):
    if at.tzinfo is None or now.tzinfo is None or not 0 <= (now - at).total_seconds() < 120:
        raise ValueError("EVIDENCE_STALE_OR_FUTURE")
