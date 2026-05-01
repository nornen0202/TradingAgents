import json
import sqlite3
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tradingagents.external.prism_conflicts import enrich_candidates_with_prism, reconcile_prism_with_actions
from tradingagents.external.prism_dashboard import load_dashboard_json_file, parse_dashboard_html
from tradingagents.external.prism_loader import PrismLoaderConfig, load_prism_signals
from tradingagents.external.prism_models import PrismIngestionResult
from tradingagents.external.prism_sqlite import load_prism_sqlite
from tradingagents.performance.action_outcomes import (
    record_run_recommendations,
    summarize_action_performance,
    update_action_outcomes,
)
from tradingagents.performance.journal import generate_closed_trade_review
from tradingagents.performance.price_history import BENCHMARK_KEY, load_price_history_for_recommendations
from tradingagents.portfolio.account_models import (
    AccountConstraints,
    AccountSnapshot,
    InstrumentIdentity,
    PortfolioAction,
    PortfolioCandidate,
    PortfolioRecommendation,
)
from tradingagents.portfolio.reporting import render_portfolio_report_markdown
from tradingagents.scheduled.runner import _augment_run_tickers_with_scanner
from tradingagents.scheduled.site import _render_performance_tracking_section
from tradingagents.scanner.prism_like_scanner import run_prism_like_scanner
from tradingagents.scanner.sector_regime import apply_buy_matrix_overlay, evaluate_buy_matrix


FIXTURES = Path(__file__).parent / "fixtures"


def _identity(ticker="000660.KS", name="SK하이닉스"):
    return InstrumentIdentity(
        broker_symbol=ticker.split(".")[0],
        canonical_ticker=ticker,
        yahoo_symbol=ticker,
        krx_code=ticker.split(".")[0],
        dart_corp_code=None,
        display_name=name,
        exchange="KRX",
        country="KR",
        currency="KRW",
    )


def _candidate(**overrides):
    payload = {
        "snapshot_id": "snap",
        "instrument": _identity(overrides.pop("ticker", "000660.KS"), overrides.pop("name", "SK하이닉스")),
        "is_held": False,
        "market_value_krw": 0,
        "quantity": 0,
        "available_qty": 0,
        "sector": "Semiconductors",
        "structured_decision": None,
        "data_coverage": {"company_news_count": 3, "disclosures_count": 1, "social_source": "dedicated", "macro_items_count": 1},
        "quality_flags": tuple(),
        "vendor_health": {"vendor_calls": {}, "fallback_count": 0},
        "suggested_action_now": "STARTER_NOW",
        "suggested_action_if_triggered": "NONE",
        "trigger_conditions": ("close above trigger",),
        "confidence": 0.60,
        "stance": "BULLISH",
        "entry_action": "STARTER",
        "setup_quality": "DEVELOPING",
        "rationale": "test",
        "risk_action": "NONE",
    }
    payload.update(overrides)
    return PortfolioCandidate(**payload)


def test_prism_dashboard_json_parses_partial_fields():
    result = load_dashboard_json_file(FIXTURES / "prism" / "dashboard_data_minimal.json", market="KR")

    assert result.ok is True
    assert len(result.signals) == 1
    assert result.signals[0].canonical_ticker == "000660.KS"
    assert result.signals[0].signal_action.value == "BUY"
    assert result.raw_payload_hash


def test_prism_invalid_json_returns_warning(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{bad json", encoding="utf-8")

    result = load_dashboard_json_file(path)

    assert result.ok is False
    assert result.warnings


def test_prism_dashboard_html_parses_embedded_payload_when_enabled():
    html_text = (FIXTURES / "prism" / "dashboard_page_embedded.html").read_text(encoding="utf-8")

    result = parse_dashboard_html(html_text, source="https://example.test", market="KR")

    assert result.ok is True
    assert result.signals[0].canonical_ticker == "000660.KS"
    assert result.signals[0].signal_action.value == "BUY"
    assert result.performance_summary
    assert "dashboard_html_scraping_opt_in" in result.warnings


def test_prism_loader_only_uses_html_scraping_when_explicitly_enabled():
    html_text = (FIXTURES / "prism" / "dashboard_page_embedded.html").read_text(encoding="utf-8")
    html_result = parse_dashboard_html(html_text, source="https://example.test", market="KR")

    with (
        patch(
            "tradingagents.external.prism_loader.fetch_dashboard_json_url",
            return_value=PrismIngestionResult(enabled=True, ok=False, warnings=["json_unavailable"]),
        ),
        patch("tradingagents.external.prism_loader.fetch_dashboard_html_url", return_value=html_result) as html_fetch,
    ):
        result = load_prism_signals(
            PrismLoaderConfig(
                enabled=True,
                use_live_http=True,
                use_html_scraping=False,
                dashboard_base_url="https://example.test",
            )
        )

    assert result.ok is False
    html_fetch.assert_not_called()

    with (
        patch(
            "tradingagents.external.prism_loader.fetch_dashboard_json_url",
            return_value=PrismIngestionResult(enabled=True, ok=False, warnings=["json_unavailable"]),
        ),
        patch("tradingagents.external.prism_loader.fetch_dashboard_html_url", return_value=html_result) as html_fetch,
    ):
        result = load_prism_signals(
            PrismLoaderConfig(
                enabled=True,
                use_live_http=True,
                use_html_scraping=True,
                dashboard_base_url="https://example.test",
            )
        )

    assert result.ok is True
    assert result.signals
    html_fetch.assert_called_once()


def test_prism_sqlite_parser_tolerates_missing_tables(tmp_path):
    db_path = tmp_path / "prism.sqlite"
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE stock_holdings (ticker TEXT, name TEXT, action TEXT, confidence REAL)")
        conn.execute("INSERT INTO stock_holdings VALUES ('005930', '삼성전자', 'HOLD', 0.55)")
        conn.commit()

    result = load_prism_sqlite(db_path, market="KR")

    assert result.ok is True
    assert result.signals[0].canonical_ticker == "005930.KS"
    assert any("sqlite_table_missing" in warning for warning in result.warnings)


def test_prism_loader_does_not_call_live_http_by_default():
    with patch("tradingagents.external.prism_dashboard.requests.get") as get:
        result = load_prism_signals(PrismLoaderConfig(enabled=True))

    assert result.ok is True
    assert result.signals == []
    get.assert_not_called()


def test_prism_buy_ta_reduce_blocks_buy_and_requires_review():
    ingestion = load_dashboard_json_file(FIXTURES / "prism" / "external_signals_conflict.json", market="KR")
    candidate = _candidate(
        is_held=True,
        suggested_action_now="HOLD",
        suggested_action_if_triggered="STOP_LOSS_IF_TRIGGERED",
        risk_action="STOP_LOSS",
    )

    enriched = enrich_candidates_with_prism([candidate], ingestion, confidence_cap=0.25)[0]

    assert enriched.prism_agreement == "conflict_prism_buy_ta_reduce"
    assert enriched.review_required is True
    assert enriched.suggested_action_now != "ADD_NOW"


def test_prism_buy_ta_add_boosts_within_cap():
    ingestion = load_dashboard_json_file(FIXTURES / "prism" / "dashboard_data_minimal.json", market="KR")
    enriched = enrich_candidates_with_prism([_candidate()], ingestion, confidence_cap=0.25)[0]

    assert enriched.prism_agreement == "confirmed_buy"
    assert 0 < enriched.external_signal_score_delta <= 0.25
    assert enriched.confidence <= 0.85


def test_prism_sell_ta_add_is_review_conflict():
    ingestion = load_dashboard_json_file(FIXTURES / "prism" / "external_signals_conflict.json", market="KR")
    candidate = _candidate(ticker="005930.KS", name="삼성전자")

    enriched = enrich_candidates_with_prism([candidate], ingestion, confidence_cap=0.25)[0]

    assert enriched.prism_agreement == "conflict_prism_sell_ta_buy"
    assert enriched.review_required is True
    assert enriched.suggested_action_now == "WATCH"


def test_scanner_filters_low_liquidity_and_overheated_movers():
    result = run_prism_like_scanner(ohlcv_path=FIXTURES / "scanner" / "kr_ohlcv_snapshot.json", market="KR")

    tickers = [candidate.ticker for candidate in result.candidates]
    assert "000660.KS" in tickers
    assert "123456.KS" not in tickers
    assert "999999.KS" not in tickers
    assert result.candidates[0].trigger_type in {"VOLUME_SURGE", "NEAR_52W_HIGH", "SECTOR_LEADER", "CLOSING_STRENGTH"}


def test_scanner_prism_failures_fall_back_to_base_universe(tmp_path):
    config = SimpleNamespace(
        scanner=SimpleNamespace(
            enabled=True,
            market="KR",
            local_ohlcv_path=None,
            max_candidates=10,
            max_new_tickers_per_run=5,
            include_prism_candidates=True,
            min_traded_value_krw=10_000_000_000,
            min_market_cap_krw=500_000_000_000,
            max_daily_change_pct=20.0,
            min_volume_ratio_to_market_avg=0.2,
            exclude_halted_or_low_liquidity=True,
        ),
        external_data=SimpleNamespace(
            prism=SimpleNamespace(
                enabled=True,
                use_for_candidate_generation=True,
            )
        ),
    )

    with (
        patch("tradingagents.scheduled.runner.load_prism_signals", side_effect=RuntimeError("prism down")),
        patch("tradingagents.scheduled.runner.run_prism_like_scanner", side_effect=RuntimeError("scanner down")),
    ):
        tickers, status = _augment_run_tickers_with_scanner(
            config=config,
            base_tickers=["000660.KS"],
            run_dir=tmp_path,
            run_id="run1",
            asof="2026-04-30T09:00:00+09:00",
        )

    assert tickers == ["000660.KS"]
    assert status is not None
    assert any("scanner_prism_ingestion_failed" in warning for warning in status["warnings"])
    assert any("scanner_failed" in warning for warning in status["warnings"])


def test_buy_matrix_blocks_low_risk_reward_candidate():
    candidate = _candidate(
        structured_decision={"buy_matrix": {"risk_reward_ratio": 0.8, "profitability_gate": True}},
        suggested_action_now="STARTER_NOW",
    )

    matrix = evaluate_buy_matrix(candidate, market_regime="sideways")
    blocked = apply_buy_matrix_overlay([candidate], market_regime="sideways")[0]

    assert matrix.passed is False
    assert "risk_reward_floor" in matrix.fail_reasons
    assert blocked.suggested_action_now == "WATCH"


def test_buy_matrix_can_upgrade_strong_wait_to_conditional_pilot():
    candidate = _candidate(
        suggested_action_now="WATCH",
        suggested_action_if_triggered="WATCH_TRIGGER",
        entry_action="WAIT",
        structured_decision={
            "buy_matrix": {
                "risk_reward_ratio": 1.9,
                "profitability_gate": True,
                "balance_sheet_gate": True,
                "growth_gate": True,
                "business_clarity_gate": True,
                "sector_leadership_score": 0.9,
            }
        },
        data_health={"relative_volume_ok": True, "session_vwap_ok": True, "execution_timing_state": "PILOT_READY"},
    )

    upgraded = apply_buy_matrix_overlay([candidate], market_regime="moderate_bull")[0]

    assert upgraded.buy_matrix["passed"] is True
    assert upgraded.suggested_action_if_triggered == "STARTER_IF_TRIGGERED"


def test_action_tracker_records_and_updates_fixture_outcomes(tmp_path):
    run_dir = tmp_path / "run"
    private = run_dir / "portfolio-private"
    private.mkdir(parents=True)
    (run_dir / "run.json").write_text(
        json.dumps({"run_id": "run1", "started_at": "2026-04-01T09:00:00+09:00"}, ensure_ascii=False),
        encoding="utf-8",
    )
    (private / "portfolio_report.json").write_text(
        json.dumps(
            {
                "actions": [
                    {
                        "canonical_ticker": "000660.KS",
                        "action_now": "STARTER_NOW",
                        "action_if_triggered": "NONE",
                        "delta_krw_now": 100000,
                        "confidence": 0.7,
                        "risk_action": "NONE",
                        "data_health": {"last_price": 100, "prism_agreement": "confirmed_buy"},
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    db_path = tmp_path / "perf.sqlite"

    record_run_recommendations(run_dir, db_path)
    update_action_outcomes(
        db_path,
        "2026-04-30",
        horizons=(1, 3, 5, 20, 60),
        price_history={
            "000660.KS": [
                {"date": "2026-04-01", "close": 100},
                {"date": "2026-04-02", "close": 101},
                {"date": "2026-04-03", "close": 102},
                {"date": "2026-04-06", "close": 104},
                {"date": "2026-04-07", "close": 105},
                {"date": "2026-04-08", "close": 106}
            ]
        },
    )
    summary = summarize_action_performance(db_path)

    assert summary.recommendations == 1
    assert summary.outcomes == 1
    assert summary.by_action["STARTER_NOW"]["count"] == 1


def test_price_history_loader_adds_benchmark_and_updates_outcomes(tmp_path):
    run_dir = tmp_path / "run"
    private = run_dir / "portfolio-private"
    private.mkdir(parents=True)
    (run_dir / "run.json").write_text(
        json.dumps({"run_id": "run1", "started_at": "2026-04-01T09:00:00+09:00"}, ensure_ascii=False),
        encoding="utf-8",
    )
    (private / "portfolio_report.json").write_text(
        json.dumps(
            {
                "actions": [
                    {
                        "canonical_ticker": "000660.KS",
                        "action_now": "STARTER_NOW",
                        "action_if_triggered": "NONE",
                        "delta_krw_now": 100000,
                        "confidence": 0.7,
                        "risk_action": "NONE",
                        "data_health": {"last_price": 100, "prism_agreement": "confirmed_buy"},
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    db_path = tmp_path / "perf.sqlite"

    record_run_recommendations(run_dir, db_path)
    price_result = load_price_history_for_recommendations(
        db_path,
        provider="local_json",
        price_history_path=FIXTURES / "performance" / "price_history_with_benchmark.json",
        benchmark_ticker="SPY",
    )
    update_action_outcomes(db_path, "2026-04-30", price_history=price_result.price_history)

    assert price_result.has_prices is True
    assert BENCHMARK_KEY in price_result.price_history
    with sqlite3.connect(db_path) as conn:
        benchmark_return = conn.execute("SELECT benchmark_return_5d FROM action_outcomes").fetchone()[0]
    assert benchmark_return is not None


def test_trading_journal_generates_rule_based_review(tmp_path):
    path = tmp_path / "closed_trade_review.json"
    review = generate_closed_trade_review(
        entry_context={"ticker": "278470.KS", "run_id": "entry", "action": "ADD_NOW"},
        exit_context={"ticker": "278470.KS", "run_id": "exit", "action": "TAKE_PROFIT"},
        realized_return_pct=0.034,
        holding_days=8,
        output_path=path,
    )

    assert review["judgment_evaluation"] == "principle_followed"
    assert review["lessons"]
    assert path.exists()


def test_investor_report_separates_actions_and_prism_sections():
    snapshot = AccountSnapshot(
        snapshot_id="snap",
        as_of="2026-04-29T15:00:00+09:00",
        broker="manual",
        account_id="test",
        currency="KRW",
        settled_cash_krw=1000000,
        available_cash_krw=1000000,
        buying_power_krw=1000000,
        total_equity_krw=1000000,
        constraints=AccountConstraints(min_cash_buffer_krw=100000),
    )
    action = PortfolioAction(
        canonical_ticker="000660.KS",
        display_name="SK하이닉스",
        priority=1,
        confidence=0.7,
        action_now="STARTER_NOW",
        delta_krw_now=100000,
        target_weight_now=0.1,
        action_if_triggered="NONE",
        delta_krw_if_triggered=0,
        target_weight_if_triggered=0.1,
        trigger_conditions=tuple(),
        rationale="test",
        data_health={"prism_agreement": "confirmed_buy"},
        prism_agreement="confirmed_buy",
    )
    recommendation = PortfolioRecommendation(
        snapshot_id="snap",
        report_date="2026-04-29",
        account_value_krw=1000000,
        recommended_cash_after_now_krw=900000,
        recommended_cash_after_triggered_krw=900000,
        market_regime="mixed",
        actions=(action,),
        portfolio_risks=tuple(),
        data_health_summary={},
    )
    reconciliation = reconcile_prism_with_actions(
        tradingagents_actions=recommendation.actions,
        ingestion=PrismIngestionResult(enabled=True, ok=True, signals=load_dashboard_json_file(FIXTURES / "prism" / "dashboard_data_minimal.json").signals),
    )

    markdown = render_portfolio_report_markdown(
        snapshot=snapshot,
        recommendation=recommendation,
        candidates=[],
        external_reconciliation=reconciliation,
    )

    assert "오늘 바로 매수 후보" in markdown
    assert "오늘 바로 매도/축소 후보" in markdown
    assert "외부 PRISM 신호 요약" in markdown
    assert "PRISM 일치" in markdown
    assert "전략상 우선순위" not in markdown


def test_site_renders_performance_tracking_section():
    html = _render_performance_tracking_section(
        {
            "run_id": "run1",
            "performance": {
                "enabled": True,
                "status": "ok",
                "outcome_update": {"enabled": True, "updated": True, "provider": "local_json", "warnings": []},
                "summary": {
                    "recommendations": 3,
                    "outcomes": 2,
                    "by_action": {"STARTER_NOW": {"count": 1, "avg_return_5d": 0.04, "avg_return_20d": 0.08}},
                    "prism_agreement": {"confirmed_buy": {"count": 1, "avg_return_5d": 0.03, "avg_return_20d": 0.07}},
                },
                "artifacts": {"performance_summary_json": "performance/performance_summary.json"},
            },
        }
    )

    assert "추천 성과 추적" in html
    assert "STARTER_NOW" in html
    assert "confirmed_buy" in html
