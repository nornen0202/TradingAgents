from copy import deepcopy
from datetime import datetime, timezone

import pytest

from tradingagents.portfolio.funded_rebalance import build_funded_rebalance

NOW = datetime(2026, 10, 20, 15, tzinfo=timezone.utc)
STAMP = "2026-10-20T14:00:00+00:00"


def row(ticker, price, *, buy=False, low=None, high=None):
    return {
        "ticker": ticker,
        "display_name": ticker,
        "last_price": price,
        "market_data_asof": STAMP,
        "portfolio_action": {
            "action_if_triggered": "STARTER_IF_TRIGGERED"
            if buy
            else "REDUCE_IF_TRIGGERED",
            "sell_intent": "NONE" if buy else "REDUCE_RISK",
        },
        "thesis": {
            "analysis_asof": STAMP,
            "entry_conditions": ["지지 확인과 원논지 재심사"],
            "execution_levels": {
                "levels": [{"level_type": "PULLBACK", "low": low, "high": high}]
                if buy
                else []
            },
        },
    }


def fixture(market="KR"):
    if market == "KR":
        rows = [
            row("000660.KS", 1_300_000),
            row("033780.KS", 193000, buy=True, low=189000, high=190500),
        ]
        quantities = {"000660.KS": 2}
        nav, cash, reserve, fx = 10_000_000, 1_000_000, 2_000_000, None
    else:
        rows = [
            row("TSM", 400),
            row("MPWR", 1300),
            row("GEV", 900),
            row("PG", 158, buy=True, low=154, high=155),
            row("ABBV", 285, buy=True, low=277, high=279),
        ]
        quantities = {"TSM": 12, "MPWR": 1, "GEV": 1}
        nav, cash, reserve, fx = 25_000_000, 1_200_000, 5_000_000, 1300
    account = {
        "as_of": STAMP,
        "account_value_krw": nav,
        "available_cash_krw": cash,
        "pending_orders": [],
        "positions": [
            {"canonical_ticker": t, "quantity": q, "available_qty": q}
            for t, q in quantities.items()
        ],
        "constraints": {
            "max_order_count_per_day": 5,
            "max_daily_turnover_ratio": 0.3,
            "max_single_name_weight": 0.35,
            "min_trade_krw": 100000,
        },
    }
    plan = {
        "market": market,
        "capital_context": {"min_cash_buffer_krw": reserve},
        "fx_krw_per_usd": fx,
        "fx_asof": STAMP,
    }
    return {"market": market, "rows": rows}, account, plan


@pytest.mark.parametrize("market", ["KR", "US"])
def test_funded_chain_reconciles_and_preserves_current_cash(market):
    payload, account, current = fixture(market)
    original = deepcopy((payload, account, current))
    result = build_funded_rebalance(payload, account, current, now=NOW)
    assert result["status"] == "CONDITIONAL_FUNDED"
    assert result["order_ready"] is False
    ledger = result["cash_ledger"]
    assert ledger["initial_cash_krw"] + ledger["net_sale_funding_krw"] - ledger[
        "buy_total_krw"
    ] == pytest.approx(ledger["after_buys_cash_krw"])
    assert (
        ledger["after_buys_cash_krw"]
        >= ledger["reserve_krw"] + ledger["extra_cash_margin_krw"]
    )
    assert ledger["order_count"] <= 5
    assert ledger["turnover_ratio"] <= 0.3
    assert all(
        isinstance(x["quantity"], int) and x["quantity"] > 0
        for x in result["buy_legs"] + result["sell_legs"]
    )
    assert ledger["fx_conversion_cost_krw"] == 0
    if market == "US":
        assert ledger["capital_tax_reserve_krw"] == pytest.approx(
            0.22 * ledger["sell_gross_krw"]
        )
        assert ledger["sell_fees_and_levy_krw"] == pytest.approx(
            (0.0025 + 0.0000206) * ledger["sell_gross_krw"]
        )
    else:
        assert len(result["sell_legs"]) == 1
        assert ledger["sell_fees_and_levy_krw"] == pytest.approx(
            0.00347 * ledger["sell_gross_krw"]
        )
    assert (payload, account, current) == original


@pytest.mark.parametrize(
    "fault",
    [
        "future_account",
        "missing_account_date",
        "naive_account",
        "old_account",
        "zero_nav",
        "nan_nav",
        "missing_cash",
        "missing_pending",
        "pending_buy",
        "pending_sell",
        "future_quote",
        "missing_quote_date",
        "future_thesis",
        "missing_thesis_date",
        "no_sellable_shares",
        "no_turnover",
        "one_order",
        "future_fx",
        "old_fx",
        "missing_fx",
    ],
)
def test_bad_or_unfundable_inputs_never_create_rotation(fault):
    market = "US" if "fx" in fault else "KR"
    payload, account, current = fixture(market)
    if fault == "future_account":
        account["as_of"] = "2026-10-21T14:00:00+00:00"
    if fault == "missing_account_date":
        account.pop("as_of")
    if fault == "naive_account":
        account["as_of"] = "2026-10-20T14:00:00"
    if fault == "old_account":
        account["as_of"] = "2026-10-01T14:00:00+00:00"
    if fault == "zero_nav":
        account["account_value_krw"] = 0
    if fault == "nan_nav":
        account["account_value_krw"] = float("nan")
    if fault == "missing_cash":
        account.pop("available_cash_krw")
    if fault == "missing_pending":
        account.pop("pending_orders")
    if fault.startswith("pending_"):
        account["pending_orders"] = [
            {
                "canonical_ticker": "000660.KS",
                "side": fault.split("_")[1],
                "remaining_qty": 1,
            }
        ]
    if fault == "future_quote":
        payload["rows"][0]["market_data_asof"] = "2026-10-21T14:00:00+00:00"
    if fault == "missing_quote_date":
        payload["rows"][0].pop("market_data_asof")
    if fault == "future_thesis":
        payload["rows"][0]["thesis"]["analysis_asof"] = "2026-10-21T14:00:00+00:00"
    if fault == "missing_thesis_date":
        payload["rows"][0]["thesis"].pop("analysis_asof")
    if fault == "no_sellable_shares":
        account["positions"][0]["available_qty"] = 0
    if fault == "no_turnover":
        account["constraints"]["max_daily_turnover_ratio"] = 0.01
    if fault == "one_order":
        account["constraints"]["max_order_count_per_day"] = 1
    if fault == "future_fx":
        current["fx_asof"] = "2026-10-21T14:00:00+00:00"
    if fault == "old_fx":
        current["fx_asof"] = "2026-10-01T14:00:00+00:00"
    if fault == "missing_fx":
        current["fx_krw_per_usd"] = None
    result = build_funded_rebalance(payload, account, current, now=NOW)
    assert result["status"] == "UNAVAILABLE"
    assert result["buy_legs"] == []
    assert result["sell_legs"] == []


def test_buy_price_conflict_and_absent_entry_do_not_become_funded():
    payload, account, current = fixture()
    payload["rows"][1]["thesis"]["execution_levels"]["levels"][0]["low"] = 200000
    assert (
        build_funded_rebalance(payload, account, current, now=NOW)["status"]
        == "UNAVAILABLE"
    )
    payload["rows"][1]["thesis"]["execution_levels"]["levels"] = []
    assert (
        build_funded_rebalance(payload, account, current, now=NOW)["status"]
        == "UNAVAILABLE"
    )


def test_fractional_position_never_rounds_up_past_half_to_fund_a_buy():
    payload, account, current = fixture()
    account["positions"][0].update(quantity=1.9, available_qty=1.9)
    result = build_funded_rebalance(payload, account, current, now=NOW)
    assert result["status"] == "UNAVAILABLE"
    assert result["sell_legs"] == []


def test_whole_share_caps_and_protected_holdings():
    payload, account, current = fixture("US")
    payload["rows"][0]["ticker"] = "GLDM"
    account["positions"][0]["canonical_ticker"] = "GLDM"
    result = build_funded_rebalance(payload, account, current, now=NOW)
    assert result["status"] == "UNAVAILABLE"
    assert result["sell_legs"] == []
