import sqlite3
import sys
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

from tradingagents.performance.action_outcomes import (
    initialize_action_tracker,
    record_run_recommendations,
    summarize_action_performance,
    update_action_outcomes,
)
from tradingagents.performance.price_history import (
    PriceHistoryLoadResult,
    _fetch_yfinance_price_history,
    load_price_history_for_recommendations,
)
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
    assert payload["summary"]["data_quality"]["feedback_loop_status"] == "COUNTERFACTUAL_ONLY"
    assert payload["summary"]["data_quality"]["actual_trade_effectiveness_available"] is False


def test_proposed_allocation_is_not_mislabeled_as_actual_execution(tmp_path):
    run_dir = tmp_path / "run"
    private = run_dir / "portfolio-private"
    private.mkdir(parents=True)
    (run_dir / "run.json").write_text(
        '{"run_id":"proposal-only","started_at":"2026-04-01T09:00:00+09:00","settings":{"market":"US"}}',
        encoding="utf-8",
    )
    (private / "portfolio_report.json").write_text(
        """
        {
          "actions": [
            {
              "canonical_ticker": "AAPL",
              "action_now": "STARTER_NOW",
              "portfolio_relative_action": "ADD",
              "delta_krw_now": 1000000,
              "confidence": 0.8
            }
          ]
        }
        """,
        encoding="utf-8",
    )
    db_path = tmp_path / "performance.sqlite"

    inserted = record_run_recommendations(run_dir, db_path, run_market="US")
    summary = summarize_action_performance(db_path)
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT was_executed, execution_evidence, skip_reason FROM action_recommendations"
        ).fetchone()

    assert inserted == 1
    assert row == (0, None, "proposed_allocation_without_execution_receipt")
    assert summary.data_quality["broker_fill_linked_rows"] == 0
    assert summary.data_quality["actual_trade_effectiveness_available"] is False
    assert summary.data_quality["measurement_scope"] == "counterfactual_recommendation_price_path"


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


def test_yfinance_due_tickers_and_benchmark_are_downloaded_once(monkeypatch):
    import pandas as pd

    dates = pd.to_datetime(["2026-04-01", "2026-04-02"])
    frame = pd.DataFrame(
        {
            ("Close", "AAPL"): [100.0, 103.0],
            ("Close", "MSFT"): [200.0, 204.0],
            ("Close", "^GSPC"): [5000.0, 5050.0],
        },
        index=dates,
    )
    calls = []
    fake_yfinance = SimpleNamespace(download=lambda tickers, **kwargs: calls.append((tickers, kwargs)) or frame)
    monkeypatch.setitem(sys.modules, "yfinance", fake_yfinance)

    history, warnings = _fetch_yfinance_price_history(
        ["AAPL", "MSFT", "^GSPC"],
        benchmark_ticker="^GSPC",
        lookback_days=120,
        asof_date="2026-04-02",
    )

    assert len(calls) == 1
    assert set(calls[0][0]) == {"AAPL", "MSFT", "^GSPC"}
    assert calls[0][1]["threads"] is True
    assert calls[0][1]["timeout"] == 10
    assert history["AAPL"][1]["close"] == 103.0
    assert history["MSFT"][1]["close"] == 204.0
    assert history["__BENCHMARK__"][1]["close"] == 5050.0
    assert not any("no_close" in warning for warning in warnings)


def test_partial_batch_does_not_assign_another_tickers_close(monkeypatch):
    import pandas as pd

    dates = pd.to_datetime(["2026-04-01", "2026-04-02"])
    frame = pd.DataFrame({("Close", "AAPL"): [100.0, 103.0]}, index=dates)
    fake_yfinance = SimpleNamespace(download=lambda *args, **kwargs: frame)
    monkeypatch.setitem(sys.modules, "yfinance", fake_yfinance)

    history, warnings = _fetch_yfinance_price_history(
        ["AAPL", "MSFT"],
        benchmark_ticker=None,
        lookback_days=120,
        asof_date="2026-04-02",
    )

    assert "AAPL" in history
    assert "MSFT" not in history
    assert "performance_yfinance_no_close:MSFT" in warnings


def test_due_recommendation_ids_bind_download_and_incremental_update(tmp_path, monkeypatch):
    import pandas as pd

    db_path = tmp_path / "perf.sqlite"
    initialize_action_tracker(db_path)
    with sqlite3.connect(db_path) as conn:
        old_id = conn.execute(
            "INSERT INTO action_recommendations (run_id, ticker, market, action, created_at) VALUES (?, ?, ?, ?, ?)",
            ("old", "005930.KS", "KR", "WATCH", "2025-01-01T09:00:00+09:00"),
        ).lastrowid
        active_id = conn.execute(
            "INSERT INTO action_recommendations (run_id, ticker, market, action, created_at) VALUES (?, ?, ?, ?, ?)",
            ("active", "005930.KS", "KR", "WATCH", "2026-07-15T09:00:00+09:00"),
        ).lastrowid
        current_id = conn.execute(
            "INSERT INTO action_recommendations (run_id, ticker, market, action, created_at) VALUES (?, ?, ?, ?, ?)",
            ("current", "005930.KS", "KR", "WATCH", "2026-07-16T09:00:00+09:00"),
        ).lastrowid
        conn.execute(
            "INSERT INTO action_outcomes (recommendation_id, return_5d, return_60d, updated_at) VALUES (?, ?, ?, ?)",
            (old_id, 0.11, 0.25, "2025-05-01"),
        )
        conn.execute(
            "INSERT INTO action_outcomes (recommendation_id, return_5d, return_60d, calculation_version, updated_at) VALUES (?, ?, ?, ?, ?)",
            (active_id, 0.01, 0.02, 1, "2026-07-19"),
        )
        conn.execute(
            "INSERT INTO action_outcomes (recommendation_id, return_5d, return_60d, updated_at) VALUES (?, ?, ?, ?)",
            (current_id, 0.03, 0.04, "2026-07-20"),
        )
        conn.commit()

    dates = pd.to_datetime([f"2026-07-{day:02d}" for day in range(15, 21)])
    frame = pd.DataFrame({("Close", "005930.KS"): [100, 101, 102, 103, 104, 110]}, index=dates)
    calls = []
    fake_yfinance = SimpleNamespace(download=lambda ticker, **kwargs: calls.append(ticker) or frame)
    monkeypatch.setitem(sys.modules, "yfinance", fake_yfinance)

    result = load_price_history_for_recommendations(
        db_path,
        provider="yfinance",
        market="KR",
        lookback_days=120,
        asof_date="2026-07-20",
    )

    assert result.due_recommendation_ids == (active_id,)
    assert result.due_recommendation_count == 1
    assert calls == ["005930.KS"]

    update_action_outcomes(
        db_path,
        "2026-07-20",
        price_history=result.price_history,
        recommendation_ids=result.due_recommendation_ids,
    )
    with sqlite3.connect(db_path) as conn:
        outcomes = dict(
            conn.execute(
                "SELECT recommendation_id, return_5d FROM action_outcomes ORDER BY recommendation_id"
            ).fetchall()
        )
        versions = dict(
            conn.execute(
                "SELECT recommendation_id, calculation_version FROM action_outcomes ORDER BY recommendation_id"
            ).fetchall()
        )
        index_names = {row[1] for row in conn.execute("PRAGMA index_list(action_outcomes)")}
    assert outcomes[old_id] == 0.11
    assert outcomes[active_id] == 0.1
    assert outcomes[current_id] == 0.03
    assert versions[active_id] == 2
    assert "idx_action_outcomes_recommendation" in index_names

    second = load_price_history_for_recommendations(
        db_path,
        provider="yfinance",
        market="KR",
        lookback_days=120,
        asof_date="2026-07-20",
    )
    assert second.due_recommendation_count == 0
    assert calls == ["005930.KS"]


def test_existing_outcome_schema_is_versioned_and_scheduled_for_correction(tmp_path, monkeypatch):
    db_path = tmp_path / "legacy.sqlite"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE action_recommendations (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              run_id TEXT NOT NULL,
              ticker TEXT NOT NULL,
              action TEXT NOT NULL,
              created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE TABLE action_outcomes (recommendation_id INTEGER, return_60d REAL, updated_at TEXT)"
        )
        recommendation_id = conn.execute(
            "INSERT INTO action_recommendations (run_id, ticker, action, created_at) VALUES (?, ?, ?, ?)",
            ("legacy", "AAPL", "WATCH", "2026-07-15T09:00:00Z"),
        ).lastrowid
        conn.execute(
            "INSERT INTO action_outcomes (recommendation_id, return_60d, updated_at) VALUES (?, ?, ?)",
            (recommendation_id, 0.05, "2026-07-20"),
        )
        conn.commit()

    initialize_action_tracker(db_path)
    with sqlite3.connect(db_path) as conn:
        version = conn.execute(
            "SELECT calculation_version FROM action_outcomes WHERE recommendation_id = ?",
            (recommendation_id,),
        ).fetchone()[0]
        index_names = {row[1] for row in conn.execute("PRAGMA index_list(action_outcomes)")}
    assert version == 1
    assert "idx_action_outcomes_recommendation" in index_names

    calls = []
    fake_yfinance = SimpleNamespace(
        download=lambda ticker, **kwargs: calls.append(ticker) or SimpleNamespace(empty=True)
    )
    monkeypatch.setitem(sys.modules, "yfinance", fake_yfinance)
    result = load_price_history_for_recommendations(
        db_path,
        provider="yfinance",
        market="US",
        lookback_days=120,
        asof_date="2026-07-20",
    )

    assert result.due_recommendation_ids == (recommendation_id,)
    assert calls == ["AAPL"]


def test_immature_horizons_are_pending_and_future_recommendation_is_not_written(tmp_path):
    db_path = tmp_path / "perf.sqlite"
    initialize_action_tracker(db_path)
    with sqlite3.connect(db_path) as conn:
        active_id = conn.execute(
            "INSERT INTO action_recommendations (run_id, ticker, action, created_at) VALUES (?, ?, ?, ?)",
            ("active", "AAPL", "STARTER_NOW", "2026-04-01T09:00:00Z"),
        ).lastrowid
        future_id = conn.execute(
            "INSERT INTO action_recommendations (run_id, ticker, action, created_at) VALUES (?, ?, ?, ?)",
            ("future", "AAPL", "STARTER_NOW", "2026-05-01T09:00:00Z"),
        ).lastrowid
        weekend_boundary_id = conn.execute(
            "INSERT INTO action_recommendations (run_id, ticker, action, created_at) VALUES (?, ?, ?, ?)",
            ("weekend", "AAPL", "STARTER_NOW", "2026-03-29T09:00:00Z"),
        ).lastrowid
        conn.commit()

    update_action_outcomes(
        db_path,
        "2026-04-03",
        price_history={
            "AAPL": [
                {"date": "2026-04-01", "close": 100.0},
                {"date": "2026-04-02", "close": 102.0},
                {"date": "2026-04-03", "close": 103.0},
            ]
        },
        recommendation_ids=(active_id, future_id, weekend_boundary_id),
    )

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM action_outcomes WHERE recommendation_id = ?",
            (active_id,),
        ).fetchone()
        future_count = conn.execute(
            "SELECT COUNT(*) FROM action_outcomes WHERE recommendation_id = ?",
            (future_id,),
        ).fetchone()[0]
        weekend_row = conn.execute(
            "SELECT return_1d, return_3d FROM action_outcomes WHERE recommendation_id = ?",
            (weekend_boundary_id,),
        ).fetchone()
    assert row["return_1d"] == 0.02
    assert row["return_3d"] is None
    assert row["return_5d"] is None
    assert row["return_60d"] is None
    assert row["max_drawdown_20d"] is None
    assert row["outcome_label"] == "pending"
    assert future_count == 0
    assert tuple(weekend_row) == (0.02, None)


def test_performance_runner_treats_empty_due_set_as_up_to_date(tmp_path):
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
    run_dir.mkdir()
    (run_dir / "run.json").write_text(
        '{"run_id":"run1","started_at":"2026-04-01T09:00:00+09:00"}',
        encoding="utf-8",
    )

    with patch(
        "tradingagents.scheduled.runner.load_price_history_for_recommendations",
        return_value=PriceHistoryLoadResult(provider="yfinance", due_recommendation_ids=()),
    ):
        payload = _run_performance_tracking(
            config=config,
            run_dir=run_dir,
            started_at=datetime(2026, 4, 1, tzinfo=timezone.utc),
        )

    assert payload["status"] == "ok"
    assert payload["outcome_update"]["updated"] is True
    assert payload["outcome_update"]["up_to_date"] is True
    assert "unavailable_reason" not in payload["outcome_update"]


def test_price_history_loader_filters_recommendations_to_run_market(tmp_path, monkeypatch):
    db_path = tmp_path / "perf.sqlite"
    us_run = tmp_path / "us_run"
    kr_run = tmp_path / "kr_run"
    for run_dir, ticker, market in ((us_run, "AAPL", "US"), (kr_run, "000660.KS", "KR")):
        private = run_dir / "portfolio-private"
        private.mkdir(parents=True)
        (run_dir / "run.json").write_text(
            f'{{"run_id":"{run_dir.name}","started_at":"2026-04-01T09:00:00+09:00","settings":{{"market":"{market}"}}}}',
            encoding="utf-8",
        )
        (private / "portfolio_report.json").write_text(
            f"""
            {{
              "actions": [
                {{
                  "canonical_ticker": "{ticker}",
                  "action_now": "WATCH",
                  "action_if_triggered": "STARTER_IF_TRIGGERED",
                  "portfolio_relative_action": "ADD",
                  "delta_krw_now": 0,
                  "confidence": 0.5
                }}
              ]
            }}
            """,
            encoding="utf-8",
        )
        record_run_recommendations(run_dir, db_path, run_market=market)

    downloaded = []
    fake_yfinance = SimpleNamespace(download=lambda ticker, **kwargs: downloaded.append(ticker) or SimpleNamespace(empty=True))
    monkeypatch.setitem(sys.modules, "yfinance", fake_yfinance)

    result = load_price_history_for_recommendations(db_path, provider="yfinance", market="US")

    assert downloaded == ["AAPL"]
    assert "performance_price_history_market_filter:US:skipped=1" in result.warnings


def test_price_history_loader_filters_us_recommendations_out_of_kr_run(tmp_path, monkeypatch):
    db_path = tmp_path / "perf.sqlite"
    us_run = tmp_path / "us_run"
    kr_run = tmp_path / "kr_run"
    for run_dir, ticker, market in ((us_run, "AAPL", "US"), (kr_run, "000660.KS", "KR")):
        private = run_dir / "portfolio-private"
        private.mkdir(parents=True)
        (run_dir / "run.json").write_text(
            f'{{"run_id":"{run_dir.name}","started_at":"2026-04-01T09:00:00+09:00","settings":{{"market":"{market}"}}}}',
            encoding="utf-8",
        )
        (private / "portfolio_report.json").write_text(
            f"""
            {{
              "actions": [
                {{
                  "canonical_ticker": "{ticker}",
                  "action_now": "WATCH",
                  "action_if_triggered": "STARTER_IF_TRIGGERED",
                  "portfolio_relative_action": "ADD",
                  "delta_krw_now": 0,
                  "confidence": 0.5
                }}
              ]
            }}
            """,
            encoding="utf-8",
        )
        record_run_recommendations(run_dir, db_path, run_market=market)

    downloaded = []
    fake_yfinance = SimpleNamespace(download=lambda ticker, **kwargs: downloaded.append(ticker) or SimpleNamespace(empty=True))
    monkeypatch.setitem(sys.modules, "yfinance", fake_yfinance)

    result = load_price_history_for_recommendations(db_path, provider="yfinance", market="KR")

    assert downloaded == ["000660.KS"]
    assert "performance_price_history_market_filter:KR:skipped=1" in result.warnings


def test_prism_skipped_rows_are_recorded_for_current_market_only(tmp_path):
    run_dir = tmp_path / "run"
    prism = run_dir / "external_signals"
    prism.mkdir(parents=True)
    (run_dir / "run.json").write_text(
        '{"run_id":"run1","started_at":"2026-04-01T09:00:00+09:00","settings":{"market":"US"}}',
        encoding="utf-8",
    )
    (prism / "prism_signals.json").write_text(
        """
        {
          "signals": [
            {"canonical_ticker": "000660.KS", "market": "KR", "signal_action": "BUY"},
            {"canonical_ticker": "AAPL", "market": "US", "signal_action": "BUY"}
          ]
        }
        """,
        encoding="utf-8",
    )
    db_path = tmp_path / "perf.sqlite"

    record_run_recommendations(run_dir, db_path, run_market="US")

    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT ticker, market FROM action_recommendations ORDER BY ticker").fetchall()
    assert rows == [("AAPL", "US")]


def test_us_prism_skipped_rows_are_not_recorded_for_kr_run(tmp_path):
    run_dir = tmp_path / "run"
    prism = run_dir / "external_signals"
    prism.mkdir(parents=True)
    (run_dir / "run.json").write_text(
        '{"run_id":"run1","started_at":"2026-04-01T09:00:00+09:00","settings":{"market":"KR"}}',
        encoding="utf-8",
    )
    (prism / "prism_signals.json").write_text(
        """
        {
          "signals": [
            {"canonical_ticker": "AAPL", "market": "US", "signal_action": "BUY"},
            {"canonical_ticker": "000660.KS", "market": "KR", "signal_action": "BUY"}
          ]
        }
        """,
        encoding="utf-8",
    )
    db_path = tmp_path / "perf.sqlite"

    record_run_recommendations(run_dir, db_path, run_market="KR")

    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT ticker, market FROM action_recommendations ORDER BY ticker").fetchall()
    assert rows == [("000660.KS", "KR")]


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
                    {"date": "2026-04-06", "close": 1060000},
                    {"date": "2026-04-07", "close": 1070000},
                    {"date": "2026-04-08", "close": 1080000},
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
        "2026-04-21",
        price_history={
            "005930.KS": [
                {"date": f"2026-04-{day:02d}", "close": 101000 - (day * 1000)}
                for day in range(1, 22)
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
