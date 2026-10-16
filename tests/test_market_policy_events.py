from dataclasses import replace
from datetime import datetime, timedelta, timezone
import json
import sys
from types import SimpleNamespace

import pytest

from tradingagents.dataflows.event_timeline import (
    build_event_timeline, capture_disclosures, disclosure_event_records,
    EventFirstSeenStore, imported_event_records, reset_event_capture, snapshot_event_records,
)
from tradingagents.dataflows.market_policy import (
    TimestampEnvelope, latest_regular_session_context, market_observation_policy, observation_status, research_observation_policy, session_policy, source_use_policy,
)
from tradingagents.execution.overlay import evaluate_execution_state
from tradingagents.schemas.execution import (
    ActionIfTriggered, BreakoutConfirmation, EventGuard, ExecutionContract,
    IntradayMarketSnapshot, LevelBasis, PrimarySetup, ThesisState, is_event_guard_active,
)
from tradingagents.work.freshness import source_freshness_receipt

NOW = datetime(2026, 10, 16, 14, tzinfo=timezone.utc)


@pytest.mark.parametrize("value,status", [
    (None, "MISSING"), ("", "MISSING"), ("bad", "INVALID"),
    ("2026-10-16T14:00:00", "INVALID"),
    ((NOW + timedelta(microseconds=1)).isoformat(), "FUTURE"),
    ((NOW - timedelta(minutes=10)).isoformat(), "STALE"),
    ((NOW - timedelta(minutes=9, seconds=59)).isoformat(), "FRESH"),
])
def test_shared_strict_freshness_clocks(value, status):
    assert observation_status(value, as_of=NOW)["status"] == status


def test_publication_cannot_renew_clock_and_clock_offsets_are_instants():
    assert not observation_status(NOW - timedelta(minutes=20), as_of=NOW, published_at=NOW)["eligible"]
    assert observation_status("2026-10-16T23:00:00+09:00", as_of=NOW)["age_seconds"] == 0
    assert observation_status(NOW, as_of=NOW, published_at=NOW + timedelta(seconds=1))["status"] == "FUTURE_PUBLICATION"
    assert observation_status(NOW, as_of=NOW, published_at="bad")["status"] == "INVALID_PUBLICATION"
    assert observation_status(NOW - timedelta(minutes=10), as_of=NOW, max_age=timedelta(hours=1))["status"] == "STALE"
    with pytest.raises(ValueError, match="timezone-aware"):
        observation_status(NOW, as_of=NOW.replace(tzinfo=None))


@pytest.mark.parametrize("provider", ["TradingView MCP", "tradingview", "tv_mcp", "trading-view-mcp"])
def test_interactive_data_never_entitled_to_automation(provider):
    assert source_use_policy(provider, use="manual_comparison")["allowed"]
    for use in ("automated_analysis", "execution", "alerts", "backtest"):
        assert not source_use_policy(provider, use=use, entitlement={"verified": True, "permitted_uses": [use]})["allowed"]


def test_session_and_source_rights_fail_closed():
    assert not source_use_policy("unconfigured_vendor")["allowed"]
    assert source_use_policy("custom", entitlement={"verified": True, "permitted_uses": ["automated_analysis"]})["allowed"]
    assert not source_use_policy("custom", entitlement={"verified": True, "permitted_uses": ["execution"]})["allowed"]
    assert not source_use_policy("kis", entitlement=[])["allowed"]
    for session in (None, "unknown", "pre_open", "post_close", {"is_open": True, "phase": "unknown"},
                    {"is_open": True, "phase": "regular", "verified": False}):
        assert not session_policy(session)["eligible"]
    assert session_policy({"is_open": True, "phase": "regular"})["eligible"]
    assert market_observation_policy(NOW, as_of=NOW, session="regular", provider="kis")["eligible"]
    assert "INTERACTIVE_SOURCE_NOT_AUTOMATION_ENTITLED" in market_observation_policy(
        NOW, as_of=NOW, session="regular", provider="tv_mcp")["blockers"]


def event(**changes):
    return {"event_id": "earnings-a", "version_id": "a1", "ticker": "AAPL", "event_type": "earnings",
            "title": "Earnings", "status": "scheduled", "provider": "local_archive",
            "scheduled_at": "2026-10-16T16:30:00-04:00", "published_at": None,
            "known_at": "2026-10-15T10:00:00-04:00", "observed_at": "2026-10-15T14:05:00Z", **changes}


def test_future_schedule_visible_but_future_disclosure_and_unknown_clocks_excluded():
    records = [event(), event(event_id="pub", version_id="p1", status="published", published_at="2026-10-17T10:00:00Z"),
               event(event_id="bad", version_id="b1", known_at=None),
               event(event_id="missing", version_id="m1", status="published", published_at=None),
               event(event_id="naive", version_id="n1", scheduled_at="2026-10-17T16:30:00"),
               event(event_id="future-observed", version_id="f1", observed_at="2026-10-17T10:00:00Z")]
    board = build_event_timeline(records, analysis_as_of=NOW)
    assert [row["event_id"] for row in board["events"]] == ["earnings-a"]
    assert len(board["rejected"]) == 3
    assert records[0] == event()
    assert build_event_timeline([], analysis_as_of=NOW)["events"] == []


def test_corrections_do_not_rewrite_earlier_knowledge_and_have_version_lineage():
    correction = event(version_id="a2", supersedes_version_id="a1", status="corrected",
                       published_at="2026-10-16T13:00:00Z", known_at="2026-10-16T13:00:00Z",
                       observed_at="2026-10-16T13:05:00Z", scheduled_at="2026-10-17T16:30:00-04:00")
    before = build_event_timeline([event(), correction], analysis_as_of=NOW - timedelta(hours=2))
    after = build_event_timeline([event(), correction], analysis_as_of=NOW)
    assert before["events"][0]["version_id"] == "a1"
    assert after["events"][0]["version_id"] == "a2"
    assert [row["version_id"] for row in after["events"][0]["versions"]] == ["a1", "a2"]
    assert not build_event_timeline([correction], analysis_as_of=NOW)["events"]
    assert not build_event_timeline([event(), event(title="conflicting")], analysis_as_of=NOW)["events"]


@pytest.mark.parametrize("change", [
    {"known_at": "bad"}, {"observed_at": None}, {"version_id": None}, {"status": "unknown"},
    {"known_at": "2026-10-15T15:00:00Z"}, {"provider": "tradingview_mcp"},
    {"status": "corrected", "published_at": "2026-10-15T14:00:00Z"},
    {"first_seen_at": "bad"},
])
def test_invalid_event_versions_are_not_analysis_evidence(change):
    board = build_event_timeline([event(**change)], analysis_as_of=NOW)
    assert not board["events"] and board["rejected"]


def test_capture_and_import_bridge_preserve_clocks_without_fabricating_dart_times():
    reset_event_capture()
    items = [SimpleNamespace(url="https://www.sec.gov/filing/1", title="10-Q", raw_vendor="sec_edgar",
                             symbol="AAPL", published_at=NOW - timedelta(hours=1)),
             SimpleNamespace(url="https://dart.fss.or.kr/1", title="Report", raw_vendor="opendart",
                             symbol="005930", published_at=NOW.replace(tzinfo=None))]
    capture_disclosures(items, observed_at=NOW)
    assert len(snapshot_event_records()) == 2
    board = build_event_timeline(snapshot_event_records(), analysis_as_of=NOW)
    assert [row["ticker"] for row in board["events"]] == ["AAPL"]
    assert len(board["rejected"]) == 1
    assert not build_event_timeline(snapshot_event_records("AAPL"), analysis_as_of=NOW - timedelta(minutes=1))["events"]
    assert imported_event_records([{"earnings_event_pack": {"event_records": [event()]}}], ticker="AAPL") == [event()]
    reset_event_capture()
    assert not snapshot_event_records()


def contract():
    return ExecutionContract(ticker="AAPL", analysis_asof=(NOW-timedelta(days=1)).isoformat(),
        market_data_asof=NOW.isoformat(), level_basis=LevelBasis.INTRADAY_SNAPSHOT,
        thesis_state=ThesisState.CONSTRUCTIVE, primary_setup=PrimarySetup.BREAKOUT_CONFIRMATION,
        portfolio_stance="BULLISH", entry_action_base="STARTER", setup_quality="COMPELLING", confidence=.8,
        action_if_triggered=ActionIfTriggered.STARTER, breakout_level=100,
        breakout_confirmation=BreakoutConfirmation.INTRADAY_ABOVE)


def market(**changes):
    return IntradayMarketSnapshot(ticker="AAPL", asof=NOW.isoformat(), provider="fixture", interval="1m",
        last_price=101, session_vwap=100, day_high=102, day_low=99, volume=100,
        avg20_daily_volume=100, relative_volume=1.2, market_session="regular", **changes)


def test_execution_uses_same_age_boundary_and_excludes_missing_future_invalid():
    for value in ("bad", "", NOW.replace(tzinfo=None).isoformat(), (NOW+timedelta(seconds=1)).isoformat(),
                  (NOW-timedelta(minutes=10)).isoformat()):
        update = evaluate_execution_state(contract(), replace(market(), asof=value), now=NOW, max_data_age_seconds=3600)
        assert update.decision_now.value == "NONE"
    assert evaluate_execution_state(contract(), market(), now=NOW, max_data_age_seconds=3600).decision_now.value == "STARTER_NOW"
    for change in ({"market_session": "closed"}, {"market_session": "unknown"}, {"provider": "tradingview_mcp"}):
        update = evaluate_execution_state(contract(), replace(market(), **change), now=NOW, max_data_age_seconds=3600)
        assert update.decision_now.value == "NONE"


def test_precise_event_window_rerun_and_risk_reduction_are_deterministic():
    guard = EventGuard(scheduled_at=(NOW+timedelta(minutes=1)).isoformat(), known_at=(NOW-timedelta(days=1)).isoformat(),
                       block_new_position_within_days=1, requires_post_event_rerun=True)
    assert is_event_guard_active(guard, NOW)
    assert not is_event_guard_active(replace(guard, known_at=(NOW+timedelta(seconds=1)).isoformat()), NOW)
    released = replace(guard, published_at=(NOW-timedelta(minutes=16)).isoformat())
    assert is_event_guard_active(released, NOW, analysis_as_of=(NOW-timedelta(hours=1)).isoformat())
    assert not is_event_guard_active(released, NOW, analysis_as_of=NOW.isoformat())
    entry = replace(contract(), event_guard=guard)
    assert evaluate_execution_state(entry, market(), now=NOW, max_data_age_seconds=600).decision_now.value == "NONE"
    protective = replace(entry, invalid_if_intraday_below=100)
    result = evaluate_execution_state(protective, market(), now=NOW, max_data_age_seconds=600)
    assert result.decision_now.value == "EXIT_NOW"


def test_freshness_receipt_excludes_future_observations_from_ranges():
    bundle = {"strategy_table": [{"market_data_asof": NOW.isoformat()},
                                  {"market_data_asof": (NOW+timedelta(days=1)).isoformat()}]}
    result = source_freshness_receipt({}, bundle, now=NOW, analysis_manifest={}, public=False)
    assert result["market_data_status"] == "INVALID"
    assert result["market_data_oldest_at"] == result["market_data_latest_at"] == NOW.isoformat()
    assert result["market_data_future_count"] == 1


def test_timestamp_envelope_preserves_three_independent_clocks():
    raw = {"published_at": (NOW-timedelta(hours=1)).isoformat(), "observed_at": NOW.isoformat(), "status": "corrected"}
    envelope = TimestampEnvelope.from_mapping(raw, evaluated_at=NOW.isoformat()).to_dict()
    assert envelope["event_time"] == raw["published_at"]
    assert envelope["ingested_at"] == raw["observed_at"]
    assert envelope["evaluated_at"] == NOW.isoformat() and envelope["is_amended"]
    assert envelope["available_as_of"]
    assert not TimestampEnvelope(NOW.isoformat(), (NOW-timedelta(hours=1)).isoformat(), NOW.isoformat()).to_dict()["available_as_of"]


def test_closed_latest_verified_close_is_research_only_without_age_relaxation():
    friday_close = datetime(2026, 10, 16, 20, tzinfo=timezone.utc)
    sunday = friday_close + timedelta(days=2)
    common = {"as_of": sunday, "session": "closed", "latest_regular_close_at": friday_close, "verified_session": True}
    receipt = research_observation_policy(friday_close, **common)
    assert receipt["research_valid"] and not receipt["execution_eligible"]
    assert receipt["category"] == "LATEST_REGULAR_CLOSE_RESEARCH_ONLY"
    assert not research_observation_policy(friday_close-timedelta(days=1), **common)["research_valid"]
    assert not research_observation_policy(friday_close, **{**common, "verified_session": False})["research_valid"]
    assert not research_observation_policy(friday_close, interval="5m", **common)["research_valid"]
    assert not research_observation_policy(friday_close, **{**common, "session": "regular"})["research_valid"]
    extended = research_observation_policy(NOW, as_of=NOW, session="pre_open")
    assert extended["research_valid"] and not extended["execution_eligible"]
    assert extended["category"] == "EXTENDED_SESSION_RESEARCH_ONLY"


def test_dart_first_seen_persists_without_inventing_publication_and_guards_prospectively(tmp_path):
    path = tmp_path / "events.sqlite3"
    disclosure = SimpleNamespace(url="https://dart.fss.or.kr/receipt/42", title="[정정] earnings",
        raw_vendor="opendart", symbol="005930", published_at=NOW.replace(tzinfo=None))
    first = disclosure_event_records([disclosure], observed_at=NOW, first_seen_db=path)[0]
    assert first["published_at"] is None and first["exact_event_time_known"] is False
    assert first["first_seen_at"] == NOW.isoformat() and first["is_amended"]
    second = disclosure_event_records([disclosure], observed_at=NOW+timedelta(hours=1), first_seen_db=path)[0]
    assert second["first_seen_at"] == first["first_seen_at"]
    assert EventFirstSeenStore(path).observe(disclosure.url, detected_at=NOW+timedelta(days=1)) == first["first_seen_at"]
    board = build_event_timeline([first], analysis_as_of=NOW)
    assert board["events"][0]["status"] == "detected"
    assert not build_event_timeline([first], analysis_as_of=NOW-timedelta(seconds=1))["events"]
    guard = EventGuard(first_seen_at=first["first_seen_at"], exact_event_time_known=False,
                       known_at=first["known_at"], first_seen_cooldown_minutes=30)
    assert not is_event_guard_active(guard, NOW-timedelta(seconds=1))
    assert is_event_guard_active(guard, NOW+timedelta(minutes=29, seconds=59))
    assert not is_event_guard_active(guard, NOW+timedelta(minutes=30))


def test_us_exact_before_and_after_cooldowns_do_not_use_whole_days():
    guard = EventGuard(scheduled_at=NOW.isoformat(), known_at=(NOW-timedelta(days=1)).isoformat(),
        minutes_before_event=30, minutes_after_publication=15)
    assert not is_event_guard_active(guard, NOW-timedelta(minutes=30, seconds=1))
    assert is_event_guard_active(guard, NOW-timedelta(minutes=30))
    released = replace(guard, published_at=NOW.isoformat())
    assert is_event_guard_active(released, NOW+timedelta(minutes=14, seconds=59))
    assert not is_event_guard_active(released, NOW+timedelta(minutes=15))


def test_dart_provider_locally_filters_provider_future_missing_and_bad_dates(monkeypatch):
    from tradingagents.dataflows import opendart
    monkeypatch.setattr(opendart, "_resolve_corp_code", lambda symbol: ("corp", "005930"))
    monkeypatch.setattr(opendart, "_get_opendart_key", lambda: "fixture")
    rows = [{"rcept_dt": value, "rcept_no": str(index), "report_nm": "report"} for index, value in enumerate(
        ["20200101", "20200102", "20210101", "bad", None, "20990101", "20200231"])]
    response = SimpleNamespace(raise_for_status=lambda: None, json=lambda: {"status": "000", "list": rows})
    monkeypatch.setattr(opendart.requests, "get", lambda *args, **kwargs: response)
    result = opendart.fetch_disclosures_opendart("005930", "2020-01-01", "2020-01-02")
    assert [item.published_at.date().isoformat() for item in result] == ["2020-01-01", "2020-01-02"]
    rows.clear()
    assert opendart.fetch_disclosures_opendart("005930", "2020-01-01", "2020-01-02") == []


def test_work_receipt_preserves_closed_research_without_revalidating_execution(monkeypatch):
    close = "2026-10-16T20:00:00+00:00"
    sunday = datetime(2026, 10, 18, 10, tzinfo=timezone.utc)
    monkeypatch.setattr("tradingagents.work.freshness.latest_regular_session_context", lambda *args, **kwargs:
        {"session": {"phase": "closed", "is_open": False}, "verified_session": True, "latest_regular_close_at": close})
    bundle = {"market": "US", "strategy_table": [{"ticker": "AAPL", "interval": "1d", "market_data_asof": close}]}
    receipt = source_freshness_receipt({}, bundle, now=sunday, analysis_manifest={}, public=True)
    assert receipt["market_data_status"] == "STALE"
    assert receipt["research_market_data_status"] == "VALID"
    assert receipt["research_market_data_receipts"][0]["category"] == "LATEST_REGULAR_CLOSE_RESEARCH_ONLY"
    assert receipt["research_market_data_receipts"][0]["execution_eligible"] is False
    assert receipt["research_does_not_enable_execution"]
    bundle["strategy_table"][0]["market_data_asof"] = "2026-10-15T20:00:00+00:00"
    assert source_freshness_receipt({}, bundle, now=sunday, analysis_manifest={}, public=True)["research_market_data_status"] == "UNVERIFIED"


def test_sec_excludes_unverifiable_acceptance_time_even_when_filing_day_is_valid(monkeypatch):
    from tradingagents.dataflows import sec_edgar
    monkeypatch.setattr(sec_edgar, "_ticker_map", lambda day: {"AAPL": "0000320193"})
    recent = {"accessionNumber": ["valid", "missing", "bad", "naive", "future"],
              "filingDate": ["2020-01-01"] * 5,
              "acceptanceDateTime": ["2020-01-01T12:00:00Z", "", "bad", "2020-01-01T12:00:00", "2099-01-01T12:00:00Z"],
              "form": ["10-Q"] * 5}
    monkeypatch.setattr(sec_edgar, "_submissions", lambda *args: {"filings": {"recent": recent}})
    report = sec_edgar.get_disclosures_sec_edgar("AAPL", "2020-01-01", "2020-01-02")
    assert "valid-index.html" in report
    assert "missing-index.html" not in report and "bad-index.html" not in report
    assert "naive-index.html" not in report and "future-index.html" not in report


def test_event_guard_exact_fields_survive_archived_runner_shim():
    from tradingagents.scheduled.runner import _ExecutionContractShim
    guard = EventGuard(scheduled_at=NOW.isoformat(), known_at=(NOW-timedelta(hours=1)).isoformat(),
        event_id="event", event_version_id="v1", market_timezone="America/New_York", minutes_before_event=10,
        minutes_after_publication=20, first_seen_at=(NOW-timedelta(minutes=10)).isoformat(),
        first_seen_cooldown_minutes=60, exact_event_time_known=False, is_amended=True)
    payload = replace(contract(), event_guard=guard).to_dict()
    assert _ExecutionContractShim(payload).to_contract().event_guard == guard


def test_calendar_context_uses_completed_closes_and_repository_holiday_overlay(monkeypatch):
    import pandas as pd
    from tradingagents.scheduled import market_calendar
    schedule = pd.DataFrame({"close": pd.to_datetime(["2026-07-16T06:30:00Z", "2026-07-17T06:30:00Z", "2026-07-20T06:30:00Z"])},
                            index=pd.to_datetime(["2026-07-16", "2026-07-17", "2026-07-20"]))
    monkeypatch.setitem(sys.modules, "exchange_calendars", SimpleNamespace(get_calendar=lambda name: SimpleNamespace(schedule=schedule)))
    monkeypatch.setattr(market_calendar, "market_session_state", lambda **kwargs:
        {"phase": "closed", "is_open": False, "source": "exchange_calendars"})
    context = latest_regular_session_context("KR", as_of="2026-07-18T10:00:00Z")
    assert context["verified_session"]
    assert context["latest_regular_close_at"] == "2026-07-16T06:30:00+00:00"
    monkeypatch.setattr(market_calendar, "market_session_state", lambda **kwargs:
        {"phase": "unknown", "is_open": False, "source": "weekday_clock_fallback"})
    assert not latest_regular_session_context("KR", as_of="2026-07-18T10:00:00Z")["verified_session"]


def test_event_board_source_aliases_and_repeated_replay_keep_original_ingestion():
    original = event()
    board = build_event_timeline([original], analysis_as_of=NOW)
    row = board["events"][0]
    assert row["event_time"] is None
    assert row["ingested_at"] == row["observed_at"] == original["observed_at"].replace("Z", "+00:00")
    assert row["evaluated_at"] == NOW.isoformat()
    replay = build_event_timeline([row], analysis_as_of=NOW-timedelta(hours=1))
    assert replay["events"][0]["ingested_at"] == row["ingested_at"]
    assert replay["events"][0]["evaluated_at"] == (NOW-timedelta(hours=1)).isoformat()
    for changes in ({"ingested_at": NOW.isoformat()}, {"event_time": NOW.isoformat()},
                    {"timestamp_envelope": {"observed_at": NOW.isoformat()}}):
        result = build_event_timeline([event(**changes)], analysis_as_of=NOW)
        assert not result["events"] and result["rejected"][0]["reason"] == "TIMESTAMP_ALIAS_CONFLICT"


def test_future_event_and_amendment_do_not_change_entire_earlier_board():
    baseline = build_event_timeline([event()], analysis_as_of=NOW)
    future = event(version_id="future-correction", supersedes_version_id="a1", status="corrected",
        published_at=(NOW+timedelta(hours=1)).isoformat(), known_at=(NOW+timedelta(hours=1)).isoformat(),
        observed_at=(NOW+timedelta(hours=1, minutes=1)).isoformat())
    entirely_new = event(event_id="future-new-event", version_id="future-new-version",
        observed_at=(NOW+timedelta(days=1)).isoformat())
    assert build_event_timeline([event(), future, entirely_new], analysis_as_of=NOW) == baseline


def test_sec_disclosure_without_schedule_and_concurrent_guards_block_entry_only():
    from tradingagents.execution.contract_builder import build_execution_contract
    published = NOW-timedelta(minutes=5)
    sec_original = event(event_id="sec8k", version_id="sec-v1", event_type="disclosure", provider="sec_edgar",
        status="published", scheduled_at=None, published_at=(NOW-timedelta(minutes=20)).isoformat(),
        known_at=(NOW-timedelta(minutes=20)).isoformat(), observed_at=(NOW-timedelta(minutes=19)).isoformat())
    sec_amended = {**sec_original, "version_id": "sec-v2", "supersedes_version_id": "sec-v1", "status": "corrected",
        "published_at": published.isoformat(), "known_at": published.isoformat(), "observed_at": (published+timedelta(seconds=1)).isoformat()}
    dart = event(event_id="dart", version_id="dart-v1", event_type="disclosure", status="detected", scheduled_at=None,
        first_seen_at=(NOW-timedelta(minutes=25)).isoformat(), exact_event_time_known=False,
        known_at=(NOW-timedelta(minutes=25)).isoformat(), observed_at=(NOW-timedelta(minutes=24)).isoformat())
    scheduled = event(event_id="earnings", version_id="earnings-v1", scheduled_at=(NOW+timedelta(minutes=70)).isoformat())
    decision = {"rating": "BUY", "portfolio_stance": "BULLISH", "entry_action": "STARTER", "risk_action": "HOLD",
        "setup_quality": "COMPELLING", "confidence": .8, "time_horizon": "short", "entry_logic": "breakout",
        "exit_logic": "invalidate", "position_sizing": "starter", "risk_limits": "1R", "catalysts": [],
        "invalidators": [], "watchlist_triggers": [], "data_coverage": {},
        "execution_levels": {"earliest_pilot_time_local": "09:30", "levels": [{"level_type": "BREAKOUT", "price": 100, "confirmation": "intraday"}]}}
    c = build_execution_contract(ticker="AAPL", analysis_payload={"finished_at": NOW.isoformat(),
        "decision": json.dumps(decision), "event_records": [sec_original, sec_amended, dart, scheduled]})
    windows = [c.event_guard.to_dict(), *c.event_guard.guarded_events]
    sec_window = next(row for row in windows if row.get("event_id") == "sec8k")
    assert sec_window["published_at"] == published.isoformat() and sec_window["scheduled_at"] is None
    assert sec_window["event_version_id"] == "sec-v2" and sec_window["is_amended"]
    for minutes, blocked in ((0, True), (6, True), (11, False), (45, True)):
        at = NOW+timedelta(minutes=minutes)
        assert is_event_guard_active(c.event_guard, at, analysis_as_of=c.analysis_asof) is blocked
        update = evaluate_execution_state(c, replace(market(), asof=at.isoformat()), now=at, max_data_age_seconds=600)
        assert (update.decision_now.value == "NONE") is blocked
    at = NOW+timedelta(minutes=6)
    protected = evaluate_execution_state(replace(c, invalid_if_intraday_below=100),
        replace(market(), asof=at.isoformat()), now=at, max_data_age_seconds=600)
    assert protected.decision_now.value == "EXIT_NOW"


@pytest.mark.parametrize("age,eligible", [(599, True), (600, False), (601, False), (-1, False)])
def test_actionable_notification_uses_same_strict_quote_clock(age, eligible):
    from tradingagents.notifications.telegram import _row_is_fresh_immediate
    row = {"market_data_asof": (NOW-timedelta(seconds=age)).isoformat(), "quality": {
        "generated_in_current_run": True, "execution_ready": True, "row_mode": "IMMEDIATE", "freshness_class": "FRESH"}}
    assert _row_is_fresh_immediate(row, reference_time=NOW) is eligible
    row["market_data_asof"] = "2026-10-16T14:00:00"
    assert not _row_is_fresh_immediate(row, reference_time=NOW)
