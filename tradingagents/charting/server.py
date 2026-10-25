"""Optional localhost read-only adapter for existing archived reports."""
from __future__ import annotations

from datetime import timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import json
from pathlib import Path
import sqlite3
from urllib.parse import parse_qs, urlparse

from .bars import instant
from .catalog_index import ArchiveCatalogIndex, CatalogPending
from .snapshot_jobs import (
    SnapshotJobs, SnapshotJobError, evidence_fingerprint, journal_fingerprint, journal_identities,
    tracked_source_metadata, boundary_identities,
)
from .snapshot import get_replay_snapshot
from .operations import archive_catalog, known_artifacts, paper_health, kis_demo_health, kis_validation_health, kis_strategy_health, now_utc

STATIC = Path(__file__).parent / "static"


class JournalScopeError(ValueError):
    """Do not combine another market's paper account into a ticker replay."""


def _snapshot_journals(ticker, source_context, common_paths, market_journals):
    if market_journals is None:
        return common_paths  # Existing explicit single-account CLI contract.
    from tradingagents.agents.utils.instrument_resolver import resolve_instrument
    try:
        market = source_context.get("market")
        country = resolve_instrument(ticker).country.upper()
        expected = "KR" if country == "KR" else "US" if country == "US" else None
        if not isinstance(market, str) or market.upper() != expected or expected not in market_journals:
            raise ValueError("Unverified journal market")
    except (ValueError, AttributeError) as error:
        raise JournalScopeError("Archive journal market scope unverified") from error
    return (*common_paths, market_journals[expected])


def make_handler(run_dir=None, *, db_paths=(), archive_dir=None, experiment_registry=None, paper_status_path=None,
                 strategy_ledger_dir=None, market_journals=None):
    if (run_dir is None) == (archive_dir is None):
        raise ValueError("Choose one existing run_dir or archive_dir")
    db_paths = tuple(db_paths)
    if market_journals is not None:
        if not isinstance(market_journals, dict) or not market_journals or set(market_journals) - {"KR", "US"}:
            raise ValueError("Explicit KR/US single-account journal mapping required")
        market_journals = {market: Path(path) for market, path in market_journals.items()}
        if len({path.resolve() for path in market_journals.values()}) != len(market_journals):
            raise ValueError("Markets must not share a paper account journal")
    index = ArchiveCatalogIndex(archive_dir) if archive_dir is not None else None
    jobs = SnapshotJobs()
    # These are configuration bindings, never request-supplied file paths.
    journal_bounds = {Path(path): Path(path).resolve() for path in (*db_paths, *(market_journals or {}).values())}
    def catalog(cutoff, *, only_ticker=None, include_coverage=True, names_only=False, generation=None):
        if archive_dir is not None:
            token, entries = index.snapshot_with_generation(generation=generation)
            return token, archive_catalog(archive_dir, analysis_as_of=cutoff, only_ticker=only_ticker,
                                   include_coverage=include_coverage, names_only=names_only,
                                   manifest_entries=entries)
        root = (Path(run_dir) / "tickers").resolve()
        # An allowlist of archive directories, never an arbitrary request-supplied path.
        return 0, {path.name: {"ticker_dir": path, "public_context": {"run_id": Path(run_dir).name,
                **(known_artifacts(path, cutoff) if include_coverage else {})}}
                for path in root.iterdir() if path.is_dir() and path.resolve().is_relative_to(root)
                and (only_ticker is None or path.name == only_ticker)}

    def build_snapshot(ticker, cutoff, anchor, catalog_ticket, progress):
        progress("INDEX")
        if index is not None:
            entries = catalog_ticket.result()
            progress("SELECTION_COVERAGE")
            selected = archive_catalog(archive_dir, analysis_as_of=cutoff, only_ticker=ticker,
                                       names_only=True, manifest_entries=entries)
        else:
            progress("SELECTION_COVERAGE")
            _, selected = catalog(cutoff, only_ticker=ticker, include_coverage=False)
        if ticker not in selected:
            raise SnapshotJobError(400, "Valid ticker and past aware as_of required")
        directory = selected[ticker]["ticker_dir"]
        manifest = directory.parent.parent / "run.json" if index is not None else None
        expected = next((raw for path, raw in entries if path == manifest), None) if index is not None else None
        context = {"market": (expected.get("settings") or {}).get("market")} if expected is not None else selected[ticker]["public_context"]
        try:
            journals = _snapshot_journals(ticker, context, db_paths, market_journals)
        except JournalScopeError:
            raise SnapshotJobError(422, "Archive journal market scope unverified") from None
        bound_journals = tuple(journal_bounds[Path(path)] for path in journals)
        root = index.root if index is not None else (Path(run_dir) / "tickers").resolve()
        alias = Path(archive_dir) / "runs" if index is not None else Path(run_dir) / "tickers"
        def journals_stamp():
            if any(Path(path).resolve() != journal_bounds[Path(path)] for path in journals):
                raise ValueError("Configured journal scope changed")
            return journal_fingerprint(bound_journals)
        def fingerprint():
            return evidence_fingerprint(directory, root=root, manifest=manifest, alias=alias)
        before = fingerprint()
        boundaries = boundary_identities((root, alias))
        journal_before = journals_stamp()
        if manifest is not None:
            from .catalog_index import project_manifest
            if expected is None or project_manifest(manifest)[1] != expected:
                raise ValueError("Catalog source changed")
            selected = archive_catalog(archive_dir, analysis_as_of=cutoff, only_ticker=ticker,
                                       manifest_entries=((manifest, expected),))
            if ticker not in selected:
                raise ValueError("Catalog source changed")
            context = selected[ticker]["public_context"]
        else:
            context = {**context, **known_artifacts(directory, cutoff)}
        private_proofs = []
        snapshot = get_replay_snapshot(ticker, cutoff, ticker_dir=directory, db_paths=bound_journals,
                                       anchor=anchor, phase_hook=progress, journal_proof_hook=private_proofs.append)
        if journals and len(private_proofs) != 1:
            raise ValueError("Snapshot journal proof unavailable")
        snapshot["source_context"] = context
        def lifecycle_hash(value):
            return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
        expected_lifecycle = lifecycle_hash(snapshot.get("lifecycle", {}))
        def verify():
            nonlocal journal_before
            if boundary_identities((root, alias)) != boundaries:
                raise ValueError("Archive root boundary changed")
            if fingerprint() != before:
                raise ValueError("Archive snapshot evidence changed")
            current = journals_stamp()
            if journal_identities(current) != journal_identities(journal_before):
                raise ValueError("Configured journal identity changed")
            if current != journal_before:
                # Appends after the explicit cutoff must not change or erase a
                # past view. Compare the existing strict reader's visible proof,
                # not the whole database bytes or its latest write timestamp.
                from tradingagents.performance.replay import replay_action_history
                for _ in range(2):
                    revised_proofs = []
                    replay = replay_action_history(bound_journals, analysis_as_of=cutoff.isoformat(), ticker=ticker,
                                                   proof_hook=revised_proofs.append) if journals else {}
                    if (lifecycle_hash(replay) != expected_lifecycle
                            or revised_proofs != private_proofs):
                        raise ValueError("Cutoff-visible journal proof changed")
                    after = journals_stamp()
                    if journal_identities(after) != journal_identities(journal_before):
                        raise ValueError("Configured journal identity changed")
                    if after == current:
                        journal_before = after
                        break
                    # Never promote metadata for bytes the replay did not see.
                    # One concurrent future append can stabilize on the second
                    # pass; continuing writes exhaust this bounded verification.
                    current = after
                else:
                    raise ValueError("Journal changed during bounded verification")
                if fingerprint() != before:
                    raise ValueError("Archive snapshot evidence changed")
        progress("VERIFY")
        verify()
        def delivery_valid():
            # Only known-path stat checks run on HTTP delivery. Changed
            # metadata re-enters the worker; replay/JSON/discovery stay there.
            return (boundary_identities((root, alias)) == boundaries
                    and tracked_source_metadata(before) == before
                    and all(Path(path).resolve() == journal_bounds[Path(path)] for path in journals)
                    and journal_fingerprint(bound_journals, validate_paths=False) == journal_before)
        return snapshot, verify, delivery_valid

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def reply(self, status, body, content_type):
            encoded = body.encode("utf-8") if isinstance(body, str) else body
            try:
                self._reply(status, encoded, content_type)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                # Manual retry/navigation can cancel a read-only request while
                # its response is being written. Do not send a second response.
                return

        def _reply(self, status, encoded, content_type):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("Cache-Control", "no-store")
            if getattr(self, "catalog_generation", None) is not None:
                self.send_header("X-Archive-Catalog-Generation", str(self.catalog_generation))
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
                generation = int(query["catalog_generation"][0]) if "catalog_generation" in query else None
                if generation is not None and generation < (1 if index is not None else 0):
                    raise SnapshotJobError(400, "Invalid archive catalog generation")
                at = instant(query.get("as_of", [now_utc().isoformat()])[0])
                if parsed.path.startswith("/api/") and (at is None or at > now_utc()):
                    self.reply(400, "Past aware as_of required", "text/plain")
                    return
                if parsed.path == "/api/tickers":
                    self.catalog_generation, tickers = catalog(at, include_coverage=False, names_only=True, generation=generation)
                    self.reply(200, json.dumps(sorted(tickers)), "application/json")
                elif parsed.path == "/api/context":
                    self.catalog_generation, tickers = catalog(at, generation=generation)
                    payload = {"as_of": at.isoformat(), "archive_mode": archive_dir is not None,
                               "tickers": {ticker: entry["public_context"] for ticker, entry in tickers.items()},
                               "journal_sources_configured": len(db_paths) + len(market_journals or {}),
                               "experiment_registry_configured": experiment_registry is not None,
                               "read_only": True, "broker_orders_sent": 0, "real_orders_enabled": False}
                    self.reply(200, json.dumps(payload, ensure_ascii=False), "application/json; charset=utf-8")
                elif parsed.path == "/api/paper-health":
                    self.reply(200, json.dumps(paper_health(paper_status_path, analysis_as_of=at)), "application/json; charset=utf-8")
                elif parsed.path == "/api/kis-demo-health":
                    self.reply(200, json.dumps(kis_demo_health(archive_dir, analysis_as_of=at)), "application/json; charset=utf-8")
                elif parsed.path == "/api/kis-validation-health":
                    self.reply(200, json.dumps(kis_validation_health(archive_dir, analysis_as_of=at)), "application/json; charset=utf-8")
                elif parsed.path == "/api/kis-strategy-health":
                    self.reply(200, json.dumps(kis_strategy_health(archive_dir, analysis_as_of=at, strategy_ledger_dir=strategy_ledger_dir), allow_nan=False), "application/json; charset=utf-8")
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
                    if "as_of" not in query:
                        # Polling must retain one explicit point in time. A
                        # moving default of now cannot be an immutable job key.
                        raise SnapshotJobError(400, "Explicit past aware as_of required for a snapshot")
                    if "snapshot_cancel" in query:
                        # A shared read-only job is not an observer's authority
                        # to cancel another tab's work or confirm an order.
                        raise SnapshotJobError(400, "Snapshot cancellation is not a public API")
                    ticker = query.get("ticker", [""])[0]
                    if not ticker or Path(ticker).name != ticker or ticker in {".", ".."} or "/" in ticker or "\\" in ticker:
                        raise SnapshotJobError(400, "Valid ticker and past aware as_of required")
                    anchor = query.get("anchor", [None])[0]
                    if anchor is not None and (instant(anchor) is None or instant(anchor) > at):
                        raise SnapshotJobError(400, "Past aware anchor required")
                    token = query.get("snapshot_job", [None])[0]
                    if token is not None and (len(token) > 160 or not token or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in token)):
                        raise SnapshotJobError(400, "Invalid archive snapshot token")
                    if token is not None and generation is None:
                        raise SnapshotJobError(400, "Snapshot polling requires its catalog generation")
                    try:
                        # Existing opaque jobs already bind their exact cohort.
                        # Another tab refreshing the index must not invalidate
                        # that job merely by evicting old index metadata.
                        if token is not None:
                            self.catalog_generation = generation
                            catalog_ticket = None
                        else:
                            if index is not None:
                                self.catalog_generation, catalog_ticket = index.capture_generation(generation)
                            else:
                                self.catalog_generation, catalog_ticket = 0, None
                    except ValueError:
                        raise SnapshotJobError(409, "Archive catalog generation is stale or unknown; refresh the catalog") from None
                    if index is None and generation not in {None, 0}:
                        raise SnapshotJobError(409, "Archive catalog generation is stale or unknown; refresh the catalog")
                    actual_generation = self.catalog_generation
                    key = (ticker, at.astimezone(timezone.utc).isoformat(), anchor, actual_generation)
                    status, payload = jobs.request(key, lambda progress: build_snapshot(ticker, at, anchor, catalog_ticket, progress), token=token)
                    self.reply(status, json.dumps(payload) if status == 202 else payload, "application/json; charset=utf-8")
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
            except CatalogPending as pending:
                self.catalog_generation = pending.progress["generation"]
                self.reply(202, json.dumps(pending.progress), "application/json")
            except SnapshotJobError as error:
                self.reply(error.status, error.message, "text/plain")
            except JournalScopeError:
                self.reply(422, "Archive journal market scope unverified", "text/plain")
            except (OSError, ValueError, KeyError, TypeError, sqlite3.DatabaseError):
                self.reply(422, "Archive input invalid or unavailable", "text/plain")
    return Handler


def serve(run_dir=None, *, port=8765, db_paths=(), archive_dir=None, experiment_registry=None, paper_status_path=None,
          strategy_ledger_dir=None, market_journals=None):
    server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(run_dir, db_paths=db_paths, archive_dir=archive_dir,
                                 experiment_registry=experiment_registry, paper_status_path=paper_status_path,
                                 strategy_ledger_dir=strategy_ledger_dir, market_journals=market_journals))
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
    parser.add_argument("--strategy-ledgers", type=Path, help="Existing normal-strategy ledgers; read-only cost validation")
    parser.add_argument("--paper-journal-kr", type=Path, help="Single KR paper account; selected only for a verified KR source")
    parser.add_argument("--paper-journal-us", type=Path, help="Single US paper account; selected only for a verified US source")
    args = parser.parse_args(argv)
    if args.run_dir is not None and not (args.run_dir / "tickers").is_dir():
        parser.error("--run-dir must contain an existing tickers archive directory")
    if args.archive_dir is not None and not args.archive_dir.is_dir():
        parser.error("--archive-dir must exist")
    if not 0 <= args.port <= 65535:
        parser.error("--port must be between 0 and 65535")
    serve(args.run_dir, port=args.port, db_paths=args.journal, archive_dir=args.archive_dir,
          experiment_registry=args.experiment_registry, paper_status_path=args.paper_status,
          strategy_ledger_dir=args.strategy_ledgers,
          market_journals=({market: path for market, path in (("KR", args.paper_journal_kr), ("US", args.paper_journal_us))
                            if path is not None} or None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
