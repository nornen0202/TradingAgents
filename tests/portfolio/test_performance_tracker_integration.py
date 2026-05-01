from tradingagents.performance.action_outcomes import record_run_recommendations, summarize_action_performance
from tradingagents.scheduled.site import _render_performance_tracking_section


def test_performance_unavailable_reason_rendered():
    html = _render_performance_tracking_section(
        {
            "run_id": "run1",
            "performance": {
                "enabled": True,
                "status": "ok",
                "outcome_update": {
                    "enabled": True,
                    "updated": False,
                    "provider": "none",
                    "unavailable_reason": "price_provider_unavailable_or_no_price_history",
                },
                "summary": {"recommendations": 1, "outcomes": 0},
            },
        }
    )

    assert "성과 추적: 기록은 저장됐지만 아직 성과 계산은 수행되지 않았습니다." in html
    assert "price_provider_unavailable_or_no_price_history" in html


def test_action_outcome_buckets_include_prism_uncovered(tmp_path):
    run_dir = tmp_path / "run"
    private = run_dir / "portfolio-private"
    private.mkdir(parents=True)
    (run_dir / "run.json").write_text('{"run_id":"run1","started_at":"2026-04-01T09:00:00+09:00"}', encoding="utf-8")
    (private / "portfolio_report.json").write_text(
        """
        {
          "actions": [
            {
              "canonical_ticker": "AAPL",
              "action_now": "WATCH",
              "action_if_triggered": "STARTER_IF_TRIGGERED",
              "portfolio_relative_action": "ADD",
              "delta_krw_now": 0,
              "confidence": 0.5,
              "data_health": {"prism_agreement": "no_same_market_prism_coverage"}
            }
          ]
        }
        """,
        encoding="utf-8",
    )
    db_path = tmp_path / "perf.sqlite"

    record_run_recommendations(run_dir, db_path)
    summary = summarize_action_performance(db_path)

    assert "PRISM-uncovered-current-market" in summary.action_buckets
