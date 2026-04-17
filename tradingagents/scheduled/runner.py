from __future__ import annotations

import argparse
from copy import deepcopy
import json
import shutil
import traceback
from datetime import date, datetime, timedelta
from pathlib import Path
from time import perf_counter
from typing import Any
from zoneinfo import ZoneInfo

import yfinance as yf

from tradingagents.agents.utils.instrument_resolver import resolve_instrument
from cli.stats_handler import StatsCallbackHandler
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.dataflows.interface import reset_tool_telemetry, snapshot_tool_telemetry
from tradingagents.dataflows.intraday_market import fetch_intraday_market_snapshot
from tradingagents.dataflows.stockstats_utils import is_retryable_yfinance_error, yf_retry
from tradingagents.execution.contract_builder import build_execution_contract
from tradingagents.execution.overlay import evaluate_execution_state
from tradingagents.execution.reporting import (
    render_execution_summary_markdown,
    render_execution_update_markdown,
)
from tradingagents.execution.selective_rerun import collect_event_signals, find_selective_rerun_targets
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.portfolio import load_snapshot_for_profile, run_portfolio_pipeline
from tradingagents.portfolio.delta import compute_portfolio_delta, render_portfolio_delta_markdown
from tradingagents.portfolio.profiles import load_portfolio_profile
from tradingagents.report_writer import polish_ticker_report
from tradingagents.schemas import (
    ActionIfTriggered,
    BreakoutConfirmation,
    EventGuard,
    ExecutionContract,
    PullbackBuyZone,
    LevelBasis,
    PrimarySetup,
    SessionVWAPPreference,
    ThesisState,
    parse_structured_decision,
)
from tradingagents.reporting import save_report_bundle

from .config import (
    ScheduledAnalysisConfig,
    _default_execution_checkpoints_kst,
    load_scheduled_config,
    with_overrides,
)
from .site import build_site


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run a non-interactive scheduled TradingAgents analysis and build a static report site."
    )
    parser.add_argument("--config", default="config/scheduled_analysis.toml", help="Path to scheduled analysis TOML config.")
    parser.add_argument("--archive-dir", help="Override archive directory for run history.")
    parser.add_argument("--site-dir", help="Override generated site output directory.")
    parser.add_argument("--tickers", help="Comma-separated ticker override.")
    parser.add_argument(
        "--ticker-universe-mode",
        choices=("config_only", "config_plus_account", "account_only"),
        help="Ticker source mode: config_only / config_plus_account / account_only.",
    )
    parser.add_argument("--trade-date", help="Optional YYYY-MM-DD override for all tickers.")
    parser.add_argument(
        "--run-mode",
        choices=("full", "overlay_only", "selective_rerun_only"),
        help="Execution mode: full / overlay_only / selective_rerun_only.",
    )
    parser.add_argument("--site-only", action="store_true", help="Only rebuild the static site from archived runs.")
    parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code if any ticker fails.")
    parser.add_argument("--label", default="github-actions", help="Run label for archived metadata.")
    args = parser.parse_args(argv)

    config = with_overrides(
        load_scheduled_config(args.config),
        archive_dir=args.archive_dir,
        site_dir=args.site_dir,
        tickers=_parse_ticker_override(args.tickers),
        ticker_universe_mode=args.ticker_universe_mode,
        trade_date=args.trade_date,
        run_mode=args.run_mode,
    )

    if args.site_only:
        manifests = build_site(config.storage.archive_dir, config.storage.site_dir, config.site)
        print(
            f"Rebuilt static site at {config.storage.site_dir} from {len(manifests)} archived run(s)."
        )
        return 0

    manifest = execute_scheduled_run(config, run_label=args.label)
    print(
        f"Completed run {manifest['run_id']} with status {manifest['status']} "
        f"({manifest['summary']['successful_tickers']} success / {manifest['summary']['failed_tickers']} failed)."
    )
    return 1 if args.strict and manifest["summary"]["failed_tickers"] else 0


def execute_scheduled_run(
    config: ScheduledAnalysisConfig,
    *,
    run_label: str = "manual",
) -> dict[str, Any]:
    tz = ZoneInfo(config.run.timezone)
    started_at = datetime.now(tz)
    run_id = _build_run_id(started_at, run_label)
    run_dir = config.storage.archive_dir / "runs" / started_at.strftime("%Y") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    run_tickers = _resolve_run_tickers(config)
    ticker_summaries: list[dict[str, Any]] = []
    engine_results_dir = run_dir / "engine-results"
    run_mode = str(config.run.run_mode or "full").strip().lower()
    source_run_id: str | None = None
    if run_mode == "selective_rerun_only" and not config.execution.execution_refresh_enabled:
        raise RuntimeError(
            "run_mode=selective_rerun_only requires [execution].enabled=true to compute rerun targets."
        )
    if run_mode == "overlay_only" and not config.execution.execution_refresh_enabled:
        raise RuntimeError(
            "run_mode=overlay_only requires [execution].enabled=true to refresh execution overlays. "
            "Use run_mode=full for research-only runs or enable [execution] in the scheduled config."
        )

    if run_mode == "full":
        for ticker in run_tickers:
            ticker_summary = _run_single_ticker(
                config=config,
                ticker=ticker,
                run_dir=run_dir,
                engine_results_dir=engine_results_dir,
            )
            ticker_summaries.append(ticker_summary)
            if ticker_summary["status"] != "success" and not config.run.continue_on_ticker_error:
                break
    else:
        ticker_summaries, source_run_id = _bootstrap_overlay_inputs_from_latest_run(
            config=config,
            run_dir=run_dir,
            tickers=run_tickers,
        )

    execution_updates: dict[str, dict[str, Any]] = {}
    if config.execution.execution_refresh_enabled:
        now_kst = datetime.now(ZoneInfo("Asia/Seoul"))
        selected_checkpoints, overlay_phase = _select_due_checkpoints(
            now_kst=now_kst,
            checkpoints=_effective_execution_checkpoints(config),
        )
        manifest_overlay_phase = {
            "name": overlay_phase,
            "selected_checkpoints": list(selected_checkpoints),
            "now_kst": now_kst.isoformat(),
        }
        execution_updates = _run_execution_overlay_passes(
            config=config,
            run_dir=run_dir,
            ticker_summaries=ticker_summaries,
            checkpoints=selected_checkpoints,
        )
        if run_mode in {"overlay_only", "selective_rerun_only"} and selected_checkpoints and not _has_ticker_execution_updates(
            execution_updates
        ):
            raise RuntimeError(
                f"run_mode={run_mode} produced no execution updates. "
                "Check execution_contract artifacts and intraday market data availability."
            )
    else:
        manifest_overlay_phase = {"name": "DISABLED", "selected_checkpoints": []}

    event_signals = collect_event_signals(run_dir=run_dir, ticker_summaries=ticker_summaries)
    selective_rerun_targets: dict[str, list[str]] = {}
    selective_rerun_results: list[dict[str, Any]] = []
    if config.execution.execution_selective_rerun_enabled and execution_updates:
        selective_rerun_targets = find_selective_rerun_targets(
            contracts=_load_execution_contracts_for_run(run_dir, ticker_summaries),
            updates={key: _ExecutionUpdateShim(val) for key, val in execution_updates.items() if not key.startswith("_")},
            event_signals=event_signals,
        )
        should_execute_selective_rerun = run_mode in {"full", "selective_rerun_only"}
        if selective_rerun_targets and should_execute_selective_rerun:
            selective_rerun_results = _run_selective_rerun(
                config=config,
                run_dir=run_dir,
                engine_results_dir=engine_results_dir,
                ticker_summaries=ticker_summaries,
                targets=selective_rerun_targets,
            )
            rerun_updates = _run_execution_overlay_passes(
                config=config,
                run_dir=run_dir,
                ticker_summaries=ticker_summaries,
                checkpoints=["selective_rerun"],
            )
            execution_updates.update(
                {key: val for key, val in rerun_updates.items() if not key.startswith("_")}
            )
            execution_updates["_latest_checkpoint"] = {"value": "selective_rerun"}

    finished_at = datetime.now(tz)
    failures = sum(1 for item in ticker_summaries if item["status"] != "success")
    successes = len(ticker_summaries) - failures
    status = "success"
    if failures and successes:
        status = "partial_failure"
    elif failures:
        status = "failed"

    manifest = {
        "version": 1,
        "run_id": run_id,
        "label": run_label,
        "status": status,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "timezone": config.run.timezone,
        "settings": _settings_snapshot(config),
        "summary": {
            "total_tickers": len(ticker_summaries),
            "successful_tickers": successes,
            "failed_tickers": failures,
        },
        "tickers": ticker_summaries,
    }
    manifest["batch_metrics"] = _compute_batch_metrics(ticker_summaries)
    manifest["warnings"] = _compute_batch_warnings(manifest["batch_metrics"])
    manifest["market_session_phase"] = _market_session_phase(manifest_overlay_phase)
    if event_signals:
        manifest["event_signals"] = event_signals
    if source_run_id:
        manifest["overlay_source_run_id"] = source_run_id
    if execution_updates:
        latest_checkpoint = str((execution_updates.get("_latest_checkpoint") or {}).get("value") or "post_research")
        manifest["execution"] = _build_execution_summary(
            run_id=run_id,
            ticker_updates=execution_updates,
            checkpoint=latest_checkpoint,
        )
        manifest["execution"]["overlay_phase"] = manifest_overlay_phase
        _write_json(run_dir / "execution_summary.json", manifest["execution"])
        (run_dir / "execution_summary.md").write_text(
            render_execution_summary_markdown(
                run_id=run_id,
                checkpoint=latest_checkpoint,
                updates=[_ExecutionUpdateShim(item) for key, item in execution_updates.items() if not key.startswith("_")],
            ),
            encoding="utf-8",
        )
    elif config.execution.execution_refresh_enabled:
        manifest["execution"] = {
            "run_id": run_id,
            "refresh_checkpoint": None,
            "overlay_phase": manifest_overlay_phase,
            "execution_asof": None,
            "actionable_now": [],
            "triggered_pending_close": [],
            "wait": [],
            "invalidated": [],
            "degraded": [],
            "top_priority_order": [],
            "market_regime": "pre_open_snapshot",
            "notes": ["No execution checkpoint is due yet; this run is a pre-open snapshot."],
        }
        _write_json(run_dir / "execution_summary.json", manifest["execution"])
    if selective_rerun_targets:
        manifest["selective_rerun_targets"] = selective_rerun_targets
    if selective_rerun_results:
        manifest["selective_rerun_results"] = selective_rerun_results

    if config.portfolio.enabled and config.portfolio.profile_path:
        portfolio_status = run_portfolio_pipeline(
            run_dir=run_dir,
            manifest=manifest,
            portfolio_settings=config.portfolio,
            llm_settings=config.llm,
        )
        manifest["portfolio"] = portfolio_status
        if portfolio_status.get("status") == "failed":
            print(
                "::warning::Portfolio pipeline failed: "
                f"{portfolio_status.get('error', 'unknown error')}"
            )
    else:
        manifest["portfolio"] = {"status": "disabled"}

    manifest["run_quality"] = _compute_run_quality(manifest=manifest)
    manifest["usefulness_rank"] = manifest["run_quality"]["usefulness_rank"]

    previous_manifest = _find_previous_comparable_manifest(
        archive_dir=config.storage.archive_dir,
        current_manifest=manifest,
    )
    portfolio_delta = compute_portfolio_delta(previous_manifest=previous_manifest, current_manifest=manifest)
    delta_json_path = run_dir / "portfolio_delta.json"
    delta_md_path = run_dir / "portfolio_delta.md"
    _write_json(delta_json_path, portfolio_delta)
    delta_md_path.write_text(render_portfolio_delta_markdown(portfolio_delta), encoding="utf-8")
    manifest["portfolio_delta"] = {
        "from_run": portfolio_delta.get("from_run"),
        "summary": portfolio_delta.get("summary"),
        "artifacts": {
            "portfolio_delta_json": _relative_to_run(run_dir, delta_json_path),
            "portfolio_delta_markdown": _relative_to_run(run_dir, delta_md_path),
        },
    }

    _write_json(run_dir / "run.json", manifest)
    _write_json(config.storage.archive_dir / "latest-run.json", manifest)
    build_site(config.storage.archive_dir, config.storage.site_dir, config.site)
    return manifest


def resolve_trade_date(
    ticker: str,
    config: ScheduledAnalysisConfig,
) -> str:
    normalized_symbol = resolve_instrument(ticker).primary_symbol
    mode = config.run.trade_date_mode
    if mode == "explicit" and config.run.explicit_trade_date:
        return config.run.explicit_trade_date

    now = datetime.now(ZoneInfo(config.run.timezone))
    if mode == "today":
        return now.date().isoformat()
    if mode == "previous_business_day":
        return _previous_business_day(now.date()).isoformat()

    normalized_symbol = (normalized_symbol or "").strip().upper()
    if not _looks_like_yahoo_ticker_format(normalized_symbol):
        raise RuntimeError(
            f"Could not resolve the latest available trade date for {ticker} ({normalized_symbol}); "
            "symbol format looks invalid for Yahoo Finance. Expected examples: AAPL, BRK.B, 005930.KS."
        )

    try:
        history = _fetch_recent_trade_date_history(
            normalized_symbol,
            lookback_days=config.run.latest_market_data_lookback_days,
        )
    except Exception as exc:
        if not is_retryable_yfinance_error(exc):
            raise
        fallback_date = _previous_business_day(now.date()).isoformat()
        print(
            "::warning::"
            f"Yahoo Finance latest-trade-date lookup failed for {ticker} ({normalized_symbol}); "
            f"using previous business day {fallback_date}. reason={_summarize_exception(exc)}"
        )
        return fallback_date
    if history.empty:
        symbol_hint = _ticker_hint(normalized_symbol)
        raise RuntimeError(
            f"Could not resolve the latest available trade date for {ticker} ({normalized_symbol}); "
            f"yfinance returned no rows.{symbol_hint}"
        )

    last_index = history.index[-1]
    last_value = getattr(last_index, "to_pydatetime", lambda: last_index)()
    last_date = last_value.date() if hasattr(last_value, "date") else last_value
    if not isinstance(last_date, date):
        raise RuntimeError(f"Unexpected trade date index value for {ticker}: {last_index!r}")
    return last_date.isoformat()


def _fetch_recent_trade_date_history(symbol: str, *, lookback_days: int) -> Any:
    period = f"{max(1, int(lookback_days))}d"
    ticker = yf.Ticker(symbol)
    try:
        history = yf_retry(
            lambda: ticker.history(
                period=period,
                interval="1d",
                auto_adjust=False,
            )
        )
    except Exception as first_exc:
        try:
            downloaded = yf_retry(
                lambda: yf.download(
                    symbol,
                    period=period,
                    interval="1d",
                    progress=False,
                    auto_adjust=False,
                    multi_level_index=False,
                    threads=False,
                )
            )
        except Exception:
            raise first_exc
        if downloaded is not None and not downloaded.empty:
            return downloaded
        raise first_exc
    if history is None:
        raise RuntimeError(f"Yahoo Finance returned no history payload for {symbol}.")
    return history


def _looks_like_yahoo_ticker_format(symbol: str) -> bool:
    if not symbol:
        return False
    if symbol.count(".") > 1:
        return False
    if symbol[0] == "." or symbol[-1] == ".":
        return False
    for ch in symbol:
        if not (ch.isalnum() or ch in ".-"):
            return False
    return True


def _ticker_hint(symbol: str) -> str:
    normalized = symbol.upper()
    common_typos = {
        "APPL": " APPL is likely an invalid ticker; if you intended Apple, use 'AAPL'.",
    }
    return common_typos.get(
        normalized,
        " The symbol may be wrong (typo or delisted) or currently unavailable on Yahoo Finance.",
    )


def _summarize_exception(exc: Exception) -> str:
    text = str(exc).strip() or exc.__class__.__name__
    return text.replace("\n", " ")[:240]


def _run_single_ticker(
    *,
    config: ScheduledAnalysisConfig,
    ticker: str,
    run_dir: Path,
    engine_results_dir: Path,
) -> dict[str, Any]:
    ticker_dir = run_dir / "tickers" / ticker
    ticker_dir.mkdir(parents=True, exist_ok=True)
    resolved_name = ticker
    try:
        resolved_name = resolve_instrument(ticker).display_name
    except Exception:
        resolved_name = ticker
    resolved_name = config.run.ticker_name_overrides.get(ticker, resolved_name)

    ticker_started = datetime.now(ZoneInfo(config.run.timezone))
    timer_start = perf_counter()
    analysis_date = ticker_started.date().isoformat()

    try:
        reset_tool_telemetry()
        trade_date = resolve_trade_date(ticker, config)
        stats_handler = StatsCallbackHandler()
        graph = TradingAgentsGraph(
            config.run.analysts,
            debug=False,
            config=_graph_config(config, engine_results_dir),
            callbacks=[stats_handler],
        )
        final_state, decision = graph.propagate(
            ticker,
            trade_date,
            analysis_date=analysis_date,
        )
        structured_decision = _select_public_decision(final_state, decision)
        final_state, report_writer_payload = polish_ticker_report(
            final_state,
            ticker=ticker,
            language=config.run.output_language,
            llm_settings=config.llm,
            enabled=config.run.report_polisher_enabled,
        )

        report_dir = ticker_dir / "report"
        report_file = save_report_bundle(
            final_state,
            ticker,
            report_dir,
            generated_at=ticker_started,
            language=config.run.output_language,
        )
        final_state_path = ticker_dir / "final_state.json"
        _write_json(final_state_path, _serialize_final_state(final_state))

        graph_log = (
            engine_results_dir
            / ticker
            / "TradingAgentsStrategy_logs"
            / f"full_states_log_{trade_date}.json"
        )
        copied_graph_log = None
        if graph_log.exists():
            copied_graph_log = ticker_dir / graph_log.name
            copied_graph_log.write_text(graph_log.read_text(encoding="utf-8"), encoding="utf-8")

        metrics = stats_handler.get_stats()
        tool_events = snapshot_tool_telemetry()
        tool_by_vendor: dict[str, int] = {}
        fallback_count = 0
        for event in tool_events:
            tool_by_vendor[event["vendor"]] = tool_by_vendor.get(event["vendor"], 0) + 1
            if event.get("fallback"):
                fallback_count += 1
        quality_flags: list[str] = []
        effective_tool_calls = max(int(metrics.get("tool_calls", 0) or 0), len(tool_events))
        called_tools = _collect_called_tool_names(final_state)
        if effective_tool_calls == 0:
            quality_flags.append("no_tool_calls_detected")
            print(f"::warning::No tool calls were recorded for {ticker}; report quality may be degraded.")
        if not metrics.get("tokens_available", False):
            quality_flags.append("token_usage_unavailable")
        if (
            "market" in config.run.analysts
            and trade_date == analysis_date
            and "get_intraday_snapshot" not in called_tools
        ):
            quality_flags.append("intraday_snapshot_missing_same_day")
            print(
                f"::warning::{ticker} same-day analysis completed without get_intraday_snapshot tool usage."
            )
        analysis_payload = {
            "ticker": ticker,
            "ticker_name": (
                config.run.ticker_name_overrides.get(ticker)
                or
                ((final_state.get("instrument_profile") or {}).get("display_name"))
                or resolved_name
            ),
            "status": "success",
            "trade_date": trade_date,
            "analysis_date": analysis_date,
            "decision": structured_decision,
            "started_at": ticker_started.isoformat(),
            "finished_at": datetime.now(ZoneInfo(config.run.timezone)).isoformat(),
            "duration_seconds": round(perf_counter() - timer_start, 2),
            "metrics": {**metrics, "tool_calls": effective_tool_calls},
            "tool_telemetry": {
                "total_tool_calls": effective_tool_calls,
                "vendor_calls": tool_by_vendor,
                "fallback_count": fallback_count,
                "events": tool_events,
                "called_tools": sorted(called_tools),
                "intraday_snapshot_used": "get_intraday_snapshot" in called_tools,
            },
            "quality_flags": quality_flags,
            "report_writer": report_writer_payload,
            "provider": config.llm.provider,
            "models": {
                "quick_model": config.llm.quick_model,
                "deep_model": config.llm.deep_model,
                "output_model": config.llm.output_model,
            },
        }
        analysis_path = ticker_dir / "analysis.json"
        _write_json(analysis_path, analysis_payload)
        execution_artifacts: dict[str, str] = {}
        execution_contract_payload = None
        execution_update_payload = None
        try:
            contract = build_execution_contract(ticker=ticker, analysis_payload=analysis_payload)
            execution_contract_payload = contract.to_dict()
            execution_contract_path = ticker_dir / "execution_contract.json"
            _write_json(execution_contract_path, execution_contract_payload)
            execution_artifacts["execution_contract_json"] = _relative_to_run(run_dir, execution_contract_path)
        except Exception as exc:
            print(f"::warning::Execution contract build failed for {ticker}: {exc}")

        return {
            "ticker": ticker,
            "ticker_name": analysis_payload["ticker_name"],
            "status": "success",
            "trade_date": trade_date,
            "analysis_date": analysis_date,
            "decision": structured_decision,
            "started_at": ticker_started.isoformat(),
            "finished_at": analysis_payload["finished_at"],
            "duration_seconds": analysis_payload["duration_seconds"],
            "metrics": {**metrics, "tool_calls": effective_tool_calls},
            "tool_telemetry": analysis_payload["tool_telemetry"],
            "quality_flags": quality_flags,
            "report_writer": report_writer_payload,
            "execution_contract": execution_contract_payload,
            "execution_update": execution_update_payload,
            "artifacts": {
                "analysis_json": _relative_to_run(run_dir, analysis_path),
                "report_markdown": _relative_to_run(run_dir, report_file),
                "final_state_json": _relative_to_run(run_dir, final_state_path),
                "graph_log_json": _relative_to_run(run_dir, copied_graph_log) if copied_graph_log else None,
                **execution_artifacts,
            },
        }
    except Exception as exc:
        error_payload = {
            "ticker": ticker,
            "ticker_name": resolved_name,
            "status": "failed",
            "analysis_date": analysis_date,
            "error": str(exc),
            "traceback": traceback.format_exc(),
            "started_at": ticker_started.isoformat(),
            "finished_at": datetime.now(ZoneInfo(config.run.timezone)).isoformat(),
            "duration_seconds": round(perf_counter() - timer_start, 2),
        }
        error_path = ticker_dir / "error.json"
        _write_json(error_path, error_payload)

        return {
            "ticker": ticker,
            "ticker_name": resolved_name,
            "status": "failed",
            "analysis_date": analysis_date,
            "trade_date": None,
            "decision": None,
            "error": str(exc),
            "started_at": error_payload["started_at"],
            "finished_at": error_payload["finished_at"],
            "duration_seconds": error_payload["duration_seconds"],
            "metrics": {"llm_calls": 0, "tool_calls": 0, "tokens_in": 0, "tokens_out": 0},
            "artifacts": {
                "error_json": _relative_to_run(run_dir, error_path),
            },
        }


def _graph_config(config: ScheduledAnalysisConfig, engine_results_dir: Path) -> dict[str, Any]:
    graph_config = deepcopy(DEFAULT_CONFIG)
    graph_config["results_dir"] = str(engine_results_dir)
    graph_config["llm_provider"] = config.llm.provider
    graph_config["quick_think_llm"] = config.llm.quick_model
    graph_config["deep_think_llm"] = config.llm.deep_model
    graph_config["output_think_llm"] = config.llm.output_model
    graph_config["max_debate_rounds"] = config.run.max_debate_rounds
    graph_config["max_risk_discuss_rounds"] = config.run.max_risk_discuss_rounds
    graph_config["output_language"] = config.run.output_language
    graph_config["translation"] = {
        "backend": config.translation.backend,
        "model": config.translation.model,
        "model_path": config.translation.model_path,
        "tokenizer_path": config.translation.tokenizer_path,
        "device": config.translation.device,
        "compute_type": config.translation.compute_type,
        "max_chunk_chars": config.translation.max_chunk_chars,
        "allow_llm_fallback": config.translation.allow_llm_fallback,
        "allow_large_model": config.translation.allow_large_model,
    }
    graph_config["codex_reasoning_effort"] = config.llm.codex_reasoning_effort
    graph_config["codex_summary"] = config.llm.codex_summary
    graph_config["codex_personality"] = config.llm.codex_personality
    graph_config["codex_request_timeout"] = config.llm.codex_request_timeout
    graph_config["codex_max_retries"] = config.llm.codex_max_retries
    graph_config["codex_cleanup_threads"] = config.llm.codex_cleanup_threads
    if config.run.market == "KR":
        graph_config["market_country"] = "KR"
        graph_config["timezone"] = "Asia/Seoul"
        graph_config["tool_vendors"] = {
            "get_company_news": "naver,yfinance,alpha_vantage",
            "get_disclosures": "opendart",
            "get_macro_news": "ecos,alpha_vantage,yfinance",
            "get_social_sentiment": "naver,yfinance",
        }
    else:
        graph_config["market_country"] = "US"
        graph_config["tool_vendors"] = {
            "get_company_news": "alpha_vantage,yfinance",
            "get_social_sentiment": "yfinance",
        }
    if config.llm.codex_workspace_dir:
        graph_config["codex_workspace_dir"] = config.llm.codex_workspace_dir
    if config.llm.codex_binary:
        graph_config["codex_binary"] = config.llm.codex_binary
    return graph_config


def _select_public_decision(final_state: dict[str, Any], decision: Any) -> str:
    decision_candidates = [
        final_state.get("final_trade_decision"),
        (final_state.get("risk_debate_state") or {}).get("judge_decision"),
        (final_state.get("investment_debate_state") or {}).get("judge_decision"),
    ]
    for candidate in decision_candidates:
        if not isinstance(candidate, str):
            continue
        stripped = candidate.strip()
        if not stripped.startswith("{"):
            continue
        try:
            parse_structured_decision(stripped)
            return stripped
        except Exception:
            continue
    return str(decision or final_state.get("final_trade_decision") or "-")


def _serialize_final_state(final_state: dict[str, Any]) -> dict[str, Any]:
    investment_debate = final_state.get("investment_debate_state") or {}
    risk_debate = final_state.get("risk_debate_state") or {}
    return {
        "company_of_interest": final_state.get("company_of_interest"),
        "trade_date": final_state.get("trade_date"),
        "analysis_date": final_state.get("analysis_date"),
        "market_report": final_state.get("market_report"),
        "sentiment_report": final_state.get("sentiment_report"),
        "news_report": final_state.get("news_report"),
        "fundamentals_report": final_state.get("fundamentals_report"),
        "investment_debate_state": {
            "bull_history": investment_debate.get("bull_history", ""),
            "bear_history": investment_debate.get("bear_history", ""),
            "history": investment_debate.get("history", ""),
            "current_response": investment_debate.get("current_response", ""),
            "judge_decision": investment_debate.get("judge_decision", ""),
        },
        "trader_investment_plan": final_state.get("trader_investment_plan", ""),
        "investment_plan": final_state.get("investment_plan", ""),
        "risk_debate_state": {
            "aggressive_history": risk_debate.get("aggressive_history", ""),
            "conservative_history": risk_debate.get("conservative_history", ""),
            "neutral_history": risk_debate.get("neutral_history", ""),
            "history": risk_debate.get("history", ""),
            "judge_decision": risk_debate.get("judge_decision", ""),
        },
        "final_trade_decision": final_state.get("final_trade_decision", ""),
        "investor_summary_report": final_state.get("investor_summary_report", ""),
        "investor_writer_status": final_state.get("investor_writer_status", {}),
    }


def _settings_snapshot(config: ScheduledAnalysisConfig) -> dict[str, Any]:
    return {
        "provider": config.llm.provider,
        "quick_model": config.llm.quick_model,
        "deep_model": config.llm.deep_model,
        "output_model": config.llm.output_model,
        "codex_reasoning_effort": config.llm.codex_reasoning_effort,
        "output_language": config.run.output_language,
        "translation_backend": config.translation.backend,
        "translation_model": config.translation.model,
        "analysts": list(config.run.analysts),
        "trade_date_mode": config.run.trade_date_mode,
        "ticker_universe_mode": config.run.ticker_universe_mode,
        "market": config.run.market,
        "run_mode": config.run.run_mode,
        "configured_ticker_count": len(config.run.tickers),
        "max_debate_rounds": config.run.max_debate_rounds,
        "max_risk_discuss_rounds": config.run.max_risk_discuss_rounds,
        "report_polisher_enabled": config.run.report_polisher_enabled,
        "portfolio_report_polisher_enabled": config.portfolio.report_polisher_enabled,
        "ticker_name_overrides_count": len(config.run.ticker_name_overrides),
        "codex_workspace_dir": config.llm.codex_workspace_dir,
        "execution_refresh_enabled": config.execution.execution_refresh_enabled,
        "execution_refresh_checkpoints_kst": list(config.execution.execution_refresh_checkpoints_kst),
        "execution_max_data_age_seconds": config.execution.execution_max_data_age_seconds,
        "execution_publish_debug": config.execution.execution_publish_debug,
    }


def _resolve_run_tickers(config: ScheduledAnalysisConfig) -> list[str]:
    configured = list(config.run.tickers)
    mode = str(config.run.ticker_universe_mode or "config_only").strip().lower()
    if mode == "config_only":
        return configured

    if not config.portfolio.enabled or not config.portfolio.profile_path:
        print(
            "::warning::ticker_universe_mode requested account tickers, but portfolio profile is disabled; "
            "falling back to configured tickers."
        )
        return configured

    try:
        profile = load_portfolio_profile(config.portfolio.profile_path, config.portfolio.profile_name)
        snapshot = load_snapshot_for_profile(profile)
    except Exception as exc:
        print(
            "::warning::Could not load account snapshot for ticker_universe_mode "
            f"'{mode}': {exc}. Falling back to configured tickers."
        )
        return configured

    account_tickers = sorted(
        {str(position.canonical_ticker).strip().upper() for position in snapshot.positions if position.canonical_ticker}
    )
    if mode == "account_only":
        if account_tickers:
            return account_tickers
        print("::warning::ticker_universe_mode=account_only produced no account holdings; using configured tickers.")
        return configured

    merged: list[str] = []
    seen: set[str] = set()
    seen_identity: set[str] = set()
    for ticker in [*configured, *account_tickers]:
        normalized = str(ticker or "").strip().upper()
        if not normalized or normalized in seen:
            continue
        identity_key = _ticker_identity_key(normalized)
        if identity_key in seen_identity:
            continue
        seen.add(normalized)
        seen_identity.add(identity_key)
        merged.append(normalized)
    return merged or configured


def _ticker_identity_key(ticker: str) -> str:
    normalized = str(ticker or "").strip().upper()
    if len(normalized) == 6 and normalized.isdigit():
        return f"KR:{normalized}"
    if normalized.endswith(".KS") or normalized.endswith(".KQ"):
        base = normalized[:-3]
        if len(base) == 6 and base.isdigit():
            return f"KR:{base}"
    return normalized


def _effective_execution_checkpoints(config: ScheduledAnalysisConfig) -> list[str]:
    configured = [str(item).strip() for item in config.execution.execution_refresh_checkpoints_kst if str(item).strip()]
    if configured:
        return configured
    return list(_default_execution_checkpoints_kst(config.run.market))


def _collect_called_tool_names(final_state: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    for message in (final_state.get("messages") or []):
        tool_calls = message.get("tool_calls") if isinstance(message, dict) else getattr(message, "tool_calls", None)
        if not tool_calls:
            continue
        for tool_call in tool_calls:
            name = tool_call.get("name") if isinstance(tool_call, dict) else getattr(tool_call, "name", None)
            if not name and hasattr(tool_call, "get"):
                name = tool_call.get("name")
            if name:
                names.add(str(name))
    return names


def _compute_batch_metrics(ticker_summaries: list[dict[str, Any]]) -> dict[str, Any]:
    successful = [item for item in ticker_summaries if item.get("status") == "success"]
    decision_distribution: dict[str, int] = {}
    translated_action_distribution: dict[str, int] = {}
    stance_distribution: dict[str, int] = {}
    entry_action_distribution: dict[str, int] = {}
    trade_date_distribution: dict[str, int] = {}
    confidences: list[float] = []
    zero_company_news = 0

    for item in successful:
        trade_date = str(item.get("trade_date") or "").strip()
        if trade_date:
            trade_date_distribution[trade_date] = trade_date_distribution.get(trade_date, 0) + 1
        raw = item.get("decision")
        if isinstance(raw, str) and raw.strip().startswith("{"):
            try:
                parsed = parse_structured_decision(raw)
                decision_distribution[parsed.rating.value] = decision_distribution.get(parsed.rating.value, 0) + 1
                stance_distribution[parsed.portfolio_stance.value] = stance_distribution.get(parsed.portfolio_stance.value, 0) + 1
                entry_action_distribution[parsed.entry_action.value] = entry_action_distribution.get(parsed.entry_action.value, 0) + 1
                translated = _translate_legacy_rating(
                    rating=parsed.rating.value,
                    stance=parsed.portfolio_stance.value,
                    entry_action=parsed.entry_action.value,
                )
                translated_action_distribution[translated] = translated_action_distribution.get(translated, 0) + 1
                confidences.append(parsed.confidence)
                if parsed.data_coverage.company_news_count == 0:
                    zero_company_news += 1
                continue
            except Exception:
                pass
        value = str(raw or "UNKNOWN")
        decision_distribution[value] = decision_distribution.get(value, 0) + 1

    total = len(successful)
    avg_confidence = (sum(confidences) / len(confidences)) if confidences else None
    return {
        "decision_distribution": decision_distribution,
        "legacy_rating_distribution": decision_distribution,
        "translated_action_distribution": translated_action_distribution,
        "stance_distribution": stance_distribution,
        "entry_action_distribution": entry_action_distribution,
        "trade_date_distribution": trade_date_distribution,
        "avg_confidence": avg_confidence,
        "company_news_zero_ratio": (zero_company_news / total) if total else None,
    }


def _compute_batch_warnings(batch_metrics: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    decision_distribution = batch_metrics.get("decision_distribution") or {}
    stance_distribution = batch_metrics.get("stance_distribution") or {}
    entry_action_distribution = batch_metrics.get("entry_action_distribution") or {}
    trade_date_distribution = batch_metrics.get("trade_date_distribution") or {}
    if len(trade_date_distribution) > 1:
        distribution_blob = ", ".join(
            f"{date_value}={count}" for date_value, count in sorted(trade_date_distribution.items())
        )
        warnings.append(f"mixed_daily_cohort: trade_date_distribution includes {distribution_blob}.")
    total = sum(int(v) for v in decision_distribution.values())
    if total < 10:
        return warnings

    no_trade_count = int(decision_distribution.get("NO_TRADE", 0))
    no_trade_ratio = no_trade_count / total if total else 0.0
    bullish = int(stance_distribution.get("BULLISH", 0))
    waiting = int(entry_action_distribution.get("WAIT", 0))
    bullish_ratio = bullish / total if total else 0.0
    wait_ratio = waiting / total if total else 0.0
    if no_trade_ratio >= 0.8:
        translated_distribution = batch_metrics.get("translated_action_distribution") or {}
        warnings.append(
            f"High NO_TRADE concentration: {no_trade_count}/{total} ({no_trade_ratio:.0%})."
        )
        if bullish_ratio >= 0.3 or wait_ratio >= 0.3:
            warnings.append(
                "Legacy NO_TRADE concentration coexists with constructive stance/action signals; calibrate stance-action mapping."
            )
        if translated_distribution:
            translated_blob = ", ".join(
                f"{key} {int(value)}/{total}" for key, value in sorted(translated_distribution.items())
            )
            warnings.append(f"Translated action distribution: {translated_blob}.")
    if wait_ratio >= 0.8 and bullish_ratio >= 0.5:
        warnings.append(
            f"Wait-heavy constructive batch: WAIT {waiting}/{total} with BULLISH {bullish}/{total}; review entry-action calibration."
        )
    buy_like_count = int(decision_distribution.get("BUY", 0)) + int(decision_distribution.get("OVERWEIGHT", 0))
    if wait_ratio >= 0.6 and bullish_ratio >= 0.5 and buy_like_count == 0:
        warnings.append(
            "Constructive batch produced no BUY/OVERWEIGHT ratings; review rating calibration against stance and entry_action outputs."
        )
    return warnings


def _translate_legacy_rating(*, rating: str, stance: str, entry_action: str) -> str:
    normalized_rating = str(rating or "").strip().upper()
    normalized_stance = str(stance or "").strip().upper()
    normalized_entry = str(entry_action or "").strip().upper()
    if normalized_rating == "NO_TRADE":
        if normalized_stance == "BEARISH" or normalized_entry == "EXIT":
            return "AVOID"
        if normalized_stance == "BULLISH":
            return "WATCH_TRIGGER"
        return "WATCH"
    if normalized_stance == "BEARISH" and normalized_entry == "EXIT":
        return "AVOID"
    if normalized_stance == "BULLISH" and normalized_entry in {"ADD", "STARTER"}:
        return "ACTIONABLE"
    if normalized_entry == "WAIT":
        return "WATCH_TRIGGER"
    return "WATCH"


def _build_run_id(started_at: datetime, run_label: str) -> str:
    clean_label = "".join(ch if ch.isalnum() or ch in ("-", "_") else "-" for ch in run_label.strip()) or "run"
    return f"{started_at.strftime('%Y%m%dT%H%M%S')}_{clean_label}"


def _parse_ticker_override(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


def _previous_business_day(current: date) -> date:
    candidate = current - timedelta(days=1)
    while candidate.weekday() >= 5:
        candidate -= timedelta(days=1)
    return candidate


def _relative_to_run(run_dir: Path, path: Path | None) -> str | None:
    if path is None:
        return None
    return path.relative_to(run_dir).as_posix()


def _resolve_artifact_source(run_dir: Path, path_value: Any) -> Path:
    candidate = Path(str(path_value))
    if candidate.is_absolute():
        return candidate
    return run_dir / candidate


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _bootstrap_overlay_inputs_from_latest_run(
    *,
    config: ScheduledAnalysisConfig,
    run_dir: Path,
    tickers: list[str],
) -> tuple[list[dict[str, Any]], str | None]:
    source_manifest = _resolve_latest_overlay_source_manifest(config.storage.archive_dir, tickers=tickers)
    if source_manifest is None:
        raise RuntimeError("overlay_only/selective_rerun_only requires an existing latest-run.json from a prior full run.")
    source_run_id = str(source_manifest.get("run_id") or "")
    source_started_at = str(source_manifest.get("started_at") or "")
    if not source_run_id or len(source_started_at) < 4:
        raise RuntimeError("latest-run.json is missing run_id/started_at required for overlay bootstrap.")
    source_run_dir = config.storage.archive_dir / "runs" / source_started_at[:4] / source_run_id
    summaries: list[dict[str, Any]] = []
    target_tickers = {str(item).strip().upper() for item in tickers}
    for source in source_manifest.get("tickers", []):
        ticker = str(source.get("ticker") or "").strip().upper()
        if not ticker or (target_tickers and ticker not in target_tickers):
            continue
        if source.get("status") != "success":
            continue
        artifacts = source.get("artifacts") or {}
        analysis_rel = artifacts.get("analysis_json")
        if not analysis_rel:
            continue
        source_analysis = source_run_dir / analysis_rel
        if not source_analysis.exists():
            continue
        target_ticker_dir = run_dir / "tickers" / ticker
        target_ticker_dir.mkdir(parents=True, exist_ok=True)
        target_analysis = target_ticker_dir / "analysis.json"
        target_analysis.write_text(source_analysis.read_text(encoding="utf-8"), encoding="utf-8")
        copied_source_artifacts: dict[str, str] = {}
        for artifact_key in ("report_markdown", "final_state_json", "graph_log_json"):
            copied_artifact = _copy_bootstrap_artifact(
                source_run_dir=source_run_dir,
                run_dir=run_dir,
                target_ticker_dir=target_ticker_dir,
                artifacts=artifacts,
                artifact_key=artifact_key,
            )
            if copied_artifact:
                copied_source_artifacts[artifact_key] = copied_artifact

        contract_rel = artifacts.get("execution_contract_json")
        target_contract = target_ticker_dir / "execution_contract.json"
        if contract_rel and (source_run_dir / contract_rel).exists():
            target_contract.write_text((source_run_dir / contract_rel).read_text(encoding="utf-8"), encoding="utf-8")
        else:
            analysis_payload = json.loads(target_analysis.read_text(encoding="utf-8"))
            contract = build_execution_contract(ticker=ticker, analysis_payload=analysis_payload)
            _write_json(target_contract, contract.to_dict())

        summaries.append(
            {
                "ticker": ticker,
                "ticker_name": source.get("ticker_name") or ticker,
                "status": "success",
                "trade_date": source.get("trade_date"),
                "analysis_date": source.get("analysis_date"),
                "decision": source.get("decision"),
                "started_at": datetime.now(ZoneInfo(config.run.timezone)).isoformat(),
                "finished_at": datetime.now(ZoneInfo(config.run.timezone)).isoformat(),
                "duration_seconds": 0.0,
                "metrics": {"llm_calls": 0, "tool_calls": 0, "tokens_in": 0, "tokens_out": 0},
                "tool_telemetry": {"total_tool_calls": 0, "vendor_calls": {}, "fallback_count": 0, "events": []},
                "quality_flags": ("overlay_only_mode",),
                "report_writer": {"mode": "skipped_overlay_only"},
                "execution_contract": None,
                "execution_update": None,
                "artifacts": {
                    "analysis_json": _relative_to_run(run_dir, target_analysis),
                    **copied_source_artifacts,
                    "execution_contract_json": _relative_to_run(run_dir, target_contract),
                },
            }
        )
    if not summaries:
        raise RuntimeError("No successful tickers available in latest run to bootstrap overlay-only mode.")
    return summaries, source_run_id


def _copy_bootstrap_artifact(
    *,
    source_run_dir: Path,
    run_dir: Path,
    target_ticker_dir: Path,
    artifacts: dict[str, Any],
    artifact_key: str,
) -> str | None:
    source_rel = artifacts.get(artifact_key)
    if not source_rel:
        return None
    source_path = _resolve_artifact_source(source_run_dir, source_rel)
    if not source_path.is_file():
        return None

    if artifact_key == "report_markdown":
        target_path = target_ticker_dir / "report" / source_path.name
    elif artifact_key == "final_state_json":
        target_path = target_ticker_dir / "final_state.json"
    else:
        target_path = target_ticker_dir / source_path.name
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, target_path)
    return _relative_to_run(run_dir, target_path)


def _resolve_latest_overlay_source_manifest(archive_dir: Path, *, tickers: list[str] | None = None) -> dict[str, Any] | None:
    latest_manifest_path = archive_dir / "latest-run.json"
    if not latest_manifest_path.exists():
        return None

    candidate = json.loads(latest_manifest_path.read_text(encoding="utf-8"))
    run_mode = str((((candidate.get("settings") or {}).get("run_mode")) or "full")).strip().lower()
    if run_mode == "full" and _manifest_has_bootstrap_ready_ticker(candidate, tickers=tickers):
        return candidate

    source_run_id = str(candidate.get("overlay_source_run_id") or "").strip()
    if source_run_id:
        source_manifest_path = _find_run_manifest_path_by_run_id(archive_dir, source_run_id)
        if source_manifest_path is not None:
            resolved = json.loads(source_manifest_path.read_text(encoding="utf-8"))
            if _manifest_has_bootstrap_ready_ticker(resolved, tickers=tickers):
                return resolved

    latest_full = _find_latest_full_run_manifest(archive_dir, tickers=tickers)
    if latest_full is not None:
        return latest_full

    # Preserve prior behavior when no better candidate exists.
    return candidate


def _find_previous_comparable_manifest(
    *,
    archive_dir: Path,
    current_manifest: dict[str, Any],
) -> dict[str, Any] | None:
    runs_dir = archive_dir / "runs"
    if not runs_dir.exists():
        return None
    current_run_id = str(current_manifest.get("run_id") or "")
    current_settings = current_manifest.get("settings") or {}
    current_scope = str(current_settings.get("market_scope") or current_settings.get("market") or "").strip().lower()
    current_profile = str(((current_manifest.get("portfolio") or {}).get("profile")) or "").strip().lower()
    for year_dir in sorted((path for path in runs_dir.iterdir() if path.is_dir()), reverse=True):
        for run_dir in sorted((path for path in year_dir.iterdir() if path.is_dir()), reverse=True):
            manifest_path = run_dir / "run.json"
            if not manifest_path.exists():
                continue
            candidate = json.loads(manifest_path.read_text(encoding="utf-8"))
            if str(candidate.get("run_id") or "") == current_run_id:
                continue
            candidate_settings = candidate.get("settings") or {}
            scope = str(candidate_settings.get("market_scope") or candidate_settings.get("market") or "").strip().lower()
            if current_scope and scope and current_scope != scope:
                continue
            profile = str(((candidate.get("portfolio") or {}).get("profile")) or "").strip().lower()
            if current_profile and profile and current_profile != profile:
                continue
            return candidate
    return None


def _market_session_phase(overlay_phase: dict[str, Any]) -> str:
    phase = str(overlay_phase.get("name") or "").upper()
    if phase == "PRE_OPEN":
        return "pre_open"
    if phase.startswith("CHECKPOINT_"):
        return "in_session"
    if phase == "POST_RESEARCH":
        return "post_research"
    if phase == "DISABLED":
        return "disabled"
    return "unknown"


def _compute_run_quality(*, manifest: dict[str, Any]) -> dict[str, Any]:
    execution = manifest.get("execution") or {}
    summary = manifest.get("summary") or {}
    total_tickers = max(int(summary.get("total_tickers") or 0), 1)
    degraded_ratio = len(execution.get("degraded") or []) / total_tickers
    batch_metrics = manifest.get("batch_metrics") or {}
    news_zero_ratio = float(batch_metrics.get("company_news_zero_ratio") or 0.0)
    semantic_health = ((manifest.get("portfolio") or {}).get("semantic_health") or {})
    fallback_ratio = float(semantic_health.get("rule_only_fallback_ratio") or 0.0)
    judge_health = "degraded" if fallback_ratio >= 0.3 else "ok"
    phase = str(((execution.get("overlay_phase") or {}).get("name")) or "").upper()
    if phase.startswith("CHECKPOINT_"):
        phase_score = 1.0
    elif phase == "PRE_OPEN":
        phase_score = 0.7
    else:
        phase_score = 0.45
    actionable = len(execution.get("actionable_now") or [])
    triggerable = len(execution.get("triggered_pending_close") or [])
    signal_score = min((actionable + triggerable) / max(total_tickers, 1), 1.0)
    score = (
        (1.0 - degraded_ratio) * 0.40
        + (1.0 - min(news_zero_ratio, 1.0)) * 0.15
        + (1.0 - min(fallback_ratio, 1.0)) * 0.10
        + phase_score * 0.30
        + signal_score * 0.05
    )
    return {
        "run_quality_score": round(max(min(score, 1.0), 0.0), 4),
        "signals": {
            "stale_ratio": round(degraded_ratio, 4),
            "company_news_zero_ratio": round(news_zero_ratio, 4),
            "judge_health": judge_health,
            "rule_only_fallback_ratio": round(fallback_ratio, 4),
            "phase": phase or "UNKNOWN",
            "triggerable_count": triggerable,
            "actionable_count": actionable,
        },
        "usefulness_rank": int(round((1.0 - max(min(score, 1.0), 0.0)) * 100)),
    }


def _manifest_has_bootstrap_ready_ticker(manifest: dict[str, Any], *, tickers: list[str] | None) -> bool:
    target_tickers = {str(item).strip().upper() for item in (tickers or []) if str(item).strip()}
    for source in manifest.get("tickers", []):
        ticker = str(source.get("ticker") or "").strip().upper()
        if not ticker:
            continue
        if target_tickers and ticker not in target_tickers:
            continue
        if source.get("status") != "success":
            continue
        artifacts = source.get("artifacts") or {}
        if artifacts.get("analysis_json"):
            return True
    return False


def _find_latest_full_run_manifest(archive_dir: Path, *, tickers: list[str] | None = None) -> dict[str, Any] | None:
    runs_dir = archive_dir / "runs"
    if not runs_dir.exists():
        return None
    year_dirs = sorted((path for path in runs_dir.iterdir() if path.is_dir()), reverse=True)
    for year_dir in year_dirs:
        run_dirs = sorted((path for path in year_dir.iterdir() if path.is_dir()), reverse=True)
        for run_dir in run_dirs:
            manifest_path = run_dir / "run.json"
            if not manifest_path.exists():
                continue
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            run_mode = str((((manifest.get("settings") or {}).get("run_mode")) or "full")).strip().lower()
            if run_mode != "full":
                continue
            if _manifest_has_bootstrap_ready_ticker(manifest, tickers=tickers):
                return manifest
    return None


def _find_run_manifest_path_by_run_id(archive_dir: Path, run_id: str) -> Path | None:
    runs_dir = archive_dir / "runs"
    if not runs_dir.exists():
        return None
    for year_dir in sorted(runs_dir.iterdir()):
        if not year_dir.is_dir():
            continue
        candidate = year_dir / run_id / "run.json"
        if candidate.exists():
            return candidate
    return None


def _has_ticker_execution_updates(execution_updates: dict[str, dict[str, Any]]) -> bool:
    return any(not str(key).startswith("_") for key in execution_updates)


def _select_due_checkpoints(*, now_kst: datetime, checkpoints: list[str]) -> tuple[list[str], str]:
    normalized = [str(item).strip() for item in checkpoints if str(item).strip()]
    if not normalized:
        return (["post_research"], "POST_RESEARCH")
    due: list[str] = []
    for item in normalized:
        try:
            hour_text, minute_text = item.split(":")
            hour = int(hour_text)
            minute = int(minute_text)
        except Exception:
            continue
        if (now_kst.hour, now_kst.minute) >= (hour, minute):
            due.append(item)
    if due:
        # Minimize API usage: execute only the most recent due checkpoint in this run.
        return ([due[-1]], f"CHECKPOINT_{due[-1].replace(':', '_')}")
    return ([], "PRE_OPEN")


def _run_selective_rerun(
    *,
    config: ScheduledAnalysisConfig,
    run_dir: Path,
    engine_results_dir: Path,
    ticker_summaries: list[dict[str, Any]],
    targets: dict[str, list[str]],
) -> list[dict[str, Any]]:
    index_by_ticker = {
        str(item.get("ticker") or "").strip().upper(): idx
        for idx, item in enumerate(ticker_summaries)
    }
    results: list[dict[str, Any]] = []
    for ticker, reasons in sorted(targets.items()):
        index = index_by_ticker.get(str(ticker).upper())
        if index is None:
            continue
        rerun_summary = _run_single_ticker(
            config=config,
            ticker=ticker,
            run_dir=run_dir,
            engine_results_dir=engine_results_dir,
        )
        rerun_summary["selective_rerun"] = {
            "trigger_reasons": list(reasons),
            "rerun_at": datetime.now(ZoneInfo(config.run.timezone)).isoformat(),
        }
        ticker_summaries[index] = rerun_summary
        results.append(
            {
                "ticker": ticker,
                "reasons": list(reasons),
                "status": rerun_summary.get("status"),
            }
        )
    return results


def _run_execution_overlay_passes(
    *,
    config: ScheduledAnalysisConfig,
    run_dir: Path,
    ticker_summaries: list[dict[str, Any]],
    checkpoints: list[str],
) -> dict[str, dict[str, Any]]:
    updates_by_ticker: dict[str, dict[str, Any]] = {}
    llm_model = config.execution.execution_llm_summary_model
    for checkpoint in checkpoints:
        checkpoint_label = str(checkpoint).strip() or "post_research"
        for summary in ticker_summaries:
            if summary.get("status") != "success":
                continue
            ticker = str(summary.get("ticker") or "").strip().upper()
            if not ticker:
                continue
            artifacts = summary.get("artifacts") or {}
            summary["artifacts"] = artifacts
            contract_rel = artifacts.get("execution_contract_json")
            if not contract_rel:
                continue
            contract_path = run_dir / contract_rel
            if not contract_path.exists():
                continue
            contract_dict: dict[str, Any] = {}
            attempt_payload = _build_intraday_attempt_payload(
                ticker=ticker,
                checkpoint_label=checkpoint_label,
                interval="5m",
                success=False,
                attempted_at=datetime.now(ZoneInfo(config.run.timezone)).isoformat(),
            )
            try:
                contract_dict = json.loads(contract_path.read_text(encoding="utf-8"))
                contract = _ExecutionContractShim(contract_dict).to_contract()
                market = fetch_intraday_market_snapshot(ticker, interval="5m")
                attempt_payload.update(
                    {
                        "success": True,
                        "provider": market.provider,
                        "market_data_asof": market.asof,
                    }
                )
                update = evaluate_execution_state(
                    contract,
                    market,
                    now=datetime.now(ZoneInfo(config.run.timezone)),
                    max_data_age_seconds=config.execution.execution_max_data_age_seconds,
                    refresh_checkpoint=checkpoint_label,
                )
                update_payload = update.to_dict()
                update_payload["intraday_snapshot_attempt"] = attempt_payload
                ticker_dir = run_dir / "tickers" / ticker
                checkpoint_dir = ticker_dir / "execution" / "checkpoints"
                _write_json(checkpoint_dir / _checkpoint_update_filename(checkpoint_label), update_payload)
                update_path = ticker_dir / "execution_update.json"
                _write_json(update_path, update_payload)
                summary["artifacts"]["execution_update_json"] = _relative_to_run(run_dir, update_path)

                md_path = ticker_dir / "execution_update.md"
                md_text = render_execution_update_markdown(
                    contract,
                    update,
                    llm_settings=config.llm,
                    llm_model=llm_model,
                    thesis_summary=str((summary.get("decision") or "")[:500]),
                    include_reason_codes=config.execution.execution_publish_debug,
                )
                md_path.write_text(md_text, encoding="utf-8")
                summary["artifacts"]["execution_update_md"] = _relative_to_run(run_dir, md_path)
                summary["execution_update"] = update_payload
                summary["intraday_snapshot_attempt"] = attempt_payload
                _append_analysis_intraday_attempt(run_dir=run_dir, ticker_summary=summary, attempt_payload=attempt_payload)
                updates_by_ticker[ticker] = update_payload
            except Exception as exc:
                attempt_payload.update(
                    {
                        "success": False,
                        "error_type": exc.__class__.__name__,
                        "error": _summarize_exception(exc),
                    }
                )
                ticker_dir = run_dir / "tickers" / ticker
                checkpoint_dir = ticker_dir / "execution" / "checkpoints"
                update_payload = _build_failed_execution_update_payload(
                    ticker=ticker,
                    checkpoint_label=checkpoint_label,
                    attempt_payload=attempt_payload,
                    summary=summary,
                    contract_payload=contract_dict,
                    now=datetime.now(ZoneInfo(config.run.timezone)),
                )
                _write_json(checkpoint_dir / _checkpoint_update_filename(checkpoint_label), update_payload)
                update_path = ticker_dir / "execution_update.json"
                _write_json(update_path, update_payload)
                summary["artifacts"]["execution_update_json"] = _relative_to_run(run_dir, update_path)
                md_path = ticker_dir / "execution_update.md"
                md_path.write_text(
                    "# Execution overlay unavailable\n\n"
                    f"- Ticker: {ticker}\n"
                    f"- Checkpoint: {checkpoint_label}\n"
                    f"- Reason: {_summarize_exception(exc)}\n",
                    encoding="utf-8",
                )
                summary["artifacts"]["execution_update_md"] = _relative_to_run(run_dir, md_path)
                summary["execution_update"] = update_payload
                summary["intraday_snapshot_attempt"] = attempt_payload
                _append_analysis_intraday_attempt(run_dir=run_dir, ticker_summary=summary, attempt_payload=attempt_payload)
                updates_by_ticker[ticker] = update_payload
                print(f"::warning::Execution overlay checkpoint '{checkpoint_label}' failed for {ticker}: {exc}")
        updates_by_ticker["_latest_checkpoint"] = {"value": checkpoint_label}
    return updates_by_ticker


def _build_intraday_attempt_payload(
    *,
    ticker: str,
    checkpoint_label: str,
    interval: str,
    success: bool,
    attempted_at: str,
) -> dict[str, Any]:
    return {
        "ticker": ticker,
        "attempted": True,
        "success": bool(success),
        "checkpoint": checkpoint_label,
        "interval": interval,
        "attempted_at": attempted_at,
    }


def _checkpoint_update_filename(checkpoint_label: str) -> str:
    safe_label = "".join(
        char if char.isalnum() or char in {"-", "_", "."} else "_"
        for char in str(checkpoint_label or "post_research")
    ).strip("_")
    return f"execution_update_{safe_label or 'post_research'}.json"


def _build_failed_execution_update_payload(
    *,
    ticker: str,
    checkpoint_label: str,
    attempt_payload: dict[str, Any],
    summary: dict[str, Any],
    contract_payload: dict[str, Any] | None,
    now: datetime,
) -> dict[str, Any]:
    contract_payload = contract_payload or {}
    return {
        "ticker": ticker,
        "analysis_asof": str(
            contract_payload.get("analysis_asof")
            or summary.get("finished_at")
            or summary.get("started_at")
            or ""
        ),
        "execution_asof": now.isoformat(),
        "market_data_asof": contract_payload.get("market_data_asof"),
        "source": {"provider": None, "interval": attempt_payload.get("interval"), "status": "failed"},
        "last_price": None,
        "session_vwap": None,
        "day_high": None,
        "day_low": None,
        "intraday_volume": None,
        "avg20_daily_volume": None,
        "relative_volume": None,
        "price_state": "UNAVAILABLE",
        "volume_state": "UNAVAILABLE",
        "event_state": "UNKNOWN",
        "decision_state": "DEGRADED",
        "decision_now": "NONE",
        "decision_if_triggered": str(contract_payload.get("action_if_triggered") or "NONE"),
        "execution_timing_state": "DEGRADED",
        "trigger_status": {
            "breakout_hit_intraday": False,
            "close_confirmation_pending": False,
            "pullback_zone_active": False,
            "invalidated": False,
        },
        "changed_fields": ["execution_asof", "intraday_snapshot_attempt"],
        "reason_codes": ["intraday_snapshot_unavailable"],
        "staleness_seconds": None,
        "data_health": "UNAVAILABLE",
        "refresh_checkpoint": checkpoint_label,
        "intraday_snapshot_attempt": attempt_payload,
    }


def _append_analysis_intraday_attempt(
    *,
    run_dir: Path,
    ticker_summary: dict[str, Any],
    attempt_payload: dict[str, Any],
) -> None:
    artifacts = ticker_summary.get("artifacts") or {}
    analysis_rel = artifacts.get("analysis_json")
    if not analysis_rel:
        return
    analysis_path = run_dir / analysis_rel
    if not analysis_path.exists():
        return
    try:
        payload = json.loads(analysis_path.read_text(encoding="utf-8"))
    except Exception:
        return
    attempts = payload.get("intraday_snapshot_attempts")
    if not isinstance(attempts, list):
        attempts = []
    attempts.append(attempt_payload)
    payload["intraday_snapshot_attempts"] = attempts
    payload["latest_intraday_snapshot_attempt"] = attempt_payload
    payload["intraday_snapshot_latest_attempt"] = attempt_payload
    _write_json(analysis_path, payload)


def _load_execution_contracts_for_run(
    run_dir: Path,
    ticker_summaries: list[dict[str, Any]],
) -> dict[str, Any]:
    loaded: dict[str, Any] = {}
    for summary in ticker_summaries:
        if summary.get("status") != "success":
            continue
        ticker = str(summary.get("ticker") or "").strip().upper()
        artifacts = summary.get("artifacts") or {}
        rel_path = artifacts.get("execution_contract_json")
        if not rel_path:
            continue
        path = run_dir / rel_path
        if not path.exists():
            continue
        try:
            loaded[ticker] = _ExecutionContractShim(json.loads(path.read_text(encoding="utf-8")))
        except Exception:
            continue
    return loaded


def _build_execution_summary(
    *,
    run_id: str,
    ticker_updates: dict[str, dict[str, Any]],
    checkpoint: str,
) -> dict[str, Any]:
    ticker_updates = {k: v for k, v in ticker_updates.items() if not k.startswith("_")}
    if not ticker_updates:
        return {
            "run_id": run_id,
            "refresh_checkpoint": checkpoint,
            "execution_asof": None,
            "actionable_now": [],
            "triggered_pending_close": [],
            "wait": [],
            "invalidated": [],
            "degraded": [],
            "top_priority_order": [],
            "market_regime": "degraded",
            "notes": ["Execution overlay produced no ticker updates."],
        }
    actionable_now = sorted(
        [ticker for ticker, payload in ticker_updates.items() if payload.get("decision_state") == "ACTIONABLE_NOW"]
    )
    pending_close = sorted(
        [ticker for ticker, payload in ticker_updates.items() if payload.get("decision_state") == "TRIGGERED_PENDING_CLOSE"]
    )
    wait = sorted([ticker for ticker, payload in ticker_updates.items() if payload.get("decision_state") == "WAIT"])
    invalidated = sorted(
        [ticker for ticker, payload in ticker_updates.items() if payload.get("decision_state") == "INVALIDATED"]
    )
    degraded = sorted(
        [ticker for ticker, payload in ticker_updates.items() if payload.get("decision_state") == "DEGRADED"]
    )
    first = next(iter(ticker_updates.values()))
    return {
        "run_id": run_id,
        "refresh_checkpoint": checkpoint,
        "execution_asof": first.get("execution_asof"),
        "actionable_now": actionable_now,
        "triggered_pending_close": pending_close,
        "wait": wait,
        "invalidated": invalidated,
        "degraded": degraded,
        "top_priority_order": actionable_now + pending_close + wait + invalidated + degraded,
        "market_regime": "constructive_but_selective" if actionable_now else "wait_and_watch",
        "notes": [
            "Do not treat pre-open report as executable without overlay refresh.",
            "Close-confirmation setups remain pending until end-of-day.",
        ],
    }


class _ExecutionUpdateShim:
    def __init__(self, payload: dict[str, Any]):
        self.ticker = str(payload.get("ticker") or "")
        self.decision_state = type("State", (), {"value": str(payload.get("decision_state") or "WAIT")})()


class _ExecutionContractShim:
    def __init__(self, payload: dict[str, Any]):
        self.payload = payload
        self.event_guard = payload.get("event_guard")

    def to_contract(self) -> ExecutionContract:
        guard_payload = self.payload.get("event_guard") or {}
        guard = EventGuard(
            earnings_date=guard_payload.get("earnings_date"),
            block_new_position_within_days=int(guard_payload.get("block_new_position_within_days", 0) or 0),
            allow_add_only_after_event=bool(guard_payload.get("allow_add_only_after_event", False)),
            requires_post_event_rerun=bool(guard_payload.get("requires_post_event_rerun", False)),
        )
        return ExecutionContract(
            ticker=str(self.payload.get("ticker") or ""),
            analysis_asof=str(self.payload.get("analysis_asof") or ""),
            market_data_asof=str(self.payload.get("market_data_asof") or ""),
            level_basis=LevelBasis(str(self.payload.get("level_basis") or "daily_close")),
            thesis_state=ThesisState(str(self.payload.get("thesis_state") or "neutral")),
            primary_setup=PrimarySetup(str(self.payload.get("primary_setup") or "watch_only")),
            portfolio_stance=str(self.payload.get("portfolio_stance") or "NEUTRAL"),
            entry_action_base=str(self.payload.get("entry_action_base") or "WAIT"),
            setup_quality=str(self.payload.get("setup_quality") or "DEVELOPING"),
            confidence=float(self.payload.get("confidence") or 0.4),
            action_if_triggered=ActionIfTriggered(str(self.payload.get("action_if_triggered") or "NONE")),
            starter_fraction_of_target=self.payload.get("starter_fraction_of_target"),
            breakout_level=self.payload.get("breakout_level"),
            breakout_confirmation=(
                BreakoutConfirmation(str(self.payload.get("breakout_confirmation")))
                if self.payload.get("breakout_confirmation")
                else None
            ),
            pullback_buy_zone=(
                PullbackBuyZone(
                    low=float((self.payload.get("pullback_buy_zone") or {}).get("low")),
                    high=float((self.payload.get("pullback_buy_zone") or {}).get("high")),
                )
                if isinstance(self.payload.get("pullback_buy_zone"), dict)
                and (self.payload.get("pullback_buy_zone") or {}).get("low") is not None
                and (self.payload.get("pullback_buy_zone") or {}).get("high") is not None
                else None
            ),
            invalid_if_close_below=self.payload.get("invalid_if_close_below"),
            invalid_if_intraday_below=self.payload.get("invalid_if_intraday_below"),
            min_relative_volume=self.payload.get("min_relative_volume"),
            session_vwap_preference=SessionVWAPPreference(
                str(self.payload.get("session_vwap_preference") or "indifferent")
            ),
            event_guard=guard,
            reason_codes=tuple(self.payload.get("reason_codes") or []),
            notes=tuple(self.payload.get("notes") or []),
        )
