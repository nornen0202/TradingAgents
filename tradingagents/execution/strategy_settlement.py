"""Explicit, reviewed settlement imports for existing normal KIS demo orders.

This module makes no HTTP request. An operator must independently verify the
source document and its execution-level cost coverage before importing it.
Account-day totals, rate schedules and cumulative order observations alone do
not meet this contract. Originals and corrections are append-only revisions.
"""
from __future__ import annotations

from decimal import Decimal
from collections.abc import Mapping as ReadOnlyMapping
import hashlib
import json
from typing import Mapping

from tradingagents.atomic_io import interprocess_file_lock
from .kis_demo import DemoError, KisDemoClient, reconciliation_issue_state
from .kis_demo_us import KisDemoUSClient
from .kis_paper import _clock, _integer, _number, _stable, _import_cashflow_checkpoints


SCHEMA = "tradingagents.strategy-settlement/v1"
PROOF_SCHEMA = "tradingagents.strategy-settlement-evaluation/v1"
COMPONENTS = ("commission", "tax", "fx_cost", "other_cost")
_VALIDATION_TOKEN = object()


class _ValidatedSettlementEvidence(ReadOnlyMapping):
    """In-process ledger capability, never a deserializable status assertion.

    Copies returned to callers are detached. A proof is bound to one exact
    cutoff, market and set of cumulative order observations; it cannot be reused
    after changing those inputs or serialized and promoted back into authority.
    """
    __slots__ = ("_encoded", "_orders_hash", "_as_of", "_market", "_token")

    def __init__(self, payload, orders, market, as_of, *, token):
        if token is not _VALIDATION_TOKEN:
            raise TypeError("Ledger validation required")
        object.__setattr__(self, "_encoded", _canonical(payload))
        object.__setattr__(self, "_orders_hash", _digest(_canonical(orders).encode()))
        object.__setattr__(self, "_as_of", _clock(as_of))
        object.__setattr__(self, "_market", market)
        object.__setattr__(self, "_token", token)

    def __setattr__(self, key, value):
        raise AttributeError("Validated settlement evidence is immutable")

    def __getitem__(self, key):
        return json.loads(self._encoded)[key]

    def __iter__(self):
        return iter(json.loads(self._encoded))

    def __len__(self):
        return len(json.loads(self._encoded))


def _validated(payload, orders, market, as_of):
    return _ValidatedSettlementEvidence(payload, orders, market, as_of, token=_VALIDATION_TOKEN)


def _canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def _digest(raw):
    return hashlib.sha256(raw).hexdigest()


def _initialize(db):
    db.execute("""CREATE TABLE IF NOT EXISTS strategy_settlement_sources(
        sha256 TEXT PRIMARY KEY, content BLOB NOT NULL)""")
    db.execute("""CREATE TABLE IF NOT EXISTS strategy_settlements(
        revision_id TEXT PRIMARY KEY, intent_id TEXT NOT NULL,
        previous_revision_id TEXT, ingested_at TEXT NOT NULL, document_json TEXT NOT NULL)""")
    db.execute("""CREATE TABLE IF NOT EXISTS strategy_settlement_bindings(
        revision_id TEXT PRIMARY KEY, binding_json TEXT NOT NULL)""")
    for table in ("strategy_settlement_sources", "strategy_settlements", "strategy_settlement_bindings"):
        for operation in ("UPDATE", "DELETE"):
            db.execute(f"""CREATE TRIGGER IF NOT EXISTS {table}_no_{operation.lower()}
                BEFORE {operation} ON {table}
                BEGIN SELECT RAISE(ABORT,'Settlement evidence is immutable'); END""")


def _binding(db, identity, as_of):
    def one(table, columns):
        cursor = db.execute(f"SELECT {columns} FROM {table} WHERE id=?", (identity,))
        rows = cursor.fetchall()
        if len(rows) != 1:
            raise DemoError("Settlement original evidence is missing or ambiguous")
        return list(rows[0])
    static = {"owner": [list(r) for r in db.execute("SELECT scope FROM owner ORDER BY scope")],
              "strategy": one("strategy_attempts", "id,ticker,run_id,prepared_at,terms"),
              "paper_intent": one("paper_intents", "id,terms,signal_id,created_at"),
              "intent": one("intents", "id,endpoint,tr_id,body"),
              "request": one("requests", "id,fingerprint,status,response,created_at"),
              "strategy_source": [list(r) for r in db.execute("SELECT id,evidence FROM strategy_source_evidence WHERE id=?", (identity,))]}
    observations = []
    for row in db.execute("SELECT observed_at,evidence FROM paper_observations WHERE id=?", (identity,)):
        try:
            observed = _clock(row[0])
            if observed > as_of:
                continue
            raw = json.loads(row[1])
            if _clock(raw.get("ingested_at")) <= as_of:
                observations.append(list(row))
        except (DemoError, ValueError, TypeError):
            continue
    reconciliations = []
    for row in db.execute("SELECT observed_at,evidence FROM reconciliations WHERE id=?", (identity,)):
        try:
            if _clock(row[0]) <= as_of:
                reconciliations.append(list(row))
        except DemoError:
            continue
    issue_history = []
    if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='reconciliation_issue_history'").fetchone():
        for sequence, digest, ingested in db.execute("SELECT sequence,proof_sha256,ingested_at FROM reconciliation_issue_history WHERE intent_id=?", (identity,)):
            if _clock(ingested) <= as_of:
                issue_history.append([sequence, digest])
    return {"static": static, "observations": sorted(observations), "reconciliations": sorted(reconciliations),
            "issue_history": sorted(issue_history)}


def _verify_binding(db, record, as_of):
    saved = db.execute("SELECT binding_json FROM strategy_settlement_bindings WHERE revision_id=?", (record["revision_id"],)).fetchone()
    if saved is None:
        raise DemoError("Settlement import lacks an immutable original-order binding")
    pinned = json.loads(saved[0])
    current = _binding(db, record["document"]["intent_id"], as_of)
    if pinned.get("static") != current["static"]:
        raise DemoError("Settlement original ACK/body/TR/strategy proof changed")
    for key in ("observations", "reconciliations", "issue_history"):
        if key not in pinned or not {_canonical(r) for r in pinned[key]} <= {_canonical(r) for r in current[key]}:
            raise DemoError("Settlement cumulative cash-flow proof changed")


def _validate_document(document, now):
    if not isinstance(document, Mapping) or document.get("schema") != SCHEMA:
        raise DemoError("Explicit strategy settlement document required")
    for key in ("revision_id", "intent_id", "broker_order_id", "account_scope"):
        _stable(document.get(key))
    if "previous_revision_id" not in document:
        raise DemoError("Explicit settlement predecessor or null required")
    if document.get("previous_revision_id") is not None:
        _stable(document["previous_revision_id"])
    if (document.get("environment") != "demo" or document.get("market") not in {"KR", "US"}
            or document.get("currency") != ("KRW" if document["market"] == "KR" else "USD")
            or document.get("attribution") != "ORDER_EXECUTION"
            or document.get("cost_coverage") != "ALL_COMPONENTS_IN_TRADING_CURRENCY"):
        raise DemoError("Same-order demo costs in the trading currency required")
    source, review = document.get("source"), document.get("review")
    if (not isinstance(source, Mapping) or not isinstance(review, Mapping)
            or source.get("kind") != "KIS_DEMO_SETTLEMENT_DOCUMENT"
            or review.get("approved") is not True):
        raise DemoError("Independently reviewed broker document required")
    _stable(review.get("reviewer_id"))
    if not isinstance(source.get("sha256"), str) or len(source["sha256"]) != 64:
        raise DemoError("Original source SHA256 required")
    observed, available = _clock(source.get("observed_at")), _clock(source.get("available_at"))
    reviewed = _clock(review.get("reviewed_at"))
    corrections = _clock(document.get("corrections_checked_through"))
    # Broker document availability precedes local collection. Do not replace
    # either clock with the later operator review or import time.
    if not available <= observed <= reviewed <= now or not observed <= corrections <= reviewed:
        raise DemoError("Future or invalid settlement source/review clocks")
    fills = document.get("fills")
    if not isinstance(fills, list) or not fills:
        raise DemoError("Incremental broker executions required")
    identities = set()
    for fill in fills:
        if not isinstance(fill, Mapping):
            raise DemoError("Incremental broker execution required")
        identity = _stable(fill.get("fill_id"))
        if identity in identities:
            raise DemoError("Duplicate incremental execution")
        identities.add(identity)
        _integer(fill.get("quantity"), positive=True)
        _number(fill.get("price"), positive=True)
        for key in COMPONENTS:
            _number(fill.get(key))
        if fill.get("currency") != document["currency"]:
            raise DemoError("Missing or unconverted execution cost currency")
        executed, confirmed, settled = (_clock(fill.get(key)) for key in ("executed_at", "confirmed_at", "settled_at"))
        if not executed <= confirmed <= settled <= available:
            raise DemoError("Execution confirmation and settlement must precede the document")
    return document


def _revision_chain(records):
    by_id, children = {}, {}
    for record in records:
        identity, previous = record["revision_id"], record["previous_revision_id"]
        if identity in by_id or previous in children:
            raise DemoError("Ambiguous settlement revision chain")
        by_id[identity], children[previous] = record, identity
    ordered, current = [], children.get(None)
    while current is not None and current not in {r["revision_id"] for r in ordered}:
        if current not in by_id:
            raise DemoError("Missing settlement predecessor")
        ordered.append(by_id[current])
        current = children.get(current)
    if len(ordered) != len(records) or current is not None:
        raise DemoError("Incomplete or cyclic settlement revision chain")
    for earlier, later in zip(ordered, ordered[1:]):
        if _clock(earlier["ingested_at"]) > _clock(later["ingested_at"]):
            raise DemoError("Settlement correction cannot backdate ingestion")
    return ordered


def _records(db, intent_id, *, as_of=None):
    result = []
    for row in db.execute("SELECT revision_id,previous_revision_id,ingested_at,document_json FROM strategy_settlements WHERE intent_id=?", (intent_id,)):
        if as_of is not None:
            try:
                if _clock(row[2]) > as_of:
                    continue
            except DemoError:
                continue
        result.append({"revision_id": row[0], "previous_revision_id": row[1], "ingested_at": row[2], "document": json.loads(row[3])})
    return result


def import_strategy_settlement(broker, document, *, source_bytes):
    """Append a reviewed whole-order execution/cost snapshot, never an order.

    The API intentionally has no automatic collector or guessed KIS cost TR.
    The reviewer is responsible for authenticity, complete pagination/coverage
    and explicit zeros. This function independently checks original bytes,
    same-account acknowledged order, strategy ownership, cumulative cash-flow
    checkpoints, timestamps and the complete correction chain.
    """
    market = "KR" if type(broker.client) is KisDemoClient else "US" if type(broker.client) is KisDemoUSClient else None
    now = _clock(broker.clock())
    _validate_document(document, now)
    if (market != document["market"] or document["account_scope"] != broker.client.credentials.scope()
            or not isinstance(source_bytes, bytes) or not 0 < len(source_bytes) <= 10 * 1024 * 1024
            or _digest(source_bytes) != document["source"]["sha256"]):
        raise DemoError("Same-scope original settlement source bytes required")
    encoded = _canonical(document)
    with interprocess_file_lock(broker.path.with_suffix(broker.path.suffix + ".paper.lock")):
        db = broker.db
        if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='strategy_attempts'").fetchone():
            raise DemoError("Original normal-strategy owned intent required")
        row = db.execute("SELECT * FROM paper_intents WHERE id=?", (document["intent_id"],)).fetchone()
        state = db.execute("SELECT * FROM order_state WHERE id=?", (document["intent_id"],)).fetchone()
        strategy = db.execute("SELECT ticker,terms,prepared_at FROM strategy_attempts WHERE id=?", (document["intent_id"],)).fetchone()
        if not row or not state or not strategy or json.loads(row["terms"]) != json.loads(strategy["terms"]):
            raise DemoError("Original normal-strategy owned intent required")
        terms = json.loads(row["terms"])
        fills = sorted(document["fills"], key=lambda f: (_clock(f["executed_at"]), f["fill_id"]))
        receipt = {"executed_at": fills[0]["executed_at"], "broker_order_id": document["broker_order_id"], "source": "kis_vts"}
        checkpoints = _import_cashflow_checkpoints(broker, row, state, receipt, now, market=market)
        quantity, amount = 0, Decimal(0)
        for fill in fills:
            executed = _clock(fill["executed_at"])
            price = Decimal(str(fill["price"]))
            if (executed < _clock(strategy["prepared_at"])
                    or terms["side"] == "BUY" and price > Decimal(str(terms["limit_price"]))
                    or terms["side"] == "SELL" and price < Decimal(str(terms["limit_price"]))):
                raise DemoError("Settlement execution conflicts with immutable order")
            quantity += fill["quantity"]
            amount += price * fill["quantity"]
            if not any(executed <= observed and ingested <= _clock(document["review"]["reviewed_at"])
                       and qty == quantity and cash == amount for observed, ingested, qty, cash, _, _ in checkpoints):
                raise DemoError("Settlement execution lacks matching cumulative cash-flow checkpoint")
        if quantity != state["filled"] or quantity != checkpoints[-1][2] or amount != checkpoints[-1][3]:
            raise DemoError("Settlement snapshot must cover the current complete cumulative fill")
        for observed, ingested, qty, cash, _, _ in checkpoints:
            if cash is None:
                continue
            known_executions = [f for f in fills if _clock(f["confirmed_at"]) <= observed]
            if (sum(f["quantity"] for f in known_executions) != qty
                    or sum((Decimal(str(f["price"])) * f["quantity"] for f in known_executions), Decimal(0)) != cash):
                raise DemoError("Incremental settlement conflicts with a broker-observed partial fill")
        db.execute("BEGIN IMMEDIATE")
        try:
            _initialize(db)
            broker.journal.ensure_issue_baseline(document["intent_id"])
            imported_at = _clock(broker.clock())
            if imported_at < now:
                raise DemoError("Settlement import clock regressed")
            records = _revision_chain(_records(db, document["intent_id"]))
            duplicate = next((r for r in records if r["revision_id"] == document["revision_id"]), None)
            if duplicate:
                if _canonical(duplicate["document"]) != encoded:
                    raise DemoError("Settlement revision ID reused with different evidence")
                db.execute("ROLLBACK")
                return False
            previous = records[-1] if records else None
            if document["previous_revision_id"] != (previous["revision_id"] if previous else None):
                raise DemoError("Settlement correction must name the latest predecessor")
            if previous:
                old = {fill["fill_id"]: fill for fill in previous["document"]["fills"]}
                new = {fill["fill_id"]: fill for fill in document["fills"]}
                economic = ("fill_id", "quantity", "price", "executed_at", "confirmed_at", "currency")
                if any(identity not in new or any(fill[k] != new[identity][k] for k in economic) for identity, fill in old.items()):
                    raise DemoError("Gross execution correction requires broker reconciliation first")
                if _clock(document["source"]["observed_at"]) < _clock(previous["document"]["source"]["observed_at"]):
                    raise DemoError("Settlement correction cannot backdate source observation")
            # A broker execution ID cannot migrate between normal strategy orders.
            for prior in db.execute("SELECT intent_id,document_json FROM strategy_settlements WHERE intent_id<>?", (document["intent_id"],)):
                other = json.loads(prior[1])
                if {f["fill_id"] for f in other["fills"]} & {f["fill_id"] for f in fills}:
                    raise DemoError("Broker execution already attributed to another order")
            db.execute("INSERT OR IGNORE INTO strategy_settlement_sources VALUES (?,?)", (document["source"]["sha256"], source_bytes))
            db.execute("INSERT INTO strategy_settlements VALUES (?,?,?,?,?)", (document["revision_id"], document["intent_id"],
                       document["previous_revision_id"], imported_at.isoformat(), encoded))
            db.execute("INSERT INTO strategy_settlement_bindings VALUES (?,?)",
                       (document["revision_id"], _canonical(_binding(db, document["intent_id"], imported_at))))
            db.execute("COMMIT")
            return True
        except Exception:
            db.execute("ROLLBACK")
            raise


def strategy_settlement_evidence(db, orders, *, market, as_of, historical=False):
    """Read only visible same-owner snapshots matching the current cash flows.

    An older revision remains visible before a later correction was ingested.
    No source/quantity/cost is guessed when evidence is absent or incomplete.
    """
    now = _clock(as_of)
    if type(historical) is not bool:
        raise ValueError("Explicit historical settlement mode required")
    result = {"schema": PROOF_SCHEMA, "status": "UNVERIFIED", "orders": []}
    if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='strategy_settlements'").fetchone():
        return _validated(result, orders, market, now)
    if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='strategy_settlement_bindings'").fetchone():
        return _validated({**result, "status": "INVALID"}, orders, market, now)
    owners = db.execute("SELECT scope FROM owner").fetchall()
    if len(owners) != 1:
        return _validated({**result, "status": "INVALID"}, orders, market, now)
    required = [o for o in orders if o["filled_quantity"]]
    try:
        for order in required:
            if not historical and db.execute("SELECT 1 FROM reconciliation_issues WHERE id=?", (order["id"],)).fetchone():
                raise DemoError("Settlement order has an unresolved broker reconciliation")
            if reconciliation_issue_state(db, order["id"], as_of=now)["status"] != "CLEAR":
                raise DemoError("Settlement reconciliation issue history is active or unverified")
            visible = []
            for record in _records(db, order["id"], as_of=now):
                document = record["document"]
                if _clock(record["ingested_at"]) > now:
                    continue
                _validate_document(document, now)
                if (document["revision_id"] != record["revision_id"] or document["previous_revision_id"] != record["previous_revision_id"]
                        or document["intent_id"] != order["id"] or document["account_scope"] != owners[0][0]
                        or document["market"] != market or _clock(document["review"]["reviewed_at"]) > _clock(record["ingested_at"])):
                    raise DemoError("Settlement row provenance conflicts")
                source = db.execute("SELECT content FROM strategy_settlement_sources WHERE sha256=?", (document["source"]["sha256"],)).fetchone()
                if source is None or _digest(source[0]) != document["source"]["sha256"]:
                    raise DemoError("Settlement original source hash mismatch")
                _verify_binding(db, record, now)
                visible.append(record)
            chain = _revision_chain(visible)
            if not chain:
                continue
            document = chain[-1]["document"]
            fills = document["fills"]
            quantity = sum(f["quantity"] for f in fills)
            notional = sum((Decimal(str(f["price"])) * f["quantity"] for f in fills), Decimal(0))
            if quantity != order["filled_quantity"] or order.get("fill_notional") is None or notional != Decimal(str(order["fill_notional"])):
                continue
            request = db.execute("SELECT response,status FROM requests WHERE id=?", (order["id"],)).fetchone()
            if not request or request[1] != "ACKNOWLEDGED" or json.loads(request[0]).get("broker_order_id") != document["broker_order_id"]:
                raise DemoError("Settlement acknowledged order mismatch")
            result["orders"].append({"intent_id": order["id"], "ticker": order["ticker"], "side": order["side"],
                "revision_id": document["revision_id"], "fills": fills, "known_at": chain[-1]["ingested_at"]})
    except (DemoError, ValueError, TypeError, KeyError):
        return _validated({**result, "status": "INVALID", "orders": []}, orders, market, now)
    if required and len(result["orders"]) == len(required):
        result["status"] = "COMPLETE_REVIEWED_IMPORT"
    elif result["orders"]:
        result["status"] = "PARTIAL_REVIEWED_IMPORT"
    return _validated(result, orders, market, now)


def settled_cost_totals(evidence, orders, *, currency, as_of):
    """Compute FIFO from explicit executions only, in the trading currency."""
    empty = {"status": evidence.get("status", "UNVERIFIED") if isinstance(evidence, Mapping) else "UNVERIFIED",
             "actual_cost": None, "realized_net_pnl": None, "realized_actual_cost": None, "exact_fifo_available": False}
    if (type(evidence) is not _ValidatedSettlementEvidence or evidence._token is not _VALIDATION_TOKEN
            or evidence._orders_hash != _digest(_canonical(orders).encode()) or evidence._as_of != _clock(as_of)
            or evidence._market != ("KR" if currency == "KRW" else "US" if currency == "USD" else None)):
        return {**empty, "status": "INVALID" if evidence is not None else "UNVERIFIED"}
    if evidence.get("schema") != PROOF_SCHEMA or evidence.get("status") != "COMPLETE_REVIEWED_IMPORT":
        return empty
    original = {o["id"]: o for o in orders if o["filled_quantity"]}
    entries, seen = [], set()
    try:
        for proof in evidence["orders"]:
            identity = proof["intent_id"]
            if identity in seen or identity not in original or _clock(proof["known_at"]) > _clock(as_of):
                raise ValueError()
            seen.add(identity)
            order = original[identity]
            if proof["ticker"] != order["ticker"] or proof["side"] != order["side"]:
                raise ValueError()
            qty, amount = 0, Decimal(0)
            for fill in proof["fills"]:
                if fill["currency"] != currency:
                    raise ValueError()
                cost = sum((Decimal(str(_number(fill[key]))) for key in COMPONENTS), Decimal(0))
                quantity = _integer(fill["quantity"], positive=True)
                price = Decimal(str(_number(fill["price"], positive=True)))
                executed = _clock(fill["executed_at"])
                if not _clock(order["prepared_at"]) <= executed <= _clock(fill["confirmed_at"]) <= _clock(fill["settled_at"]) <= _clock(proof["known_at"]):
                    raise ValueError()
                qty += quantity
                amount += quantity * price
                entries.append((executed, fill["fill_id"], identity, order, quantity, price, cost))
            if qty != order["filled_quantity"] or amount != Decimal(str(order["fill_notional"])):
                raise ValueError()
        if seen != set(original) or not seen or len({e[1] for e in entries}) != len(entries):
            raise ValueError()
        observed_cost = _number(float(sum((entry[6] for entry in entries), Decimal(0))))
        clocks = [(entry[0], entry[3]["ticker"]) for entry in entries]
        if len(clocks) != len(set(clocks)):
            # Equal timestamp precision does not establish a broker execution
            # sequence. Do not invent FIFO from lexical execution IDs.
            return {"status": "COMPLETE_REVIEWED_IMPORT", "actual_cost": observed_cost,
                    "realized_net_pnl": None, "realized_actual_cost": None, "exact_fifo_available": False}
        lots, total, realized_cost, realized = {}, Decimal(0), Decimal(0), Decimal(0)
        sold = False
        for _, _, _, order, quantity, price, cost in sorted(entries, key=lambda e: e[:3]):
            total += cost
            symbol_lots = lots.setdefault(order["ticker"], [])
            if order["side"] == "BUY":
                symbol_lots.append([quantity, price, cost / quantity])
                continue
            sold = True
            remaining = quantity
            while remaining:
                if not symbol_lots:
                    raise ValueError()
                entry = symbol_lots[0]
                matched = min(entry[0], remaining)
                matched_cost = matched * (entry[2] + cost / quantity)
                realized_cost += matched_cost
                realized += matched * (price - entry[1]) - matched_cost
                remaining -= matched
                entry[0] -= matched
                if not entry[0]:
                    symbol_lots.pop(0)
        return {"status": "COMPLETE_REVIEWED_IMPORT", "actual_cost": float(total),
                "realized_net_pnl": float(realized) if sold else None,
                "realized_actual_cost": float(realized_cost) if sold else None, "exact_fifo_available": True}
    except (DemoError, ValueError, TypeError, KeyError):
        return {**empty, "status": "INVALID"}
