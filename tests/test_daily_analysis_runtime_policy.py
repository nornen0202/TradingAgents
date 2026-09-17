import tomllib
from pathlib import Path


DAILY_CONFIGS = (
    Path("config/scheduled_analysis.toml"),
    Path("config/scheduled_analysis_korea.toml"),
    Path("config/scheduled_analysis.example.toml"),
)


def _load_toml(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def test_daily_configs_keep_full_depth_while_production_universe_is_capped():
    for path in DAILY_CONFIGS:
        payload = _load_toml(path)
        run = payload["run"]
        llm = payload["llm"]
        performance = payload["portfolio_performance"]
        summary_image = payload["summary_image"]

        assert run["ticker_universe_mode"] == "config_plus_account", path
        if path.name == "scheduled_analysis.example.toml":
            assert run["daily_active_ticker_limit"] == 0, path
        else:
            assert run["daily_active_ticker_limit"] == 30, path
            assert payload["universe"]["enabled"] is True, path
            assert payload["universe"]["max_tickers"] == 30, path
        assert run["max_runtime_minutes"] == 0, path
        assert run["min_remaining_minutes_for_next_ticker"] == 0, path
        assert run["max_parallel_tickers"] >= 4, path
        assert run["per_ticker_timeout_minutes"] >= 60, path
        assert llm["codex_request_timeout"] >= 360.0, path
        assert performance["publish_to_site"] is False, path
        assert summary_image["publish_to_site"] is False, path
        assert summary_image["redact_account_values"] is True, path
