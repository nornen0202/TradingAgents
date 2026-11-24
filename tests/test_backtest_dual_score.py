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
    assert data["records"][0]["new_exposure"] == initial["records"][0]["new_exposure"]
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
