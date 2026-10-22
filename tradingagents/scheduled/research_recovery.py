"""Recover a completed partial full run into a new, explicitly sourced cohort."""
from copy import deepcopy
from datetime import date, datetime, timedelta
import hashlib
import json
from pathlib import Path
import re
from zoneinfo import ZoneInfo

MAX_RECOVERY_LINEAGE = 16


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


def _research_date(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("Recovery research date is missing or invalid")
    return date.fromisoformat(value)


def _market_date(value, settings):
    zone = {"US": "America/New_York", "KR": "Asia/Seoul"}.get(str(settings.get("market", "")).upper())
    if zone is None:
        raise ValueError("Recovery research market is unverified")
    return _instant(value).astimezone(ZoneInfo(zone)).date()


def _load_one_terminal_source(*, archive_dir: Path, source_run_id: str, now: datetime):
    if not isinstance(source_run_id, str) or not re.fullmatch(r"\d{8}T\d{6}_[A-Za-z0-9_-]+", source_run_id):
        raise ValueError("Invalid recovery source run ID")
    root = archive_dir.resolve()
    source_dir = (root / "runs" / source_run_id[:4] / source_run_id).resolve()
    if not source_dir.is_relative_to(root):
        raise ValueError("Recovery source escapes archive")
    try:
        source = _read(source_dir / "run.json")
        attempt = _read(source_dir / "attempt.json")
    except (OSError, ValueError) as exc:
        raise ValueError("Recovery source manifest or attempt is missing or malformed") from exc
    if not isinstance(source, dict) or source.get("run_id") != source_run_id or source.get("status") not in {"partial_failure", "failed"}:
        raise ValueError("Recovery requires a completed failed or partial full run")
    if (any(not isinstance(source.get(key), dict) for key in ("settings", "active_universe", "summary"))
            or not isinstance(source.get("tickers"), list)
            or any(not isinstance(row, dict) for row in source["tickers"])):
        raise ValueError("Recovery source cohort is malformed")
    if not isinstance(attempt, dict) or attempt.get("status") not in {"FAILED", "PARTIAL_FAILURE"}:
        raise ValueError("Recovery source attempt is still active or unverified")
    if any(key in attempt and attempt[key] != value for key, value in (
            ("run_id", source_run_id), ("run_mode", "full"),
            ("market", (source.get("settings") or {}).get("market")))):
        raise ValueError("Recovery source attempt identity differs from its manifest")
    started, finished = _instant(source.get("started_at")), _instant(source.get("finished_at"))
    now = _instant(now)
    if not started <= finished <= now or now - started > timedelta(hours=24):
        raise ValueError("Recovery source is future-dated, reversed or older than 24 hours")
    if "started_at" in attempt or "finished_at" in attempt:
        if not started == _instant(attempt.get("started_at")) or not finished <= _instant(attempt.get("finished_at")) <= now:
            raise ValueError("Recovery source attempt clocks differ from its completed manifest")
    return source, source_dir


def _artifact_hashes(source_dir, row):
    result = {}
    artifacts = row.get("artifacts")
    if not isinstance(artifacts, dict):
        raise ValueError("Recovery lineage artifacts are missing")
    for key, relative in artifacts.items():
        if relative is None:
            continue
        if not isinstance(relative, str):
            raise ValueError("Recovery lineage artifact path is invalid")
        path = (source_dir / relative).resolve()
        if not path.is_relative_to(source_dir) or not path.is_file():
            raise ValueError("Recovery lineage artifact path is invalid or missing")
        result[key] = hashlib.sha256(path.read_bytes()).hexdigest()
    if not all(key in result for key in ("analysis_json", "final_state_json", "report_markdown", "execution_contract_json")):
        raise ValueError("Recovery lineage required artifacts are missing")
    return result


def _reuse_receipt(source, row, hashes):
    return {"source_run_id": source["run_id"], "source_code_sha": (source.get("github_actions") or {}).get("sha"),
            "analysis_started_at": row.get("started_at"), "analysis_finished_at": row.get("finished_at"),
            "artifact_sha256": hashes}


def _load_recovery_lineage(*, archive_dir, source_run_id, now):
    """Validate immutable parent links without treating copied research as new."""
    chain, seen = [], set()
    while True:
        if not isinstance(source_run_id, str) or source_run_id in seen or len(chain) >= MAX_RECOVERY_LINEAGE:
            raise ValueError("Recovery lineage is cyclic, malformed or too deep")
        seen.add(source_run_id)
        source, directory = _load_one_terminal_source(archive_dir=archive_dir, source_run_id=source_run_id, now=now)
        chain.append((source, directory))
        if "research_recovery" not in source:
            break
        receipt = source["research_recovery"]
        if (not isinstance(receipt, dict) or receipt.get("schema") != "tradingagents.research-recovery/v1"
                or receipt.get("finalization_only") is not False):
            raise ValueError("Recovery lineage receipt is malformed or is not failed-only recovery")
        source_run_id = receipt.get("source_run_id")
    for (child, child_dir), (parent, parent_dir) in zip(chain, chain[1:]):
        receipt = child["research_recovery"]
        if (receipt.get("source_manifest_sha256") != hashlib.sha256((parent_dir / "run.json").read_bytes()).hexdigest()
                or receipt.get("source_status") != parent["status"]
                or not _instant(parent["finished_at"]) <= _instant(child["started_at"])
                or child.get("daily_thesis_trade_date") != parent.get("daily_thesis_trade_date")):
            raise ValueError("Recovery lineage source hash, status or clocks changed")
        # Each hop retains the original selection and research settings. Current
        # holdings may change within that cohort and are checked separately.
        child_active = child.get("active_universe") or {}
        parent_plan = _cohort_plan(parent, parent_dir, settings=child.get("settings") or {},
                                  holding_tickers=_tickers(child_active.get("expected_holding_tickers")),
                                  account_status=child_active.get("account_snapshot_status", "disabled"))
        if receipt.get("source_selection_sha256") != parent_plan["source_selection_sha256"]:
            raise ValueError("Recovery lineage source selection hash changed")
        parent_active = parent.get("active_universe") or {}
        if any(child_active.get(key) != parent_active.get(key) for key in (
                "mode", "active_count", "selected_tickers", "expected_watchlist_tickers")):
            raise ValueError("Recovery lineage frozen selection changed")
        parent_rows = {row["ticker"]: row for row in parent["tickers"]}
        child_rows = child.get("tickers") or []
        if _tickers([row.get("ticker") for row in child_rows]) != list(parent_rows):
            raise ValueError("Recovery lineage ticker cohort changed")
        inherited = [ticker for ticker, row in parent_rows.items() if row.get("status") == "success"]
        retry = [ticker for ticker, row in parent_rows.items() if row.get("status") in {"failed", "skipped"}]
        if (receipt.get("reused_tickers") != inherited or receipt.get("retry_tickers") != retry
                or not isinstance(receipt.get("reused_research"), dict)
                or set(receipt["reused_research"]) != set(inherited)):
            raise ValueError("Recovery lineage reuse membership changed")
        for row in child_rows:
            ticker = row["ticker"]
            if ticker not in inherited:
                if "research_reuse" in row:
                    raise ValueError("Recovery lineage attributes new research to an unrelated source")
                continue
            previous = parent_rows[ticker]
            hashes = _artifact_hashes(parent_dir, previous)
            proof = _reuse_receipt(parent, previous, hashes)
            if (row.get("status") != "success" or row.get("research_reuse") != proof
                    or receipt["reused_research"][ticker] != proof
                    or _artifact_hashes(child_dir, row) != hashes
                    or any(row.get(key) != previous.get(key) for key in (
                        "decision", "analysis_date", "trade_date", "started_at", "finished_at"))
                    or any(row.get(f"source_{key}") != (
                        previous.get(f"source_{key}") if "research_reuse" in previous else previous.get(key))
                        for key in ("llm_usage", "metrics", "duration_seconds"))):
                raise ValueError("Recovery lineage reused research changed")
    return chain


def _load_terminal_source(*, archive_dir: Path, source_run_id: str, now: datetime):
    return _load_recovery_lineage(archive_dir=archive_dir, source_run_id=source_run_id, now=now)[0]


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


def _failed_holding_selection_proof(source_dir, active, rows):
    """Prove selection separately from failed held-position research.

    Fresh portfolio reconciliation can mark selection incomplete when a selected
    holding's analysis failed. Only the intact opening selection and matching
    terminal rows can establish that this is a retryable analysis gap.
    """
    failed = {row.get("ticker") for row in rows if row.get("status") in {"failed", "skipped"}}
    successful = {row.get("ticker") for row in rows if row.get("status") == "success"}
    holdings = set(_tickers(active.get("expected_holding_tickers")))
    missing = set(_tickers(active.get("missing_holding_tickers")))
    if (not missing or missing != holdings - successful or not missing <= failed
            or active.get("missing_watchlist_tickers")
            or active.get("account_snapshot_status") != "loaded"
            or (active.get("fresh_snapshot_drift") or {}).get("status") != "VERIFIED"
            or (active.get("coverage") or {}).get("fresh_snapshot_complete") is not True):
        raise ValueError("Recovery source lacks a proven failed-holding selection contract")
    path = source_dir / "universe_selection.json"
    if not path.resolve().is_relative_to(source_dir) or not path.is_file():
        raise ValueError("Recovery source selection proof is missing or escapes source")
    raw = path.read_bytes()
    selection = json.loads(raw)
    selected = _tickers(selection.get("selected_tickers"))
    required = holdings | set(_tickers(active.get("expected_watchlist_tickers")))
    if (any(selection.get(key) != active.get(key) for key in (
            "mode", "active_count", "selected_tickers", "expected_holding_tickers", "expected_watchlist_tickers"))
            or selected != [row.get("ticker") for row in rows] or not required <= set(selected)
            or len(selected) != selection.get("active_count")
            or (selection.get("coverage") or {}).get("complete") is not True
            or selection.get("missing_holding_tickers") or selection.get("missing_watchlist_tickers")):
        raise ValueError("Recovery source selection proof does not match the terminal cohort")
    return hashlib.sha256(raw).hexdigest()


def load_recovery_source(*, archive_dir: Path, source_run_id: str, settings: dict,
                         now: datetime, holding_tickers: list[str], account_status: str):
    chain = _load_recovery_lineage(archive_dir=archive_dir, source_run_id=source_run_id, now=now)
    plans = [_cohort_plan(source, directory, settings=settings, holding_tickers=holding_tickers,
                          account_status=account_status) for source, directory in chain]
    plan = plans[0]
    owners, fingerprints = {}, {}
    # Oldest to newest: only a newly successful ticker obtains a new owner.
    for ancestor in reversed(plans):
        source, directory = ancestor["source"], ancestor["source_dir"]
        for row in ancestor["successful_rows"]:
            if "research_reuse" not in row:
                owners[row["ticker"]] = {"run_id": source["run_id"], "started_at": source["started_at"],
                                         "finished_at": source["finished_at"]}
        for name in ("run.json", "attempt.json"):
            path = directory / name
            fingerprints[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
        if ancestor["source_selection_sha256"]:
            fingerprints[str(directory / "universe_selection.json")] = ancestor["source_selection_sha256"]
    if any(row["ticker"] not in owners for row in plan["successful_rows"]):
        raise ValueError("Recovery lineage has no original research owner")
    plan.update(research_owners=owners, lineage_file_sha256=fingerprints,
                lineage_archive_dir=archive_dir, lineage_checked_at=now)
    return plan


def _cohort_plan(source, source_dir, *, settings, holding_tickers, account_status):
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
    if active.get("mode") not in {"full_required_coverage", "adaptive_required_coverage"}:
        raise ValueError("Recovery source lacks a complete required-universe selection contract")
    expected = set(_tickers(active.get("expected_holding_tickers"))) | set(_tickers(active.get("expected_watchlist_tickers")))
    rows = source.get("tickers") or []
    tickers = _tickers([row.get("ticker") for row in rows])
    if not tickers or not expected <= set(tickers) or len(tickers) != active.get("active_count"):
        raise ValueError("Recovery source is missing required ticker rows")
    if "selected_tickers" in active and _tickers(active["selected_tickers"]) != tickers:
        raise ValueError("Recovery frozen selection differs from terminal ticker rows")
    source_selection_sha256 = None
    if coverage.get("selection_complete") is not True:
        source_selection_sha256 = _failed_holding_selection_proof(source_dir, active, rows)
        # Derive only the new cohort's selection view. Stored source coverage,
        # analysis failures and original observations remain unchanged.
        active["coverage"]["selection_complete"] = True
        active["missing_holding_tickers"] = []
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
    if _research_date(trade_date) > _market_date(source["started_at"], source_settings):
        raise ValueError("Recovery source daily price reference date is future-dated")
    active["coverage"]["complete"] = True  # selection only; finalizer recomputes analysis completion
    active["expected_holding_tickers"] = list(holding_tickers)
    active["holding_tickers"] = list(holding_tickers)
    active["account_snapshot_status"] = account_status
    active["account_holding_count"] = len(holding_tickers)
    active["coverage"].update(holding_expected_count=len(holding_tickers), holding_selected_count=len(holding_tickers), holding_missing_count=0)
    active["recovery_source_run_id"] = source["run_id"]
    return {"source": source, "source_dir": source_dir, "tickers": tickers,
            "successful_rows": success, "retry_tickers": retry, "active_universe": active,
            "trade_date": trade_date, "source_manifest_sha256": hashlib.sha256((source_dir / "run.json").read_bytes()).hexdigest(),
            "source_selection_sha256": source_selection_sha256}


def copy_recovered_research(plan: dict, *, run_dir: Path):
    """Copy only validated research; never mutate the source or refresh its TTL."""
    source, source_dir = plan["source"], plan["source_dir"]
    protected = {source_dir.resolve(), *(Path(path).parent.resolve() for path in plan.get("lineage_file_sha256", {})
                                        if Path(path).name == "run.json")}
    if any(run_dir.resolve().is_relative_to(directory) for directory in protected):
        raise ValueError("Recovery source changed or destination would overwrite it")
    if plan.get("finalization_only"):
        for relative, expected_hash in plan["source_file_sha256"].items():
            if hashlib.sha256((source_dir / relative).read_bytes()).hexdigest() != expected_hash:
                raise ValueError("Finalization source changed after validation")
    elif hashlib.sha256((source_dir / "run.json").read_bytes()).hexdigest() != plan["source_manifest_sha256"]:
        raise ValueError("Recovery source changed or destination would overwrite it")
    if plan.get("lineage_file_sha256"):
        for path, expected_hash in plan["lineage_file_sha256"].items():
            if not Path(path).is_file() or hashlib.sha256(Path(path).read_bytes()).hexdigest() != expected_hash:
                raise ValueError("Recovery lineage source or selection changed after validation")
        _load_recovery_lineage(archive_dir=plan["lineage_archive_dir"], source_run_id=source["run_id"],
                               now=plan["lineage_checked_at"])
    if (plan.get("source_selection_sha256") and hashlib.sha256((source_dir / "universe_selection.json").read_bytes()).hexdigest()
            != plan["source_selection_sha256"]):
        raise ValueError("Recovery source selection changed after validation")
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
        owner = plan.get("research_owners", {}).get(row["ticker"], source)
        if (analysis.get("started_at") != row.get("started_at") or analysis.get("finished_at") != row.get("finished_at")
                or not (_instant(owner["started_at"]) <= _instant(analysis.get("started_at"))
                        <= _instant(analysis.get("finished_at")) <= _instant(owner["finished_at"]))):
            raise ValueError("Recovered research timestamps fall outside the source run")
        analysis_date = _research_date(analysis.get("analysis_date"))
        if (analysis_date != _market_date(analysis["started_at"], source["settings"])
                or _research_date(plan["trade_date"]) > analysis_date):
            raise ValueError("Recovered research dates differ from their original market day")
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
        receipt = _reuse_receipt(source, row, {key: value[2] for key, value in files.items()})
        item["research_reuse"] = receipt
        for key in ("llm_usage", "metrics", "duration_seconds"):
            item[f"source_{key}"] = row.get(f"source_{key}") if "research_reuse" in row else row.get(key)
        item["metrics"] = {"llm_calls": 0, "llm_fallback_calls": 0, "tool_calls": 0, "tokens_in": 0, "tokens_out": 0}
        item["llm_usage"] = {"available": False, "calls": 0, "input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "by_model": {}, "by_role": {}, "events": []}
        item["duration_seconds"] = 0.0
        item["execution_update"] = None
        summaries.append(item)
        receipts[row["ticker"]] = receipt
    return summaries, {"schema": "tradingagents.research-recovery/v1", "source_run_id": source["run_id"],
                       "source_manifest_sha256": plan.get("source_manifest_sha256"),
                       "source_selection_sha256": plan.get("source_selection_sha256"),
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
