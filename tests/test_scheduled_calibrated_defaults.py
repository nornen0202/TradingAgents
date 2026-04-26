from pathlib import Path

from tradingagents.scheduled.config import load_scheduled_config


def test_scheduled_config_uses_calibrated_defaults(tmp_path: Path):
    config_path = tmp_path / "scheduled_analysis.toml"
    config_path.write_text(
        """
[run]
tickers = ["NVDA"]

[storage]
archive_dir = "./archive"
site_dir = "./site"
""",
        encoding="utf-8",
    )

    config = load_scheduled_config(config_path)
    assert config.run.max_debate_rounds == 2
    assert config.run.max_risk_discuss_rounds == 2
    assert config.llm.deep_model == "gpt-5.5"
    assert config.llm.quick_model == "gpt-5.5"
    assert config.llm.output_model == "gpt-5.5"


def test_empty_execution_checkpoints_fall_back_to_market_defaults(tmp_path: Path):
    config_path = tmp_path / "scheduled_analysis.toml"
    config_path.write_text(
        """
[run]
tickers = ["AAPL"]
market = "US"

[execution]
enabled = true
checkpoints_kst = []

[storage]
archive_dir = "./archive"
site_dir = "./site"
""",
        encoding="utf-8",
    )
    config = load_scheduled_config(config_path)
    assert len(config.execution.execution_refresh_checkpoints_kst) == 3
