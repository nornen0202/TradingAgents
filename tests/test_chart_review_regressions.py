import json

import pytest

from tradingagents.charting.bars import validate_bars
from tradingagents.charting.report import build_review, main, render_review
from tradingagents.charting.snapshot import get_replay_snapshot
from tradingagents.dataflows.institutional_models import EvidenceItem


ASOF = "2026-10-11T00:00:00+00:00"


def candle(**changes):
    return {"timestamp": "2026-10-09T20:00:00+00:00", "available_at": "2026-10-09T20:00:01+00:00",
            "observed_at": "2026-10-09T20:00:02+00:00", "session_id": "2026-10-09", "interval": "1d",
            "open": 100, "high": 110, "low": 90, "close": 105, "volume": 1000, **changes}


def write(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")


def archive(tmp_path, **capture_changes):
    directory = tmp_path / "AAPL"
    directory.mkdir()
    write(directory / "chart_evidence.json", {"ticker": "AAPL", "provider": "fixture", "bars": [candle()], **capture_changes})
    write(directory / "analysis.json", {"finished_at": "2026-10-09T20:01:00Z"})
    return directory


def evidence(**changes):
    return {"claim": "Timestamp-verified fact", "kind": "fact", "ticker": "AAPL",
            "known_at": "2026-10-09T19:00:00Z", "published_at": "2026-10-09T18:00:00Z",
            "observed_at": "2026-10-09T19:01:00Z", "source_refs": [{"provider": "sec", "title": "filing"}], **changes}


def test_actual_list_evidence_artifact_preserves_imported_clocks_and_kind(tmp_path):
    directory = archive(tmp_path)
    item = EvidenceItem.from_mapping(evidence(), ticker="AAPL").to_dict()
    assert item["kind"] == "fact" and item["known_at"] == evidence()["known_at"]
    write(directory / "evidence_ledger.json", [item, {"claim": "Untimed agent inference"}])
    review = build_review(directory, analysis_as_of=ASOF)
    assert review["evidence"][0]["claim"] == item["claim"]
    assert review["evidence"][0]["event_time"] == "2026-10-09T18:00:00+00:00"
    assert review["unverified_evidence_count"] == 1


@pytest.mark.parametrize("changes", [{"provider": "tradingview_mcp"},
                                    {"source_refs": [{"provider": "unconfigured_vendor"}]},
                                    {"known_at": "2026-10-09T17:00:00Z"},
                                    {"observed_at": "2026-10-19T00:00:00Z"},
                                    {"kind": "verified_by_model"}])
def test_invalid_or_unentitled_evidence_cannot_enter_fact_view(tmp_path, changes):
    directory = archive(tmp_path)
    write(directory / "evidence_ledger.json", [evidence(**changes)])
    review = build_review(directory, analysis_as_of=ASOF)
    assert review["evidence"] == [] and review["unverified_evidence_count"] == 1


@pytest.mark.parametrize("provider,entitlement", [("tradingview_mcp", None), ("custom_vendor", None),
                                                  ("fixture", []), ("fixture", {"verified": False})])
def test_denied_chart_sources_are_not_calculated_or_rendered(tmp_path, provider, entitlement):
    directory = archive(tmp_path, provider=provider, entitlement=entitlement, public_display_allowed=True)
    review = build_review(directory, analysis_as_of=ASOF)
    assert review["series"] == []
    assert review["public_display_allowed"] is False
    assert review["rejected_bars"]["source_not_entitled"] == 1


def test_foreign_ticker_microstructure_cannot_contaminate_chart(tmp_path):
    directory = archive(tmp_path)
    write(directory / "microstructure_snapshot.json", {"ticker": "MSFT", "provider": "kis", "chart_bars": [candle(close=101)]})
    review = build_review(directory, analysis_as_of=ASOF)
    assert review["series"][0]["bars"][0]["close"] == 105
    assert review["rejected_bars"]["ticker_mismatch"] == 1


@pytest.mark.parametrize("change", [{"interval": []}, {"session_id": True}, {"session_id": "bad"},
                                    {"corrected_at": "2026-10-19T00:00:00Z"}])
def test_malformed_rows_do_not_destroy_valid_bars(change):
    result = validate_bars([candle(), candle(**change)], analysis_as_of=ASOF)
    assert len(result["bars"]) == 1
    assert result["rejected"]


def test_closed_last_session_remains_research_only_and_older_close_is_rejected(tmp_path):
    directory = archive(tmp_path)
    snapshot = get_replay_snapshot("AAPL", ASOF, ticker_dir=directory)
    assert snapshot["freshness_status"] == "MISSING"
    assert snapshot["research_status"] == "LATEST_REGULAR_CLOSE_RESEARCH_ONLY"
    assert snapshot["research_receipt"]["research_valid"]
    assert not snapshot["research_receipt"]["execution_eligible"]
    write(directory / "chart_evidence.json", {"ticker": "AAPL", "provider": "fixture",
          "bars": [candle(timestamp="2026-10-08T20:00:00Z", available_at="2026-10-08T20:00:01Z",
                          observed_at="2026-10-08T20:00:02Z", session_id="2026-10-08")]})
    stale = get_replay_snapshot("AAPL", ASOF, ticker_dir=directory)
    assert not stale["research_receipt"]["research_valid"]


def test_legacy_contract_levels_and_cli_share_snapshot(tmp_path):
    directory = archive(tmp_path)
    write(directory / "execution_contract.json", {"ingested_at": "2026-10-09T20:01:01Z", "breakout_level": 111, "invalid_if_close_below": 90,
                                                  "pullback_buy_zone": {"low": 95, "high": 97}})
    snapshot = get_replay_snapshot("AAPL", ASOF, ticker_dir=directory)
    assert {level["price"] for level in snapshot["price_levels"]} == {111, 90, 95, 97}
    output = tmp_path / "review.html"
    assert main(["--ticker", "AAPL", "--ticker-dir", str(directory), "--as-of", ASOF,
                 "--output", str(output)]) == 0
    assert output.read_text(encoding="utf-8") == render_review(snapshot)


def test_event_guard_reconstruction_retains_detection_and_exact_windows():
    from tradingagents.scheduled.runner import _ExecutionContractShim
    guard = {"minutes_before_event": 45, "minutes_after_publication": 17,
             "first_seen_at": "2026-10-09T20:00:00Z", "first_seen_cooldown_minutes": 31,
             "exact_event_time_known": False, "is_amended": True}
    restored = _ExecutionContractShim({"ticker": "AAPL", "event_guard": guard}).to_contract().event_guard.to_dict()
    assert all(restored[key] == value for key, value in guard.items())


def test_canonical_replay_entry_matches_chart_entry(tmp_path):
    from tradingagents.performance.replay import get_replay_snapshot as replay_snapshot
    directory = archive(tmp_path)
    assert replay_snapshot("AAPL", ASOF, ticker_dir=directory) == get_replay_snapshot("AAPL", ASOF, ticker_dir=directory)


def test_primary_render_tool_uses_canonical_snapshot_and_multiple_journals(tmp_path):
    from tools.render_investment_review import main as render_main
    directory = archive(tmp_path)
    output = tmp_path / "tool-review.html"
    assert render_main([str(directory), "--as-of", ASOF, "--output", str(output),
                        "--tracker-db", str(tmp_path / "absent1.sqlite"),
                        "--tracker-db", str(tmp_path / "absent2.sqlite")]) == 0
    snapshot = get_replay_snapshot("AAPL", ASOF, ticker_dir=directory)
    # Empty journal projections have the canonical empty replay shape.
    actual = json.loads(output.with_suffix(".json").read_text(encoding="utf-8"))
    assert actual["series"] == snapshot["series"]
    assert actual["analysis_as_of"] == snapshot["analysis_as_of"]
    assert actual["broker_orders_sent"] == 0 and actual["read_only"]


def test_capture_excludes_supplemental_kr_holiday_and_preserves_actual_close():
    import pandas as pd
    from datetime import datetime, timezone
    from tradingagents.charting.capture import ChartCapture, capture_daily_frame
    frame = pd.DataFrame([{ "Date": day, "Open": 100, "High": 110, "Low": 90, "Close": 105, "Volume": 10}
                          for day in ("2026-07-16", "2026-07-17")])
    recorder = ChartCapture("005930.KS")
    token = recorder.activate()
    try:
        capture_daily_frame("005930.KS", frame, curr_date="2026-07-17")
    finally:
        recorder.reset(token)
    bars = recorder.artifact(analysis_as_of=datetime.now(timezone.utc))["bars"]
    assert [bar["session_id"] for bar in bars] == ["2026-07-16"]


def test_contract_cannot_appear_before_its_own_ingestion(tmp_path):
    directory = archive(tmp_path)
    write(directory / "execution_contract.json", {"ingested_at": "2026-10-09T20:03:00Z", "breakout_level": 111})
    assert build_review(directory, analysis_as_of="2026-10-09T20:02:00Z")["plan"] == {}
    assert build_review(directory, analysis_as_of="2026-10-09T20:03:00Z")["plan"]["breakout_level"] == 111
    write(directory / "execution_contract.json", {"breakout_level": 111})
    assert build_review(directory, analysis_as_of=ASOF)["plan"] == {}


def test_fill_markers_preserve_sell_direction_and_execution_mode(tmp_path, monkeypatch):
    directory = archive(tmp_path)
    history = {"events": [{"kind": "FILL", "mode": mode, "occurred_at": "2026-10-09T19:00:00Z",
                            "payload": {"side": "SELL"}} for mode in ("actual", "demo", "paper")]}
    monkeypatch.setattr("tradingagents.performance.replay.replay_action_history", lambda *args, **kwargs: history)
    result = get_replay_snapshot("AAPL", ASOF, ticker_dir=directory, db_paths=["fixture.sqlite"])
    markers = result["markers"]
    assert {marker["category"] for marker in markers} == {"REAL_FILL", "DEMO_FILL", "PAPER_FILL"}
    assert all(marker["shape"] == "arrowDown" and marker["position"] == "aboveBar" for marker in markers)
    assert {marker["text"] for marker in markers} == {"실제 체결 · SELL", "데모 체결 · SELL", "모의 체결 · SELL"}


def test_shared_snapshot_rejects_future_queries_and_fixture_clock_is_explicit(tmp_path):
    from datetime import datetime, timezone
    directory = archive(tmp_path)
    with pytest.raises(ValueError, match="future"):
        get_replay_snapshot("AAPL", "2099-01-01T00:00:00Z", ticker_dir=directory)
    snapshot = get_replay_snapshot("AAPL", "2026-10-18T00:00:00Z", ticker_dir=directory,
                                   clock=lambda: datetime(2026, 10, 19, tzinfo=timezone.utc))
    assert snapshot["analysis_as_of"] == "2026-10-18T00:00:00+00:00"
    with pytest.raises(SystemExit):
        main(["--ticker", "AAPL", "--ticker-dir", str(directory), "--as-of", "2099-01-01T00:00:00Z",
              "--output", str(tmp_path / "future.html")])
