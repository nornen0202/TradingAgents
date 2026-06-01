from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from tradingagents.scheduled.config import load_scheduled_config
from tradingagents.scheduled.runner import (
    FRESHNESS_PRIOR_SESSION_BACKFILL,
    _bootstrap_overlay_inputs_from_latest_run,
    _run_execution_overlay_passes,
    _write_chatgpt_execution_context_from_ticker_artifacts,
)
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
    report_text = (target_run_dir / "tickers" / "AAPL" / "microstructure_report.md").read_text(encoding="utf-8")
    assert "Publication Status" in report_text
    assert "| Generated in current run | false |" in report_text


def test_overlay_bootstrap_does_not_drop_tickers_from_partial_overlay_source(tmp_path: Path):
    archive_dir = tmp_path / "archive"
    config_path = tmp_path / "scheduled.toml"
    config_path.write_text(
        f"""
[run]
tickers = ["AAPL", "MSFT"]
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
        tickers=("AAPL", "MSFT"),
    )
    partial_overlay = _write_source_run(
        archive_dir,
        run_id="20260530T040000_overlay_partial",
        started_at="2026-05-30T04:00:00+09:00",
        run_mode="overlay_only",
        microstructure=True,
        tickers=("AAPL",),
    )
    partial_overlay["overlay_source_run_id"] = full_manifest["run_id"]
    (archive_dir / "latest-run.json").write_text(json.dumps(partial_overlay), encoding="utf-8")

    summaries, source_run_id = _bootstrap_overlay_inputs_from_latest_run(
        config=config,
        run_dir=archive_dir / "runs" / "2026" / "new_overlay",
        tickers=["AAPL", "MSFT"],
    )

    assert source_run_id == full_manifest["run_id"]
    assert {item["ticker"] for item in summaries} == {"AAPL", "MSFT"}


def test_backfills_microstructure_per_ticker_with_source_metadata(tmp_path: Path):
    archive_dir = tmp_path / "archive"
    config_path = tmp_path / "scheduled.toml"
    config_path.write_text(
        f"""
[run]
tickers = ["AAPL", "MSFT"]
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
        tickers=("AAPL", "MSFT"),
    )
    _write_source_run(
        archive_dir,
        run_id="20260530T030000_overlay_aapl",
        started_at="2026-05-30T03:00:00+09:00",
        run_mode="overlay_only",
        microstructure=True,
        tickers=("AAPL",),
    )
    _write_source_run(
        archive_dir,
        run_id="20260530T040000_overlay_msft",
        started_at="2026-05-30T04:00:00+09:00",
        run_mode="overlay_only",
        microstructure=True,
        tickers=("MSFT",),
    )
    latest_no_micro = _write_source_run(
        archive_dir,
        run_id="20260530T160000_overlay",
        started_at="2026-05-30T16:00:00+09:00",
        run_mode="overlay_only",
        microstructure=False,
        tickers=("AAPL", "MSFT"),
    )
    latest_no_micro["overlay_source_run_id"] = full_manifest["run_id"]
    (archive_dir / "latest-run.json").write_text(json.dumps(latest_no_micro), encoding="utf-8")

    target_run_dir = archive_dir / "runs" / "2026" / "new_overlay"
    summaries, _source_run_id = _bootstrap_overlay_inputs_from_latest_run(
        config=config,
        run_dir=target_run_dir,
        tickers=["AAPL", "MSFT"],
    )

    by_ticker = {item["ticker"]: item for item in summaries}
    aapl_payload = json.loads(
        (target_run_dir / by_ticker["AAPL"]["artifacts"]["microstructure_snapshot_json"]).read_text(encoding="utf-8")
    )
    msft_payload = json.loads(
        (target_run_dir / by_ticker["MSFT"]["artifacts"]["microstructure_snapshot_json"]).read_text(encoding="utf-8")
    )
    assert aapl_payload["generated_in_current_run"] is False
    assert aapl_payload["microstructure_source_run_id"] == "20260530T030000_overlay_aapl"
    assert aapl_payload["freshness_class"] == FRESHNESS_PRIOR_SESSION_BACKFILL
    assert msft_payload["microstructure_source_run_id"] == "20260530T040000_overlay_msft"
    aapl_update = json.loads(
        (target_run_dir / by_ticker["AAPL"]["artifacts"]["execution_update_json"]).read_text(encoding="utf-8")
    )
    assert aapl_update["microstructure_publication"]["artifact_asof"] == "2026-05-29T13:00:00-04:00"
    assert aapl_update["source"]["artifact_asof"] == "2026-05-29T13:00:00-04:00"

    artifacts = _write_chatgpt_execution_context_from_ticker_artifacts(
        config=config,
        run_dir=target_run_dir,
        ticker_summaries=summaries,
        overlay_phase={"name": "CLOSED", "selected_checkpoints": []},
    )
    assert artifacts["chatgpt_execution_context_json"] == "chatgpt_execution_context.json"
    context = json.loads((target_run_dir / "chatgpt_execution_context.json").read_text(encoding="utf-8"))
    assert {item["ticker"] for item in context["tickers"]} == {"AAPL", "MSFT"}
    assert context["tickers"][0]["generated_in_current_run"] is False

    site_dir = tmp_path / "site"
    _copy_artifacts(
        site_dir,
        target_run_dir,
        {
            "run_id": "new_overlay",
            "execution": {"artifacts": artifacts},
            "tickers": summaries,
            "portfolio": {"status": "disabled"},
        },
        {},
    )
    assert (site_dir / "downloads" / "new_overlay" / "execution" / "chatgpt_execution_context.json").exists()


def test_overlay_bootstrap_uses_same_market_partial_full_when_universe_expands(tmp_path: Path):
    archive_dir = tmp_path / "archive"
    config_path = tmp_path / "scheduled.toml"
    config_path.write_text(
        f"""
[run]
tickers = ["AAPL", "MSFT"]
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
    latest_kr = _write_source_run(
        archive_dir,
        run_id="20260601T090000_kr",
        started_at="2026-06-01T09:00:00+09:00",
        run_mode="full",
        microstructure=False,
        tickers=("005930.KS",),
        market="KR",
    )
    _write_source_run(
        archive_dir,
        run_id="20260530T010000_us_partial",
        started_at="2026-05-30T01:00:00+09:00",
        run_mode="full",
        microstructure=False,
        tickers=("AAPL",),
        market="US",
    )
    (archive_dir / "latest-run.json").write_text(json.dumps(latest_kr), encoding="utf-8")

    summaries, source_run_id = _bootstrap_overlay_inputs_from_latest_run(
        config=config,
        run_dir=archive_dir / "runs" / "2026" / "new_overlay",
        tickers=["AAPL", "MSFT"],
    )

    assert source_run_id == "20260530T010000_us_partial"
    assert {item["ticker"] for item in summaries} == {"AAPL"}


def _write_source_run(
    archive_dir: Path,
    *,
    run_id: str,
    started_at: str,
    run_mode: str,
    microstructure: bool,
    tickers: tuple[str, ...] = ("AAPL",),
    market: str = "US",
) -> dict:
    run_dir = archive_dir / "runs" / started_at[:4] / run_id
    ticker_items = []
    for ticker in tickers:
        ticker_dir = run_dir / "tickers" / ticker
        ticker_dir.mkdir(parents=True)
        (ticker_dir / "analysis.json").write_text(json.dumps({"ticker": ticker}), encoding="utf-8")
        (ticker_dir / "execution_contract.json").write_text("{}", encoding="utf-8")
        artifacts = {
            "analysis_json": f"tickers/{ticker}/analysis.json",
            "execution_contract_json": f"tickers/{ticker}/execution_contract.json",
        }
        if microstructure:
            (ticker_dir / "microstructure_report.md").write_text(
                f"# Microstructure Report - {ticker}\n\n| Field | Value |\n|---|---|\n| As-of | 2026-05-29T13:00:00-04:00 |\n",
                encoding="utf-8",
            )
            (ticker_dir / "microstructure_snapshot.json").write_text(
                json.dumps(
                    {
                        "ticker": ticker,
                        "asof": "2026-05-29T13:00:00-04:00",
                        "market_session": "regular",
                        "execution_data_quality": "REALTIME_EXECUTION_READY",
                        "microstructure": {
                            "ticker": ticker,
                            "asof_local": "2026-05-29T13:00:00-04:00",
                            "data_quality": "REALTIME_EXECUTION_READY",
                        },
                    }
                ),
                encoding="utf-8",
            )
            (ticker_dir / "execution_update.json").write_text(
                json.dumps(
                    {
                        "ticker": ticker,
                        "market_data_asof": "2026-05-29T13:00:00-04:00",
                        "execution_asof": "2026-05-29T13:01:00-04:00",
                        "source": {
                            "provider": "kis_microstructure",
                            "market_session": "regular",
                            "execution_data_quality": "REALTIME_EXECUTION_READY",
                        },
                    }
                ),
                encoding="utf-8",
            )
            artifacts.update(
                {
                    "execution_update_json": f"tickers/{ticker}/execution_update.json",
                    "microstructure_report_md": f"tickers/{ticker}/microstructure_report.md",
                    "microstructure_snapshot_json": f"tickers/{ticker}/microstructure_snapshot.json",
                }
            )
        ticker_items.append({"ticker": ticker, "status": "success", "artifacts": artifacts})
    manifest = {
        "version": 1,
        "run_id": run_id,
        "started_at": started_at,
        "settings": {"run_mode": run_mode, "market": market},
        "summary": {"total_tickers": len(ticker_items), "successful_tickers": len(ticker_items), "failed_tickers": 0},
        "tickers": ticker_items,
    }
    (run_dir / "run.json").write_text(json.dumps(manifest), encoding="utf-8")
    return manifest
