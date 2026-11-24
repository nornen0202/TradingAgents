# Decision backtest

Run a private grid from the installed CLI.

    tradingagents backtest AAPL,MSFT --start 2025-01-02 --end 2025-02-28 --every 7
    tradingagents backtest AAPL,MSFT --start 2025-01-02 --end 2025-02-28 --every 7 --run-id RUN

The output directory contains evaluation.json, evaluation.ko.md and evaluation.ko.html. The Korean report shows the numerator, scored denominator, target count, exclusions and trade clocks. The JSON preserves the historic active new-exposure hit_rate key.

Directional accuracy follows the upstream close-to-close measure between the first eligible session and the close N exchange sessions later. The market-relative return is serialized to one decimal percentage point before determining directional hits. The cash-exposure measure uses the next regular session's open, the Nth session's close and a two-sided cost proportional to the new exposure. The two measures have independent required inputs and denominators.

Fetches require exact exchange dates. Missing prices and benchmarks are not substituted. The currently retrieved adjusted series can contain later vendor revisions. Use a reviewed price provider for an analysis that requires original historical vintages. The scorecards represent independent decisions and cash exposures, without a portfolio allocation, simulated fills, or actual tax.

Each run stores its private parameters, original judgments, reports and settlement attempts. A completed decision is kept when settlement fails. An identical run ID resumes incomplete work. A parameter change, simultaneous writer, and backward settlement cutoff fail explicitly. Existing research archive readers continue using their current files.

The Python entry points are tradingagents.backtest.run_backtest and tradingagents.backtest.summarize. The stock graph accepts propagate(ticker, trade_date, "stock", portfolio=book) and the existing analysis_date form. The portfolio is a JSON file with positions and optional cash/currency. The fork presently supports its stock graph. An explicit unsupported asset type raises a diagnostic.
