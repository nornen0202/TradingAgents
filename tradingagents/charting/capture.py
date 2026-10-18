"""Capture already acquired data in the current analysis, without another API call."""
from __future__ import annotations

from contextvars import ContextVar
from datetime import datetime, timedelta, timezone
from threading import Lock
from zoneinfo import ZoneInfo

from .bars import instant, validate_bars

_ACTIVE = ContextVar("tradingagents_chart_capture", default=None)


class ChartCapture:
    def __init__(self, ticker):
        self.ticker, self._rows, self._lock = ticker, [], Lock()
        self._providers = set()

    def activate(self):
        return _ACTIVE.set(self)

    @staticmethod
    def reset(token):
        _ACTIVE.reset(token)

    def add(self, rows, *, provider="yfinance"):
        with self._lock:
            self._rows.extend(rows)
            self._providers.add(provider)

    def artifact(self, *, analysis_as_of):
        with self._lock:
            result = validate_bars(self._rows, analysis_as_of=analysis_as_of)
            providers = sorted(self._providers)
        return {**result, "ticker": self.ticker, "public_display_allowed": False,
                "execution_authorized": False, "source": "existing_analysis_inputs",
                "provider": providers[0] if len(providers) == 1 else "local_archive",
                "providers": providers,
                "price_basis": "provider_adjustment_basis; never combine daily and intraday"}


def capture_daily_frame(ticker, frame, *, curr_date):
    recorder = _ACTIVE.get()
    if recorder is None or recorder.ticker != ticker:
        return
    import exchange_calendars as xcals
    from datetime import date
    from tradingagents.scheduled.market_calendar import is_supplemental_market_holiday
    market = "KR" if ticker[:6].isdigit() else "US"
    calendar = xcals.get_calendar("XKRX" if market == "KR" else "XNYS")
    observed = datetime.now(timezone.utc)
    rows = []
    for row in frame.tail(260).to_dict("records"):
        day = str(row.get("Date", ""))[:10]
        try:
            if day > str(curr_date)[:10] or not calendar.is_session(day):
                continue
            if is_supplemental_market_holiday(market=market, session_date=date.fromisoformat(day)):
                continue
            completed = calendar.session_close(day).to_pydatetime()
        except (ValueError, TypeError, KeyError):
            continue
        if completed > observed:
            continue
        rows.append({**{key: row.get(key.title()) for key in ("open", "high", "low", "close", "volume")},
                     "timestamp": completed.isoformat(), "available_at": completed.isoformat(),
                     "observed_at": observed.isoformat(), "session_id": day, "interval": "1d"})
    source = str(frame.attrs.get("source") or "")
    recorder.add(rows, provider="kis" if source.startswith("KIS domestic_daily_itemchartprice") else "yfinance")


def normalize_kis_bars(rows, *, observed_at, timezone_name):
    """KIS time-item chart bars have explicit business-date + one-minute start clocks."""
    observed = instant(observed_at)
    if observed is None:
        raise ValueError("observed_at must include a timezone")
    result = []
    fields = {"open": ("stck_oprc", "open", "OPEN"), "high": ("stck_hgpr", "high", "HIGH"),
              "low": ("stck_lwpr", "low", "LOW"), "close": ("stck_prpr", "last", "LAST", "close"),
              "volume": ("cntg_vol", "evol", "EVOL", "volume")}
    for row in rows:
        day = str(row.get("stck_bsop_date") or row.get("xymd") or row.get("XYMD") or "")
        time = str(row.get("stck_cntg_hour") or row.get("xhms") or row.get("XHMS") or "")
        try:
            stamp = datetime.strptime(day + time, "%Y%m%d%H%M%S").replace(tzinfo=ZoneInfo(timezone_name))
        except ValueError:
            continue
        result.append({**{key: next((row[name] for name in names if name in row), None) for key, names in fields.items()},
                       "timestamp": stamp.isoformat(), "available_at": (stamp + timedelta(minutes=1)).isoformat(),
                       "observed_at": observed.isoformat(), "session_id": stamp.date().isoformat(), "interval": "1m"})
    return validate_bars(result, analysis_as_of=observed)["bars"]
