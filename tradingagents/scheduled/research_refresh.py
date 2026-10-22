"""Publish bounded new research as a complete, verifiable cohort revision.

A revision is neither a quote refresh nor a full-universe research run. Every
unchanged thesis retains its bytes and clocks. Discovery verifies originals on
each read; this receipt never grants order authority or extends a signal.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

from tradingagents.charting.bars import instant

SCHEMA = "tradingagents.research-refresh/v1"
MAX_TARGETS = 2
MAX_LINEAGE = 128


def manifest_path(archive, identity):
    if (not isinstance(identity, str) or identity in {".", ".."}
            or not re.fullmatch(r"[A-Za-z0-9_.-]+", identity)):
        raise ValueError("Invalid research source identity")
    matches = list((Path(archive) / "runs").glob(f"*/{identity}/run.json"))
    if len(matches) != 1:
        raise ValueError("Research source identity is missing or ambiguous")
    return matches[0]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def artifact(run_dir, row, key):
    path = (run_dir / row["artifacts"][key]).resolve()
    if not path.is_relative_to((run_dir / "tickers" / row["ticker"]).resolve()):
        raise ValueError("Research artifact escaped its ticker directory")
    return path


def rows_by_ticker(manifest):
    rows = manifest["tickers"]
    result = {r["ticker"]: r for r in rows if r.get("status") == "success"}
    if not result or len(result) != len(rows):
        raise ValueError("Incomplete or duplicate research cohort")
    return result


def root_baseline(archive, manifest):
    """Follow explicit parent identities; reject a cycle or an unknown root."""
    seen = set()
    for _ in range(MAX_LINEAGE):
        identity = manifest["run_id"]
        if identity in seen:
            raise ValueError("Research lineage cycle")
        seen.add(identity)
        if (manifest.get("settings") or {}).get("run_mode", "full") == "full":
            return manifest
        parent = manifest.get("overlay_source_run_id")
        manifest = json.loads(manifest_path(archive, parent).read_text(encoding="utf-8"))
    raise ValueError("Research lineage is too deep")


def make_plan(archive, source, targets, *, now, reasons):
    rows = rows_by_ticker(source)
    targets = list(targets)
    if not 1 <= len(targets) <= MAX_TARGETS or len(set(targets)) != len(targets) or not set(targets) <= rows.keys():
        raise ValueError("Bounded research targets must belong to the original cohort")
    if instant(now) is None:
        raise ValueError("Aware research request clock required")
    parent_path = manifest_path(archive, source["run_id"])
    original = json.loads(parent_path.read_text(encoding="utf-8"))
    if source != original:
        raise ValueError("Research source differs from its completed archive")
    baseline = root_baseline(archive, source)
    from .runner import _manifest_is_complete_overlay_baseline
    market = str(source["settings"]["market"]).upper()
    if not _manifest_is_complete_overlay_baseline(baseline, market=market,
            requested_tickers=list(rows), required_holding_tickers=list(rows)):
        raise ValueError("Research refresh requires a complete same-market full baseline")
    finished = instant(source.get("finished_at"))
    started = instant(source.get("started_at"))
    if finished is None or started is None or not started <= finished <= now:
        raise ValueError("Research source completion clock is unverified")
    return {"schema": SCHEMA, "market": market, "requested_at": now.isoformat(),
            "baseline_run_id": baseline["run_id"], "parent_run_id": source["run_id"],
            "parent_manifest_sha256": digest(parent_path), "targets": targets,
            "parent_artifacts_sha256": {ticker: {key: digest(artifact(parent_path.parent, row, key))
                for key in ("analysis_json", "execution_contract_json")} for ticker, row in rows.items()},
            "cohort_tickers": sorted(rows), "reasons": list(reasons), "real_orders_enabled": False}


def load_plan_source(archive, plan, *, now):
    parent_path = manifest_path(archive, plan["parent_run_id"])
    source = json.loads(parent_path.read_text(encoding="utf-8"))
    if make_plan(archive, source, plan["targets"], now=instant(plan["requested_at"]),
                 reasons=plan["reasons"]) != plan or not instant(plan["requested_at"]) <= now:
        raise ValueError("Research plan no longer matches its pinned source")
    return source


def revision_receipt(archive, run_dir, manifest, plan):
    source = load_plan_source(archive, plan, now=instant(manifest["finished_at"]))
    if not instant(plan["requested_at"]) <= instant(manifest["started_at"]) <= instant(manifest["finished_at"]):
        raise ValueError("Research revision started before its request")
    parent_dir = manifest_path(archive, source["run_id"]).parent
    previous, current = rows_by_ticker(source), rows_by_ticker(manifest)
    if sorted(current) != plan["cohort_tickers"]:
        raise ValueError("Research revision changed cohort coverage")
    fingerprints = {}
    for ticker, row in current.items():
        proofs = {}
        for key in ("analysis_json", "execution_contract_json"):
            path = artifact(run_dir, row, key)
            proofs[key] = digest(path)
            if ticker not in plan["targets"] and proofs[key] != digest(artifact(parent_dir, previous[ticker], key)):
                raise ValueError("Carried-forward research changed")
        if ticker in plan["targets"]:
            analysis = json.loads(artifact(run_dir, row, "analysis_json").read_text(encoding="utf-8"))
            start, end = instant(analysis.get("started_at")), instant(analysis.get("finished_at"))
            if (analysis.get("ticker") != ticker or analysis.get("status") != "success"
                    or start is None or end is None
                    or not instant(manifest["started_at"]) <= start <= end <= instant(manifest["finished_at"])):
                raise ValueError("New research did not actually complete after its request")
            contract = json.loads(artifact(run_dir, row, "execution_contract_json").read_text(encoding="utf-8"))
            if instant(contract.get("analysis_asof")) != end or contract.get("ticker") != ticker:
                raise ValueError("New contract does not belong to the new research")
        fingerprints[ticker] = proofs
    return {"plan": plan, "source_revision": manifest.get("source_revision"), "artifacts_sha256": fingerprints,
            "completed_targets": list(plan["targets"]),
            "carried_forward_tickers": sorted(set(current) - set(plan["targets"]))}


def verified_revision(archive, manifest, *, market, now):
    try:
        if ((manifest.get("settings") or {}).get("run_mode") != "selective_rerun_only"
                or manifest.get("status") != "success" or str(manifest["settings"]["market"]).upper() != str(market).upper()
                or not instant(manifest["started_at"]) <= instant(manifest["finished_at"]) <= now):
            return False
        receipt = manifest["research_refresh"]
        plan = receipt["plan"]
        if plan["market"] != str(market).upper() or manifest["overlay_source_run_id"] != plan["parent_run_id"]:
            return False
        path = manifest_path(archive, manifest["run_id"])
        if json.loads(path.read_text(encoding="utf-8")) != json.loads(json.dumps(manifest)):
            return False
        run_dir = path.parent
        return revision_receipt(archive, run_dir, manifest, plan) == receipt
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        return False


def prefer_completed_revision(archive, candidate, *, market, tickers, now):
    """Find a completed revision even if a later-started quote won latest-run."""
    from .manifest_discovery import full_manifests_desc
    try:
        baseline_manifest = root_baseline(archive, candidate)
        baseline = baseline_manifest["run_id"]
        current_id = candidate["run_id"]
        current_key = None
        lineage = candidate
        for _ in range(MAX_LINEAGE):
            if "research_refresh" in lineage:
                if not verified_revision(archive, lineage, market=market, now=now):
                    # A derived quote cannot legitimize a damaged research
                    # revision. Rebuild from the original complete baseline.
                    from .runner import _manifest_is_complete_overlay_baseline
                    return baseline_manifest if _manifest_is_complete_overlay_baseline(baseline_manifest,
                        market=market, requested_tickers=tickers, required_holding_tickers=tickers) else None
                current_key = instant(lineage["started_at"])
                break
            if lineage["run_id"] == baseline:
                break
            lineage = json.loads(manifest_path(archive, lineage["overlay_source_run_id"]).read_text(encoding="utf-8"))
        eligible = []
        for revision, _ in full_manifests_desc(archive, modes={"selective_rerun_only"}):
            plan = (revision.get("research_refresh") or {}).get("plan") or {}
            start = instant(revision.get("started_at"))
            if (plan.get("baseline_run_id") == baseline and revision["run_id"] != current_id
                    and (not tickers or set(tickers) <= set(plan.get("cohort_tickers", [])))
                    and start is not None and (current_key is None or start > current_key)
                    and verified_revision(archive, revision, market=market, now=now)):
                eligible.append((start, revision["run_id"], revision))
        return max(eligible, key=lambda r: r[:2])[2] if eligible else candidate
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        return candidate
