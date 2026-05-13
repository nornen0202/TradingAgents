from __future__ import annotations

import json

import pytest

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
