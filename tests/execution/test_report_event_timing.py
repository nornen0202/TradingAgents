import pandas as pd
import pytest

from tools.evaluate_report_signals import next_open_index, publication_key
from tools.audit_strategy_history import available_after_run


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


def test_analysis_before_open_is_not_available_until_run_finishes():
    at = available_after_run("2026-09-15T08:19:00+09:00", "2026-09-15T10:46:00+09:00")
    assert next_open_index(pd.to_datetime(["2026-09-15", "2026-09-16"]), at, "kr") == 1
    assert available_after_run("2026-09-15T08:19:00+09:00", None) is None


def test_first_publication_order_uses_instants_not_timestamp_strings():
    rows = [
        {"available_at": "2026-09-15T08:00:00+09:00"},
        {"available_at": "2026-09-15T00:00:00+00:00"},
    ]
    assert sorted(rows, key=publication_key)[0] == rows[0]
