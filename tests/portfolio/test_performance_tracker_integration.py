import sqlite3
import sys
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

from tradingagents.performance.action_outcomes import record_run_recommendations, summarize_action_performance, update_action_outcomes
from tradingagents.performance.price_history import _fetch_yfinance_price_history
from tradingagents.scheduled.config import load_scheduled_config
from tradingagents.scheduled.runner import _run_performance_tracking
from tradingagents.scheduled.site import _render_performance_tracking_section


def test_performance_unavailable_reason_is_hidden_from_investor_section():
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

    assert html == ""


def test_action_recommendations_recorded_even_when_outcome_update_disabled(tmp_path):
    config_path = tmp_path / "scheduled_analysis.toml"
    config_path.write_text(
        """
[run]
tickers = ["AAPL"]

[storage]
archive_dir = "./archive"
site_dir = "./site"

[performance]
enabled = true
store_path = "./performance.sqlite"
update_outcomes_on_run = false
price_provider = "none"
""",
        encoding="utf-8",
    )
    config = load_scheduled_config(config_path)
    run_dir = tmp_path / "run"
    private = run_dir / "portfolio-private"
    private.mkdir(parents=True)
    (run_dir / "run.json").write_text(
        '{"run_id":"run1","started_at":"2026-04-01T09:00:00+09:00"}',
        encoding="utf-8",
    )
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
              "confidence": 0.5
            }
          ]
        }
        """,
        encoding="utf-8",
    )

    payload = _run_performance_tracking(
        config=config,
        run_dir=run_dir,
        started_at=datetime(2026, 4, 1, tzinfo=timezone.utc),
    )

    assert payload["status"] == "recorded_pending_outcomes"
    assert payload["recorded_recommendations"] == 1
    assert payload["summary"]["recommendations"] == 1
    assert payload["summary"]["outcomes"] == 0
    assert payload["outcome_update"]["unavailable_reason"] == "outcome_update_disabled"


def test_outcome_update_failure_does_not_discard_recorded_recommendations(tmp_path):
    config_path = tmp_path / "scheduled_analysis.toml"
    config_path.write_text(
        """
[run]
tickers = ["AAPL"]

[storage]
archive_dir = "./archive"
site_dir = "./site"

[performance]
enabled = true
store_path = "./performance.sqlite"
update_outcomes_on_run = true
price_provider = "yfinance"
""",
        encoding="utf-8",
    )
    config = load_scheduled_config(config_path)
    run_dir = tmp_path / "run"
    private = run_dir / "portfolio-private"
    private.mkdir(parents=True)
    (run_dir / "run.json").write_text(
        '{"run_id":"run1","started_at":"2026-04-01T09:00:00+09:00"}',
        encoding="utf-8",
    )
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
              "confidence": 0.5
            }
          ]
        }
        """,
        encoding="utf-8",
    )

    with patch(
        "tradingagents.scheduled.runner.load_price_history_for_recommendations",
        side_effect=TypeError("float() argument must be a string or a real number, not 'Series'"),
    ):
        payload = _run_performance_tracking(
            config=config,
            run_dir=run_dir,
            started_at=datetime(2026, 4, 1, tzinfo=timezone.utc),
        )

    assert payload["status"] == "recorded_pending_outcomes"
    assert payload["summary"]["recommendations"] == 1
    assert payload["outcome_update"]["unavailable_reason"] == "outcome_update_failed"
    assert "Series" in payload["outcome_update"]["failure_reason"]


def test_yfinance_close_dataframe_is_converted_to_scalar_rows(monkeypatch):
    import pandas as pd

    dates = pd.to_datetime(["2026-04-01", "2026-04-02"])
    frame = pd.DataFrame({("Close", "AAPL"): [100.0, 103.0]}, index=dates)
    fake_yfinance = SimpleNamespace(download=lambda *args, **kwargs: frame)
    monkeypatch.setitem(sys.modules, "yfinance", fake_yfinance)

    history, warnings = _fetch_yfinance_price_history(
        ["AAPL"],
        benchmark_ticker=None,
        lookback_days=5,
        asof_date="2026-04-02",
    )

    assert history["AAPL"][0]["close"] == 100.0
    assert history["AAPL"][1]["close"] == 103.0
    assert not any("Series" in warning for warning in warnings)


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


def test_action_lift_calibration_metrics_are_recorded_and_rendered(tmp_path):
    run_dir = tmp_path / "run"
    private = run_dir / "portfolio-private"
    private.mkdir(parents=True)
    (run_dir / "run.json").write_text('{"run_id":"run1","started_at":"2026-04-01T09:00:00+09:00"}', encoding="utf-8")
    (private / "portfolio_report.json").write_text(
        """
        {
          "actions": [
            {
              "canonical_ticker": "009150.KS",
              "action_now": "WATCH",
              "action_if_triggered": "NONE",
              "portfolio_relative_action": "WATCH",
              "delta_krw_now": 0,
              "confidence": 0.8,
              "data_health": {
                "last_price": 1000000,
                "prism_agreement": "conflict_prism_sell_ta_buy",
                "action_lift": {
                  "lift_status": "ACTION_LIFT_FAILURE",
                  "opportunity_cost_score": 0.85,
                  "pilot_allowed": true,
                  "full_size_allowed": false
                }
              }
            }
          ]
        }
        """,
        encoding="utf-8",
    )
    db_path = tmp_path / "perf.sqlite"

    record_run_recommendations(run_dir, db_path)
    update_action_outcomes(
        db_path,
        "2026-04-08",
        price_history={
            "009150.KS": [
                {"date": "2026-04-01", "close": 1000000},
                {"date": "2026-04-02", "close": 1020000},
                {"date": "2026-04-03", "close": 1050000},
            ]
        },
    )
    summary = summarize_action_performance(db_path)
    html = _render_performance_tracking_section(
        {
            "run_id": "run1",
            "performance": {
                "enabled": True,
                "status": "ok",
                "outcome_update": {"enabled": True, "updated": True},
                "summary": summary.to_dict(),
            },
        }
    )

    assert summary.calibration["actionable_not_ordered_count"] == 1
    assert summary.calibration["actionable_not_ordered_rate"] == 1.0
    assert summary.calibration["missed_upside_5d"] is not None
    assert "액션 승격 미주문 비율" in html


def test_calibration_denominator_excludes_scanner_and_prism_rows(tmp_path):
    run_dir = tmp_path / "run"
    private = run_dir / "portfolio-private"
    scanner = run_dir / "scanner"
    prism = run_dir / "external_signals"
    private.mkdir(parents=True)
    scanner.mkdir()
    prism.mkdir()
    (run_dir / "run.json").write_text('{"run_id":"run1","started_at":"2026-04-01T09:00:00+09:00"}', encoding="utf-8")
    (private / "portfolio_report.json").write_text(
        """
        {
          "actions": [
            {
              "canonical_ticker": "009150.KS",
              "action_now": "WATCH",
              "action_if_triggered": "NONE",
              "portfolio_relative_action": "WATCH",
              "delta_krw_now": 0,
              "confidence": 0.8,
              "data_health": {
                "action_lift": {
                  "lift_status": "ACTION_LIFT_FAILURE",
                  "opportunity_cost_score": 0.85,
                  "pilot_allowed": true,
                  "full_size_allowed": false
                }
              }
            }
          ]
        }
        """,
        encoding="utf-8",
    )
    (scanner / "scanner_candidates.json").write_text(
        """
        {
          "candidates": [
            {"ticker": "000001.KS", "final_score": 80},
            {"ticker": "000002.KS", "final_score": 79},
            {"ticker": "000003.KS", "final_score": 78},
            {"ticker": "000004.KS", "final_score": 77},
            {"ticker": "000005.KS", "final_score": 76}
          ]
        }
        """,
        encoding="utf-8",
    )
    (prism / "prism_signals.json").write_text(
        """
        {
          "signals": [
            {"canonical_ticker": "000006.KS", "signal_action": "BUY", "current_price": 1000},
            {"canonical_ticker": "000007.KS", "signal_action": "BUY", "current_price": 1000},
            {"canonical_ticker": "000008.KS", "signal_action": "BUY", "current_price": 1000},
            {"canonical_ticker": "000009.KS", "signal_action": "BUY", "current_price": 1000}
          ]
        }
        """,
        encoding="utf-8",
    )
    db_path = tmp_path / "perf.sqlite"

    record_run_recommendations(run_dir, db_path)
    summary = summarize_action_performance(db_path)

    assert summary.recommendations == 10
    assert summary.calibration["action_lift_denominator_count"] == 1
    assert summary.calibration["actionable_not_ordered_count"] == 1
    assert summary.calibration["actionable_not_ordered_rate"] == 1.0
    assert summary.calibration["scanner_candidate_skipped_count"] == 5
    assert summary.calibration["prism_candidate_skipped_count"] == 4


def test_take_profit_if_triggered_is_tracked_as_profit_like(tmp_path):
    run_dir = tmp_path / "run"
    private = run_dir / "portfolio-private"
    private.mkdir(parents=True)
    (run_dir / "run.json").write_text('{"run_id":"run1","started_at":"2026-04-01T09:00:00+09:00"}', encoding="utf-8")
    (private / "portfolio_report.json").write_text(
        """
        {
          "actions": [
            {
              "canonical_ticker": "005930.KS",
              "action_now": "HOLD",
              "action_if_triggered": "TAKE_PROFIT_IF_TRIGGERED",
              "portfolio_relative_action": "REDUCE_RISK",
              "risk_action": "REDUCE_RISK",
              "sell_intent": "TAKE_PROFIT",
              "sell_trigger_status": "IF_TRIGGERED",
              "sell_size_plan": "PARTIAL_20",
              "delta_krw_now": 0,
              "confidence": 0.7,
              "position_metrics": {"current_price": 100000, "unrealized_return_pct": 20.0, "profit_protection_score": 0.7},
              "profit_taking_plan": {"enabled": true, "stage_1_price": 101000, "stage_1_fraction": 0.20, "reason_codes": ["PROFIT_TAKING"]}
            }
          ]
        }
        """,
        encoding="utf-8",
    )
    db_path = tmp_path / "perf.sqlite"

    record_run_recommendations(run_dir, db_path)
    update_action_outcomes(
        db_path,
        "2026-04-08",
        price_history={
            "005930.KS": [
                {"date": "2026-04-01", "close": 100000},
                {"date": "2026-04-02", "close": 99000},
                {"date": "2026-04-03", "close": 97000},
                {"date": "2026-04-06", "close": 95000},
                {"date": "2026-04-07", "close": 96000},
                {"date": "2026-04-08", "close": 94000},
            ]
        },
    )
    summary = summarize_action_performance(db_path)

    assert "TAKE_PROFIT_IF_TRIGGERED" in summary.profit_taking
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT r.sell_intent, r.unrealized_return_pct, o.outcome_label, o.avoided_drawdown_20d
            FROM action_recommendations r
            JOIN action_outcomes o ON o.recommendation_id = r.id
            """
        ).fetchone()
    assert row[0] == "TAKE_PROFIT"
    assert row[1] == 20.0
    assert row[2] == "avoided_loss"
    assert row[3] > 0
