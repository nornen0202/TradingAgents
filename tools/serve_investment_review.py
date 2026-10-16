"""Open an archived TradingAgents run through a read-only localhost viewer."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tradingagents.charting.server import serve


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--tracker-db", action="append", type=Path, default=[])
    args = parser.parse_args()
    serve(args.run_dir, port=args.port, db_paths=args.tracker_db)
