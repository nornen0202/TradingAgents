import tomllib
from pathlib import Path


DAILY_CONFIGS = (
    Path("config/scheduled_analysis.toml"),
    Path("config/scheduled_analysis_korea.toml"),
    Path("config/scheduled_analysis.example.toml"),
)


def _load_toml(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def test_daily_configs_use_bounded_holdings_first_rotation_policy():
    for path in DAILY_CONFIGS:
        payload = _load_toml(path)
        run = payload["run"]
        llm = payload["llm"]

        assert 10 <= run["daily_active_ticker_limit"] <= 20, path
        assert 90 <= run["max_runtime_minutes"] <= 120, path
        assert run["min_remaining_minutes_for_next_ticker"] >= 10, path
        assert run["max_parallel_tickers"] >= 4, path
        assert 20 <= run["per_ticker_timeout_minutes"] <= 45, path
        assert llm["codex_request_timeout"] >= 360.0, path
