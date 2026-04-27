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
    assert config.summary_image.enabled is True
    assert config.summary_image.mode == "deterministic_svg"
    assert config.summary_image.publish_to_site is True


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


def test_summary_image_config_accepts_openai_mode_alias(tmp_path: Path):
    config_path = tmp_path / "scheduled_analysis.toml"
    config_path.write_text(
        """
[run]
tickers = ["AAPL"]

[storage]
archive_dir = "./archive"
site_dir = "./site"

[summary_image]
enabled = true
mode = "openai"
publish_to_site = false
redact_account_values = true
image_model = "gpt-image-2"
""",
        encoding="utf-8",
    )
    config = load_scheduled_config(config_path)
    assert config.summary_image.mode == "openai_image"
    assert config.summary_image.publish_to_site is False
    assert config.summary_image.redact_account_values is True


def test_codex_model_env_override_replaces_configured_models(tmp_path: Path, monkeypatch):
    config_path = tmp_path / "scheduled_analysis.toml"
    codex_workspace = tmp_path / "codex-workspace"
    config_path.write_text(
        """
[run]
tickers = ["AAPL"]

[llm]
quick_model = "gpt-5.5"
deep_model = "gpt-5.5"
output_model = "gpt-5.5"

[execution]
llm_summary_model = "gpt-5.5"

[storage]
archive_dir = "./archive"
site_dir = "./site"
""",
        encoding="utf-8",
    )
    monkeypatch.setenv("TRADINGAGENTS_CODEX_MODEL", "gpt-5.4")
    monkeypatch.setenv("TRADINGAGENTS_CODEX_WORKSPACE_DIR", str(codex_workspace))

    config = load_scheduled_config(config_path)

    assert config.llm.quick_model == "gpt-5.4"
    assert config.llm.deep_model == "gpt-5.4"
    assert config.llm.output_model == "gpt-5.4"
    assert config.llm.codex_workspace_dir == str(codex_workspace)
    assert config.execution.execution_llm_summary_model == "gpt-5.4"
