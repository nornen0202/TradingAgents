from datetime import datetime, timedelta, timezone
import json
import subprocess
import sys
import urllib.error

import pytest

from tradingagents.atomic_io import atomic_write_json
from tradingagents.execution.demo_runtime import MODE, SCHEMA
from tradingagents.notifications import local, strategy
from tradingagents.notifications.telegram import AtomicNotificationLedger, TelegramBotClient, TelegramNotSent


def test_strategy_outbox_deduplicates_lifecycle_and_excludes_identifiers(tmp_path):
    now = datetime.now(timezone.utc)
    filled_at = (now - timedelta(seconds=30)).isoformat()
    row = {"orders": [{"id": "PRIVATE_INTENT", "broker_id": "PRIVATE_BROKER_ID", "status": "FILLED",
                       "filled_quantity": 1, "first_fill_observed_at": filled_at, "ingested_at": now.isoformat(),
                       "source": "KIS_DEMO_BROKER_REPORT", "strategy_performance": True, "mode": "demo"}],
           "blockers": ["AMBIGUOUS_ORDER", "SOURCE_EXECUTION_EXPIRED"],
           "evaluation": {"sample": {"first_observed_at": (now - timedelta(days=2)).isoformat()},
                          "settlement_available_at": filled_at,
                          "cost_evidence_status": "COMPLETE_REVIEWED_IMPORT", "exact_fifo_available": True,
                          "realized_net_pnl": 0}}
    receipt = {"mode": MODE, "schema": SCHEMA, "enabled": True, "real_orders_enabled": False,
               "checked_at": now.isoformat(), "markets": {"US": row}}
    assert not strategy.queue_receipt(tmp_path, receipt)
    atomic_write_json(tmp_path / "notifications/kis-strategy-enabled.json", {"mode": MODE,
        "enabled": True, "real_orders_enabled": False, "enabled_at": (now - timedelta(minutes=1)).isoformat()})
    keys = strategy.queue_receipt(tmp_path, receipt)
    bumped = (now + timedelta(seconds=1)).isoformat()
    row["orders"][0]["ingested_at"] = bumped
    assert keys == strategy.queue_receipt(tmp_path, {**receipt, "checked_at": bumped})
    files = list((tmp_path / "notifications/events").glob("*.json"))
    assert len(files) == 3
    assert {json.loads(p.read_text(encoding="utf-8"))["event"] for p in files} == {"FILL", "ISSUE", "REALIZED_PNL"}
    assert all("PRIVATE" not in p.read_text(encoding="utf-8") for p in files)
    assert all(local.notify(key, tmp_path, tmp_path, dry_run=True)["status"] == "DRY_RUN" for key in keys)


def test_strategy_composition_loads_without_project_dependencies():
    subprocess.run([sys.executable, "-S", "-c", "from tradingagents.notifications.strategy import compose"], check=True)


@pytest.mark.parametrize("bad_time", [None, "bad", "2099-01-01T00:00:00Z"])
def test_no_event_for_missing_invalid_or_future_broker_evidence(tmp_path, bad_time):
    now = datetime.now(timezone.utc)
    atomic_write_json(tmp_path / "notifications/kis-strategy-enabled.json", {"mode": MODE,
        "enabled": True, "real_orders_enabled": False, "enabled_at": (now - timedelta(minutes=1)).isoformat()})
    row = {"orders": [{"id": "fixture", "status": "FILLED", "mode": "demo", "filled_quantity": 1,
                       "source": "KIS_DEMO_BROKER_REPORT", "strategy_performance": True,
                       "first_fill_observed_at": bad_time, "ingested_at": now.isoformat()}],
           "evaluation": {"settlement_available_at": bad_time, "cost_evidence_status": "COMPLETE_REVIEWED_IMPORT",
                          "exact_fifo_available": True, "realized_net_pnl": 0}}
    assert not strategy.queue_receipt(tmp_path, {"mode": MODE, "schema": SCHEMA, "enabled": True,
        "real_orders_enabled": False, "checked_at": now.isoformat(), "markets": {"US": row}})


@pytest.mark.parametrize("failure, calls, status", [
    (TimeoutError(), 1, "DELIVERY_UNKNOWN"),
    (urllib.error.URLError(ConnectionRefusedError()), 2, "SENT"),
])
def test_strategy_telegram_restarts_without_resending_ambiguous_requests(tmp_path, failure, calls, status):
    attempts = []

    def opener(*args, **kwargs):
        attempts.append(1)
        raise failure

    client = TelegramBotClient(bot_token="fixture-token", chat_id="123", opener=opener, max_attempts=2,
                               sleep=lambda seconds: None)
    options = dict(event_key="fixture", chunks=["report"], buttons=None, receipt_metadata={},
                   prevent_ambiguous_retries=True)
    path = tmp_path / "ledger.json"
    first = AtomicNotificationLedger(path)
    send = lambda text, buttons: client.send_message(text, buttons=buttons, conservative=True)
    if status == "SENT":
        with pytest.raises(TelegramNotSent):
            first.deliver(sender=send, **options)
    else:
        assert first.deliver(sender=send, **options)["status"] == "DELIVERY_UNKNOWN"
    assert len(attempts) == calls
    sent = []

    def recovered(text, buttons):
        sent.append(text)
        return 42

    restarted = AtomicNotificationLedger(path)
    assert restarted.deliver(sender=recovered, **options)["status"] == status
    assert sent == (["report"] if status == "SENT" else [])
