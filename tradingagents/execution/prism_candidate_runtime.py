"""Private five-minute hints consumed only after ordinary VTS admission."""
from contextlib import closing
from datetime import timedelta
from pathlib import Path
import sqlite3
from zoneinfo import ZoneInfo

from tradingagents.atomic_io import atomic_write_json, interprocess_file_lock
from tradingagents.charting.bars import instant
from tradingagents.performance.price_evidence import native_reference
from tradingagents.scheduled.research_refresh import MAX_LINEAGE, artifact, digest, manifest_path, rows_by_ticker, verified_revision
from .paper_runtime import _latest_source, _read
from .prism_autotrader import (
    MARKET_CURRENCIES, MARKET_ZONES, _derive_stop_and_target, _num, evaluate_prism_buy_gate,
    load_autotrader_policy, risk_exit_reason,
)

SCHEMA = "tradingagents.prism-vts-candidates/v1"
SOURCE_ARTIFACTS = ("decision_bundle_v2.json", "portfolio-private/portfolio_candidates.json")
KIS_QUOTE_PROVIDERS = {"kis", "kis_quote", "kis_microstructure"}


def active(lane, policy):
    return (policy.mode == "kis_vts" and policy.enabled is True and policy.kill_switch is False
            and policy.live_orders_confirmed is False and not (lane / "HALT").exists())


def baseline(archive, source, market, now):
    """Read a completed same-market lineage back to its verified full root."""
    from tradingagents.scheduled.runner import _manifest_is_complete_overlay_baseline

    seen = set()
    cohort = None
    cutoff = now
    expected = source.name
    current = source / "run.json"
    for _ in range(MAX_LINEAGE):
        if expected in seen:
            break
        seen.add(expected)
        manifest = _read(current)
        settings = manifest["settings"]
        started, finished = instant(manifest["started_at"]), instant(manifest["finished_at"])
        if (manifest["run_id"] != expected or manifest["status"] != "success" or settings["market"].upper() != market
                or started is None or finished is None or not started <= finished <= cutoff
                or (manifest.get("active_universe") or {}).get("coverage", {}).get("complete") is not True):
            break
        rows = rows_by_ticker(manifest)
        tickers = rows.keys()
        if cohort is not None and cohort != tickers:
            break
        cohort = tickers
        mode = settings.get("run_mode", "full")
        if mode == "full":
            if (_manifest_is_complete_overlay_baseline(manifest, market=market, requested_tickers=None,
                    required_holding_tickers=None, archive_dir=archive, now=now)
                    and all(artifact(current.parent, row, "analysis_json").is_file() for row in rows.values())):
                return current, finished
            break
        if mode == "selective_rerun_only" and not verified_revision(archive, manifest, market=market, now=now):
            break
        if mode not in {"overlay_only", "selective_rerun_only"}:
            break
        expected = manifest["overlay_source_run_id"]
        current = manifest_path(archive, expected)
        cutoff = started
    raise ValueError("Unverified five-minute research lineage")


def _research(path):
    document = _read(path.parent / SOURCE_ARTIFACTS[1])
    rows = {}
    for item in document["candidates"]:
        ticker = item["instrument"]["canonical_ticker"]
        if ticker in rows:
            raise ValueError("Duplicate five-minute research candidate")
        rows[ticker] = item
    return rows, (document.get("batch_metrics") or {}).get("market_regime")


def _journal(lane, market, now):
    from .demo_runtime import summary

    path = lane.parent / "kis-strategy" / f"{market.lower()}-strategy.sqlite"
    if not path.is_file():
        return {}, []
    with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        db.row_factory = sqlite3.Row
        state = summary(db, now, market, order_limit=None)
    return state["owned"], state["orders"]


def _reference(item, market, finished):
    reference, _ = native_reference((item.get("data_health") or {}).get("price_reference"), market, finished.isoformat())
    return reference.price if reference and reference.basis == "unadjusted" else None


def _entries(research, regime, owned, policy, market, finished):
    held = {ticker for ticker, qty in owned.items() if qty > 0}
    entries = {}
    for ticker, item in research.items():
        if ticker in held:
            continue
        price = _reference(item, market, finished)
        sector = item.get("sector")
        gate = evaluate_prism_buy_gate(item, current_price=price, regime=regime, slots_used=len(held),
            max_slots=min(10, policy.max_slots), same_sector_count=sum(research.get(it, {}).get("sector") == sector for it in held),
            max_same_sector=policy.max_same_sector, policy=policy)
        if gate.allowed:
            entries[ticker] = {"reference_price": price, "score": gate.effective_score,
                               "slot_fraction": gate.slot_fraction}
    return entries


def _regular(session, now):
    opened, closed = instant(session.get("session_open")), instant(session.get("session_close"))
    return (session.get("source") == "exchange_calendars" and session.get("is_open") is True
            and session.get("phase") == "regular" and opened is not None and closed is not None and opened <= now < closed)


def _exit_price(row, opened, now):
    clock = instant(row.get("market_data_asof"))
    quality = row.get("quality") or {}
    price = _num(row.get("last_price"))
    if (clock is not None and opened <= clock <= now < clock + timedelta(seconds=120)
            and row.get("market_session") == "regular" and row.get("provider") in KIS_QUOTE_PROVIDERS
            and row.get("market_data_basis") == "EXECUTION_CONTEXT"
            and quality.get("generated_in_current_run") is True and quality.get("execution_ready") is True
            and price is not None and price > 0):
        return price
    return None


def _exits(source, market, now, session, research, owned, orders, previous, policy):
    if not _regular(session, now):
        return {}, previous
    bundle_path = source / SOURCE_ARTIFACTS[0]
    bundle = _read(bundle_path)
    generated = instant(bundle["generated_at"])
    finished = instant(_read(source / "run.json")["finished_at"])
    if bundle["market"].upper() != market or generated is None or finished is None or not generated <= finished <= now:
        raise ValueError("Unverified five-minute quote bundle")
    quotes = {row["ticker"]: row for row in bundle["strategy_table"]}
    if len(quotes) != len(bundle["strategy_table"]):
        raise ValueError("Duplicate five-minute quote row")
    exits, marks = {}, {}
    for order in reversed(orders):
        ticker = order["ticker"]
        qty = owned.get(ticker, 0)
        if (ticker in marks or qty != 1 or order["side"] != "BUY" or order["filled_quantity"] != qty
                or order["source"] != "KIS_DEMO_BROKER_REPORT" or ticker not in research):
            continue
        entry, acquired = _num(order["average_fill_price"]), instant(order["first_fill_observed_at"])
        if entry is None or entry <= 0 or acquired is None or acquired > now:
            continue
        row = quotes.get(ticker, {})
        opened = instant(session["session_open"])
        price = _exit_price(row, opened, generated)
        if _exit_price(row, opened, now) is None:
            price = None
        prior = previous.get(ticker, {})
        peak = _num(prior.get("peak"), entry) if prior.get("lot") == order["id"] else entry
        peak = max(peak, price or entry)
        marks[ticker] = {"lot": order["id"], "peak": peak}
        if price is None:
            continue
        item = research[ticker]
        stop, target = _derive_stop_and_target(item, current_price=entry,
            default_stop_pct=policy.default_stop_loss_pct, default_target_pct=policy.default_target_profit_pct)
        zone = ZoneInfo(MARKET_ZONES[market])
        evidence = {"entry": entry, "stop": stop, "target": target, "peak": peak,
                    "runner": (peak / entry - 1) * 100 >= policy.runner_activate_pct,
                    "days": (now.astimezone(zone).date() - acquired.astimezone(zone).date()).days,
                    "risk": item.get("risk_action")}
        if risk_exit_reason(price=price, policy=policy, **evidence):
            exits[ticker] = {**evidence, "observation": row["market_data_asof"], "lot": order["id"]}
    return exits, marks


def _path(lane, market):
    return lane / f"{market.lower()}-vts-candidates.json"


def _receipt(lane, market):
    data = _read(_path(lane, market), {})
    if (data.get("schema") == SCHEMA and data.get("market") == market and data.get("mode") == "kis_vts"
            and data.get("real_orders_enabled") is False):
        return data
    return {}


def produce(archive, lane, market, now, session, policy):
    path = _path(lane, market)
    with interprocess_file_lock(path.with_suffix(".lock"), timeout=0):
        try:
            if not active(lane, policy) or session.get("source") != "exchange_calendars" or session.get("phase") in {None, "unknown"}:
                raise ValueError("Candidate lane or calendar unverified")
            source = _latest_source(archive, market.lower(), now, required_artifacts=SOURCE_ARTIFACTS)
            if source is None:
                raise ValueError("No completed execution source")
            root, finished = baseline(archive, source, market, now)
            expires = finished + timedelta(hours=policy.session_entry_ttl_hours)
            if not finished <= now < expires:
                raise ValueError("Candidate research expired")
            research, regime = _research(root)
            owned, orders = _journal(lane, market, now)
            entries = _entries(research, regime, owned, policy, market, finished)
            exits, marks = _exits(source, market, now, session, research, owned, orders,
                                  _receipt(lane, market).get("marks", {}), policy)
            if not active(lane, policy):
                raise ValueError("Candidate lane stopped during generation")
            atomic_write_json(path, {
                "schema": SCHEMA, "mode": "kis_vts", "market": market, "real_orders_enabled": False,
                "baseline_id": root.parent.name, "baseline_sha256": digest(root),
                "research_sha256": digest(root.parent / SOURCE_ARTIFACTS[1]),
                "execution_id": source.name, "execution_sha256": digest(source / SOURCE_ARTIFACTS[0]),
                "produced_at": now.isoformat(), "expires_at": expires.isoformat(),
                "entries": entries, "exits": exits, "marks": marks,
            })
        except (OSError, ValueError, TypeError, KeyError, AttributeError, ArithmeticError, sqlite3.Error):
            return {"blockers": ["VTS_CANDIDATE_SOURCE_UNVERIFIED"]}
    return {"source_run_id": source.name, "entries_queued": sorted(entries),
            "risk_exit_candidates": len(exits), "blockers": []}


def authorize(archive, lane, market, source, candidate, terms, quote, account, current, now, session):
    """Constrain a native candidate and native quantity; never create an intent."""
    policy = load_autotrader_policy(lane)
    if not active(lane, policy) or not _regular(session, now):
        raise ValueError("Five-minute lane halted or market closed")
    receipt = _receipt(lane, market)
    produced, expires = instant(receipt.get("produced_at")), instant(receipt.get("expires_at"))
    root, finished = baseline(archive, source, market, now)
    if (produced is None or expires is None or not finished <= produced <= now < expires
            or expires != finished + timedelta(hours=policy.session_entry_ttl_hours)
            or receipt.get("baseline_id") != root.parent.name or receipt.get("baseline_sha256") != digest(root)
            or receipt.get("research_sha256") != digest(root.parent / SOURCE_ARTIFACTS[1])):
        raise ValueError("No current five-minute candidate for the selected full lineage")
    observed, received = instant(quote.get("observed_at")), instant(quote.get("ingested_at"))
    opened = instant(session["session_open"])
    if (observed is None or received is None or not opened <= observed <= received <= now < observed + timedelta(seconds=120)
            or quote.get("provider") not in KIS_QUOTE_PROVIDERS
            or quote.get("currency") != MARKET_CURRENCIES[market] or quote.get("session") != "regular"
            or quote.get("ticker") != terms["ticker"] or quote.get("execution_ready") is not True):
        raise ValueError("Five-minute gate requires a current native quote")
    ticker, side = candidate["ticker"], terms["side"]
    if side == "BUY":
        entry = receipt["entries"][ticker]
        research, regime = _research(root)
        price = _reference(research[ticker], market, finished)
        held = [position for position in account["positions"] if position["quantity"] > 0]
        securities = {key[:6] if market == "KR" else key: value for key, value in research.items()}
        sector = research[ticker].get("sector")
        gate = evaluate_prism_buy_gate(research[ticker], current_price=terms["limit_price"], regime=regime,
            slots_used=len(held), max_slots=min(10, policy.max_slots), max_same_sector=policy.max_same_sector,
            same_sector_count=sum(securities.get(position["ticker"], {}).get("sector") == sector for position in held),
            policy=policy)
        if (price is None or price != entry["reference_price"] or not gate.allowed
                or terms["limit_price"] > price * (1 + policy.buy_max_premium_pct / 100)):
            raise ValueError("Five-minute entry is outside its price or slot bounds")
    else:
        exit_hint = receipt["exits"][ticker]
        evidence = {key: exit_hint[key] for key in ("entry", "stop", "target", "peak", "runner", "days", "risk")}
        hint_clock = instant(exit_hint["observation"])
        lot = next((order for order in reversed(current["orders"]) if order["ticker"] == ticker
                    and order["side"] == "BUY" and order["source"] == "KIS_DEMO_BROKER_REPORT"
                    and order["filled_quantity"] == 1), {})
        matches_lot = lot.get("id") == exit_hint["lot"] and lot.get("average_fill_price") == evidence["entry"]
        if (receipt["execution_id"] != source.name or receipt["execution_sha256"] != digest(source / SOURCE_ARTIFACTS[0])
                or hint_clock is None or not opened <= hint_clock <= now < hint_clock + timedelta(seconds=120)
                or current["owned"].get(ticker) != 1 or not matches_lot
                or not risk_exit_reason(price=quote["last_price"], policy=policy, **evidence)):
            raise ValueError("Five-minute exit lacks current native holdings or risk evidence")
    return {"schema": SCHEMA, "baseline_id": root.parent.name, "produced_at": produced.isoformat(), "side": side}
