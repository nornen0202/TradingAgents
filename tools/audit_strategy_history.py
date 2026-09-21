"""Read-only inventory of archived decisions; outputs stay in a private directory."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def audit(archive: Path, output: Path, chats: Path | None = None):
    output.mkdir(parents=True, exist_ok=True)
    totals = {}
    signals = []
    manifest = []

    def tracked_read(path):
        payload = read(path)
        manifest.append(
            {
                "path": str(path.relative_to(archive)),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
        return payload

    for market in ("kr", "us"):
        runs, theses, executions, bundles, work = [], {}, {}, [], []
        run_dirs = []
        for p in sorted(archive.glob("runs/*/*/run.json")):
            j = read(p)
            if str(j.get("settings", {}).get("market", "")).lower() != market:
                continue
            runs.append(j)
            run_dirs.append(p.parent)
            manifest.append(
                {
                    "path": str(p.relative_to(archive)),
                    "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                }
            )
            bp = p.parent / "decision_bundle_v2.json"
            if bp.exists():
                b = tracked_read(bp)
                for row in b.get("strategy_table", []):
                    bundles.append(row)
            for tp in sorted((p.parent / "tickers").glob("*/daily_thesis.json")):
                t = tracked_read(tp)
                key = (t.get("ticker"), t.get("analysis_asof"))
                # An overlay copies the same thesis: count the original only once.
                if key not in theses:
                    theses[key] = t
                    d = t.get("decision", {})
                    if isinstance(d, str):
                        try:
                            d = json.loads(d)
                        except ValueError:
                            d = {}
                    signals.append(
                        {
                            "market": market,
                            "ticker": t["ticker"],
                            "available_at": t.get("analysis_asof"),
                            "trade_date": t.get("daily_thesis_trade_date"),
                            "entry_action": t.get("entry_action_base"),
                            "stance": t.get("portfolio_stance"),
                            "rating": d.get("rating"),
                            "confidence": t.get("confidence"),
                            "source": str(tp.relative_to(archive)),
                        }
                    )
                ep = tp.parent / "execution_update.json"
                if ep.exists():
                    e = tracked_read(ep)
                    executions[(e.get("ticker"), e.get("execution_asof"))] = e
        for wp in sorted((archive / "work-reports" / market / "events").glob("*.json")):
            j = read(wp)
            work.append(j)
            manifest.append(
                {
                    "path": str(wp.relative_to(archive)),
                    "sha256": hashlib.sha256(wp.read_bytes()).hexdigest(),
                }
            )
        tr = list(theses.values())
        ex = list(executions.values())
        wr = [
            s
            for w in work
            for s in w.get("structured_report", {}).get("strategies", [])
        ]

        def count(rows, field):
            return dict(Counter(str(row.get(field)) for row in rows))

        def nested(rows, parent, field):
            return dict(Counter(str(row.get(parent, {}).get(field)) for row in rows))

        totals[market] = {
            "runs": len(runs),
            "run_start": min((r["started_at"] for r in runs), default=None),
            "run_end": max((r["finished_at"] for r in runs), default=None),
            "unique_theses": len(tr),
            "entry_actions": count(tr, "entry_action_base"),
            "stances": count(tr, "portfolio_stance"),
            "unique_execution_updates": len(ex),
            "execution_actions": count(ex, "decision_now"),
            "execution_states": count(ex, "decision_state"),
            "execution_reasons": dict(
                Counter(c for e in ex for c in e.get("reason_codes", []))
            ),
            "execution_quality": nested(ex, "source", "execution_data_quality"),
            "bundle_rows_including_overlay_repeats": len(bundles),
            "bundle_strategy_counts": count(bundles, "strategy_code"),
            "bundle_execution_ready": nested(bundles, "quality", "execution_ready"),
            "work_reports": len(work),
            "work_source_hashes": len({w.get("source_sha256") for w in work}),
            "work_start": min((w.get("published_at", "") for w in work), default=None),
            "work_end": max((w.get("published_at", "") for w in work), default=None),
            "work_strategy_rows": len(wr),
            "work_stances": nested(wr, "thesis", "stance"),
            "work_readiness": nested(wr, "execution", "readiness"),
            "work_blockers": dict(
                Counter(
                    c for s in wr for c in s.get("execution", {}).get("blockers", [])
                )
            ),
            "work_missing_asof": sum(
                not s.get("execution", {}).get("as_of") for s in wr
            ),
            "work_expired_at_generation": sum(
                bool(s.get("execution", {}).get("valid_until"))
                and datetime.fromisoformat(s["execution"]["valid_until"])
                < datetime.fromisoformat(w["structured_report"]["generated_at"])
                for w in work
                for s in w.get("structured_report", {}).get("strategies", [])
                if w.get("structured_report", {}).get("generated_at")
            ),
        }
        # Account results are observations, not returns caused by report recommendations.
        account_files = [
            run_dir / "portfolio-private" / "account_performance_public.json"
            for run_dir in run_dirs
        ]
        account_files = [p for p in account_files if p.exists()]
        if account_files:
            a = tracked_read(account_files[-1])
            totals[market]["observed_account"] = {
                k: a.get(k)
                for k in (
                    "summary",
                    "chart_data",
                    "reconciliation",
                    "data_quality",
                    "costs",
                )
            }
    if chats:
        totals["chat"] = []
        for p in sorted(chats.glob("full-*.json")):
            j = read(p)
            if not isinstance(j, dict) or "turns" not in j:
                continue  # Ignore separately generated message extracts.
            messages = [
                i for t in j["turns"] for i in t["items"] if i["type"] == "agentMessage"
            ]
            totals["chat"].append(
                {
                    "title": j["thread"]["title"],
                    "id": j["thread"]["id"],
                    "messages": len(messages),
                    "truncated": sum(bool(i.get("truncated")) for i in messages),
                    "pagination_complete": not j["page"]["hasMore"],
                }
            )
    for name, data in [
        ("audit_summary.json", totals),
        ("thesis_signals.json", signals),
        ("source_manifest.json", manifest),
    ]:
        (output / name).write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    return totals


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--chats", type=Path)
    a = p.parse_args()
    result = audit(a.archive, a.output, a.chats)
    print(
        json.dumps(
            {
                m: {k: v for k, v in s.items() if k != "observed_account"}
                if isinstance(s, dict)
                else s
                for m, s in result.items()
            },
            ensure_ascii=True,
            indent=2,
        )
    )
