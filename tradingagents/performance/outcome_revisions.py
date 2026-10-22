"""Point-in-time selection of append-only, whole-exit FIFO allocations."""
from __future__ import annotations

import hashlib
import json
import math

from .lifecycle import timestamp, validate_event


REVISION_KIND = "RETROSPECTIVE_ALLOCATION"
CLOCKS = ("occurred_at", "available_at", "confirmed_at", "settled_at", "ingested_at")
ALGORITHM = "FIFO_INCREMENTAL_FILL_COSTS/v1"


def known_at(event):
    return max(timestamp(event[key]) for key in CLOCKS if event.get(key) is not None)


def content_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def allocation_hash(reviews, input_event_ids):
    keys = ("entry_fill_id", "exit_fill_id", "closed_quantity", "net_profit", "total_cost", "currency", "mode")
    members = [{key: row[key] for key in keys} for row in reviews]
    return content_hash({"algorithm": ALGORITHM, "inputs": sorted(input_event_ids),
                         "members": sorted(members, key=lambda row: row["entry_fill_id"])})


def read_events(conn):
    columns = [row[1] for row in conn.execute("PRAGMA table_info(lifecycle_events)")]
    if not columns:
        return []
    result = []
    for row in conn.execute("SELECT * FROM lifecycle_events"):
        event = dict(zip(columns, row))
        try:
            event["payload"] = json.loads(event.pop("payload_json"))
        except (ValueError, TypeError):
            continue
        result.append(event)
    return result


def visible_events(events, analysis_as_of):
    """Exclude unknown/future clocks before revision selection or any statistics."""
    cutoff = timestamp(analysis_as_of)
    visible = {}
    for event in events:
        try:
            validate_event(event)
            if known_at(event) > cutoff:
                continue
        except (ValueError, TypeError, KeyError):
            continue
        previous = visible.get(event["event_id"])
        if previous is not None and previous != event:
            raise ValueError("Conflicting lifecycle evidence")
        visible[event["event_id"]] = event
    intents = {(e["mode"], e["intent_id"], e["signal_id"]) for e in visible.values() if e["kind"] == "INTENT"}
    return {key: e for key, e in visible.items() if e["kind"] != "FILL" or
            (e["mode"], e["intent_id"], e["signal_id"]) in intents}


def scope(event):
    payload = event["payload"]
    return event["mode"], payload.get("currency"), payload.get("ticker"), payload.get("exit_fill_id")


def event_order(event):
    return timestamp(event["occurred_at"]), 0 if event["kind"] == "ACCOUNT_SEED" else 1, event["event_id"]


def validate_opening_seeds(visible):
    """Each mode/currency ledger has at most one opening balance, before fills."""
    seeds, first_fills = {}, {}
    for event in visible.values():
        if event["kind"] not in {"ACCOUNT_SEED", "FILL"}:
            continue
        key = event["mode"], event["payload"].get("currency", "KRW")
        occurred = timestamp(event["occurred_at"])
        if event["kind"] == "ACCOUNT_SEED":
            if key in seeds:
                raise ValueError("Combine journals for one account only; duplicate account seed")
            seeds[key] = occurred
        else:
            first_fills[key] = min(first_fills.get(key, occurred), occurred)
    if any(key in first_fills and occurred > first_fills[key] for key, occurred in seeds.items()):
        raise ValueError("Opening account seed cannot follow fill occurrence")


def revision_heads(events, analysis_as_of):
    """Require one unbranched chain per exit; a future child cannot hide its parent."""
    visible = visible_events(events, analysis_as_of)
    groups = {}
    for event in visible.values():
        if event["kind"] == REVISION_KIND:
            groups.setdefault(scope(event), {})[event["event_id"]] = event
    heads = {}
    for key, revisions in groups.items():
        children = {}
        for identity, event in revisions.items():
            previous = event["payload"]["previous_revision_id"]
            if previous is not None and (previous not in revisions or known_at(revisions[previous]) > known_at(event)):
                raise ValueError("Allocation revision has an unavailable predecessor")
            if previous in children:
                raise ValueError("Allocation revision chain fork")
            children[previous] = identity
        current, visited = children.get(None), set()
        while current is not None and current not in visited:
            visited.add(current)
            head = revisions[current]
            current = children.get(current)
        if len(visited) != len(revisions) or current is not None:
            raise ValueError("Allocation revision chain is incomplete or cyclic")
        heads[key] = head
    return visible, heads


def _review_valid(review, visible):
    payload = review["payload"]
    entry, exit_event = (visible.get(payload.get(key)) for key in ("entry_fill_id", "exit_fill_id"))
    if not entry or not exit_event or entry["kind"] != "FILL" or exit_event["kind"] != "FILL":
        return False
    buy, sell = entry["payload"], exit_event["payload"]
    if (entry["mode"] != review["mode"] or exit_event["mode"] != review["mode"]
            or payload.get("mode") != review["mode"]
            or buy["side"] != "BUY" or sell["side"] != "SELL"
            or any(p.get("ticker") != payload.get("ticker") or p.get("currency") != payload.get("currency") for p in (buy, sell))
            or exit_event["signal_id"] != review["signal_id"]
            or timestamp(entry["occurred_at"]) > timestamp(exit_event["occurred_at"])
            or max(known_at(entry), known_at(exit_event)) > known_at(review)):
        return False
    quantity = payload.get("closed_quantity")
    if (type(quantity) not in (int, float) or not math.isfinite(quantity)
            or not 0 < quantity <= min(buy["quantity"], sell["quantity"])):
        return False
    costs = buy["cost"] * quantity / buy["quantity"] + sell["cost"] * quantity / sell["quantity"]
    profit = (sell["price"] - buy["price"]) * quantity - costs
    return all(type(payload.get(key)) in (int, float) and math.isfinite(payload[key])
               and math.isclose(payload[key], expected, rel_tol=1e-12, abs_tol=1e-9)
               for key, expected in (("total_cost", costs), ("net_profit", profit)))


def _validate_input_prefixes(visible, heads):
    """A later SELL must use the same economic evidence through earlier exits.

    Different calculation cutoffs are normal. A partial refresh is inconsistent
    only when its overlapping chronological input prefix differs, even if its
    lots do not violate either BUY or SELL quantity conservation.
    """
    groups = {}
    for key, head in heads.items():
        groups.setdefault(key[:3], []).append(head)
    for revisions in groups.values():
        revisions.sort(key=lambda e: event_order(visible[e["payload"]["exit_fill_id"]]))
        for earlier, later in zip(revisions, revisions[1:]):
            boundary = event_order(visible[earlier["payload"]["exit_fill_id"]])
            prefix = {identity for identity in later["payload"]["input_event_ids"] if event_order(visible[identity]) <= boundary}
            if prefix != set(earlier["payload"]["input_event_ids"]):
                raise ValueError("Active allocation input snapshots disagree")


def select_retrospectives(events, *, analysis_as_of):
    """Return only active economic reviews; caller may retain all events for audit."""
    visible, heads = revision_heads(events, analysis_as_of)
    validate_opening_seeds(visible)
    selected = []
    for key, head in heads.items():
        payload = head["payload"]
        exit_event = visible.get(key[-1])
        if (not exit_event or exit_event["kind"] != "FILL" or exit_event["payload"].get("side") != "SELL"
                or (exit_event["mode"], exit_event["payload"].get("currency"), exit_event["payload"].get("ticker")) != key[:3]
                or exit_event["signal_id"] != head["signal_id"] or known_at(exit_event) > known_at(head)):
            raise ValueError("Allocation exit evidence unavailable")
        for identity in payload["input_event_ids"]:
            event = visible.get(identity)
            if (not event or event["kind"] not in {"FILL", "ACCOUNT_SEED"}
                    or event["mode"] != key[0] or event["payload"].get("currency", "KRW") != key[1]
                    or event["kind"] == "FILL" and event["payload"].get("ticker") != key[2]
                    or known_at(event) > timestamp(payload["input_as_of"])):
                raise ValueError("Allocation input evidence unavailable")
        members = []
        for identity in payload["review_ids"]:
            event = visible.get(identity)
            if (not event or event["kind"] != "RETROSPECTIVE" or scope(event) != key
                    or event["payload"].get("allocation_revision_id") != head["event_id"]
                    or event["payload"].get("entry_fill_id") not in payload["input_event_ids"]
                    or known_at(event) > known_at(head) or not _review_valid(event, visible)):
                raise ValueError("Allocation membership evidence unavailable")
            members.append(event)
        if sum(e["payload"]["closed_quantity"] for e in members) > exit_event["payload"]["quantity"] + 1e-9:
            raise ValueError("Allocation exceeds exit quantity")
        if allocation_hash([e["payload"] for e in members], payload["input_event_ids"]) != payload["content_hash"]:
            raise ValueError("Allocation content hash mismatch")
        selected.extend(members)
    # Existing evidence remains valid before the first explicitly published
    # revision. A versioned member is never active without its committed revision.
    revised_groups = {key[:3] for key in heads}
    for event in visible.values():
        if (event["kind"] == "RETROSPECTIVE" and not event["payload"].get("allocation_revision_id")
                and scope(event) not in heads and _review_valid(event, visible)):
            if scope(event)[:3] in revised_groups:
                # Legacy rows have no complete input snapshot with which to
                # prove compatibility. Reconcile all exits in this group first.
                raise ValueError("Legacy allocation requires complete revision coverage")
            selected.append(event)
    totals, entry_totals = {}, {}
    for event in selected:
        key = scope(event)
        totals[key] = totals.get(key, 0) + event["payload"]["closed_quantity"]
        if totals[key] > visible[key[-1]]["payload"]["quantity"] + 1e-9:
            raise ValueError("Legacy retrospective allocation exceeds exit quantity")
        entry_id = event["payload"]["entry_fill_id"]
        entry_totals[entry_id] = entry_totals.get(entry_id, 0) + event["payload"]["closed_quantity"]
        if entry_totals[entry_id] > visible[entry_id]["payload"]["quantity"] + 1e-9:
            raise ValueError("Active retrospective allocation exceeds entry quantity")
    _validate_input_prefixes(visible, heads)
    return sorted(selected, key=lambda e: (known_at(e), e["event_id"]))
