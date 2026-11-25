"""Bind risk actions to #553's hashed original decisions without reading account databases."""
from collections import Counter, defaultdict
from datetime import datetime
import json
from pathlib import Path

from tools.hybrid_audit_inputs import digest
from tradingagents.backtest import _digest
from tradingagents.dataflows.market_policy import aware_datetime
from tradingagents.scheduled.strategy_research_sources import ResearchArchive, _decision
from tradingagents.schemas.decision import RiskAction

EVALUATION = "512d7e49e6ca38999fbfb741a4c4fe9f71f065bb6e5669da91ebc96f3420f005"
MANIFESTS = "0775127fcd063766ad6908675cb571eb942aa3d924368690b468bbe92cb24b92"
NO_OBSERVATION = "NO_OBSERVATION"

# The last eligible candidate files returned by #569's _latest_market_run
# at its historical merge clock, 2026-11-25T12:45:36Z (18-hour TTL).
COHORTS = {
    "KR": ("20261125T152914_local-freshness-kr-overlay",
           "d5145e255b4bd03e7908bdf7f130d4a2f43487791fb51ef228dd0cfeaaab7001",
           "03c385279ed275e0b01bb76799d247a877bcd28621746da98151d594be9cb328",
           "3d3f74b283cebfeec415f1fff687c25f68ad5b2b08e97c45f27363d8789cd181"),
    "US": ("20261125T201205_local-scheduler-us-full",
           "36535587c18770bbdd27a64a7581015b9f8de43adfc3b58f32c85ec406ecf174",
           "881f3ac359857dba7b39e2188390b19ac35c898055a54fa94c0b3f7e4d4d8e69",
           "a68bf2c1f17dceb99004dfb15de247d62aae7a4bd7a2209415f5f9ce3410a828"),
}


def frozen_json(path, checksum):
    raw = Path(path).read_bytes()
    if digest(raw) != checksum:
        raise ValueError(f"Source differs from the pinned receipt: {path.name}")
    return json.loads(raw)


def cohort_coverage(archive, market, symbols):
    run_id, manifest_hash, candidate_hash, bundle_hash = COHORTS[market]
    directory = archive / "runs" / run_id[:4] / run_id
    manifest = frozen_json(directory / "run.json", manifest_hash)
    rows = frozen_json(directory / "portfolio-private/portfolio_candidates.json", candidate_hash)["candidates"]
    bundle = frozen_json(directory / "decision_bundle_v2.json", bundle_hash)
    decisions = [r["structured_decision"] for r in rows]
    return {"run_id": run_id, "run_finished_at": manifest["finished_at"], "candidates": len(rows),
            "overlapping_symbols": len(set(symbols) & {r["canonical_ticker"] for r in rows}),
            "run_sha256": manifest_hash, "candidate_sha256": candidate_hash, "bundle_sha256": bundle_hash,
            "entry_now": dict(Counter(d["entry_action"] for d in decisions)),
            "conditional_entry": dict(Counter(d["conditional_entry_action"] for d in decisions)),
            "original_risk": dict(Counter(d["risk_action"] for d in decisions)),
            "portfolio_risk": dict(Counter(r["risk_action"] for r in rows)),
            "portfolio_now": dict(Counter(r["suggested_action_now"] for r in rows)),
            "portfolio_if_triggered": dict(Counter(r["suggested_action_if_triggered"] for r in rows)),
            "bundle_ready": bundle["quality"]["decision_ready"],
            "conditional_bundle_ready": bundle["quality"]["conditional_strategy_ready"],
            "usage": "cohort coverage only; later than the last performance mark"}


def bind_action(record, manifest, raw, manifest_hash, cutoff):
    when = aware_datetime(record.get("executed_at"))
    if when is None or when > cutoff:
        return None, "unavailable_by_signal"
    if not raw or digest(raw) != manifest_hash:
        return None, "manifest_unverified"
    completed = aware_datetime(manifest.get("finished_at"))
    if completed is None or when > completed or completed > cutoff:
        return None, "unavailable_by_signal"
    for row in manifest["tickers"]:
        if row.get("ticker") != record["ticker"] or aware_datetime(row.get("finished_at")) != when:
            continue
        decision = _decision(row)
        if _digest(decision) != record["original_decision_sha256"]:
            continue
        action = decision.get("risk_action")
        if action not in {member.value for member in RiskAction}:
            return None, "no_explicit_risk_action"
        return {"executed_at": when.isoformat(), "available_at": completed.isoformat(),
                "action": action, "decision_sha256": record["original_decision_sha256"],
                "manifest_sha256": manifest_hash}, "verified"
    return None, "decision_unverified"


def load_observations(frozen_dir, live_archive, market, symbols, signal_days):
    evaluation = frozen_json(frozen_dir / "evaluation.json", EVALUATION)
    receipts = frozen_json(frozen_dir / "archive-inputs.json", MANIFESTS)
    hashes = {r["run_id"]: r["manifest_sha256"] for r in receipts if r["market"] == market}
    archive = ResearchArchive(live_archive, market, datetime.fromisoformat(evaluation["manifest"]["settlement_cutoff"]))
    counts = Counter()
    grouped = defaultdict(list)
    for row in evaluation["records"]:
        if row["market"] != market or row["ticker"] not in symbols:
            continue
        counts["universe_rows"] += 1
        day = row["decision_date"]
        if day not in signal_days:
            continue
        counts["signal_date_rows"] += 1
        manifest, _, raw = archive.run(row["source"])
        bound, status = bind_action(row, manifest, raw, hashes.get(row["source"]),
                                    datetime.fromisoformat(day + "T22:00:00+00:00"))
        counts[status] += 1
        # An available but unreadable newer original cannot certify an older non-veto.
        if status != "unavailable_by_signal":
            grouped[day, row["ticker"]].append((aware_datetime(row["executed_at"]), bound))
    observations = {}
    for (day, ticker), group in grouped.items():
        newest = max(t for t, _ in group)
        latest = [r for t, r in group if t == newest]
        if all(latest) and len({r["action"] for r in latest}) == 1:
            observations.setdefault(day, {})[ticker] = latest[0]
    return observations, dict(counts)
