from tradingagents.portfolio.candidates import _apply_execution_overlay_actions


def test_actionable_now_promotes_action():
    now, trig = _apply_execution_overlay_actions(
        action_now="WATCH",
        action_if_triggered="STARTER_IF_TRIGGERED",
        execution_update={"decision_state": "ACTIONABLE_NOW", "decision_now": "STARTER_NOW"},
        is_held=False,
    )
    assert now == "STARTER_NOW"
    assert trig == "NONE"


def test_degraded_fail_closed():
    now, trig = _apply_execution_overlay_actions(
        action_now="ADD_NOW",
        action_if_triggered="STARTER_IF_TRIGGERED",
        execution_update={"decision_state": "DEGRADED", "decision_now": "ADD_NOW"},
        is_held=False,
    )
    assert now == "WATCH"
    assert trig == "STARTER_IF_TRIGGERED"


def test_degraded_without_trigger_does_not_fabricate_watch_trigger():
    now, trig = _apply_execution_overlay_actions(
        action_now="STARTER_NOW",
        action_if_triggered="NONE",
        execution_update={"decision_state": "DEGRADED", "decision_now": "STARTER_NOW"},
        is_held=False,
    )
    assert now == "WATCH"
    assert trig == "NONE"


def test_wait_heavy_batch_keeps_confirmed_alternative_and_independent_gate():
    from types import SimpleNamespace
    from tradingagents.portfolio.candidates import _build_single_candidate, _execution_health
    from tradingagents.portfolio.gates import apply_gates
    from dataclasses import replace

    snapshot = SimpleNamespace(snapshot_id="fixture", account_value_krw=100, positions=[],
                               constraints=SimpleNamespace(max_single_name_weight=1.0))
    candidate, _ = _build_single_candidate(snapshot=snapshot, canonical_ticker="AAPL", analysis=None, position=None)
    metrics = _execution_health(execution_update={
        "decision_state": "ACTIONABLE_NOW", "decision_now": "STARTER_NOW",
        "reason_codes": ["conditional_entry_group_confirmed"],
        "entry_confirmation_v2": {"evaluation": {"paper_candidate_ready": True, "matched_alternatives": [0]}},
    }, execution_levels={})
    candidate = replace(candidate, suggested_action_now="STARTER_NOW", trigger_profile=metrics,
                        data_coverage={"company_news_count": 3})
    batch = {"entry_action_distribution": {"WAIT": 30}, "stance_distribution": {"BULLISH": 28}}

    def gated(value):
        return apply_gates(candidates=[value], snapshot=snapshot, batch_metrics=batch, warnings=[], profile=None)[0]

    assert gated(candidate).suggested_action_now == "STARTER_NOW"
    assert "wait_heavy_batch_review" in gated(candidate).gate_reasons
    assert gated(replace(candidate, trigger_profile={})).suggested_action_now == "WATCH"
    assert gated(replace(candidate, data_coverage={"company_news_count": 0})).suggested_action_now == "WATCH"
