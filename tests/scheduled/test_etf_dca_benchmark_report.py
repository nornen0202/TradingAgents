from __future__ import annotations

from tests.portfolio.benchmarks.helpers import build_fixture_comparison


def test_public_etf_dca_payload_has_required_report_fields():
    public = build_fixture_comparison().to_public_dict()

    assert public["exact_dated_cashflows_available"] is True
    assert public["actual_source"] == "broker_reported"
    assert public["benchmarks"]
    assert public["actual_vs_benchmark"]
    assert public["best_benchmark_id"]
    assert public["blended_benchmark_id"] == "BLENDED"
    assert public["cashflow_markers"] == [
        {"date": "2026-04-13", "flow_type": "deposit", "source": "baseline"},
        {"date": "2026-04-20", "flow_type": "deposit", "source": "baseline"},
    ]
    assert any(item.get("equity_curve") for item in public["benchmarks"])


def test_unavailable_payload_explains_dated_cashflows_missing():
    from tests.portfolio.benchmarks.helpers import default_settings

    settings = default_settings(use_cashflows=False)
    public = build_fixture_comparison(settings=settings).to_public_dict()

    assert public["exact_dated_cashflows_available"] is False
    assert public["reason"] == "dated_cashflows_missing"
    assert "dated cashflows" in public["message"]
