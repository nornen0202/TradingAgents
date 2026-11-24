"""Read-only KIS regular closes and validation for report observations."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import math
import re
from time import monotonic, sleep
from zoneinfo import ZoneInfo

from tradingagents.calendar_access import get_exchange_calendar
from tradingagents.dataflows.intraday.us_symbols import kis_symbol
from tradingagents.dataflows.market_policy import aware_datetime, source_use_policy
from tradingagents.scheduled.market_calendar import default_calendar_name, is_supplemental_market_holiday

ZONES = {"KR": ZoneInfo("Asia/Seoul"), "US": ZoneInfo("America/New_York")}
CURRENCIES = {"KR": "KRW", "US": "USD"}
_SETTLE = timedelta(minutes=5)


def market_days(market, now, start=None, through=None):
    local = now.astimezone(ZONES[market]).date()
    try:
        calendar = get_exchange_calendar(default_calendar_name(market))
        days = calendar.sessions_in_range(start or local - timedelta(days=10), through or local + timedelta(days=10))
        return {day.date(): (calendar.session_open(day).to_pydatetime(), calendar.session_close(day).to_pydatetime())
                for day in days if not is_supplemental_market_holiday(market=market, session_date=day.date())}
    except (ImportError, ValueError, KeyError, OverflowError):
        return {}


def price_epoch(now):
    """Rebuild when the latest publishable completed regular session changes."""
    return tuple(max((day.isoformat() for day, (_, close) in market_days(market, now).items()
                      if close + _SETTLE <= now), default=None) for market in ("KR", "US"))


def positive(value):
    try:
        return type(value) in (int, float) and math.isfinite(value) and value > 0
    except OverflowError:
        return False


def price_equal(a, b):
    return positive(a) and positive(b) and math.isclose(a, b, abs_tol=0.001, rel_tol=1e-7)


def validated_quote(raw, market, days, now):
    quote = raw or {}
    source = source_use_policy(quote.get("source"))
    event, observed, published, provider_at = (aware_datetime(quote.get(key)) for key in
        ("event_at", "observed_at", "published_at", "provider_at"))
    venues = {"KRX", "J"} if market == "KR" else {"NAS", "NYS", "AMS", "NASDAQ", "NYSE", "AMEX", "US_SIP"}
    if (source["provider"] not in {"kis_microstructure", "kis_us_microstructure", "kis_quote", "massive", "alpaca"}
            or not source["allowed"] or not positive(quote.get("price")) or event is None or observed is None
            or not event <= observed <= now or quote.get("market_session") != "regular"
            or quote.get("category") not in {"REALTIME_EXECUTION_READY", "DELAYED_ANALYSIS_ONLY"}
            or quote.get("exchange") not in venues or quote.get("currency") not in (None, CURRENCIES[market])
            or quote.get("adjustment") not in (None, "unadjusted")
            or (source["provider"] in {"massive", "alpaca"} and quote.get("adjustment") != "unadjusted")
            or any(quote.get(key) and (value is None or not event <= value <= now)
                   for key, value in (("published_at", published), ("provider_at", provider_at)))):
        return None
    day = event.astimezone(ZONES[market]).date()
    window = days.get(day)
    if not window or not window[0] <= event < window[1]:
        return None
    current = window[0] <= now < window[1]
    age = int((now - event).total_seconds())
    return {
        "kind": ("REGULAR_QUOTE" if age < 180 and quote["category"] == "REALTIME_EXECUTION_READY"
                 else "DELAYED_REGULAR_QUOTE") if current else "HISTORICAL_REGULAR_QUOTE",
        "price": quote["price"], "currency": CURRENCIES[market], "adjustment": "unadjusted",
        "source": source["provider"], "exchange": quote["exchange"], "session": day.isoformat(),
        "event_at": event.isoformat(), "observed_at": observed.isoformat(), "age_seconds": age,
    }


def _rows(payload, market, start, end):
    names = (("stck_bsop_date", "stck_oprc", "stck_clpr", "stck_hgpr", "stck_lwpr", "acml_vol") if market == "KR"
             else ("xymd", "open", "clos", "high", "low", "tvol"))
    rows = payload.get("output2") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        return {}
    result, ambiguous = {}, set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        try:
            day = datetime.strptime(row[names[0]], "%Y%m%d").date()
            if not start <= day <= end:
                continue
            opening, close, high, low, volume = (float(row[key]) for key in names[1:])
            if not all(positive(value) for value in (opening, close, high, low, volume)) or not low <= min(opening, close) <= max(opening, close) <= high:
                continue
        except (KeyError, TypeError, ValueError):
            continue
        if day in result:
            ambiguous.add(day)
        result[day] = {"price": close, "open": opening, "high": high, "low": low, "volume": volume}
    return {day: item for day, item in result.items() if day not in ambiguous}


class KisResearchCloses:
    """Use the existing approved KIS read-only quotation endpoints with explicit price basis."""

    def __init__(self, client, *, clock=lambda: datetime.now(timezone.utc), budget_seconds=100):
        self.client = client
        self.clock = clock
        self.deadline = monotonic() + budget_seconds
        self.next_request = 0.0

    @classmethod
    def configured(cls):
        from tradingagents.portfolio.kis import KisClient, PortfolioConfigurationError

        try:
            client = KisClient.from_api_keys(environment="real")
        except (PortfolioConfigurationError, ValueError):
            return None
        return cls(client)

    def _download(self, market, ticker, venue, start, end, adjusted):
        if monotonic() >= self.deadline:
            return {}
        sleep(max(0, self.next_request - monotonic()))
        self.next_request = monotonic() + 0.25
        if market == "KR":
            return self.client.domestic_daily_itemchartprice(ticker[:6], start_date=start, end_date=end,
                market_division="J", period_division="D", adjusted_price="0" if adjusted else "1")
        symbol = kis_symbol(ticker)
        payload, _ = self.client.request_json(method="GET", path="/uapi/overseas-price/v1/quotations/dailyprice",
            tr_id="HHDFS76240000", params={"AUTH": "", "EXCD": venue, "SYMB": symbol, "GUBN": "0",
                "BYMD": end.strftime("%Y%m%d"), "MODP": "1" if adjusted else "0"})
        header = payload.get("output1") if isinstance(payload, dict) else None
        identity = header.get("rsym") if isinstance(header, dict) else None
        return payload if identity == f"D{venue}{symbol}" else {}

    def __call__(self, market, ticker, days, start, now, exchange=None):
        ticker_pattern = r"\d{6}(?:\.(?:KS|KQ))?" if market == "KR" else r"[A-Z][A-Z0-9.-]{0,14}"
        if not re.fullmatch(ticker_pattern, ticker):
            return {}
        completed = {day: close for day, (_, close) in days.items() if start <= day and close + _SETTLE <= now}
        if not completed:
            return {}
        end = max(completed)
        from tradingagents.portfolio.kis import KisApiError
        venues = ("KRX",) if market == "KR" else tuple(dict.fromkeys(
            ([exchange] if exchange in {"NAS", "NYS", "AMS"} else []) + ["NAS", "NYS", "AMS"]))
        for venue in venues:
            try:
                raw = _rows(self._download(market, ticker, venue, start, end, False), market, start, end)
            except (OSError, RuntimeError, ValueError, TypeError, KisApiError):
                continue
            if not raw:
                continue
            received = self.clock()
            try:
                adjusted = _rows(self._download(market, ticker, venue, start, end, True), market, start, end)
            except (OSError, RuntimeError, ValueError, TypeError, KisApiError):
                adjusted = {}
            basis_observed = self.clock() if adjusted else None
            return {day: {**raw[day], "kind": "REGULAR_CLOSE", "source": "KIS",
                          "session": day.isoformat(), "event_at": completed[day].isoformat(),
                          "observed_at": received.isoformat(), "currency": CURRENCIES[market], "exchange": venue,
                          "adjustment": "unadjusted",
                          "adjusted_close": (adjusted.get(day) or {}).get("price"),
                          "adjustment_checked_at": basis_observed.isoformat() if basis_observed else None,
                          "adjustment_check": "FID_ORG_ADJ_PRC=0" if market == "KR" else "MODP=1"}
                    for day in sorted(raw.keys() & completed.keys()) if received >= completed[day] + _SETTLE}
        return {}

