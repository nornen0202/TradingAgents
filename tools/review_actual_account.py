"""Review latest completed local KIS account snapshots, with no API calls."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from tradingagents.portfolio.account_review import (
    review_market_views,
    render_account_review,
)


def select_latest(root: Path, *, now: datetime) -> dict[str, Path]:
    selected = {}
    for path in root.glob("**/portfolio-private/account_snapshot.json"):
        try:
            snapshot = json.loads(path.read_text(encoding="utf-8"))
            manifest = json.loads(
                (path.parent.parent / "run.json").read_text(encoding="utf-8")
            )
            status = json.loads(
                (path.parent / "status.json").read_text(encoding="utf-8")
            )
            as_of = datetime.fromisoformat(snapshot["as_of"].replace("Z", "+00:00"))
            if (
                as_of.tzinfo is None
                or as_of > now
                or manifest.get("status") != "success"
                or status.get("status") != "success"
            ):
                continue
            if (
                snapshot.get("snapshot_health") != "VALID"
                or snapshot.get("broker") != "kis"
            ):
                continue
            symbols = [p["canonical_ticker"] for p in snapshot.get("positions", [])]
            declared = str((manifest.get("settings") or {}).get("market") or "").upper()
            # A completed all-cash snapshot must supersede older holdings.
            # Prefer explicit run scope; never infer an empty view's market.
            if declared in {"KR", "US"}:
                market = declared
            elif symbols and all(s.endswith((".KS", ".KQ")) for s in symbols):
                market = "KR"
            elif symbols and all(
                "." not in s or s.endswith((".A", ".B")) for s in symbols
            ):
                market = "US"
            else:
                continue
            if market not in selected or as_of > selected[market][0]:
                selected[market] = (as_of, path)
        except (ValueError, OSError, KeyError, TypeError):
            continue
    return {market: value[1] for market, value in sorted(selected.items())}


def run(root: Path, output: Path, *, now: datetime | None = None):
    now = now or datetime.now(timezone.utc)
    paths = select_latest(root, now=now)
    if not paths:
        raise ValueError("No completed, valid, timestamped KIS snapshots found")
    snapshots = {
        market: json.loads(path.read_text(encoding="utf-8"))
        for market, path in paths.items()
    }
    report = review_market_views(snapshots, now=now)
    report["sources"] = {
        market: {
            "path": str(path),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        for market, path in paths.items()
    }
    report["missing_market_views"] = sorted({"KR", "US"} - set(paths))
    output.mkdir(parents=True, exist_ok=True)
    (output / "account-review.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    (output / "실계좌 보유 현금 검토.md").write_text(
        render_account_review(report), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "output": str(output),
                "market_views": list(paths),
                "orders_submitted": 0,
                "api_calls": 0,
            }
        )
    )
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    run(args.archive_root, args.output)
