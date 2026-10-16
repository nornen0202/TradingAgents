from dataclasses import asdict

import pytest

from tradingagents.execution.paper import PaperBroker, PaperLimits


def _quote(at, price):
    return {"A": {"as_of": at, "price_krw": price, "session": "regular",
                  "executable": True, "spread_bps": 2}}


def _signal(at, action, signal_id):
    return {"ticker": "A", "action": action, "signal_id": signal_id,
            "quantity": 1, "execution_ready": True, "available_at": at,
            "valid_until": at[:10] + "T15:00:00+09:00"}


def _seed(broker):
    broker.seed({"as_of": "2026-09-21T10:00:00+09:00",
                 "available_cash_krw": 50000,
                 "positions": [{"canonical_ticker": "A", "quantity": 500,
                                "market_price_krw": 100}]})


def _limits(**overrides):
    return PaperLimits(**{"cash_floor": 0, "max_daily_loss": 0.9,
                          "max_single_name": 0.9, "max_drawdown": 0.1,
                          **overrides})


def test_cumulative_drawdown_survives_day_and_restart_and_allows_reductions(tmp_path):
    path = tmp_path / "drawdown.sqlite"
    with_broker = PaperBroker(path, _limits())
    try:
        _seed(with_broker)
        peak_at = "2026-09-22T10:00:00+09:00"
        with_broker.step(now=peak_at, quotes=_quote(peak_at, 120), signals=[])
    finally:
        with_broker.close()
    broker = PaperBroker(path, _limits())
    try:
        at = "2026-09-23T10:00:00+09:00"
        result = broker.step(now=at, quotes=_quote(at, 96), signals=[
            _signal(at, "BUY", "buy"), _signal(at, "REDUCE", "reduce")])
        assert result["trading_state"] == "REDUCING"
        assert result["peak_nav_krw"] == 110000
        assert result["drawdown_fraction"] == pytest.approx(1 - 98000 / 110000)
        by_side = {order["side"]: order for order in result["orders"]}
        assert by_side["BUY"]["status"] == "REJECTED"
        assert by_side["BUY"]["reason"] == "max_drawdown_reached"
        assert by_side["SELL"]["status"] == "PENDING"
        later = "2026-09-23T10:01:00+09:00"
        result = broker.step(now=later, quotes=_quote(later, 96), signals=[])
        assert next(o for o in result["orders"] if o["side"] == "SELL")["status"] == "FILLED"
        assert result["broker_orders_sent"] == 0
    finally:
        broker.close()


def test_breach_cancels_pending_buy_before_it_can_fill(tmp_path):
    broker = PaperBroker(tmp_path / "pending.sqlite", _limits())
    try:
        _seed(broker)
        at = "2026-09-22T10:00:00+09:00"
        assert broker.step(now=at, quotes=_quote(at, 120), signals=[
            _signal(at, "BUY", "pending")])["orders"][0]["status"] == "PENDING"
        later = "2026-09-22T10:01:00+09:00"
        order = broker.step(now=later, quotes=_quote(later, 96), signals=[])["orders"][0]
        assert order["status"] == "CANCELLED"
        assert order["reason"] == "max_drawdown_reached"
    finally:
        broker.close()


def test_fill_costs_crossing_cap_cancel_next_pending_buy_in_same_step(tmp_path):
    broker = PaperBroker(tmp_path / "fill-costs.sqlite", _limits(max_drawdown=0.00001, fee_bps=100))
    try:
        _seed(broker)
        at = "2026-09-22T10:00:00+09:00"
        quotes = _quote(at, 100)
        quotes["B"] = dict(quotes["A"])
        second_buy = {**_signal(at, "BUY", "second"), "ticker": "B"}
        queued = broker.step(now=at, quotes=quotes, signals=[
            _signal(at, "BUY", "first"), second_buy])
        assert all(order["status"] == "PENDING" for order in queued["orders"])

        later = "2026-09-22T10:01:00+09:00"
        quotes = _quote(later, 100)
        quotes["B"] = dict(quotes["A"])
        result = broker.step(now=later, quotes=quotes, signals=[])

        by_ticker = {order["ticker"]: order for order in result["orders"]}
        assert by_ticker["A"]["status"] == "FILLED"
        assert by_ticker["B"]["status"] == "CANCELLED"
        assert by_ticker["B"]["reason"] == "max_drawdown_reached"
        first = by_ticker["A"]
        loss = first["fill_price"] - 100 + first["cost"]
        assert result["nav_krw"] == pytest.approx(100000 - loss)
        assert result["drawdown_fraction"] > broker.limits.max_drawdown
        assert result["trading_state"] == "REDUCING"
    finally:
        broker.close()


def test_drawdown_limit_blocks_at_exact_boundary_and_clears_on_recovery(tmp_path):
    broker = PaperBroker(tmp_path / "boundary.sqlite", _limits())
    try:
        _seed(broker)
        at = "2026-09-22T10:00:00+09:00"
        result = broker.step(now=at, quotes=_quote(at, 80), signals=[
            _signal(at, "BUY", "boundary")])
        assert result["nav_krw"] == 90000
        assert result["drawdown_fraction"] == pytest.approx(0.1)
        assert result["trading_state"] == "REDUCING"
        assert result["orders"][0]["reason"] == "max_drawdown_reached"

        recovered = "2026-09-22T10:01:00+09:00"
        result = broker.step(now=recovered, quotes=_quote(recovered, 80.01), signals=[
            _signal(recovered, "BUY", "recovered")])
        assert result["trading_state"] == "ACTIVE"
        assert next(order for order in result["orders"] if order["status"] == "PENDING")
    finally:
        broker.close()


def test_incomplete_marks_do_not_raise_peak_or_clear_breach(tmp_path):
    broker = PaperBroker(tmp_path / "marks.sqlite", _limits())
    try:
        _seed(broker)
        at = "2026-09-22T10:00:00+09:00"
        result = broker.step(now=at, quotes=_quote(at, 70), signals=[])
        assert result["trading_state"] == "REDUCING"
        missing = "2026-09-23T10:00:00+09:00"
        result = broker.step(now=missing, quotes={}, signals=[])
        assert result["drawdown_fraction"] is None
        assert result["trading_state"] == "REDUCING"
        recovered = "2026-09-24T10:00:00+09:00"
        result = broker.step(now=recovered, quotes=_quote(recovered, 100), signals=[])
        assert result["trading_state"] == "ACTIVE"
        assert result["drawdown_fraction"] == 0
    finally:
        broker.close()


def test_partial_account_revaluation_cannot_create_artificial_peak(tmp_path):
    broker = PaperBroker(tmp_path / "partial.sqlite", _limits())
    try:
        broker.seed({"as_of": "2026-09-21T10:00:00+09:00",
                     "available_cash_krw": 50000,
                     "positions": [{"canonical_ticker": ticker, "quantity": 250,
                                    "market_price_krw": 100} for ticker in ("A", "B")]})
        at = "2026-09-22T10:00:00+09:00"
        result = broker.step(now=at, quotes=_quote(at, 1000), signals=[])
        assert result["peak_nav_krw"] == 100000
        assert result["drawdown_fraction"] is None
    finally:
        broker.close()


def test_legacy_limits_keep_policy_and_new_cap_requires_new_experiment(tmp_path):
    path = tmp_path / "legacy.sqlite"
    broker = PaperBroker(path, _limits(max_drawdown=None))
    try:
        _seed(broker)
        legacy = asdict(broker.limits)
        del legacy["max_drawdown"]
        broker._set("limits", legacy)
        broker.db.execute("DELETE FROM state WHERE key='peak_nav'")
        at = "2026-09-22T10:00:00+09:00"
        result = broker.step(now=at, quotes=_quote(at, 70), signals=[])
        assert result["trading_state"] == "ACTIVE"
        assert result["peak_nav_krw"] == 100000
    finally:
        broker.close()
    broker = PaperBroker(path, _limits())
    try:
        with pytest.raises(ValueError, match="Limits changed"):
            broker.step(now="2026-09-23T10:00:00+09:00", quotes={}, signals=[])
    finally:
        broker.close()


@pytest.mark.parametrize("limit", [0, 1, -0.1, True, float("nan"), float("inf"), "0.15"])
def test_invalid_drawdown_limit_rejected(limit):
    with pytest.raises(ValueError):
        _limits(max_drawdown=limit)
