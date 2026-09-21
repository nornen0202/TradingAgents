import json

from tools.paper_from_archive import build_step
from tradingagents.execution.paper import PaperBroker


def archive(tmp_path, *, budget=90000, expiry="2026-09-21T10:02:00+09:00"):
    at = "2026-09-21T10:00:00+09:00"
    data = {
        "run.json": {"status": "success"},
        "portfolio-private/account_snapshot.json": {
            "as_of": at,
            "account_value_krw": 10000000,
            "available_cash_krw": 10000000,
            "positions": [],
        },
        "portfolio-private/proposed_orders.json": {
            "orders": [
                {"canonical_ticker": "TEST", "side": "BUY", "delta_krw_now": budget}
            ]
        },
        "decision_bundle_v2.json": {
            "market": "kr",
            "generated_at": at,
            "analysis_source_run_id": "synthetic",
            "strategy_table": [
                {
                    "ticker": "TEST",
                    "last_price": 20000,
                    "spread_bps": 5,
                    "market_data_asof": at,
                    "market_session": "regular",
                    "quality": {
                        "execution_ready": True,
                        "generated_in_current_run": True,
                    },
                    "raw_codes": {"decision_now": "STARTER_NOW"},
                }
            ],
        },
        "tickers/TEST/execution_contract.json": {"entry_valid_until": expiry},
    }
    for name, value in data.items():
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(value), encoding="utf-8")
    return build_step(tmp_path, at)


def test_unheld_symbol_budget_queues_then_fills_only_at_later_quote(tmp_path):
    snapshot, step, market = archive(tmp_path)
    assert market == "kr" and step["signals"][0]["quantity"] == 4
    broker = PaperBroker(tmp_path / "paper.sqlite")
    try:
        broker.seed(snapshot)
        broker.step(**step)
        assert broker.db.execute("SELECT status FROM orders").fetchone()[0] == "PENDING"
        later = "2026-09-21T10:00:30+09:00"
        step["quotes"]["TEST"]["as_of"] = later
        broker.step(now=later, quotes=step["quotes"], signals=[])
        assert broker.db.execute("SELECT status FROM orders").fetchone()[0] == "FILLED"
    finally:
        broker.close()


def test_explicit_budget_missing_and_expiry_are_preserved(tmp_path):
    _, step, _ = archive(tmp_path, budget=None, expiry="2026-09-21T09:59:00+09:00")
    assert step["signals"][0]["quantity"] is None
    assert step["signals"][0]["valid_until"] == "2026-09-21T09:59:00+09:00"
