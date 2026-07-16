import tempfile
from datetime import date, datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from tradingagents.scheduled.config import load_scheduled_config
from tradingagents.scheduled.runner import resolve_trade_date


class _FakeIndexValue:
    def __init__(self, value: date):
        self._value = value

    def to_pydatetime(self):
        return datetime.combine(self._value, datetime.min.time())


class _FakeHistory:
    empty = False

    def __init__(self, value: date):
        self.index = [_FakeIndexValue(value)]


class _FixedDatetime(datetime):
    @classmethod
    def now(cls, tz=None):
        value = datetime(2026, 5, 6, 10, 0)
        return value.replace(tzinfo=tz) if tz else value


def _kr_config():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "scheduled.toml"
        config_path.write_text(
            """
[run]
tickers = ["005930.KS"]
market = "KR"
trade_date_mode = "latest_available"
timezone = "Asia/Seoul"

[storage]
archive_dir = "./archive"
site_dir = "./site"
""",
            encoding="utf-8",
        )
        return load_scheduled_config(config_path)


def test_kr_latest_available_holiday_safe():
    config = _kr_config()

    with (
        patch("tradingagents.scheduled.runner.datetime", _FixedDatetime),
        patch(
            "tradingagents.scheduled.runner._completed_daily_trade_date_from_exchange_calendar",
            return_value=None,
        ),
        patch(
            "tradingagents.scheduled.runner._fetch_recent_trade_date_history",
            return_value=_FakeHistory(date(2026, 5, 4)),
        ) as fetch_history,
    ):
        trade_date = resolve_trade_date("005930.KS", config)

    assert trade_date == "2026-05-04"
    fetch_history.assert_called_once()


def test_kr_latest_available_fails_closed_when_calendar_and_vendor_are_unavailable():
    config = _kr_config()

    with (
        patch("tradingagents.scheduled.runner.datetime", _FixedDatetime),
        patch(
            "tradingagents.scheduled.runner._completed_daily_trade_date_from_exchange_calendar",
            return_value=None,
        ),
        patch(
            "tradingagents.scheduled.runner._completed_daily_trade_date_for_kr"
        ) as weekday_fallback,
        patch(
            "tradingagents.scheduled.runner._fetch_recent_trade_date_history",
            side_effect=TypeError("'NoneType' object is not subscriptable"),
        ),
    ):
        with pytest.raises(RuntimeError, match="Refusing to synthesize an unverified"):
            resolve_trade_date("005930.KS", config)

    weekday_fallback.assert_not_called()
