"""Serialize exchange calendar construction and its process-global caches."""
from datetime import date
from functools import lru_cache
from threading import RLock

_calendar_lock = RLock()


@lru_cache(maxsize=2)
def _default_calendar(factory, name, day):
    # Upstream caches only the last start/end parameterization per exchange.
    # History queries otherwise evict the expensive default session calendar.
    # Retain only KR/US defaults, keyed by factory identity and actual day;
    # explicit ranges and official daily closure checks keep their own paths.
    return factory(name)


def get_exchange_calendar(name, **kwargs):
    # XKRX holiday construction mutates shared pandas Series upstream. Keep
    # all application construction paths under the same process-local lock;
    # do not hold it while fetching market data or calculating indicators.
    with _calendar_lock:
        import exchange_calendars

        if not kwargs and name in {"XKRX", "XNYS"}:
            return _default_calendar(exchange_calendars.get_calendar, name, date.today())
        return exchange_calendars.get_calendar(name, **kwargs)
