from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from tradingagents.scheduled.config import load_scheduled_config
from tradingagents.scheduled.market_calendar import is_supplemental_market_holiday, market_session_state
from tradingagents.scheduled.runner import _effective_execution_checkpoints, _execution_checkpoint_timezone, _select_due_checkpoints


def test_us_local_checkpoints_use_new_york_timezone(tmp_path: Path):
    config_path = tmp_path / "scheduled.toml"
    config_path.write_text(
        f"""
[run]
tickers = ["AAPL"]
market = "US"
timezone = "Asia/Seoul"

[storage]
archive_dir = "{(tmp_path / 'archive').as_posix()}"
site_dir = "{(tmp_path / 'site').as_posix()}"

[execution]
enabled = true
checkpoints_local = ["10:00", "11:00", "15:50"]
checkpoint_timezone = "America/New_York"
session_calendar = "XNYS"
""",
        encoding="utf-8",
    )
    config = load_scheduled_config(config_path)

    assert _execution_checkpoint_timezone(config) == "America/New_York"
    assert _effective_execution_checkpoints(config) == ["10:00", "11:00", "15:50"]


def test_select_due_checkpoints_uses_local_wall_clock_for_us_dst():
    now_local = datetime(2026, 7, 1, 11, 5, tzinfo=ZoneInfo("America/New_York"))
    due, phase = _select_due_checkpoints(
        now_local=now_local,
        checkpoints=["10:00", "11:00", "12:00", "15:50"],
    )

    assert due == ["11:00"]
    assert phase == "CHECKPOINT_11_00"


def test_market_session_fallback_handles_us_regular_session():
    state = market_session_state(
        market="US",
        now_local=datetime(2026, 1, 5, 10, 0, tzinfo=ZoneInfo("America/New_York")),
        calendar_name="XNYS",
    )

    assert state["is_open"] is True
    assert state["phase"] == "regular"


def test_market_session_closes_for_restored_kr_constitution_day():
    state = market_session_state(
        market="KR",
        now_local=datetime(2026, 7, 17, 10, 0, tzinfo=ZoneInfo("Asia/Seoul")),
        calendar_name="XKRX",
    )

    assert state["is_open"] is False
    assert state["phase"] == "closed"
    assert state["source"] == "supplemental_market_holiday"


def test_restored_kr_constitution_day_has_substitute_holiday():
    assert is_supplemental_market_holiday(market="KR", session_date=date(2027, 7, 17))
    assert is_supplemental_market_holiday(market="KR", session_date=date(2027, 7, 19))
    assert not is_supplemental_market_holiday(market="KR", session_date=date(2027, 7, 20))
