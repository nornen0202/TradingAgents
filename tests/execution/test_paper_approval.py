from datetime import datetime, timedelta, timezone
from copy import deepcopy

import pytest

from tradingagents.execution.paper_approval import PaperApproval, apply_telegram_paper_callback


NOW = datetime(2026, 10, 7, 14, tzinfo=timezone.utc)


def _proposal(**changes):
    return {"intent": "paper-1", "scope": "fixture-scope", "mode": "isolated_paper", "ticker": "ABC",
            "market": "US", "currency": "USD", "side": "BUY", "quantity": "3", "quantity_step": "1",
            "limit": "101", "expires_at": (NOW + timedelta(minutes=1)).isoformat(), **changes}


def _quote(at=NOW, **changes):
    return {"ticker": "ABC", "market": "US", "currency": "USD", "session_open": True,
            "observed_at": at.isoformat(), "ask": "100", "bid": "99", **changes}


def _ledger(path, clock=lambda: NOW):
    return PaperApproval(path, secret=b"synthetic-only-key".ljust(32, b"x"),
                         authorized=frozenset({"first", "second"}), clock=clock)


def test_callback_authentication_idempotency_reduction_and_durable_handoff(tmp_path):
    path = tmp_path / "proposals.sqlite"
    with _ledger(path) as ledger:
        callbacks = ledger.propose(_proposal())
        assert callbacks == ledger.propose(_proposal())
        assert all(len(value.encode()) <= 64 for value in callbacks.values())
        with pytest.raises(ValueError, match="Unauthorized"):
            ledger.decide(callbacks["reduce"], actor_id="outsider", delivery_id="a")
        with pytest.raises(ValueError, match="signature"):
            ledger.decide("A" + callbacks["reduce"][1:], actor_id="first", delivery_id="a")
        assert ledger.decide(callbacks["reduce"], actor_id="first", delivery_id="a")
        assert not ledger.decide(callbacks["reduce"], actor_id="first", delivery_id="a")
        with pytest.raises(ValueError, match="already has a decision"):
            ledger.decide(callbacks["approve"], actor_id="first", delivery_id="b")
        admission = ledger.consume("paper-1", scope="fixture-scope", quote=_quote())
        assert admission["quantity"] == "1" and not admission["live_order_authority"]
        with pytest.raises(ValueError, match="unused"):
            ledger.consume("paper-1", scope="fixture-scope", quote=_quote())
    with _ledger(path) as ledger:
        assert ledger.recover_admission("paper-1", scope="fixture-scope") == admission
        assert ledger.recover_admission("paper-1", scope="other-scope") is None


def test_revocation_expiry_and_rechecking_a_fresh_quote(tmp_path):
    clock = [NOW]
    with _ledger(tmp_path / "proposals.sqlite", lambda: clock[0]) as ledger:
        callbacks = ledger.propose(_proposal())
        ledger.decide(callbacks["approve"], actor_id="first", delivery_id="a")
        for quote in (_quote(at=NOW - timedelta(seconds=1)), _quote(currency="KRW"), _quote(ask="102"),
                      _quote(session_open=False)):
            with pytest.raises(ValueError):
                ledger.consume("paper-1", scope="fixture-scope", quote=quote)
        with pytest.raises(ValueError, match="approving actor"):
            ledger.decide(callbacks["revoke"], actor_id="second", delivery_id="r")
        assert ledger.decide(callbacks["revoke"], actor_id="first", delivery_id="r")
        with pytest.raises(ValueError, match="unused"):
            ledger.consume("paper-1", scope="fixture-scope", quote=_quote())
        expired = ledger.propose(_proposal(intent="paper-2"))
        clock[0] += timedelta(minutes=1)
        with pytest.raises(ValueError, match="expired"):
            ledger.decide(expired["approve"], actor_id="first", delivery_id="late")


def test_rejection_and_single_lot_cannot_turn_into_an_order(tmp_path):
    with _ledger(tmp_path / "proposals.sqlite") as ledger:
        callbacks = ledger.propose(_proposal(quantity="1"))
        with pytest.raises(ValueError, match="below one lot"):
            ledger.decide(callbacks["reduce"], actor_id="first", delivery_id="a")
        assert ledger.decide(callbacks["reject"], actor_id="first", delivery_id="b")
        with pytest.raises(ValueError, match="unused"):
            ledger.consume("paper-1", scope="fixture-scope", quote=_quote())
        with pytest.raises(ValueError, match="isolated"):
            ledger.propose(_proposal(intent="live", mode="real"))


def test_telegram_ingress_checks_webhook_actor_chat_message_origin_and_replay(tmp_path):
    secret = "isolated_fixture_webhook_secret_012345"
    with PaperApproval(tmp_path / "telegram.sqlite", secret=b"fixture-private-signing-key".ljust(32, b"x"),
                       authorized=frozenset({"1001"}), clock=lambda: NOW) as ledger:
        callbacks = ledger.propose(_proposal())
        update = {"update_id": 10, "callback_query": {"id": "query-1", "data": callbacks["approve"],
                  "from": {"id": 1001, "is_bot": False},
                  "message": {"chat": {"id": -1000001}, "from": {"id": 2001, "is_bot": True}}}}
        args = dict(supplied_secret=secret, webhook_secret=secret, bot_id=2001, allowed_chats={-1000001})
        with pytest.raises(ValueError, match="webhook"):
            apply_telegram_paper_callback(ledger, update, **(args | {"supplied_secret": "forged"}))
        for field, changed in (("chat", {"id": -1000002}), ("from", {"id": 3001, "is_bot": True})):
            other = deepcopy(update)
            other["callback_query"]["message"][field] = changed
            with pytest.raises(ValueError, match="scope"):
                apply_telegram_paper_callback(ledger, other, **args)
        other = deepcopy(update)
        other["callback_query"]["from"]["id"] = 9999
        with pytest.raises(ValueError, match="Unauthorized"):
            apply_telegram_paper_callback(ledger, other, **args)
        assert apply_telegram_paper_callback(ledger, update, **args)["status"] == "RECORDED"
        assert apply_telegram_paper_callback(ledger, update, **args)["status"] == "REPLAY"
        other = deepcopy(update)
        other["callback_query"]["data"] = callbacks["reject"]
        with pytest.raises(ValueError, match="different decision"):
            apply_telegram_paper_callback(ledger, other, **args)


@pytest.mark.parametrize("clock", [None, "not-a-date", "2026-10-07T14:00:00", "2026-10-07T14:00:01Z"])
def test_missing_or_invalid_quote_clocks_cannot_consume_approval(tmp_path, clock):
    with _ledger(tmp_path / "proposals.sqlite") as ledger:
        callbacks = ledger.propose(_proposal())
        ledger.decide(callbacks["approve"], actor_id="first", delivery_id="once")
        mark = _quote()
        if clock is None:
            mark.pop("observed_at")
        else:
            mark["observed_at"] = clock
        with pytest.raises(ValueError):
            ledger.consume("paper-1", scope="fixture-scope", quote=mark)
        assert ledger.recover_admission("paper-1", scope="fixture-scope") is None
