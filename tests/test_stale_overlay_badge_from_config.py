from pathlib import Path

from tradingagents.scheduled.config import _default_execution_checkpoints_kst, load_scheduled_config


def test_us_default_checkpoints_are_three_kst_times():
    checkpoints = _default_execution_checkpoints_kst("US")
    assert len(checkpoints) == 3
    assert all(len(value) == 5 and value[2] == ":" for value in checkpoints)


def test_kr_default_checkpoints_match_operational_profile():
    assert _default_execution_checkpoints_kst("KR") == ("10:05", "11:05", "12:35", "14:35")


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


def test_intraday_overlay_workflow_uses_kr_operational_crons():
    workflow = Path(".github/workflows/intraday-overlay-refresh.yml").read_text(encoding="utf-8")
    assert "KR checkpoints: 10:05, 11:05, 12:35, 14:35 KST." in workflow
    assert "5 1,2 * * 1-5" in workflow
    assert "35 3,5 * * 1-5" in workflow
    assert "5 0,2,4 * * 1-5" not in workflow
    assert "25 6 * * 1-5" not in workflow
