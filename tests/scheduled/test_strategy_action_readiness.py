import pytest

from tests.scheduled.test_decision_bundle import _live_context
from tradingagents.scheduled.decision_bundle import build_decision_bundle


def build(now, conditional, portfolio="STARTER_NOW", held=False):
    context = _live_context()
    context["tickers"][0].update(decision_now=now, decision_if_triggered=conditional,
                                decision_state="ARMED" if now == "NONE" else "ACTIONABLE_NOW")
    return build_decision_bundle(run_id="fixture", market="US",
        generated_at="2026-07-10T12:01:00-04:00", analysis_source_run_id="research",
        ticker_summaries=[{"ticker": "NVDA", "status": "success"}], execution_context=context,
        portfolio_candidates=[{"canonical_ticker": "NVDA", "is_held": held}],
        portfolio_actions=[{"canonical_ticker": "NVDA", "action_now": portfolio,
                            "action_if_triggered": "STARTER_IF_TRIGGERED"}],
        benchmark_loader=lambda _: {})


def test_fresh_observation_and_portfolio_opinion_cannot_promote_explicit_none():
    row = build("NONE", "NONE")["strategy_table"][0]
    assert row["strategy_code"] == "WAIT"
    assert row["quality"]["data_ready"] is True
    assert row["quality"]["action_ready"] is False
    assert row["quality"]["action_status"] == "NO_EXECUTION_ACTION"


def test_conditional_authorization_is_not_an_immediate_buy():
    row = build("NONE", "STARTER")["strategy_table"][0]
    assert row["strategy_code"] == "BUY_ON_CONFIRMATION"
    assert row["quality"]["action_ready"] is False
    assert row["quality"]["action_status"] == "WAITING_TRIGGER"


@pytest.mark.parametrize("conditional", ["REDUCE", "EXIT"])
def test_conditional_risk_exit_remains_visible_without_immediate_authority(conditional):
    from tradingagents.scheduled.mobile_site import _public_quality
    row = build("NONE", conditional, portfolio="HOLD", held=True)["strategy_table"][0]
    assert row["raw_codes"]["decision_now"] == "NONE"
    assert row["raw_codes"]["decision_if_triggered"] == conditional
    assert row["quality"]["action_ready"] is False
    assert row["quality"]["action_status"] == "WAITING_TRIGGER"
    assert _public_quality(row["quality"])["investor_label"] == "조건 충족 대기"


def test_original_execution_buy_and_risk_sell_survive_portfolio_disagreement():
    for action, expected in (("STARTER_NOW", "BUY_NOW"), ("EXIT_NOW", "SELL"), ("REDUCE_NOW", "REDUCE")):
        row = build(action, "NONE", portfolio="WATCH", held=True)["strategy_table"][0]
        assert row["strategy_code"] == expected
        assert row["quality"]["action_ready"] is True


def test_no_action_counts_are_separate_from_freshness_coverage():
    quality = build("NONE", "NONE")["quality"]
    assert quality["fresh_row_ratio"] == 1
    assert quality["action_ready_rows"] == 0


def test_public_mobile_projection_preserves_data_action_distinction():
    from tradingagents.scheduled.mobile_site import _public_quality
    quality = build("NONE", "NONE")["strategy_table"][0]["quality"]
    public = _public_quality(quality)
    assert public["data_ready"] is True
    assert public["action_ready"] is False
    assert public["action_status"] == "NO_EXECUTION_ACTION"
    assert public["investor_state"] == "RESEARCH"
    assert public["investor_label"] == "자료 확인 · 매매 행동 없음"
    conditional = _public_quality(build("NONE", "STARTER")["strategy_table"][0]["quality"])
    assert conditional["investor_label"] == "조건 충족 대기"
    expired = _public_quality({**quality, "row_mode": "BLOCKED_STALE", "data_ready": False})
    assert expired["investor_state"] == "RECHECK"
