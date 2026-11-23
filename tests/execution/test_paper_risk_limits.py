from datetime import datetime, timedelta, timezone

from tradingagents.execution.paper_risk_limits import evaluate_micro_paper


NOW = datetime(2026, 10, 2, 14, tzinfo=timezone.utc)
POLICY = {"version": "fixture", "scope": "paper-fixture", "currency": "USD", "capital_ceiling": "1000",
          "order_ceiling": "100", "day_loss_fraction": ".03", "drawdown_fraction": ".08",
          "max_api_failures": 2, "max_account_age_seconds": 30}
SCOPE = {"scope": "paper-fixture", "currency": "USD", "mode": "isolated_paper"}
ACCOUNT = {**SCOPE, "observed_at": NOW.isoformat(), "reconciled": True, "kill_switch": False, "nav": "1000",
           "day_open_nav": "1000", "peak_nav": "1000", "gross_exposure": "850", "settled_cash": "100",
           "pending_buy_notional": "20", "unsettled_cash": "300"}
ORDER = {**SCOPE, "side": "BUY", "notional": "60"}


def _api(*success):
    return [{"id": str(i), "observed_at": (NOW - timedelta(seconds=len(success) - i)).isoformat(),
             "scope": "paper-fixture", "success": value} for i, value in enumerate(success)]


def test_only_settled_cash_is_eligible_for_a_buy():
    result = evaluate_micro_paper(POLICY, ACCOUNT, ORDER, _api(True), as_of=NOW)
    assert result["projected_paper_candidate"] and not result["live_order_authority"]
    result = evaluate_micro_paper(POLICY, {**ACCOUNT, "settled_cash": "50"}, ORDER, _api(True), as_of=NOW)
    assert "capital_or_settled_cash_limit" in result["blocking_reasons"]


def test_loss_blocks_new_risk_and_does_not_turn_an_unverified_sell_into_an_order():
    loss = {**ACCOUNT, "nav": "890"}
    result = evaluate_micro_paper(POLICY, loss, ORDER, _api(True), as_of=NOW)
    assert set(result["reduce_only_reasons"]) == {"daily_loss_limit", "drawdown_limit"}
    sell = {**ORDER, "side": "SELL"}
    result = evaluate_micro_paper(POLICY, loss, sell, _api(True), as_of=NOW)
    assert not result["projected_paper_candidate"]
    result = evaluate_micro_paper(POLICY, loss, {**sell, "verified_risk_reduction": True}, _api(True), as_of=NOW)
    assert result["projected_paper_candidate"]


def test_api_errors_missing_observation_or_live_mode_make_no_order_eligible():
    result = evaluate_micro_paper(POLICY, ACCOUNT, ORDER, _api(True, False, False), as_of=NOW)
    assert "consecutive_api_errors" in result["blocking_reasons"]
    result = evaluate_micro_paper(POLICY, ACCOUNT, ORDER, _api(False, False, True), as_of=NOW)
    assert result["consecutive_api_failures"] == 0
    result = evaluate_micro_paper(POLICY, {**ACCOUNT, "mode": "live"}, ORDER, [], as_of=NOW)
    assert not result["projected_paper_candidate"]
