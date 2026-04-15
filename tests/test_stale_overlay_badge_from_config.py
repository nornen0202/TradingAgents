from pathlib import Path

from tradingagents.scheduled.config import _default_execution_checkpoints_kst, load_scheduled_config


def test_us_default_checkpoints_are_three_kst_times():
    checkpoints = _default_execution_checkpoints_kst("US")
    assert len(checkpoints) == 3
    assert all(len(value) == 5 and value[2] == ":" for value in checkpoints)


def test_kr_default_checkpoints_match_operational_profile():
    assert _default_execution_checkpoints_kst("KR") == ("09:20", "12:00", "15:40")


def test_explicit_market_overrides_timezone_inference(tmp_path: Path):
    config_path = tmp_path / "scheduled.toml"
    config_path.write_text(
        """
[run]
tickers = ["AAPL"]
timezone = "Asia/Seoul"
market = "US"

[storage]
archive_dir = ".archive"
site_dir = ".site"
""",
        encoding="utf-8",
    )
    config = load_scheduled_config(config_path)
    assert config.run.market == "US"
    assert len(config.execution.execution_refresh_checkpoints_kst) == 3
