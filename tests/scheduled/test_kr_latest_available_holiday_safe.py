import tempfile
from datetime import date, datetime
from pathlib import Path
from unittest.mock import patch

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


def test_kr_latest_available_holiday_safe():
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
        config = load_scheduled_config(config_path)

    with (
        patch("tradingagents.scheduled.runner.datetime", _FixedDatetime),
        patch(
            "tradingagents.scheduled.runner._fetch_recent_trade_date_history",
            return_value=_FakeHistory(date(2026, 5, 4)),
        ) as fetch_history,
    ):
        trade_date = resolve_trade_date("005930.KS", config)

    assert trade_date == "2026-05-04"
    fetch_history.assert_called_once()
