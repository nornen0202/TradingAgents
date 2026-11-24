from __future__ import annotations

import json

try:
    import pytest
except ModuleNotFoundError:  # pragma: no cover - CI unittest import compatibility.
    from tests.pytest_compat import pytest

from tradingagents.portfolio.benchmarks.dca_engine import build_etf_dca_comparison

from .helpers import (
    build_fixture_comparison,
    default_broker_summary,
    default_settings,
    default_snapshot,
)


def test_aggregate_only_broker_summary_marks_exact_benchmark_unavailable(etf_fixture_dir):
    settings = default_settings(etf_fixture_dir, use_cashflows=False)

    result = build_fixture_comparison(etf_fixture_dir, settings=settings)
    public = result.to_public_dict()

    assert public["status"] == "cashflow_dates_required"
    assert public["reason"] == "dated_cashflows_missing"
    assert public["exact_dated_cashflows_available"] is False
    assert "requires dated cashflows" in public["message"]


def test_exact_comparison_uses_broker_actual_and_same_cashflows(etf_fixture_dir):
    expected = json.loads((etf_fixture_dir / "expected_etf_dca_comparison.json").read_text(encoding="utf-8"))

    result = build_fixture_comparison(etf_fixture_dir)
    public = result.to_public_dict()
    kospi = next(item for item in public["benchmarks"] if item["key"] == "KOSPI200_100")

    assert public["status"] == "OK"
    assert public["actual_source"] == expected["actual_source"]
    assert public["actual_return_pct"] == expected["actual_return_pct"]
    assert public["exact_dated_cashflows_available"] is True
    assert kospi["end_value_krw"] == expected["kospi200_final_value_krw"]
    assert kospi["balance_return_pct"] == pytest.approx(expected["kospi200_return_pct_approx"], abs=1e-5)
    assert public["actual_vs_benchmark"]["KOSPI200_100"]["winner"] == "benchmark"
    assert public["best_benchmark_id"] is not None


def test_period_mismatch_suppresses_excess_return(etf_fixture_dir):
    settings = default_settings(etf_fixture_dir)
    settings.etf_dca_period_end = "2026-05-13"

    result = build_etf_dca_comparison(
        snapshot=default_snapshot(),
        settings=settings,
        summary={},
        periods=[],
        broker_performance=default_broker_summary(etf_fixture_dir),
        reconciliation={"reconciliation_status": "FAILED"},
        warnings=[],
    )
    public = result.to_public_dict()
    kospi = next(item for item in public["benchmarks"] if item["key"] == "KOSPI200_100")

    assert public["period_match_status"] == "MISMATCH"
    assert kospi["excess_return_pct"] is None
    assert "etf_alternative_period_end_mismatch" in public["warnings"]

def test_internal_snapshot_does_not_turn_missing_ledger_into_exact_zero_cashflows(etf_fixture_dir):
    settings = default_settings(etf_fixture_dir, use_cashflows=False)
    broker_period = default_broker_summary(etf_fixture_dir)
    result = build_etf_dca_comparison(
        snapshot=default_snapshot(), settings=settings, summary={"default_period": "ALL"},
        periods=[{
            "period": "ALL", "start_date": broker_period.period_start, "end_date": broker_period.period_end,
            "actual_start_value_krw": 50000, "actual_end_value_krw": 52000, "actual_return": .04,
        }],
        broker_performance=None, reconciliation={"reconciliation_status": "OK"},
    )
    public = result.to_public_dict()
    assert public["status"] == "cashflow_evidence_unverified"
    assert public["exact_dated_cashflows_available"] is False
    assert public["actual"]["deposit_amount_krw"] is None
    kospi = next(item for item in public["alternatives"] if item["key"] == "KOSPI200_100")
    assert kospi["status"] == "research_only_unverified_cashflows"
    assert kospi["balance_return_pct"] is not None and kospi["excess_return_pct"] is None
    assert public["best_benchmark_id"] is None


def test_scheduled_ledger_uses_dates_before_applying_withdrawals(etf_fixture_dir):
    from dataclasses import replace
    from tradingagents.portfolio.performance.etf_alternatives import ExternalCapitalFlow

    deposit = ExternalCapitalFlow("2026-04-13", 20_000_000, "deposit")
    withdrawal = ExternalCapitalFlow("2026-04-20", 5_000_000, "withdrawal")
    broker = replace(default_broker_summary(etf_fixture_dir), start_asset_krw=0,
                     deposit_amount_krw=deposit.amount_krw, withdrawal_amount_krw=withdrawal.amount_krw)
    result = build_etf_dca_comparison(
        snapshot=default_snapshot(), settings=default_settings(etf_fixture_dir, use_cashflows=False),
        summary={}, periods=[], broker_performance=broker,
        reconciliation={"reconciliation_status": "FAILED"}, scheduled_cashflows=(withdrawal, deposit),
    )
    assert result.cashflows["source"] == "scheduled_account_ledger"
    kospi = next(item for item in result.alternatives if item.key == "KOSPI200_100")
    assert kospi.status == "OK"
    assert [transaction["source_flow_type"] for transaction in kospi.transactions] == ["deposit", "withdrawal"]
