from pathlib import Path

from tradingagents.scheduled.config import load_scheduled_config


def test_scheduled_config_injects_safe_codex_workspace_default(tmp_path: Path):
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

    assert config.llm.codex_workspace_dir is not None
    assert ".codex" in config.llm.codex_workspace_dir
