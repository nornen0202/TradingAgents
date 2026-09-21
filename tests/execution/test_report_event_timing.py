import pandas as pd
import pytest

from tools.evaluate_report_signals import next_open_index


def test_us_local_time_does_not_trade_before_publication():
    dates = pd.to_datetime(["2026-09-08", "2026-09-09"])
    assert next_open_index(dates, "2026-09-08T23:30:00+09:00", "us") == 1
    assert next_open_index(dates, "2026-09-08T21:30:00+09:00", "us") == 0


def test_missing_holiday_bar_is_not_invented():
    dates = pd.to_datetime(["2026-09-04", "2026-09-08"])
    assert next_open_index(dates, "2026-09-07T10:00:00-04:00", "us") == 1


def test_naive_publication_time_rejected():
    with pytest.raises(ValueError):
        next_open_index(pd.to_datetime(["2026-09-08"]), "2026-09-08T10:00:00", "kr")
