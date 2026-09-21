"""Forward event study, NOT a portfolio backtest or proof of condition fills."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, time, timezone
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd


def publication_key(row):
    value = row.get("available_at")
    if not value:
        return datetime.min.replace(tzinfo=timezone.utc)
    at = datetime.fromisoformat(value)
    if at.tzinfo is None:
        raise ValueError("Publication timestamps must be timezone aware")
    return at.astimezone(timezone.utc)


def next_open_index(dates, available_at, market):
    tz = ZoneInfo("Asia/Seoul" if market == "kr" else "America/New_York")
    at = datetime.fromisoformat(available_at)
    if at.tzinfo is None:
        raise ValueError("Publication timestamps must be timezone aware")
    opening = time(9, 0) if market == "kr" else time(9, 30)
    return next(
        (
            i
            for i, day in enumerate(dates)
            if datetime.combine(day.date(), opening, tzinfo=tz) > at
        ),
        None,
    )


def run(archive, directory):
    raw = pd.read_pickle(directory / "signal_prices.pkl")
    etf = pd.read_pickle(directory / "etf_prices.pkl")
    rows = json.loads((directory / "thesis_signals.json").read_text(encoding="utf-8"))
    manifest_path = directory / "source_manifest.json"
    approved_work = None
    if manifest_path.exists():
        approved_work = {
            Path(r["path"]).as_posix()
            for r in json.loads(manifest_path.read_text(encoding="utf-8"))
            if Path(r["path"]).parts[0] == "work-reports"
        }
    for r in rows:
        r["source_kind"] = "project_thesis"
        r["group"] = r["stance"]
    for p in archive.glob("work-reports/*/events/*.json"):
        if (
            approved_work is not None
            and p.relative_to(archive).as_posix() not in approved_work
        ):
            continue
        w = json.loads(p.read_text(encoding="utf-8"))
        if w.get("surface") not in ("kr", "us"):
            continue
        for s in w["structured_report"].get("strategies", []):
            rows.append(
                {
                    "source_kind": "work",
                    "market": w["surface"],
                    "ticker": s["ticker"],
                    "available_at": w["published_at"],
                    "group": s.get("thesis", {}).get("stance", "UNKNOWN"),
                    "readiness": s.get("execution", {}).get("readiness"),
                    "source": str(p.relative_to(archive)),
                }
            )
    dedup, observations, exclusions = set(), [], Counter()
    for r in sorted(rows, key=publication_key):
        if not r.get("available_at"):
            exclusions["missing_publication_time"] += 1
            continue
        market = r["market"]
        tz = ZoneInfo("Asia/Seoul" if market == "kr" else "America/New_York")
        day = (
            datetime.fromisoformat(r["available_at"]).astimezone(tz).date().isoformat()
        )
        # First published ticker/day only, across all groups; prevents hindsight selection.
        key = (r["source_kind"], market, r["ticker"], day)
        if key in dedup:
            exclusions["same_ticker_local_day_repeat"] += 1
            continue
        dedup.add(key)
        symbol = r["ticker"]
        if symbol not in raw["Open"].columns:
            exclusions["missing_symbol"] += 1
            continue
        px = raw.xs(symbol, axis=1, level=1)[["Open", "Close"]].dropna()
        if px.empty:
            exclusions["unavailable_price_history"] += 1
            continue
        i = next_open_index(px.index, r["available_at"], market)
        if i is None:
            exclusions["no_future_open"] += 1
            continue
        benchmark = "069500.KS" if market == "kr" else "SPY"
        for horizon in [1, 5, 10]:
            end = i + horizon - 1
            if end >= len(px):
                exclusions[f"immature_{horizon}d"] += 1
                continue
            entry, exit_ = px.index[i], px.index[end]
            bo = etf["Open"][benchmark].get(entry)
            bc = etf["Close"][benchmark].get(exit_)
            if pd.isna(bo) or pd.isna(bc):
                exclusions["benchmark_missing"] += 1
                continue
            gross = px.iloc[end].Close / px.iloc[i].Open - 1
            net = px.iloc[end].Close * (1 - 0.001) / (px.iloc[i].Open * (1 + 0.001)) - 1
            br = bc * (1 - 0.001) / (bo * (1 + 0.001)) - 1
            observations.append(
                {
                    **r,
                    "local_signal_date": day,
                    "horizon": horizon,
                    "entry": str(entry.date()),
                    "exit": str(exit_.date()),
                    "gross_pct": gross * 100,
                    "net_pct": net * 100,
                    "benchmark_net_pct": br * 100,
                    "excess_pct": (net - br) * 100,
                }
            )
    df = pd.DataFrame(observations)
    summaries = []
    for keys, g in df.groupby(["source_kind", "market", "group", "horizon"]):
        # Cluster by signal date to reduce within-date pseudo-replication.
        means = g.groupby("local_signal_date").excess_pct.mean().to_numpy()
        rng = np.random.default_rng(73219)
        ci = (
            np.quantile(
                np.mean(rng.choice(means, (2000, len(means))), axis=1), [0.025, 0.975]
            )
            if len(means) >= 5
            else [None, None]
        )
        summaries.append(
            dict(zip(["source_kind", "market", "group", "horizon"], keys))
            | {
                "n": len(g),
                "signal_dates": len(means),
                "tickers": g.ticker.nunique(),
                "mean_net_pct": g.net_pct.mean(),
                "median_net_pct": g.net_pct.median(),
                "positive_pct": (g.net_pct > 0).mean() * 100,
                "mean_excess_pct": g.excess_pct.mean(),
                "equal_date_mean_excess_pct": means.mean(),
                "date_cluster_ci_low": ci[0],
                "date_cluster_ci_high": ci[1],
            }
        )
    result = {
        "notes": [
            "First report per ticker/local day; first market opening strictly after publication",
            "Unconditional next-open exposure counterfactual, not fulfillment of original conditions",
            "Round-trip 10bps each side assumed; no tax/FX; adjusted total-return prices",
            "Events overlap; date-cluster bootstrap does not remove serial dependence",
            "Do not compound overlapping event returns into a portfolio return",
        ],
        "exclusions": dict(exclusions),
        "rows": len(df),
        "price_sha256": hashlib.sha256(
            (directory / "signal_prices.pkl").read_bytes()
        ).hexdigest(),
        "summaries": summaries,
    }
    (directory / "event_study.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    df.to_csv(directory / "event_observations.csv", index=False)
    print(pd.DataFrame(summaries).query("horizon == 5").to_string(index=False))
    print(dict(exclusions))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive", type=Path, required=True)
    p.add_argument("--directory", type=Path, required=True)
    a = p.parse_args()
    run(a.archive, a.directory)
