from __future__ import annotations

import json
from pathlib import Path

from tradingagents.scheduled import runner
from tradingagents.scheduled.config import load_scheduled_config


def test_overlay_snapshot_workers_are_daemonized(monkeypatch, tmp_path: Path):
    config_path = tmp_path / "scheduled_analysis.toml"
    config_path.write_text(
        f"""
[run]
tickers = ["NVDA", "AAPL"]
market = "US"

[storage]
archive_dir = "{(tmp_path / 'archive').as_posix()}"
site_dir = "{(tmp_path / 'site').as_posix()}"

[execution]
enabled = true
checkpoint_timezone = "America/New_York"
""",
        encoding="utf-8",
    )
    config = load_scheduled_config(config_path)
    run_dir = tmp_path / "run"
    tickers = []
    for ticker in ("NVDA", "AAPL"):
        contract_path = run_dir / "tickers" / ticker / "execution_contract.json"
        contract_path.parent.mkdir(parents=True, exist_ok=True)
        contract_path.write_text(json.dumps({"ticker": ticker}), encoding="utf-8")
        tickers.append(
            {
                "ticker": ticker,
                "status": "success",
                "artifacts": {"execution_contract_json": contract_path.relative_to(run_dir).as_posix()},
            }
        )

    daemon_flags: list[bool] = []

    class ImmediateThread:
        def __init__(self, *, target, name: str, daemon: bool):
            self.target = target
            daemon_flags.append(daemon)

        def start(self) -> None:
            self.target()

    monkeypatch.setattr(runner, "Thread", ImmediateThread)
    monkeypatch.setattr(runner, "fetch_intraday_market_snapshot", lambda ticker, **_kwargs: f"snapshot:{ticker}")
    monkeypatch.setenv("TRADINGAGENTS_OVERLAY_MAX_WORKERS", "2")

    results = runner._fetch_overlay_market_snapshots(
        config=config,
        ticker_summaries=tickers,
        run_dir=run_dir,
        checkpoint_label="15:00",
    )

    assert daemon_flags == [True, True]
    assert results == {"NVDA": "snapshot:NVDA", "AAPL": "snapshot:AAPL"}
