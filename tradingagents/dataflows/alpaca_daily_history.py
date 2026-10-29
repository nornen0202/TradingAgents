"""Complete adjusted SIP daily history from the existing Alpaca data connection.

This is a separate series, never a row-level repair of Yahoo or KIS prices.
"""
from datetime import date, datetime, time as day_time, timedelta, timezone
import hashlib
import math
import os
import time
from zoneinfo import ZoneInfo

import pandas as pd
import requests

from .api_keys import get_api_key
from .integrity import safe_symbol, validate_daily_bars
from .vendor_exceptions import VendorInputError, VendorMalformedResponseError

SOURCE = 'Alpaca SIP daily bars (adjustment=all)'
ENABLED = 'TRADINGAGENTS_ALPACA_RESEARCH_FALLBACK_ENABLED'
URL = 'https://data.alpaca.markets/v2/stocks/bars'


def load_us_daily_bars(symbol, start_date, end_date):
    if os.getenv(ENABLED) != '1':
        return None
    key, secret = get_api_key('ALPACA_API_KEY_ID'), get_api_key('ALPACA_SECRET_KEY')
    if not key or not secret:
        return None
    symbol = safe_symbol(symbol)
    from .us_daily_history import _sessions, fallback_enabled
    if not fallback_enabled(symbol):
        return None
    try:
        start, end = date.fromisoformat(start_date), date.fromisoformat(end_date)
    except (ValueError, TypeError) as exc:
        raise VendorInputError('Alpaca history requires ISO dates') from exc
    if start > end:
        raise VendorInputError('History start is after end')
    start = min(start, (pd.Timestamp(end) - pd.DateOffset(years=5)).date())
    required = _sessions(start, end)
    from tradingagents.calendar_access import get_exchange_calendar
    calendar = get_exchange_calendar('XNYS')
    cutoff = calendar.session_close(required[-1].isoformat()).to_pydatetime().astimezone(timezone.utc)
    if cutoff > datetime.now(timezone.utc) - timedelta(minutes=15):
        raise VendorMalformedResponseError('Completed SIP session is not yet available with the historical delay')
    api_symbol = 'BRK.B' if symbol == 'BRK-B' else symbol
    params = {'symbols': api_symbol, 'timeframe': '1Day', 'start': datetime.combine(start, day_time(), ZoneInfo('America/New_York')).isoformat(),
              'end': cutoff.isoformat(), 'asof': end_date, 'feed': 'sip', 'adjustment': 'all',
              'sort': 'asc', 'limit': '10000', 'currency': 'USD'}
    headers = {'APCA-API-KEY-ID': key, 'APCA-API-SECRET-KEY': secret}
    records, tokens = {}, set()
    began = time.monotonic()
    for page in range(10):
        if time.monotonic() - began >= 60:
            raise VendorMalformedResponseError('Alpaca history exceeded its time limit')
        try:
            response = requests.get(URL, headers=headers, params=params, timeout=20, allow_redirects=False)
            if response.status_code != 200:
                raise VendorMalformedResponseError(f'Alpaca SIP history unavailable (HTTP {response.status_code})')
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise VendorMalformedResponseError('Alpaca history request failed') from exc
        bars = payload.get('bars') if isinstance(payload, dict) else None
        rows = bars.get(api_symbol) if isinstance(bars, dict) else None
        if not isinstance(rows, list) or not rows:
            raise VendorMalformedResponseError('Alpaca history has no requested bars')
        before = len(records)
        for row in rows:
            try:
                stamp = pd.Timestamp(row['t'])
                if pd.isna(stamp) or stamp.tzinfo is None:
                    raise ValueError('Unknown daily timestamp')
                local = stamp.tz_convert('America/New_York')
                day = local.date()
                if day > end or day < start:
                    continue
                if local.hour or local.minute or local.second or local.microsecond or local.nanosecond:
                    raise ValueError('Not an exchange daily label')
                values = {name: float(row[field]) for name, field in
                          {'Open':'o','High':'h','Low':'l','Close':'c','Volume':'v'}.items()}
                if (any(not math.isfinite(v) or v < 0 or (name != 'Volume' and v == 0) for name,v in values.items())
                        or values['High'] < max(values['Open'],values['Low'],values['Close'])
                        or values['Low'] > min(values['Open'],values['Close'])):
                    raise ValueError('Invalid OHLCV')
            except (ValueError, KeyError, TypeError, OverflowError) as exc:
                raise VendorMalformedResponseError('Alpaca history contains invalid dates or OHLCV') from exc
            if day in records and records[day] != values:
                raise VendorMalformedResponseError('Alpaca history contains conflicting duplicate sessions')
            records[day] = values
        token = payload.get('next_page_token')
        if not token:
            break
        if not isinstance(token,str) or token in tokens or len(records) == before:
            raise VendorMalformedResponseError('Alpaca history pagination made no progress')
        tokens.add(token)
        params['page_token'] = token
    else:
        raise VendorMalformedResponseError('Alpaca history exceeded its page limit')
    if time.monotonic() - began >= 60 or set(records) != set(required):
        raise VendorMalformedResponseError('Alpaca history is incomplete or exceeded its time limit')
    frame = validate_daily_bars(pd.DataFrame([{'Date':day,**values} for day,values in sorted(records.items())]),end_date)
    frame.attrs.update(source=SOURCE, provider='alpaca', exchange='US_SIP', feed='sip', adjustment='all',
                       observed_at=datetime.now(timezone.utc).isoformat(), requested_start=start.isoformat(),
                       requested_end=end_date, request_end=cutoff.isoformat(), symbol_asof=end_date,
                       complete=True, session_count=len(required), request_count=page+1,
                       series_sha256=hashlib.sha256(frame.to_csv(index=False).encode('utf-8')).hexdigest())
    return frame
