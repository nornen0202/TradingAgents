"""Open an archived TradingAgents run through a read-only localhost viewer."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tradingagents.charting.server import serve


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path, nargs="?")
    parser.add_argument("--archive-dir", type=Path)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--tracker-db", action="append", type=Path, default=[])
    parser.add_argument("--experiment-registry", type=Path)
    parser.add_argument("--paper-status", type=Path)
    args = parser.parse_args()
    if (args.run_dir is None) == (args.archive_dir is None):
        parser.error("Choose either run_dir or --archive-dir")
    if not 0 <= args.port <= 65535:
        parser.error("--port must be between 0 and 65535")
    serve(args.run_dir, port=args.port, db_paths=args.tracker_db, archive_dir=args.archive_dir,
          experiment_registry=args.experiment_registry, paper_status_path=args.paper_status)
