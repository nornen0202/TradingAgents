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
        action_if_triggered="NONE",
        execution_update={"decision_state": "DEGRADED", "decision_now": "ADD_NOW"},
        is_held=False,
    )
    assert now == "WATCH"
    assert trig == "NONE"
