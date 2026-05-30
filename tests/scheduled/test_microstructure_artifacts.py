from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from tradingagents.scheduled.config import load_scheduled_config
from tradingagents.scheduled.runner import _bootstrap_overlay_inputs_from_latest_run, _run_execution_overlay_passes
from tradingagents.scheduled.site import _copy_artifacts
from tradingagents.schemas import (
    ActionIfTriggered,
    BreakoutConfirmation,
    ExecutionContract,
    IntradayMarketSnapshot,
    LevelBasis,
    PrimarySetup,
    ThesisState,
)


def test_overlay_writes_microstructure_and_chatgpt_context_artifacts(tmp_path: Path, monkeypatch):
    config_path = tmp_path / "scheduled.toml"
    config_path.write_text(
        f"""
[run]
tickers = ["AAPL"]
timezone = "Asia/Seoul"
market = "US"

[storage]
archive_dir = "{(tmp_path / 'archive').as_posix()}"
site_dir = "{(tmp_path / 'site').as_posix()}"

[execution]
enabled = true
checkpoints_local = ["10:00"]
checkpoint_timezone = "America/New_York"
""",
        encoding="utf-8",
    )
    config = load_scheduled_config(config_path)
    run_dir = tmp_path / "archive" / "runs" / "2026" / "run"
    ticker_dir = run_dir / "tickers" / "AAPL"
    ticker_dir.mkdir(parents=True)

    contract = ExecutionContract(
        ticker="AAPL",
        analysis_asof="2026-05-29T09:00:00-04:00",
        market_data_asof="2026-05-28",
        level_basis=LevelBasis.DAILY_CLOSE,
        thesis_state=ThesisState.CONSTRUCTIVE,
        primary_setup=PrimarySetup.BREAKOUT_CONFIRMATION,
        portfolio_stance="BULLISH",
        entry_action_base="WAIT",
        setup_quality="COMPELLING",
        confidence=0.8,
        action_if_triggered=ActionIfTriggered.STARTER,
        breakout_level=100.0,
        breakout_confirmation=BreakoutConfirmation.INTRADAY_ABOVE,
        min_relative_volume=1.0,
    )
    (ticker_dir / "execution_contract.json").write_text(json.dumps(contract.to_dict()), encoding="utf-8")
    (ticker_dir / "analysis.json").write_text(json.dumps({"ticker": "AAPL"}), encoding="utf-8")
    summary = {
        "status": "success",
        "ticker": "AAPL",
        "artifacts": {
            "execution_contract_json": "tickers/AAPL/execution_contract.json",
            "analysis_json": "tickers/AAPL/analysis.json",
        },
    }

    snapshot = IntradayMarketSnapshot(
        ticker="AAPL",
        asof=datetime.now(timezone.utc).isoformat(),
        provider="kis_microstructure",
        interval="5m",
        last_price=101.0,
        session_vwap=100.0,
        day_high=102.0,
        day_low=99.0,
        volume=1000,
        avg20_daily_volume=1000.0,
        relative_volume=1.2,
        provider_realtime_capable=True,
        quote_delay_seconds=0,
        market_session="regular",
        market="US",
        exchange="NAS",
        spread_bps=5.0,
        orderbook_imbalance=0.1,
        execution_strength=120.0,
        halt_status={"status": "normal", "is_clear": True},
        investor_flow_status="not_applicable",
        program_flow_status="not_applicable",
        microstructure_required=True,
    )

    monkeypatch.setattr("tradingagents.scheduled.runner.fetch_intraday_market_snapshot", lambda *a, **k: snapshot)
    monkeypatch.setattr(
        "tradingagents.scheduled.runner.render_execution_update_markdown",
        lambda *a, **k: "# update\n",
    )

    updates = _run_execution_overlay_passes(
        config=config,
        run_dir=run_dir,
        ticker_summaries=[summary],
        checkpoints=["10:00"],
    )

    assert (ticker_dir / "microstructure_snapshot.json").exists()
    assert (ticker_dir / "microstructure_report.md").exists()
    assert (ticker_dir / "execution" / "checkpoints" / "microstructure_snapshot_10_00.json").exists()
    assert (run_dir / "chatgpt_execution_context.json").exists()
    assert updates["_artifacts"]["chatgpt_execution_context_json"] == "chatgpt_execution_context.json"

    manifest = {
        "run_id": "run",
        "execution": {"artifacts": updates["_artifacts"]},
        "tickers": [summary],
        "portfolio": {"status": "disabled"},
    }
    site_dir = tmp_path / "site"
    _copy_artifacts(site_dir, run_dir, manifest, {})

    assert (site_dir / "downloads" / "run" / "AAPL" / "microstructure_snapshot.json").exists()
    assert (site_dir / "downloads" / "run" / "execution" / "chatgpt_execution_context.json").exists()


def test_overlay_bootstrap_preserves_latest_microstructure_artifacts(tmp_path: Path):
    archive_dir = tmp_path / "archive"
    config_path = tmp_path / "scheduled.toml"
    config_path.write_text(
        f"""
[run]
tickers = ["AAPL"]
timezone = "Asia/Seoul"
market = "US"
run_mode = "overlay_only"

[storage]
archive_dir = "{archive_dir.as_posix()}"
site_dir = "{(tmp_path / 'site').as_posix()}"

[execution]
enabled = true
checkpoints_local = ["10:00"]
checkpoint_timezone = "America/New_York"
""",
        encoding="utf-8",
    )
    config = load_scheduled_config(config_path)

    full_manifest = _write_source_run(
        archive_dir,
        run_id="20260530T010000_full",
        started_at="2026-05-30T01:00:00+09:00",
        run_mode="full",
        microstructure=False,
    )
    _write_source_run(
        archive_dir,
        run_id="20260530T040000_overlay",
        started_at="2026-05-30T04:00:00+09:00",
        run_mode="overlay_only",
        microstructure=True,
    )
    latest_no_micro = _write_source_run(
        archive_dir,
        run_id="20260530T160000_overlay",
        started_at="2026-05-30T16:00:00+09:00",
        run_mode="overlay_only",
        microstructure=False,
    )
    latest_no_micro["overlay_source_run_id"] = full_manifest["run_id"]
    (archive_dir / "latest-run.json").write_text(json.dumps(latest_no_micro), encoding="utf-8")

    target_run_dir = archive_dir / "runs" / "2026" / "new_overlay"
    summaries, source_run_id = _bootstrap_overlay_inputs_from_latest_run(
        config=config,
        run_dir=target_run_dir,
        tickers=["AAPL"],
    )

    assert source_run_id == "20260530T010000_full"
    artifacts = summaries[0]["artifacts"]
    assert artifacts["microstructure_report_md"] == "tickers/AAPL/microstructure_report.md"
    assert (target_run_dir / "tickers" / "AAPL" / "microstructure_report.md").read_text(encoding="utf-8") == "# micro\n"


def _write_source_run(
    archive_dir: Path,
    *,
    run_id: str,
    started_at: str,
    run_mode: str,
    microstructure: bool,
) -> dict:
    run_dir = archive_dir / "runs" / started_at[:4] / run_id
    ticker_dir = run_dir / "tickers" / "AAPL"
    ticker_dir.mkdir(parents=True)
    (ticker_dir / "analysis.json").write_text("{}", encoding="utf-8")
    (ticker_dir / "execution_contract.json").write_text("{}", encoding="utf-8")
    artifacts = {
        "analysis_json": "tickers/AAPL/analysis.json",
        "execution_contract_json": "tickers/AAPL/execution_contract.json",
    }
    if microstructure:
        (ticker_dir / "microstructure_report.md").write_text("# micro\n", encoding="utf-8")
        (ticker_dir / "microstructure_snapshot.json").write_text("{}", encoding="utf-8")
        artifacts.update(
            {
                "microstructure_report_md": "tickers/AAPL/microstructure_report.md",
                "microstructure_snapshot_json": "tickers/AAPL/microstructure_snapshot.json",
            }
        )
    manifest = {
        "version": 1,
        "run_id": run_id,
        "started_at": started_at,
        "settings": {"run_mode": run_mode, "market": "US"},
        "summary": {"total_tickers": 1, "successful_tickers": 1, "failed_tickers": 0},
        "tickers": [{"ticker": "AAPL", "status": "success", "artifacts": artifacts}],
    }
    (run_dir / "run.json").write_text(json.dumps(manifest), encoding="utf-8")
    return manifest
