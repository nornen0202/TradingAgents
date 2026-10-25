from concurrent.futures import ThreadPoolExecutor
from contextvars import copy_context
from copy import deepcopy
from datetime import datetime
import hashlib
import json
from types import SimpleNamespace

import pytest

from tradingagents.agents.utils import decision_provenance as trace
from tradingagents.agents.utils import decision_retry as retry
from tradingagents.schemas.decision import build_decision_output_instructions

PM = "portfolio manager final decision"
RM = "research manager investment plan"


def decision(**changes):
    value = {"rating": "HOLD", "portfolio_stance": "BULLISH", "entry_action": "WAIT",
             "setup_quality": "DEVELOPING", "confidence": .6, "time_horizon": "medium",
             "entry_logic": "Wait for evidence.", "exit_logic": "Respect support.",
             "position_sizing": "No new allocation.", "risk_limits": "Keep existing limits.",
             "catalysts": [], "invalidators": [], "watchlist_triggers": []}
    return json.dumps({**value, **changes})


class LLM:
    def __init__(self, *responses):
        self.responses = iter(responses)
        self.calls = 0

    def invoke(self, prompt):
        self.calls += 1
        value = next(self.responses)
        if isinstance(value, Exception):
            raise value
        return SimpleNamespace(content=value)


def invoke(session, llm, context=PM, **kwargs):
    with session.capture():
        response, normalized = retry.invoke_structured_decision_with_retry(llm, "fixture", context=context, **kwargs)
    session.bind_selected(normalized, {"final_trade_decision": normalized})
    return response, normalized, session.receipt()


def test_legacy_omissions_and_explicit_none_are_distinct_without_changing_calls():
    for explicit in (False, True):
        changes = {"conditional_entry_action": "NONE", "conditional_entry_valid_until": None} if explicit else {}
        raw = decision(**changes)
        llm = LLM(raw)
        _, normalized, receipt = invoke(trace.DecisionProvenanceSession("AAPL"), llm)
        event = receipt["events"][0]
        assert llm.calls == 1 and json.loads(normalized)["conditional_entry_action"] == "NONE"
        assert receipt["status"] == "RECORDED"
        assert event["parser_input_text_sha256"] == hashlib.sha256(raw.encode()).hexdigest()
        assert event["defaulted_fields"] == ([] if explicit else list(trace._FIELDS))
        assert event["conditional_fields"]["conditional_entry_valid_until"]["presence"] == ("EXPLICIT_NULL" if explicit else "ABSENT")
        assert receipt["selected_binding"]["binding_basis"] == "EXACT_NORMALIZED_TEXT"


def test_common_example_names_both_existing_fields_without_fixed_none_action():
    prompt = build_decision_output_instructions("fixture")
    assert '"conditional_entry_action":"NONE | STARTER | ADD"' in prompt
    assert '"conditional_entry_valid_until"' in prompt
    assert "otherwise use NONE and JSON null" in prompt


def conditional():
    return decision(conditional_entry_action="STARTER", conditional_entry_valid_until="2026-10-26T10:45:00+09:00",
                    risk_action="NONE", execution_levels={"levels": [{"label": "trigger", "level_type": "BREAKOUT",
                        "price": 100, "confirmation": "intraday", "source_text": "observed trigger"}]})


def test_explicit_conditional_plan_keeps_original_tuple_and_aware_validity():
    llm = LLM(conditional())
    response, normalized, receipt = invoke(trace.DecisionProvenanceSession("AAPL"), llm)
    assert response.content == conditional() and llm.calls == 1
    assert json.loads(normalized)["conditional_entry_valid_until"] == "2026-10-26T10:45:00+09:00"
    assert receipt["events"][0]["defaulted_fields"] == []
    assert receipt["events"][0]["conditional_fields"]["conditional_entry_valid_until"]["valid_shape"] is True
    assert receipt["execution_authorized"] is False


def test_repair_and_structural_fallback_do_not_add_model_calls():
    llm = LLM('{"rating":"HOLD"}', decision())
    _, _, receipt = invoke(trace.DecisionProvenanceSession("AAPL"), llm)
    assert llm.calls == 2
    assert [(e["attempt"], e["outcome"]) for e in receipt["events"]] == [(0, "VALIDATION_REJECTED"), (1, "VALIDATED_REPAIR")]
    llm = LLM('{"rating":"HOLD"}', '{"rating":"HOLD"}')
    _, normalized, receipt = invoke(trace.DecisionProvenanceSession("AAPL"), llm, max_retries=1)
    assert llm.calls == 2 and json.loads(normalized)["risk_action_reason_codes"] == ["STRUCTURED_DECISION_INVALID"]
    assert receipt["events"][-1]["outcome"] == "STRUCTURAL_FALLBACK"
    assert receipt["selected_binding"]["selected_origin"] == "STRUCTURAL_FALLBACK"


def test_provider_failure_and_unknown_error_are_static_and_private():
    llm = LLM(RuntimeError("Timed out waiting for Codex app-server PRIVATE_RESPONSE"))
    _, _, receipt = invoke(trace.DecisionProvenanceSession("AAPL"), llm)
    assert llm.calls == 1 and receipt["events"][0]["outcome"] == "PROVIDER_FALLBACK"
    assert "PRIVATE_RESPONSE" not in json.dumps(receipt)
    session = trace.DecisionProvenanceSession("AAPL")
    with session.capture(), pytest.raises(RuntimeError, match="private authentication"):
        retry.invoke_structured_decision_with_retry(LLM(RuntimeError("private authentication")), "fixture", context=PM)
    assert session.receipt()["events"][0]["outcome"] == "PROVIDER_EXCEPTION"


def test_exact_existing_extractor_first_mapping_is_not_replaced_by_later_json():
    raw = '{"private":"NEVER_SAVE"}\n' + conditional()
    session = trace.DecisionProvenanceSession("AAPL")
    _, _, receipt = invoke(session, LLM(raw), max_retries=0)
    first = receipt["events"][0]
    assert first["candidate_status"] == "MAPPING"
    assert first["conditional_fields"]["conditional_entry_action"]["presence"] == "ABSENT"
    assert first["outcome"] == "VALIDATION_REJECTED"
    assert "NEVER_SAVE" not in json.dumps(receipt)


@pytest.mark.parametrize("value,kind", [(None, "NULL"), (False, "BOOLEAN"), (0, "NUMBER"), ([], "ARRAY"), ({}, "OBJECT"), ("NONE", "STRING")])
def test_only_presence_type_and_shape_are_retained(value, kind):
    session = trace.DecisionProvenanceSession("AAPL")
    with session.capture():
        trace.record_decision_input(PM, 0, "VALIDATION_REJECTED", text=decision(conditional_entry_action=value))
    field = session.receipt()["events"][0]["conditional_fields"]["conditional_entry_action"]
    assert field["type"] == kind and "value" not in field
    assert field["valid_shape"] is (value == "NONE")


def test_shared_copied_context_and_nested_ticker_isolation():
    outer = trace.DecisionProvenanceSession("AAPL")
    inner = trace.DecisionProvenanceSession("000660.KS")
    with outer.capture():
        with ThreadPoolExecutor(max_workers=1) as pool:
            pool.submit(copy_context().run, retry.invoke_structured_decision_with_retry,
                        LLM(decision()), "fixture", context=RM).result()
        with inner.capture():
            retry.invoke_structured_decision_with_retry(LLM(decision()), "fixture", context=PM)
        retry.invoke_structured_decision_with_retry(LLM(decision()), "fixture", context=PM)
    assert [e["stage"] for e in outer.receipt()["events"]] == ["RESEARCH_MANAGER", "PORTFOLIO_MANAGER"]
    assert len(inner.receipt()["events"]) == 1
    retry.invoke_structured_decision_with_retry(LLM(decision()), "fixture", context=PM)
    assert len(outer.receipt()["events"]) == 2 and trace._ACTIVE.get() is None


def test_trace_overflow_and_capture_failure_are_unverified_without_call_changes(monkeypatch):
    session = trace.DecisionProvenanceSession("AAPL")
    session.recorder.max_events = 1
    llm = LLM('{"rating":"HOLD"}', decision())
    _, _, receipt = invoke(session, llm)
    assert llm.calls == 2 and receipt["status"] == "UNVERIFIED" and receipt["overflow_count"] == 1
    session = trace.DecisionProvenanceSession("AAPL")
    monkeypatch.setattr(session.recorder, "add", lambda *a, **k: (_ for _ in ()).throw(ValueError("PRIVATE_TRACE_FAILURE")))
    _, normalized, receipt = invoke(session, LLM(decision()))
    assert json.loads(normalized)["entry_action"] == "WAIT" and receipt["status"] == "UNVERIFIED"
    assert "PRIVATE_TRACE_FAILURE" not in json.dumps(receipt)


@pytest.mark.parametrize("method", ["activate", "reset", "snapshot"])
def test_trace_lifecycle_failure_never_changes_decision_and_always_resets(monkeypatch, method):
    session = trace.DecisionProvenanceSession("AAPL")
    monkeypatch.setattr(session.recorder, method, lambda *a: (_ for _ in ()).throw(RuntimeError("PRIVATE")))
    _, normalized, receipt = invoke(session, LLM(decision()))
    assert json.loads(normalized)["entry_action"] == "WAIT" and receipt["status"] == "UNVERIFIED"
    assert trace._ACTIVE.get() is None and "PRIVATE" not in json.dumps(receipt)


def test_trace_factory_failure_does_not_write_into_inherited_ticker(monkeypatch):
    outer = trace.DecisionProvenanceSession("AAPL")
    with outer.capture():
        monkeypatch.setattr(trace, "DecisionProvenanceRecorder", lambda *a: (_ for _ in ()).throw(RuntimeError("PRIVATE")))
        inner = trace.DecisionProvenanceSession("000660.KS")
        _, _, receipt = invoke(inner, LLM(decision()))
        assert receipt["status"] == "UNVERIFIED" and outer.receipt()["events"] == []
    assert trace._ACTIVE.get() is None


def test_whitespace_localized_narrative_and_machine_projection_are_distinct():
    session = trace.DecisionProvenanceSession("AAPL")
    _, normalized, _ = invoke(session, LLM(decision()))
    localized = json.loads(normalized)
    localized["entry_logic"] = "확인을 기다린다."
    selected = json.dumps(localized, ensure_ascii=False)
    session.bind_selected(selected, {"final_trade_decision": selected})
    receipt = session.receipt()
    assert receipt["status"] == "RECORDED"
    assert receipt["selected_binding"]["binding_basis"] == "MACHINE_PROJECTION_ONLY_POST_LOCALIZATION"
    assert receipt["selected_binding"]["full_decision_text_equal"] is False
    assert receipt["selected_binding"]["selected_machine_projection_matches"] is True
    assert receipt["full_translation_faithfulness_verified"] is False


@pytest.mark.parametrize("change", ["price", "volume", "expiry", "risk_plan"])
def test_localized_machine_changes_cannot_bind_as_same_projection(change):
    session = trace.DecisionProvenanceSession("AAPL")
    _, normalized, _ = invoke(session, LLM(conditional()))
    altered = json.loads(normalized)
    if change == "price":
        altered["execution_levels"]["levels"][0]["price"] = 101
    elif change == "volume":
        altered["execution_levels"]["min_relative_volume"] = 9
    elif change == "expiry":
        altered["conditional_entry_valid_until"] = "2026-10-26T11:00:00+09:00"
    else:
        altered["profit_taking_plan"]["keep_core_fraction"] = .33
    text = json.dumps(altered)
    session.bind_selected(text, {"final_trade_decision": text})
    assert session.receipt()["status"] == "UNVERIFIED"
    assert session.receipt()["selected_binding"]["selected_machine_projection_matches"] is False


def test_ambiguous_same_stage_is_not_assumed_to_be_latest_and_RM_fallback_binds_RM():
    session = trace.DecisionProvenanceSession("AAPL")
    with session.capture():
        for _ in range(2):
            _, normalized = retry.invoke_structured_decision_with_retry(LLM(decision()), "fixture", context=PM)
    session.bind_selected(normalized, {"final_trade_decision": normalized})
    assert session.receipt()["selected_binding"]["binding_basis"] == "AMBIGUOUS"
    assert session.receipt()["status"] == "UNVERIFIED"
    session = trace.DecisionProvenanceSession("AAPL")
    with session.capture():
        _, normalized = retry.invoke_structured_decision_with_retry(LLM(decision()), "fixture", context=RM)
    session.bind_selected(normalized, {"final_trade_decision": "invalid", "investment_debate_state": {"judge_decision": normalized}})
    assert session.receipt()["selected_binding"]["selected_stage"] == "RESEARCH_MANAGER"
    assert session.receipt()["status"] == "RECORDED"


def test_unknown_context_and_oversized_input_never_copy_private_values():
    session = trace.DecisionProvenanceSession("AAPL")
    with session.capture():
        trace.record_decision_input("PRIVATE_CONTEXT", 0, "VALIDATION_REJECTED", text="PRIVATE" * trace.MAX_INPUT_CHARS)
    assert session.receipt()["status"] == "UNVERIFIED"
    assert "PRIVATE" not in json.dumps(session.receipt())


def test_snapshot_copies_are_isolated():
    session = trace.DecisionProvenanceSession("AAPL")
    _, _, receipt = invoke(session, LLM(decision()))
    original = deepcopy(receipt)
    receipt["events"].clear()
    assert session.receipt() == original


@pytest.mark.parametrize("expiry,valid", [(None, True), ("2026-10-26", False),
                                         ("bad", False), (False, False), (42, False),
                                         ("2099-01-01T10:30:00+09:00", True)])
def test_expiry_shape_is_not_a_freshness_or_order_authority(expiry, valid):
    session = trace.DecisionProvenanceSession("AAPL")
    with session.capture():
        trace.record_decision_input(PM, 0, "VALIDATION_REJECTED",
            text=decision(conditional_entry_action="NONE", conditional_entry_valid_until=expiry))
    receipt = session.receipt()
    event = receipt["events"][0]
    assert event["conditional_fields"]["conditional_entry_valid_until"]["valid_shape"] is valid
    assert datetime.fromisoformat(event["recorded_at"]).utcoffset() is not None
    assert receipt["execution_authorized"] is False


def test_metadata_sink_exception_cannot_interrupt_existing_model_tuple(monkeypatch):
    session = trace.DecisionProvenanceSession("AAPL")
    monkeypatch.setattr(retry, "_record_decision_input", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("PRIVATE")))
    llm = LLM(decision())
    response, normalized, receipt = invoke(session, llm)
    assert llm.calls == 1 and response.content == decision()
    assert json.loads(normalized)["entry_action"] == "WAIT"
    assert receipt["status"] == "UNVERIFIED" and "PRIVATE" not in json.dumps(receipt)
