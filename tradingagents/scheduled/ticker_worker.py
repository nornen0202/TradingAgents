from __future__ import annotations

import argparse
import json
import os
import traceback
from pathlib import Path
from typing import Any

from .config import load_scheduled_config
from .runner import _run_single_ticker


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run one scheduled ticker analysis worker.")
    parser.add_argument("--config", required=True, help="Scheduled analysis TOML config path.")
    parser.add_argument("--ticker", required=True, help="Ticker to analyze.")
    parser.add_argument("--run-dir", required=True, help="Parent run directory.")
    parser.add_argument("--engine-results-dir", required=True, help="Engine results directory.")
    parser.add_argument("--summary-json", required=True, help="Worker summary output JSON path.")
    parser.add_argument("--trade-date", help="Optional resolved trade date override.")
    args = parser.parse_args(argv)

    summary_path = Path(args.summary_json)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        config = load_scheduled_config(args.config)
        summary = _run_single_ticker(
            config=config,
            ticker=args.ticker,
            run_dir=Path(args.run_dir),
            engine_results_dir=Path(args.engine_results_dir),
            trade_date_override=args.trade_date,
        )
        _write_summary(summary_path, summary)
        return 0
    except Exception as exc:
        payload: dict[str, Any] = {
            "ticker": args.ticker,
            "status": "failed",
            "error": str(exc),
            "traceback": traceback.format_exc(),
            "worker_pid": os.getpid(),
        }
        _write_summary(summary_path, payload)
        return 1


def _write_summary(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
