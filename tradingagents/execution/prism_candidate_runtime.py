"""Private five-minute hints consumed only after ordinary VTS admission."""
from contextlib import closing
from collections import Counter
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
REFERENCE_SOURCES = {"KR": {"kis.domestic_time_itemchartprice", "kis.FHKST01010100.stck_prpr"},
                     "US": {"kis.overseas_time_itemchartprice"}}


def active(lane, policy):
    return observes(policy) and policy.kill_switch is False and not (lane / "HALT").exists()


def observes(policy):
    return policy.mode == "kis_vts" and policy.enabled is True and policy.live_orders_confirmed is False


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


def _reference(item, market, finished, source):
    value = (item.get("data_health") or {}).get("price_reference")
    reference, _ = native_reference(value, market, finished.isoformat())
    instrument = item["instrument"]
    zone = ZoneInfo(MARKET_ZONES[market])
    if (reference and reference.basis == "unadjusted" and reference.source in REFERENCE_SOURCES[market]
            and instrument.get("country") == market and instrument.get("currency") == reference.currency
            and instant(reference.observed_at).astimezone(zone).date() == finished.astimezone(zone).date()):
        ticker = instrument["canonical_ticker"]
        try:
            parent = (source / "tickers").resolve()
            path = (parent / ticker / "execution_update.json").resolve()
            if path.parent.parent != parent:
                return None
            update = _read(path, {})
            observed = instant(update.get("market_data_asof"))
            available = instant(reference.observed_at)
            if (update.get("ticker") == ticker and update.get("price_reference") == value
                    and observed is not None and observed <= available <= finished):
                return reference
        except (OSError, TypeError, ValueError):
            pass
    return None


def _entries(research, regime, owned, policy, market, finished, now, source):
    from .demo_strategy_plan import HARD_BUY_GATES

    held = {ticker for ticker, qty in owned.items() if qty > 0}
    entries = {}
    reasons = Counter()
    for ticker, item in research.items():
        if ticker in held:
            reasons["STRATEGY_POSITION_ALREADY_OPEN"] += 1
            continue
        health = item.get("data_health") or {}
        if (item.get("review_required") is True or health.get("reanalysis_required") is True
                or set(item.get("gate_reasons") or []) & HARD_BUY_GATES or (item.get("buy_matrix") or {}).get("fail_reasons")):
            reasons["ENTRY_RESEARCH_REVIEW_REQUIRED"] += 1
            continue
        reference = _reference(item, market, finished, source)
        price = reference.price if reference else None
        structured = item.get("structured_decision") or {}
        trigger = structured.get("conditional_entry_action")
        trigger_expiry = instant(structured.get("conditional_entry_valid_until"))
        deferred = (price is None and trigger in {"STARTER", "ADD"} and trigger_expiry is not None
                    and now < trigger_expiry and item.get("suggested_action_if_triggered") == f"{trigger}_IF_TRIGGERED")
        sector = item.get("sector")
        gate = evaluate_prism_buy_gate(item, current_price=price, regime=regime, slots_used=len(held),
            max_slots=min(10, policy.max_slots), same_sector_count=sum(research.get(it, {}).get("sector") == sector for it in held),
            max_same_sector=policy.max_same_sector, policy=policy, defer_price=deferred)
        if gate.allowed:
            entries[ticker] = {"reference_price": price, "score": gate.effective_score,
                               "slot_fraction": gate.slot_fraction if reference else None,
                               "requires_native_price": deferred}
        else:
            reasons[gate.reasons[0].split(":", 1)[0]] += 1
    return entries, dict(reasons)


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


def _execution_rows(source, market, now):
    bundle = _read(source / SOURCE_ARTIFACTS[0])
    generated = instant(bundle["generated_at"])
    finished = instant(_read(source / "run.json")["finished_at"])
    if bundle["market"].upper() != market or generated is None or finished is None or not generated <= finished <= now:
        raise ValueError("Unverified five-minute quote bundle")
    quotes = {row["ticker"]: row for row in bundle["strategy_table"]}
    if len(quotes) != len(bundle["strategy_table"]):
        raise ValueError("Duplicate five-minute quote row")
    return quotes, generated


def _exits(quotes, generated, market, now, session, research, owned, orders, previous, policy):
    if not _regular(session, now):
        return {}, previous
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


def _forward_snapshot(lane, market, source, identity, now, session, quotes, entries, exits):
    """Persist observations without a simulated fill, position, or performance entry."""
    observed = {}
    if _regular(session, now):
        opened = instant(session["session_open"])
        for ticker in sorted(entries.keys() | exits.keys()):
            row = quotes.get(ticker, {})
            price = _exit_price(row, opened, now)
            if price is not None:
                observed[ticker] = {"price": price, "currency": MARKET_CURRENCIES[market],
                                    "event_at": row["market_data_asof"],
                                    "decision_now": (row.get("raw_codes") or {}).get("decision_now")}
    path = lane / "forward-observations" / market.lower() / f"{identity}.json"
    if not path.is_file():
        atomic_write_json(path, {"schema": "tradingagents.prism-forward-observation/v1", "mode": "observe_only",
                                 "market": market, "source_run_id": source.name, "observed_at": now.isoformat(),
                                 "entry_candidates": len(entries), "risk_exit_candidates": len(exits),
                                 "observations": observed, "broker_orders_sent": 0})
    return len(observed)


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
            if not observes(policy) or session.get("source") != "exchange_calendars" or session.get("phase") in {None, "unknown"}:
                raise ValueError("Candidate lane or calendar unverified")
            source = _latest_source(archive, market.lower(), now, required_artifacts=SOURCE_ARTIFACTS)
            if source is None:
                raise ValueError("No completed execution source")
            root, finished = baseline(archive, source, market, now)
            entry_expires = finished + timedelta(hours=policy.session_entry_ttl_hours)
            research, regime = _research(root)
            owned, orders = _journal(lane, market, now)
            entries, reasons = (_entries(research, regime, owned, policy, market, finished, now, root.parent) if now < entry_expires
                                else ({}, {"ENTRY_RESEARCH_EXPIRED": len(research)}))
            quotes, generated = _execution_rows(source, market, now)
            exits, marks = _exits(quotes, generated, market, now, session, research, owned, orders,
                                  _receipt(lane, market).get("marks", {}), policy)
            stopped = not active(lane, policy)
            execution_identity = digest(source / SOURCE_ARTIFACTS[0])
            observed = _forward_snapshot(lane, market, source, execution_identity, now, session, quotes, entries, exits)
            atomic_write_json(path, {
                "schema": SCHEMA, "mode": "kis_vts", "market": market, "real_orders_enabled": False,
                "transmission_halted": stopped,
                "baseline_id": root.parent.name, "baseline_sha256": digest(root),
                "research_sha256": digest(root.parent / SOURCE_ARTIFACTS[1]),
                "execution_id": source.name, "execution_sha256": execution_identity,
                "produced_at": now.isoformat(), "entry_expires_at": entry_expires.isoformat(),
                "entries": entries, "exits": exits, "marks": marks, "entry_first_exclusions": reasons,
            })
        except (OSError, ValueError, TypeError, KeyError, AttributeError, ArithmeticError, sqlite3.Error):
            return {"blockers": ["VTS_CANDIDATE_SOURCE_UNVERIFIED"]}
    return {"source_run_id": source.name, "entries_queued": sorted(entries),
            "entry_research_expired": now >= entry_expires, "risk_exit_candidates": len(exits),
            "evaluated_research_rows": len(research), "entry_first_exclusions": reasons,
            "entries_waiting_for_native_price": sum(row["requires_native_price"] for row in entries.values()),
            "forward_observations": observed, "broker_orders_sent": 0,
            "transmission_halted": stopped, "blockers": ["KILL_SWITCH_ACTIVE"] if stopped else []}


def authorize(archive, lane, market, source, candidate, terms, quote, account, current, now, session):
    """Constrain a native candidate and native quantity; never create an intent."""
    policy = load_autotrader_policy(lane)
    if not active(lane, policy) or not _regular(session, now):
        raise ValueError("Five-minute lane halted or market closed")
    receipt = _receipt(lane, market)
    produced = instant(receipt.get("produced_at"))
    root, finished = baseline(archive, source, market, now)
    if (produced is None or not finished <= produced <= now
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
    deadline = observed + timedelta(seconds=120)
    if side == "BUY":
        expires = instant(receipt.get("entry_expires_at"))
        if (expires is None or expires != finished + timedelta(hours=policy.session_entry_ttl_hours)
                or not produced <= now < expires):
            raise ValueError("Five-minute entry research has expired")
        deadline = min(deadline, expires)
        entry = receipt["entries"][ticker]
        research, regime = _research(root)
        reference = _reference(research[ticker], market, finished, root.parent)
        if entry.get("requires_native_price") is True and reference is None and entry.get("reference_price") is None:
            current_research, _ = _research(source / "run.json")
            reference = _reference(current_research[ticker], market, instant(_read(source / "run.json")["finished_at"]), source)
            reference_at = instant(reference.observed_at) if reference else None
            if reference_at is None or not opened <= reference_at <= now < reference_at + timedelta(seconds=120):
                raise ValueError("Five-minute entry requires a current native research reference")
            deadline = min(deadline, reference_at + timedelta(seconds=120))
        elif reference is None or reference.price != entry["reference_price"]:
            raise ValueError("Five-minute entry reference proof changed")
        held = [position for position in account["positions"] if position["quantity"] > 0]
        securities = {key[:6] if market == "KR" else key: value for key, value in research.items()}
        sector = research[ticker].get("sector")
        gate = evaluate_prism_buy_gate(research[ticker], current_price=terms["limit_price"], regime=regime,
            slots_used=len(held), max_slots=min(10, policy.max_slots), max_same_sector=policy.max_same_sector,
            same_sector_count=sum(securities.get(position["ticker"], {}).get("sector") == sector for position in held),
            policy=policy)
        if not gate.allowed or terms["limit_price"] > reference.price * (1 + policy.buy_max_premium_pct / 100):
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
                or not risk_exit_reason(price=quote["bid"], policy=policy, **evidence)):
            raise ValueError("Five-minute exit lacks current native holdings or risk evidence")
        deadline = min(deadline, hint_clock + timedelta(seconds=120))
    return {"schema": SCHEMA, "baseline_id": root.parent.name, "produced_at": produced.isoformat(),
            "valid_until": deadline.isoformat(), "side": side}
