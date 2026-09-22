from copy import deepcopy
from datetime import datetime, timezone
import json

import pytest

from tradingagents.portfolio.account_models import AccountSnapshot
from tradingagents.portfolio.account_review import review_account, review_market_views
from tools.review_actual_account import select_latest


NOW = datetime(2026, 9, 22, 7, tzinfo=timezone.utc)


def snapshot():
    return {
        "as_of": "2026-09-22T15:59:00+09:00",
        "snapshot_health": "VALID",
        "broker": "kis",
        "account_id": "secret-account-number",
        "currency": "KRW",
        "total_equity_krw": 1000,
        "settled_cash_krw": 200,
        "available_cash_krw": 0,
        "buying_power_krw": 0,
        "pending_orders": [],
        "constraints": {"min_cash_buffer_krw": 100},
        "positions": [
            {
                "canonical_ticker": "SPY",
                "quantity": 2,
                "available_qty": 2,
                "market_value_krw": 800,
                "market_price_krw": 400,
            }
        ],
    }


def test_explicit_zero_does_not_become_available_deposit():
    result = review_account(snapshot(), now=NOW)
    assert result["cash"]["available_cash_krw"] == 0
    assert result["cash"]["buying_power_krw"] == 0
    assert result["order_authorized"] is False
    assert "NON_MARGIN_SYMBOL_BUYING_POWER_NOT_VERIFIED" in result["issues"]


def test_empty_pending_list_and_valid_health_are_not_completeness_proof():
    result = review_account(snapshot(), now=NOW)
    assert result["reported_pending_order_count"] == 0
    assert not result["pending_orders_known"]
    assert not result["holdings_complete"]
    assert "PENDING_ORDERS_UNKNOWN" in result["issues"]


@pytest.mark.parametrize(
    "as_of,code",
    [
        ("2026-09-22T08:00:00+00:00", "SNAPSHOT_FROM_FUTURE"),
        ("2026-09-21T08:00:00+00:00", "SNAPSHOT_STALE"),
        ("2026-09-22T07:00:00", "SNAPSHOT_TIME_UNKNOWN"),
        ("invalid", "SNAPSHOT_TIME_UNKNOWN"),
    ],
)
def test_timestamps_fail_closed(as_of, code):
    data = snapshot()
    data["as_of"] = as_of
    assert code in review_account(data, now=NOW)["issues"]


def test_overlap_warned_but_never_summed_and_identifiers_omitted():
    data = snapshot()
    data["available_cash_krw"] = 200
    result = review_market_views({"KR": data, "US": deepcopy(data)}, now=NOW)
    assert result["matching_cash_views"] == [["KR", "US"]]
    assert result["combined_nav_krw"] is None
    assert result["combined_buying_power_krw"] is None
    assert "secret-account-number" not in json.dumps(result)


def test_wait_exposure_and_stress_are_position_based():
    result = review_account(snapshot(), now=NOW)
    assert result["equity_exposure_pct"] == 80
    stress = result["no_trade_stress_scenarios"][0]
    assert stress["pnl_krw"] == -240
    assert stress["market_view_return_pct"] == -24


@pytest.mark.parametrize("rows", [None, {}, [None]])
def test_missing_or_malformed_positions_are_not_zero_exposure(rows):
    data = snapshot()
    data["positions"] = rows
    result = review_account(data, now=NOW)
    assert result["holdings_value_krw"] is None
    assert result["equity_exposure_pct"] is None
    assert result["no_trade_stress_scenarios"] == []


def test_unconfirmed_currency_does_not_get_labeled_as_krw():
    data = snapshot()
    data["currency"] = "USD"
    result = review_account(data, now=NOW)
    assert result["market_view_nav_krw"] is None
    assert result["holdings_value_krw"] is None
    assert all(x is None for x in result["cash"].values())
    assert result["no_trade_stress_scenarios"] == []


@pytest.mark.parametrize(
    "extra",
    [
        {"cash_diagnostics": "bad", "constraints": [1]},
        {"cash_diagnostics": {"selected_fields": [1], "query_coverage": "bad"}},
    ],
)
def test_malformed_optional_metadata_does_not_break_report_storage(extra):
    data = snapshot()
    data.update(extra)
    result = review_account(data, now=NOW)
    assert not result["holdings_complete"]
    assert not result["pending_orders_known"]


@pytest.mark.parametrize("value", [None, float("inf"), float("nan"), -1])
def test_invalid_positions_cannot_produce_plausible_stress(value):
    data = snapshot()
    data["positions"][0]["market_value_krw"] = value
    result = review_account(data, now=NOW)
    assert result["no_trade_stress_scenarios"] == []
    assert result["equity_exposure_pct"] is None
    json.dumps(result, allow_nan=False)


@pytest.mark.parametrize("equity", [0, -100])
def test_authoritative_nonpositive_equity_not_replaced_by_cash(equity):
    account = AccountSnapshot(
        snapshot_id="s",
        as_of="",
        broker="kis",
        account_id="",
        currency="KRW",
        settled_cash_krw=200,
        available_cash_krw=200,
        buying_power_krw=500,
        total_equity_krw=equity,
    )
    assert account.account_value_krw == equity
    result = review_account(account.to_dict(), now=NOW)
    assert result["market_view_nav_krw"] is None
    assert "NAV_NOT_POSITIVE" in result["issues"]


def test_archive_selector_uses_completed_asof_not_directory_name(tmp_path):
    def save(name, data, status="success"):
        run = tmp_path / name
        private = run / "portfolio-private"
        private.mkdir(parents=True)
        (run / "run.json").write_text(json.dumps({"status": status}))
        (private / "status.json").write_text(json.dumps({"status": status}))
        path = private / "account_snapshot.json"
        path.write_text(json.dumps(data))
        return path

    good = save("a", snapshot())
    data = snapshot()
    data["as_of"] = "2026-09-22T06:50:00+00:00"
    save("z", data)
    data["as_of"] = "2026-09-22T09:00:00+00:00"
    save("future", data)
    save("failed", snapshot(), "failed")
    assert select_latest(tmp_path, now=NOW) == {"US": good}


def test_completed_all_cash_view_supersedes_older_holdings(tmp_path):
    for name, stamp, positions in (
        ("old", "2026-09-22T06:40:00+00:00", snapshot()["positions"]),
        ("new", "2026-09-22T06:59:00+00:00", []),
    ):
        run = tmp_path / name
        private = run / "portfolio-private"
        private.mkdir(parents=True)
        data = snapshot()
        data.update(as_of=stamp, positions=positions)
        (run / "run.json").write_text(
            json.dumps({"status": "success", "settings": {"market": "us"}})
        )
        (private / "status.json").write_text(json.dumps({"status": "success"}))
        (private / "account_snapshot.json").write_text(json.dumps(data))
    assert select_latest(tmp_path, now=NOW)["US"].parent.parent.name == "new"
