import copy
import json
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

from tradingagents.agents.utils.decision_retry import invoke_structured_decision_with_retry
from tradingagents.execution.contract_builder import build_execution_contract
from tradingagents.execution.overlay import evaluate_execution_state
from tradingagents.schemas import ActionIfTriggered, IntradayMarketSnapshot, PriceLevel
from tradingagents.schemas.decision import (
    ExplicitPriceRangeConflictError,
    explicit_price_range_conflicts,
    parse_structured_decision,
)
from tradingagents.work import packet as work_packet
from tradingagents.work.runtime import WorkRuntimeError, _validate_report_execution_gate


def _level(**overrides):
    return {
        "label": "두 번째 저항 실패 확인선", "level_type": "TRIM",
        "price": 75200.0, "low": 75.0, "high": 75200.0, "currency": "KRW",
        "confirmation": "two_bar",
        "source_text": "75,200~75,700원 접근 후 75,200원 아래 완료된 5분봉 2개가 형성되면 축소한다.",
        **overrides,
    }


def _decision(level=None):
    return {
        "rating": "HOLD", "portfolio_stance": "NEUTRAL", "entry_action": "WAIT",
        "setup_quality": "DEVELOPING", "confidence": 0.6, "time_horizon": "short",
        "entry_logic": "확인 후 진입", "exit_logic": "지지 이탈 시 축소",
        "position_sizing": "소규모", "risk_limits": "지지선 재확인",
        "catalysts": [], "invalidators": [],
        "execution_levels": {"levels": [level or _level()]},
    }


def test_raw_conflicting_level_is_not_silently_dropped_or_repaired():
    decision = _decision()
    original = copy.deepcopy(decision)
    with pytest.raises(ExplicitPriceRangeConflictError, match=r"execution_levels.levels\[0\].*75, 75200.*75200, 75700"):
        parse_structured_decision(decision)
    assert decision == original


def test_conflicting_risk_level_cannot_fall_back_to_another_level():
    decision = _decision(_level(low=75200, high=75700))
    decision.update(risk_action="REDUCE_RISK", risk_action_level=_level())
    with pytest.raises(ExplicitPriceRangeConflictError, match="risk_action_level"):
        parse_structured_decision(decision)


@pytest.mark.parametrize("low,high", [(75200, 75700), (75200, 75200), (75300, 75500), (75700, 75200)])
def test_equal_contained_or_reversed_numeric_bounds_keep_existing_normalization(low, high):
    parsed = parse_structured_decision(_decision(_level(low=low, high=high)))
    assert len(parsed.execution_levels.levels) == 1
    assert (parsed.execution_levels.levels[0].low, parsed.execution_levels.levels[0].high) == tuple(sorted((low, high)))


@pytest.mark.parametrize("bounds", [(74000, 74000), (74000, 74100)])
@pytest.mark.parametrize("spacing", [" ", ""])
def test_separate_confirmation_price_is_not_assumed_to_represent_the_source_range(bounds, spacing):
    level = _level(price=74000, low=bounds[0], high=bounds[1], source_text=f"75,200~75,700원 접근 후{spacing}74,000원 아래 5분봉 2개 확인")
    assert explicit_price_range_conflicts(_decision(level)) == []
    parsed = parse_structured_decision(_decision(level)).execution_levels.levels[0]
    assert (parsed.low, parsed.high) == bounds


def test_point_bounds_outside_source_range_remain_a_legacy_threshold():
    level = _level(price=74000, low=74000, high=74000)
    assert explicit_price_range_conflicts(_decision(level)) == []


@pytest.mark.parametrize("text,currency,low,high", [
    ("75,200원~75,700구간", "KRW", 75, 75200),
    ("KRW 75,200~75,700 구간", "KRW", 75, 75200),
    ("USD 75~80 confirmed", "USD", 7.5, 75),
    ("usd75~USD80 confirmed", "USD", 7.5, 75),
    ("75,200~75,700원 접근 후 보유분 20~35% 축소", "KRW", 75, 75200),
    ("RSI 60~70, 75,200~75,700원 접근 후 RVOL 1~2 확인", "KRW", 75, 75200),
    ("09:00~10:00, 75,200~75,700원 구간에서 5~10분 관찰", "KRW", 75, 75200),
    ("75,200~75,700원 접근 후 20~35주 축소", "KRW", 75, 75200),
    ("2026-10-14, 75,200~75,700원 및 60~70 RSI 확인", "KRW", 75, 75200),
    ("USD75~80 분할 매수", "USD", 7.5, 75),
    ("75,200원~75,700 주가 구간", "KRW", 75, 75200),
])
def test_currency_prices_are_validated_independently_of_non_price_ranges(text, currency, low, high):
    level = _level(source_text=text, currency=currency, low=low, high=high)
    with pytest.raises(ExplicitPriceRangeConflictError):
        parse_structured_decision(_decision(level))
    level.update(low=75200 if currency == "KRW" else 75, high=75700 if currency == "KRW" else 80)
    assert explicit_price_range_conflicts(_decision(level)) == []


def test_iso_prefixed_separate_confirmation_price_preserves_threshold_bounds():
    level = _level(source_text="KRW 75,200~75,700 접근 후 KRW 74,000 아래 확인", low=74000, high=74100)
    assert explicit_price_range_conflicts(_decision(level)) == []


@pytest.mark.parametrize("text", ["$0.75–$0.80 confirmed", "0.75~0.80 USD 확인", "0.75달러~0.80달러 확인"])
def test_sub_dollar_us_ranges_are_not_rejected_by_absolute_price_heuristics(text):
    level = _level(price=0.78, low=0.75, high=0.80, currency="USD", source_text=text)
    assert explicit_price_range_conflicts(_decision(level)) == []
    assert parse_structured_decision(_decision(level)).execution_levels.levels[0].low == 0.75
    level["low"] = 0.075
    assert explicit_price_range_conflicts(_decision(level))


@pytest.mark.parametrize("overrides", [
    {"source_text": "75,200~75,700원 또는 73,000~74,000원"},
    {"source_text": "75,200~75,700원 또는 73,000~74,000"},
    {"source_text": "USD75~80 또는 USD70~72", "currency": "USD"},
    {"source_text": "KRW 75,200~USD 75,700"},
    {"source_text": "75,200~75,700"},
    {"source_text": "RSI 75~80 및 RVOL 1~2 확인"},
    {"source_text": "75~80% 축소"},
    {"source_text": "75~80주 축소"},
    {"source_text": "75.2~75.7천원 확인"},
    {"source_text": "$1–$2 million", "low": 1000000, "high": 2000000, "currency": "USD"},
    {"source_text": "$75~80% 확인", "currency": "USD"},
    {"source_text": "2026-10-14 09:00~10:00 확인"},
    {"currency": "USD"},
    {"low": None}, {"high": None}, {"low": "75"}, {"low": True},
    {"low": float("nan")}, {"low": float("inf")},
])
def test_ambiguous_or_non_numeric_bounds_remain_outside_narrow_validator(overrides):
    assert explicit_price_range_conflicts(_decision(_level(**overrides))) == []


class _LLM:
    def __init__(self, decisions):
        self.responses = [json.dumps(decision, ensure_ascii=False) for decision in decisions]
        self.calls = []

    def invoke(self, prompt):
        self.calls.append(prompt)
        return SimpleNamespace(content=self.responses.pop(0))


def test_conflicting_raw_range_enters_existing_bounded_repair():
    llm = _LLM([_decision(), _decision(_level(low=75200, high=75700))])
    _, result = invoke_structured_decision_with_retry(
        llm, [{"role": "user", "content": "Return decision JSON"}], context="final decision",
    )
    assert len(llm.calls) == 2
    assert "structured_price_range_conflict" in llm.calls[1][-1]["content"]
    assert json.loads(result)["execution_levels"]["levels"][0]["low"] == 75200


def test_conflict_repair_exhaustion_is_no_trade_with_original_retry_budget():
    llm = _LLM([_decision()] * 4)
    _, result = invoke_structured_decision_with_retry(llm, "Return JSON", context="final decision")
    decision = json.loads(result)
    assert len(llm.calls) == 4
    assert decision["rating"] == "NO_TRADE"
    assert decision["entry_action"] == "WAIT"
    assert decision["risk_action"] == "NONE"
    assert not decision["execution_levels"]["levels"]


def _market(now):
    return IntradayMarketSnapshot(
        ticker="034020.KS", asof=now.isoformat(), provider="kis_quote", interval="5m",
        last_price=76000, session_vwap=75000, day_high=77000, day_low=75000,
        volume=1000, avg20_daily_volume=1000, relative_volume=2, market_session="regular",
    )


def test_saved_decision_rebuild_uses_observable_watch_only_fallback_without_throwing():
    payload = {"decision": json.dumps(_decision()), "finished_at": "2026-10-14T01:00:00Z", "trade_date": "2026-10-13"}
    before = copy.deepcopy(payload)
    contract = build_execution_contract(ticker="034020.KS", analysis_payload=payload)
    assert payload == before
    assert contract.action_if_triggered == ActionIfTriggered.NONE
    assert contract.reason_codes == ("fallback_contract", "structured_price_range_conflict")
    assert "execution_levels.levels[0]" in contract.notes[-1]
    now = datetime(2026, 10, 14, 1, 5, tzinfo=timezone.utc)
    update = evaluate_execution_state(contract, _market(now), now=now, max_data_age_seconds=180)
    assert update.decision_now.value == "NONE"
    assert update.decision_if_triggered == ActionIfTriggered.NONE
    assert update.reason_codes == ("structured_price_range_conflict",)


@pytest.mark.parametrize("location", ["structured_levels", "risk_action_level"])
@pytest.mark.parametrize("source_text", [
    _level()["source_text"], "75,200원~75,700구간", "KRW 75,200~75,700 구간",
    "75,200~75,700원 접근 후 보유분 20~35% 축소",
])
def test_copied_legacy_contract_is_blocked_even_with_fresh_quote(location, source_text):
    from tradingagents.scheduled.runner import _ExecutionContractShim

    payload = {"decision": json.dumps(_decision(_level(low=75200, high=75700)))}
    contract = build_execution_contract(ticker="034020.KS", analysis_payload=payload)
    bad_level = PriceLevel(**_level(source_text=source_text))
    contract = replace(contract, action_if_triggered=ActionIfTriggered.STARTER,
                       **{location: (bad_level,) if location == "structured_levels" else bad_level})
    archived = contract.to_dict()
    contract = _ExecutionContractShim(copy.deepcopy(archived)).to_contract()
    before = contract.to_dict()
    now = datetime(2026, 10, 14, 1, 5, tzinfo=timezone.utc)
    update = evaluate_execution_state(contract, _market(now), now=now, max_data_age_seconds=180)
    assert contract.to_dict() == before  # Same contract bootstrap copies from an immutable archive.
    assert update.decision_state.value == "DEGRADED"
    assert update.data_health == "UNAVAILABLE"
    assert update.decision_now.value == "NONE"
    assert update.decision_if_triggered == ActionIfTriggered.NONE
    assert update.reason_codes == ("structured_price_range_conflict",)


@pytest.mark.parametrize("action_name,delta", [("ADD", 1_000_000), ("REDUCE_RISK", -1_000_000)])
@pytest.mark.parametrize("phase", ["NOW", "CONDITIONAL"])
def test_private_mobile_and_trade_plan_cannot_restore_conflicting_archived_allocation(monkeypatch, action_name, delta, phase):
    from tradingagents.scheduled.mobile_site import _private_market_payload
    from tradingagents.scheduled.trade_plan import build_trade_plan

    now = datetime(2026, 10, 14, 1, 5, tzinfo=timezone.utc)
    decision = _decision()
    decision["conditional_entry_action"] = "STARTER"  # Must not re-create a conditional buy.
    row = {
        "ticker": "034020.KS", "is_held": True,
        "market_data_asof": "2026-10-14T01:00:00Z", "thesis": decision,
        "quality": {"row_mode": "IMMEDIATE", "execution_ready": True},
        "strategy_code": "BUY_NOW",
    }
    good = copy.deepcopy(row)
    good.update(ticker="OTHER", thesis=_decision(_level(level_type="PULLBACK", low=75200, high=75700)))
    bundle = {"strategy_table": [row, good], "quality": {"decision_ready": True}}
    work_packet._apply_market_row_validity(bundle, now=now)
    action = {
        "canonical_ticker": "034020.KS", "action_now": action_name if phase == "NOW" else "HOLD",
        "action_if_triggered": action_name if phase == "CONDITIONAL" else "NONE",
        "delta_krw_now": delta if phase == "NOW" else 0,
        "delta_krw_if_triggered": delta if phase == "CONDITIONAL" else 0,
        "target_weight_now": 0.3, "target_weight_if_triggered": 0.4,
        "strategy_state": "READY", "execution_feasibility_now": "executable",
        "gate_reasons": ["prior_gate"],
    }
    good_action = dict(action, canonical_ticker="OTHER", action_now="ADD", delta_krw_now=1_000_000)
    report = {"actions": [action, good_action]}
    before = copy.deepcopy(report)
    monkeypatch.setattr(work_packet, "load_json", lambda path: report)
    overlay = work_packet._local_private_overlay(
        Path("."), {"portfolio": {"artifacts": {"portfolio_report_json": "portfolio.json"}}}, bundle,
    )
    assert report == before
    safe = overlay["actions"][0]
    assert safe["reference_plan"]["delta_krw_now"] == action["delta_krw_now"]
    assert safe["reference_plan"]["delta_krw_if_triggered"] == action["delta_krw_if_triggered"]
    assert safe["action_now"] == "WAIT" and safe["action_if_triggered"] == "NONE"
    assert safe["delta_krw_now"] == safe["delta_krw_if_triggered"] == 0
    assert safe["execution_feasibility_now"] == "blocked_stale_or_degraded_data"
    assert "structured_price_range_conflict" in safe["gate_reasons"]
    assert overlay["actions"][1]["action_now"] == "ADD"
    mobile = _private_market_payload({"surface": "kr", "body": {
        "market": "KR", "source_health": "OK",
        "guardrails": {"valid_until": "2026-10-14T01:30:00Z"},
        "current": {"bundle": bundle, "private_portfolio_overlay": overlay},
    }})
    assert mobile["rows"][0]["portfolio_action"]["reference_plan"] == safe["reference_plan"]
    assert mobile["rows"][0]["portfolio_action"]["action_now"] == "WAIT"
    account = {
        "as_of": now.isoformat(), "snapshot_health": "VALID", "pending_orders": [],
        "available_cash_krw": 1_000_000, "buying_power_krw": 1_000_000,
        "constraints": {"min_cash_buffer_krw": 0},
        "positions": [{"canonical_ticker": "034020.KS", "quantity": 100, "available_qty": 100}],
    }
    for payload in (mobile, copy.deepcopy(mobile)):
        # Also test an older caller that still passes the unmodified allocation.
        if payload is not mobile:
            payload["rows"][0]["portfolio_action"] = action
        plan = build_trade_plan(payload, account_snapshot=account, now=now)
        blocked, healthy = plan["rows"]
        assert plan["account_fresh"] is True
        assert blocked["status"] == "RECHECK"
        assert blocked["action"] == blocked["action_now"] == "WAIT"
        assert blocked["phase"] == "OBSERVE"
        assert blocked["quantity"] is None
        assert blocked["price_low"] is blocked["price_high"] is None
        assert blocked["estimated_net_cash"] is None
        assert blocked["target_weight"] is None
        assert "분석 원문과 가격 범위가 일치하지 않아" in blocked["reasons"][0]
        assert healthy["quantity"] > 0  # Conflict consumed no healthy row's budget.


@pytest.mark.parametrize("expired", [False, True])
def test_archive_work_blocks_only_affected_row_preserves_thesis_hash_and_gate(expired):
    decision = _decision()
    original = copy.deepcopy(decision)
    row = {
        "ticker": "034020.KS", "market_data_asof": "2026-10-14T01:00:00Z",
        "strategy_code": "BUY_NOW", "quality": {"row_mode": "IMMEDIATE", "execution_ready": True},
        "execution": {"readiness": "READY_NOW", "action_now": "BUY", "action_if_triggered": "BUY",
                      "blockers": ["existing_blocker"], "required_rechecks": ["existing_recheck"]},
    }
    good = copy.deepcopy(row)
    good["ticker"] = "OTHER"
    bundle = {"strategy_table": [row, good], "quality": {"decision_ready": True}}
    manifest = {"run_id": "immutable-original", "tickers": [{"ticker": "034020.KS", "decision": decision}]}
    work_packet._attach_analysis_theses(bundle, manifest, manifest)
    thesis = copy.deepcopy(row["thesis"])
    now = datetime(2026, 10, 14, 2 if expired else 1, 5, tzinfo=timezone.utc)
    work_packet._apply_market_row_validity(bundle, now=now)
    once = copy.deepcopy(row)
    work_packet._apply_market_row_validity(bundle, now=now)
    assert row == once  # Repeated packet preparation does not accumulate blockers.
    assert decision == original
    assert row["thesis"] == thesis
    assert thesis["decision_sha256"] == work_packet.sha256_json(original)
    assert thesis["execution_levels"]["levels"][0]["low"] == 75
    assert row["strategy_code"] == "DATA_CHECK"
    assert row["quality"]["execution_ready"] is False
    assert bundle["quality"]["decision_ready"] is False
    assert row["execution"]["readiness"] == "NEEDS_LIVE_RECHECK"
    assert row["execution"]["action_now"] is None
    assert row["execution"]["action_if_triggered"] is None
    assert "existing_blocker" in row["execution"]["blockers"]
    assert "structured_price_range_conflict" in row["execution"]["blockers"]
    assert "existing_recheck" in row["execution"]["required_rechecks"]
    assert any("execution_levels.levels[0]" in item for item in row["execution"]["required_rechecks"])
    if expired:
        assert "work_packet_row_expired" in row["execution"]["blockers"]
    else:
        assert good["execution"]["readiness"] == "READY_NOW"
        assert "structured_price_range_conflict" not in good["execution"]["blockers"]
        assert bundle["quality"]["report_mode"] == "MIXED"
    compact = work_packet._compact_market_row(row, 1)
    assert compact["thesis"] == thesis
    assert compact["execution"]["blockers"] == row["execution"]["blockers"]
    report = {"execution": copy.deepcopy(compact["execution"])}
    _validate_report_execution_gate(report, compact, ticker=row["ticker"], now=now)
    report["execution"]["readiness"] = "WAIT_FOR_TRIGGER"
    with pytest.raises(WorkRuntimeError, match="promotes a blocked packet"):
        _validate_report_execution_gate(report, compact, ticker=row["ticker"], now=now)
    report["execution"] = copy.deepcopy(compact["execution"])
    report["execution"]["blockers"].remove("structured_price_range_conflict")
    with pytest.raises(WorkRuntimeError, match="omits packet execution blockers"):
        _validate_report_execution_gate(report, compact, ticker=row["ticker"], now=now)
    report["execution"] = copy.deepcopy(compact["execution"])
    report["execution"]["required_rechecks"] = ["existing_recheck"]
    with pytest.raises(WorkRuntimeError, match="omits packet execution required_rechecks"):
        _validate_report_execution_gate(report, compact, ticker=row["ticker"], now=now)
