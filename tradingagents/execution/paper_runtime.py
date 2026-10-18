"""Persistent local-only forward paper execution alongside existing analysis.

No LLM is called and no broker write client is imported. A source is an actual
completed analysis, never an historical source replayed as today's decision.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo

from tradingagents.atomic_io import atomic_write_json, interprocess_file_lock
from tradingagents.charting.bars import instant
from tradingagents.execution.paper import PaperBroker, PaperLimits
from tradingagents.execution.paper_quotes import ReadOnlyPaperQuotes

SCHEMA = "tradingagents.paper-runtime/v1"


def _read(path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _latest_source(archive, market, now):
    # Canonical run IDs are validated before becoming a filesystem component.
    for path in sorted((archive / "runs").glob("*/*/run.json"), reverse=True):
        try:
            manifest = _read(path)
            if str((manifest.get("settings") or {}).get("market", "")).lower() != market:
                continue
            at = instant(manifest.get("finished_at"))
            started = instant(manifest.get("started_at"))
            if at is None or started is None or not started <= at or not timedelta(0) <= now - at < timedelta(hours=36):
                continue
            if manifest.get("status") != "success":
                continue
            if path.parent.name != manifest.get("run_id"):
                continue
            if all((path.parent / name).is_file() for name in (
                "decision_bundle_v2.json", "portfolio-private/account_snapshot.json", "portfolio-private/proposed_orders.json")):
                return path.parent
        except (ValueError, TypeError, AttributeError):
            continue
    return None


def _load_account(market):
    from tradingagents.portfolio.kis import load_account_snapshot_from_kis
    from tradingagents.portfolio.profiles import load_portfolio_profile
    root = Path(__file__).resolve().parents[2]
    profile = load_portfolio_profile(root / "config/portfolio_profiles.toml", f"{market}_kis_default")
    if not profile.enabled or not profile.read_only or profile.broker != "kis" or profile.broker_environment != "real":
        raise ValueError("READ_ONLY_ACCOUNT_PROFILE_REQUIRED")
    return load_account_snapshot_from_kis(profile).to_dict()


def _account_valid(snapshot, at):
    clock = instant(snapshot.get("as_of"))
    return (clock is not None and 0 <= (at - clock).total_seconds() <= 120
            and snapshot.get("snapshot_health") in {"VALID", "CAPITAL_CONSTRAINED"}
            and snapshot.get("pending_orders") == []
            and not any("pending-order lookup failed" in str(w) for w in snapshot.get("warnings", [])))


def _runtime_session(*, market, now_local):
    from tradingagents.scheduled.market_calendar import market_session_state
    from tradingagents.scheduled.automation_calendar import automated_market_session_status
    session = market_session_state(market=market, now_local=now_local)
    if session.get("is_open"):
        official = automated_market_session_status(market, now_local)
        if official.is_session is not True:
            return {**session, "is_open": False, "phase": "closed" if official.is_session is False else "unknown",
                    "official_source": official.source}
    return session


def _summary(broker):
    counts = {r[0]: r[1] for r in broker.db.execute("SELECT status,count(*) FROM orders GROUP BY status")}
    fill = broker.db.execute("SELECT max(filled_at) FROM orders WHERE status='FILLED'").fetchone()[0]
    return {"order_counts": {k: counts.get(k, 0) for k in ("PENDING", "FILLED", "REJECTED", "CANCELLED")},
            "last_observation_at": broker._get("last_step"), "last_fill_at": fill}


def advance_market(archive, state, market, *, now=None, clock=None, account_loader=None, quote_factory=None,
                   session_resolver=None, limits=None):
    # An explicit fixed ``now`` remains a deterministic offline clock unless a
    # caller supplies an advancing one. Production callers supply neither.
    fixed_now = instant(now) if now is not None else None
    clock = clock or ((lambda: fixed_now) if now is not None else (lambda: datetime.now(timezone.utc)))
    now = instant(now if now is not None else clock())
    if now is None or market not in {"kr", "us"}:
        raise ValueError("Aware real clock and kr/us required")
    limits = limits or PaperLimits()
    session_resolver = session_resolver or _runtime_session
    status_path = state / f"{market}-status.json"
    previous = _read(status_path, {})
    previous = previous if isinstance(previous, dict) else {}
    previous_success = {key: previous.get(key) for key in (
        "source_run_id", "last_observation_at", "last_fill_at", "last_quote_at", "order_counts") if key in previous}
    result = {**previous_success, "schema": SCHEMA, "mode": "LOCAL_PAPER_ONLY", "market": market,
              "checked_at": now.isoformat(), "source_revision": os.getenv("TRADINGAGENTS_SOURCE_SHA"),
              "broker_orders_sent": 0, "real_orders_enabled": False, "blockers": []}

    def finish(status, blockers=(), **fields):
        result.update(status=status, blockers=list(blockers), **fields)
        completed = instant(clock())
        known_clocks = [now] + [instant(result.get(key)) for key in ("last_observation_at", "last_fill_at")]
        if completed is None or any(value is not None and completed < value for value in known_clocks):
            raise ValueError("Paper receipt completion clock precedes its observations")
        # Counters and state are known after account/quote reads and ledger
        # updates finish, never at the earlier request-start timestamp.
        result["checked_at"] = completed.isoformat()
        atomic_write_json(status_path, result)
        return result

    session = session_resolver(market=market, now_local=now)
    ledger = archive / "paper" / f"{market}.sqlite"
    if not session.get("is_open"):
        if ledger.exists():
            broker = PaperBroker(ledger, limits)
            try:
                local_now = now.astimezone(ZoneInfo("Asia/Seoul" if market == "kr" else "America/New_York"))
                broker.expire_pending(now=local_now.isoformat(), halted=(state / "HALT").exists())
                result.update(_summary(broker))
            finally:
                broker.close()
        return finish("MARKET_CLOSED" if session.get("phase") == "closed" else "BLOCKED",
                      () if session.get("phase") == "closed" else ("CALENDAR_UNVERIFIED",), session=session)
    source = _latest_source(archive, market, now)
    if source is None and not ledger.exists():
        return finish("WAITING_SOURCE", ("NO_RECENT_COMPLETED_SOURCE",), session=session)
    account_loader = account_loader or _load_account
    try:
        account = account_loader(market)
        observed = instant(clock())
        if not _account_valid(account, observed):
            return finish("BLOCKED", ("ACCOUNT_NOT_FRESH_COMPLETE_OR_PENDING_ORDERS",), attempted_source_run_id=source.name if source else None)
        broker = PaperBroker(ledger, limits)
        try:
            scope = hashlib.sha256(str(account.get("account_id", "")).encode()).hexdigest()
            if not account.get("account_id"):
                return finish("BLOCKED", ("ACCOUNT_IDENTITY_UNKNOWN",))
            if not broker._get("seeded"):
                broker.seed(account, account_scope=scope)
            elif broker._get("account_scope") != scope:
                return finish("BLOCKED", ("PAPER_ACCOUNT_IDENTITY_CHANGED",))
            # Import is local; the adapter never sends orders or fetches data.
            from tradingagents.execution.archive_paper import build_step
            step = {"signals": []}
            bundle_at = None
            if source is not None:
                source_account, step, selected = build_step(source, observed.isoformat(), limits)
                if selected != market:
                    return finish("BLOCKED", ("SOURCE_MARKET_MISMATCH",))
                if (not source_account.get("account_id")
                        or hashlib.sha256(str(source_account["account_id"]).encode()).hexdigest() != scope):
                    return finish("BLOCKED", ("SOURCE_ACCOUNT_IDENTITY_MISMATCH",))
                bundle_at = instant(_read(source / "decision_bundle_v2.json").get("generated_at"))
            if bundle_at is None or not 0 <= (observed - bundle_at).total_seconds() < 600:
                # Positions still get a genuine new valuation; expired proposals
                # never become new orders merely because quotes were refreshed.
                step["signals"] = []
                result["blockers"].append("SOURCE_EXECUTION_EXPIRED" if source else "NO_RECENT_COMPLETED_SOURCE")
            if market == "us":
                # build_step deliberately sizes only KR. For USD simulation use
                # the new independently observed reference rate, with the same
                # explicit proposal budgets and unchanged engine limits.
                result["fx_basis"] = "BROKER_REFERENCE_RATE; valuation only, no FX trades"
                result["simulation_basis"] = "KRW_CASH_SHADOW: cash remains in seed KRW; USD positions revalued at observed broker reference FX; not an exact USD account mirror"
            held = {r[0] for r in broker.db.execute("SELECT ticker FROM positions WHERE qty>0")}
            pending = {r[0] for r in broker.db.execute("SELECT ticker FROM orders WHERE status='PENDING'")}
            tickers = held | pending | {s["ticker"] for s in step["signals"]}
            provider = (quote_factory or ReadOnlyPaperQuotes)()
            try:
                quotes, quote_blockers = provider.fetch(tickers, market=market,
                    fx_quote=(account.get("cash_diagnostics") or {}).get("fx_quote"))
            finally:
                provider.close()
            at = instant(clock())
            # A response acquired after the market close cannot open new orders.
            if not session_resolver(market=market, now_local=at).get("is_open"):
                broker.expire_pending(now=at.astimezone(ZoneInfo("Asia/Seoul" if market == "kr" else "America/New_York")).isoformat())
                return finish("MARKET_CLOSED", ("SESSION_ENDED_DURING_READ",), **_summary(broker))
            if not _account_valid(account, at):
                return finish("BLOCKED", ("ACCOUNT_EXPIRED_DURING_READ",), **_summary(broker))
            signals = []
            if market == "us" and step["signals"]:
                from tradingagents.execution.sizing import size_paper_order
                proposals = (_read(source / "portfolio-private/proposed_orders.json") or {}).get("orders", [])
                for signal in step["signals"]:
                    q = quotes.get(signal["ticker"])
                    if q is None:
                        continue
                    p = next((p for p in proposals if p.get("canonical_ticker") == signal["ticker"]
                              and str(p.get("side")).upper() == ("BUY" if signal["action"] == "BUY" else "SELL")), {})
                    held_qty = broker.db.execute("SELECT qty FROM positions WHERE ticker=?", (signal["ticker"],)).fetchone()
                    size = size_paper_order(side="BUY" if signal["action"] == "BUY" else "SELL",
                        quantity=(int(p["estimated_qty"]) if isinstance(p.get("estimated_qty"), (int, float))
                                  and not isinstance(p["estimated_qty"], bool) and p["estimated_qty"] > 0
                                  and float(p["estimated_qty"]).is_integer() else None),
                        budget_krw=abs(p["delta_krw_now"]) if p.get("delta_krw_now") else None,
                        price_krw=q["price_krw"], nav_krw=broker._get("cash") + sum(r[0]*r[1] for r in broker.db.execute("SELECT qty,price FROM positions")),
                        available_qty=held_qty[0] if held_qty else 0, limits=limits)
                    signal.update(quantity=size.quantity or None, sizing_reason=size.reason)
            for signal in step["signals"]:
                # Each actual producer run is a single evaluation. Restarts and
                # minute ticks cannot consume it twice with a changed fingerprint.
                signal["signal_id"] = f"{source.name}:{signal['signal_id']}"
                key = hashlib.sha256(f"{signal['signal_id']}|{signal['ticker']}|{signal['action']}".encode()).hexdigest()
                if not broker.db.execute("SELECT 1 FROM orders WHERE id=?", (key,)).fetchone():
                    signals.append(signal)
            local_at = at.astimezone(ZoneInfo("Asia/Seoul" if market == "kr" else "America/New_York")).isoformat()
            receipt = broker.step(now=local_at, quotes=quotes, signals=signals, halted=(state / "HALT").exists())
            valid_clocks = [instant(q["as_of"]) for q in quotes.values() if instant(q.get("as_of"))]
            # Detailed prices/cash are private. Only safe operational status is
            # supplied to the read-only viewer and routine task logs.
            atomic_write_json(archive / "paper" / f"{market}-latest-private.json", receipt)
            result.update(_summary(broker), source_run_id=source.name if source else result.get("source_run_id"),
                          quote_blockers=quote_blockers, marks_complete=receipt["marks_complete"],
                          trading_state=receipt["trading_state"])
            if valid_clocks:
                result["last_quote_at"] = max(valid_clocks).isoformat()
            blockers = result["blockers"] + sorted(set(quote_blockers.values()))
            state_label = "BLOCKED" if not receipt["marks_complete"] or quote_blockers else "VALUATION_ONLY" if blockers else "ACTIVE"
            return finish(state_label, blockers)
        finally:
            broker.close()
    except Exception as exc:
        # Exceptions may embed private account/HTTP details; never persist them.
        return finish("ERROR", ("PAPER_TICK_FAILED",), error_type=type(exc).__name__, attempted_source_run_id=source.name if source else None)


def tick(archive, state, *, now=None, clock=None, **kwargs):
    archive, state = Path(archive).resolve(), Path(state).resolve()
    state.mkdir(parents=True, exist_ok=True)
    fixed_now = instant(now) if now is not None else None
    clock = clock or ((lambda: fixed_now) if now is not None else (lambda: datetime.now(timezone.utc)))
    at = instant(now if now is not None else clock())
    if at is None:
        raise ValueError("Aware now required")
    with interprocess_file_lock(state / "paper.lock", timeout=0):
        enabled = _read(state / "enabled.json", {})
        if enabled.get("mode") != "LOCAL_PAPER_ONLY" or enabled.get("enabled") is not True:
            return {"schema": SCHEMA, "status": "DISABLED", "broker_orders_sent": 0, "real_orders_enabled": False}
        markets = {market: advance_market(archive, state, market, now=at, clock=clock, **kwargs) for market in ("kr", "us")}
        completed = instant(clock())
        if completed is None or completed < at or any(completed < instant(receipt["checked_at"]) for receipt in markets.values()):
            raise ValueError("Paper tick completion clock precedes a market receipt")
        result = {"schema": SCHEMA, "mode": "LOCAL_PAPER_ONLY", "enabled": True, "checked_at": completed.isoformat(),
                  "broker_orders_sent": 0, "real_orders_enabled": False, "markets": markets}
        atomic_write_json(archive / "paper/status.json", result)
        return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive-dir", required=True, type=Path)
    parser.add_argument("--state-dir", required=True, type=Path)
    parser.add_argument("--enable", action="store_true")
    args = parser.parse_args(argv)
    if args.enable:
        atomic_write_json(args.state_dir / "enabled.json", {"mode": "LOCAL_PAPER_ONLY", "enabled": True,
                          "created_at": datetime.now(timezone.utc).isoformat(), "real_orders_enabled": False})
    result = tick(args.archive_dir, args.state_dir)
    print(json.dumps(result, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
