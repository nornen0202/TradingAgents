from __future__ import annotations

from datetime import datetime


import json
from zoneinfo import ZoneInfo

from tradingagents.scheduled.automation_calendar import (
    CACHE_SCHEMA,
    MarketSessionStatus,
    automated_market_session_status,
)


SEOUL = ZoneInfo("Asia/Seoul")


class _Response:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")


def test_exchange_calendar_closes_2026_korean_substitute_holiday(
    monkeypatch,
) -> None:
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
                        "detail": "ad-hoc market closure",
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("TRADINGAGENTS_KIS_MARKET_CALENDAR_ENABLED", "1")
    monkeypatch.setenv("KIS_APP_KEY", "key")
    monkeypatch.setenv("KIS_APP_SECRET", "secret")

    def should_not_open(*_args, **_kwargs):
        raise AssertionError("same-day cache should avoid another KIS request")

    status = automated_market_session_status(
        "kr",
        datetime(2026, 8, 18, 10, 0, tzinfo=SEOUL),
        cache_path=cache_path,
        opener=should_not_open,
    )

    assert status.is_session is False
    assert status.source == "kis_official_cache"


def test_previous_day_forecast_is_revalidated_for_ad_hoc_closure(
    tmp_path, monkeypatch
) -> None:
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
    monkeypatch.setenv("KIS_APP_KEY", "key")
    monkeypatch.setenv("KIS_APP_SECRET", "secret")
    responses = iter(
        [
            _Response({"access_token": "temporary-token"}),
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

    assert status.is_session is False
    assert json.loads(cache_path.read_text(encoding="utf-8"))["records"][
        "2026-08-18"
    ]["is_open"] is False


def test_enabled_official_calendar_without_credentials_fails_closed(
    monkeypatch,
) -> None:
    monkeypatch.setenv("TRADINGAGENTS_KIS_MARKET_CALENDAR_ENABLED", "1")
    monkeypatch.delenv("KIS_APP_KEY", raising=False)
    monkeypatch.delenv("KIS_APP_SECRET", raising=False)
    monkeypatch.delenv("KIS_DEVELOPERS_APP_KEY", raising=False)
    monkeypatch.delenv("KIS_DEVELOPERS_APP_SECRET", raising=False)

    status = automated_market_session_status(
        "kr", datetime(2026, 8, 18, 10, 0, tzinfo=SEOUL)
    )

    assert status.is_session is None
    assert status.source == "kis_official_unconfigured"


def test_enabled_official_calendar_outage_fails_closed(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setenv("TRADINGAGENTS_KIS_MARKET_CALENDAR_ENABLED", "1")
    monkeypatch.setenv("KIS_APP_KEY", "key")
    monkeypatch.setenv("KIS_APP_SECRET", "secret")

    def unavailable(*_args, **_kwargs):
        raise OSError("temporary outage")

    status = automated_market_session_status(
        "kr",
        datetime(2026, 8, 18, 10, 0, tzinfo=SEOUL),
        cache_path=tmp_path / "calendar.json",
        opener=unavailable,
    )

    assert status.is_session is None
    assert status.source == "kis_official_unavailable"


def test_kis_response_is_cached_without_storing_credentials(
    tmp_path, monkeypatch
) -> None:
    now = datetime.now(SEOUL)
    market_date = now.date()
    monkeypatch.setenv("TRADINGAGENTS_KIS_MARKET_CALENDAR_ENABLED", "1")
    monkeypatch.setenv("KIS_APP_KEY", "sensitive-key")
    monkeypatch.setenv("KIS_APP_SECRET", "sensitive-secret")
    calls: list[str] = []

    def opener(request, **_kwargs):
        calls.append(request.full_url)
        if request.full_url.endswith("/oauth2/tokenP"):
            return _Response({"access_token": "sensitive-token"})
        assert request.get_header("Custtype") == "P"
        return _Response(
            {
                "rt_cd": "0",
                "output": [
                    {
                        "bass_dt": market_date.strftime("%Y%m%d"),
                        "opnd_yn": "Y",
                    }
                ],
            }
        )

    cache_path = tmp_path / "calendar.json"
    status = automated_market_session_status(
        "kr", now, cache_path=cache_path, opener=opener
    )

    serialized = cache_path.read_text(encoding="utf-8")
    assert status == MarketSessionStatus(
        "kr",
        market_date,
        True,
        "kis_official_cache",
        "KIS chk-holiday opnd_yn",
    )
    assert len(calls) == 2
    assert "sensitive" not in serialized

def test_calendar_reason_matches_gate_contract():
    from datetime import date

    for value, label in [(True, "open"), (False, "closed"), (None, "unavailable")]:
        status = MarketSessionStatus("kr", date(2026, 8, 18), value, "test")
        assert label in status.reason
        assert "2026-08-18" in status.reason


def test_missing_date_in_fresh_response_does_not_revalidate_old_forecast(tmp_path, monkeypatch):
    path = tmp_path / "calendar.json"
    old = {"schema": CACHE_SCHEMA, "fetched_at": "2026-08-17T00:00:00+09:00",
           "records": {"2026-08-18": {"is_open": True}}}
    path.write_text(json.dumps(old), encoding="utf-8")
    monkeypatch.setenv("TRADINGAGENTS_KIS_MARKET_CALENDAR_ENABLED", "1")
    monkeypatch.setenv("KIS_APP_KEY", "key")
    monkeypatch.setenv("KIS_APP_SECRET", "secret")
    responses = iter([_Response({"access_token": "token"}), _Response({
        "rt_cd": "0", "output": [{"bass_dt": "20260819", "opnd_yn": "Y"}]
    })])
    status = automated_market_session_status(
        "kr", datetime(2026, 8, 18, 10, tzinfo=SEOUL), cache_path=path,
        opener=lambda *_a, **_k: next(responses),
    )
    assert status.is_session is None
    assert json.loads(path.read_text(encoding="utf-8")) == old


def test_workflow_env_aliases_timeout_and_response_cleanup(tmp_path, monkeypatch):
    import tradingagents.scheduled.automation_calendar as module

    monkeypatch.setenv("TRADINGAGENTS_KIS_MARKET_CALENDAR_ENABLED", "1")
    monkeypatch.delenv("KIS_APP_KEY", raising=False)
    monkeypatch.delenv("KIS_APP_SECRET", raising=False)
    monkeypatch.setenv("KIS_Developers_APP_KEY", "key")
    monkeypatch.setenv("KIS_Developers_APP_SECRET", "secret")
    monkeypatch.setenv("KIS_HTTP_TIMEOUT_SECONDS", "8")
    monkeypatch.delenv("TRADINGAGENTS_KIS_MARKET_CALENDAR_TIMEOUT_SECONDS", raising=False)
    path = tmp_path / "calendar.json"
    monkeypatch.setenv("TRADINGAGENTS_MARKET_CALENDAR_CACHE_PATH", str(path))
    closed = []

    class Response(_Response):
        def close(self):
            closed.append(True)

    responses = iter([Response({"access_token": "token"}), Response({
        "rt_cd": "0", "output": [{"bass_dt": "20260818", "opnd_yn": "Y"}]
    })])
    def opener(request, timeout):
        assert timeout == 8
        return next(responses)

    now = datetime(2026, 8, 18, 10, tzinfo=SEOUL)
    assert automated_market_session_status("kr", now, opener=opener).is_session is True
    assert len(closed) == 2
    assert module._cache_was_fetched_on(json.loads(path.read_text()), now.date())
    assert automated_market_session_status("kr", now, opener=lambda *_a, **_k: 1/0).is_session is True


def test_us_session_uses_new_york_date(monkeypatch):
    import tradingagents.scheduled.automation_calendar as module

    seen = []
    def resolve(market, session_date):
        seen.append((market, session_date.isoformat()))
        return MarketSessionStatus(market, session_date, True, "test")
    monkeypatch.setattr(module, "_exchange_calendar_status", resolve)
    automated_market_session_status("us", datetime(2026, 9, 19, 2, tzinfo=SEOUL))
    assert seen == [("us", "2026-09-18")]


def test_calendar_import_does_not_load_cli_or_llm_dependencies():
    import subprocess
    import sys

    result = subprocess.run([sys.executable, "-c",
        "import sys; import tradingagents.scheduled.automation_calendar; "
        "assert 'cli.utils' not in sys.modules; "
        "assert 'langchain_core' not in sys.modules"
    ], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
