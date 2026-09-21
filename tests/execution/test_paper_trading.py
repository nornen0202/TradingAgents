import pytest

from tradingagents.execution.paper import (
    PaperBroker,
    PaperLimits,
    kis_demo_order_preview,
)


@pytest.fixture
def broker(tmp_path):
    b = PaperBroker(
        tmp_path / "paper.sqlite", PaperLimits(cash_floor=100, max_order_nav=0.1)
    )
    b.seed(
        {
            "as_of": "2026-09-21T10:00:00+09:00",
            "available_cash_krw": 10000,
            "positions": [],
        }
    )
    yield b
    b.close()


def quote(at, **changes):
    return {
        "A": {
            "as_of": at,
            "price_krw": 100,
            "session": "regular",
            "executable": True,
            "spread_bps": 10,
            **changes,
        }
    }


def signal(**changes):
    return {
        "signal_id": "one",
        "ticker": "A",
        "action": "BUY",
        "quantity": 2,
        "execution_ready": True,
        "available_at": "2026-09-21T10:00:00+09:00",
        "valid_until": "2026-09-21T10:02:00+09:00",
        **changes,
    }


def test_next_snapshot_only_and_restart_idempotency(broker):
    at = "2026-09-21T10:00:00+09:00"
    first = broker.step(now=at, quotes=quote(at), signals=[signal()])
    assert first["orders"][0]["status"] == "PENDING"
    same = broker.step(
        now="2026-09-21T10:00:30+09:00", quotes=quote(at), signals=[signal()]
    )
    assert same["orders"][0]["status"] == "PENDING"
    later = "2026-09-21T10:01:00+09:00"
    done = broker.step(now=later, quotes=quote(later), signals=[signal()])
    assert len(done["orders"]) == 1
    assert done["orders"][0]["status"] == "FILLED"
    assert done["orders"][0]["fill_price"] > 100
    assert done["broker_orders_sent"] == 0
    assert done["cash_krw"] < 9800


@pytest.mark.parametrize(
    "changes",
    [
        {"executable": False},
        {"price_krw": float("nan")},
        {"spread_bps": None},
        {"session": "closed"},
        {"as_of": "2026-09-21T10:01:00+09:00"},
    ],
)
def test_invalid_quote_rejected(broker, changes):
    at = "2026-09-21T10:00:00+09:00"
    assert (
        broker.step(now=at, quotes=quote(at, **changes), signals=[signal()])["orders"][
            0
        ]["status"]
        == "REJECTED"
    )


def test_expired_pending_order_is_cancelled(broker):
    at = "2026-09-21T10:00:00+09:00"
    broker.step(now=at, quotes=quote(at), signals=[signal()])
    later = "2026-09-21T10:03:00+09:00"
    assert (
        broker.step(now=later, quotes=quote(later), signals=[])["orders"][0]["status"]
        == "CANCELLED"
    )


def test_cash_and_whole_share_limits(broker):
    at = "2026-09-21T10:00:00+09:00"
    r = broker.step(
        now=at, quotes=quote(at, price_krw=2000), signals=[signal(quantity=1)]
    )
    assert r["orders"][0]["reason"] == "whole_share_budget_or_holdings"


@pytest.mark.parametrize(
    "side,exception,expected",
    [
        ("SELL", 0, "FILLED"),
        ("BUY", 0, "REJECTED"),
        ("BUY", 0.05, "FILLED"),
    ],
)
def test_whole_share_policy_survives_queue_and_fill(
    tmp_path, side, exception, expected
):
    at = "2026-09-21T10:00:00+09:00"
    b = PaperBroker(
        tmp_path / "sizing.sqlite", PaperLimits(one_share_nav_ceiling=exception)
    )
    try:
        b.seed(
            {
                "as_of": at,
                "account_value_krw": 25000000,
                "available_cash_krw": 24200000,
                "positions": [
                    {"canonical_ticker": "A", "quantity": 1, "market_price_krw": 800000}
                ],
            }
        )
        b.step(
            now=at,
            quotes=quote(at, price_krw=800000),
            signals=[signal(action=side, quantity=1)],
        )
        later = "2026-09-21T10:01:00+09:00"
        result = b.step(now=later, quotes=quote(later, price_krw=800000), signals=[])
        assert result["orders"][0]["status"] == expected
    finally:
        b.close()


def test_kill_switch_cancels_pending(broker):
    at = "2026-09-21T10:00:00+09:00"
    broker.step(now=at, quotes=quote(at), signals=[signal()])
    later = "2026-09-21T10:01:00+09:00"
    assert (
        broker.step(now=later, quotes=quote(later), signals=[], halted=True)["orders"][
            0
        ]["status"]
        == "CANCELLED"
    )


def test_demo_preview_has_no_send_or_live_route():
    r = kis_demo_order_preview(
        ticker="005930", side="BUY", quantity=1, limit_price=70000
    )
    assert not r["send_enabled"]
    assert "openapivts" in r["base_url"]
    assert r["tr_id"] == "VTTC0012U"
    with pytest.raises(ValueError):
        kis_demo_order_preview(ticker="NVDA", side="BUY", quantity=1, limit_price=100)


def test_transaction_rolls_back_on_bad_timestamp(broker):
    with pytest.raises(ValueError):
        broker.step(
            now="2026-09-21T10:00:00+09:00",
            quotes=quote("2026-09-21T10:00:00"),
            signals=[],
        )
    assert broker._get("last_step") is None


def test_valuation_cash_is_not_all_buying_power(tmp_path):
    b = PaperBroker(
        tmp_path / "foreign.sqlite", PaperLimits(cash_floor=0, max_order_nav=0.1)
    )
    b.seed(
        {
            "as_of": "2026-09-21T10:00:00+09:00",
            "available_cash_krw": 1000,
            "buying_power_krw": 50,
            "account_value_krw": 12000,
            "positions": [
                {"canonical_ticker": "A", "quantity": 100.5, "market_price_krw": 100}
            ],
        }
    )
    assert b._get("cash") == 1950
    assert b._get("spendable") == 50
    at = "2026-09-21T10:00:00+09:00"
    result = b.step(now=at, quotes=quote(at), signals=[signal()])
    assert result["nav_krw"] == 12000
    assert result["orders"][0]["status"] == "REJECTED"
    b.close()


def test_persistent_ledger_survives_restart(tmp_path):
    path = tmp_path / "restart.sqlite"
    b = PaperBroker(path, PaperLimits(cash_floor=0, max_order_nav=0.1))
    b.seed(
        {
            "as_of": "2026-09-21T10:00:00+09:00",
            "available_cash_krw": 10000,
            "positions": [],
        }
    )
    at = "2026-09-21T10:00:00+09:00"
    b.step(now=at, quotes=quote(at), signals=[signal()])
    b.close()
    b = PaperBroker(path, PaperLimits(cash_floor=0, max_order_nav=0.1))
    later = "2026-09-21T10:01:00+09:00"
    result = b.step(now=later, quotes=quote(later), signals=[signal()])
    assert len(result["orders"]) == 1 and result["orders"][0]["status"] == "FILLED"
    b.close()


def test_signal_without_quantity_cannot_become_order(broker):
    at = "2026-09-21T10:00:00+09:00"
    result = broker.step(now=at, quotes=quote(at), signals=[signal(quantity=None)])
    assert result["orders"][0]["reason"] == "missing_integer_quantity"


def test_snapshot_cannot_be_used_before_available(broker):
    with pytest.raises(ValueError, match="before account"):
        broker.step(now="2026-09-21T09:59:59+09:00", quotes={}, signals=[])


def test_fill_cost_cannot_push_order_over_nav_limit(broker):
    at = "2026-09-21T10:00:00+09:00"
    broker.step(now=at, quotes=quote(at), signals=[signal(quantity=10)])
    later = "2026-09-21T10:01:00+09:00"
    result = broker.step(now=later, quotes=quote(later), signals=[])
    assert result["orders"][0]["status"] == "PENDING"
    assert result["cash_krw"] == 10000


def test_first_observation_loss_is_measured_from_seed(tmp_path):
    b = PaperBroker(tmp_path / "loss.sqlite")
    b.seed(
        {
            "as_of": "2026-09-21T10:00:00+09:00",
            "available_cash_krw": 0,
            "positions": [
                {"canonical_ticker": "A", "quantity": 100, "market_price_krw": 100}
            ],
        }
    )
    at = "2026-09-21T10:01:00+09:00"
    result = b.step(
        now=at, quotes=quote(at, price_krw=95), signals=[signal(action="SELL")]
    )
    assert result["orders"][0]["reason"] == "kill_or_daily_stop"
    later = "2026-09-21T10:01:30+09:00"
    recovered = b.step(
        now=later,
        quotes=quote(later),
        signals=[signal(signal_id="recovered", action="SELL")],
    )
    assert all(o["reason"] == "kill_or_daily_stop" for o in recovered["orders"])
    b.close()


@pytest.mark.parametrize(
    "extra",
    [{"snapshot_health": "INVALID_SNAPSHOT"}, {"pending_orders": [{"ticker": "A"}]}],
)
def test_incomplete_or_reserved_account_rejected(tmp_path, extra):
    b = PaperBroker(tmp_path / "invalid.sqlite")
    with pytest.raises(ValueError):
        b.seed(
            {
                "as_of": "2026-09-21T10:00:00+09:00",
                "available_cash_krw": 10000,
                "positions": [],
                **extra,
            }
        )
    b.close()
