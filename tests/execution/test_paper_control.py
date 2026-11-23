from datetime import datetime, timedelta, timezone
import sqlite3

import pytest

from tradingagents.execution.paper_control import PaperControlLedger, sign_paper_control


START = datetime(2026, 8, 4, 15, 0, tzinfo=timezone.utc)
KEY = b"local-fixture-paper-control-key-000"
RIGHTS = {"observe": {"observer"}, "halt": {"operator"}, "flatten": {"risk"}}


def request(action, actor, nonce, *, now=START):
    return {"action": action, "actor": actor, "nonce": f"test-nonce-{nonce:06}",
            "scope": "shadow-fixture", "mode": "isolated_paper",
            "expires_at": (now + timedelta(seconds=30)).isoformat()}


def snapshot(at, *, owned=None, sellable=None, clear=True):
    return {"mode": "isolated_paper", "scope": "shadow-fixture", "market": "US",
            "owned": owned or {}, "sellable": sellable or {}, "observed_at": at.isoformat(),
            "reconciled": True, "pending_orders_reconciled_empty": clear}


def quotes(at):
    return {"ABC": {"scope": "shadow-fixture", "market": "US", "currency": "USD",
                    "regular_executable": True, "observed_at": at.isoformat(), "bid": "40.50"}}


def test_signed_status_position_and_halt_controls_enforce_permission_and_expiry(tmp_path):
    at = [START]
    with PaperControlLedger(tmp_path / "control.sqlite", scope="shadow-fixture", market="US",
                            secret=KEY, rights=RIGHTS, clock=lambda: at[0]) as control:
        epoch = control.claim("writer", seconds=120)

        def send(row, *, actor=None, signature=None, **evidence):
            return control.execute(row, signature or sign_paper_control(KEY, row),
                                   actor=actor or row["actor"], writer="writer", epoch=epoch, **evidence)

        status = request("status", "observer", 1)
        assert send(status)["halted"] is False
        with pytest.raises(ValueError, match="Unauthorized"):
            send(status, actor="operator")
        with pytest.raises(ValueError, match="Unauthorized"):
            send(status, signature="damaged")
        with pytest.raises(ValueError, match="Unauthorized"):
            send(request("halt", "observer", 2))
        results = send(request("positions", "observer", 3),
                       snapshot=snapshot(at[0], owned={"ABC": "2"}, sellable={"ABC": "1"}))
        assert results["positions"] == {"ABC": "2"}
        assert send(request("halt", "operator", 4))["halted"] is True
        with pytest.raises(ValueError, match="already bound"):
            send(request("positions", "observer", 1), snapshot=snapshot(at[0]))
        at[0] += timedelta(seconds=31)
        with pytest.raises(ValueError, match="expired"):
            send(status)
        assert send(request("status", "observer", 6, now=at[0]))["halted"] is True


def test_failover_recovers_one_flatten_handoff_without_creating_a_second_sell(tmp_path):
    at = [START]
    path = tmp_path / "control.sqlite"
    control_params = {"scope": "shadow-fixture", "market": "US", "secret": KEY,
                      "rights": RIGHTS, "clock": lambda: at[0]}
    with PaperControlLedger(path, **control_params) as first, PaperControlLedger(path, **control_params) as second:
        epoch = first.claim("primary", seconds=4)
        with pytest.raises(RuntimeError, match="owns"):
            second.claim("standby")
        flatten = request("flatten", "risk", 1)
        signature = sign_paper_control(KEY, flatten)
        position = snapshot(at[0], owned={"ABC": "2"}, sellable={"ABC": "2"})
        evidence = {"snapshot": position, "quotes": quotes(at[0])}
        with pytest.raises(ValueError, match="halt"):
            first.execute(flatten, signature, actor="risk", writer="primary", epoch=epoch, **evidence)
        halt = request("halt", "operator", 2)
        first.execute(halt, sign_paper_control(KEY, halt), actor="operator", writer="primary", epoch=epoch)
        for adjustment, error in [
            ({"pending_orders_reconciled_empty": False}, "cancelled"),
            ({"sellable": {"ABC": "1"}}, "sellable"),
            ({"sellable": {"ABC": "3"}}, "exceed"),
        ]:
            with pytest.raises(ValueError, match=error):
                first.execute(flatten, signature, actor="risk", writer="primary", epoch=epoch,
                              snapshot=position | adjustment, quotes=quotes(at[0]))
        with pytest.raises(ValueError, match="quote"):
            first.execute(flatten, signature, actor="risk", writer="primary", epoch=epoch,
                          snapshot=position, quotes=quotes(at[0] - timedelta(seconds=16)))
        plan = first.execute(flatten, signature, actor="risk", writer="primary", epoch=epoch, **evidence)
        assert plan["requires_broker_revalidation"] is True
        assert plan["live_order_authority"] is False
        intent, = plan["paper_intents"]
        assert (intent["side"], intent["quantity"], intent["limit"]) == ("SELL", "2", "40.50")

        at[0] += timedelta(seconds=5)
        replacement = second.claim("standby")
        assert replacement > epoch
        with pytest.raises(RuntimeError, match="Stale"):
            first.flatten_recovery("primary", epoch)
        record = second.flatten_recovery("standby", replacement)
        assert record == {"state": "READY", "nonce": flatten["nonce"], "intent_ids": [intent["id"]]}
        assert second.execute(flatten, signature, actor="risk", writer="standby", epoch=replacement) == plan
        different = request("flatten", "risk", 3)
        with pytest.raises(ValueError, match="unused"):
            second.execute(different, sign_paper_control(KEY, different), actor="risk", writer="standby",
                           epoch=replacement, **evidence)
        with pytest.raises(ValueError, match="fresh flat"):
            second.finish_flatten("standby", replacement, nonce=flatten["nonce"],
                                  flat_snapshot=position, receipt_id="fixture-fill")
        for expected in (True, False):
            assert second.finish_flatten("standby", replacement, nonce=flatten["nonce"],
                                         flat_snapshot=snapshot(at[0]), receipt_id="fixture-fill") is expected
        assert second.flatten_recovery("standby", replacement)["state"] == "DONE"


def test_verified_backup_restores_halted_state_and_original_nonce(tmp_path):
    at = [START]
    source, copy = tmp_path / "controls.sqlite", tmp_path / "restored.sqlite"
    params = {"scope": "shadow-fixture", "market": "US", "secret": KEY,
              "rights": RIGHTS, "clock": lambda: at[0]}
    halt = request("halt", "operator", 12)
    with PaperControlLedger(source, **params) as original:
        epoch = original.claim("primary", seconds=3)
        original.execute(halt, sign_paper_control(KEY, halt), actor="operator", writer="primary", epoch=epoch)
        with sqlite3.connect(source.as_uri() + "?mode=ro", uri=True) as reader, sqlite3.connect(copy) as writer:
            reader.backup(writer)
            assert writer.execute("PRAGMA quick_check").fetchone() == ("ok",)
    at[0] += timedelta(seconds=4)
    status = request("status", "observer", 13, now=at[0])
    with PaperControlLedger(copy, **params) as restored:
        epoch = restored.claim("verified-standby")
        assert restored.execute(status, sign_paper_control(KEY, status), actor="observer",
                                writer="verified-standby", epoch=epoch)["halted"]
    with sqlite3.connect(copy) as reader:
        assert reader.execute("SELECT 1 FROM paper_control_commands WHERE nonce=?", (halt["nonce"],)).fetchone()


def test_expired_unsubmitted_flatten_can_be_renewed_by_fenced_writer(tmp_path):
    at = [START]
    params = {"scope": "shadow-fixture", "market": "US", "secret": KEY, "rights": RIGHTS, "clock": lambda: at[0]}
    with PaperControlLedger(tmp_path / "control.sqlite", **params) as control:
        epoch = control.claim("primary", seconds=4)
        halt = request("halt", "operator", 1)
        control.execute(halt, sign_paper_control(KEY, halt), actor="operator", writer="primary", epoch=epoch)
        old = request("flatten", "risk", 2)
        holding = {"owned": {"ABC": "2"}, "sellable": {"ABC": "2"}}
        initial = control.execute(old, sign_paper_control(KEY, old), actor="risk", writer="primary", epoch=epoch,
                                  snapshot=snapshot(at[0], **holding), quotes=quotes(at[0]))
        intent, = initial["paper_intents"]
        at[0] += timedelta(seconds=31)
        replacement = control.claim("standby")
        latest = request("flatten", "risk", 3, now=at[0])
        current = snapshot(at[0], **holding)
        args = dict(actor="risk", writer="standby", epoch=replacement, quotes=quotes(at[0]))
        with pytest.raises(ValueError, match="expired"):
            control.execute(old, sign_paper_control(KEY, old), snapshot=current, **args)
        with pytest.raises(ValueError, match="unsubmitted"):
            control.execute(latest, sign_paper_control(KEY, latest), snapshot=current, **args)
        renewed = control.execute(latest, sign_paper_control(KEY, latest),
                                  snapshot=current | {"unsubmitted_intent_ids": [intent["id"]]}, **args)
        updated, = renewed["paper_intents"]
        assert updated["id"] == intent["id"] and updated["expires_at"] != intent["expires_at"]
        assert renewed["flatten_nonce"] == initial["flatten_nonce"]


def test_partial_flatten_recovery_sells_only_the_proven_remaining_shares(tmp_path):
    at = [START]
    params = {"scope": "shadow-fixture", "market": "US", "secret": KEY, "rights": RIGHTS, "clock": lambda: at[0]}
    with PaperControlLedger(tmp_path / "control.sqlite", **params) as control:
        primary = control.claim("primary", seconds=2)
        halt = request("halt", "operator", 1)
        control.execute(halt, sign_paper_control(KEY, halt), actor="operator", writer="primary", epoch=primary)
        request_all = request("flatten", "risk", 2)
        plan = control.execute(request_all, sign_paper_control(KEY, request_all), actor="risk", writer="primary", epoch=primary,
                               snapshot=snapshot(at[0], owned={"ABC": "2"}, sellable={"ABC": "2"}), quotes=quotes(at[0]))
        previous, = plan["paper_intents"]
        at[0] += timedelta(seconds=5)
        standby = control.claim("standby")
        request_remainder = request("flatten", "risk", 3, now=at[0])
        proof = {previous["id"]: {"status": "CANCELED", "filled_quantity": "1", "receipt_id": "fixture-cancel-1"}}
        evidence = snapshot(at[0], owned={"ABC": "1"}, sellable={"ABC": "1"}) | {"terminal_flatten_orders": proof}
        args = dict(actor="risk", writer="standby", epoch=standby, quotes=quotes(at[0]))
        signature = sign_paper_control(KEY, request_remainder)
        with pytest.raises(ValueError, match="unfilled quantity"):
            control.execute(request_remainder, signature, snapshot=evidence | {"owned": {"ABC": "2"},
                            "sellable": {"ABC": "2"}}, **args)
        plan = control.execute(request_remainder, signature, snapshot=evidence, **args)
        remainder, = plan["paper_intents"]
        assert remainder["id"] != previous["id"] and remainder["quantity"] == "1"
        assert control.execute(request_remainder, signature, snapshot=evidence, **args) == plan
        assert control.flatten_recovery("standby", standby)["intent_ids"] == [remainder["id"]]


@pytest.mark.parametrize("evidence_type", ["positions", "quote"])
@pytest.mark.parametrize("clock", [None, "not-a-date", "2026-08-04T15:00:00", "2026-08-04T15:00:01Z"])
def test_invalid_or_future_observations_cannot_admit_flatten(tmp_path, evidence_type, clock):
    with PaperControlLedger(tmp_path / "control.sqlite", scope="shadow-fixture", market="US", secret=KEY,
                            rights=RIGHTS, clock=lambda: START) as control:
        epoch = control.claim("writer")
        halt = request("halt", "operator", 1)
        control.execute(halt, sign_paper_control(KEY, halt), actor="operator", writer="writer", epoch=epoch)
        command = request("flatten", "risk", 2)
        holdings, marks = snapshot(START, owned={"ABC": "1"}, sellable={"ABC": "1"}), quotes(START)
        source = holdings if evidence_type == "positions" else marks["ABC"]
        if clock is None:
            source.pop("observed_at")
        else:
            source["observed_at"] = clock
        with pytest.raises(ValueError):
            control.execute(command, sign_paper_control(KEY, command), actor="risk", writer="writer", epoch=epoch,
                            snapshot=holdings, quotes=marks)
        assert control.flatten_recovery("writer", epoch)["state"] == "NONE"
