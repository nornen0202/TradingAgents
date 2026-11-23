import json

import pytest

from tradingagents.execution.paper_policy_v2 import SCHEMA, bind_v2_journal, main, size_v2_candidate

AT = "2026-09-08T14:05:00+00:00"
POLICY = {"schema": SCHEMA, "version": "fixture-v2", "scope": "v2-fixture", "broker": "kis_vts", "market": "US",
          "currency": "USD", "frozen_at": "2026-09-01T00:00:00+00:00", "cash_reserve_fraction": ".1",
          "max_order_fraction": ".05", "max_position_fraction": ".15", "max_sale_fraction": ".2",
          "fee_bps": "10", "drift_band_fraction": ".02", "max_quote_age_seconds": 30}
WATCH = {"version": "fixture-watch-v1", "market": "US", "known_at": POLICY["frozen_at"], "tickers": ["ABC"]}
SCOPE = {"scope": "v2-fixture", "market": "US", "currency": "USD", "observed_at": AT}
ACCOUNT = {**SCOPE, "mode": "isolated_paper", "reconciled": True, "settlement_verified": True,
           "portfolio_complete": True, "benchmark_fresh": True, "nav": "1000", "settled_cash": "300",
           "unsettled_cash": "100", "pending_buy_notional": "20", "pending_buys_by_ticker": {}, "positions": {}}
SIGNAL = {**SCOPE, "action_now": "STARTER_NOW", "execution_ready": True, "ticker": "ABC",
          "target_weight": ".20", "quantity": "10"}
QUOTE = {**SCOPE, "ticker": "ABC", "regular_executable": True, "ask": "30", "bid": "29.9",
         "fractionable": True, "fractional_quantity_step": ".25", "asset_observed_at": AT}


def sized(policy=POLICY, account=ACCOUNT, signal=SIGNAL, quote=QUOTE):
    return size_v2_candidate(policy, WATCH, account, signal, quote, as_of=AT)


def test_native_cash_lot_and_stale_fractional_asset_are_distinct():
    assert sized()["quantity"] == "1"
    assert sized(quote=QUOTE | {"ask": "60"})["status"] == "NO_ELIGIBLE_LOT"
    assert sized(account=ACCOUNT | {"settled_cash": "125"})["status"] == "NO_ELIGIBLE_LOT"
    assert sized(account=ACCOUNT | {"currency": "KRW"})["status"] == "SCOPE_MISMATCH"
    alpaca = POLICY | {"broker": "alpaca_paper"}
    assert sized(policy=alpaca)["quantity"] == "1.50"
    assert sized(policy=alpaca, quote=QUOTE | {"fractionable": False})["quantity"] == "1"
    assert sized(policy=alpaca, quote=QUOTE | {"asset_observed_at": None})["status"] == "UNVERIFIED_FRACTIONAL_ASSET"


@pytest.mark.parametrize("action", ["WAIT", "WATCH", "ADD_IF_TRIGGERED", "start", None])
def test_wait_or_conditional_signals_never_become_automatic_buys(action):
    assert sized(signal=SIGNAL | {"action_now": action})["status"] == "NO_CURRENT_STRATEGY_ACTION"


def test_buy_requires_benchmark_scope_and_drift_and_sell_is_bounded_by_sellable_inventory():
    blocked = ACCOUNT | {"portfolio_complete": False, "benchmark_fresh": False}
    assert sized(account=blocked)["status"] == "BUY_COVERAGE_OR_WATCHLIST_BLOCKED"
    held = ACCOUNT | {"positions": {"ABC": {"owned": "2", "sellable": "2", "pending_sell": "1"}}}
    assert sized(account=held, signal=SIGNAL | {"target_weight": ".07"})["status"] == "WITHIN_DRIFT_BAND"
    concentrated = held | {"positions": {"ABC": {"owned": "5", "sellable": "5", "pending_sell": "1"}}}
    assert sized(account=concentrated)["status"] == "NO_ELIGIBLE_LOT"
    sell = SIGNAL | {"action_now": "EXIT_NOW", "verified_risk_reduction": True}
    assert sized(account=held | {"portfolio_complete": False}, signal=sell)["quantity"] == "1"
    assert sized(account=held, signal=sell | {"verified_risk_reduction": False})["status"] == "SELL_RISK_REDUCTION_UNVERIFIED"


def test_v2_journal_binds_one_policy_and_watchlist_per_lane(tmp_path, capsys):
    state = tmp_path / "state"
    journal = bind_v2_journal(state, POLICY, WATCH, as_of=AT)
    assert journal.is_file() and journal.is_relative_to(state / "paper-v2")
    assert bind_v2_journal(state, POLICY, WATCH, as_of=AT) == journal
    with pytest.raises(ValueError, match="different policy"):
        bind_v2_journal(state, POLICY, WATCH | {"version": "another"}, as_of=AT)
    folder = tmp_path / "candidate.json"
    folder.write_text(json.dumps(dict(policy=POLICY, watchlist=WATCH, account=ACCOUNT, signal=SIGNAL, quote=QUOTE)))
    assert main([str(folder), "--journal-root", str(state), "--as-of", AT]) == 0
    saved = json.loads(capsys.readouterr().out)
    assert saved["v2_journal_bound"] is True and saved["live_order_authority"] is False


@pytest.mark.parametrize("target", ["account", "signal", "quote", "asset", "policy", "watchlist"])
@pytest.mark.parametrize("bad_clock", [None, "invalid-date", "2026-09-08T14:06:00+00:00", "2026-09-08T14:05:00"])
def test_v2_rejects_unavailable_invalid_naive_and_future_evidence(target, bad_clock):
    inputs = dict(policy=dict(POLICY), watchlist=dict(WATCH), account=dict(ACCOUNT), signal=dict(SIGNAL), quote=dict(QUOTE))
    field = {"policy": "frozen_at", "watchlist": "known_at", "asset": "asset_observed_at"}.get(target, "observed_at")
    if target == "asset":
        inputs["policy"]["broker"] = "alpaca_paper"
    row = inputs["quote" if target == "asset" else target]
    if bad_clock is None:
        row.pop(field)
    else:
        row[field] = bad_clock
    if target in {"policy", "watchlist"}:
        with pytest.raises(ValueError):
            size_v2_candidate(**inputs, as_of=AT)
    else:
        assert size_v2_candidate(**inputs, as_of=AT)["status"] != "PAPER_CANDIDATE"


def test_v2_empty_broker_or_signal_payloads_have_no_order_authority():
    assert sized(account={})["status"] == "SCOPE_MISMATCH"
    assert sized(quote={})["status"] == "SCOPE_MISMATCH"
    assert sized(signal={})["status"] == "NO_CURRENT_STRATEGY_ACTION"
