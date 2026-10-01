from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from tradingagents.scheduled import market_calendar


@pytest.mark.parametrize(
    "market,zone,stamp,is_open,close_at",
    [
        ("US", "America/New_York", "2026-10-01T10:00:33", True, "2026-10-01T16:00:00-04:00"),
        ("US", "America/New_York", "2026-11-27T12:59:33", True, "2026-11-27T13:00:00-05:00"),
        ("US", "America/New_York", "2026-11-27T14:00:00", False, "2026-11-27T13:00:00-05:00"),
        ("US", "America/New_York", "2026-11-02T10:00:01", True, "2026-11-02T16:00:00-05:00"),
        ("KR", "Asia/Seoul", "2026-10-01T13:00:42", True, "2026-10-01T15:30:00+09:00"),
    ],
)
def test_installed_calendar_api_handles_seconds_dst_and_early_closes(market, zone, stamp, is_open, close_at):
    state = market_calendar.market_session_state(
        market=market, now_local=datetime.fromisoformat(stamp).replace(tzinfo=ZoneInfo(zone)),
    )
    assert state["source"] == "exchange_calendars"
    assert state["is_open"] is is_open
    assert state["session_close"] == close_at


def test_us_thanksgiving_is_not_a_regular_thursday():
    state = market_calendar.market_session_state(
        market="US", now_local=datetime(2026, 11, 26, 10, 0, tzinfo=ZoneInfo("America/New_York")),
    )
    assert state["source"] == "exchange_calendars"
    assert state["is_open"] is False


def test_calendar_failure_cannot_open_execution_gate(monkeypatch):
    monkeypatch.setattr(market_calendar, "_exchange_calendar_state", lambda **kwargs: None)
    state = market_calendar.market_session_state(
        market="US", now_local=datetime(2026, 11, 27, 14, 0, tzinfo=ZoneInfo("America/New_York")),
    )
    assert state["is_open"] is False
    assert state["phase"] == "unknown"
    assert state["estimated_is_open"] is True
    assert state["reason"] == "exchange_calendar_unavailable"
