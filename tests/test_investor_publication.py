"""Investor delivery remains useful without turning reference prices into orders."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

import pytest

from tests.test_chatgpt_work import _write_market_run
from tradingagents.work.investor_policy import investment_plan, price_zones, project_investor_body
from tradingagents.work.investor_draft import compose_investor_draft
from tradingagents.work.runtime import WorkRuntime, WorkRuntimeError, validate_work_report

AT = datetime(2026, 7, 17, 14, tzinfo=timezone.utc)


def thesis():
    return {"stance": "BUY", "analysis_asof": AT.isoformat(), "horizon": "short", "confidence": .7,
            "entry_conditions": ["98~102 지지 확인 후 분할 매수 검토"],
            "invalidation_conditions": ["종가 95 하회"], "invalidation_action": "신규 진입 취소, 보유 위험 축소 검토",
            "position_sizing": "전체 계획 손실은 기존 한도 이내",
            "execution_levels": {"levels": [{"label": "지지 구간", "level_type": "PULLBACK", "low": 98, "high": 102,
                                             "source_text": "98~102 달러", "confirmation": "close"}]}}


def source(tmp_path, *, analysis=AT.isoformat(), quote=AT.isoformat(), partial=False):
    run = _write_market_run(tmp_path, run_id="full", market="us", started_at=AT.isoformat())
    path = run / "run.json"
    manifest = json.loads(path.read_text())
    manifest.update(status="partial_failure" if partial else "success", finished_at=AT.isoformat())
    manifest["settings"]["run_mode"] = "full"
    manifest["tickers"] = [{"ticker": "NVDA", "status": "success", "finished_at": analysis, "trade_date": "2026-07-17"}]
    if partial:
        manifest["tickers"].append({"ticker": "AMD", "status": "failed"})
    path.write_text(json.dumps(manifest), encoding="utf-8")
    path = run / "decision_bundle_v2.json"
    bundle = json.loads(path.read_text())
    bundle["strategy_table"][0].update(thesis=thesis(), market_data_asof=quote)
    bundle["strategy_table"][0]["thesis"]["analysis_asof"] = analysis
    path.write_text(json.dumps(bundle), encoding="utf-8")
    return run


@pytest.mark.parametrize("delay", [timedelta(minutes=12), timedelta(hours=48), timedelta(days=9), timedelta(days=120)])
@pytest.mark.parametrize("partial", [False, True])
def test_closed_delayed_and_partial_reports_publish_ack_without_broker(tmp_path, monkeypatch, delay, partial):
    from tradingagents.work import pre_report
    monkeypatch.setattr(pre_report, "prepare_market_report", lambda *a, **k: pytest.fail("no producer refresh"))
    archive = tmp_path / "archive"
    run = source(archive, partial=partial)
    original = {p.name: p.read_bytes() for p in run.iterdir()}
    runtime = WorkRuntime(tmp_path / "runtime")
    prepared = runtime.prepare("us", archive_dir=archive, now=AT + delay, investor_report=True)
    packet = json.loads(Path(prepared["packet_path"]).read_text(encoding="utf-8"))
    markdown, draft = compose_investor_draft(packet, now=AT + delay)
    # A slow draft does not need a new producer or a new immutable event.
    result = runtime.publish("us", prepared["event_id"], prepared["source_sha256"], archive_dir=archive,
                             report_markdown=markdown, structured_report=draft, now=AT + delay + timedelta(hours=1))
    assert result["status"] == "PUBLISHED"
    report = json.loads(Path(result["report_path"]).read_text(encoding="utf-8"))
    validate_work_report(report)
    assert "98–102" in report["report_markdown"]
    assert draft["strategies"][0]["thesis"]["stance"] == "BUY"
    assert draft["strategies"][0]["execution"]["action_now"] is None
    assert draft["strategies"][0]["investment_plan"]["execution_eligible"] is False
    assert draft["source_summary"]["freshness_receipt"] == packet["body"]["current"]["freshness_receipt"]
    ack = runtime.acknowledge("us", prepared["event_id"], now=AT + delay + timedelta(hours=1))
    assert ack["event_id"] == prepared["event_id"]
    assert {p.name: p.read_bytes() for p in run.iterdir()} == original


@pytest.mark.parametrize("clock", [None, "bad", "2026-07-17T14:00:00", "2026-07-19T14:00:00Z"])
def test_bad_analysis_is_excluded_per_row_not_used_as_evidence(tmp_path, clock):
    source(tmp_path / "archive", analysis=clock)
    prepared = WorkRuntime(tmp_path / "runtime").prepare("us", archive_dir=tmp_path / "archive",
                                                        now=AT + timedelta(days=1), investor_report=True)
    packet = json.loads(Path(prepared["packet_path"]).read_text(encoding="utf-8"))
    row = packet["body"]["current"]["bundle"]["strategy_table"][0]
    assert row["thesis"]["stance"] == "RESEARCH"
    assert row["investment_plan"]["status"] == "DATA_NEEDED"
    assert "98~102" not in json.dumps(row, ensure_ascii=False)
    markdown, draft = compose_investor_draft(packet, now=AT + timedelta(days=1))
    assert "98–102" not in markdown
    assert draft["strategies"][0]["investment_plan"]["price_zones"] == []


@pytest.mark.parametrize("clock", [None, "bad", "2026-07-17T14:00:00", "2026-07-19T14:00:00Z"])
def test_bad_quote_does_not_erase_independently_dated_thesis(tmp_path, clock):
    source(tmp_path / "archive", quote=clock)
    prepared = WorkRuntime(tmp_path / "runtime").prepare("us", archive_dir=tmp_path / "archive",
                                                        now=AT + timedelta(days=1), investor_report=True)
    packet = json.loads(Path(prepared["packet_path"]).read_text(encoding="utf-8"))
    row = packet["body"]["current"]["bundle"]["strategy_table"][0]
    assert "last_price" not in row
    assert row["thesis"]["stance"] == "BUY"
    assert row["investment_plan"]["price_zones"][0]["low"] == 98


@pytest.mark.parametrize("tamper", ["order", "zone", "window", "policy", "future_generation"])
def test_investor_plan_cannot_change_bound_levels_or_enable_orders(tmp_path, tamper):
    source(tmp_path / "archive")
    runtime = WorkRuntime(tmp_path / "runtime")
    prepared = runtime.prepare("us", archive_dir=tmp_path / "archive", now=AT, investor_report=True)
    packet = json.loads(Path(prepared["packet_path"]).read_text(encoding="utf-8"))
    markdown, draft = compose_investor_draft(packet, now=AT)
    row = draft["strategies"][0]
    if tamper == "order":
        row["execution"].update(readiness="READY_NOW", action_now="BUY")
    elif tamper == "zone":
        row["investment_plan"]["price_zones"][0]["low"] = 50
    elif tamper == "window":
        row["investment_plan"]["review_window"]["review_by"] = "2099-01-01T00:00:00Z"
    elif tamper == "policy":
        draft["source_summary"].pop("publication_policy")
    else:
        draft["generated_at"] = (AT + timedelta(days=1)).isoformat()
    with pytest.raises(WorkRuntimeError):
        runtime.publish("us", prepared["event_id"], prepared["source_sha256"], archive_dir=tmp_path / "archive",
                        report_markdown=markdown, structured_report=draft, now=AT)
    assert not (tmp_path / "archive/work-reports/us/latest.json").exists()


def test_price_tolerance_never_widens_risk_threshold_or_overrides_source_range():
    original = thesis()
    original["execution_levels"]["levels"] += [
        {"level_type": "BREAKOUT", "price": 110}, {"level_type": "STOP_LOSS", "price": 95},
        {"level_type": "SUPPORT", "price": 210, "low": 30, "high": 60, "source_text": "30~60분 확인"},
        {"level_type": "PULLBACK", "low": float("nan"), "high": 100},
    ]
    before = deepcopy(original)
    zones, excluded = price_zones(original)
    assert [(z["low"], z["high"]) for z in zones] == [(98, 102), (110, 111.1), (95, 95)]
    assert len(excluded) == 2
    assert original["execution_levels"]["levels"][:3] == before["execution_levels"]["levels"][:3]


def test_risk_reduction_does_not_demand_buy_funding_or_volume():
    row = {"thesis": {**thesis(), "stance": "HOLD", "risk_action": "REDUCE_RISK"}}
    plan = investment_plan(row, now=AT)
    assert plan["purpose"] == "RISK_REDUCTION"
    assert "현금" not in str(plan["before_acting"])
    assert "매도 가능" in str(plan["before_acting"])
    assert plan["risk_action"] == "REDUCE_RISK"


def test_projection_is_pure_and_empty_input_does_not_create_state(tmp_path):
    body = {"current": {"bundle": {"strategy_table": [{"ticker": "X", "thesis": thesis()}]}}}
    original = deepcopy(body)
    projected = project_investor_body(body, now=AT)
    assert body == original and projected != original
    runtime = WorkRuntime(tmp_path / "runtime")
    with pytest.raises(WorkRuntimeError, match="No completed"):
        runtime.prepare("us", archive_dir=tmp_path / "empty", now=AT, investor_report=True)
    assert not runtime.state_path.exists()


def test_fundamental_invalidator_is_not_rejected_for_missing_price_keyword(tmp_path):
    run = source(tmp_path / "archive")
    path = run / "decision_bundle_v2.json"
    data = json.loads(path.read_text())
    condition = "운전자본 유입 반전이 구조적인 현금창출력 약점을 드러내거나 인수 조달·통합 부담이 기대 수익을 훼손하는 경우"
    data["strategy_table"][0]["thesis"]["invalidation_conditions"] = [condition]
    path.write_text(json.dumps(data), encoding="utf-8")
    prepared = WorkRuntime(tmp_path / "runtime").prepare("us", archive_dir=tmp_path / "archive", now=AT, investor_report=True)
    packet = json.loads(Path(prepared["packet_path"]).read_text(encoding="utf-8"))
    markdown, draft = compose_investor_draft(packet, now=AT)
    assert condition in markdown
    draft["strategies"][0]["thesis"]["invalidation_conditions"] = ["임의로 새 무효화 조건 변경"]
    from tradingagents.work.investor_policy import validate_investor_draft
    with pytest.raises(WorkRuntimeError, match="source conditions"):
        validate_investor_draft(draft, packet, now=AT)


def test_cli_defaults_to_investor_without_refresh(tmp_path, monkeypatch, capsys):
    import sys
    from tradingagents.work import __main__ as cli
    from tradingagents.work import pre_report
    source(tmp_path / "archive")
    monkeypatch.setattr(pre_report, "prepare_market_report", lambda *a, **k: pytest.fail("unexpected broker call"))
    monkeypatch.setattr(sys, "argv", ["work", "--runtime-dir", str(tmp_path / "runtime"), "prepare",
                                     "--surface", "us", "--archive-dir", str(tmp_path / "archive")])
    assert cli.main() == 0
    prepared = json.loads(capsys.readouterr().out)
    packet = json.loads(Path(prepared["packet_path"]).read_text(encoding="utf-8"))
    assert packet["body"]["publication_policy"]["profile"] == "investor"


def test_report_budget_measures_content_not_indentation(tmp_path):
    from tradingagents.work.packet import sha256_json
    from tradingagents.work.runtime import _report_material
    source(tmp_path / "archive")
    runtime = WorkRuntime(tmp_path / "runtime")
    prepared = runtime.prepare("us", archive_dir=tmp_path / "archive", now=AT, investor_report=True)
    packet = json.loads(Path(prepared["packet_path"]).read_text(encoding="utf-8"))
    md, draft = compose_investor_draft(packet, now=AT)
    result = runtime.publish("us", prepared["event_id"], prepared["source_sha256"], report_markdown=md,
                             structured_report=draft, archive_dir=tmp_path / "archive", now=AT)
    report = json.loads(Path(result["report_path"]).read_text(encoding="utf-8"))
    compact = len(json.dumps(report, ensure_ascii=False, separators=(",", ":")))
    assert len(json.dumps(report, ensure_ascii=False, indent=2)) > compact
    validate_work_report(report, max_chars=compact)
    report["report_markdown"] += "x" * 100
    report["report_sha256"] = sha256_json(_report_material(report))
    report["report_id"] = f"us:{report['report_sha256'][:32]}"
    with pytest.raises(WorkRuntimeError, match="too large"):
        validate_work_report(report, max_chars=compact)
