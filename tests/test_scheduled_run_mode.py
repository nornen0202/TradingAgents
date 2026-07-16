import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

from tradingagents.scheduled.config import load_scheduled_config
from tradingagents.scheduled.runner import (
    _ResolvedRunTickerUniverse,
    _bootstrap_overlay_inputs_from_latest_run,
    _freeze_overlay_universe_to_latest_full_baseline,
    _manifest_has_bootstrap_ready_ticker,
    _manifest_production_priority,
    _resolve_latest_overlay_source_manifest,
    execute_scheduled_run,
)


def _recent_started_at(*, hours_ago: float = 1.0) -> str:
    return (datetime.now(timezone.utc) - timedelta(hours=hours_ago)).isoformat()


def test_overlay_production_label_token_matching_does_not_reject_latest() -> None:
    assert _manifest_production_priority({"label": "latest-production"}) == 1
    assert _manifest_production_priority({"label": "github-actions-test"}) == 0


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


def _write_full_overlay_baseline(
    archive_dir: Path,
    *,
    tickers: list[str],
    market: str = "US",
    run_id: str = "20260716T180000_full",
    started_at: str | None = None,
    label: str = "github-actions",
    set_latest: bool = True,
) -> dict:
    run_dir = archive_dir / "runs" / "2026" / run_id
    rows = []
    for ticker in tickers:
        ticker_dir = run_dir / "tickers" / ticker
        ticker_dir.mkdir(parents=True, exist_ok=True)
        (ticker_dir / "analysis.json").write_text(
            json.dumps(
                {"ticker": ticker, "decision": "HOLD", "trade_date": "2026-07-16"},
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        rows.append(
            {
                "ticker": ticker,
                "status": "success",
                "decision": "HOLD",
                "artifacts": {"analysis_json": f"tickers/{ticker}/analysis.json"},
            }
        )
    manifest = {
        "run_id": run_id,
        "label": label,
        "started_at": started_at or _recent_started_at(),
        "settings": {"run_mode": "full", "market": market},
        "tickers": rows,
    }
    (run_dir / "run.json").write_text(json.dumps(manifest), encoding="utf-8")
    archive_dir.mkdir(parents=True, exist_ok=True)
    if set_latest:
        (archive_dir / "latest-run.json").write_text(json.dumps(manifest), encoding="utf-8")
    return manifest


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
        "started_at": _recent_started_at(),
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

[performance]
enabled = true
update_outcomes_on_run = true
price_provider = "yfinance"
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
        patch("tradingagents.scheduled.runner._run_performance_tracking", side_effect=AssertionError("overlay must skip long-horizon performance tracking")),
        patch("tradingagents.scheduled.runner.build_site", return_value=[]),
    ):
        manifest = execute_scheduled_run(config, run_label="overlay-test")

    assert manifest["settings"]["run_mode"] == "overlay_only"
    assert manifest["summary"]["total_tickers"] == 1
    assert manifest["tickers"][0]["quality_flags"] == ("overlay_only_mode",)
    assert manifest["performance"] == {"status": "skipped", "reason": "overlay_fast_path"}


def test_overlay_freezes_full_baseline_and_defers_new_dynamic_candidates(tmp_path: Path):
    archive_dir = tmp_path / "archive"
    _write_full_overlay_baseline(archive_dir, tickers=["NVDA", "AAPL"])
    config_path = tmp_path / "scheduled_analysis.toml"
    config_path.write_text(
        f"""
[run]
tickers = ["NVDA", "AAPL"]
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
    scanner_receipt = {
        "enabled": True,
        "added_tickers": ["ABT"],
        "candidate_count": 0,
        "source_counts": {"prism_imported_same_market": 3},
    }

    with (
        patch(
            "tradingagents.scheduled.runner._augment_run_tickers_with_scanner",
            return_value=(["NVDA", "AAPL", "ABT"], scanner_receipt),
        ),
        patch(
            "tradingagents.scheduled.runner._run_execution_overlay_passes",
            side_effect=_fake_overlay_updates,
        ),
        patch("tradingagents.scheduled.runner.build_site", return_value=[]),
    ):
        manifest = execute_scheduled_run(config, run_label="overlay-freeze-test")

    assert [row["ticker"] for row in manifest["tickers"]] == ["NVDA", "AAPL"]
    assert manifest["summary"]["total_tickers"] == 2
    assert manifest["overlay_universe"]["baseline_run_id"] == "20260716T180000_full"
    assert manifest["overlay_universe"]["deferred_new_candidates"] == ["ABT"]
    assert manifest["scanner"]["deferred_added_tickers"] == ["ABT"]
    assert manifest["active_universe"]["coverage"]["complete"] is True
    assert any(
        warning.startswith("overlay_dynamic_candidates_deferred_until_full_run:")
        for warning in manifest["warnings"]
    )


def test_overlay_prefers_older_complete_production_baseline_over_newer_partial_custom(
    tmp_path: Path,
) -> None:
    archive_dir = tmp_path / "archive"
    friday = datetime(2026, 7, 17, 20, 0, tzinfo=timezone.utc)
    monday = datetime(2026, 7, 20, 14, 0, tzinfo=timezone.utc)
    complete = _write_full_overlay_baseline(
        archive_dir,
        tickers=["NVDA", "AAPL"],
        run_id="20260717T200000_production_full",
        started_at=friday.isoformat(),
        set_latest=False,
    )
    _write_full_overlay_baseline(
        archive_dir,
        tickers=["NVDA"],
        run_id="20260720T130000_manual_partial",
        started_at=(monday - timedelta(hours=1)).isoformat(),
        label="manual-custom",
        set_latest=True,
    )
    config_path = tmp_path / "scheduled_analysis.toml"
    config_path.write_text(
        f"""
[run]
tickers = ["NVDA", "AAPL", "NEW"]
market = "US"
run_mode = "overlay_only"

[storage]
archive_dir = "{archive_dir.as_posix()}"
site_dir = "{(tmp_path / 'site').as_posix()}"

[execution]
enabled = true
""",
        encoding="utf-8",
    )
    config = load_scheduled_config(config_path)
    universe = _ResolvedRunTickerUniverse(
        tickers=("NVDA", "AAPL", "NEW"),
        configured_tickers=("NVDA", "AAPL", "NEW"),
        profile_watch_tickers=(),
        holding_tickers=("NVDA",),
        mode="config_plus_account",
        account_snapshot_status="loaded",
        account_snapshot_health="VALID",
    )

    tickers, _selection, _scanner, metadata, warnings = (
        _freeze_overlay_universe_to_latest_full_baseline(
            config=config,
            resolved_universe=universe,
            requested_base_tickers=["NVDA", "AAPL", "NEW"],
            discovered_tickers=["NVDA", "AAPL", "NEW"],
            scanner_status=None,
            now=monday,
        )
    )

    assert tickers == ["NVDA", "AAPL"]
    assert metadata["baseline_run_id"] == complete["run_id"]
    assert metadata["deferred_nonholding_tickers"] == ["NEW"]
    assert metadata["baseline_max_age_hours"] == 96
    assert metadata["baseline_max_newer_sessions"] == 1
    assert any("overlay_nonholding_universe_changes_deferred" in warning for warning in warnings)


def test_overlay_fails_closed_when_complete_baseline_is_truly_stale(tmp_path: Path) -> None:
    archive_dir = tmp_path / "archive"
    now = datetime(2026, 7, 20, 14, 0, tzinfo=timezone.utc)
    _write_full_overlay_baseline(
        archive_dir,
        tickers=["NVDA"],
        run_id="20260713T140000_stale_full",
        started_at=(now - timedelta(days=7)).isoformat(),
    )
    config_path = tmp_path / "scheduled_analysis.toml"
    config_path.write_text(
        f"""
[run]
tickers = ["NVDA"]
market = "US"
run_mode = "overlay_only"

[storage]
archive_dir = "{archive_dir.as_posix()}"
site_dir = "{(tmp_path / 'site').as_posix()}"

[execution]
enabled = true
""",
        encoding="utf-8",
    )
    config = load_scheduled_config(config_path)
    universe = _ResolvedRunTickerUniverse(
        tickers=("NVDA",),
        configured_tickers=("NVDA",),
        profile_watch_tickers=(),
        holding_tickers=("NVDA",),
        mode="config_plus_account",
        account_snapshot_status="loaded",
        account_snapshot_health="VALID",
    )

    with pytest.raises(RuntimeError, match="OVERLAY_BASELINE_STALE"):
        _freeze_overlay_universe_to_latest_full_baseline(
            config=config,
            resolved_universe=universe,
            requested_base_tickers=["NVDA"],
            discovered_tickers=["NVDA"],
            scanner_status=None,
            now=now,
        )


def test_overlay_rejects_manual_custom_run_as_only_baseline(tmp_path: Path) -> None:
    archive_dir = tmp_path / "archive"
    now = datetime(2026, 7, 20, 14, 0, tzinfo=timezone.utc)
    _write_full_overlay_baseline(
        archive_dir,
        tickers=["NVDA"],
        run_id="20260720T130000_manual_custom",
        started_at=(now - timedelta(hours=1)).isoformat(),
        label="manual-custom",
    )
    config_path = tmp_path / "scheduled_analysis.toml"
    config_path.write_text(
        f"""
[run]
tickers = ["NVDA"]
market = "US"
run_mode = "overlay_only"
[storage]
archive_dir = "{archive_dir.as_posix()}"
site_dir = "{(tmp_path / 'site').as_posix()}"
[execution]
enabled = true
""",
        encoding="utf-8",
    )
    config = load_scheduled_config(config_path)
    universe = _ResolvedRunTickerUniverse(
        tickers=("NVDA",),
        configured_tickers=("NVDA",),
        profile_watch_tickers=(),
        holding_tickers=(),
        mode="config_only",
        account_snapshot_status="disabled",
    )
    with pytest.raises(RuntimeError, match="OVERLAY_BASELINE_MISSING"):
        _freeze_overlay_universe_to_latest_full_baseline(
            config=config,
            resolved_universe=universe,
            requested_base_tickers=["NVDA"],
            discovered_tickers=["NVDA"],
            scanner_status=None,
            now=now,
        )


def test_overlay_keeps_current_holding_coverage_gap_fatal(tmp_path: Path):
    archive_dir = tmp_path / "archive"
    _write_full_overlay_baseline(archive_dir, tickers=["NVDA"])
    config_path = tmp_path / "scheduled_analysis.toml"
    config_path.write_text(
        f"""
[run]
tickers = ["NVDA"]
market = "US"
run_mode = "overlay_only"

[storage]
archive_dir = "{archive_dir.as_posix()}"
site_dir = "{(tmp_path / 'site').as_posix()}"

[execution]
enabled = true
""",
        encoding="utf-8",
    )
    config = load_scheduled_config(config_path)
    universe = _ResolvedRunTickerUniverse(
        tickers=("NVDA", "ABT"),
        configured_tickers=("NVDA",),
        profile_watch_tickers=(),
        holding_tickers=("ABT",),
        mode="config_plus_account",
        account_snapshot_status="loaded",
        account_snapshot_health="VALID",
    )

    with (
        patch("tradingagents.scheduled.runner._resolve_run_ticker_universe", return_value=universe),
        patch(
            "tradingagents.scheduled.runner._augment_run_tickers_with_scanner",
            return_value=(["NVDA", "ABT"], None),
        ),
    ):
        try:
            execute_scheduled_run(config, run_label="overlay-holding-gap-test")
            assert False, "expected a fatal current-holding baseline coverage gap"
        except RuntimeError as exc:
            assert "OVERLAY_BASELINE_HOLDING_COVERAGE_GAP" in str(exc)
            assert "ABT" in str(exc)


def test_overlay_source_resolution_fails_closed_on_partial_target_coverage(tmp_path: Path):
    archive_dir = tmp_path / "archive"
    archive_dir.mkdir(parents=True)
    partial = {
        "run_id": "partial-full",
        "started_at": _recent_started_at(),
        "settings": {"run_mode": "full", "market": "US"},
        "tickers": [
            {
                "ticker": "NVDA",
                "status": "success",
                "artifacts": {"analysis_json": "tickers/NVDA/analysis.json"},
            }
        ],
    }
    (archive_dir / "latest-run.json").write_text(json.dumps(partial), encoding="utf-8")

    resolved = _resolve_latest_overlay_source_manifest(
        archive_dir,
        tickers=["NVDA", "AAPL"],
        market="US",
    )

    assert resolved is None


def test_overlay_bootstrap_matches_kr_alias_identity(tmp_path: Path):
    archive_dir = tmp_path / "archive"
    source_run_dir = archive_dir / "runs" / "2026" / "alias-full"
    source_ticker_dir = source_run_dir / "tickers" / "005930"
    source_ticker_dir.mkdir(parents=True)
    (source_ticker_dir / "analysis.json").write_text(
        json.dumps({"ticker": "005930", "decision": "HOLD", "trade_date": "2026-07-15"}),
        encoding="utf-8",
    )
    (source_ticker_dir / "execution_contract.json").write_text("{}", encoding="utf-8")
    source_manifest = {
        "run_id": "alias-full",
        "started_at": _recent_started_at(),
        "settings": {"run_mode": "full", "market": "KR"},
        "tickers": [
            {
                "ticker": "005930",
                "status": "success",
                "decision": "HOLD",
                "artifacts": {
                    "analysis_json": "tickers/005930/analysis.json",
                    "execution_contract_json": "tickers/005930/execution_contract.json",
                },
            }
        ],
    }
    (source_run_dir / "run.json").write_text(json.dumps(source_manifest), encoding="utf-8")
    archive_dir.mkdir(parents=True, exist_ok=True)
    (archive_dir / "latest-run.json").write_text(json.dumps(source_manifest), encoding="utf-8")
    config_path = tmp_path / "scheduled_analysis.toml"
    config_path.write_text(
        f"""
[run]
tickers = ["005930.KS"]
run_mode = "overlay_only"
market = "KR"

[storage]
archive_dir = "{archive_dir.as_posix()}"
site_dir = "{(tmp_path / 'site').as_posix()}"

[execution]
enabled = true
""",
        encoding="utf-8",
    )
    config = load_scheduled_config(config_path)

    assert _manifest_has_bootstrap_ready_ticker(
        source_manifest,
        tickers=["005930.KS"],
    )
    summaries, source_run_id = _bootstrap_overlay_inputs_from_latest_run(
        config=config,
        run_dir=tmp_path / "overlay-run",
        tickers=["005930.KS"],
    )

    assert source_run_id == "alias-full"
    assert [summary["ticker"] for summary in summaries] == ["005930.KS"]
    assert (tmp_path / "overlay-run" / "tickers" / "005930.KS" / "analysis.json").is_file()


def test_portfolio_only_mode_skips_ticker_analysis_and_runs_portfolio_pipeline(tmp_path: Path):
    config_path = tmp_path / "scheduled_analysis.toml"
    config_path.write_text(
        f"""
[run]
tickers = ["NVDA"]
run_mode = "portfolio_only"

[storage]
archive_dir = "{(tmp_path / 'archive').as_posix()}"
site_dir = "{(tmp_path / 'site').as_posix()}"

[execution]
enabled = true
checkpoints_kst = ["22:35"]

[portfolio]
enabled = true
profile_path = "portfolio_profiles.toml"
profile_name = "kr_kis_default"

[performance]
enabled = true
""",
        encoding="utf-8",
    )
    config = load_scheduled_config(config_path)

    with (
        patch("tradingagents.scheduled.runner._resolve_run_tickers", side_effect=AssertionError("ticker universe must be skipped")),
        patch("tradingagents.scheduled.runner._run_single_ticker", side_effect=AssertionError("ticker research must be skipped")),
        patch("tradingagents.scheduled.runner._run_execution_overlay_passes", side_effect=AssertionError("execution overlay must be skipped")),
        patch("tradingagents.scheduled.runner._run_performance_tracking", side_effect=AssertionError("recommendation tracking must be skipped")),
        patch("tradingagents.scheduled.runner.build_live_context_delta", return_value={}),
        patch("tradingagents.scheduled.runner.run_portfolio_pipeline", return_value={"status": "success"}) as portfolio_pipeline,
        patch("tradingagents.scheduled.runner.build_site", return_value=[]),
    ):
        manifest = execute_scheduled_run(config, run_label="portfolio-only-test")

    assert manifest["settings"]["run_mode"] == "portfolio_only"
    assert manifest["summary"]["total_tickers"] == 0
    assert manifest["tickers"] == []
    assert "execution" not in manifest
    assert "performance" not in manifest
    assert manifest["market_session_phase"] == "portfolio_only"
    assert manifest["portfolio"]["status"] == "success"
    assert portfolio_pipeline.call_count == 1
    assert portfolio_pipeline.call_args.kwargs["external_data_settings"] is None


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
                "started_at": _recent_started_at(hours_ago=0.5),
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
                "started_at": _recent_started_at(hours_ago=1.0),
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


def test_full_mode_records_selective_targets_without_running_second_research_pass(tmp_path: Path):
    config_path = tmp_path / "scheduled_analysis.toml"
    config_path.write_text(
        f"""
[run]
tickers = ["NVDA"]
run_mode = "full"

[storage]
archive_dir = "{(tmp_path / 'archive').as_posix()}"
site_dir = "{(tmp_path / 'site').as_posix()}"

[execution]
enabled = true
checkpoints_kst = ["00:00"]
selective_rerun_enabled = true
""",
        encoding="utf-8",
    )
    config = load_scheduled_config(config_path)

    ticker_summary = {
        "ticker": "NVDA",
        "ticker_name": "NVIDIA",
        "status": "success",
        "trade_date": "2026-04-14",
        "analysis_date": "2026-04-14",
        "decision": "HOLD",
        "started_at": "2026-04-14T22:00:00+09:00",
        "finished_at": "2026-04-14T22:01:00+09:00",
        "duration_seconds": 60.0,
        "metrics": {"llm_calls": 1, "tool_calls": 1, "tokens_in": 0, "tokens_out": 0},
        "tool_telemetry": {"called_tools": []},
        "quality_flags": [],
        "artifacts": {},
    }

    with (
        patch("tradingagents.scheduled.runner._resolve_run_trade_date", return_value="2026-04-14"),
        patch("tradingagents.scheduled.runner._run_single_ticker", return_value=ticker_summary) as run_single,
        patch("tradingagents.scheduled.runner._run_execution_overlay_passes", side_effect=_fake_overlay_updates),
        patch("tradingagents.scheduled.runner.collect_event_signals", return_value={}),
        patch("tradingagents.scheduled.runner.find_selective_rerun_targets", return_value={"NVDA": ["overlay_invalidated"]}),
        patch("tradingagents.scheduled.runner._run_selective_rerun", side_effect=AssertionError("full mode must not rerun research")),
        patch("tradingagents.scheduled.runner.build_site", return_value=[]),
    ):
        manifest = execute_scheduled_run(config, run_label="full-selective-target-test")

    assert run_single.call_count == 1
    assert manifest["selective_rerun_targets"] == {"NVDA": ["overlay_invalidated"]}
    assert "selective_rerun_results" not in manifest


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
                "started_at": _recent_started_at(hours_ago=0.5),
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
                "started_at": _recent_started_at(hours_ago=1.0),
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
                "started_at": _recent_started_at(hours_ago=0.5),
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
                "started_at": _recent_started_at(),
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
                "started_at": _recent_started_at(),
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
