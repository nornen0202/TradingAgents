"""Run domestic KIS paper strategy entry points against an offline transcript."""

from __future__ import annotations

from base64 import b64decode
from contextlib import contextmanager
from datetime import timedelta
import hashlib
import json
import math
import os
from pathlib import Path
import re
import secrets
from urllib.parse import urlsplit

from tradingagents.atomic_io import atomic_write_json, interprocess_file_lock
from tradingagents.calendar_access import get_exchange_calendar
from tradingagents.scheduled.market_calendar import (
    default_calendar_name, is_supplemental_market_holiday, market_session_state,
)

from . import demo_runtime
from .kis_demo import DemoCredentials, DemoError, KisDemoClient, RequestPacer
from .kis_strategy_limits import configured_limits, make_strategy_broker
from .paper_approval import PaperApproval, apply_telegram_paper_callback
from .promotion import PromotionLedger
from .strategy_settlement import import_strategy_settlement, strategy_settlement_evidence

SCHEMA = "tradingagents.isolated-kis-replay/v1"
ACTIONS = ("init", "tick", "callback", "inspect-orders", "settlement", "promotion-start", "promotion-record", "promotion-status")
_MARKER = ".paper-replay.json"
_ACTOR, _BOT, _CHAT = 101, 202, -303
_SCOPE = demo_runtime.FIXTURE_SCOPE
_ROUTES = {
    "inquire-balance": ("GET", "VTTC8434R"),
    "inquire-daily-ccld": ("GET", "VTTC0081R"),
    "inquire-psbl-order": ("GET", "VTTC8908R"),
    "order-cash": ("POST", "VTTC0012U", "VTTC0011U"),
    "order-rvsecncl": ("POST", "VTTC0013U"),
}


def _load(path):
    with path.open(encoding="utf-8-sig") as stream:
        payload = json.load(stream)
    if not isinstance(payload, dict) or payload.get("schema") != SCHEMA:
        raise ValueError("An isolated replay document is required")
    return payload


def _path(root, name):
    path = root / name
    if path.resolve() != path or (path.is_file() and path.stat().st_nlink != 1):
        raise ValueError("Replay paths cannot traverse a symlink, junction or hard link")
    return path


def _initialize(root):
    root.mkdir(mode=0o700, exist_ok=False)
    try:
        atomic_write_json(root / _MARKER, {"schema": SCHEMA, "secret": secrets.token_hex(32)})
        atomic_write_json(root / "state/enabled.json", {
            "mode": demo_runtime.MODE, "enabled": True, "real_orders_enabled": False,
            "evidence_scope": _SCOPE,
        })
    except OSError:
        raise ValueError("Unable to initialize new isolated replay directory") from None
    return {"status": "INITIALIZED", "approval_actor": _ACTOR, "approval_bot": _BOT, "approval_chat": _CHAT}


class _Response:
    headers = {}

    def __init__(self, body, status_code=200):
        self.body = body
        self.status_code = status_code

    def json(self):
        return self.body


class _OfflineSession:
    """Treat undocumented, foreign-host or unlisted requests as failures."""

    def __init__(self, document, clock, path):
        self.responses = document.get("responses", {})
        if not isinstance(self.responses, dict):
            raise ValueError("A replay transcript must map transaction codes to responses")
        self.clock, self.path = clock, path

    def request(self, method, url, *, allow_redirects, headers=None, **fields):
        target = urlsplit(url)
        if ((target.scheme, target.netloc) != ("https", "openapivts.koreainvestment.com:29443")
                or allow_redirects is not False or target.query or target.fragment):
            raise DemoError("Replay rejected non-VTS transport")
        if target.path == "/oauth2/tokenP" and method == "POST":
            return _Response({"access_token": "offline-fixture", "expires_in": 3600})
        prefix = "/uapi/domestic-stock/v1/trading/"
        route = _ROUTES.get(target.path.removeprefix(prefix)) if target.path.startswith(prefix) else None
        tr_id = (headers or {}).get("tr_id")
        if not route or method != route[0] or tr_id not in route[1:]:
            raise DemoError("Replay rejected undocumented method or transaction code")
        configured = self.responses.get(tr_id)
        if not isinstance(configured, dict):
            raise DemoError("Replay response absent")
        request_body = fields["json" if method == "POST" else "params"]
        expected = configured.get("expect", {})
        if not isinstance(expected, dict) or any(request_body.get(key) != value for key, value in expected.items()):
            raise DemoError("Replay transaction terms differ from the transcript")
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"as_of": self.clock().isoformat(), "method": method, "tr_id": tr_id}) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        if configured.get("response_lost") is True:
            raise TimeoutError("Offline response lost after acceptance")
        return _Response(configured.get("body"))

    def close(self):
        pass


def _index(record, now, *, final=False):
    if (not isinstance(record, dict) or record.get("source") != "KIS_KOSPI_FIXTURE"
            or record.get("symbol") != "0001" or record.get("market") != "KR" or record.get("kind") != (
                "final_regular_close" if final else "intraday_index")
            or type(record.get("price")) not in (int, float)
            or not math.isfinite(record["price"]) or record["price"] <= 0):
        raise ValueError("KOSPI observation is missing or unverified")
    event, observed = demo_runtime.at(record.get("event_at")), demo_runtime.at(record.get("observed_at"))
    if event > observed or observed > now:
        raise ValueError("KOSPI observation clock is unverified")
    if not final and now - event > timedelta(seconds=120):
        raise ValueError("KOSPI observation is stale")
    return event, observed


class _Replay:
    def __init__(self, root, document, marker):
        self.root, self.document, self.secret = root, document, marker["secret"]
        self.now = demo_runtime.at(document.get("as_of"))
        self.state, self.validation, self.archive = root / "state", root / "validation", root / "archive"
        self.limits = configured_limits(demo_runtime.read(self.state / "enabled.json", {}))
        self.tickers = tuple(document.get("tickers", ()))
        if any(not isinstance(ticker, str) or not re.fullmatch(r"[0-9]{6}\.(KS|KQ)", ticker) for ticker in self.tickers):
            raise ValueError("Domestic fixture ticker identities are required")
        self.credentials = DemoCredentials("offline-key-unused", "offline-secret-unused", "00000001", "01")
        self.scope = self.credentials.scope()
        self.requests = _OfflineSession(document, self.clock, root / "wire.jsonl")

    def clock(self):
        return self.now

    def approval(self):
        return PaperApproval(self.root / "approvals.sqlite", secret=bytes.fromhex(self.secret),
                             authorized=frozenset({str(_ACTOR)}), clock=self.clock)

    def gate(self, _, market, __):
        if market != "KR":
            raise ValueError("The isolated transcript declares only the domestic demo account")
        return self.scope

    @contextmanager
    def broker(self, market, path, clock, tickers, scope):
        if (market, scope) != ("KR", self.scope):
            raise ValueError("The isolated broker scope cannot change")
        client = KisDemoClient(self.credentials, session=self.requests, pacer=RequestPacer(interval=0), utcnow=clock)
        broker = make_strategy_broker(market, path, client, clock, tickers, self.limits.get(market))
        try:
            yield broker
        finally:
            broker.close()
            client.close()

    def quote(self, market, ticker, _):
        if market != "KR":
            raise ValueError("Foreign quote is outside the replay scope")
        quote = self.document.get("quotes", {}).get(ticker)
        if not isinstance(quote, dict):
            raise ValueError("Missing fixture quote")
        return quote

    def _approval_identity(self, candidate):
        source = demo_runtime._latest_source(self.archive, "kr", self.now)
        if source is None or source.name != candidate["run_id"] or not source.is_relative_to(self.archive):
            raise ValueError("Cannot bind approval to the original producer run")
        documents = ["run.json", "decision_bundle_v2.json", "portfolio-private/proposed_orders.json",
                     "portfolio-private/account_snapshot.json"]
        if candidate["side"] == "BUY":
            documents.append(f"tickers/{candidate['ticker']}/execution_contract.json")
        digest = hashlib.sha256()
        for name in documents:
            path = _path(self.archive, (source / name).relative_to(self.archive))
            with path.open("rb") as stream:
                digest.update(hashlib.file_digest(stream, "sha256").digest())
        if candidate not in demo_runtime.candidates(source, "KR", self.now, self.tickers):
            raise ValueError("Producer evidence changed during admission")
        source_sha = digest.hexdigest()
        return f"{candidate['id']}:{source_sha}", source_sha

    def tick(self):
        if not self.tickers:
            raise ValueError("No domestic tickers in replay")
        previews = {}

        def authorize(candidate, terms, signal, quote, scope, state):
            if (terms["side"] == "BUY" and not state["evaluation"]["settlement_known"]
                    and state["evaluation"]["sample"]["sell_filled_orders"]):
                raise ValueError("Previous strategy sale requires settlement evidence before a new purchase")
            index = self.document.get("index")
            try:
                event, observed = _index(index, self.now)
                index_evidence = {"status": "VERIFIED", "source": index["source"],
                                  "event_at": event.isoformat(), "observed_at": observed.isoformat()}
            except ValueError:
                if terms["side"] == "BUY":
                    raise
                index_evidence = {"status": "UNVERIFIED"}
            confirmation = signal.get("entry_confirmation")
            if terms["side"] == "BUY" and (not isinstance(confirmation, dict)
                    or confirmation.get("paper_candidate_ready") is not True
                    or confirmation.get("verified_next_open") is not True
                    or not any(row["stage"] == "close" and row["ready"] for row in confirmation["conditions"].values())):
                raise ValueError("A producer final-close and next-open proof is required for entries")
            with self.approval() as approval:
                identifier, source_sha = self._approval_identity(candidate)
                previews[candidate["id"]] = approval.propose({
                    "intent": identifier, "scope": scope, "mode": "isolated_paper",
                    "ticker": candidate["ticker"], "market": "KR", "currency": "KRW", "side": terms["side"],
                    "quantity": terms["quantity"], "quantity_step": 1,
                    "limit": terms["limit_price"], "expires_at": signal["valid_until"],
                })
                admission = approval.consume(identifier, scope=scope, quote={
                    "ticker": candidate["ticker"], "market": "KR", "currency": quote["currency"],
                    "session_open": quote["session"] == "regular", "observed_at": quote["observed_at"],
                    "ask": quote.get("ask", quote["last_price"]), "bid": quote.get("bid", quote["last_price"]),
                })
            previews.pop(candidate["id"])
            return int(admission["quantity"]), {"scope": _SCOPE, "approval": "AUTHENTICATED",
                    "index": index_evidence, "confirmation": confirmation, "producer_evidence_sha256": source_sha}

        receipt = demo_runtime.tick(self.archive, self.state, self.validation, clock=self.clock,
                                    broker_factory=self.broker, quote_loader=self.quote, gate=self.gate,
                                    session_resolver=market_session_state,
                                    tickers={"KR": self.tickers, "US": ()}, authorize=authorize,
                                    evidence_scope=_SCOPE)
        return {"approval_previews": previews, "strategy": receipt["markets"]["KR"]}

    def callback(self):
        with self.approval() as approval:
            return apply_telegram_paper_callback(approval, self.document.get("update"),
                supplied_secret=self.document.get("supplied_secret"), webhook_secret=self.secret,
                bot_id=_BOT, allowed_chats=frozenset({_CHAT}))

    @contextmanager
    def journal(self):
        path = self.state / "kr-strategy.sqlite"
        if not path.is_file() or not self.tickers:
            raise ValueError("A completed replay tick and its original universe are required")
        with self.broker("KR", path, self.clock, self.tickers, self.scope) as broker:
            yield broker

    def settlements(self):
        with self.journal() as broker:
            imported = sum(import_strategy_settlement(broker, item["document"],
                           source_bytes=b64decode(item["source_base64"], validate=True))
                           for item in self.document["settlements"])
            state = demo_runtime.summary(broker.db, self.now, "KR")
        return {"imported": imported, "strategy": state}

    def inspect_orders(self):
        """Requery official rows without assigning an ambiguous order identity."""
        with self.journal() as broker:
            rows = broker.client.orders(self.document["trade_date"])
        return {"status": "REPLAY_ORDER_INQUIRY", "rows": len(rows), "broker_state_changed": False}

    def promotion(self, action):
        with PromotionLedger(self.root / "promotion.sqlite", clock=self.clock) as ledger:
            if action == "promotion-start":
                spec = self.document["policy"]
                if spec.get("market") != "KR" or spec.get("sample_kind") != "round_trip":
                    raise ValueError("The isolated replay supports domestic round trips")
                ledger.start(spec)
                return ledger.status(spec["version"])
            version = self.document["version"]
            status = ledger.status(version)
            if action == "promotion-status":
                return status
            ledger.record(version, self.document["session"], self._promotion_observation(status["policy"]))
            return ledger.status(version)

    def _promotion_observation(self, policy):
        prior, current = self.document["previous_index_close"], self.document["index_close"]
        previous_event, previous_observed = _index(prior, self.now, final=True)
        current_event, current_obs = _index(current, self.now, final=True)
        calendar = get_exchange_calendar(default_calendar_name("KR"))
        day = self.document["session"]
        previous = calendar.previous_session(day)
        while is_supplemental_market_holiday(market="KR", session_date=previous.date()):
            previous = calendar.previous_session(previous)
        opening, closing = calendar.session_open(day), calendar.session_close(day)
        if (previous_event != calendar.session_close(previous) or previous_observed > opening or current_event != closing
                or not closing <= current_obs <= self.now or policy["benchmark"] != "KOSPI_FIXTURE"):
            raise ValueError("Promotion requires the exact benchmark session closes")
        starting_nav = self.document["starting_nav"]
        if type(starting_nav) not in (int, float) or not math.isfinite(starting_nav) or starting_nav <= 0:
            raise ValueError("Explicit starting fixture NAV required")
        with self.journal() as broker:
            state = demo_runtime.summary(broker.db, self.now, "KR")
            evaluation, orders = state["evaluation"], state["orders"]
            settlement = strategy_settlement_evidence(broker.db, orders, market="KR", as_of=self.now.isoformat())
            mismatches = broker.db.execute("SELECT COUNT(*) FROM reconciliation_issues").fetchone()[0]
        if (len(orders) != 2 or any(order["status"] != "FILLED" for order in orders)
                or evaluation["sample"]["closed_inventory_episodes"] != 1 or not evaluation["settlement_known"]
                or not opening <= max(demo_runtime.at(order["known_at"]) for order in settlement["orders"]) <= self.now):
            raise ValueError("A verified pair of settled fills must become available in this session")
        ids = sorted(order["id"] for order in orders)
        sample = hashlib.sha256("\n".join(ids).encode()).hexdigest()
        benchmark_return = current["price"] / prior["price"] - 1
        return {"cost_version": policy["cost_version"], "benchmark": policy["benchmark"],
                "regime": "risk_on" if benchmark_return > 0 else "risk_off" if benchmark_return < 0 else "neutral",
                "net_return": evaluation["realized_net_pnl"] / starting_nav, "benchmark_net_return": benchmark_return,
                "samples": [sample], "order_ids": ids, "mismatches": mismatches, "monitored_seconds": 0,
                "kill_switch_drill_id": None, "source_id": f"fixture-settled-roundtrip:{sample}"}


def command(root: Path, action: str, fixture: Path | None = None) -> dict:
    root = root.absolute()
    if root.resolve() != root or action not in ACTIONS:
        raise ValueError("Select a dedicated replay directory and supported action")
    if action == "init":
        if fixture is not None:
            raise ValueError("Initialization does not accept a fixture")
        body = _initialize(root)
    else:
        if fixture is None:
            raise ValueError("Replay action requires an explicit fixture")
        marker = _load(_path(root, _MARKER))
        if not isinstance(marker.get("secret"), str) or not re.fullmatch("[0-9a-f]{64}", marker["secret"]):
            raise ValueError("Invalid replay workspace")
        with interprocess_file_lock(_path(root, "replay.lock"), timeout=0):
            for name in ("state/enabled.json", "state/strategy.lock", "state/kr-strategy.sqlite",
                         "state/kr-strategy.sqlite.paper.lock",
                         "state/kr-strategy.sqlite-journal", "state/kr-strategy.sqlite-wal", "state/kr-strategy.sqlite-shm",
                         "state/paper-v2", "state/kr-v2-evidence.json", "state/kr-v2-settlement.json", "state/kr-v2-benchmark.json",
                         "validation/campaign.lock", "archive/paper/kis-strategy-runtime.json", "wire.jsonl",
                         "approvals.sqlite", "approvals.sqlite-journal", "promotion.sqlite", "promotion.sqlite-journal",
                         "clock.json"):
                _path(root, name)
            runner = _Replay(root, _load(fixture), marker)
            clock_file = root / "clock.json"
            previous = demo_runtime.read(clock_file)
            if previous is not None and runner.now < demo_runtime.at(previous["as_of"]):
                raise ValueError("Replay clock cannot move backwards")
            if action in {"tick", "settlement"}:
                atomic_write_json(clock_file, {"as_of": runner.now.isoformat()})
            if action.startswith("promotion-"):
                body = runner.promotion(action)
            else:
                body = {"tick": runner.tick, "callback": runner.callback,
                        "inspect-orders": runner.inspect_orders, "settlement": runner.settlements}[action]()
            if action not in {"tick", "settlement"}:
                atomic_write_json(clock_file, {"as_of": runner.now.isoformat()})
    return {**body, "evidence_scope": _SCOPE, "network_requests_sent": 0, "real_orders_enabled": False}
