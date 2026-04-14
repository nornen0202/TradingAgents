import json
from pathlib import Path
from unittest.mock import patch

from tradingagents.scheduled.config import load_scheduled_config
from tradingagents.scheduled.runner import execute_scheduled_run


class _NoopUpdate:
    def __init__(self, ticker: str):
        self.payload = {
            "ticker": ticker,
            "decision_state": "WAIT",
            "execution_asof": "2026-04-14T22:40:00+09:00",
        }


def _fake_overlay_updates(**kwargs):
    updates = {}
    for summary in kwargs["ticker_summaries"]:
        ticker = summary["ticker"]
        updates[ticker] = {
            "ticker": ticker,
            "decision_state": "WAIT",
            "execution_asof": "2026-04-14T22:40:00+09:00",
        }
    updates["_latest_checkpoint"] = {"value": "22:35"}
    return updates


def test_overlay_only_mode_uses_latest_run_without_full_research(tmp_path: Path):
    archive_dir = tmp_path / "archive"
    source_run_dir = archive_dir / "runs" / "2026" / "20260414T220000_full"
    source_ticker_dir = source_run_dir / "tickers" / "NVDA"
    source_ticker_dir.mkdir(parents=True, exist_ok=True)

    (source_ticker_dir / "analysis.json").write_text(
        json.dumps({"ticker": "NVDA", "decision": "HOLD", "trade_date": "2026-04-14"}, ensure_ascii=False),
        encoding="utf-8",
    )
    (source_ticker_dir / "execution_contract.json").write_text(
        json.dumps(
            {
                "ticker": "NVDA",
                "analysis_asof": "2026-04-14T22:00:00+09:00",
                "market_data_asof": "2026-04-14",
                "level_basis": "daily_close",
                "thesis_state": "neutral",
                "primary_setup": "watch_only",
                "portfolio_stance": "NEUTRAL",
                "entry_action_base": "WAIT",
                "setup_quality": "DEVELOPING",
                "confidence": 0.5,
                "action_if_triggered": "NONE",
                "session_vwap_preference": "indifferent",
                "event_guard": {"earnings_date": None, "block_new_position_within_days": 0, "allow_add_only_after_event": False, "requires_post_event_rerun": False},
                "reason_codes": [],
                "notes": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    latest_manifest = {
        "run_id": "20260414T220000_full",
        "started_at": "2026-04-14T22:00:00+09:00",
        "tickers": [
            {
                "ticker": "NVDA",
                "ticker_name": "NVIDIA",
                "status": "success",
                "trade_date": "2026-04-14",
                "analysis_date": "2026-04-14",
                "decision": "HOLD",
                "artifacts": {
                    "analysis_json": "tickers/NVDA/analysis.json",
                    "execution_contract_json": "tickers/NVDA/execution_contract.json",
                },
            }
        ],
    }
    archive_dir.mkdir(parents=True, exist_ok=True)
    (archive_dir / "latest-run.json").write_text(json.dumps(latest_manifest, ensure_ascii=False), encoding="utf-8")

    config_path = tmp_path / "scheduled_analysis.toml"
    config_path.write_text(
        f"""
[run]
tickers = ["NVDA"]
run_mode = "overlay_only"

[storage]
archive_dir = "{archive_dir.as_posix()}"
site_dir = "{(tmp_path / 'site').as_posix()}"

[execution]
enabled = true
checkpoints_kst = ["22:35"]
""",
        encoding="utf-8",
    )
    config = load_scheduled_config(config_path)

    def fake_overlay(**kwargs):
        ticker = kwargs["ticker_summaries"][0]["ticker"]
        return {ticker: {"ticker": ticker, "decision_state": "WAIT", "execution_asof": "2026-04-14T22:40:00+09:00"}, "_latest_checkpoint": {"value": "22:35"}}

    with (
        patch("tradingagents.scheduled.runner._run_single_ticker", side_effect=AssertionError("full research must be skipped in overlay_only")),
        patch("tradingagents.scheduled.runner._run_execution_overlay_passes", side_effect=fake_overlay),
        patch("tradingagents.scheduled.runner.build_site", return_value=[]),
    ):
        manifest = execute_scheduled_run(config, run_label="overlay-test")

    assert manifest["settings"]["run_mode"] == "overlay_only"
    assert manifest["summary"]["total_tickers"] == 1
    assert manifest["tickers"][0]["quality_flags"] == ("overlay_only_mode",)


def test_overlay_only_mode_prefers_full_source_when_latest_is_overlay(tmp_path: Path):
    archive_dir = tmp_path / "archive"
    full_run_dir = archive_dir / "runs" / "2026" / "20260414T220000_full"
    full_ticker_dir = full_run_dir / "tickers" / "NVDA"
    full_ticker_dir.mkdir(parents=True, exist_ok=True)
    (full_ticker_dir / "analysis.json").write_text(
        json.dumps({"ticker": "NVDA", "decision": "BUY", "trade_date": "2026-04-14"}, ensure_ascii=False),
        encoding="utf-8",
    )

    overlay_run_dir = archive_dir / "runs" / "2026" / "20260414T235900_overlay"
    overlay_ticker_dir = overlay_run_dir / "tickers" / "NVDA"
    overlay_ticker_dir.mkdir(parents=True, exist_ok=True)
    (overlay_ticker_dir / "analysis.json").write_text(
        json.dumps({"ticker": "NVDA", "decision": "WAIT", "trade_date": "2026-04-14"}, ensure_ascii=False),
        encoding="utf-8",
    )

    (archive_dir / "latest-run.json").write_text(
        json.dumps(
            {
                "run_id": "20260414T235900_overlay",
                "started_at": "2026-04-14T23:59:00+09:00",
                "overlay_source_run_id": "20260414T220000_full",
                "settings": {"run_mode": "overlay_only"},
                "tickers": [
                    {
                        "ticker": "NVDA",
                        "status": "success",
                        "artifacts": {"analysis_json": "tickers/NVDA/analysis.json"},
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (full_run_dir / "run.json").write_text(
        json.dumps(
            {
                "run_id": "20260414T220000_full",
                "started_at": "2026-04-14T22:00:00+09:00",
                "settings": {"run_mode": "full"},
                "tickers": [
                    {
                        "ticker": "NVDA",
                        "ticker_name": "NVIDIA",
                        "status": "success",
                        "trade_date": "2026-04-14",
                        "analysis_date": "2026-04-14",
                        "decision": "BUY",
                        "artifacts": {"analysis_json": "tickers/NVDA/analysis.json"},
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    config_path = tmp_path / "scheduled_analysis.toml"
    config_path.write_text(
        f"""
[run]
tickers = ["NVDA"]
run_mode = "overlay_only"

[storage]
archive_dir = "{archive_dir.as_posix()}"
site_dir = "{(tmp_path / 'site').as_posix()}"

[execution]
enabled = true
checkpoints_kst = ["22:35"]
""",
        encoding="utf-8",
    )
    config = load_scheduled_config(config_path)

    with (
        patch("tradingagents.scheduled.runner._run_execution_overlay_passes", side_effect=_fake_overlay_updates),
        patch("tradingagents.scheduled.runner.build_site", return_value=[]),
    ):
        manifest = execute_scheduled_run(config, run_label="overlay-source-test")

    assert manifest["overlay_source_run_id"] == "20260414T220000_full"
    assert manifest["tickers"][0]["decision"] == "BUY"


def test_overlay_only_mode_requires_execution_enabled(tmp_path: Path):
    config_path = tmp_path / "scheduled_analysis.toml"
    config_path.write_text(
        f"""
[run]
tickers = ["NVDA"]
run_mode = "overlay_only"

[storage]
archive_dir = "{(tmp_path / 'archive').as_posix()}"
site_dir = "{(tmp_path / 'site').as_posix()}"

[execution]
enabled = false
""",
        encoding="utf-8",
    )
    config = load_scheduled_config(config_path)

    try:
        execute_scheduled_run(config, run_label="overlay-disabled")
        assert False, "expected RuntimeError when overlay_only runs with execution disabled"
    except RuntimeError as exc:
        assert "run_mode=overlay_only requires [execution].enabled=true" in str(exc)


def test_selective_rerun_only_requires_execution_refresh_enabled(tmp_path: Path):
    archive_dir = tmp_path / "archive"
    config_path = tmp_path / "scheduled_analysis.toml"
    config_path.write_text(
        f"""
[run]
tickers = ["NVDA"]
run_mode = "selective_rerun_only"

[storage]
archive_dir = "{archive_dir.as_posix()}"
site_dir = "{(tmp_path / 'site').as_posix()}"

[execution]
enabled = false
""",
        encoding="utf-8",
    )
    config = load_scheduled_config(config_path)
    try:
        execute_scheduled_run(config, run_label="selective-guard")
        assert False, "expected RuntimeError when selective_rerun_only runs with execution disabled"
    except RuntimeError as exc:
        assert "requires [execution].enabled=true" in str(exc)


def test_overlay_only_mode_falls_back_to_latest_matching_full_run(tmp_path: Path):
    archive_dir = tmp_path / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    latest_full_run_dir = archive_dir / "runs" / "2026" / "20260414T235900_full_us"
    latest_full_run_ticker_dir = latest_full_run_dir / "tickers" / "AAPL"
    latest_full_run_ticker_dir.mkdir(parents=True, exist_ok=True)
    (latest_full_run_ticker_dir / "analysis.json").write_text(
        json.dumps({"ticker": "AAPL", "decision": "HOLD", "trade_date": "2026-04-14"}, ensure_ascii=False),
        encoding="utf-8",
    )
    (latest_full_run_dir / "run.json").write_text(
        json.dumps(
            {
                "run_id": "20260414T235900_full_us",
                "started_at": "2026-04-14T23:59:00+09:00",
                "settings": {"run_mode": "full"},
                "tickers": [
                    {
                        "ticker": "AAPL",
                        "status": "success",
                        "decision": "HOLD",
                        "artifacts": {"analysis_json": "tickers/AAPL/analysis.json"},
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    matching_full_run_dir = archive_dir / "runs" / "2026" / "20260414T220000_full_kr"
    matching_ticker_dir = matching_full_run_dir / "tickers" / "005930.KS"
    matching_ticker_dir.mkdir(parents=True, exist_ok=True)
    (matching_ticker_dir / "analysis.json").write_text(
        json.dumps({"ticker": "005930.KS", "decision": "BUY", "trade_date": "2026-04-14"}, ensure_ascii=False),
        encoding="utf-8",
    )
    (matching_full_run_dir / "run.json").write_text(
        json.dumps(
            {
                "run_id": "20260414T220000_full_kr",
                "started_at": "2026-04-14T22:00:00+09:00",
                "settings": {"run_mode": "full"},
                "tickers": [
                    {
                        "ticker": "005930.KS",
                        "status": "success",
                        "decision": "BUY",
                        "artifacts": {"analysis_json": "tickers/005930.KS/analysis.json"},
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    # latest-run points to a full run, but with non-overlapping tickers for this KR overlay request.
    (archive_dir / "latest-run.json").write_text(
        json.dumps(
            {
                "run_id": "20260414T235900_full_us",
                "started_at": "2026-04-14T23:59:00+09:00",
                "settings": {"run_mode": "full"},
                "tickers": [
                    {
                        "ticker": "AAPL",
                        "status": "success",
                        "decision": "HOLD",
                        "artifacts": {"analysis_json": "tickers/AAPL/analysis.json"},
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    config_path = tmp_path / "scheduled_analysis.toml"
    config_path.write_text(
        f"""
[run]
tickers = ["005930.KS"]
run_mode = "overlay_only"

[storage]
archive_dir = "{archive_dir.as_posix()}"
site_dir = "{(tmp_path / 'site').as_posix()}"

[execution]
enabled = true
checkpoints_kst = ["22:35"]
""",
        encoding="utf-8",
    )
    config = load_scheduled_config(config_path)

    with (
        patch("tradingagents.scheduled.runner._run_execution_overlay_passes", side_effect=_fake_overlay_updates),
        patch("tradingagents.scheduled.runner.build_site", return_value=[]),
    ):
        manifest = execute_scheduled_run(config, run_label="overlay-fallback-test")

    assert manifest["overlay_source_run_id"] == "20260414T220000_full_kr"
    assert manifest["tickers"][0]["ticker"] == "005930.KS"
    assert manifest["tickers"][0]["decision"] == "BUY"


def test_overlay_only_mode_copies_source_report_markdown(tmp_path: Path):
    archive_dir = tmp_path / "archive"
    source_run_dir = archive_dir / "runs" / "2026" / "20260414T220000_full"
    source_ticker_dir = source_run_dir / "tickers" / "NVDA"
    source_report_dir = source_ticker_dir / "report"
    source_report_dir.mkdir(parents=True, exist_ok=True)
    (source_ticker_dir / "analysis.json").write_text(
        json.dumps({"ticker": "NVDA", "decision": "HOLD", "trade_date": "2026-04-14"}, ensure_ascii=False),
        encoding="utf-8",
    )
    (source_report_dir / "complete_report.md").write_text("# NVDA report\n\nBaseline research.", encoding="utf-8")
    (source_run_dir / "run.json").write_text(
        json.dumps(
            {
                "run_id": "20260414T220000_full",
                "started_at": "2026-04-14T22:00:00+09:00",
                "settings": {"run_mode": "full"},
                "tickers": [
                    {
                        "ticker": "NVDA",
                        "ticker_name": "NVIDIA",
                        "status": "success",
                        "trade_date": "2026-04-14",
                        "analysis_date": "2026-04-14",
                        "decision": "HOLD",
                        "artifacts": {
                            "analysis_json": "tickers/NVDA/analysis.json",
                            "report_markdown": "tickers/NVDA/report/complete_report.md",
                        },
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    archive_dir.mkdir(parents=True, exist_ok=True)
    (archive_dir / "latest-run.json").write_text(
        json.dumps(
            {
                "run_id": "20260414T220000_full",
                "started_at": "2026-04-14T22:00:00+09:00",
                "settings": {"run_mode": "full"},
                "tickers": [
                    {
                        "ticker": "NVDA",
                        "ticker_name": "NVIDIA",
                        "status": "success",
                        "trade_date": "2026-04-14",
                        "analysis_date": "2026-04-14",
                        "decision": "HOLD",
                        "artifacts": {
                            "analysis_json": "tickers/NVDA/analysis.json",
                            "report_markdown": "tickers/NVDA/report/complete_report.md",
                        },
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    config_path = tmp_path / "scheduled_analysis.toml"
    config_path.write_text(
        f"""
[run]
tickers = ["NVDA"]
run_mode = "overlay_only"

[storage]
archive_dir = "{archive_dir.as_posix()}"
site_dir = "{(tmp_path / 'site').as_posix()}"

[execution]
enabled = true
checkpoints_kst = ["22:35"]
""",
        encoding="utf-8",
    )
    config = load_scheduled_config(config_path)

    with (
        patch("tradingagents.scheduled.runner._run_execution_overlay_passes", side_effect=_fake_overlay_updates),
        patch("tradingagents.scheduled.runner.build_site", return_value=[]),
    ):
        manifest = execute_scheduled_run(config, run_label="overlay-copy-report")

    report_rel = manifest["tickers"][0]["artifacts"].get("report_markdown")
    assert report_rel == "tickers/NVDA/report/complete_report.md"
    report_path = archive_dir / "runs" / manifest["started_at"][:4] / manifest["run_id"] / report_rel
    assert report_path.read_text(encoding="utf-8") == "# NVDA report\n\nBaseline research."
