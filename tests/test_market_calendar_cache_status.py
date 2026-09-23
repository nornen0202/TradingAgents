from datetime import datetime
import importlib.util
import json
from pathlib import Path

from tradingagents.scheduled.automation_calendar import CACHE_SCHEMA, SEOUL


def test_old_restored_cache_cannot_reserve_today_actions_key(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("calendar_cache_status", ".github/scripts/market_calendar_cache_status.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    cache = tmp_path / "calendar.json"
    monkeypatch.setenv("TRADINGAGENTS_MARKET_CALENDAR_CACHE_PATH", str(cache))
    now = datetime(2026, 9, 22, 8, tzinfo=SEOUL)
    payload = {"schema": CACHE_SCHEMA, "fetched_at": "2026-09-21T09:00:00+09:00",
               "records": {"2026-09-22": {"is_open": True}}}
    cache.write_text(json.dumps(payload), encoding="utf-8")
    assert module.cache_ready(now) is False
    payload["fetched_at"] = "2026-09-22T07:00:00+09:00"
    cache.write_text(json.dumps(payload), encoding="utf-8")
    assert module.cache_ready(now) is True
    payload["records"] = {}
    cache.write_text(json.dumps(payload), encoding="utf-8")
    assert module.cache_ready(now) is False


def test_calendar_workflows_check_freshness_before_immutable_cache_save():
    for name in ["daily-codex-analysis", "intraday-overlay-refresh", "scheduled-actions-watchdog"]:
        source = (Path(".github/workflows") / (name + ".yml")).read_text(encoding="utf-8")
        assert "python .github/scripts/market_calendar_cache_status.py" in source
        assert "steps.market_calendar_ready.outputs.fresh == 'true'" in source
