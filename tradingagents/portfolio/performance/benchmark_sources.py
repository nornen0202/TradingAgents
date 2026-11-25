"""Session-bounded Yahoo benchmark inputs. The cache never contains account data."""
from datetime import date, datetime, timedelta, timezone
from hashlib import sha256
import json
import math
from pathlib import Path
from zoneinfo import ZoneInfo

from tradingagents.atomic_io import atomic_write_json
from tradingagents.calendar_access import get_exchange_calendar
from tradingagents.charting.bars import instant
from tradingagents.dataflows.stockstats_utils import yf_retry
from tradingagents.scheduled.market_calendar import is_supplemental_market_holiday


_YAHOO_FX_ZONE = ZoneInfo("Europe/London")


def _checksum(rows):
    return sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _download(symbol, start, end, *, fx):
    import yfinance as yf

    ticker = yf.Ticker(symbol)
    data = yf_retry(
        lambda: ticker.history(start=start.isoformat(), end=(end + timedelta(days=1)).isoformat(),
                               auto_adjust=not fx, actions=not fx, timeout=8, raise_errors=True),
        max_retries=1, base_delay=1,
    )
    if data.empty:
        raise ValueError("empty_history")
    return data, ticker.get_history_metadata()


def load_yahoo_benchmark(symbol, currency, start, end, *, as_of, cache_dir: Path | None = None, fx=False):
    """Return complete selected sessions plus a sanitized acquisition receipt."""
    cutoff = instant(as_of)
    now = datetime.now(timezone.utc)
    if cutoff is None or cutoff > now:
        return [], {"state": "as_of_unverified"}
    required = []
    try:
        if not fx:
            market = "KR" if symbol.endswith((".KS", ".KQ")) else "US"
            calendar = get_exchange_calendar("XKRX" if market == "KR" else "XNYS")
            required = [session.date() for session in calendar.sessions_in_range(start.isoformat(), end.isoformat())
                        if not is_supplemental_market_holiday(market=market, session_date=session.date())
                        and calendar.session_close(session).to_pydatetime() <= cutoff]
            if not required:
                return [], {"state": "no_completed_rows"}
    except (ValueError, TypeError, KeyError, OverflowError):
        return [], {"state": "session_calendar_unavailable"}
    eligible_through = cutoff.astimezone(_YAHOO_FX_ZONE).date() if fx else required[-1]
    request = [symbol, currency, start.isoformat(), end.isoformat(),
               _YAHOO_FX_ZONE.key if fx else None, eligible_through.isoformat()]
    path = cache_dir / (sha256(json.dumps(request).encode()).hexdigest() + ".json") if cache_dir else None
    fetched = None
    input_origin = "fresh"
    if path and path.is_file():
        try:
            candidate = json.loads(path.read_bytes())
            checked = instant(candidate["observed_at"])
            if (candidate["request"] == request and checked and timedelta(0) <= now - checked <= timedelta(hours=12)
                    and candidate["payload_sha256"] == _checksum(candidate["rows"])):
                fetched = candidate
                input_origin = "cache"
        except (OSError, ValueError, TypeError, KeyError):
            pass
    if fetched is None:
        try:
            data, meta = _download(symbol, start, end, fx=fx)
            if (meta.get("symbol") != symbol or meta.get("currency") != currency
                    or (fx and meta.get("instrumentType") != "CURRENCY")):
                return [], {"state": "provider_instrument_or_currency_unverified"}
            if not fx and not {"Dividends", "Stock Splits", "Close"} <= set(data.columns):
                return [], {"state": "adjustment_evidence_missing"}
            records = []
            for index, values in data.iterrows():
                amount = float(values["Close"])
                if not math.isfinite(amount) or amount <= 0:
                    continue
                row = {"date": index.date().isoformat(), "close": amount}
                if not fx:
                    row.update(dividend=float(values["Dividends"]), split=float(values["Stock Splits"]))
                    if (not all(math.isfinite(row[key]) for key in ("dividend", "split"))
                            or min(row["dividend"], row["split"]) < 0):
                        return [], {"state": "adjustment_evidence_invalid"}
                records.append(row)
            if fx and (meta.get("exchangeTimezoneName") != _YAHOO_FX_ZONE.key
                       or str(getattr(data.index, "tz", None)) != _YAHOO_FX_ZONE.key):
                return [], {"state": "fx_source_timezone_unverified"}
            fetched = {"request": request, "observed_at": datetime.now(timezone.utc).isoformat(),
                       "exchange": meta.get("exchangeName"), "rows": records, "payload_sha256": _checksum(records)}
        except Exception as exc:
            return [], {"state": "provider_unavailable", "failure_type": type(exc).__name__}
    try:
        selected = {}
        for raw in fetched["rows"]:
            session = date.fromisoformat(raw["date"])
            if not start <= session <= end:
                continue
            if session in selected or not math.isfinite(raw["close"]) or raw["close"] <= 0:
                return [], {"state": "invalid_or_duplicate_vendor_row"}
            selected[session] = raw
        if fx:
            # Yahoo's daily FX label is insufficient to time same-day settlement.
            # Use only past daily marks and document that this is a proxy.
            rows = [row | {"source": "yfinance", "fx_method": "prior_daily_mark"}
                    for day, row in sorted(selected.items()) if day < eligible_through and day.weekday() < 5]
            missing = 0
        else:
            missing = sum(day not in selected for day in required)
            rows = [selected[day] for day in required if day in selected]
    except (ValueError, TypeError, KeyError, OverflowError):
        return [], {"state": "unverified_session_or_vendor_row"}
    if path and input_origin == "fresh" and rows and not missing:
        try:
            atomic_write_json(path, fetched)
        except OSError:
            input_origin = "fresh_cache_write_failed"
    receipt = {
        "state": "missing_sessions" if missing else ("available" if rows else "no_completed_rows"),
        "rows": len(rows), "missing_sessions": missing, "provider": "yfinance", "symbol": symbol,
        "currency": currency, "exchange": fetched.get("exchange"), "input_origin": input_origin,
        "observed_at": fetched["observed_at"], "as_of": cutoff.isoformat(),
        "price_basis": "close" if fx else "adjusted_close",
        "historical_vintage_verified": False,
        "first_session": rows[0]["date"] if rows else None, "last_session": rows[-1]["date"] if rows else None,
        "series_sha256": _checksum(rows),
    }
    if fx:
        receipt.update(pair="USD/KRW", units="KRW per USD", method="prior_daily_mark",
                       source_timezone=_YAHOO_FX_ZONE.key)
    else:
        receipt.update(dividend_event_count=sum(row["dividend"] > 0 for row in rows),
                       split_event_count=sum(row["split"] > 0 for row in rows),
                       distributions="embedded_in_provider_adjusted_close")
    return (rows if not missing else []), receipt
