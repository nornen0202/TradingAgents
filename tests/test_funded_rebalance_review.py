import json
import sys

import pandas as pd
import pytest

from tools.review_funded_rebalance import main, price_series


def test_historical_reader_locally_excludes_future_prices(tmp_path):
    path = tmp_path / "fixture.csv"
    path.write_text(
        "Date,Close\n2026-10-22,999\n2026-10-19,100\n2026-10-20,101\n",
        encoding="utf8",
    )
    result = price_series(path, pd.Timestamp("2026-10-20"))
    assert list(result) == [100, 101]
    assert result.index.max() == pd.Timestamp("2026-10-20")


@pytest.mark.parametrize(
    "body",
    [
        "Date,Close\n",
        "Date,Close\n,100\n",
        "Date,Close\nbad-date,100\n",
        "Date,Close\n2026-10-19,100\n2026-10-19,101\n",
        "Date,Close\n2026-10-19,NaN\n",
        "Date,Close\n2026-10-19,inf\n",
        "Date,Close\n2026-10-19,0\n",
        "Date,Close\n2026-10-19,-10\n",
        "Date,Close\n2026-10-22,100\n",
    ],
)
def test_historical_reader_rejects_unverifiable_or_empty_history(tmp_path, body):
    path = tmp_path / "fixture.csv"
    path.write_text(body, encoding="utf8")
    with pytest.raises(ValueError):
        price_series(path, pd.Timestamp("2026-10-20"))


@pytest.mark.parametrize("unverified_jump", [False, True])
def test_offline_comparison_preserves_tax_reserve_and_flags_price_jumps(
    tmp_path, monkeypatch, unverified_jump
):
    source = {
        "markets": {
            "us": {
                "run_id": "fixture",
                "trade_plan": {"fx_krw_per_usd": 1},
                "rows": [
                    {
                        "ticker": "A",
                        "is_held": True,
                        "portfolio_action": {
                            "position_metrics": {"market_value_krw": 9000}
                        },
                    }
                ],
            }
        }
    }
    plan = {
        "us": {
            "status": "CONDITIONAL_FUNDED",
            "cash_ledger": {
                "nav_krw": 10000,
                "initial_cash_krw": 1000,
                "net_sale_funding_krw": 693,
                "capital_tax_reserve_krw": 198,
                "buy_total_krw": 101,
            },
            "sell_legs": [{"ticker": "A", "quantity": 10, "holding_quantity": 100}],
            "buy_legs": [{"ticker": "B", "gross_krw": 100}],
        }
    }
    for name, value in (("input.json", source), ("plan.json", plan)):
        (tmp_path / name).write_text(json.dumps(value), encoding="utf8")
    dates = pd.bdate_range("2025-01-02", periods=50)
    for ticker in ("A", "B", "KRW_X"):
        values = [1.0 if ticker == "KRW_X" else 100.0] * len(dates)
        if ticker == "A" and unverified_jump:
            values[10] = 50.0
        pd.DataFrame({"Close": values}, index=dates).to_csv(tmp_path / f"{ticker}.csv")
    output = tmp_path / "output"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "review",
            "--input",
            str(tmp_path / "input.json"),
            "--plan",
            str(tmp_path / "plan.json"),
            "--prices",
            str(tmp_path),
            "--output",
            str(output),
            "--analysis-as-of",
            "2025-12-31",
        ],
    )
    main()
    result = pd.read_csv(output / "historical_analogues.csv")
    rotation = result[result["policy"].eq("funded_rotation")].iloc[0]
    # Flat endpoints: 9 sale fees + 1 buy fee, with the 198 tax reserve still owned.
    assert rotation["total_return_pct"] == pytest.approx(-0.1)
    assert rotation["terminal_return_if_upper_tax_paid_pct"] == pytest.approx(-2.08)
    assert bool(rotation["usable_as_selection_evidence"]) is not unverified_jump
