"""Optional localhost read-only adapter for existing archived reports."""
from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sqlite3
from urllib.parse import parse_qs, urlparse

from .bars import instant
from .snapshot import get_replay_snapshot
from .operations import archive_catalog, known_artifacts, paper_health, now_utc

STATIC = Path(__file__).parent / "static"


def make_handler(run_dir=None, *, db_paths=(), archive_dir=None, experiment_registry=None, paper_status_path=None):
    if (run_dir is None) == (archive_dir is None):
        raise ValueError("Choose one existing run_dir or archive_dir")
    def catalog(cutoff, *, only_ticker=None, include_coverage=True):
        if archive_dir is not None:
            return archive_catalog(archive_dir, analysis_as_of=cutoff, only_ticker=only_ticker, include_coverage=include_coverage)
        root = (Path(run_dir) / "tickers").resolve()
        # An allowlist of archive directories, never an arbitrary request-supplied path.
        return {path.name: {"ticker_dir": path, "public_context": {"run_id": Path(run_dir).name,
                **(known_artifacts(path, cutoff) if include_coverage else {})}}
                for path in root.iterdir() if path.is_dir() and path.resolve().is_relative_to(root)
                and (only_ticker is None or path.name == only_ticker)}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def reply(self, status, body, content_type):
            encoded = body.encode("utf-8") if isinstance(body, str) else body
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(encoded)

        def do_GET(self):
            # Defend against browser DNS rebinding to the localhost data adapter.
            if self.headers.get("Host", "").split(":")[0] not in {"127.0.0.1", "localhost"}:
                self.reply(403, "Local host required", "text/plain")
                return
            parsed = urlparse(self.path)
            try:
                if len(self.path) > 12_000:
                    self.reply(414, "Query too long", "text/plain")
                    return
                query = parse_qs(parsed.query)
                at = instant(query.get("as_of", [now_utc().isoformat()])[0])
                if parsed.path.startswith("/api/") and (at is None or at > now_utc()):
                    self.reply(400, "Past aware as_of required", "text/plain")
                    return
                if parsed.path == "/api/tickers":
                    self.reply(200, json.dumps(sorted(catalog(at, include_coverage=False))), "application/json")
                elif parsed.path == "/api/context":
                    payload = {"as_of": at.isoformat(), "archive_mode": archive_dir is not None,
                               "tickers": {ticker: entry["public_context"] for ticker, entry in catalog(at).items()},
                               "journal_sources_configured": len(db_paths),
                               "experiment_registry_configured": experiment_registry is not None,
                               "read_only": True, "broker_orders_sent": 0, "real_orders_enabled": False}
                    self.reply(200, json.dumps(payload, ensure_ascii=False), "application/json; charset=utf-8")
                elif parsed.path == "/api/paper-health":
                    self.reply(200, json.dumps(paper_health(paper_status_path, analysis_as_of=at)), "application/json; charset=utf-8")
                elif parsed.path == "/api/condition-draft":
                    from tradingagents.scanner.natural_language import compile_condition_text
                    draft = compile_condition_text(query.get("text", [""])[0], market=query.get("market", [None])[0])
                    self.reply(200, json.dumps(draft, ensure_ascii=False, allow_nan=False), "application/json; charset=utf-8")
                elif parsed.path == "/api/experiment-cards":
                    from tradingagents.execution.experiment_cards import list_experiment_cards, read_experiment_card
                    if experiment_registry is None:
                        cards = {"status": "not_configured", "cards": [], "issues": ["experiment_registry_not_configured"], "as_of": at.isoformat()}
                    elif query.get("experiment_id"):
                        cards = read_experiment_card(experiment_registry, query["experiment_id"][0], analysis_as_of=at.isoformat())
                    else:
                        cards = list_experiment_cards(experiment_registry, analysis_as_of=at.isoformat())
                    self.reply(200, json.dumps(cards, ensure_ascii=False, allow_nan=False), "application/json; charset=utf-8")
                elif parsed.path == "/api/snapshot":
                    ticker = query.get("ticker", [""])[0]
                    tickers = catalog(at, only_ticker=ticker)
                    if ticker not in tickers:
                        self.reply(400, "Valid ticker and past aware as_of required", "text/plain")
                        return
                    snapshot = get_replay_snapshot(ticker, at, ticker_dir=tickers[ticker]["ticker_dir"], db_paths=db_paths,
                                                   anchor=query.get("anchor", [None])[0])
                    snapshot["source_context"] = tickers[ticker]["public_context"]
                    self.reply(200, json.dumps(snapshot, ensure_ascii=False, allow_nan=False), "application/json; charset=utf-8")
                else:
                    allowed = {"/": ("viewer.html", "text/html; charset=utf-8"),
                               "/viewer.js": ("viewer.js", "text/javascript"),
                               "/lightweight.js": ("lightweight-charts-5.2.0.js", "text/javascript"),
                               "/NOTICE": ("NOTICE.lightweight-charts", "text/plain; charset=utf-8"),
                               "/LICENSE": ("LICENSE.lightweight-charts", "text/plain; charset=utf-8")}
                    allowed["/LICENSE.fancy-canvas"] = ("LICENSE.fancy-canvas", "text/plain; charset=utf-8")
                    if parsed.path not in allowed:
                        self.reply(404, "Not found", "text/plain")
                        return
                    name, kind = allowed[parsed.path]
                    self.reply(200, (STATIC / name).read_bytes(), kind)
            except (OSError, ValueError, KeyError, TypeError, sqlite3.DatabaseError):
                self.reply(422, "Archive input invalid or unavailable", "text/plain")
    return Handler


def serve(run_dir=None, *, port=8765, db_paths=(), archive_dir=None, experiment_registry=None, paper_status_path=None):
    server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(run_dir, db_paths=db_paths, archive_dir=archive_dir,
                                 experiment_registry=experiment_registry, paper_status_path=paper_status_path))
    print(f"TradingAgents local read-only review: http://127.0.0.1:{server.server_port}", flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(description="Open existing TradingAgents archive data through a read-only localhost viewer")
    sources = parser.add_mutually_exclusive_group(required=True)
    sources.add_argument("--run-dir", type=Path)
    sources.add_argument("--archive-dir", type=Path)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--journal", "--tracker-db", type=Path, action="append", default=[])
    parser.add_argument("--experiment-registry", type=Path)
    parser.add_argument("--paper-status", type=Path)
    args = parser.parse_args(argv)
    if args.run_dir is not None and not (args.run_dir / "tickers").is_dir():
        parser.error("--run-dir must contain an existing tickers archive directory")
    if args.archive_dir is not None and not args.archive_dir.is_dir():
        parser.error("--archive-dir must exist")
    if not 0 <= args.port <= 65535:
        parser.error("--port must be between 0 and 65535")
    serve(args.run_dir, port=args.port, db_paths=args.journal, archive_dir=args.archive_dir,
          experiment_registry=args.experiment_registry, paper_status_path=args.paper_status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
