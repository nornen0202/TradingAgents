"""Summarize the frozen November KR full and US overlay artifacts offline."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path

from tradingagents.execution.session_confirmation import _entry_alternatives, _schedule


def _read(path):
    return json.loads(path.read_bytes())


def _rows(root):
    for path in sorted(root.glob("2026112*_local-scheduler-kr-full/run.json")):
        if path.parent.name[:8] not in {"20261123", "20261124"}:
            continue
        data = path.read_bytes()
        manifest = json.loads(data)
        active = manifest["active_universe"]
        held = set(active["expected_holding_tickers"])
        source = _read(path.with_name("attempt.json"))
        review = next((row for row in active["candidates"] if row["ticker"] == "119850.KS"), {})
        for row in manifest["tickers"]:
            yield {
                "run_id": manifest["run_id"], "manifest_sha256": hashlib.sha256(data).hexdigest(),
                "attempt": source["status"], "ticker": row["ticker"], "held": row["ticker"] in held,
                "status": row["status"], "first_block": (row.get("failure_diagnostics") or {}).get("failure_category"),
                "failure": row.get("error"), "119850_selected": review.get("selected"),
                "119850_selection_reason": review.get("selection_reason"),
            }


def _us_rows(directory):
    manifest = _read(directory / "run.json")
    candidates = _read(directory / "portfolio-private" / "portfolio_candidates.json")["candidates"]
    candidates = {row["canonical_ticker"]: row for row in candidates}
    snapshot = _read(directory / "portfolio-private" / "account_snapshot.json")
    portfolio = _read(directory / "portfolio-private" / "portfolio_report.json")
    final_actions = {row["canonical_ticker"]: row for row in portfolio["actions"]}
    cash_gap = (portfolio.get("funding_plan") or {}).get("cash_gap_to_strict_buffer_krw")
    held = {row["canonical_ticker"] for row in snapshot["positions"]}
    for row in manifest["tickers"]:
        ticker = row["ticker"]
        update = row.get("execution_update") or _read(directory / "tickers" / ticker / "execution_update.json")
        thesis = json.loads(row["decision"])
        candidate = candidates.get(ticker, {})
        levels = [level for level in thesis["execution_levels"]["levels"]
                  if level["level_type"].upper() in {"BREAKOUT", "RESISTANCE", "PULLBACK", "SUPPORT"}]
        grouped = [level for level in levels if level.get("confirmation_group")]
        ungrouped = [level for level in levels if not level.get("confirmation_group")]
        alternatives = _entry_alternatives(grouped, "USD", True)
        original_pilot = any(all(rule["stage"] == "intraday" for rule in group) for group in alternatives)
        intraday_crossed = any(all(
            rule["stage"] == "intraday"
            and (update["last_price"] >= rule["level"] if rule["direction"] == "above"
                 else update["last_price"] <= rule["level"])
            for rule in group) for group in alternatives) if update.get("last_price") is not None else False
        reasons = update.get("reason_codes") or []
        market = update.get("source") or {}
        asof = datetime.fromisoformat(update["execution_asof"])
        from zoneinfo import ZoneInfo
        day = asof.astimezone(ZoneInfo("America/New_York")).date().isoformat()
        session = next(iter(_schedule("US", day)), None)
        session_open = bool(session and session[0] == day and session[1] <= asof < session[2])
        yield {
            "ticker": ticker, "held": ticker in held, "research_entry": thesis["entry_action"],
            "conditional_entry": thesis.get("conditional_entry_action"),
            "entry_expiry": thesis.get("conditional_entry_valid_until"),
            "named_groups": len({level["confirmation_group"] for level in grouped}),
            "ungrouped_entry_type_levels": len(ungrouped), "regular_session_at_evaluation": session_open,
            "quote_asof": update.get("market_data_asof"), "evaluation_at": update.get("execution_asof"),
            "data_quality": market.get("execution_data_quality"), "first_overlay_block": reasons[0] if reasons else None,
            "all_overlay_reasons": " | ".join(reasons), "now_original": update.get("decision_now"),
            "portfolio_now_original": candidate.get("suggested_action_now"),
            "portfolio_final_action_original": (final_actions.get(ticker) or {}).get("action_now"),
            "portfolio_gate_reasons": " | ".join(candidate.get("gate_reasons") or []),
            "wait_heavy_marked": "wait_heavy_batch_reduce_immediate_entries" in candidate.get("gate_reasons", []),
            "budget_blocked_actionable": candidate.get("budget_blocked_actionable"),
            "batch_cash_gap_to_strict_buffer_krw": cash_gap,
            "diagnostic_discard_ungrouped_has_intraday_alternative": original_pilot,
            "diagnostic_discard_ungrouped_intraday_price_crossed": intraday_crossed,
            "diagnostic_remove_wait_heavy_can_release_overlay_block": False if reasons else None,
        }


def _write(path, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs_2026", type=Path)
    parser.add_argument("private_output", type=Path)
    args = parser.parse_args()
    kr = list(_rows(args.runs_2026))
    us = list(_us_rows(args.runs_2026 / "20261125T010228_local-scheduler-us-overlay_only"))
    if len(kr) != 8 * 30 or len(us) != 30 or len({row["ticker"] for row in us}) != 30:
        raise ValueError("Frozen cohort differs from requested 8 × 30 KR and 30 US rows")
    args.private_output.mkdir(parents=True, exist_ok=True)
    _write(args.private_output / "kr-full.csv", kr)
    _write(args.private_output / "us-overlay.csv", us)
    print(json.dumps({
        "kr_status": Counter(row["status"] for row in kr),
        "us_first_overlay_block": Counter(row["first_overlay_block"] for row in us),
        "us_wait_heavy_marked": sum(row["wait_heavy_marked"] for row in us),
        "us_with_intraday_price_crossed_diagnostic": [
            row["ticker"] for row in us if row["diagnostic_discard_ungrouped_intraday_price_crossed"]
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
