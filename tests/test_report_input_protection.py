from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path

import pytest

from tests.test_investor_publication import AT, source, thesis
from tests.test_work_market_report_context import research_fixture
from tradingagents.work.freshness import source_freshness_receipt
from tradingagents.work.investor_draft import compose_investor_draft
from tradingagents.work.investor_policy import PROTECTION_NOTICE, project_investor_body
from tradingagents.work.market_report_context import research_receipts
from tradingagents.work.packet import sha256_json
from tradingagents.work.runtime import WorkRuntime, WorkRuntimeError


NOW = datetime(2026, 11, 16, 14, 13, tzinfo=timezone.utc)
CLOSE = "2026-11-13T21:00:00Z"


@pytest.mark.parametrize("clock", [None, "bad", "2026-11-13", "2026-11-13T21:00:00", "2026-11-17T21:00:00Z", CLOSE])
def test_live_overlay_cannot_validate_original_research_clock(monkeypatch, clock):
    monkeypatch.setattr("tradingagents.work.freshness.latest_regular_session_context", lambda *a, **k: {
        "session": {"phase": "pre_open", "is_open": False}, "verified_session": True,
        "latest_regular_close_at": CLOSE})
    original = {"tickers": [{"ticker": "AAPL", "status": "success",
        "started_at": "2026-11-16T12:00:00Z", "finished_at": "2026-11-16T13:00:00Z",
        "execution_contract": {"ticker": "AAPL", "analysis_asof": "2026-11-16T13:00:00Z",
            "market_data_asof": clock, "level_basis": "daily_close"}}]}
    bundle = {"market": "US", "strategy_table": [{"ticker": "AAPL", "market_data_asof": NOW.isoformat(), "interval": "1d"}]}
    receipt = source_freshness_receipt({}, bundle, now=NOW, analysis_manifest=original, public=False)
    assert receipt["market_data_status"] == "FRESH"
    assert receipt["research_market_data_status"] == ("VALID" if clock == CLOSE else "UNVERIFIED")
    before = deepcopy(receipt["research_market_data_receipts"])
    bundle["strategy_table"][0]["market_data_asof"] = CLOSE
    assert source_freshness_receipt({}, bundle, now=NOW, analysis_manifest=original, public=False)["research_market_data_receipts"] == before
    assert before[0]["execution_eligible"] is False
    original["tickers"].append(deepcopy(original["tickers"][0]))
    assert source_freshness_receipt({}, bundle, now=NOW, analysis_manifest=original, public=False)["research_market_data_status"] == "UNVERIFIED"


def test_empty_research_is_not_recovered_by_fresh_quotes():
    bundle = {"market": "US", "strategy_table": [{"ticker": "AAPL", "market_data_asof": NOW.isoformat()}]}
    assert source_freshness_receipt({}, bundle, now=NOW, analysis_manifest={}, public=True)["research_market_data_status"] == "UNVERIFIED"
    bundle["strategy_table"] = []
    assert source_freshness_receipt({}, bundle, now=NOW, analysis_manifest={}, public=True)["research_market_data_status"] == "UNVERIFIED"


@pytest.mark.parametrize("damage", [None, "missing", "decision_mismatch", "future"])
def test_investor_research_status_requires_original_bound_evidence(tmp_path, damage):
    archive, run, manifest, analysis = research_fixture(tmp_path)
    now = datetime(2026, 7, 14, 14, tzinfo=timezone.utc)
    rows = [{"ticker": "NVDA", "thesis": {**thesis(), "analysis_asof": analysis["finished_at"],
        "decision_sha256": sha256_json(json.loads(analysis["decision"]))}}]
    if damage == "missing":
        (run / "analysis.json").unlink()
    elif damage == "decision_mismatch":
        rows[0]["thesis"]["decision_sha256"] = "b" * 64
    elif damage == "future":
        rows[0]["thesis"]["analysis_asof"] = "2026-07-15T13:00:00Z"
    body = {"kind": "market", "market": "US", "current": {
        "bundle": {"strategy_table": rows},
        "research_readiness": research_receipts(archive, manifest, rows, market="us", now=now)}}
    plan = project_investor_body(body, now=now)["current"]["bundle"]["strategy_table"][0]["investment_plan"]
    assert plan["research_verification"]["status"] == ("COMPLETE" if damage is None else "UNVERIFIED")
    assert plan["status"] == ("CONDITIONAL_PLAN" if damage is None else "DATA_NEEDED" if damage == "future" else "REVIEW_REQUIRED")
    assert plan["execution_eligible"] is False


@pytest.mark.parametrize("tamper", [None, "protection", "rechecks", "research"])
def test_publish_enforces_protection_and_live_reconciliation(tmp_path, tamper):
    archive = tmp_path / "archive"
    source(archive)
    runtime = WorkRuntime(tmp_path / "runtime")
    prepared = runtime.prepare("us", archive_dir=archive, now=AT, investor_report=True)
    packet = json.loads(Path(prepared["packet_path"]).read_text(encoding="utf-8"))
    _, draft = compose_investor_draft(packet, now=AT)
    plan = draft["strategies"][0]["investment_plan"]
    assert plan["existing_protection"] == "PRESERVE_STRICTER_RULES"
    assert any("미체결" in item for item in plan["before_acting"])
    if tamper == "protection":
        plan["existing_protection"] = "REPLACE_WITH_NEW_REPORT"
    elif tamper == "rechecks":
        plan["before_acting"] = []
    elif tamper == "research":
        plan["research_verification"]["status"] = "COMPLETE"
    kwargs = dict(archive_dir=archive, now=AT, structured_report=draft,
                  report_markdown="# 투자 계획\n\n원분석을 요약한 보고서입니다.")
    if tamper:
        with pytest.raises(WorkRuntimeError):
            runtime.publish("us", prepared["event_id"], prepared["source_sha256"], **kwargs)
        assert not (archive / "work-reports/us/latest.json").exists()
    else:
        result = runtime.publish("us", prepared["event_id"], prepared["source_sha256"], **kwargs)
        published = json.loads(Path(result["report_path"]).read_text(encoding="utf-8"))
        assert PROTECTION_NOTICE in published["report_markdown"]
        assert "연구 입력 검증 완료 0/1" in published["report_markdown"]
