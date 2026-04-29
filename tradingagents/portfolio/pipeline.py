from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from tradingagents.report_writer import polish_portfolio_report_markdown
from tradingagents.external.prism_conflicts import (
    enrich_candidates_with_prism,
    reconcile_prism_with_actions,
    write_prism_signal_artifacts,
)
from tradingagents.external.prism_loader import load_prism_signals
from tradingagents.external.prism_models import PrismIngestionResult
from tradingagents.live.sell_side_delta import build_sell_side_delta_candidates, render_risk_action_delta_markdown
from tradingagents.scanner.sector_regime import apply_buy_matrix_overlay
from tradingagents.summary_image.generator import generate_summary_image_artifacts

from .action_judge import arbitrate_portfolio_actions
from .account_models import AccountSnapshot
from .allocation import build_recommendation
from .candidates import build_portfolio_candidates
from .csv_import import load_snapshot_from_positions_csv
from .gates import apply_gates
from .kis import PortfolioConfigurationError, load_account_snapshot_from_kis
from .manual_snapshot import load_manual_snapshot
from .profiles import load_portfolio_profile
from .reporting import render_portfolio_report_markdown
from .semantic_judge import build_semantic_verdicts
from .state_store import save_portfolio_outputs


def run_portfolio_pipeline(
    *,
    run_dir: Path,
    manifest: dict[str, Any],
    portfolio_settings: Any,
    llm_settings: Any | None = None,
    summary_image_settings: Any | None = None,
    external_data_settings: Any | None = None,
) -> dict[str, Any]:
    if not getattr(portfolio_settings, "enabled", False):
        return {"status": "disabled"}

    profile = load_portfolio_profile(portfolio_settings.profile_path, portfolio_settings.profile_name)
    if not profile.enabled:
        return {"status": "disabled", "reason": f"profile {profile.name} is disabled"}

    private_dir = run_dir / profile.private_output_dirname
    status_path = private_dir / "status.json"
    try:
        snapshot = load_snapshot_for_profile(profile)
        candidates, candidate_warnings = build_portfolio_candidates(
            snapshot=snapshot,
            run_dir=run_dir,
            manifest=manifest,
            watch_tickers=profile.watch_tickers,
        )
        prism_ingestion = _load_prism_ingestion(external_data_settings)
        candidates = enrich_candidates_with_prism(
            candidates,
            prism_ingestion,
            confidence_cap=_prism_confidence_cap(external_data_settings),
        )
        semantic_candidates, semantic_verdicts, semantic_warnings = build_semantic_verdicts(
            candidates=candidates,
            run_dir=run_dir,
            manifest=manifest,
            llm_settings=llm_settings,
            portfolio_settings=portfolio_settings,
        )
        all_warnings = (
            list(manifest.get("warnings") or [])
            + list(candidate_warnings)
            + list(semantic_warnings)
            + list(snapshot.warnings)
        )
        gated_candidates = apply_gates(
            candidates=semantic_candidates,
            snapshot=snapshot,
            batch_metrics=manifest.get("batch_metrics") or {},
            warnings=all_warnings,
            profile=profile,
        )
        gated_candidates = apply_buy_matrix_overlay(
            gated_candidates,
            market_regime=str((manifest.get("batch_metrics") or {}).get("market_regime") or ""),
        )
        recommendation, scored_candidates = build_recommendation(
            candidates=gated_candidates,
            snapshot=snapshot,
            batch_metrics=manifest.get("batch_metrics") or {},
            warnings=all_warnings,
            profile=profile,
            report_date=str(manifest.get("started_at") or "")[:10],
        )
        live_sell_side_delta = build_sell_side_delta_candidates(
            live_context_delta=manifest.get("live_context_delta"),
            held_tickers={position.canonical_ticker for position in snapshot.positions},
        )
        recommendation, action_judge_payload, action_judge_warnings = arbitrate_portfolio_actions(
            recommendation=recommendation,
            candidates=scored_candidates,
            snapshot=snapshot,
            batch_metrics=manifest.get("batch_metrics") or {},
            warnings=all_warnings,
            llm_settings=llm_settings,
            portfolio_settings=portfolio_settings,
        )
        all_warnings.extend(action_judge_warnings)
        external_signal_context = _build_external_signal_context(
            run_dir=run_dir,
            recommendation=recommendation,
            ingestion=prism_ingestion,
            external_data_settings=external_data_settings,
        )
        markdown = render_portfolio_report_markdown(
            snapshot=snapshot,
            recommendation=recommendation,
            candidates=scored_candidates,
            live_context_delta=manifest.get("live_context_delta"),
            live_sell_side_delta=live_sell_side_delta,
            external_reconciliation=external_signal_context.get("reconciliation"),
        )
        markdown, report_writer_payload = polish_portfolio_report_markdown(
            markdown,
            snapshot=snapshot,
            recommendation=recommendation,
            language=str((manifest.get("settings") or {}).get("output_language") or "Korean"),
            llm_settings=llm_settings,
            enabled=bool(getattr(portfolio_settings, "report_polisher_enabled", True)),
        )
        summary_image_artifacts = generate_summary_image_artifacts(
            private_dir=private_dir,
            snapshot=snapshot,
            recommendation=recommendation,
            candidates=scored_candidates,
            manifest=manifest,
            live_sell_side_delta=live_sell_side_delta,
            report_writer_payload=report_writer_payload,
            settings=summary_image_settings,
        )
        artifact_paths = save_portfolio_outputs(
            private_dir=private_dir,
            snapshot=snapshot,
            candidates=scored_candidates,
            recommendation=recommendation,
            portfolio_report_markdown=markdown,
            semantic_verdicts=semantic_verdicts,
            action_judge_payload=action_judge_payload,
            report_writer_payload=report_writer_payload,
            batch_metrics=manifest.get("batch_metrics") or {},
            warnings=all_warnings,
            live_sell_side_delta=live_sell_side_delta,
            risk_action_delta_markdown=render_risk_action_delta_markdown(live_sell_side_delta),
            summary_image_artifacts=summary_image_artifacts,
            external_signal_artifacts=external_signal_context.get("artifacts") or {},
            external_reconciliation=external_signal_context.get("reconciliation"),
        )
        status_value = _derive_pipeline_status(snapshot)
        semantic_health = _build_semantic_health(scored_candidates)
        if semantic_health["judge_unavailable"]:
            status_value = "degraded"
        status = {
            "status": status_value,
            "profile": profile.name,
            "snapshot_health": snapshot.snapshot_health,
            "watchlist_reason": _derive_watchlist_reason(snapshot),
            "semantic_health": semantic_health,
            "action_summary": _build_action_summary(recommendation),
            "sell_side_summary": recommendation.data_health_summary.get("sell_side_distribution") or {},
            "sell_side_calibration_warnings": _sell_side_calibration_warnings(recommendation),
            "report_writer": report_writer_payload,
            "external_signals": external_signal_context.get("status"),
            "private_output_dir": private_dir.as_posix(),
            "artifacts": artifact_paths,
            "generated_at": datetime.now().astimezone().isoformat(),
        }
        _write_json(status_path, status)
        return status
    except Exception as exc:
        status = {
            "status": "failed",
            "profile": getattr(portfolio_settings, "profile_name", None),
            "private_output_dir": private_dir.as_posix(),
            "error": str(exc),
            "generated_at": datetime.now().astimezone().isoformat(),
        }
        _write_json(status_path, status)
        if getattr(portfolio_settings, "continue_on_error", True):
            return status
        raise


def load_snapshot_for_profile(profile) -> Any:
    if profile.broker == "manual":
        if not profile.manual_snapshot_path:
            raise PortfolioConfigurationError("manual broker profile requires manual_snapshot_path.")
        return load_manual_snapshot(profile.manual_snapshot_path)
    if profile.broker == "csv":
        return load_snapshot_from_positions_csv(profile)
    if profile.broker in {"watchlist", "paper", "none"}:
        return _load_watchlist_only_snapshot(profile)
    if profile.broker == "kis":
        try:
            return load_account_snapshot_from_kis(profile)
        except PortfolioConfigurationError:
            if profile.manual_snapshot_path and profile.manual_snapshot_path.exists():
                return load_manual_snapshot(profile.manual_snapshot_path)
            if profile.csv_positions_path and profile.csv_positions_path.exists():
                return load_snapshot_from_positions_csv(profile)
            raise
    raise PortfolioConfigurationError(f"Unsupported portfolio broker '{profile.broker}'.")


def _load_watchlist_only_snapshot(profile) -> AccountSnapshot:
    now = datetime.now().astimezone()
    return AccountSnapshot(
        snapshot_id=f"{now.strftime('%Y%m%dT%H%M%S')}_watchlist_{profile.name}",
        as_of=now.isoformat(),
        broker=profile.broker,
        account_id=profile.name,
        currency="KRW",
        settled_cash_krw=0,
        available_cash_krw=0,
        buying_power_krw=0,
        total_equity_krw=0,
        snapshot_health="WATCHLIST_ONLY",
        cash_diagnostics={
            "source": "watchlist_only_profile",
            "reason": "No broker account snapshot is configured for this scheduled profile.",
        },
        pending_orders=tuple(),
        positions=tuple(),
        constraints=profile.constraints,
        warnings=(
            "No broker account snapshot is configured; generated a watchlist-only account report.",
        ),
    )


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _load_prism_ingestion(external_data_settings: Any | None) -> PrismIngestionResult:
    try:
        return load_prism_signals(external_data_settings)
    except Exception as exc:
        return PrismIngestionResult(
            enabled=bool(getattr(getattr(external_data_settings, "prism", None), "enabled", False)),
            ok=False,
            warnings=[f"external_prism_ingestion_failed:{exc}"],
        )


def _build_external_signal_context(
    *,
    run_dir: Path,
    recommendation: Any,
    ingestion: PrismIngestionResult,
    external_data_settings: Any | None,
) -> dict[str, Any]:
    settings = getattr(external_data_settings, "prism", None) or getattr(external_data_settings, "prism_dashboard", None)
    if not settings or not getattr(settings, "enabled", False) or not getattr(settings, "use_for_ui_comparison", True):
        return {"status": {"enabled": False}, "reconciliation": None, "artifacts": {}}

    reconciliation = reconcile_prism_with_actions(
        tradingagents_actions=recommendation.actions,
        ingestion=ingestion,
        confidence_cap=_prism_confidence_cap(external_data_settings),
    )
    artifacts = write_prism_signal_artifacts(
        run_dir=run_dir,
        ingestion=ingestion,
        reconciliation=reconciliation,
    )
    return {
        "status": {
            "enabled": True,
            "prism": ingestion.status_dict(),
            "reconciliation_summary": reconciliation.get("summary") or {},
            "artifacts": artifacts,
        },
        "reconciliation": reconciliation,
        "artifacts": artifacts,
    }


def _prism_confidence_cap(external_data_settings: Any | None) -> float:
    settings = getattr(external_data_settings, "prism", None) or getattr(external_data_settings, "prism_dashboard", None)
    try:
        return float(getattr(settings, "confidence_cap", 0.25))
    except (TypeError, ValueError):
        return 0.25


def _derive_pipeline_status(snapshot) -> str:
    if snapshot.snapshot_health == "INVALID_SNAPSHOT":
        return "degraded"
    if snapshot.snapshot_health == "WATCHLIST_ONLY":
        return "watchlist_only"
    if snapshot.snapshot_health == "CAPITAL_CONSTRAINED":
        return "capital_constrained"
    return "success"


def _derive_watchlist_reason(snapshot) -> str | None:
    if str(getattr(snapshot, "snapshot_health", "")).strip().upper() != "WATCHLIST_ONLY":
        return None

    diagnostics = getattr(snapshot, "cash_diagnostics", {}) or {}
    source = str(diagnostics.get("source") or "").strip().lower() if isinstance(diagnostics, dict) else ""
    warnings = [str(item).strip().lower() for item in (getattr(snapshot, "warnings", ()) or ()) if str(item).strip()]
    warning_blob = " ".join(warnings)

    if source == "watchlist_only_profile" or "no broker account snapshot is configured" in warning_blob:
        return "NO_BROKER_SNAPSHOT"
    if "no positions" in warning_blob and "insufficient cash" in warning_blob:
        return "LOW_CAPITAL_EMPTY_ACCOUNT"
    if "insufficient cash" in warning_blob:
        return "LOW_CAPITAL"
    return "WATCHLIST_POLICY"


def _build_semantic_health(candidates: list[Any]) -> dict[str, Any]:
    total = max(len(candidates), 1)
    fallback_count = sum(
        1 for candidate in candidates if str(getattr(candidate, "decision_source", "")).upper() == "RULE_ONLY_FALLBACK"
    )
    review_required_count = sum(1 for candidate in candidates if bool(getattr(candidate, "review_required", False)))
    fallback_ratio = fallback_count / total
    return {
        "total_candidates": len(candidates),
        "rule_only_fallback_count": fallback_count,
        "review_required_count": review_required_count,
        "rule_only_fallback_ratio": round(fallback_ratio, 4),
        "judge_unavailable": fallback_ratio >= 0.3,
    }


def _build_action_summary(recommendation) -> dict[str, Any]:
    return {
        "relative_actions": {
            action.canonical_ticker: action.portfolio_relative_action
            for action in recommendation.actions
        },
        "actions_now": {
            action.canonical_ticker: action.action_now
            for action in recommendation.actions
        },
    }


def _sell_side_calibration_warnings(recommendation) -> list[str]:
    warnings: list[str] = []
    distribution = recommendation.data_health_summary.get("sell_side_distribution") or {}
    if int(distribution.get("REDUCE_RISK") or 0) == 0 and any(
        str(action.data_health.get("execution_timing_state") or "").upper() == "SUPPORT_FAIL"
        for action in recommendation.actions
    ):
        warnings.append("sell_side_missed_support_fail")
    if int(distribution.get("REDUCE_RISK") or 0) == 0 and recommendation.actions:
        warnings.append("reduce_risk_count_zero_in_account_aware_run")
    return warnings
