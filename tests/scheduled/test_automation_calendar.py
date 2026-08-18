from __future__ import annotations

from datetime import datetime
import importlib.util
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

from tradingagents.notifications.telegram import _diagnostic_signature
from tradingagents.scheduled.automation_calendar import (
    CACHE_SCHEMA,
    MarketSessionStatus,
    automated_market_session_status,
)


ROOT = Path(__file__).resolve().parents[2]
SEOUL = ZoneInfo("Asia/Seoul")


class _Response:
    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def _load_script(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_exchange_calendar_closes_2026_korean_substitute_holiday(monkeypatch) -> None:
    monkeypatch.delenv("TRADINGAGENTS_KIS_MARKET_CALENDAR_ENABLED", raising=False)

    status = automated_market_session_status(
        "kr", datetime(2026, 8, 17, 10, 0, tzinfo=SEOUL)
    )

    assert status.is_session is False
    assert status.session_date.isoformat() == "2026-08-17"


def test_same_day_official_cache_overrides_exchange_calendar(
    tmp_path, monkeypatch
) -> None:
    cache_path = tmp_path / "calendar.json"
    cache_path.write_text(
        json.dumps(
            {
                "schema": CACHE_SCHEMA,
                "fetched_at": "2026-08-18T00:01:00+09:00",
                "records": {
                    "2026-08-18": {
                        "is_open": False,
                        "detail": "ad-hoc closure",
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("TRADINGAGENTS_KIS_MARKET_CALENDAR_ENABLED", "1")
    monkeypatch.setenv("KIS_APP_KEY", "key")
    monkeypatch.setenv("KIS_APP_SECRET", "secret")

    status = automated_market_session_status(
        "kr",
        datetime(2026, 8, 18, 10, 0, tzinfo=SEOUL),
        cache_path=cache_path,
        opener=lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("same-day cache must avoid a KIS request")
        ),
    )

    assert status.is_session is False
    assert status.source == "kis_official_cache"


def test_previous_day_forecast_is_revalidated(tmp_path, monkeypatch) -> None:
    cache_path = tmp_path / "calendar.json"
    cache_path.write_text(
        json.dumps(
            {
                "schema": CACHE_SCHEMA,
                "fetched_at": "2026-08-17T09:00:00+09:00",
                "records": {"2026-08-18": {"is_open": True}},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("TRADINGAGENTS_KIS_MARKET_CALENDAR_ENABLED", "1")
    monkeypatch.setenv("KIS_APP_KEY", "sensitive-key")
    monkeypatch.setenv("KIS_APP_SECRET", "sensitive-secret")
    responses = iter(
        [
            _Response({"access_token": "sensitive-token"}),
            _Response(
                {
                    "rt_cd": "0",
                    "output": [{"bass_dt": "20260818", "opnd_yn": "N"}],
                }
            ),
        ]
    )

    status = automated_market_session_status(
        "kr",
        datetime(2026, 8, 18, 10, 0, tzinfo=SEOUL),
        cache_path=cache_path,
        opener=lambda *_args, **_kwargs: next(responses),
    )

    serialized = cache_path.read_text(encoding="utf-8")
    assert status.is_session is False
    assert "sensitive" not in serialized


def test_official_calendar_failure_is_fail_closed(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TRADINGAGENTS_KIS_MARKET_CALENDAR_ENABLED", "1")
    monkeypatch.setenv("KIS_APP_KEY", "key")
    monkeypatch.setenv("KIS_APP_SECRET", "secret")

    status = automated_market_session_status(
        "kr",
        datetime(2026, 8, 18, 10, 0, tzinfo=SEOUL),
        cache_path=tmp_path / "calendar.json",
        opener=lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("down")),
    )

    assert status.is_session is None
    assert status.source == "kis_official_unavailable"


def test_schedule_gate_holds_official_holiday_without_api_lookup() -> None:
    gate = _load_script(
        "_test_scheduled_workflow_gate",
        ".github/scripts/scheduled_workflow_gate.py",
    )
    now = datetime(2026, 8, 17, 10, 0, tzinfo=SEOUL)
    target = gate.ScheduleTarget(
        profile="kr",
        window_start_time=now.time(),
        target_jobs=("analyze_kr",),
    )

    profile, should_run, reason = gate.decide_schedule_gate(
        event_name="schedule",
        schedule="test",
        requested_profile="",
        manual_default_profile="all",
        workflow_file="daily-codex-analysis.yml",
        current_run_id=1,
        client=object(),
        targets={"test": target},
        now_kst=now,
        market_status_resolver=lambda *_args: MarketSessionStatus(
            "kr", now.date(), False, "test-official"
        ),
    )

    assert profile == "kr"
    assert should_run is False
    assert "closed" in reason


def test_intraday_gate_holds_holiday_before_dependency_lookup() -> None:
    gate = _load_script(
        "_test_intraday_overlay_gate",
        ".github/scripts/intraday_overlay_gate.py",
    )
    now = datetime(2026, 8, 17, 10, 0, tzinfo=SEOUL)

    decisions, messages = gate.decide_intraday_gate(
        event_name="schedule",
        schedule="5 1 * * 1-5",
        requested_profile="",
        client=object(),
        now_kst=now,
        market_status_resolver=lambda *_args: MarketSessionStatus(
            "kr", now.date(), False, "test-official"
        ),
    )

    assert decisions["kr"] is False
    assert any("market is closed" in message for message in messages)


def test_github_correlation_ids_do_not_split_telegram_incidents() -> None:
    first = (
        "##[error]Failed to download action. HTTP 429. "
        "GitHub Request Id: 06CA:C276A:1261:191C8:6A8312F6"
    )
    second = (
        "##[error]Failed to download action. HTTP 429. "
        "GitHub Request Id: 3125:1C2169:29B4:1DD30:6A8314DF"
    )

    assert _diagnostic_signature(first) == _diagnostic_signature(second)
