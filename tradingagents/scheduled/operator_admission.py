"""Certify fresh operator research after terminal pre-worker identity failures.

The sidecar binds existing bytes; it never changes research clocks, manifests,
attempt counters or execution eligibility. Ordinary manual/test runs stay excluded.
"""

from datetime import datetime, timezone
import hashlib
from pathlib import Path
import re

from tradingagents.atomic_io import atomic_write_json, interprocess_file_lock
from .research_recovery import (
    _artifact_hashes,
    _instant,
    _load_one_terminal_source,
    _market_date,
    _read,
    _research_date,
    _tickers,
)

CERTIFICATE = "operator-production-admission.json"
SCHEMA = "tradingagents.operator-production-admission/v1"


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _evidence(archive, manifest, original, repair, *, now):
    run_id = manifest["run_id"]
    canonical, directory = _load_one_terminal_source(
        archive_dir=archive, source_run_id=run_id, now=now, completed_head=True
    )
    if canonical != {k: v for k, v in manifest.items() if not k.startswith("_")}:
        raise ValueError("Noncanonical operator manifest")
    market = canonical["settings"]["market"].lower()
    if (
        market not in {"us", "kr"}
        or canonical.get("label") != f"manual-{market}-identity-recovery"
        or "research_recovery" in canonical
    ):
        raise ValueError("Not a fresh operator identity repair")
    settings = canonical["settings"]
    models = [
        settings.get(f"{role}_model")
        for role in ("quick", "deep", "output", "writer", "judge")
    ]
    if (
        settings.get("provider") != "codex"
        or settings.get("run_mode") != "full"
        or settings.get("analysis_mode") != "full"
        or settings.get("codex_fallback_on_app_server_error") is not False
        or not all(
            isinstance(m, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", m)
            for m in models
        )
        or models[3] != models[2]
        or models[4] != models[1]
    ):
        raise ValueError("Unverified full research model roles")
    revision = canonical.get("source_revision")
    if (
        not isinstance(revision, str)
        or not re.fullmatch(r"[a-f0-9]{40}", revision)
        or repair.get("source_revision") != revision
    ):
        raise ValueError("Operator research source revision changed")
    counts = [
        original.get("attempts"),
        repair.get("attempts"),
        repair.get("original_attempts"),
    ]
    if (
        any(type(n) is not int or n < 1 for n in counts)
        or counts[0] != counts[2]
        or counts[0] + counts[1] > 4
        or type(repair.get("cumulative_limit")) is not int
        or repair["cumulative_limit"] != 4
        or original.get("target") != f"daily-codex-{market}"
        or type(original.get("exit_code")) is not int
        or original["exit_code"] == 0
        or repair.get("schema") != "tradingagents.manual-research-repair/v1"
        or repair.get("mode") != "fresh_research_after_preworker_identity_failure"
        or repair.get("status") != "COMPLETED"
        or type(repair.get("exit_code")) is not int
        or repair["exit_code"] != 0
        or type(repair.get("orders_sent")) is not int
        or repair["orders_sent"] != 0
        or type(repair.get("reused_ticker_count")) is not int
        or repair["reused_ticker_count"] != 0
        or not re.fullmatch(r"[a-f0-9]{64}", str(repair.get("original_target_key", "")))
    ):
        raise ValueError("Unverified original attempt budget or terminal repair")
    attempt = _read(directory / "attempt.json")
    started, finished = (
        _instant(canonical["started_at"]),
        _instant(canonical["finished_at"]),
    )
    if not (
        _instant(original["started_at"])
        <= _instant(original["finished_at"])
        <= _instant(repair["started_at"])
        <= started
        <= finished
        <= _instant(attempt["finished_at"])
        <= _instant(repair["finished_at"])
        <= _instant(now)
    ):
        raise ValueError("Unverified operator repair chronology")
    sources = repair.get("source_attempt_sha256")
    if (
        not isinstance(sources, dict)
        or len(sources) != counts[0]
        or repair.get("source_run_id") not in sources
    ):
        raise ValueError("Original failures are not fully accounted for")
    source_finishes = {}
    for source_id, expected in sources.items():
        if not re.fullmatch(
            rf"\d{{8}}T\d{{6}}_local-scheduler-{market}-full", str(source_id)
        ):
            raise ValueError("Invalid original production failure identity")
        source_dir = (archive / "runs" / source_id[:4] / source_id).resolve()
        if not source_dir.is_relative_to(archive.resolve()):
            raise ValueError("Original failure escapes archive")
        failed = _read(source_dir / "attempt.json")
        if (
            failed.get("run_id") != source_id
            or failed.get("status") != "FAILED"
            or failed.get("error_type") != "KeyError"
            or failed.get("market", "").lower() != market
            or failed.get("run_mode") != "full"
            or (
                failed.get("completed_tickers") is not None
                and (
                    type(failed["completed_tickers"]) is not int
                    or failed["completed_tickers"] != 0
                )
            )
            or (source_dir / "run.json").exists()
            or any((source_dir / "worker-summaries").glob("*.json"))
            or any((source_dir / "tickers").rglob("analysis.json"))
            or _sha(source_dir / "attempt.json") != expected
            or not _instant(failed["started_at"])
            <= _instant(failed["finished_at"])
            <= _instant(original["finished_at"])
        ):
            raise ValueError(
                "Original failure has workers, changed bytes or invalid clocks"
            )
        source_finishes[source_id] = _instant(failed["finished_at"])
    if source_finishes[repair["source_run_id"]] != max(source_finishes.values()):
        raise ValueError("Repair is not bound to the latest original failure")
    rows, summary = canonical["tickers"], canonical["summary"]
    tickers = _tickers([row.get("ticker") for row in rows])
    active = canonical["active_universe"]
    if (
        not rows
        or any(
            type(summary.get(k)) is not int
            for k in ("total_tickers", "successful_tickers", "failed_tickers")
        )
        or type(active.get("active_count")) is not int
        or type(summary.get("configured_ticker_count", len(rows))) is not int
        or summary.get("total_tickers") != len(rows)
        or summary.get("successful_tickers") != len(rows)
        or summary.get("failed_tickers") != 0
        or summary.get("configured_ticker_count", len(rows)) > len(rows)
        or (active.get("coverage") or {}).get("complete") is not True
        or active.get("active_count") != len(rows)
        or set(_tickers(active.get("selected_tickers"))) != set(tickers)
    ):
        raise ValueError("Operator cohort is incomplete")
    hashes = {}
    for row in rows:
        hashes[row["ticker"]] = _artifact_hashes(directory, row)
        analysis = _read(directory / row["artifacts"]["analysis_json"])
        if (
            row.get("status") != "success"
            or "research_reuse" in row
            or analysis.get("ticker") != row["ticker"]
            or analysis.get("status") != "success"
            or any(
                analysis.get(k) != row.get(k)
                for k in ("started_at", "finished_at", "analysis_date", "trade_date")
            )
            or not started
            <= _instant(row["started_at"])
            <= _instant(row["finished_at"])
            <= finished
            or _research_date(row["analysis_date"])
            > _market_date(row["started_at"], settings)
            or _research_date(row["trade_date"])
            > _market_date(row["started_at"], settings)
        ):
            raise ValueError("Operator research identity or clocks are invalid")
    return {
        "run_id": run_id,
        "source_revision": revision,
        "manifest_sha256": _sha(directory / "run.json"),
        "attempt_sha256": _sha(directory / "attempt.json"),
        "artifact_sha256": hashes,
        "source_attempt_sha256": sources,
        "original_target_key": repair["original_target_key"],
        "cumulative_attempts": counts[0] + counts[1],
        "cumulative_limit": 4,
    }


def verified_operator_research(archive_dir, manifest, *, now):
    """Fail closed without a terminal, byte-bound canonical certificate."""
    try:
        archive = Path(archive_dir)
        run_id = manifest["run_id"]
        if not isinstance(run_id, str) or not re.fullmatch(
            r"\d{8}T\d{6}_[A-Za-z0-9_-]+", run_id
        ):
            return False
        directory = (archive / "runs" / run_id[:4] / run_id).resolve()
        if not directory.is_relative_to(archive.resolve()):
            return False
        certificate = _read(directory / CERTIFICATE)
        certified = _instant(certificate["certified_at"])
        repair = certificate["repair_receipt"]
        if certificate.get("schema") != SCHEMA or not _instant(
            repair["finished_at"]
        ) <= certified <= _instant(now):
            return False
        return certificate["evidence"] == _evidence(
            archive, manifest, certificate["original_receipt"], repair, now=certified
        )
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        return False


def certify_operator_research(*, archive_dir, state_dir, run_id, target_key, now=None):
    """Explicit operator action; read trusted scheduler receipts without mutation."""
    archive, state = Path(archive_dir), Path(state_dir)
    if not re.fullmatch(r"[a-f0-9]{64}", str(target_key)):
        raise ValueError("Invalid original target key")
    if not isinstance(run_id, str) or not re.fullmatch(
        r"\d{8}T\d{6}_[A-Za-z0-9_-]+", run_id
    ):
        raise ValueError("Invalid operator run ID")
    now = datetime.now(timezone.utc) if now is None else now
    directory = (archive / "runs" / run_id[:4] / run_id).resolve()
    if not directory.is_relative_to(archive.resolve()):
        raise ValueError("Operator run escapes archive")
    with interprocess_file_lock(state / "research-kis.lock", timeout=0):
        original = _read(state / "attempts" / f"{target_key}.json")
        repair = _read(state / "finalization-recovery" / f"{target_key}.json")
        # Archive only admission evidence, never arbitrary scheduler metadata,
        # process details, operator prose or credentials added by another writer.
        original = {
            k: original[k]
            for k in ("target", "attempts", "exit_code", "started_at", "finished_at")
            if k in original
        }
        repair = {
            k: repair[k]
            for k in (
                "schema",
                "mode",
                "status",
                "attempts",
                "exit_code",
                "source_revision",
                "original_target_key",
                "original_attempts",
                "cumulative_limit",
                "orders_sent",
                "reused_ticker_count",
                "source_attempt_sha256",
                "source_run_id",
                "started_at",
                "finished_at",
            )
            if k in repair
        }
        if repair.get("original_target_key") != target_key:
            raise ValueError("Original target key changed")
        manifest = _read(directory / "run.json")
        evidence = _evidence(archive, manifest, original, repair, now=now)
        path = directory / CERTIFICATE
        if path.exists():
            existing = _read(path)
            if (
                not verified_operator_research(archive, manifest, now=now)
                or existing.get("evidence") != evidence
                or existing.get("original_receipt") != original
                or existing.get("repair_receipt") != repair
            ):
                raise ValueError(
                    "Existing operator certificate is invalid; never overwrite it"
                )
            return existing
        certificate = {
            "schema": SCHEMA,
            "certified_at": _instant(now).isoformat(),
            "original_receipt": original,
            "repair_receipt": repair,
            "evidence": evidence,
        }
        atomic_write_json(path, certificate)
        return certificate
