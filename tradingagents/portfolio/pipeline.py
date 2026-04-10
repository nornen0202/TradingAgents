from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .action_judge import arbitrate_portfolio_actions
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
) -> dict[str, Any]:
    if not getattr(portfolio_settings, "enabled", False):
        return {"status": "disabled"}

    profile = load_portfolio_profile(portfolio_settings.profile_path, portfolio_settings.profile_name)
    if not profile.enabled:
        return {"status": "disabled", "reason": f"profile {profile.name} is disabled"}

    private_dir = run_dir / profile.private_output_dirname
    status_path = private_dir / "status.json"
    try:
        snapshot = _load_snapshot(profile)
        candidates, candidate_warnings = build_portfolio_candidates(
            snapshot=snapshot,
            run_dir=run_dir,
            manifest=manifest,
            watch_tickers=profile.watch_tickers,
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
        recommendation, scored_candidates = build_recommendation(
            candidates=gated_candidates,
            snapshot=snapshot,
            batch_metrics=manifest.get("batch_metrics") or {},
            warnings=all_warnings,
            profile=profile,
            report_date=str(manifest.get("started_at") or "")[:10],
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
        markdown = render_portfolio_report_markdown(
            snapshot=snapshot,
            recommendation=recommendation,
            candidates=scored_candidates,
        )
        artifact_paths = save_portfolio_outputs(
            private_dir=private_dir,
            snapshot=snapshot,
            candidates=scored_candidates,
            recommendation=recommendation,
            portfolio_report_markdown=markdown,
            semantic_verdicts=semantic_verdicts,
            action_judge_payload=action_judge_payload,
            batch_metrics=manifest.get("batch_metrics") or {},
            warnings=all_warnings,
        )
        status = {
            "status": "success",
            "profile": profile.name,
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


def _load_snapshot(profile) -> Any:
    if profile.broker == "manual":
        if not profile.manual_snapshot_path:
            raise PortfolioConfigurationError("manual broker profile requires manual_snapshot_path.")
        return load_manual_snapshot(profile.manual_snapshot_path)
    if profile.broker == "csv":
        return load_snapshot_from_positions_csv(profile)
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


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
