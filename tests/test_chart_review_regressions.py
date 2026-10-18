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
    # Future ingestion is wholly absent from an earlier frame, including its
    # diagnostics; other present-time invalid records remain accounted for.
    expected = 0 if changes.get("observed_at") == "2026-10-19T00:00:00Z" else 1
    assert review["evidence"] == [] and review["unverified_evidence_count"] == expected


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


def test_prior_checkpoint_restores_decision_and_original_bar_vintage(tmp_path):
    directory = archive(tmp_path)
    checkpoints = directory / "execution" / "checkpoints"
    checkpoints.mkdir(parents=True)
    old_execution = {"ticker": "AAPL", "execution_asof": "2026-10-09T20:05:00Z", "ingested_at": "2026-10-09T20:05:01Z",
                     "market_data_asof": "2026-10-09T20:04:00Z", "decision_state": "WAIT", "reason_codes": ["old_volume_block"]}
    old_bar = candle(timestamp="2026-10-09T19:59:00Z", available_at="2026-10-09T20:00:00Z",
                     observed_at="2026-10-09T20:04:00Z", interval="1m")
    old_micro = {"ticker": "AAPL", "provider": "fixture", "published_at": "2026-10-09T20:05:01Z", "chart_bars": [old_bar, {"invalid": "old row"}]}
    write(checkpoints / "execution_update_open.json", old_execution)
    write(checkpoints / "microstructure_snapshot_open.json", old_micro)
    write(directory / "execution_update.json", old_execution)
    write(directory / "microstructure_snapshot.json", old_micro)
    early = build_review(directory, analysis_as_of="2026-10-09T20:06:00Z")
    new_execution = {**old_execution, "execution_asof": "2026-10-09T20:10:00Z", "ingested_at": "2026-10-09T20:10:01Z",
                     "decision_state": "APPROVED", "reason_codes": ["FUTURE_ENGINE_REASON"]}
    revised_bar = {**old_bar, "observed_at": "2026-10-09T20:09:00Z", "available_at": "2026-10-09T20:08:00Z", "close": 106}
    next_bar = {**revised_bar, "timestamp": "2026-10-09T20:00:00Z", "close": 107}
    new_micro = {**old_micro, "published_at": "2026-10-09T20:10:01Z", "chart_bars": [revised_bar, next_bar]}
    write(checkpoints / "close_execution_update.json", new_execution)
    write(checkpoints / "close_microstructure_snapshot.json", new_micro)
    write(directory / "execution_update.json", new_execution)
    write(directory / "microstructure_snapshot.json", new_micro)
    assert build_review(directory, analysis_as_of="2026-10-09T20:06:00Z") == early
    assert early["execution"]["reason_codes"] == ["old_volume_block"]
    assert "FUTURE_ENGINE_REASON" not in json.dumps(early)
    assert next(item for item in early["series"] if item["interval"] == "1m")["bars"][0]["close"] == 105
    late = build_review(directory, analysis_as_of="2026-10-09T20:11:00Z")
    assert late["execution"]["reason_codes"] == ["FUTURE_ENGINE_REASON"]
    assert [row["close"] for row in next(item for item in late["series"] if item["interval"] == "1m")["bars"]] == [106, 107]


def test_future_checkpoint_source_diagnostics_do_not_change_prior_frame(tmp_path):
    directory = archive(tmp_path, public_display_allowed=True)
    early = build_review(directory, analysis_as_of="2026-10-09T20:06:00Z")
    checkpoints = directory / "execution" / "checkpoints"
    checkpoints.mkdir(parents=True)
    future = {"published_at": "2026-10-09T21:00:00Z", "ticker": "WRONG", "provider": "tradingview_mcp",
              "chart_bars": [candle(), {"invalid": "FUTURE_DIAGNOSTIC"}]}
    write(checkpoints / "microstructure_snapshot_future.json", future)
    write(directory / "microstructure_snapshot.json", future)
    assert build_review(directory, analysis_as_of="2026-10-09T20:06:00Z") == early
    assert early["public_display_allowed"] is True


def test_same_observation_conflicts_are_excluded_instead_of_inferred_revision(tmp_path):
    directory = archive(tmp_path, bars=[candle(), candle(close=106)])
    assert build_review(directory, analysis_as_of=ASOF)["series"] == []
    write(directory / "chart_evidence.json", {"ticker": "AAPL", "provider": "fixture", "bars": [candle(),
          candle(close=106, available_at="2026-10-09T20:02:00Z", observed_at="2026-10-09T20:03:00Z")]})
    result = build_review(directory, analysis_as_of=ASOF)
    bar = result["series"][0]["bars"][0]
    assert bar["close"] == 106 and not bar["is_amended"]  # No invented provider amendment flag.


def test_stored_session_vwap_and_quote_metrics_are_copied_without_recalculation(tmp_path):
    directory = archive(tmp_path)
    execution = {"ticker": "AAPL", "execution_asof": "2026-10-09T20:03:00Z", "ingested_at": "2026-10-09T20:03:01Z",
                 "market_data_asof": "2026-10-09T20:02:00Z", "decision_state": "WAIT", "reason_codes": ["stored_gate"],
                 "session_vwap": 123, "last_price": 127, "relative_volume": 2.5}
    write(directory / "execution_update.json", execution)
    snapshot = get_replay_snapshot("AAPL", "2026-10-09T20:04:00Z", ticker_dir=directory)
    for key in ("session_vwap", "last_price", "relative_volume"):
        assert snapshot["execution"][key] == execution[key]
    vwap = next(level for level in snapshot["price_levels"] if level["label"] == "당일 VWAP · 실행 엔진")
    assert vwap["price"] == 123 and vwap["style"] == "DOTTED"
    assert vwap["event_time"] == vwap["market_data_asof"] == execution["market_data_asof"]
    assert vwap["ingested_at"] == execution["ingested_at"] and vwap["evaluated_at"] == execution["execution_asof"]
    rendered = render_review(snapshot)
    assert "당일 VWAP · 실행 엔진 123" in rendered and 'stroke-dasharray="1 3"' in rendered
    assert execution["market_data_asof"] in rendered
    for key, bad in (("session_vwap", float("nan")), ("last_price", -1), ("relative_volume", float("inf"))):
        write(directory / "execution_update.json", {**execution, key: bad})
        assert key not in build_review(directory, analysis_as_of="2026-10-09T20:04:00Z")["execution"]


def test_future_engine_vwap_is_hidden_and_prior_checkpoint_vwap_is_restored(tmp_path):
    directory = archive(tmp_path)
    checkpoints = directory / "execution" / "checkpoints"
    checkpoints.mkdir(parents=True)
    old = {"ticker": "AAPL", "execution_asof": "2026-10-09T20:03:00Z", "ingested_at": "2026-10-09T20:03:01Z",
           "market_data_asof": "2026-10-09T20:02:00Z", "decision_state": "WAIT", "session_vwap": 123}
    write(checkpoints / "execution_update_first.json", old)
    write(directory / "execution_update.json", {**old, "session_vwap": 999, "execution_asof": "2026-10-09T20:10:00Z",
                                               "ingested_at": "2026-10-09T20:10:01Z", "market_data_asof": "2026-10-09T20:09:00Z"})
    early = get_replay_snapshot("AAPL", "2026-10-09T20:02:59Z", ticker_dir=directory)
    assert not any(level["label"] == "당일 VWAP · 실행 엔진" for level in early["price_levels"])
    restored = get_replay_snapshot("AAPL", "2026-10-09T20:04:00Z", ticker_dir=directory)
    assert restored["execution"]["session_vwap"] == 123
    assert next(level["price"] for level in restored["price_levels"] if level["label"] == "당일 VWAP · 실행 엔진") == 123
    late = get_replay_snapshot("AAPL", "2026-10-09T20:11:00Z", ticker_dir=directory)
    assert late["execution"]["session_vwap"] == 999
