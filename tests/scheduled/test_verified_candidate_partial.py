from datetime import datetime
import json

import pytest

from tradingagents.scheduled.research_recovery import verified_candidate_partial
from tradingagents.scheduled.runner import _resolve_latest_full_overlay_baseline_manifest


RUN = "20261124T053248_local-scheduler-kr-full"
START = "2026-11-24T05:32:48+09:00"
END = "2026-11-24T06:30:00+09:00"
NOW = datetime.fromisoformat("2026-11-24T10:03:00+09:00")


def _write(path, document):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document), encoding="utf-8")


@pytest.mark.parametrize("missing,blocker", [(1, None), (2, None), (3, None), (4, "budget"), (1, "holding"),
    (1, "required_alias"), (1, "global"), (1, "identity"), (1, "duplicate"), (1, "market")])
def test_regular_overlay_baseline_requires_a_verified_optional_ticker_failure(tmp_path, missing, blocker):
    directory = tmp_path / "runs" / "2026" / RUN
    symbols = [f"{i:06d}.KS" for i in range(1, 31)]
    broken = symbols[-missing:]
    rows = []
    for symbol in symbols:
        if symbol in broken:
            rows.append({"ticker": symbol, "status": "failed",
                         "failure_diagnostics": {"failure_category": "DATA_PROVIDERS_UNAVAILABLE"},
                         "error": "KR daily history has missing required sessions or non-session bars"})
            continue
        row = {"ticker": symbol, "status": "success", "started_at": START, "finished_at": END,
               "trade_date": "2026-11-23", "decision": "WAIT"}
        artifacts = {"analysis_json": "analysis.json", "final_state_json": "final_state.json",
                     "execution_contract_json": "execution_contract.json"}
        row["artifacts"] = {key: f"tickers/{symbol}/{file}" for key, file in artifacts.items()}
        _write(directory / row["artifacts"]["analysis_json"], row)
        _write(directory / row["artifacts"]["final_state_json"], {"company_of_interest": (
            "000123.KS" if blocker == "identity" and symbol == symbols[0] else symbol)})
        _write(directory / row["artifacts"]["execution_contract_json"], {"ticker": symbol})
        rows.append(row)
    manifest = {
        "run_id": RUN, "label": "local-scheduler-kr-full", "status": "partial_failure",
        "started_at": START, "finished_at": END, "daily_thesis_trade_date": "2026-11-23",
        "settings": {"market": "US" if blocker == "market" else "KR", "run_mode": "full", "analysis_mode": "full"},
        "summary": {"total_tickers": 30, "successful_tickers": 30 - missing, "failed_tickers": missing},
        "circuit_breaker": {"triggered": blocker == "global"},
        "tickers": rows if blocker != "duplicate" else [*rows[:-1], rows[0]],
        "active_universe": {
            "mode": "adaptive_required_coverage", "market": "KR", "account_snapshot_status": "loaded",
            "account_snapshot_health": "VALID", "coverage": {"complete": False, "selection_complete": True},
            "active_count": 30, "selected_tickers": symbols, "expected_watchlist_tickers": symbols[13:],
            "expected_holding_tickers": symbols[:13] if blocker != "holding" else [broken[0]],
            "candidates": [{"ticker": symbol, "selected": True, "selection_reason": "fresh_candidate_exploration"}
                           for symbol in broken],
        },
    }
    _write(directory / "run.json", manifest)
    _write(directory / "attempt.json", {"status": "PARTIAL_FAILURE"})
    required = (broken[0].split(".")[0],) if blocker == "required_alias" else ()
    assert verified_candidate_partial(tmp_path, manifest, now=NOW, required_tickers=required) == ([] if blocker else broken)
    assert _resolve_latest_full_overlay_baseline_manifest(tmp_path, now=NOW, market="KR") is None
    admitted = _resolve_latest_full_overlay_baseline_manifest(
        tmp_path, now=NOW, market="KR", partial_required_tickers=required,
    )
    assert (admitted or {}).get("_verified_candidate_omissions") == (None if blocker else broken)
    assert json.loads((directory / "run.json").read_bytes()) == manifest
