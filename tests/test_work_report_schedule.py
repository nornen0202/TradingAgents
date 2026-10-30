from datetime import datetime, date
from types import SimpleNamespace

import pytest

from tradingagents.work.schedule import scheduled_report_session


@pytest.mark.parametrize("market,clock,session,allowed", [
    ("kr", "2026-10-30T10:40:00+09:00", "2026-10-30", True),
    ("kr", "2026-10-31T10:40:00+09:00", "2026-10-31", False),
    ("us", "2026-10-31T03:10:00+09:00", "2026-10-30", True),
    ("us", "2026-10-31T23:10:00+09:00", "2026-10-31", False),
    ("us", "2026-11-02T01:10:00+09:00", "2026-11-01", False),
    ("us", "2026-11-03T03:10:00+09:00", "2026-11-02", True),  # After US DST ends.
])
def test_market_local_weekends_and_dst(market, clock, session, allowed):
    def resolve(**kwargs):
        assert allowed  # Weekends require no API.
        return SimpleNamespace(session_date=date.fromisoformat(session), is_session=True, source="fixture")
    receipt = scheduled_report_session(market, now=datetime.fromisoformat(clock), resolver=resolve)
    assert receipt["session_date"] == session
    assert receipt["status"] == ("TRADING_DAY" if allowed else "SKIP_NON_TRADING_DAY")


@pytest.mark.parametrize("market,clock,session", [
    ("kr", "2026-10-09T10:40:00+09:00", "2026-10-09"),
    ("us", "2026-11-27T03:10:00+09:00", "2026-11-26"),
])
def test_confirmed_holidays_skip(market, clock, session):
    status = SimpleNamespace(session_date=date.fromisoformat(session), is_session=False, source="fixture")
    receipt = scheduled_report_session(market, now=datetime.fromisoformat(clock), resolver=lambda **_: status)
    assert receipt["status"] == "SKIP_NON_TRADING_DAY"


@pytest.mark.parametrize("kind", ["empty", "unknown", "wrong_date", "error"])
def test_calendar_outage_does_not_suppress_investor_research(kind):
    def resolve(**kwargs):
        if kind == "error": raise OSError("offline")
        if kind == "empty": return None
        return SimpleNamespace(session_date=date(2026, 10, 29 if kind == "wrong_date" else 30),
                               is_session=False if kind == "wrong_date" else None, source="fixture")
    receipt = scheduled_report_session("kr", now=datetime.fromisoformat("2026-10-30T10:40:00+09:00"), resolver=resolve)
    assert receipt["status"] == "CALENDAR_UNVERIFIED_REPORT_ALLOWED"


def test_cli_closed_day_does_not_prepare_or_write_runtime(monkeypatch, capsys):
    from tradingagents.work import __main__ as cli, schedule
    monkeypatch.setattr("sys.argv", ["work", "prepare", "--surface", "us", "--scheduled-market"])
    monkeypatch.setattr(schedule, "scheduled_report_session", lambda _: {"status": "SKIP_NON_TRADING_DAY"})
    monkeypatch.setattr(cli, "WorkRuntime", lambda *_: pytest.fail("must skip before allocating event"))
    assert cli.main() == 0
    assert "SKIP_NON_TRADING_DAY" in capsys.readouterr().out


def test_saved_market_prompts_use_the_deterministic_schedule_gate():
    import json
    from pathlib import Path
    tasks = json.loads(Path("config/chatgpt_work_tasks.json").read_text(encoding="utf-8"))["tasks"]
    for task in tasks:
        if task["surface"] in {"kr", "us"}:
            assert "prepare --scheduled-market --report-policy investor" in task["prompt"]
            assert "SKIP_NON_TRADING_DAY" in task["prompt"]


@pytest.mark.parametrize("options", [["--surface", "youtube"], ["--surface", "us", "--refresh-market"],
                                    ["--surface", "kr", "--report-policy", "execution"]])
def test_calendar_reporting_exception_cannot_enable_execution(monkeypatch, options):
    from tradingagents.work import __main__ as cli
    monkeypatch.setattr("sys.argv", ["work", "prepare", "--scheduled-market", *options])
    with pytest.raises(SystemExit) as error:
        cli.main()
    assert error.value.code == 2
