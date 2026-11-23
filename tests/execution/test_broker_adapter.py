from datetime import datetime, timedelta, timezone
from dataclasses import replace

import pytest

from tradingagents.execution.broker_adapter import Account, BrokerDispatcher, Intent, Order, subscription_budget


START = datetime(2026, 10, 1, 14, tzinfo=timezone.utc)


class BrokerFixture:
    kind = "kis_vts"
    mode = "fixture"
    market = "US"
    scope = "fixture-account"

    def __init__(self):
        self.now = START
        self.calls = []
        self.orders = {}
        self.drop_receipt = False

    def account(self):
        return Account(self.scope, "USD", self.now.isoformat(), "100", {"ABC": "2"})

    def submit(self, intent):
        self.calls.append(("submit", intent.id))
        order = Order(self.scope, intent.id, f"order-{intent.id}", "OPEN", "0", self.now.isoformat())
        self.orders[intent.id] = order
        if self.drop_receipt:
            raise TimeoutError("fixture accepted but disconnected")
        return order

    def find(self, client_id):
        self.calls.append(("find", client_id))
        return self.orders.get(client_id)

    def intent(self, identity="a", side="SELL", qty="1", price="80"):
        return Intent(identity, "ABC", side, qty, price, "USD", (START + timedelta(minutes=10)).isoformat())


def test_accept_then_disconnect_is_reconciled_after_failover_without_resubmission(tmp_path):
    broker = BrokerFixture()
    broker.drop_receipt = True
    path = tmp_path / "dispatch.sqlite"
    with BrokerDispatcher(path, broker, clock=lambda: broker.now) as first:
        epoch = first.claim("worker-1", seconds=3)
        intent = broker.intent()
        assert first.dispatch("worker-1", epoch, intent, broker.account()) == "UNKNOWN"
        assert first.dispatch("worker-1", epoch, intent, broker.account()) == "UNKNOWN"
        assert broker.calls == [("submit", "a")]
        with pytest.raises(RuntimeError, match="Reconcile"):
            first.dispatch("worker-1", epoch, broker.intent("b"), broker.account())
        with BrokerDispatcher(path, broker, clock=lambda: broker.now) as second:
            with pytest.raises(RuntimeError, match="lease"):
                second.claim("worker-2")
            broker.now += timedelta(seconds=4)
            next_epoch = second.claim("worker-2")
            assert next_epoch > epoch
            with pytest.raises(RuntimeError, match="stale"):
                first.reconcile("worker-1", epoch, intent.id)
            assert second.reconcile("worker-2", next_epoch, intent.id) == "OPEN"
            assert broker.calls == [("submit", "a"), ("find", "a")]


def test_pending_sells_and_old_account_proofs_cannot_sell_twice(tmp_path):
    broker = BrokerFixture()
    with BrokerDispatcher(tmp_path / "dispatch.sqlite", broker, clock=lambda: broker.now) as dispatcher:
        epoch = dispatcher.claim("worker")
        old_account = broker.account()
        assert dispatcher.dispatch("worker", epoch, broker.intent(qty="2"), old_account) == "OPEN"
        broker.now += timedelta(seconds=1)
        with pytest.raises(ValueError, match="inventory"):
            dispatcher.dispatch("worker", epoch, broker.intent("b"), broker.account())
        order = broker.orders["a"]
        partial = replace(order, status="PARTIAL", filled_quantity="1", observed_at=broker.now.isoformat())
        assert dispatcher.notice("worker", epoch, partial) == "PARTIAL"
        assert dispatcher.notice("worker", epoch, order) == "PARTIAL"
        with pytest.raises(ValueError, match="latest fill"):
            dispatcher.dispatch("worker", epoch, broker.intent("b"), old_account)
        with pytest.raises(ValueError, match="account"):
            dispatcher.notice("worker", epoch, replace(partial, scope="different-account"))
        broker.now += timedelta(seconds=1)
        with pytest.raises(ValueError, match="inventory"):
            dispatcher.dispatch("worker", epoch, broker.intent("b"), replace(broker.account(), sellable={"ABC": "1"}))


def test_account_shared_pacing_and_settled_cash_hard_gate(tmp_path):
    broker = BrokerFixture()
    path = tmp_path / "dispatch.sqlite"
    with BrokerDispatcher(path, broker, clock=lambda: broker.now) as dispatcher:
        epoch = dispatcher.claim("worker")
        assert dispatcher.dispatch("worker", epoch, broker.intent(), broker.account()) == "OPEN"
        with pytest.raises(RuntimeError, match="REST budget"):
            dispatcher.dispatch("worker", epoch, broker.intent("b"), broker.account())
        broker.now += timedelta(seconds=1)
        with pytest.raises(ValueError, match="settled cash"):
            dispatcher.dispatch("worker", epoch, broker.intent("b", side="BUY", price="101"), broker.account())
        with pytest.raises(ValueError, match="Intent"):
            dispatcher.dispatch("worker", epoch, broker.intent("b", qty=".5"), broker.account())
    broker.kind = "kis_live"
    with pytest.raises(ValueError, match="isolated"):
        BrokerDispatcher(path, broker, clock=lambda: broker.now)


def test_subscription_priority_retains_open_order_and_held_names():
    required = ["notice:KR", "notice:US", "active-order", "owned"]
    planned = subscription_budget(pinned=required, optional=["owned", *(f"candidate-{i}" for i in range(100))])
    assert planned[:4] == tuple(required) and len(planned) == 41
    with pytest.raises(ValueError, match="cannot cover"):
        subscription_budget(pinned=required, optional=[], limit=3)
