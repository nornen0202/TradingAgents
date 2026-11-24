from datetime import datetime, timezone
import pandas as pd
import pytest
from typer.testing import CliRunner

from cli.main import app
from tradingagents import backtest as bt
from tradingagents.atomic_io import interprocess_file_lock
from tradingagents.eval.decision_scores import score_decision
from tradingagents.graph.trading_graph import TradingAgentsGraph

CUTOFF = datetime(2026, 3, 10, 22, tzinfo=timezone.utc)
DATES = ["2026-03-02"]
BAR_DATES = pd.to_datetime(["2026-03-03", "2026-03-04", "2026-03-05", "2026-03-06"])


def prices(symbol, first, last):
    base = [100, 101, 101, 999] if symbol == "AAPL" else [100, 102, 102, 999]
    if symbol == "MSFT":
        base = [100, 90, 90, 999]
    if symbol == "QQQ":
        base = [100, 100, 100, 999]
    return pd.DataFrame({"Open": [100] * 4, "Close": base}, index=BAR_DATES)


def graph_with(monkeypatch, fails=()):
    class Graph:
        calls = []
        closed = False

        def __init__(self, config, **_):
            assert config["memory_dir"] is None and config["point_in_time_strict"]

        def propagate(self, ticker, day, **settings):
            self.calls.append((ticker, day, settings))
            if self.calls.count(self.calls[-1]) == 1 and ticker in fails:
                raise OSError("fixture")
            return {"company_of_interest": ticker, "trade_date": day}, "매수" if ticker == "AAPL" else "매도"

        def close(self):
            self.__class__.closed = True

    monkeypatch.setattr(bt, "TradingAgentsGraph", Graph)
    return Graph


def test_two_scorecards_follow_the_upstream_rounding_and_fork_cost():
    buy = score_decision(ticker="AAPL", market="US", decision_date=DATES[0], rating="BUY",
                         benchmark="SPY", holding=2, fee_bps=10, as_of=CUTOFF, provider=prices)
    sell = score_decision(ticker="MSFT", market="US", decision_date=DATES[0], rating="SELL",
                          benchmark="QQQ", holding=2, fee_bps=10, as_of=CUTOFF, provider=prices)
    assert buy["direction"]["alpha_logged"] == "-1.0%"
    assert buy["direction"]["hit"] is False and sell["direction"]["hit"] is True
    assert sell["direction"]["alpha_logged"] == "-10.0%"
    assert sell["new_exposure"]["status"] == "NO_NEW_EXPOSURE"
    assert buy["new_exposure"]["strategy_return"] == pytest.approx(.008)
    assert buy["new_exposure"]["exit_session"] == "2026-03-04"
    assert buy["direction"]["exit_session"] == "2026-03-05"
    hold = score_decision(ticker="AAPL", market="US", decision_date=DATES[0], rating="HOLD",
                          benchmark="SPY", holding=2, fee_bps=10, as_of=CUTOFF, provider=prices)
    assert hold["direction"]["alpha_logged"] == "-1.0%"
    assert hold["direction"]["status"] == "NO_DIRECTION" and hold["direction"]["hit"] is None


def test_missing_first_bars_do_not_shift_and_maturity_is_local():
    def missing_first(symbol, first, last):
        return prices(symbol, first, last).iloc[1:]
    args = dict(ticker="AAPL", market="US", decision_date=DATES[0], rating="BUY",
                benchmark="SPY", holding=2, fee_bps=10, provider=missing_first)
    failed = score_decision(as_of=CUTOFF, **args)
    assert {row["status"] for row in failed.values()} == {"ASSET_PRICE_MISSING"}
    early = score_decision(as_of=datetime(2026, 3, 4, 20, 59, tzinfo=timezone.utc), **args)
    assert {row["status"] for row in early.values()} == {"PENDING"}
    with pytest.raises(ValueError):
        score_decision(as_of=datetime(2026, 3, 4), **args)


def test_backtest_resumes_decisions_and_score_failures_once_and_exports(tmp_path, monkeypatch):
    graph = graph_with(monkeypatch, fails=("MSFT",))
    def flaky(ticker, first, last):
        if ticker == "SPY":
            raise OSError("fixture")
        return prices(ticker, first, last)
    opts = dict(config={"results_dir": str(tmp_path)}, run_id="same", as_of=CUTOFF,
                holding_period=2, portfolio={"cash": 100, "currency": "USD"})
    first = bt.run_backtest(["AAPL", "MSFT"], DATES, provider=flaky, **opts)
    assert first.cells_run == 1 and len(first.failures) == 1 and first.settlement_failures
    initial = bt.summarize(first).data
    assert initial["direction"]["statuses"]["BENCHMARK_PROVIDER_FAILURE"] == 1
    assert initial["new_exposure"]["hits"] == 1 and initial["new_exposure"]["scored"] == 1
    assert initial["metrics"]["hit_rate"] == 1
    second = bt.run_backtest(["AAPL", "MSFT"], DATES, provider=prices, **opts)
    data = bt.summarize(second).data
    assert second.cells_run == second.skipped == 1 and not second.failures
    assert [ticker for ticker, _, _ in graph.calls] == ["AAPL", "MSFT", "MSFT"]
    assert graph.calls[0][-1]["portfolio"]["cash"] == 100
    assert data["records"][0]["executed_at"] == initial["records"][0]["executed_at"]
    assert data["records"][0]["new_exposure"]["strategy_return"] == initial["records"][0]["new_exposure"]["strategy_return"]
    assert data["records"][0]["new_exposure"]["benchmark_status"] == "AVAILABLE"
    assert data["direction"]["scored"] == 2 and data["direction"]["hits"] == 1
    root = first.log_path.parent
    assert len(list(root.rglob("settlement.json"))) == 3
    text = (root / "evaluation.ko.md").read_text(encoding="utf-8")
    assert "1/2 (50.0%)" in text and "1/1 (100.0%)" in text
    assert "<table" in (root / "evaluation.ko.html").read_text(encoding="utf-8")
    with pytest.raises(ValueError, match="Parameters differ"):
        bt.run_backtest(["AAPL", "MSFT"], DATES, provider=prices, transaction_cost_bps=11, **opts)
    with interprocess_file_lock(root / "run.lock", timeout=0):
        with pytest.raises(TimeoutError):
            bt.run_backtest(["AAPL", "MSFT"], DATES, provider=prices, **opts)


def test_cli_and_programmatic_asset_type_and_date_dispatch(tmp_path, monkeypatch):
    graph_with(monkeypatch)
    def fast(tickers, dates, config, **kwargs):
        return run(tickers, dates, config, provider=prices, as_of=CUTOFF, **kwargs)
    run = bt.run_backtest
    monkeypatch.setattr(bt, "run_backtest", fast)
    flags = ["backtest", "AAPL", "--start", DATES[0], "--end", DATES[0], "--holding-period", "2",
             "--output-dir", str(tmp_path), "--run-id", "cli-fixture"]
    result = CliRunner().invoke(app, flags)
    assert result.exit_code == 0, result.output
    retry = CliRunner().invoke(app, flags)
    assert "재사용 1" in retry.output
    wrong = CliRunner().invoke(app, flags + ["--asset-type", "crypto"])
    assert wrong.exit_code == 2 and "stock graph" in wrong.output
    graph = TradingAgentsGraph.__new__(TradingAgentsGraph)
    graph.config = {}
    graph._propagate = lambda *a, **kwargs: kwargs
    assert graph.propagate("AAPL", DATES[0], "stock")["analysis_date"] is None
    assert graph.propagate("AAPL", DATES[0], "2026-03-03")["analysis_date"] == "2026-03-03"
    assert graph.propagate("AAPL", DATES[0], "stock", portfolio={"cash": 200})["portfolio"]["cash"] == 200
    with pytest.raises(ValueError):
        graph.propagate("AAPL", DATES[0], "stock", asset_type="crypto")


def test_legacy_metrics_are_preserved_without_reclassification(tmp_path):
    path = tmp_path / "legacy.json"
    path.write_text('{"metrics":{"hit_rate":0.8}}', encoding="utf-8")
    report = bt.summarize(path)
    assert report.data["metrics"]["hit_rate"] == .8
    assert not report.by_rating and "원자료" in report.render()


def test_close_bars_require_next_market_day_and_exact_benchmark():
    args = dict(ticker="AAPL", market="US", decision_date=DATES[0], rating="BUY",
                benchmark="SPY", holding=2, fee_bps=10)
    pending = score_decision(as_of=datetime(2026, 3, 5, 1, tzinfo=timezone.utc), provider=prices, **args)
    assert pending["new_exposure"]["status"] == "PENDING"
    assert pending["new_exposure"]["exit_close_at"] == "2026-03-04T21:00:00+00:00"
    assert pending["new_exposure"]["matures_at"] == "2026-03-05T00:00:00-05:00"

    def missing(symbol, first, last):
        return prices(symbol, first, last).iloc[1:] if symbol == "SPY" else prices(symbol, first, last)

    mature = score_decision(as_of=CUTOFF, provider=missing, **args)
    assert mature["direction"]["status"] == "BENCHMARK_PRICE_MISSING"
    assert mature["new_exposure"]["benchmark_status"] == "BENCHMARK_PRICE_MISSING"
    assert mature["new_exposure"]["hit"] is True


def test_cli_report_reader_path_keeps_two_distinct_saves(tmp_path):
    from cli.main import save_report_to_disk

    state = {"company_of_interest": "AAPL", "analysis_date": DATES[0], "trade_date": DATES[0]}
    first = save_report_to_disk({**state, "market_report": "first decision evidence"}, "AAPL", tmp_path)
    saved = save_report_to_disk({**state, "market_report": "second decision evidence"}, "AAPL", tmp_path)
    assert saved == first == tmp_path / "complete_report.md"
    assert "second decision evidence" in saved.read_text(encoding="utf-8")
    archived = list((tmp_path / "runs").glob("*/complete_report.md"))
    assert len(archived) == 2
    assert sum("first decision evidence" in path.read_text(encoding="utf-8") for path in archived) == 1


def test_qualified_kr_benchmark_and_holdings_use_same_market_identity(tmp_path, monkeypatch):
    from tradingagents.portfolio.context import render_portfolio, normalize_portfolio

    graph_with(monkeypatch)
    queried = []
    def price(symbol, first, last):
        queried.append(symbol)
        return prices(symbol, first, last)
    result = bt.run_backtest(["005930"], DATES, {"results_dir": str(tmp_path)}, benchmark_symbol="069500",
                             holding_period=2, as_of=CUTOFF, provider=price)
    assert "069500.KS" in queried and "069500" not in queried
    book = normalize_portfolio({"positions": [{"ticker": "005930", "quantity": 10}]})
    rendered = render_portfolio({"company_of_interest": "005930.KS", "standing_portfolio": book})
    assert "005930.KS: 10 units" in rendered and "No position" not in rendered
    assert bt.summarize(result).data["records"][0]["benchmark"] == "069500.KS"


def test_calendar_range_accepts_actual_long_horizon_and_historical_dates():
    from tradingagents.eval.decision_scores import evaluation_sessions

    future = evaluation_sessions("US", "2026-11-24", 101)
    assert len(future) == 101 and future[0][0] == "2026-11-25"
    assert evaluation_sessions("US", "2001-01-02", 2)[0][0] == "2001-01-03"


def test_retry_fetches_only_the_unavailable_benchmark_after_both_outcomes_settled():
    def only_close_benchmark(symbol, first, last):
        if symbol == "SPY" and last == "2026-03-04":
            raise OSError("isolated exception")
        return prices(symbol, first, last)
    opts = dict(ticker="AAPL", market="US", decision_date=DATES[0], rating="BUY",
                benchmark="SPY", holding=2, fee_bps=10, as_of=CUTOFF)
    before = score_decision(provider=only_close_benchmark, **opts)
    assert before["direction"]["status"] == before["new_exposure"]["status"] == "SCORED"
    queried = []
    def changed(symbol, first, last):
        queried.append(symbol)
        return prices(symbol, first, last)
    after = score_decision(provider=changed, previous=before, **opts)
    assert queried == ["SPY"] and after["direction"] == before["direction"]
    assert after["new_exposure"]["strategy_return"] == before["new_exposure"]["strategy_return"]
    assert after["new_exposure"]["benchmark_status"] == "AVAILABLE"

def test_summary_compatibility_counts_settled_hold_without_a_direction(tmp_path, monkeypatch):
    graph = graph_with(monkeypatch)
    original = graph.propagate

    def propagate(self, ticker, day, **kwargs):
        state, rating = original(self, ticker, day, **kwargs)
        return state, {"AAPL": "보유", "MSFT": "매도", "AMD": "검토", "NVDA": "매수"}.get(ticker, rating)

    def missing_asset(ticker, first, last):
        return prices(ticker, first, last).iloc[:0] if ticker == "NVDA" else prices(ticker, first, last)

    monkeypatch.setattr(graph, "propagate", propagate)
    result = bt.run_backtest(["AAPL", "MSFT", "AMD", "NVDA"], DATES, {"results_dir": str(tmp_path)},
                             "stock", holding_period=2, as_of=CUTOFF, provider=missing_asset)
    report = bt.summarize(result)
    assert (report.resolved, report.pending, report.unscored) == (2, 1, 1)
    assert report.holding == "2 trading days"
    assert report.by_rating["Hold"] == bt.RatingScore(1, None, -.01)
    assert report.by_rating["Sell"] == bt.RatingScore(1, 1., -.12)
    assert "Review" not in report.by_rating and "Buy" not in report.by_rating
    assert report.data["direction"]["scored"] == 1
    assert report.data["new_exposure"]["scored"] == 0
    assert report.data["metrics"]["hit_rate"] is None
    assert "2 / 1 / 1" in report.render()
    assert bt.summarize(result.log_path) == report


def test_upstream_log_path_reads_recorded_outcomes_and_preserves_source_bytes(tmp_path):
    path = tmp_path / "trading_memory.md"
    tags = [
        "2026-03-02 | AAPL | Hold | +1.0% | -1.0% | 2d | resolved:2026-03-05",
        "2026-03-02 | MSFT | Sell | -10.0% | -12.0% | 2d | resolved:2026-03-05",
        "2026-03-02 | AMD | Review | pending",
        "2026-03-02 | NVDA | Buy | pending",
        "2026-03-02 | AMZN | Buy | +0.0% | n/a | 2d",
        "2026-03-02 | META | Buy | +1.0% | +0.0% | 5d",
        "2026-03-02 | GOOG | Overweight | +3.0% | +1.0% | 2d",
        "2026-03-02 | QQQ | Underweight | -1.0% | -0.0% | 2d",
    ]
    source = "".join(f"[{tag}]\r\n\r\nDECISION:\r\nFixture\r\n\r\n<!-- ENTRY_END -->\r\n\r\n"
                     for tag in tags).encode()
    path.write_bytes(source)
    report = bt.summarize(path)
    assert (report.resolved, report.pending, report.unscored) == (5, 2, 1)
    assert report.holding == "2 trading days, 5 trading days"
    assert report.by_rating == {
        "Hold": bt.RatingScore(1, None, -.01),
        "Sell": bt.RatingScore(1, 1., -.12),
        "Buy": bt.RatingScore(1, 0., 0.),
        "Overweight": bt.RatingScore(1, 1., .01),
        "Underweight": bt.RatingScore(1, 0., 0.),
    }
    assert path.read_bytes() == source
    assert "Hold" in report.render() and "new_exposure" not in report.data

    path.write_text("[2026-03-02 | AAPL | Buy | +3.0% | +2.0% | 2d]\nUnverified report", encoding="utf-8")
    assert bt.summarize(path).data.get("schema") == "legacy/unverified"


def test_run_reuses_full_decision_with_separate_visible_provenance(tmp_path, monkeypatch):
    graph = graph_with(monkeypatch)
    args = (["AAPL"], DATES, {"results_dir": str(tmp_path)})
    opts = dict(run_id="resume-provenance", holding_period=2, as_of=CUTOFF, provider=prices)
    first = bt.run_backtest(*args, asset_type="stock", **opts)
    first_report = bt.summarize(first)
    assert "FULL · 신규 분석" in first_report.render()
    second = bt.run_backtest(*args, "stock", **opts)
    second_report = bt.summarize(second)
    assert len(graph.calls) == second.skipped == second_report.resolved == 1
    assert second.cells_run == 0
    assert "FULL · 기존 판단 재사용" in second_report.render()
    assert "기존 판단 재사용" in (second.log_path.parent / "evaluation.ko.html").read_text(encoding="utf-8")
    assert second_report.data["records"][0]["executed_at"] == first_report.data["records"][0]["executed_at"]


def test_public_api_reports_unsupported_asset_and_date(tmp_path):
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        bt.iter_grid("2026-3-02", DATES[0])
    assert bt.iter_grid("2026-03-02", "2026-03-05", every_n_days=3) == ["2026-03-02", "2026-03-05"]
    book = {"cash": 100, "currency": "USD"}
    with pytest.raises(ValueError, match="stock graph"):
        bt.run_backtest(["BTC-USD"], DATES, {"results_dir": str(tmp_path)}, "crypto", book)
    graph = TradingAgentsGraph.__new__(TradingAgentsGraph)
    graph.config = {}
    graph._propagate = lambda *a, **kwargs: kwargs
    assert graph.propagate("AAPL", DATES[0], portfolio=book, asset_type="stock")["portfolio"] == book
    with pytest.raises(ValueError, match="stock graph"):
        graph.propagate("BTC-USD", DATES[0], asset_type="crypto")
