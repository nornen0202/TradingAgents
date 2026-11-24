# Decision backtest

Run a private grid from the installed CLI.

    tradingagents backtest AAPL,MSFT --start 2025-01-02 --end 2025-02-28 --every 7
    tradingagents backtest AAPL,MSFT --start 2025-01-02 --end 2025-02-28 --every 7 --run-id RUN

The output directory contains evaluation.json, evaluation.ko.md and evaluation.ko.html. The Korean report shows the numerator, scored denominator, target count, exclusions and trade clocks. The JSON preserves the historic active new-exposure hit_rate key.

Directional accuracy follows the upstream close-to-close measure between the first eligible session and the close N exchange sessions later. The market-relative return is serialized to one decimal percentage point before determining directional hits. The cash-exposure measure uses the next regular session's open, the Nth session's close and a two-sided cost proportional to the new exposure. The two measures have independent required inputs and denominators.

Fetches require exact exchange dates. Missing prices and benchmarks are not substituted. The currently retrieved adjusted series can contain later vendor revisions. Use a reviewed price provider for an analysis that requires original historical vintages. The scorecards represent independent decisions and cash exposures, without a portfolio allocation, simulated fills, or actual tax.

Each run stores its private parameters, original judgments, reports and settlement attempts. A completed decision is kept when settlement fails. An identical run ID resumes incomplete work. A parameter change, simultaneous writer, and backward settlement cutoff fail explicitly. Existing research archive readers continue using their current files.

The Python API supports the upstream stock example.

    from tradingagents.backtest import iter_grid, run_backtest, summarize
    from tradingagents.default_config import DEFAULT_CONFIG

    dates = iter_grid("2026-06-01", "2026-08-01", every_n_days=7)
    result = run_backtest(["NVDA", "AAPL"], dates, DEFAULT_CONFIG,
                          selected_analysts=["market", "news"], asset_type="stock")
    print(summarize(result).render())

The graph accepts both `propagate(ticker, trade_date, "stock", portfolio=book)` and `propagate(ticker, trade_date, asset_type="stock", portfolio=book)`. The existing positional and keyword `analysis_date` calls and `save_reports(state, ticker)` remain available. The portfolio JSON can include positions, cash and currency. The CLI and Python accept stock assets. Crypto requests fail explicitly before calling a model or provider.

The compatibility fields `resolved`, `pending`, `unscored`, `by_rating` and `holding` describe the stored judgments. A settled Hold contributes a count and mean alpha with no directional hit rate. Review is unscored. Other stored judgments with missing alpha stay pending. Failed cells without a judgment stay visible in the scorecard target and failure counts. `summarize(path)` also reads preserved upstream Markdown memory logs and uses their recorded alpha and windows without fetching prices. Other prior formats are left unverified.

Backtest exports distinguish newly analyzed and resumed cells and preserve the original judgment clock. Scheduled run and ticker pages show fresh full research, copied full research or an execution overlay. The recommendation ledger captures independently generated judgments and leaves reused decisions with their original run.
