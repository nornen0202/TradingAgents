"""Serialize exchange calendar construction and its process-global caches."""
from threading import RLock

_calendar_lock = RLock()


def get_exchange_calendar(name, **kwargs):
    # XKRX holiday construction mutates shared pandas Series upstream. Keep
    # all application construction paths under the same process-local lock;
    # do not hold it while fetching market data or calculating indicators.
    with _calendar_lock:
        import exchange_calendars

        return exchange_calendars.get_calendar(name, **kwargs)
