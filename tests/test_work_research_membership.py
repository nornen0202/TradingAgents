from datetime import timedelta
import json

import pytest

from tradingagents.atomic_io import atomic_write_json
from tradingagents.work.packet import build_surface_packet
from tests.scheduled.test_research_refresh import NOW, cohort, revision


def research_packet(tmp_path, *, public=False, damage=None):
    watchlist = [f"WATCH{i:02}" for i in range(27)]
    held_only = [f"PRIVATE{i}" for i in range(3)]
    tickers = [*held_only, *watchlist]
    directory, full = cohort(tmp_path, tickers=tickers)
    full["active_universe"] = {
        "expected_holding_tickers": [*held_only, *watchlist[:10]],
        "expected_watchlist_tickers": watchlist,
        "scanner_candidates": [],
        "account_snapshot_status": "loaded",
        "coverage": {"complete": True},
    }
    atomic_write_json(directory / "run.json", full)
    directory, revised = revision(tmp_path, full, target=held_only[0])
    # Actual research-only runs retain all analyses but collect no new account.
    revised["active_universe"] = {"mode": "all_configured", "active_count": 30}
    revised["decision_bundle"] = {"artifacts": {"decision_bundle_v2_json": "decision_bundle_v2.json"}}
    bundle = {"run_id": revised["run_id"], "market": "US", "generated_at": revised["finished_at"],
              "quality": {"decision_ready": False, "report_mode": "OUTAGE"},
              "strategy_table": [{"ticker": t, "is_held": False, "strategy_code": "DATA_CHECK",
                                  "quality": {"execution_ready": False}} for t in tickers]}
    atomic_write_json(directory / "decision_bundle_v2.json", bundle)
    if damage == "receipt":
        revised["research_refresh"]["completed_targets"] = [watchlist[0]]
    if damage == "future":
        revised["finished_at"] = (NOW + timedelta(days=1)).isoformat()
    atomic_write_json(directory / "run.json", revised)
    if damage == "source":
        parent = tmp_path / "runs/2026" / full["run_id"] / "tickers" / held_only[0] / "analysis.json"
        parent.write_text("damaged", encoding="utf-8")
    before = {p: p.read_bytes() for p in tmp_path.rglob("*.json")}
    packet = build_surface_packet("us", archive_dir=tmp_path, now=NOW + timedelta(hours=1), public=public)
    assert before == {p: p.read_bytes() for p in tmp_path.rglob("*.json")}
    return packet["body"], held_only, watchlist


def test_research_revision_preserves_all_frozen_holdings_and_watchlist_without_freshness(tmp_path):
    body, held_only, watchlist = research_packet(tmp_path)
    current = body["current"]
    rows = current["bundle"]["strategy_table"]
    assert len(rows) == len({r["ticker"] for r in rows}) == 30
    roles = {r["ticker"]: r["portfolio_role"] for r in rows}
    assert all(roles[t] == "holding" for t in [*held_only, *watchlist[:10]])
    assert all(roles[t] == "watchlist" for t in watchlist[10:])
    assert current["universe_coverage"]["status"] == "UNVERIFIED"
    assert current["universe_coverage"]["complete"] is False
    assert current["universe_membership_reference"]["status"] == "REFERENCE_ONLY"
    assert current["universe_membership_reference"]["current_account_verified"] is False
    assert current["freshness_receipt"]["account_as_of"] is None
    assert body["source_health"] == "UNVERIFIED"
    assert all(r["execution"]["readiness"] == "NEEDS_LIVE_RECHECK" for r in rows)
    assert all(r["execution"]["action_now"] is None for r in rows)


def test_public_research_revision_exposes_only_original_watchlist(tmp_path):
    body, held_only, watchlist = research_packet(tmp_path, public=True)
    rows = body["current"]["bundle"]["strategy_table"]
    assert {r["ticker"] for r in rows} == set(watchlist)
    assert not any(t in json.dumps(body) for t in held_only)
    assert all("is_held" not in r and "execution" not in r for r in rows)


@pytest.mark.parametrize("damage", ["receipt", "source", "future"])
def test_unverified_revision_cannot_inherit_membership(tmp_path, damage):
    body, _, _ = research_packet(tmp_path, damage=damage)
    rows = body["current"]["bundle"]["strategy_table"]
    assert len(rows) == 10
    assert all(r["portfolio_role"] == "discovery" for r in rows)
    assert body["current"]["universe_coverage"]["complete"] is False
