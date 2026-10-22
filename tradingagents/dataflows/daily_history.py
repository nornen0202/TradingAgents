"""Dispatch independent daily history recovery without mixing price sources."""
from . import kr_daily_history as kr, us_daily_history as us


def fallback_enabled(symbol):
    return kr.fallback_enabled(symbol) or us.fallback_enabled(symbol)


def selected_history(symbol, start_date, end_date):
    return us.selected_history(symbol, start_date, end_date)


def validate_with_fallback(data, symbol, start_date, end_date):
    if us.fallback_enabled(symbol):
        return us.validate_with_us_fallback(data, symbol, start_date, end_date)
    return kr.validate_with_kr_fallback(data, symbol, start_date, end_date)


def source_note(frame):
    return us.source_note(frame) or kr.source_note(frame)
