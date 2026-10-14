"""Recover a completed partial full run into a new, explicitly sourced cohort."""
from copy import deepcopy
from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path
import re


def _read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _instant(value):
    result = datetime.fromisoformat(str(value))
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("Recovery source timestamps must be timezone-aware")
    return result


def _tickers(values):
    if not isinstance(values, list) or not all(isinstance(v, str) and re.fullmatch(r"[A-Z0-9][A-Z0-9.-]*", v) for v in values):
        raise ValueError("Invalid recovery ticker contract")
    if len(values) != len(set(values)):
        raise ValueError("Duplicate recovery ticker")
    return values


def _load_terminal_source(*, archive_dir: Path, source_run_id: str, now: datetime):
    if not re.fullmatch(r"\d{8}T\d{6}_[A-Za-z0-9_-]+", source_run_id):
        raise ValueError("Invalid recovery source run ID")
    root = archive_dir.resolve()
    source_dir = (root / "runs" / source_run_id[:4] / source_run_id).resolve()
    if not source_dir.is_relative_to(root):
        raise ValueError("Recovery source escapes archive")
    source = _read(source_dir / "run.json")
    if source.get("run_id") != source_run_id or source.get("status") not in {"partial_failure", "failed"}:
        raise ValueError("Recovery requires a completed failed or partial full run")
    if source.get("research_recovery"):
        raise ValueError("Retry against the original source, not an already recovered cohort")
    attempt = _read(source_dir / "attempt.json")
    if attempt.get("status") not in {"FAILED", "PARTIAL_FAILURE"}:
        raise ValueError("Recovery source attempt is still active or unverified")
    started, finished = _instant(source["started_at"]), _instant(source["finished_at"])
    if not started <= finished <= now or now - started > timedelta(hours=24):
        raise ValueError("Recovery source is future-dated, reversed or older than 24 hours")
    return source, source_dir


def recovery_preflight_models(*, archive_dir: Path, source_run_id: str, now: datetime,
                              quick_model: str, deep_model: str, output_model: str):
    """Pin only failed-only preflight to the original cohort's model roles.

    The runner still checks every research setting, current holdings and artifact
    integrity before reuse. Ordinary production keeps its configured defaults.
    """
    if not source_run_id:
        return quick_model, deep_model, output_model
    source, _ = _load_terminal_source(archive_dir=archive_dir, source_run_id=source_run_id, now=now)
    settings = source.get("settings") or {}
    if (settings.get("provider") != "codex"
            or settings.get("run_mode") != "full" or settings.get("analysis_mode") != "full"
            or settings.get("codex_fallback_on_app_server_error") is not False):
        raise ValueError("Recovery preflight requires full Codex research without model fallbacks")
    models = [settings.get(f"{role}_model") for role in ("quick", "deep", "output", "writer", "judge")]
    if not all(isinstance(m, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", m) for m in models):
        raise ValueError("Recovery source model roles are missing or invalid")
    if models[3] != models[2] or models[4] != models[1]:
        raise ValueError("Recovery preflight requires paired output/writer and deep/judge models")
    return tuple(models[:3])


def load_recovery_source(*, archive_dir: Path, source_run_id: str, settings: dict,
                         now: datetime, holding_tickers: list[str], account_status: str):
    source, source_dir = _load_terminal_source(archive_dir=archive_dir, source_run_id=source_run_id, now=now)
    source_settings = source.get("settings") or {}
    for key in ("run_mode", "analysis_mode"):
        if settings.get(key) != "full" or source_settings.get(key) != "full":
            raise ValueError("Only full research can be recovered; smoke/overlay is not a full cohort")
    for key in ("market", "ticker_universe_mode", "configured_ticker_count", "provider",
                "quick_model", "deep_model", "output_model", "writer_model", "judge_model",
                "analysts", "output_language", "translation_backend", "translation_model",
                "codex_reasoning_effort", "codex_quick_reasoning_effort", "codex_deep_reasoning_effort",
                "codex_output_reasoning_effort", "codex_writer_reasoning_effort", "codex_judge_reasoning_effort",
                "report_polisher_enabled", "max_debate_rounds", "max_risk_discuss_rounds",
                "codex_max_retries", "codex_fallback_on_app_server_error"):
        if key not in source_settings or settings.get(key) != source_settings[key]:
            raise ValueError(f"Recovery research configuration changed: {key}")
    if source_settings.get("codex_fallback_on_app_server_error") is not False:
        raise ValueError("Recovery cannot reuse a cohort allowing model fallbacks")
    active = deepcopy(source.get("active_universe") or {})
    coverage = active.get("coverage") or {}
    if active.get("mode") not in {"full_required_coverage", "adaptive_required_coverage"} or coverage.get("selection_complete") is not True:
        raise ValueError("Recovery source lacks a complete required-universe selection contract")
    expected = set(_tickers(active.get("expected_holding_tickers"))) | set(_tickers(active.get("expected_watchlist_tickers")))
    rows = source.get("tickers") or []
    tickers = _tickers([row.get("ticker") for row in rows])
    if not tickers or not expected <= set(tickers) or len(tickers) != active.get("active_count"):
        raise ValueError("Recovery source is missing required ticker rows")
    if any(active.get(k) for k in ("missing_holding_tickers", "missing_watchlist_tickers", "missing_analysis_tickers", "unexpected_analysis_tickers", "duplicate_analysis_tickers")):
        raise ValueError("Recovery source contains coverage gaps beyond failed ticker analyses")
    if not set(holding_tickers) <= set(tickers):
        raise ValueError("New account holdings require a new full universe selection")
    if settings["ticker_universe_mode"] != "config_only" and account_status != "loaded":
        raise ValueError("Recovery requires a current loaded account snapshot")
    success = [r for r in rows if r.get("status") == "success"]
    retry = [r["ticker"] for r in rows if r.get("status") in {"failed", "skipped"}]
    summary = source.get("summary") or {}
    if (not retry or len(success) + len(retry) != len(rows)
            or summary.get("total_tickers") != len(rows)
            or summary.get("successful_tickers") != len(success)
            or summary.get("failed_tickers") != len(retry)):
        raise ValueError("Recovery source summary does not match ticker results")
    trade_date = source.get("daily_thesis_trade_date")
    if not isinstance(trade_date, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", trade_date):
        raise ValueError("Recovery source lacks a single daily price reference date")
    active["coverage"]["complete"] = True  # selection only; finalizer recomputes analysis completion
    active["expected_holding_tickers"] = list(holding_tickers)
    active["holding_tickers"] = list(holding_tickers)
    active["account_snapshot_status"] = account_status
    active["account_holding_count"] = len(holding_tickers)
    active["coverage"].update(holding_expected_count=len(holding_tickers), holding_selected_count=len(holding_tickers), holding_missing_count=0)
    active["recovery_source_run_id"] = source_run_id
    return {"source": source, "source_dir": source_dir, "tickers": tickers,
            "successful_rows": success, "retry_tickers": retry, "active_universe": active,
            "trade_date": trade_date, "source_manifest_sha256": hashlib.sha256((source_dir / "run.json").read_bytes()).hexdigest()}


def copy_recovered_research(plan: dict, *, run_dir: Path):
    """Copy only validated research; never mutate the source or refresh its TTL."""
    source, source_dir = plan["source"], plan["source_dir"]
    if run_dir.resolve() == source_dir:
        raise ValueError("Recovery source changed or destination would overwrite it")
    if plan.get("finalization_only"):
        for relative, expected_hash in plan["source_file_sha256"].items():
            if hashlib.sha256((source_dir / relative).read_bytes()).hexdigest() != expected_hash:
                raise ValueError("Finalization source changed after validation")
    elif hashlib.sha256((source_dir / "run.json").read_bytes()).hexdigest() != plan["source_manifest_sha256"]:
        raise ValueError("Recovery source changed or destination would overwrite it")
    prepared = []
    for row in plan["successful_rows"]:
        artifacts = row.get("artifacts") or {}
        if not all(artifacts.get(k) for k in ("analysis_json", "final_state_json", "report_markdown", "execution_contract_json")):
            raise ValueError(f"Recovery research artifacts missing: {row['ticker']}")
        files = {}
        for key, relative in artifacts.items():
            if relative is None:
                continue
            path = (source_dir / relative).resolve()
            target = (run_dir / relative).resolve()
            if not path.is_relative_to(source_dir) or not target.is_relative_to(run_dir.resolve()) or not path.is_file():
                raise ValueError("Recovery artifact path is invalid or missing")
            data = path.read_bytes()
            files[key] = (relative, data, hashlib.sha256(data).hexdigest())
        analysis = json.loads(files["analysis_json"][1])
        state = json.loads(files["final_state_json"][1])
        decision = analysis.get("decision")
        final_decision = state.get("final_trade_decision")
        decision = json.loads(decision) if isinstance(decision, str) else decision
        final_decision = json.loads(final_decision) if isinstance(final_decision, str) else final_decision
        if (analysis.get("status") != "success" or analysis.get("ticker") != row["ticker"]
                or analysis.get("decision") != row.get("decision")
                or not isinstance(decision, dict) or decision != final_decision
                or state.get("company_of_interest") != row["ticker"]
                or analysis.get("trade_date") != plan["trade_date"]
                or analysis.get("analysis_date") != row.get("analysis_date")
                or analysis.get("metrics", {}).get("llm_fallback_calls") != 0
                or "decision_unvalidated" in analysis.get("quality_flags", [])):
            raise ValueError(f"Recovery research integrity failed: {row['ticker']}")
        if not (_instant(source["started_at"]) <= _instant(analysis["started_at"])
                <= _instant(analysis["finished_at"]) <= _instant(source["finished_at"])):
            raise ValueError("Recovered research timestamps fall outside the source run")
        for field in ("market_report", "news_report", "sentiment_report", "fundamentals_report"):
            report = state.get(field)
            if not isinstance(report, str) or not report.strip() or "TRADINGAGENTS_CODEX_FALLBACK_RESPONSE" in report:
                raise ValueError(f"Recovery required report is incomplete: {row['ticker']} {field}")
        contract = json.loads(files["execution_contract_json"][1])
        if contract.get("ticker") != row["ticker"]:
            raise ValueError("Recovery execution contract ticker mismatch")
        prepared.append((row, files))
    # Validate the whole cohort before writing any recovered ticker files.
    summaries, receipts = [], {}
    for row, files in prepared:
        for relative, data, _hash in files.values():
            target = run_dir / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        item = deepcopy(row)
        receipt = {"source_run_id": source["run_id"], "source_code_sha": (source.get("github_actions") or {}).get("sha"),
                   "analysis_started_at": row.get("started_at"), "analysis_finished_at": row.get("finished_at"),
                   "artifact_sha256": {key: value[2] for key, value in files.items()}}
        item["research_reuse"] = receipt
        item["source_llm_usage"] = item.get("llm_usage")
        item["source_metrics"] = item.get("metrics")
        item["source_duration_seconds"] = item.get("duration_seconds")
        item["metrics"] = {"llm_calls": 0, "llm_fallback_calls": 0, "tool_calls": 0, "tokens_in": 0, "tokens_out": 0}
        item["llm_usage"] = {"available": False, "calls": 0, "input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "by_model": {}, "by_role": {}, "events": []}
        item["duration_seconds"] = 0.0
        item["execution_update"] = None
        summaries.append(item)
        receipts[row["ticker"]] = receipt
    return summaries, {"schema": "tradingagents.research-recovery/v1", "source_run_id": source["run_id"],
                       "source_manifest_sha256": plan.get("source_manifest_sha256"),
                       "finalization_only": bool(plan.get("finalization_only")),
                       "source_file_sha256": plan.get("source_file_sha256"),
                       "source_config_sha256": plan.get("source_config_sha256"),
                       "source_code_sha": plan.get("source_code_sha"),
                       "source_status": source["status"], "reused_tickers": list(receipts),
                       "retry_tickers": plan["retry_tickers"], "reused_research": receipts,
                       "universe_scope": "Frozen source selection; research settings and configured ticker count matched. This is not a fresh scanner selection.",
                       "usage_scope": "This run's LLM usage excludes reused source calls; original per-ticker artifacts and source_llm_usage preserve them."}


def load_finalization_source(*, archive_dir: Path, source_run_id: str, settings: dict,
                             now: datetime, holding_tickers: list[str], account_status: str,
                             source_config_path: Path):
    """Recover all completed research after postprocessing failed, without
    creating a manifest in the interrupted source or running ticker graphs.

    Legacy runs lack a settings checkpoint. Their operator must supply the
    original immutable Git source configuration, verified against local Git.
    """
    import subprocess
    from .config import load_scheduled_config
    from .runner import _settings_snapshot

    if not re.fullmatch(r"\d{8}T\d{6}_[A-Za-z0-9_-]+", source_run_id):
        raise ValueError("Invalid finalization source run ID")
    source_dir = (archive_dir.resolve() / "runs" / source_run_id[:4] / source_run_id).resolve()
    if not source_dir.is_relative_to(archive_dir.resolve()) or (source_dir / "run.json").exists():
        raise ValueError("Finalization requires an incomplete source without a terminal manifest")
    attempt = _read(source_dir / "attempt.json")
    if (attempt.get("run_id") != source_run_id or attempt.get("status") != "FAILED"
            or attempt.get("run_mode") != "full" or attempt.get("market") != settings.get("market")):
        raise ValueError("Finalization source is active or not a failed full attempt")
    started, finished = _instant(attempt["started_at"]), _instant(attempt["finished_at"])
    if not started <= finished <= now or now - started > timedelta(hours=24):
        raise ValueError("Finalization source timestamps are outside the recovery window")

    config_path = Path(source_config_path).resolve()
    snapshot = config_path.parent.parent
    sha = (snapshot / ".source-ready").read_text(encoding="utf-8-sig").strip()
    if (not re.fullmatch(r"[0-9a-f]{40}", sha) or snapshot.name != sha
            or config_path.parent.name != "config"):
        raise ValueError("Finalization source config must come from a pinned Git snapshot")
    git_path = "config/" + config_path.name
    repository = Path(__file__).resolve().parents[2]
    original = subprocess.check_output(["git", "-C", str(repository), "show", f"{sha}:{git_path}"])
    config_bytes = config_path.read_bytes()
    if original.replace(b"\r\n", b"\n") != config_bytes.replace(b"\r\n", b"\n"):
        raise ValueError("Finalization source configuration changed after Git snapshot")
    source_settings = _settings_snapshot(load_scheduled_config(config_path))
    for key in ("run_mode", "analysis_mode", "market", "ticker_universe_mode", "configured_ticker_count",
                "provider", "quick_model", "deep_model", "output_model", "writer_model", "judge_model",
                "analysts", "output_language", "translation_backend", "translation_model",
                "codex_reasoning_effort", "codex_quick_reasoning_effort", "codex_deep_reasoning_effort",
                "codex_output_reasoning_effort", "codex_writer_reasoning_effort", "codex_judge_reasoning_effort",
                "report_polisher_enabled", "max_debate_rounds", "max_risk_discuss_rounds", "codex_max_retries",
                "codex_fallback_on_app_server_error"):
        if settings.get(key) != source_settings.get(key):
            raise ValueError(f"Finalization research configuration changed: {key}")
    if (source_settings.get("provider") != "codex" or source_settings.get("run_mode") != "full"
            or source_settings.get("analysis_mode") != "full"
            or source_settings.get("codex_fallback_on_app_server_error") is not False):
        raise ValueError("Finalization requires full Codex research without fallbacks")

    active = _read(source_dir / "universe_selection.json")
    tickers = _tickers(active.get("selected_tickers"))
    required = set(_tickers(active.get("expected_holding_tickers"))) | set(_tickers(active.get("expected_watchlist_tickers")))
    if (active.get("mode") not in {"full_required_coverage", "adaptive_required_coverage"}
            or (active.get("coverage") or {}).get("complete") is not True
            or active.get("active_count") != len(tickers) or not tickers or not required <= set(tickers)
            or not set(holding_tickers) <= set(tickers)):
        raise ValueError("Finalization requires complete frozen selection and current holdings coverage")
    if settings["ticker_universe_mode"] != "config_only" and account_status != "loaded":
        raise ValueError("Finalization requires a current loaded account snapshot")
    rows, hashes = [], {}
    for relative in ("attempt.json", "universe_selection.json"):
        hashes[relative] = hashlib.sha256((source_dir / relative).read_bytes()).hexdigest()
    summary_paths = sorted((source_dir / "worker-summaries").glob("*.json"))
    if len(summary_paths) != len(tickers):
        raise ValueError("Finalization worker summary coverage is incomplete")
    for path in summary_paths:
        row = _read(path)
        if row.get("status") != "success" or row.get("ticker") not in tickers:
            raise ValueError("Finalization cannot retry failed or unknown ticker research")
        hashes[path.relative_to(source_dir).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
        for relative in (row.get("artifacts") or {}).values():
            if relative is None:
                continue
            artifact = (source_dir / relative).resolve()
            if not artifact.is_relative_to(source_dir) or not artifact.is_file():
                raise ValueError("Finalization research artifact is missing or escapes source")
            hashes[relative] = hashlib.sha256(artifact.read_bytes()).hexdigest()
        analysis_path = (row.get("artifacts") or {}).get("analysis_json")
        analysis = _read(source_dir / analysis_path) if analysis_path else {}
        if (analysis.get("provider") != "codex" or any(
                (analysis.get("models") or {}).get(f"{role}_model") != source_settings.get(f"{role}_model")
                for role in ("quick", "deep", "output"))):
            raise ValueError("Finalization ticker model provenance differs from source config")
        rows.append(row)
    if set(_tickers([row.get("ticker") for row in rows])) != set(tickers):
        raise ValueError("Finalization has duplicate or missing completed tickers")
    dates = {row.get("trade_date") for row in rows}
    if len(dates) != 1 or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(next(iter(dates)))):
        raise ValueError("Finalization requires a single original research price date")
    active = deepcopy(active)
    active["coverage"]["selection_complete"] = True
    active["expected_holding_tickers"] = list(holding_tickers)
    active["account_snapshot_status"] = account_status
    active["recovery_source_run_id"] = source_run_id
    source = {"run_id": source_run_id, "status": "interrupted_postprocessing",
              "started_at": started.isoformat(), "finished_at": finished.isoformat(), "settings": source_settings,
              "github_actions": {"sha": sha}, "tickers": rows, "active_universe": active}
    return {"source": source, "source_dir": source_dir, "tickers": tickers, "successful_rows": rows,
            "retry_tickers": [], "active_universe": active, "trade_date": next(iter(dates)),
            "finalization_only": True, "source_file_sha256": hashes,
            "source_config_sha256": hashlib.sha256(config_bytes).hexdigest(), "source_code_sha": sha}
