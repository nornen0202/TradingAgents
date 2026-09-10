"""Run one explicitly dated investment analysis using the configured Codex roles."""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import date
from dotenv import load_dotenv


def main():
    load_dotenv()
    from tradingagents.default_config import DEFAULT_CONFIG
    from tradingagents.graph.trading_graph import TradingAgentsGraph
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticker", required=True)
    parser.add_argument("--date", required=True, help="Analysis date, YYYY-MM-DD")
    parser.add_argument("--historical", action="store_true", help="Exclude unverified current financial snapshots")
    parser.add_argument("--checkpoint", action="store_true")
    args = parser.parse_args()
    date.fromisoformat(args.date)
    config = deepcopy(DEFAULT_CONFIG)
    config.update(point_in_time_strict=args.historical, checkpoint_enabled=args.checkpoint)
    with TradingAgentsGraph(config=config) as graph:
        state, decision = graph.propagate(args.ticker, args.date)
        print(decision)
        print(graph.save_reports(state))


if __name__ == "__main__":
    main()
