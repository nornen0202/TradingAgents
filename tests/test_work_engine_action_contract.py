from copy import deepcopy
from datetime import datetime

import pytest

from tests.scheduled.test_strategy_action_readiness import build
from tradingagents.work.packet import _compact_market_row, _apply_market_row_validity
from tradingagents.work.runtime import WorkRuntimeError, _validate_report_execution_gate


@pytest.mark.parametrize("now,conditional,readiness,action", [
    ("NONE", "NONE", "RESEARCH_ONLY", None),
    ("NONE", "STARTER", "WAIT_FOR_TRIGGER", "신규 매수"),
    ("NONE", "ADD", "WAIT_FOR_TRIGGER", "추가 매수"),
    ("NONE", "REDUCE", "WAIT_FOR_TRIGGER", "비중 축소"),
    ("NONE", "EXIT", "WAIT_FOR_TRIGGER", "전량 매도"),
    ("STARTER_NOW", "NONE", "READY_NOW", "신규 매수"),
    ("REDUCE_NOW", "NONE", "READY_NOW", "비중 축소"),
    ("EXIT_NOW", "NONE", "READY_NOW", "전량 매도"),
])
def test_packet_preserves_engine_phase_and_action_without_raw_code_payload(now, conditional, readiness, action):
    original = build(now, conditional, held=True)["strategy_table"][0]
    before = deepcopy(original)
    row = _compact_market_row(original, 1)
    execution = row["execution"]
    assert execution["readiness"] == readiness
    assert execution["action_now"] == (action if readiness == "READY_NOW" else None)
    assert execution["action_if_triggered"] == (action if readiness == "WAIT_FOR_TRIGGER" else None)
    assert "raw_codes" not in row and original == before
    assert _compact_market_row(row, 1)["execution"] == execution
    checked_at = datetime.fromisoformat("2026-07-10T12:01:00-04:00")
    _apply_market_row_validity({"strategy_table": [row]}, now=checked_at)
    _validate_report_execution_gate({"execution": deepcopy(row["execution"])}, row,
                                   ticker="NVDA", now=checked_at)


@pytest.mark.parametrize("conditional", ["NONE", "STARTER", "REDUCE", "EXIT"])
def test_packet_validator_rejects_immediate_promotion_of_engine_none(conditional):
    row = _compact_market_row(build("NONE", conditional, held=True)["strategy_table"][0], 1)
    report = {"execution": {**row["execution"], "readiness": "READY_NOW", "action_now": "신규 매수", "action_if_triggered": None}}
    with pytest.raises(WorkRuntimeError, match="promotes packet"):
        _validate_report_execution_gate(report, row, ticker="NVDA", now=datetime.fromisoformat("2026-07-10T12:01:00-04:00"))


def test_packet_risk_exit_cannot_be_rewritten_as_conditional_buy():
    row = _compact_market_row(build("NONE", "EXIT", held=True)["strategy_table"][0], 1)
    report = {"execution": {**row["execution"], "action_if_triggered": "신규 매수"}}
    with pytest.raises(WorkRuntimeError, match="engine action"):
        _validate_report_execution_gate(report, row, ticker="NVDA", now=datetime.fromisoformat("2026-07-10T12:01:00-04:00"))


@pytest.mark.parametrize("case", ["expired", "downgraded", "contradictory", "missing_raw"])
def test_packet_engine_contract_does_not_upgrade_unverified_inputs(case):
    original = build("STARTER_NOW", "NONE")["strategy_table"][0]
    if case == "expired":
        _apply_market_row_validity({"strategy_table": [original]}, now=datetime.fromisoformat("2026-07-11T12:01:00-04:00"))
    elif case == "downgraded":
        original["execution"] = {"readiness": "NEEDS_LIVE_RECHECK", "blockers": ["extra_check"]}
    elif case == "contradictory":
        original["quality"]["action_ready"] = False
    else:
        original.pop("raw_codes")
    execution = _compact_market_row(original, 1)["execution"]
    assert execution["readiness"] == "NEEDS_LIVE_RECHECK"
    assert execution["action_now"] is None and execution["action_if_triggered"] is None


def test_legacy_raw_engine_none_also_prevents_immediate_packet():
    original = build("NONE", "NONE")["strategy_table"][0]
    for field in ("data_ready", "action_ready", "action_status"):
        original["quality"].pop(field)
    assert _compact_market_row(original, 1)["execution"]["readiness"] == "RESEARCH_ONLY"
