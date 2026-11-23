from datetime import datetime, timedelta, timezone
from dataclasses import replace

import pytest

from tradingagents.execution.broker_adapter import Account, BrokerDispatcher, ExecutionFill, Intent, Order, subscription_budget


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
        self.coarse_clock = False

    def account(self):
        self.calls.append(("account", self.market))
        return Account(self.scope, "USD", self.now.isoformat(), "100", {"ABC": "2"})

    def submit(self, intent):
        self.calls.append(("submit", intent.id))
        clock = self.now.isoformat(timespec="seconds" if self.coarse_clock else "auto")
        order = Order(self.scope, intent.id, f"order-{intent.id}", "OPEN", "0.00", clock)
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
        assert [call for call in broker.calls if call[0] == "submit"] == [("submit", "a")]
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
            assert [call for call in broker.calls if call[0] != "account"] == [("submit", "a"), ("find", "a")]


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
        fill = ExecutionFill("fixture-fill-1", "1", "80", "USD", broker.now.isoformat())
        partial = replace(order, status="PARTIAL", filled_quantity="1", observed_at=broker.now.isoformat(), fills=(fill,))
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


def test_shared_account_slot_hint_and_fill_identity_survive_restart(tmp_path):
    broker = BrokerFixture()
    path = tmp_path / "dispatch.sqlite"
    hint = dict(scope=broker.scope, market=broker.market, order_id="order-a")
    with BrokerDispatcher(path, broker, clock=lambda: broker.now) as dispatcher:
        epoch = dispatcher.claim("writer", seconds=3)
        account = dispatcher.account_snapshot("writer", epoch)
        with pytest.raises(RuntimeError, match="REST budget"):
            dispatcher.dispatch("writer", epoch, broker.intent(qty="2"), account)
        broker.now += timedelta(seconds=1)
        assert dispatcher.dispatch("writer", epoch, broker.intent(qty="2"), account) == "OPEN"
        with pytest.raises(ValueError, match="scope"):
            dispatcher.reconcile_broker_hint("writer", epoch, **(hint | {"scope": "another"}))
        with pytest.raises(RuntimeError, match="REST budget"):
            dispatcher.reconcile_broker_hint("writer", epoch, **hint)
    broker.now += timedelta(seconds=3)
    order = broker.orders["a"]
    first_fill = ExecutionFill("partial-a", "1", "80", "USD", broker.now.isoformat())
    partial = replace(order, status="PARTIAL", filled_quantity="1", observed_at=broker.now.isoformat())
    with BrokerDispatcher(path, broker, clock=lambda: broker.now) as dispatcher:
        epoch = dispatcher.claim("replacement")
        with pytest.raises(ValueError, match="fill identifiers"):
            dispatcher.notice("replacement", epoch, partial)
        broker.orders["a"] = replace(partial, fills=(first_fill,))
        assert dispatcher.reconcile_broker_hint("replacement", epoch, **hint) == "PARTIAL"
        broker.now += timedelta(seconds=1)
        next_fill = replace(first_fill, id="complete-a", occurred_at=broker.now.isoformat())
        full = replace(partial, status="FILLED", filled_quantity="2", observed_at=broker.now.isoformat())
        with pytest.raises(ValueError, match="different evidence"):
            dispatcher.notice("replacement", epoch, replace(full, fills=(replace(first_fill, quantity="2"),)))
        assert dispatcher.notice("replacement", epoch, replace(full, fills=(next_fill, first_fill))) == "FILLED"
        assert dispatcher.notice("replacement", epoch, replace(full, fills=(first_fill, next_fill))) == "FILLED"


def test_distinct_same_second_fills_and_later_terminal_confirmation_are_reconciled(tmp_path):
    broker = BrokerFixture()
    broker.now = START.replace(microsecond=500_000)
    broker.coarse_clock = True
    with BrokerDispatcher(tmp_path / "dispatch.sqlite", broker, clock=lambda: broker.now) as dispatcher:
        epoch = dispatcher.claim("writer")
        assert dispatcher.dispatch("writer", epoch, broker.intent(qty="2"), broker.account()) == "OPEN"
        order = broker.orders["a"]
        fill = ExecutionFill("first-same-second", "1", "80", "USD", START.isoformat())
        early = replace(fill, occurred_at=(START - timedelta(seconds=1)).isoformat())
        partial = replace(order, status="PARTIAL", filled_quantity="1", fills=(early,))
        with pytest.raises(ValueError, match="stable identity"):
            dispatcher.notice("writer", epoch, partial)
        assert dispatcher.notice("writer", epoch, replace(partial, fills=(fill,))) == "PARTIAL"
        final = replace(order, status="FILLED", filled_quantity="2", fills=(fill, replace(fill, id="second-same-second")))
        assert dispatcher.notice("writer", epoch, final) == "FILLED"
        assert dispatcher.notice("writer", epoch, order) == "FILLED"
        broker.now += timedelta(seconds=1)
        broker.orders["a"] = replace(final, observed_at=broker.now.isoformat(), fills=())
        assert dispatcher.reconcile("writer", epoch, "a") == "FILLED"


def test_numeric_zero_ack_does_not_count_as_a_fill(tmp_path):
    broker = BrokerFixture()
    with BrokerDispatcher(tmp_path / "dispatch.sqlite", broker, clock=lambda: broker.now) as dispatcher:
        epoch = dispatcher.claim("writer")
        snapshot = broker.account()
        assert dispatcher.dispatch("writer", epoch, broker.intent(), snapshot) == "OPEN"
        broker.now += timedelta(seconds=1)
        assert dispatcher.dispatch("writer", epoch, broker.intent("b"), snapshot) == "OPEN"
