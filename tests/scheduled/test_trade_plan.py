from datetime import datetime, timezone
import json

import pytest

from tradingagents.scheduled.trade_plan import build_trade_plan


NOW = datetime(2026, 10, 2, 3, tzinfo=timezone.utc)


def snapshot(cash=1_000, buying_power=1_000, positions=None):
    return {
        "account_id": "must-never-publish",
        "snapshot_id": "private-id",
        "as_of": "2026-10-02T02:00:00Z",
        "snapshot_health": "VALID",
        "pending_orders": [],
        "available_cash_krw": cash,
        "buying_power_krw": buying_power,
        "constraints": {"min_cash_buffer_krw": 0},
        "positions": positions or [],
    }


def row(ticker="AAA", *, delta=600, held=False, action="ADD_IF_TRIGGERED", price=100):
    return {
        "ticker": ticker,
        "is_held": held,
        "quality": {"row_valid_until": "2026-10-02T04:00:00Z"},
        "portfolio_action": {
            "action_now": "HOLD" if held else "WATCH",
            "delta_krw_now": 0,
            "action_if_triggered": action,
            "delta_krw_if_triggered": delta,
            "risk_action": "REDUCE_RISK",
            "risk_action_level": {"level_type": "SUPPORT", "price": price},
        },
        "thesis": {
            "execution_levels": {
                "levels": [
                    {"level_type": "PULLBACK", "low": price * 0.9, "high": price}
                ]
            },
            "analysis_asof": "2026-10-02T01:00:00Z",
        },
    }


def plan(rows, account=None, **kwargs):
    return build_trade_plan(
        {"market": "KR", "rows": rows},
        account_snapshot=account or snapshot(),
        now=NOW,
        **kwargs,
    )


def test_buys_share_one_cash_ledger_with_fees_and_upper_range():
    result = plan([row("AAA"), row("BBB")])
    assert [r["quantity"] for r in result["rows"]] == [5, 4]
    assert result["summary"]["buy_budget_used_krw"] == pytest.approx(901.323)
    assert result["rows"][0]["estimated_fees"] == pytest.approx(0.735)
    assert result["rows"][0]["estimated_net_cash"] == pytest.approx(-500.735)
    assert "must-never-publish" not in json.dumps(result)
    assert "private-id" not in json.dumps(result)


def test_zero_orderability_is_not_missing_or_replaced_by_cash():
    result = plan([row()], snapshot(cash=50_000, buying_power=0))["rows"][0]
    assert result["quantity"] == 0
    assert result["status"] == "NO_QUANTITY"


def test_missing_orderability_does_not_become_zero():
    account = snapshot()
    del account["buying_power_krw"]
    result = plan([row()], account)["rows"][0]
    assert result["quantity"] is None
    assert result["status"] == "UNSIZED"


def test_cash_buffer_and_tiny_allocation_do_not_round_up_to_a_share():
    account = snapshot()
    account["constraints"]["min_cash_buffer_krw"] = 950
    assert plan([row()], account)["rows"][0]["quantity"] == 0
    assert plan([row(delta=99.99)])["rows"][0]["quantity"] == 0


def test_sell_capped_at_available_whole_shares_and_does_not_fund_buy():
    account = snapshot(
        0, 0, [{"canonical_ticker": "AAA", "quantity": 10.7, "available_qty": 3.8}]
    )
    result = plan(
        [row("AAA", held=True, delta=-1_000, action="REDUCE_IF_TRIGGERED"), row("BBB")],
        account,
    )
    sell, buy = result["rows"]
    assert sell["quantity"] == 3
    assert sell["estimated_net_cash"] == pytest.approx(298.959)
    assert buy["quantity"] == 0
    assert result["summary"]["buy_budget_used_krw"] == 0


def test_hold_with_negative_risk_allocation_remains_conditional():
    item = row("005930.KS", held=True, delta=-250, action="WATCH_TRIGGER")
    account = snapshot(
        positions=[{"canonical_ticker": "005930", "quantity": 5, "available_qty": 5}]
    )
    result = plan([item], account)["rows"][0]
    assert result["action"] == "SELL"
    assert result["action_now"] == "HOLD"
    assert result["phase"] == "CONDITIONAL"
    assert result["quantity"] == 2
    assert result["price_kind"] == "TRIGGER"
    assert result["price_comparator"] == "<="
    assert result["order_ready"] is False


def test_relative_trim_without_allocation_does_not_create_sell():
    item = row(held=True, delta=0, action="WATCH_TRIGGER")
    item["portfolio_action"]["portfolio_relative_action"] = "TRIM_TO_FUND"
    result = plan([item])["rows"][0]
    assert result["action"] == "HOLD"
    assert result["quantity"] == 0


def test_conditional_buy_without_budget_is_zero_even_if_research_bullish():
    item = row(delta=0, action="WATCH_TRIGGER")
    item["thesis"]["conditional_entry_action"] = "STARTER"
    result = plan([item])["rows"][0]
    assert result["action"] == "BUY"
    assert result["quantity"] == 0
    assert "0원" in result["reasons"][0]


@pytest.mark.parametrize(
    "levels",
    [
        [],
        [{"level_type": "SUPPORT", "price": 99}],
        [{"level_type": "PULLBACK", "low": 105, "high": 100}],
        [{"level_type": "PULLBACK", "low": 90, "high": 100, "currency": "USD"}],
    ],
)
def test_no_invented_price_bands_from_quote_or_wrong_currency(levels):
    item = row()
    item["last_price"] = 100
    item["thesis"]["execution_levels"]["levels"] = levels
    result = plan([item])["rows"][0]
    assert result["quantity"] is None
    assert result["price_high"] is None


def test_single_breakout_is_threshold_and_requires_repricing():
    item = row()
    item["thesis"]["execution_levels"]["levels"] = [
        {"level_type": "BREAKOUT", "price": 100}
    ]
    result = plan([item])["rows"][0]
    assert result["price_kind"] == "TRIGGER"
    assert result["price_comparator"] == ">="
    assert any("체결 보장" in reason for reason in result["reasons"])


def test_us_requires_explicit_fx_and_never_infers_from_old_position_mark():
    item = row(delta=600_000)
    item["last_price"] = 100
    item["portfolio_action"]["position_metrics"] = {"market_price_krw": 140_000}
    account = snapshot(1_000_000, 1_000_000)
    result = build_trade_plan(
        {"market": "US", "rows": [item]}, account_snapshot=account, now=NOW
    )
    assert result["rows"][0]["quantity"] is None
    with_fx = build_trade_plan(
        {"market": "US", "rows": [item]},
        account_snapshot=account,
        fx_krw_per_usd=1_400,
        fx_asof="2026-10-02T02:00:00Z",
        now=NOW,
    )
    assert with_fx["rows"][0]["quantity"] == 4
    assert with_fx["rows"][0]["estimated_fees"] == 1
    assert with_fx["summary"]["buy_budget_used_krw"] == pytest.approx(563_645.6)
    assert with_fx["rows"][0]["fx_budget_reserve_krw"] == pytest.approx(2_245.6)
    assert with_fx["rows"][0]["estimated_net_cash"] == -401


def test_missing_sell_availability_is_not_assumed_equal_to_held_quantity():
    account = snapshot(positions=[{"canonical_ticker": "AAA", "quantity": 10}])
    result = plan([row(delta=-600, held=True, action="REDUCE_IF_TRIGGERED")], account)[
        "rows"
    ][0]
    assert result["quantity"] is None


def test_stale_snapshot_still_labels_asof_scenario_not_ready():
    account = snapshot()
    account["as_of"] = "2026-09-22T00:00:00Z"
    item = row()
    item["quality"]["execution_ready"] = True
    result = plan([item], account)["rows"][0]
    assert result["quantity"] == 5
    assert result["status"] == "RECHECK"
    assert result["order_ready"] is False


def test_duplicate_alias_does_not_double_allocate():
    result = plan([row("005930"), row("005930.KS")])
    assert len(result["rows"]) == 1


def test_nonfinite_inputs_and_invalid_fee_config_cannot_create_quantity():
    assert (
        plan([row()], snapshot(buying_power=float("nan")))["rows"][0]["quantity"]
        is None
    )
    assert plan([row()], fee_config={})["rows"][0]["quantity"] is None


def test_domestic_equity_etf_does_not_get_common_share_transaction_tax():
    item = row(delta=-600, held=True, action="REDUCE_IF_TRIGGERED")
    item["asset_type"] = "domestic_equity_etf"
    account = snapshot(
        positions=[{"canonical_ticker": "AAA", "quantity": 10, "available_qty": 10}]
    )
    result = plan([item], account)["rows"][0]
    assert result["sell_levy_rate"] == 0
    assert result["estimated_fees"] == pytest.approx(0.882)


@pytest.mark.parametrize(
    ("size_plan", "expected"), [("FULL_EXIT", 6), ("PARTIAL_20", 2), ("PARTIAL_35", 3)]
)
def test_us_structured_sell_fraction_needs_no_invented_fx(size_plan, expected):
    item = row(delta=-500_000, held=True, action="REDUCE_IF_TRIGGERED")
    item["portfolio_action"]["sell_size_plan"] = size_plan
    item["portfolio_action"]["trigger_conditions"] = [
        "BUY BREAKOUT MUST NOT LEAK TO SELL"
    ]
    item["risk_condition_ko"] = "100달러 이하 하락 시 위험 축소"
    account = snapshot(
        positions=[{"canonical_ticker": "AAA", "quantity": 10.7, "available_qty": 6.2}]
    )
    result = build_trade_plan(
        {"market": "US", "rows": [item]}, account_snapshot=account, now=NOW
    )["rows"][0]
    assert result["quantity"] == expected
    assert result["quantity_basis"].startswith("STRUCTURED_")
    assert result["status"] == "RECHECK"
    assert result["trigger_conditions"] == [item["risk_condition_ko"]]
    assert "환율 확인 후" in " ".join(result["reasons"])


def test_structured_sell_fraction_respects_known_allocation_cap_and_zero():
    item = row(delta=-250, held=True, action="REDUCE_IF_TRIGGERED")
    item["portfolio_action"]["sell_size_plan"] = "FULL_EXIT"
    account = snapshot(
        positions=[{"canonical_ticker": "AAA", "quantity": 10, "available_qty": 10}]
    )
    assert plan([item], account)["rows"][0]["quantity"] == 2
    item["portfolio_action"]["delta_krw_if_triggered"] = 0
    assert plan([item], account)["rows"][0]["quantity"] == 0


def test_structured_full_exit_can_size_from_explicit_plan_without_delta():
    item = row(delta=None, held=True, action="EXIT_IF_TRIGGERED")
    item["portfolio_action"]["sell_size_plan"] = "FULL_EXIT"
    account = snapshot(
        positions=[
            {"canonical_ticker": "AAA", "quantity": 0.436, "available_qty": 0.436}
        ]
    )
    assert plan([item], account)["rows"][0]["quantity"] == 0


def test_malformed_optional_nested_fields_do_not_crash_site_build():
    item = row()
    item["thesis"]["execution_levels"]["levels"] = 3
    assert plan([item], fee_config=[])["rows"][0]["quantity"] is None
    result = build_trade_plan(
        {"market": "KR", "rows": []}, account_snapshot={"positions": None}, now=NOW
    )
    assert result["rows"] == []


def test_work_report_cannot_override_allocation_or_approve_orders():
    item = row(delta=0)
    item["execution"] = {"action_now": "BUY_NOW", "readiness": "READY_NOW"}
    result = plan([item])["rows"][0]
    assert result["quantity"] == 0
    assert result["order_ready"] is False


@pytest.mark.parametrize("buffer", [None, -1, float("nan")])
def test_missing_or_invalid_cash_buffer_is_not_assumed_zero(buffer):
    account = snapshot()
    account["constraints"]["min_cash_buffer_krw"] = buffer
    result = plan([row()], account)["rows"][0]
    assert result["quantity"] is None
    assert "최소 보유 현금" in " ".join(result["reasons"])


def test_hold_no_transaction_costs_are_known_zero_without_price_or_fee_data():
    item = row(held=True, delta=0, action="WATCH_TRIGGER")
    result = plan([item], fee_config={})["rows"][0]
    for field in (
        "quantity",
        "estimated_gross_low",
        "estimated_gross_high",
        "estimated_fees",
        "estimated_net_cash",
    ):
        assert result[field] == 0


def test_pending_buy_blocks_new_buy_without_double_counting_reserved_cash():
    account = snapshot()
    account["pending_orders"] = [
        {"canonical_ticker": "OTHER", "side": "buy", "remaining_qty": 2}
    ]
    result = plan([row()], account)["rows"][0]
    assert result["quantity"] is None
    assert "미체결 주문" in " ".join(result["reasons"])


@pytest.mark.parametrize(
    "source_reason", [None, "PRIVATE-ERROR C:/private/path", {"raw": "PRIVATE-ERROR"}]
)
def test_missing_account_has_generic_reason_without_false_pending_failure(
    source_reason,
):
    result = build_trade_plan(
        {"market": "KR", "rows": [row()]},
        account_source_reason=source_reason,
        now=NOW,
    )["rows"][0]
    assert result["quantity"] is None
    assert (
        result["reasons"][0]
        == "동일 실행 계좌를 확인할 수 없어 수량 산정을 보류했습니다."
    )
    assert all("미체결" not in message for message in result["reasons"])
    assert "PRIVATE-ERROR" not in json.dumps(result)


def test_actual_pending_failure_source_keeps_its_own_block_reason():
    result = build_trade_plan(
        {"market": "KR", "rows": [row()]},
        account_source_reason="PENDING_ORDERS_UNVERIFIED",
        now=NOW,
    )["rows"][0]
    assert result["quantity"] is None
    assert "미체결 주문 확인" in result["reasons"][0]
    assert result["order_ready"] is False


def test_missing_account_does_not_change_explicit_zero_allocation_or_hold():
    result = build_trade_plan(
        {
            "market": "KR",
            "rows": [
                row(delta=0),
                row("BBB", held=True, delta=0, action="WATCH_TRIGGER"),
            ],
        },
        account_source_reason="SOURCE_RUN_PARTIAL_FAILURE",
        now=NOW,
    )
    assert [r["quantity"] for r in result["rows"]] == [0, 0]
    assert [r["status"] for r in result["rows"]] == ["NO_QUANTITY", "OBSERVE"]


def test_same_ticker_pending_order_blocks_additional_sell_not_unrelated_buy():
    account = snapshot(
        positions=[{"canonical_ticker": "AAA", "quantity": 10, "available_qty": 6}]
    )
    account["pending_orders"] = [
        {"canonical_ticker": "AAA", "side": "sell", "remaining_qty": 4}
    ]
    result = plan(
        [row("AAA", held=True, delta=-600, action="REDUCE_IF_TRIGGERED"), row("BBB")],
        account,
    )
    assert result["rows"][0]["quantity"] is None
    assert result["rows"][1]["quantity"] == 5


def test_completed_pending_order_does_not_block_plan_and_identifier_is_not_exported():
    account = snapshot()
    account["pending_orders"] = [
        {
            "broker_order_id": "do-not-export",
            "canonical_ticker": "AAA",
            "side": "buy",
            "remaining_qty": 0,
        }
    ]
    result = plan([row()], account)
    assert result["rows"][0]["quantity"] == 5
    assert "do-not-export" not in json.dumps(result)


@pytest.mark.parametrize(
    "pending",
    [
        None,
        ["bad"],
        [{"remaining_qty": 2, "side": "buy"}],
        [{"remaining_qty": float("nan")}],
    ],
)
def test_unknown_pending_order_state_does_not_mean_empty(pending):
    account = snapshot()
    account["pending_orders"] = pending
    assert plan([row()], account)["rows"][0]["quantity"] is None


def test_zero_available_quantity_stays_zero_for_explicit_full_exit_without_fx():
    item = row(held=True, delta=-500_000, action="EXIT_IF_TRIGGERED")
    item["portfolio_action"]["sell_size_plan"] = "FULL_EXIT"
    account = snapshot(
        positions=[{"canonical_ticker": "AAA", "quantity": 10, "available_qty": 0}]
    )
    result = build_trade_plan(
        {"market": "US", "rows": [item]}, account_snapshot=account, now=NOW
    )["rows"][0]
    assert result["quantity"] == 0
    assert result["estimated_net_cash"] == 0


def test_below_minimum_trade_preserves_reference_quantity_but_flags_first_reason():
    account = snapshot(
        positions=[{"canonical_ticker": "AAA", "quantity": 10, "available_qty": 10}]
    )
    account["constraints"]["min_trade_krw"] = 1_000
    item = row(delta=-250, held=True, action="REDUCE_IF_TRIGGERED")
    result = plan([item], account)["rows"][0]
    assert result["quantity"] == 2
    assert result["status"] == "RECHECK"
    assert result["constraint_review_required"] is True
    assert result["reasons"][0].startswith(
        "계획 거래대금이 계좌 최소 거래금액 1,000원 미만"
    )


def test_known_disabled_order_limit_and_overweight_are_not_presented_as_available():
    account = snapshot()
    account["constraints"].update(
        max_order_count_per_day=0, max_single_name_weight=0.35
    )
    item = row()
    item["portfolio_action"]["target_weight_if_triggered"] = 0.5
    result = plan([item], account)["rows"][0]
    assert result["quantity"] == 5
    assert result["constraint_review_required"] is True
    assert result["status"] == "RECHECK"
    assert any("0건" in reason for reason in result["reasons"])
    assert any("비중 상한" in reason for reason in result["reasons"])
