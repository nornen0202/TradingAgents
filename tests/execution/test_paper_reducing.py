import pytest

from tradingagents.execution.paper import PaperBroker, PaperLimits


def quote(at, price):
    return {
        "A": {
            "as_of": at,
            "price_krw": price,
            "session": "regular",
            "executable": True,
            "spread_bps": 2,
        }
    }


@pytest.mark.parametrize("halted,expected", [(False, "FILLED"), (True, "REJECTED")])
def test_daily_loss_stops_buys_but_only_emergency_halt_stops_reductions(
    tmp_path, halted, expected
):
    start, middle, end = [f"2026-09-22T10:0{i}:00+09:00" for i in range(3)]
    b = PaperBroker(tmp_path / "paper.sqlite", PaperLimits(cash_floor=0))
    try:
        b.seed(
            {
                "as_of": start,
                "available_cash_krw": 90000,
                "positions": [
                    {"canonical_ticker": "A", "quantity": 100, "market_price_krw": 100}
                ],
            }
        )
        b.step(now=start, quotes=quote(start, 100), signals=[])
        common = {
            "ticker": "A",
            "quantity": 1,
            "execution_ready": True,
            "available_at": middle,
            "valid_until": "2026-09-22T10:10:00+09:00",
        }
        b.step(
            now=middle,
            quotes=quote(middle, 70),
            signals=[
                {**common, "signal_id": "buy", "action": "BUY"},
                {**common, "signal_id": "reduce", "action": "REDUCE"},
            ],
            halted=halted,
        )
        result = b.step(now=end, quotes=quote(end, 70), signals=[], halted=halted)
        assert result["trading_state"] == ("HALTED" if halted else "REDUCING")
        by_side = {r["side"]: r for r in result["orders"]}
        assert by_side["BUY"]["status"] == "REJECTED"
        assert by_side["SELL"]["status"] == expected
        assert b.db.execute("SELECT qty FROM positions WHERE ticker='A'").fetchone()[
            0
        ] == (99 if not halted else 100)
    finally:
        b.close()


def test_order_expires_at_boundary_not_after_it(tmp_path):
    at, end = "2026-09-22T10:00:00+09:00", "2026-09-22T10:01:00+09:00"
    b = PaperBroker(tmp_path / "paper.sqlite", PaperLimits(cash_floor=0))
    try:
        b.seed({"as_of": at, "available_cash_krw": 100000, "positions": []})
        b.step(
            now=at,
            quotes=quote(at, 100),
            signals=[
                {
                    "signal_id": "a",
                    "ticker": "A",
                    "action": "BUY",
                    "quantity": 1,
                    "execution_ready": True,
                    "available_at": at,
                    "valid_until": end,
                }
            ],
        )
        assert (
            b.step(now=end, quotes=quote(end, 100), signals=[])["orders"][0]["status"]
            == "CANCELLED"
        )
    finally:
        b.close()
