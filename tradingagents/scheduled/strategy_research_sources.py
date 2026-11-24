"""Resolve report research by immutable ticker lineage, independently of order bundles."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date, timedelta
from pathlib import Path

from tradingagents.dataflows.market_policy import aware_datetime
from tradingagents.work.packet import canonical_json, sha256_text

_RUN_ID = re.compile(r"\d{8}T\d{6}_[A-Za-z0-9_-]+")


def _read(path, limit=24 * 1024 * 1024):
    try:
        with path.open("rb") as stream:
            raw = stream.read(limit + 1)
        if len(raw) > limit:
            return {}, b""
        data = json.loads(raw)
        return (data, raw) if isinstance(data, dict) else ({}, b"")
    except (OSError, ValueError):
        return {}, b""


def _artifact(directory, row, key):
    relative = (row.get("artifacts") or {}).get(key)
    if not isinstance(relative, str):
        return {}, b""
    path = (directory / relative).resolve()
    return _read(path) if path.is_relative_to(directory.resolve()) else ({}, b"")


def _decision(row):
    data = row.get("decision")
    try:
        return data if isinstance(data, dict) else json.loads(data) if isinstance(data, str) else {}
    except ValueError:
        return {}


def _identity(ticker):
    from tradingagents.dataflows.intraday.us_symbols import canonical_symbol
    return canonical_symbol(ticker)


class ResearchArchive:
    def __init__(self, archive, market, now):
        self.root = (Path(archive) / "runs").resolve()
        self.market = market
        self.now = now
        self.runs = {}

    def run(self, run_id):
        if not isinstance(run_id, str) or not _RUN_ID.fullmatch(run_id):
            return {}, self.root, b""
        if run_id not in self.runs:
            directory = (self.root / run_id[:4] / run_id).resolve()
            if not (directory / "run.json").is_file():
                directory = (self.root / run_id).resolve()
            manifest, raw = _read(directory / "run.json") if directory.is_relative_to(self.root) else ({}, b"")
            settings = manifest.get("settings") or {}
            start = aware_datetime(manifest.get("started_at"))
            end = aware_datetime(manifest.get("finished_at"))
            if (manifest.get("run_id") != run_id or str(settings.get("market", "")).upper() != self.market
                    or start is None or end is None or not start <= end <= self.now):
                manifest, raw = {}, b""
            self.runs[run_id] = manifest, directory, raw
        return self.runs[run_id]

    def candidates(self):
        market = self.market.lower()
        labels = (f"local-scheduler-{market}-full", f"github-actions-{market}")
        cutoff = (self.now.date() - timedelta(days=45)).strftime("%Y%m%d")
        for year in {self.now.year, (self.now.date() - timedelta(days=46)).year}:
            for label in labels:
                for folder in (self.root, self.root / str(year)):
                    for path in folder.glob(f"{year}*_{label}"):
                        if path.name[:8] >= cutoff:
                            yield path.name
        # Older layouts can name a scheduled full run differently. A dated
        # thesis already carried by its packet remains available for those runs.

    def origin(self, run_id, row, seen=frozenset()):
        if run_id in seen or len(seen) >= 16 or not isinstance(row, dict) or row.get("status") != "success":
            return None
        manifest, directory, _ = self.run(run_id)
        if ((manifest.get("settings") or {}).get("run_mode", "full") != "full"
                or manifest.get("status") not in {"success", "partial_failure", "partial", "degraded"}):
            return None
        decision = _decision(row)
        if not isinstance(decision, dict) or decision.get("rating") not in {
            "BUY", "OVERWEIGHT", "HOLD", "UNDERWEIGHT", "REDUCE", "SELL", "NO_TRADE", "AVOID", "RESEARCH",
        }:
            return None
        ticker = row.get("ticker")
        start, end = (aware_datetime(row.get(key)) for key in ("started_at", "finished_at"))
        if start is None or end is None or not start <= end <= self.now:
            return None
        try:
            day = date.fromisoformat(row["trade_date"])
        except (KeyError, TypeError, ValueError):
            return None
        if day > end.date() or day > self.now.date():
            return None
        analysis, raw = _artifact(directory, row, "analysis_json")
        if (not analysis or analysis.get("ticker") != ticker or analysis.get("status") != "success"
                or _decision(analysis) != decision or any(analysis.get(field) != row.get(field) for field in
                    ("started_at", "finished_at", "trade_date", "analysis_date"))):
            return None
        if "decision_unvalidated" in row.get("quality_flags", []) or (analysis.get("metrics") or {}).get("llm_fallback_calls"):
            return None
        reuse = row.get("research_reuse")
        if reuse is not None:
            if not isinstance(reuse, dict):
                return None
            receipt = manifest.get("research_recovery") or {}
            parent_id = reuse.get("source_run_id")
            parent, parent_dir, parent_bytes = self.run(parent_id)
            if (not parent or receipt.get("source_run_id") != parent_id
                    or receipt.get("source_manifest_sha256") != hashlib.sha256(parent_bytes).hexdigest()
                    or (receipt.get("reused_research") or {}).get(ticker) != reuse
                    or reuse.get("analysis_started_at") != row.get("started_at")
                    or reuse.get("analysis_finished_at") != row.get("finished_at")
                    or (reuse.get("artifact_sha256") or {}).get("analysis_json") != hashlib.sha256(raw).hexdigest()):
                return None
            matches = [item for item in parent.get("tickers", []) if isinstance(item, dict) and item.get("ticker") == ticker]
            if len(matches) != 1:
                return None
            _, parent_raw = _artifact(parent_dir, matches[0], "analysis_json")
            if raw != parent_raw:
                return None
            return self.origin(parent_id, matches[0], seen | {run_id})
        if not aware_datetime(manifest["started_at"]) <= start <= end <= aware_datetime(manifest["finished_at"]):
            return None
        chart, _ = _artifact(directory, row, "chart_evidence_json")
        return run_id, row, analysis, decision, day, end, chart

    def latest(self, tickers):
        """Use a successful row from a partial attempt when its original bytes verify."""
        wanted = {_identity(ticker) for ticker in tickers}
        selected = {}
        for run_id in sorted(set(self.candidates()), reverse=True):
            manifest, _, _ = self.run(run_id)
            summaries = {}
            for row in manifest.get("tickers", []):
                if not isinstance(row, dict):
                    continue
                identity = _identity(row.get("ticker"))
                if identity in wanted:
                    summaries.setdefault(identity, []).append(row)
            for identity, rows in summaries.items():
                if len(rows) != 1:
                    continue
                origin = self.origin(run_id, rows[0])
                if not origin:
                    continue
                previous = selected.get(identity)
                if previous is None or (origin[4], origin[5]) > (previous[1][4], previous[1][5]):
                    selected[identity] = run_id, origin
            # The event window is bounded. Drop large expanded manifests as we
            # walk it, retaining just projections for the selected instruments.
            self.runs.clear()
        return selected

    def quotes(self, market_payload):
        """Read the archived provider envelope for the exact published price."""
        run_id = market_payload.get("run_id")
        manifest, _, _ = self.run(run_id)
        by_ticker = {_identity(row.get("ticker")): row for row in manifest.get("tickers", []) if isinstance(row, dict)}
        quotes = {}
        for row in market_payload["rows"]:
            ticker = _identity(row.get("ticker"))
            update = by_ticker.get(ticker, {}).get("execution_update") or {}
            if not isinstance(update, dict):
                continue
            raw = update.get("source") or {}
            if not isinstance(raw, dict):
                continue
            if (aware_datetime(update.get("market_data_asof")) == aware_datetime(row.get("market_data_asof"))
                    and update.get("ticker") == by_ticker.get(ticker, {}).get("ticker")
                    and update.get("last_price") == row.get("last_price")):
                quotes[ticker] = {
                    "price": row.get("last_price"), "event_at": update.get("market_data_asof"),
                    "observed_at": update.get("execution_asof"), "source": raw.get("provider"),
                    "exchange": raw.get("exchange"), "market_session": raw.get("market_session"),
                    "currency": raw.get("currency"), "adjustment": raw.get("adjustment"),
                    "category": raw.get("execution_data_quality"),
                    "published_at": raw.get("published_at"), "provider_at": raw.get("provider_timestamp"),
                }
        return quotes


def thesis_for(origin):
    """Project only analysis-time fields. Retain original rating and condition arrays."""
    from tradingagents.work.packet import _source_coverage

    run_id, row, _, decision, day, finished, _ = origin
    rating = decision["rating"]
    stance = {"OVERWEIGHT": "BUY", "UNDERWEIGHT": "REDUCE", "NO_TRADE": "AVOID"}.get(rating, rating)
    thesis = {key: decision.get(key) for key in (
        "portfolio_stance", "entry_action", "conditional_entry_action", "conditional_entry_valid_until",
        "execution_levels", "risk_action", "risk_action_reason", "risk_action_level", "catalysts",
        "risk_limits", "profit_taking_plan", "data_coverage", "confidence", "position_sizing",
    )}
    logic = decision.get("entry_logic")
    return thesis | {
        "rating": rating, "stance": stance, "analysis_run_id": run_id, "analysis_asof": finished.isoformat(),
        "decision_asof": row.get("analysis_date"), "price_reference_date": day.isoformat(),
        "analysis_trade_date": day.isoformat(), "decision_sha256": sha256_text(canonical_json(decision)),
        "source_coverage": _source_coverage(row), "rationale": [logic] if logic else [],
        "entry_conditions": [logic] if logic else [], "observation_conditions": decision.get("watchlist_triggers") or [],
        "invalidation_conditions": decision.get("invalidators") or [], "invalidation_action": decision.get("exit_logic"),
        "horizon": decision.get("time_horizon"),
    }

