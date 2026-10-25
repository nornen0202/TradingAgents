from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from tests.test_chatgpt_work import _structured_report, _write_market_run, _write_youtube_market_evidence
from tradingagents.dataflows.research_evidence import REQUIRED_METHODS, SCHEMA as TOOL_SCHEMA
from tradingagents.work import packet as packets
from tradingagents.work.market_report_context import (
    bounded_file, empty_baseline, make_context, research_receipts, validate_context,
)
from tradingagents.work.runtime import (
    WorkRuntime, WorkRuntimeError, _load_last_acked_market_baseline,
    _validate_market_context_report, _validate_report_packet_coverage, validate_work_report,
)
from tradingagents.work.site import _publish_latest_report

NOW = datetime(2026, 7, 14, 14, 5, tzinfo=timezone.utc)


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def setup(tmp_path, market="us", *, run_id="first"):
    archive = tmp_path / "archive"
    _write_market_run(archive, run_id=run_id, market=market, started_at="2026-07-14T14:00:00Z")
    return WorkRuntime(tmp_path / "runtime"), archive


def prepare(runtime, archive, market="us", *, now=NOW, opt=True):
    return runtime.prepare(market, archive_dir=archive, now=now, report_context_v1=opt)


def packet(prepared):
    return json.loads(Path(prepared["packet_path"]).read_text(encoding="utf-8"))


def draft(prepared, *, at=None):
    result = _structured_report(prepared)
    context = packet(prepared)["body"].get("report_context")
    if context:
        result["source_summary"]["report_context_receipt"] = context
    if at:
        result["generated_at"] = at.isoformat()
    return result


def publish(runtime, archive, prepared, *, at=NOW + timedelta(minutes=1)):
    return runtime.publish(prepared["surface"], prepared["event_id"], prepared["source_sha256"],
        report_markdown="# 검증 보고서\n\n원래 판단과 현재 실행 조건을 구분합니다.",
        structured_report=draft(prepared, at=at), archive_dir=archive, now=at)


def acked(tmp_path, *, opt=True):
    runtime, archive = setup(tmp_path)
    first = prepare(runtime, archive, opt=opt)
    report = publish(runtime, archive, first)
    runtime.acknowledge("us", first["event_id"], now=NOW + timedelta(minutes=2))
    return runtime, archive, first, report


def next_source(archive, *, market="us", run_id="second", at="2026-07-14T14:08:00Z"):
    return _write_market_run(archive, run_id=run_id, market=market, started_at=at)


def test_explicit_opt_in_preserves_legacy_packets_prompts_and_advisory(tmp_path):
    runtime, archive = setup(tmp_path)
    legacy = packets.build_surface_packet("us", archive_dir=archive, now=NOW)
    explicit_false = packets.build_surface_packet("us", archive_dir=archive, now=NOW, report_context_v1=False)
    assert legacy == explicit_false
    old = prepare(runtime, archive, opt=False)
    old_bytes = Path(old["packet_path"]).read_bytes()
    new = prepare(runtime, archive)
    assert packet(old)["prompt_contract_version"] == "market-work-v13-us"
    assert packet(new)["prompt_contract_version"] == "market-work-v14-us"
    assert Path(old["packet_path"]).read_bytes() == old_bytes
    assert "report_context" not in packet(old)["body"]
    for surface in ("kr", "us"):
        assert packets.prompt_path(surface, packets.MARKET_CONTEXT_CONTRACTS[surface]).read_bytes().startswith(packets.prompt_path(surface).read_bytes())
    for surface in ("youtube", "prism"):
        with pytest.raises(ValueError, match="market surfaces"):
            packets.build_surface_packet(surface, archive_dir=archive, now=NOW, report_context_v1=True)


def test_no_ack_resume_and_self_ack_do_not_ratchet_event(tmp_path):
    runtime, archive = setup(tmp_path)
    first = prepare(runtime, archive)
    first_bytes = Path(first["packet_path"]).read_bytes()
    context = packet(first)["body"]["report_context"]
    assert context["prior_ack"]["status"] == "NO_PRIOR_ACK"
    assert context["first_unmet"]["stage"] == "RESEARCH"
    assert prepare(runtime, archive)["result"] == "RESUME"
    publish(runtime, archive, first)
    runtime.acknowledge("us", first["event_id"], now=NOW + timedelta(minutes=2))
    after = prepare(runtime, archive, now=NOW + timedelta(minutes=3))
    assert after["result"] == "NOOP" and after["event_id"] == first["event_id"]
    assert Path(first["packet_path"]).read_bytes() == first_bytes


@pytest.mark.parametrize("acked_first", [False, True])
def test_equal_upstream_does_not_bypass_immutable_tamper(tmp_path, acked_first):
    runtime, archive = setup(tmp_path)
    first = prepare(runtime, archive)
    if acked_first:
        publish(runtime, archive, first)
        runtime.acknowledge("us", first["event_id"], now=NOW + timedelta(minutes=2))
    raw = packet(first)
    raw["body"]["report_context"]["market"] = "KR"
    write_json(Path(first["packet_path"]), raw)
    with pytest.raises(WorkRuntimeError):
        prepare(runtime, archive, now=NOW + timedelta(minutes=3))


def test_previous_exact_ack_is_used_when_latest_pointer_is_newer_pending(tmp_path):
    runtime, archive, first, report = acked(tmp_path)
    next_source(archive)
    second = prepare(runtime, archive, now=NOW + timedelta(minutes=4))
    context = packet(second)["body"]["report_context"]
    assert context["prior_ack"]["status"] == "VERIFIED"
    assert context["prior_ack"]["report_sha256"] == report["report_sha256"]
    assert context["comparison_status"] == "VERIFIED" and context["changes"]
    assert context["changes"][0]["fields"] == ["market_data_asof"]
    publish(runtime, archive, second, at=NOW + timedelta(minutes=5))
    state = json.loads(runtime.state_path.read_text(encoding="utf-8"))["surfaces"]["us"]
    baseline, previous = _load_last_acked_market_baseline(runtime, state, surface="us", archive_dir=archive,
                                                         cutoff=NOW + timedelta(minutes=6))
    assert baseline["status"] == "VERIFIED" and previous["event_id"] == first["event_id"]
    validate_context(json.loads(json.dumps(context, sort_keys=True)))


def test_unrelated_surface_revision_does_not_invalidate_surface_ack(tmp_path):
    runtime, archive, _, _ = acked(tmp_path)
    state = json.loads(runtime.state_path.read_text(encoding="utf-8"))
    state["revision"] += 10
    write_json(runtime.state_path, state)
    next_source(archive)
    context = packet(prepare(runtime, archive, now=NOW + timedelta(minutes=4)))["body"]["report_context"]
    assert context["prior_ack"]["ledger_revision"] == 1
    assert context["prior_ack"]["status"] == "VERIFIED"


def test_legacy_ack_without_surface_revision_is_not_promoted_to_verified(tmp_path):
    runtime, archive, _, _ = acked(tmp_path, opt=False)
    next_source(archive)
    context = packet(prepare(runtime, archive, now=NOW + timedelta(minutes=4)))["body"]["report_context"]
    assert context["prior_ack"]["status"] == "UNVERIFIED"
    assert context["comparison_status"] == "NOT_COMPARABLE" and context["changes"] == []


def test_changed_workflow_hash_is_not_comparable_even_with_same_version(tmp_path, monkeypatch):
    runtime, archive, first, _ = acked(tmp_path)
    original = packets.workflow_contract_hashes("us", packets.MARKET_CONTEXT_CONTRACTS["us"])
    monkeypatch.setattr(packets, "workflow_contract_hashes", lambda *args: {**original, "prompt_sha256": "f" * 64})
    second = prepare(runtime, archive, now=NOW + timedelta(minutes=3))
    context = packet(second)["body"]["report_context"]
    assert second["result"] == "NEW" and second["event_id"] != first["event_id"]
    assert context["prior_ack"]["status"] == "VERIFIED"
    assert context["comparison_status"] == "NOT_COMPARABLE" and context["changes"] == []


@pytest.mark.parametrize("case", ["future_ack", "naive_ack", "bad_ack", "missing_ack", "status", "wrong_surface", "source", "revision", "revision_tamper", "report", "packet", "report_path", "report_future", "report_naive", "ledger_duplicate"])
def test_invalid_prior_ack_is_explicitly_unverified_without_fallback(tmp_path, case):
    runtime, archive, first, published = acked(tmp_path)
    state = json.loads(runtime.state_path.read_text(encoding="utf-8"))
    us = state["surfaces"]["us"]
    ledger = [json.loads(line) for line in runtime.ledger_path.read_text().splitlines()]
    ack = next(row for row in ledger if row["event"] == "acknowledged")
    if case in {"future_ack", "naive_ack", "bad_ack", "missing_ack"}:
        value = {"future_ack": "2026-07-15T14:00:00Z", "naive_ack": "2026-07-14T14:07:00", "bad_ack": "invalid", "missing_ack": None}[case]
        us["last_acked_at"] = value
        ack["at"] = value
    elif case == "status":
        us["last_acked_status"] = ack["status"] = "received"
    elif case == "wrong_surface":
        ack["surface"] = "kr"
    elif case == "source":
        ack["source_sha256"] = "a" * 64
    elif case == "revision":
        ack["state_revision"] = True
    elif case == "revision_tamper":
        ack["state_revision"] = 777
    elif case == "report":
        us["last_acked_report_sha256"] = "b" * 64
    elif case == "report_path":
        us["last_acked_report_path"] = str(tmp_path / "outside.json")
    elif case == "packet":
        Path(first["packet_path"]).write_text("{}")
    elif case in {"report_future", "report_naive"}:
        path = Path(published["report_path"])
        report = json.loads(path.read_text(encoding="utf-8"))
        # published_at is not part of report material: prior reader still must
        # enforce aware <= ACK instead of trusting a valid content hash.
        report["published_at"] = "2026-07-15T14:00:00Z" if case == "report_future" else "2026-07-14T14:06:00"
        write_json(path, report)
    elif case == "ledger_duplicate":
        ledger.append(copy.deepcopy(ack))
    write_json(runtime.state_path, state)
    runtime.ledger_path.write_text("\n".join(json.dumps(row) for row in ledger) + "\n")
    next_source(archive)
    context = packet(prepare(runtime, archive, now=NOW + timedelta(minutes=4)))["body"]["report_context"]
    assert context["prior_ack"] == empty_baseline("UNVERIFIED")
    assert context["comparison_status"] == "NOT_COMPARABLE" and context["changes"] == []


@pytest.mark.parametrize("field", ["actual_cost", "account_id", "owner", "position_quantity", "url", "raw_tool_args"])
def test_context_closed_schema_rejects_private_or_unknown_llm_keys(tmp_path, field):
    runtime, archive = setup(tmp_path)
    prepared = prepare(runtime, archive)
    report = draft(prepared)
    report["source_summary"]["report_context_receipt"][field] = "private"
    with pytest.raises(WorkRuntimeError, match="public context|unsupported or private"):
        _validate_market_context_report(report, surface="us", contract=packets.MARKET_CONTEXT_CONTRACTS["us"])


def test_receipt_exact_copy_and_new_action_cap_do_not_affect_old_contract(tmp_path):
    runtime, archive = setup(tmp_path)
    prepared = prepare(runtime, archive)
    report = draft(prepared)
    report["source_summary"]["report_context_receipt"]["data_status"] = "STALE"
    with pytest.raises(WorkRuntimeError, match="exactly match"):
        _validate_report_packet_coverage(report, packet(prepared), now=NOW + timedelta(minutes=1))
    report = draft(prepared)
    report["top_actions"] = [{}, {}, {}, {}]
    with pytest.raises(WorkRuntimeError, match="at most 3"):
        _validate_market_context_report(report, surface="us", contract=packets.MARKET_CONTEXT_CONTRACTS["us"])
    _validate_market_context_report(report, surface="us", contract=packets.PROMPT_CONTRACTS["us"])
    report["source_summary"].pop("report_context_receipt")
    with pytest.raises(WorkRuntimeError, match="public context|unsupported or private"):
        _validate_market_context_report(report, surface="us", contract=packets.MARKET_CONTEXT_CONTRACTS["us"])


def research_fixture(tmp_path):
    archive = tmp_path / "research"
    run_dir = archive / "runs" / "2026" / "original"
    run_dir.mkdir(parents=True)
    decision = {"rating": "HOLD", "portfolio_stance": "BULLISH", "entry_action": "WAIT", "risk_action": "HOLD",
        "confidence": 0.7, "time_horizon": "medium", "entry_logic": "Wait for verified breakout.",
        "exit_logic": "Exit below support.", "position_sizing": "Existing limit.", "risk_limits": "Existing risk cap.",
        "catalysts": ["Earnings"], "invalidators": ["Support lost"], "watchlist_triggers": ["Breakout"]}
    outcomes, events = [], []
    for index, method in enumerate(sorted(REQUIRED_METHODS)):
        identity = f"{index:032x}"
        outcomes.append({"request_id": identity, "method": method, "status": "available", "result_sha256": "a" * 64,
                         "started_at": "2026-07-14T13:01:00Z", "completed_at": "2026-07-14T13:02:00Z"})
        events.append({"request_id": identity, "method": method, "status": "success", "fallback": False,
                       "args": {"account_id": "NEVER_TRANSMIT"}, "url": "https://private.invalid"})
    analysis = {"ticker": "NVDA", "status": "success", "decision": json.dumps(decision),
                "started_at": "2026-07-14T13:00:00Z", "finished_at": "2026-07-14T13:03:00Z",
                "trade_date": "2026-07-13", "analysis_date": "2026-07-14", "quality_flags": [],
                "metrics": {"llm_fallback_calls": 0},
                "tool_telemetry": {"request_schema": TOOL_SCHEMA, "request_outcomes": outcomes, "events": events}}
    summary = {key: copy.deepcopy(value) for key, value in analysis.items() if key not in {"quality_flags", "metrics", "tool_telemetry"}}
    summary["artifacts"] = {"analysis_json": "analysis.json"}
    manifest = {"run_id": "original", "settings": {"market": "US", "run_mode": "full"},
                "started_at": "2026-07-14T13:00:00Z", "finished_at": "2026-07-14T13:04:00Z", "tickers": [summary]}
    write_json(run_dir / "analysis.json", analysis)
    write_json(run_dir / "run.json", manifest)
    return archive, run_dir, manifest, analysis


def assess(archive, manifest):
    return research_receipts(archive, manifest, [{"ticker": "NVDA"}], market="us", now=NOW)[0]


def test_original_canonical_wait_is_not_conflated_with_fallback(tmp_path):
    archive, run_dir, manifest, analysis = research_fixture(tmp_path)
    proof = assess(archive, manifest)
    assert proof["status"] == "COMPLETE" and proof["decision_parse"] == "VALIDATED"
    assert proof["entry_action"] == "WAIT" and proof["risk_action"] == "HOLD"
    assert proof["analysis_sha256"] == hashlib.sha256((run_dir / "analysis.json").read_bytes()).hexdigest()
    assert "NEVER_TRANSMIT" not in json.dumps(proof) and "url" not in proof
    analysis["tool_telemetry"]["request_outcomes"][0]["status"] = "unavailable"
    write_json(run_dir / "analysis.json", analysis)
    proof = assess(archive, manifest)
    assert proof["status"] == "REQUIRED_EVIDENCE_MISSING" and proof["entry_action"] == "WAIT"


@pytest.mark.parametrize("case", ["empty", "legacy", "future_tool", "missing_tool_date", "bad_tool_date", "future_analysis", "naive_analysis", "wrong_ticker", "decision_mismatch", "missing_analysis", "tamper_hash", "fallback", "parse_invalid", "quality_flag", "metric_missing", "inverted_dates", "wrong_market_day", "future_day", "invalid_day"])
def test_original_receipts_fail_closed_without_raw_payload_leak(tmp_path, case):
    archive, run_dir, manifest, analysis = research_fixture(tmp_path)
    if case == "empty":
        analysis["tool_telemetry"]["request_outcomes"] = []
    elif case == "legacy":
        analysis["tool_telemetry"] = {}
    elif case in {"future_tool", "missing_tool_date", "bad_tool_date"}:
        analysis["tool_telemetry"]["request_outcomes"][0]["completed_at"] = {"future_tool": "2026-07-15T13:02:00Z", "missing_tool_date": None, "bad_tool_date": "broken"}[case]
    elif case in {"future_analysis", "naive_analysis"}:
        analysis["finished_at"] = "2026-07-15T13:03:00Z" if case == "future_analysis" else "2026-07-14T13:03:00"
        manifest["tickers"][0]["finished_at"] = analysis["finished_at"]
    elif case == "wrong_ticker":
        analysis["ticker"] = "005930.KS"
    elif case == "decision_mismatch":
        analysis["decision"] = "{}"
    elif case == "tamper_hash":
        manifest["tickers"][0]["research_reuse"] = {"artifact_sha256": {"analysis_json": "0" * 64}}
    elif case in {"fallback", "parse_invalid"}:
        value = json.loads(analysis["decision"])
        value["fallback_reason"] = "provider unavailable" if case == "fallback" else None
        if case == "parse_invalid":
            value["confidence"] = "invalid"
        analysis["decision"] = manifest["tickers"][0]["decision"] = json.dumps(value)
    elif case == "quality_flag":
        analysis["quality_flags"] = ["decision_unvalidated"]
    elif case == "metric_missing":
        analysis["metrics"] = {}
    elif case in {"inverted_dates", "wrong_market_day", "future_day", "invalid_day"}:
        analysis["analysis_date"] = {"inverted_dates": "2026-07-13", "wrong_market_day": "2026-07-12",
                                     "future_day": "2026-07-15", "invalid_day": "2026-02-30"}[case]
        analysis["trade_date"] = "2026-07-14"
        for key in ("analysis_date", "trade_date"):
            manifest["tickers"][0][key] = analysis[key]
    write_json(run_dir / "analysis.json", analysis)
    write_json(run_dir / "run.json", manifest)
    if case == "missing_analysis":
        (run_dir / "analysis.json").unlink()
    proof = assess(archive, manifest)
    assert proof["status"] == "UNVERIFIED"
    if case in {"fallback", "quality_flag"}:
        assert proof["decision_parse"] == "FALLBACK"
    assert "NEVER_TRANSMIT" not in json.dumps(proof)


@pytest.mark.parametrize("stage", ["DATA", "RESEARCH", "DECISION", "PRIVATE_OPERATIONS"])
def test_first_unmet_uses_only_proven_public_stages(stage):
    body = {"kind": "market", "market": "US", "current": {
        "freshness_receipt": {"market_data_status": "STALE" if stage == "DATA" else "FRESH"},
        "research_readiness": [{"ticker": "NVDA", "status": "UNVERIFIED" if stage == "RESEARCH" else "COMPLETE",
                                "decision_parse": "VALIDATED", "entry_action": "WAIT", "risk_action": "HOLD", "missing_required_methods": [],
                                "reason": "VERIFIED", "decision_sha256": "a" * 64, "analysis_sha256": "b" * 64,
                                "manifest_sha256": "c" * 64, "finished_at": "2026-07-14T13:03:00Z"}],
        "bundle": {"strategy_table": [{"ticker": "NVDA", "is_held": True, "owner": "private", "actual_cost": 1,
            "market_data_asof": "2026-07-14T14:00:00Z",
            "thesis": {"stance": "HOLD", "decision_sha256": "a" * 64, "analysis_asof": "2026-07-14T13:03:00Z"},
            "execution": {"readiness": "RESEARCH_ONLY" if stage == "DECISION" else "READY_NOW"}}]}}}
    context = make_context(body, market="us", cutoff=NOW, baseline=empty_baseline(), prior_body=None, comparable=False)
    assert context["first_unmet"]["stage"] == stage
    assert context["private_execution_cost_status"] == "NOT_PROVIDED"
    assert all(key not in json.dumps(context) for key in ("is_held", '"owner"', "actual_cost"))


@pytest.mark.parametrize("field,value", [("decision_sha256", "0" * 64), ("analysis_asof", None), ("analysis_asof", "2026-07-14T14:01:00Z")])
def test_original_analysis_proof_cannot_bless_a_different_current_thesis(tmp_path, field, value):
    archive, _, manifest, _ = research_fixture(tmp_path)
    proof = assess(archive, manifest)
    thesis = {"stance": "BUY", "decision_sha256": proof["decision_sha256"], "analysis_asof": proof["finished_at"]}
    thesis[field] = value
    body = {"kind": "market", "market": "US", "current": {"freshness_receipt": {"market_data_status": "FRESH"},
        "research_readiness": [proof], "bundle": {"strategy_table": [{"ticker": "NVDA", "thesis": thesis,
            "market_data_asof": "2026-07-14T14:00:00Z",
            "execution": {"readiness": "READY_NOW"}}]}}}
    context = make_context(body, market="us", cutoff=NOW, baseline=empty_baseline(), prior_body=None, comparable=False)
    row = context["market_inputs"][0]
    assert row["research_status"] == "UNVERIFIED" and row["decision_parse"] == "UNVERIFIED"
    assert row["research_reason"] == "ORIGINAL_DECISION_MISMATCH" and row["entry_action"] is None
    assert context["first_unmet"]["stage"] == "RESEARCH"


def test_market_mismatch_and_bounded_path_escape_are_rejected(tmp_path):
    body = {"kind": "market", "market": "US", "current": {"bundle": {"strategy_table": [{"ticker": "005930.KS"}]}}}
    with pytest.raises(ValueError, match="ticker market"):
        make_context(body, market="us", cutoff=NOW, baseline=empty_baseline(), prior_body=None, comparable=False)
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside.json"
    outside.write_text("{}")
    with pytest.raises(ValueError, match="outside"):
        bounded_file(root, root / ".." / "outside.json")


def test_kr_original_dates_use_market_day_instead_of_serialized_utc_date(tmp_path):
    archive, run_dir, manifest, analysis = research_fixture(tmp_path)
    # Original KR research starts Jul 14 00:00 KST, serialized as Jul 13 UTC.
    analysis.update(ticker="005930.KS", started_at="2026-07-13T15:00:00Z", finished_at="2026-07-13T15:03:00Z")
    for outcome in analysis["tool_telemetry"]["request_outcomes"]:
        outcome.update(started_at="2026-07-13T15:01:00Z", completed_at="2026-07-13T15:02:00Z")
    manifest["settings"]["market"] = "KR"
    manifest.update(started_at="2026-07-13T15:00:00Z", finished_at="2026-07-13T15:04:00Z")
    for key in ("ticker", "started_at", "finished_at"):
        manifest["tickers"][0][key] = analysis[key]
    write_json(run_dir / "analysis.json", analysis)
    write_json(run_dir / "run.json", manifest)
    proof = research_receipts(archive, manifest, [{"ticker": "005930.KS"}], market="kr", now=NOW)[0]
    assert proof["status"] == "COMPLETE"


@pytest.mark.parametrize("asof", [None, "broken", "2026-07-14T14:00:00", "2026-07-15T14:00:00Z"])
def test_unverified_market_clock_cannot_claim_public_data_ready(asof):
    body = {"kind": "market", "market": "US", "current": {"freshness_receipt": {"market_data_status": "FRESH"},
        "bundle": {"strategy_table": [{"ticker": "NVDA", "market_data_asof": asof}]}}}
    context = make_context(body, market="us", cutoff=NOW, baseline=empty_baseline(), prior_body=None, comparable=False)
    assert context["first_unmet"]["stage"] == "DATA" and context["data_status"] != "FRESH"


@pytest.mark.parametrize("offset", [-1, 2])
def test_new_report_must_be_generated_after_comparison_before_publication(tmp_path, offset):
    runtime, archive = setup(tmp_path)
    prepared = prepare(runtime, archive)
    report = draft(prepared, at=NOW + timedelta(minutes=offset))
    with pytest.raises(WorkRuntimeError, match="cutoff|public context"):
        _validate_report_packet_coverage(report, packet(prepared), now=NOW + timedelta(minutes=1))


@pytest.mark.parametrize("target", ["prior", "row", "change"])
def test_nested_private_fields_are_not_an_extensible_report_context(target, tmp_path):
    runtime, archive, _, _ = acked(tmp_path)
    next_source(archive)
    prepared = prepare(runtime, archive, now=NOW + timedelta(minutes=4))
    report = draft(prepared, at=NOW + timedelta(minutes=5))
    context = report["source_summary"]["report_context_receipt"]
    if target == "prior":
        context["prior_ack"]["account_id"] = "private"
    elif target == "row":
        context["market_inputs"][0]["actual_cost"] = 0
    else:
        context["changes"][0]["before"]["owner"] = "private"
    with pytest.raises(WorkRuntimeError, match="public context|unsupported or private"):
        _validate_market_context_report(report, surface="us", contract=packets.MARKET_CONTEXT_CONTRACTS["us"])


@pytest.mark.parametrize("opt", [False, True])
def test_standalone_report_validation_preserves_original_bytes(tmp_path, opt):
    runtime, archive = setup(tmp_path)
    prepared = prepare(runtime, archive, opt=opt)
    published = publish(runtime, archive, prepared)
    path = Path(published["report_path"])
    original = path.read_bytes()
    report = json.loads(original)
    validate_work_report(report)
    assert (archive / "work-reports/us/latest.json").read_bytes() == original
    assert path.read_bytes() == original
    public = tmp_path / "public"
    _publish_latest_report(root=public, archive_dir=archive, surface="us", url_prefix="https://example.invalid")
    assert (public / "us/report/latest.json").read_bytes() == original
    assert (public / "us/report/latest.md").read_bytes() == report["report_markdown"].encode("utf-8")


@pytest.mark.parametrize("location", ["source_summary", "root", "strategy", "nested_rationale"])
def test_private_cost_receipt_cannot_bypass_context_at_another_location(tmp_path, location):
    runtime, archive = setup(tmp_path)
    prepared = prepare(runtime, archive)
    report = draft(prepared)
    private = {"owner": "private-owner-example", "actual_cost": 999, "net_pnl": 77}
    target = report["source_summary"] if location == "source_summary" else report if location == "root" else report["strategies"][0]
    if location == "nested_rationale":
        report["strategies"][0]["thesis"]["rationale"] = [private]
    else:
        target["private_cost_receipt"] = private
    with pytest.raises(WorkRuntimeError, match="unsupported or private"):
        runtime.publish("us", prepared["event_id"], prepared["source_sha256"], report_markdown="# Public report",
                        structured_report=report, archive_dir=archive, now=NOW + timedelta(minutes=1))
    assert not (archive / "work-reports/us/latest.json").exists()


def test_new_contract_retains_legitimate_external_evidence_stance_change(tmp_path):
    archive, youtube = tmp_path / "archive", tmp_path / "youtube"
    _write_market_run(archive, run_id="stance-change", market="us", started_at="2026-07-14T14:00:00Z", row_mode="CONDITIONAL")
    _write_youtube_market_evidence(youtube, video_id="nvda-evidence", ticker="NVDA")
    runtime = WorkRuntime(tmp_path / "runtime")
    prepared = runtime.prepare("us", archive_dir=archive, youtube_archive_dir=youtube,
                               prism_archive_dir=tmp_path / "prism", now=NOW, report_context_v1=True)
    report = draft(prepared)
    strategy = report["strategies"][0]
    original = strategy["thesis"]["stance"]
    assert original == "HOLD"
    strategy["thesis"]["stance"] = "BUY"
    strategy["thesis"]["stance_change"] = {"from": original, "to": "BUY", "reason": "Matched public evidence strengthens demand outlook",
        "evidence": [{"source": "youtube", "event_key": "nvda-evidence", "finding": "New public demand evidence supports the research view"}]}
    result = runtime.publish("us", prepared["event_id"], prepared["source_sha256"], report_markdown="# Bound public research change",
                             structured_report=report, archive_dir=archive, now=NOW + timedelta(minutes=1))
    assert result["status"] == "PUBLISHED"
