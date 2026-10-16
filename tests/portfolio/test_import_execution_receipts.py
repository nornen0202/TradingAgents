import json
import socket

import pytest

from tools.import_execution_receipts import import_receipts, main
from tradingagents.performance.replay import replay_action_history


ASOF = "2026-09-23T12:00:00+00:00"


def entry(fill_id="one", **changes):
    receipt = {"status": "PARTIALLY_FILLED", "source": "kis", "intent_id": "local-order", "fill_id": fill_id,
        "intent_at": "2026-09-21T00:00:00+00:00", "executed_at": "2026-09-21T00:01:00+00:00",
        "confirmed_at": "2026-09-21T00:01:01+00:00", "settled_at": "2026-09-23T00:00:00+00:00",
        "side": "BUY", "requested_quantity": 2, "filled_quantity": 1, "fill_price": 100, "cost": .1, "currency": "KRW"}
    receipt.update(changes)
    return {"recommendation": {"run_id": "run", "ticker": "A", "action": "STARTER_NOW",
        "created_at": "2026-09-21T00:00:00+00:00"}, "receipt": receipt}


def test_cli_imports_once_without_network_and_does_not_backdate(tmp_path, capsys, monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("Offline receipt importer must not use the network")
    monkeypatch.setattr(socket.socket, "connect", no_network)
    source, db = tmp_path / "receipts.json", tmp_path / "tracker.sqlite"
    source.write_text(json.dumps({"entries": [entry()]}), encoding="utf-8")
    args = ["--db", str(db), "--input", str(source), "--as-of", ASOF]
    assert main(args) == 0
    first = json.loads(capsys.readouterr().out)
    assert first["inserted_fills"] == 1 and first["broker_orders_sent"] == 0
    assert replay_action_history(db, analysis_as_of=ASOF)["fills"] == []
    assert len(replay_action_history(db, analysis_as_of=first["ingested_at"])["fills"]) == 1
    assert main(args) == 0
    second = json.loads(capsys.readouterr().out)
    assert second["inserted_fills"] == 0 and second["duplicate_fills"] == 1


@pytest.mark.parametrize("changes", [
    {"settled_at": "2026-09-24T00:00:00+00:00"}, {"confirmed_at": None},
    {"intent_at": "bad"}, {"cost": None}, {"filled_quantity": 3},
])
def test_invalid_batch_is_rejected_before_destination_is_opened(tmp_path, changes):
    db = tmp_path / "tracker.sqlite"
    with pytest.raises(ValueError):
        import_receipts(db, {"entries": [entry(), entry("bad", **changes)]}, as_of=ASOF)
    assert not db.exists()


def test_batch_conflict_rolls_back_preceding_valid_new_fill(tmp_path):
    db = tmp_path / "tracker.sqlite"
    first = import_receipts(db, entry(), as_of=ASOF)
    original = replay_action_history(db, analysis_as_of=first["ingested_at"])
    # The first new entry fits, but the second conflicts with a stored fill ID.
    with pytest.raises(ValueError, match="different evidence"):
        import_receipts(db, {"entries": [entry("new"), entry(cost=.2)]}, as_of=ASOF)
    assert replay_action_history(db, analysis_as_of="2026-12-31T00:00:00+00:00") == {**original, "analysis_as_of": "2026-12-31T00:00:00+00:00"}
