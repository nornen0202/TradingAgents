import tempfile
from datetime import date, datetime
from pathlib import Path
from unittest.mock import patch
import unittest

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
        value = datetime(2026, 6, 30, 16, 0)
        return value.replace(tzinfo=tz) if tz else value


class _ConstitutionDayWeekendDatetime(datetime):
    @classmethod
    def now(cls, tz=None):
        value = datetime(2026, 7, 20, 6, 31)
        return value.replace(tzinfo=tz) if tz else value


def _config(market: str = "US"):
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "scheduled.toml"
        config_path.write_text(
            f"""
[run]
tickers = ["AAPL"]
market = "{market}"
trade_date_mode = "latest_available"
timezone = "Asia/Seoul"

[storage]
archive_dir = "./archive"
site_dir = "./site"
""",
            encoding="utf-8",
        )
        return load_scheduled_config(config_path)


class TradeDateFreshnessGuardTests(unittest.TestCase):
    def test_latest_available_refuses_vendor_date_older_than_completed_market_session(self):
        with (
            patch("tradingagents.scheduled.runner.datetime", _FixedDatetime),
            patch(
                "tradingagents.scheduled.runner._completed_daily_trade_date_from_exchange_calendar",
                return_value=date(2026, 6, 29),
            ),
            patch(
                "tradingagents.scheduled.runner._fetch_recent_trade_date_history",
                return_value=_FakeHistory(date(2026, 6, 26)),
            ),
        ):
            with self.assertRaisesRegex(RuntimeError, "Refusing stale latest_available trade date"):
                resolve_trade_date("AAPL", _config("US"))

    def test_latest_available_caps_future_or_partial_vendor_date_to_completed_market_session(self):
        with (
            patch("tradingagents.scheduled.runner.datetime", _FixedDatetime),
            patch(
                "tradingagents.scheduled.runner._completed_daily_trade_date_from_exchange_calendar",
                return_value=date(2026, 6, 29),
            ),
            patch(
                "tradingagents.scheduled.runner._fetch_recent_trade_date_history",
                return_value=_FakeHistory(date(2026, 6, 30)),
            ),
        ):
            self.assertEqual(resolve_trade_date("AAPL", _config("US")), "2026-06-29")

    def test_retryable_lookup_failure_uses_completed_market_session_not_wall_clock_business_day(self):
        with (
            patch("tradingagents.scheduled.runner.datetime", _FixedDatetime),
            patch(
                "tradingagents.scheduled.runner._completed_daily_trade_date_from_exchange_calendar",
                return_value=date(2026, 6, 29),
            ),
            patch(
                "tradingagents.scheduled.runner._fetch_recent_trade_date_history",
                side_effect=TypeError("'NoneType' object is not subscriptable"),
            ),
        ):
            self.assertEqual(resolve_trade_date("AAPL", _config("US")), "2026-06-29")

    def test_latest_available_accepts_vendor_date_before_restored_kr_constitution_day(self):
        with (
            patch("tradingagents.scheduled.runner.datetime", _ConstitutionDayWeekendDatetime),
            patch(
                "tradingagents.scheduled.runner._fetch_recent_trade_date_history",
                return_value=_FakeHistory(date(2026, 7, 16)),
            ),
        ):
            self.assertEqual(resolve_trade_date("000660.KS", _config("KR")), "2026-07-16")
