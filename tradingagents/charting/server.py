"""Optional localhost read-only adapter for existing archived reports."""
from __future__ import annotations

from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .bars import instant
from .snapshot import get_replay_snapshot

STATIC = Path(__file__).parent / "static"


def make_handler(run_dir, *, db_paths=()):
    root = (Path(run_dir) / "tickers").resolve()
    # An allowlist of archive directories, never an arbitrary request-supplied path.
    tickers = {path.name: path for path in root.iterdir() if path.is_dir() and path.resolve().is_relative_to(root)}

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
                if parsed.path == "/api/tickers":
                    self.reply(200, json.dumps(sorted(tickers)), "application/json")
                elif parsed.path == "/api/snapshot":
                    query = parse_qs(parsed.query)
                    ticker = query.get("ticker", [""])[0]
                    at = instant(query.get("as_of", [datetime.now(timezone.utc).isoformat()])[0])
                    if ticker not in tickers or at is None or at > datetime.now(timezone.utc):
                        self.reply(400, "Valid ticker and past aware as_of required", "text/plain")
                        return
                    snapshot = get_replay_snapshot(ticker, at, ticker_dir=tickers[ticker], db_paths=db_paths,
                                                   anchor=query.get("anchor", [None])[0])
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
            except (OSError, ValueError, KeyError, TypeError):
                self.reply(422, "Archive input invalid or unavailable", "text/plain")
    return Handler


def serve(run_dir, *, port=8765, db_paths=()):
    server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(run_dir, db_paths=db_paths))
    print(f"TradingAgents local read-only review: http://127.0.0.1:{server.server_port}", flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(description="Open existing TradingAgents archive data through a read-only localhost viewer")
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--journal", type=Path, action="append", default=[])
    args = parser.parse_args(argv)
    if not (args.run_dir / "tickers").is_dir():
        parser.error("--run-dir must contain an existing tickers archive directory")
    if not 0 <= args.port <= 65535:
        parser.error("--port must be between 0 and 65535")
    serve(args.run_dir, port=args.port, db_paths=args.journal)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
