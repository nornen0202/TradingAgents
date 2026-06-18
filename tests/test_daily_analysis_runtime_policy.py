import tomllib
from pathlib import Path


DAILY_CONFIGS = (
    Path("config/scheduled_analysis.toml"),
    Path("config/scheduled_analysis_korea.toml"),
    Path("config/scheduled_analysis.example.toml"),
)


def _load_toml(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def test_daily_configs_do_not_cap_full_universe_runtime_or_ticker_count():
    for path in DAILY_CONFIGS:
        payload = _load_toml(path)
        run = payload["run"]
        llm = payload["llm"]

        assert run["daily_active_ticker_limit"] == 0, path
        assert run["max_runtime_minutes"] == 0, path
        assert run["min_remaining_minutes_for_next_ticker"] == 0, path
        assert run["max_parallel_tickers"] >= 4, path
        assert run["per_ticker_timeout_minutes"] >= 60, path
        assert llm["codex_request_timeout"] >= 360.0, path
