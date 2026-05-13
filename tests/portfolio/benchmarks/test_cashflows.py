from __future__ import annotations

from pathlib import Path

from tradingagents.portfolio.benchmarks.cashflows import load_dated_cashflows
from tradingagents.portfolio.benchmarks.models import CashflowSource, CashflowType


def test_manual_csv_aliases_create_dated_cashflows(tmp_path: Path):
    path = tmp_path / "cashflows.csv"
    path.write_text(
        "\n".join(
            [
                "event_date,cashflow_type,amount_local,currency,memo",
                "2026-04-13,DEPOSIT,10000000,KRW,initial",
                "2026-05-02,WITHDRAWAL,200000,KRW,withdrawal",
            ]
        ),
        encoding="utf-8",
    )

    flows = load_dated_cashflows(path)

    assert [flow.type for flow in flows] == [CashflowType.DEPOSIT, CashflowType.WITHDRAWAL]
    assert flows[0].source == CashflowSource.MANUAL_CSV
    assert flows[0].amount_krw == 10_000_000
    assert flows[1].amount_krw == -200_000
    assert flows[0].description == "initial"


def test_buy_sell_rows_are_not_external_cashflows(tmp_path: Path):
    path = tmp_path / "cashflows.csv"
    path.write_text(
        "\n".join(
            [
                "date,type,amount_krw",
                "2026-04-13,BUY,1000000",
                "2026-04-14,SELL,1000000",
                "2026-04-20,DEPOSIT,5000000",
            ]
        ),
        encoding="utf-8",
    )

    flows = load_dated_cashflows(path)

    assert len(flows) == 1
    assert flows[0].type == CashflowType.DEPOSIT
