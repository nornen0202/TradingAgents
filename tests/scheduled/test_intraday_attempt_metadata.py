import json
from pathlib import Path

from tradingagents.scheduled.config import load_scheduled_config
from tradingagents.scheduled.runner import _run_execution_overlay_passes
from tradingagents.schemas import (
    ActionIfTriggered,
    BreakoutConfirmation,
    ExecutionContract,
    LevelBasis,
    PrimarySetup,
    ThesisState,
)


def test_intraday_snapshot_failure_writes_metadata_and_degraded_update(tmp_path: Path, monkeypatch):
    config_path = tmp_path / "scheduled.toml"
    config_path.write_text(
        f"""
[run]
tickers = ["NVDA"]
timezone = "Asia/Seoul"
market = "US"

[storage]
archive_dir = "{(tmp_path / 'archive').as_posix()}"
site_dir = "{(tmp_path / 'site').as_posix()}"

[execution]
enabled = true
checkpoints_kst = ["12:35"]
""",
        encoding="utf-8",
    )
    config = load_scheduled_config(config_path)
    run_dir = tmp_path / "archive" / "runs" / "2026" / "run"
    ticker_dir = run_dir / "tickers" / "NVDA"
    ticker_dir.mkdir(parents=True)

    contract = ExecutionContract(
        ticker="NVDA",
        analysis_asof="2026-04-16T09:16:00+09:00",
        market_data_asof="2026-04-15",
        level_basis=LevelBasis.DAILY_CLOSE,
        thesis_state=ThesisState.CONSTRUCTIVE,
        primary_setup=PrimarySetup.BREAKOUT_CONFIRMATION,
        portfolio_stance="BULLISH",
        entry_action_base="WAIT",
        setup_quality="COMPELLING",
        confidence=0.78,
        action_if_triggered=ActionIfTriggered.ADD,
        breakout_level=900.0,
        breakout_confirmation=BreakoutConfirmation.CLOSE_ABOVE,
    )
    contract_path = ticker_dir / "execution_contract.json"
    analysis_path = ticker_dir / "analysis.json"
    contract_path.write_text(json.dumps(contract.to_dict(), ensure_ascii=False), encoding="utf-8")
    analysis_path.write_text(json.dumps({"ticker": "NVDA"}, ensure_ascii=False), encoding="utf-8")
    summary = {
        "status": "success",
        "ticker": "NVDA",
        "artifacts": {
            "execution_contract_json": "tickers/NVDA/execution_contract.json",
            "analysis_json": "tickers/NVDA/analysis.json",
        },
    }

    def raise_fetch(*args, **kwargs):
        raise RuntimeError("intraday feed down")

    monkeypatch.setattr("tradingagents.scheduled.runner.fetch_intraday_market_snapshot", raise_fetch)

    updates = _run_execution_overlay_passes(
        config=config,
        run_dir=run_dir,
        ticker_summaries=[summary],
        checkpoints=["12:35"],
    )

    update = updates["NVDA"]
    assert update["decision_state"] == "DEGRADED"
    assert update["execution_timing_state"] == "NO_LIVE_DATA"
    assert update["decision_if_triggered"] == "ADD"
    assert update["intraday_snapshot_attempt"]["success"] is False
    assert update["intraday_snapshot_attempt"]["error_type"] == "RuntimeError"
    assert (ticker_dir / "execution" / "checkpoints" / "execution_update_12_35.json").exists()
    assert (ticker_dir / "execution_update.json").exists()
    assert summary["execution_update"]["decision_state"] == "DEGRADED"

    analysis_payload = json.loads(analysis_path.read_text(encoding="utf-8"))
    assert analysis_payload["intraday_snapshot_attempts"][0]["success"] is False
    assert analysis_payload["latest_intraday_snapshot_attempt"]["success"] is False
    assert analysis_payload["intraday_snapshot_latest_attempt"]["success"] is False
