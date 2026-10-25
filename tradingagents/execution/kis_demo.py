"""KIS VTS-only transport and durable request journal. No real-account route.

Transport is separate from strategy/risk approval. Acknowledged is not filled.
Ambiguous writes are never retried, including after process restart.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import threading
import time
from zoneinfo import ZoneInfo

import requests

from tradingagents.dataflows.api_keys import get_api_key
from .paper import kis_demo_order_preview, stamp
from .demo_secrets import DEMO_KEYS, load_demo_settings

DEMO_HOST = "https://openapivts.koreainvestment.com:29443"
PREFIX = "/uapi/domestic-stock/v1/trading/"


def _settings():
    # Use one complete encrypted bundle, never mix it with older plaintext keys.
    return load_demo_settings() or {key: get_api_key(key) for key in DEMO_KEYS}


class DemoError(RuntimeError):
    """Sanitized error: never include broker bodies, URLs, account IDs or keys."""


class DemoNotSentError(DemoError):
    """Local validation/authentication failed before the order request was sent."""


def configuration_status():
    return {key: bool(value) for key, value in _settings().items()}


@dataclass(frozen=True)
class DemoCredentials:
    app_key: str = field(repr=False)
    app_secret: str = field(repr=False)
    account_no: str = field(repr=False)
    product_code: str = field(repr=False)

    def __post_init__(self):
        if (
            not self.app_key
            or not self.app_secret
            or not re.fullmatch(r"[0-9]{8}", self.account_no)
            or not re.fullmatch(r"[0-9]{2}", self.product_code)
        ):
            raise DemoError("Invalid or missing dedicated demo credentials")

    @classmethod
    def from_local_settings(cls):
        settings = _settings()
        values = [settings.get(key) for key in DEMO_KEYS]
        if not all(values):
            raise DemoError(
                "Dedicated KIS_DEMO settings required; real credentials are not a fallback"
            )
        return cls(*values)

    def scope(self):
        return hashlib.sha256(
            f"demo:{self.account_no}:{self.product_code}".encode()
        ).hexdigest()


class RequestPacer:
    """One process/app-key request spacing; no retries of reads or writes."""

    # Actual VTS balance pagination returned EGW00201 at 1.1s spacing; 2.2s
    # completed the same read sequence. Keep headroom without retrying writes.
    def __init__(self, *, interval=2.2, clock=time.monotonic, sleep=time.sleep):
        self.interval, self.clock, self.sleep = interval, clock, sleep
        self.last = None
        self.lock = threading.Lock()

    def wait(self):
        with self.lock:
            now = self.clock()
            if self.last is not None:
                self.sleep(max(0, self.interval - (now - self.last)))
            self.last = self.clock()


_PACERS = {}
_PACERS_LOCK = threading.Lock()


def _pacer(credentials):
    key = hashlib.sha256(credentials.app_key.encode()).hexdigest()
    with _PACERS_LOCK:
        return _PACERS.setdefault(key, RequestPacer())


def _assert_no_http_retries(session):
    for adapter in getattr(session, "adapters", {}).values():
        retries = getattr(adapter, "max_retries", None)
        if retries is not None and getattr(retries, "total", 0) not in {0, False}:
            raise DemoNotSentError("VTS transport forbids automatic HTTP retries")


class KisDemoClient:
    def __init__(
        self,
        credentials: DemoCredentials,
        *,
        session=None,
        timeout=15,
        pacer=None,
        utcnow=None,
    ):
        self.credentials = credentials
        self.session = session or requests.Session()
        # A caller-supplied HTTP retry adapter could silently duplicate a write.
        # Test transports expose only request(); real Requests sessions must use
        # the default zero-retry adapters for every mounted scheme.
        _assert_no_http_retries(self.session)
        self.timeout = max(1, min(float(timeout), 30))
        self._token = None
        self._expires = datetime.min.replace(tzinfo=timezone.utc)
        self.pacer = pacer or _pacer(credentials)
        self.utcnow = utcnow or (lambda: datetime.now(timezone.utc))

    def close(self):
        self.session.close()

    def _now(self):
        value = self.utcnow()
        if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
            raise DemoNotSentError("Aware transport clock required")
        return value.astimezone(timezone.utc)

    def _http(self, method, path, *, deadline=None, not_before=None, **kwargs):
        allowed = {
            ("POST", "/oauth2/tokenP"),
            ("GET", PREFIX + "inquire-balance"),
            ("GET", PREFIX + "inquire-daily-ccld"),
            ("GET", PREFIX + "inquire-psbl-order"),
            ("POST", PREFIX + "order-cash"),
            ("POST", PREFIX + "order-rvsecncl"),
        }
        if (method, path) not in allowed:
            raise DemoNotSentError("Request is outside the VTS path allowlist")
        _assert_no_http_retries(self.session)
        started = self._now()
        if not_before is not None and started < not_before:
            raise DemoNotSentError("VTS clock regressed before transport")
        self.pacer.wait()
        sent_at = self._now()
        if sent_at < started:
            raise DemoNotSentError("VTS clock regressed during pacing")
        if deadline is not None and sent_at >= stamp(deadline):
            raise DemoNotSentError("VTS request deadline elapsed before sending")
        try:
            response = self.session.request(
                method,
                DEMO_HOST + path,
                timeout=self.timeout,
                allow_redirects=False,
                **kwargs,
            )
            if not 200 <= response.status_code < 300:
                raise DemoError(f"VTS HTTP status {int(response.status_code)}")
            payload = response.json()
            if not isinstance(payload, dict):
                raise DemoError("VTS invalid response")
            try:
                received_at = self._now()
            except DemoNotSentError:
                raise DemoError("VTS response clock unavailable after transport") from None
            if received_at < sent_at:
                # A write might already be accepted: retain UNKNOWN rather than
                # classify a post-transport clock failure as safely NOT_SENT.
                raise DemoError("VTS clock regressed during response")
            return payload, response.headers
        except (requests.RequestException, ValueError):
            raise DemoError("VTS response unavailable or invalid") from None

    def authenticate(self):
        now = self._now()
        if self._token and now < self._expires:
            return
        payload, _ = self._http(
            "POST",
            "/oauth2/tokenP",
            json={
                "grant_type": "client_credentials",
                "appkey": self.credentials.app_key,
                "appsecret": self.credentials.app_secret,
            },
        )
        token = payload.get("access_token")
        if not isinstance(token, str) or not token:
            raise DemoError("VTS authentication rejected")
        self._token = token
        try:
            seconds = int(payload.get("expires_in", 0))
        except (TypeError, ValueError):
            raise DemoError("VTS invalid token expiry") from None
        self._expires = now + timedelta(seconds=max(0, min(seconds, 86400) - 120))

    def _account(self):
        return {
            "CANO": self.credentials.account_no,
            "ACNT_PRDT_CD": self.credentials.product_code,
        }

    def request(
        self,
        method,
        endpoint,
        tr_id,
        *,
        params=None,
        body=None,
        continuation="",
        deadline=None,
        not_before=None,
    ):
        allowed = {
            ("GET", "inquire-balance", "VTTC8434R"),
            ("GET", "inquire-daily-ccld", "VTTC0081R"),
            ("GET", "inquire-psbl-order", "VTTC8908R"),
            ("POST", "order-cash", "VTTC0012U"),
            ("POST", "order-cash", "VTTC0011U"),
            ("POST", "order-rvsecncl", "VTTC0013U"),
        }
        if (method, endpoint, tr_id) not in allowed:
            raise DemoNotSentError("Request is outside the VTS allowlist")
        supplied = body if body is not None else params or {}
        if any(supplied.get(k) != v for k, v in self._account().items()):
            raise DemoNotSentError("VTS account scope mismatch")
        started = self._now()
        if not_before is not None and started < stamp(not_before):
            raise DemoNotSentError("VTS clock regressed since intent validation")
        try:
            self.authenticate()
        except DemoError:
            raise DemoNotSentError(
                "VTS authentication failed before sending the request"
            ) from None
        if self._now() < started:
            raise DemoNotSentError("VTS clock regressed during authentication")
        headers = {
            "authorization": f"Bearer {self._token}",
            "appkey": self.credentials.app_key,
            "appsecret": self.credentials.app_secret,
            "tr_id": tr_id,
            "custtype": "P",
            "content-type": "application/json",
            "tr_cont": continuation,
        }
        # No generic HTTP retry adapter: even a timeout can conceal an accepted order.
        return self._http(
            method,
            PREFIX + endpoint,
            headers=headers,
            params=params,
            json=body,
            deadline=deadline,
            not_before=started,
        )

    def _pages(self, endpoint, tr_id, params):
        rows, totals, seen = [], [], set()
        continuation = ""
        for _ in range(20):
            payload, headers = self.request(
                "GET", endpoint, tr_id, params=params, continuation=continuation
            )
            if str(payload.get("rt_cd")) != "0":
                raise DemoError("VTS read rejected")
            if not isinstance(payload.get("output1"), list) or any(
                not isinstance(r, dict) for r in payload["output1"]
            ):
                raise DemoError("VTS missing rows; not an empty account")
            rows.extend(payload["output1"])
            totals = payload.get("output2", totals)
            flag = next(
                (str(v) for k, v in headers.items() if k.lower() == "tr_cont"), ""
            )
            if flag not in {"M", "F"}:
                return rows, totals
            cursor = (
                str(payload.get("ctx_area_fk100") or ""),
                str(payload.get("ctx_area_nk100") or ""),
            )
            if cursor == ("", "") or cursor in seen:
                raise DemoError("VTS pagination incomplete")
            seen.add(cursor)
            params = {
                **params,
                "CTX_AREA_FK100": cursor[0],
                "CTX_AREA_NK100": cursor[1],
            }
            continuation = "N"
        raise DemoError("VTS pagination limit reached")

    def balance(self):
        rows, totals = self._pages(
            "inquire-balance",
            "VTTC8434R",
            {
                **self._account(),
                "AFHR_FLPR_YN": "N",
                "OFL_YN": "",
                "INQR_DVSN": "02",
                "UNPR_DVSN": "01",
                "FUND_STTL_ICLD_YN": "N",
                "FNCG_AMT_AUTO_RDPT_YN": "N",
                "PRCS_DVSN": "00",
                "CTX_AREA_FK100": "",
                "CTX_AREA_NK100": "",
            },
        )
        if not totals or not isinstance(totals, (dict, list)):
            raise DemoError("VTS missing balance totals")
        return rows, totals

    def orders(self, trade_date: str):
        if not isinstance(trade_date, str) or not re.fullmatch(r"[0-9]{8}", trade_date):
            raise DemoError("Explicit eight-digit order date required")
        if datetime.strptime(trade_date, "%Y%m%d").date() > self.utcnow().astimezone(ZoneInfo("Asia/Seoul")).date():
            raise DemoError("Future order date is not allowed")
        return self._pages(
            "inquire-daily-ccld",
            "VTTC0081R",
            {
                **self._account(),
                "INQR_STRT_DT": trade_date,
                "INQR_END_DT": trade_date,
                "SLL_BUY_DVSN_CD": "00",
                "CCLD_DVSN": "00",
                "INQR_DVSN": "00",
                "INQR_DVSN_3": "00",
                "PDNO": "",
                "ORD_GNO_BRNO": "",
                "ODNO": "",
                "INQR_DVSN_1": "",
                "EXCG_ID_DVSN_CD": "KRX",
                "CTX_AREA_FK100": "",
                "CTX_AREA_NK100": "",
            },
        )[0]

    def buying_power(self, *, ticker: str, limit_price: int):
        """Cash-only buying capacity; never use margin-inclusive max_buy_amt."""
        if not re.fullmatch(r"[0-9]{6}", str(ticker)) or type(limit_price) is not int or limit_price <= 0:
            raise DemoNotSentError("KR ticker and integer limit required")
        payload, _ = self.request("GET", "inquire-psbl-order", "VTTC8908R", params={
            **self._account(), "PDNO": ticker, "ORD_UNPR": str(limit_price),
            # Official cash-only quantity guidance uses market-order division
            # for the capacity query. The submitted order remains limit-only.
            "ORD_DVSN": "01", "CMA_EVLU_AMT_ICLD_YN": "N", "OVRS_ICLD_YN": "N",
        })
        if str(payload.get("rt_cd")) != "0" or not isinstance(payload.get("output"), dict):
            raise DemoError("VTS cash buying capacity unavailable")
        return payload["output"]


def _issue_at(value):
    try:
        return stamp(value.isoformat() if isinstance(value, datetime) else value).astimezone(timezone.utc)
    except (TypeError, ValueError):
        raise DemoError("Explicit reconciliation issue clock required") from None


def _issue_hash(intent_id, previous_sequence, previous_hash, transition, reason, present, observed_at, ingested_at):
    values = [intent_id, previous_sequence, previous_hash, transition, reason, present, observed_at, ingested_at]
    return hashlib.sha256(json.dumps(values, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def reconciliation_issue_state(db, intent_id, *, as_of):
    """Read dated issue transitions without inferring legacy occurrence times.

    Mutable current rows remain the live order gate. Comparing the full immutable
    history head with that current table only detects an unlogged edit; historical
    state is selected solely from transitions available by the requested cutoff.
    No schema migration or other write happens in this reader.
    """
    unknown = {"status": "UNVERIFIED", "known_at": None}
    cutoff = _issue_at(as_of)
    if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='reconciliation_issue_history'").fetchone():
        return unknown
    rows = db.execute("""SELECT sequence,previous_sequence,transition,reason,present,observed_at,ingested_at,proof_sha256
        FROM reconciliation_issue_history WHERE intent_id=? ORDER BY sequence""", (intent_id,)).fetchall()
    current = db.execute("SELECT reason FROM reconciliation_issues WHERE id=?", (intent_id,)).fetchone()
    if not rows:
        return unknown
    previous, previous_hash, previous_time, selected = None, None, None, None
    try:
        for row in rows:
            sequence, parent, transition, reason, present, observed, ingested, digest = row
            received, known = _issue_at(observed), _issue_at(ingested)
            if (parent != previous or transition not in {"BASELINE_CLEAR", "SET", "CLEAR", "LEGACY_UNKNOWN"}
                    or type(present) is not int or present not in {0, 1}
                    or transition in {"BASELINE_CLEAR", "CLEAR"} and (present or reason is not None)
                    or transition == "SET" and (not present or not isinstance(reason, str) or not reason)
                    or transition == "LEGACY_UNKNOWN" and (present and (not isinstance(reason, str) or not reason)
                        or not present and reason is not None)
                    or received > known or previous_time is not None and received < previous_time
                    or digest != _issue_hash(intent_id, parent, previous_hash, transition, reason, present, observed, ingested)):
                return unknown
            if known <= cutoff:
                selected = row
            previous, previous_hash, previous_time = sequence, digest, known
        head = rows[-1]
        if bool(current) != bool(head[4]) or current is not None and current[0] != head[3]:
            return unknown
        if any(row[2] == "LEGACY_UNKNOWN" and _issue_at(row[6]) > cutoff for row in rows):
            # Its first observation is not its onset. In particular, recording
            # an undated legacy row must not turn it into a harmless future SET.
            return unknown
        if selected is None or selected[2] == "LEGACY_UNKNOWN":
            return unknown
        return {"status": "ACTIVE" if selected[4] else "CLEAR", "known_at": selected[6]}
    except (DemoError, TypeError, ValueError):
        return unknown


class DemoOrderJournal:
    def __init__(self, path: Path, client: KisDemoClient, *, issue_clock=None):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.client = client
        self.issue_clock = issue_clock or (lambda: client.utcnow())
        self.db = sqlite3.connect(path, isolation_level=None, timeout=20)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
          CREATE TABLE IF NOT EXISTS owner(scope TEXT PRIMARY KEY);
          CREATE TABLE IF NOT EXISTS requests(id TEXT PRIMARY KEY, fingerprint TEXT NOT NULL,
            status TEXT NOT NULL, response TEXT NOT NULL, created_at TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS reconciliations(id TEXT NOT NULL, observed_at TEXT NOT NULL,
            evidence TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS intents(id TEXT PRIMARY KEY, endpoint TEXT NOT NULL,
            tr_id TEXT NOT NULL, body TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS order_state(id TEXT PRIMARY KEY, status TEXT NOT NULL,
            filled INTEGER NOT NULL, remaining INTEGER NOT NULL);
          CREATE TABLE IF NOT EXISTS reconciliation_issues(id TEXT PRIMARY KEY, reason TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS reconciliation_issue_history(
            sequence INTEGER PRIMARY KEY AUTOINCREMENT, intent_id TEXT NOT NULL,
            previous_sequence INTEGER, transition TEXT NOT NULL, reason TEXT,
            present INTEGER NOT NULL, observed_at TEXT NOT NULL, ingested_at TEXT NOT NULL,
            proof_sha256 TEXT NOT NULL);
          CREATE TRIGGER IF NOT EXISTS reconciliation_issue_history_no_update BEFORE UPDATE ON reconciliation_issue_history
            BEGIN SELECT RAISE(ABORT,'Reconciliation issue history is immutable'); END;
          CREATE TRIGGER IF NOT EXISTS reconciliation_issue_history_no_delete BEFORE DELETE ON reconciliation_issue_history
            BEGIN SELECT RAISE(ABORT,'Reconciliation issue history is immutable'); END;
        """)
        self.db.execute("BEGIN IMMEDIATE")
        try:
            owner = self.db.execute("SELECT scope FROM owner").fetchone()
            if owner and owner[0] != client.credentials.scope():
                raise DemoError("Journal belongs to another demo account")
            self.db.execute(
                "INSERT OR IGNORE INTO owner VALUES (?)", (client.credentials.scope(),)
            )
            for identity, reason in self.db.execute("SELECT id,reason FROM reconciliation_issues").fetchall():
                head = self._issue_head(identity)
                if not head or not head[4] or head[3] != reason:
                    # First seen is an observation, never a backdated start.
                    self._append_issue(identity, "LEGACY_UNKNOWN", reason, 1)
            self.db.execute("COMMIT")
        except Exception:
            self.db.execute("ROLLBACK")
            self.db.close()
            raise

    def close(self):
        self.db.close()

    def _block(self, intent_id, reason):
        self.db.execute("SAVEPOINT reconciliation_issue_change")
        try:
            self._observe_unlogged_issue(intent_id)
            head = self._issue_head(intent_id)
            if not head or (head[2], head[3], head[4]) != ("SET", reason, 1):
                self._append_issue(intent_id, "SET", reason, 1)
            self.db.execute("INSERT OR REPLACE INTO reconciliation_issues VALUES (?,?)", (intent_id, reason))
            self.db.execute("RELEASE SAVEPOINT reconciliation_issue_change")
        except Exception:
            self.db.execute("ROLLBACK TO SAVEPOINT reconciliation_issue_change")
            self.db.execute("RELEASE SAVEPOINT reconciliation_issue_change")
            # A missing/regressed clock cannot remove the original live block.
            # This undated state is deliberately unverified for cost evaluation.
            self.db.execute("INSERT OR REPLACE INTO reconciliation_issues VALUES (?,?)", (intent_id, reason))
            raise

    def _issue_head(self, intent_id):
        return self.db.execute("""SELECT sequence,previous_sequence,transition,reason,present,observed_at,ingested_at,proof_sha256
            FROM reconciliation_issue_history WHERE intent_id=? ORDER BY sequence DESC LIMIT 1""", (intent_id,)).fetchone()

    def _append_issue(self, intent_id, transition, reason, present):
        observed, ingested = _issue_at(self.issue_clock()), _issue_at(self.issue_clock())
        head = self._issue_head(intent_id)
        if observed > ingested or head and observed < _issue_at(head[6]):
            raise DemoError("Reconciliation issue clock regressed")
        parent, previous_hash = (head[0], head[7]) if head else (None, None)
        observed, ingested = observed.isoformat(), ingested.isoformat()
        digest = _issue_hash(intent_id, parent, previous_hash, transition, reason, present, observed, ingested)
        self.db.execute("""INSERT INTO reconciliation_issue_history
            (intent_id,previous_sequence,transition,reason,present,observed_at,ingested_at,proof_sha256)
            VALUES (?,?,?,?,?,?,?,?)""", (intent_id, parent, transition, reason, present, observed, ingested, digest))

    def _observe_unlogged_issue(self, intent_id):
        current = self.db.execute("SELECT reason FROM reconciliation_issues WHERE id=?", (intent_id,)).fetchone()
        head = self._issue_head(intent_id)
        if current is not None and (not head or not head[4] or head[3] != current[0]):
            self._append_issue(intent_id, "LEGACY_UNKNOWN", current[0], 1)
        elif current is None and head and head[4]:
            self._append_issue(intent_id, "LEGACY_UNKNOWN", None, 0)

    def _clear_issue(self, intent_id):
        """Called only by the original verified reconciliation CLEAR paths."""
        self.db.execute("SAVEPOINT reconciliation_issue_change")
        try:
            self._observe_unlogged_issue(intent_id)
            head = self._issue_head(intent_id)
            if not head or head[2] not in {"BASELINE_CLEAR", "CLEAR"} or head[4]:
                self._append_issue(intent_id, "CLEAR", None, 0)
            self.db.execute("DELETE FROM reconciliation_issues WHERE id=?", (intent_id,))
            self.db.execute("RELEASE SAVEPOINT reconciliation_issue_change")
        except Exception:
            self.db.execute("ROLLBACK TO SAVEPOINT reconciliation_issue_change")
            self.db.execute("RELEASE SAVEPOINT reconciliation_issue_change")
            raise

    def ensure_issue_baseline(self, intent_id):
        """Date a currently issue-free import; never invent its earlier history."""
        if self.db.execute("SELECT 1 FROM reconciliation_issues WHERE id=?", (intent_id,)).fetchone():
            raise DemoError("Settlement order has an unresolved reconciliation")
        head = self._issue_head(intent_id)
        if head is None:
            self._append_issue(intent_id, "BASELINE_CLEAR", None, 0)
        elif reconciliation_issue_state(self.db, intent_id, as_of=_issue_at(self.issue_clock()))["status"] != "CLEAR":
            raise DemoError("Settlement reconciliation history is unverified")

    def _write_once(self, intent_id, endpoint, tr_id, body, now, *, deadline=None):
        if not isinstance(intent_id, str) or not intent_id or len(intent_id) > 200:
            raise ValueError("Stable intent ID required")
        fingerprint = hashlib.sha256(
            json.dumps([endpoint, tr_id, body], sort_keys=True).encode()
        ).hexdigest()
        self.db.execute("BEGIN IMMEDIATE")
        try:
            row = self.db.execute(
                "SELECT * FROM requests WHERE id=?", (intent_id,)
            ).fetchone()
            if row:
                if row["fingerprint"] != fingerprint:
                    raise DemoError("Intent ID reused with different order content")
                self.db.execute("COMMIT")
                return {"status": row["status"], **json.loads(row["response"])}
            if endpoint in {"order-cash", "order"} and (
                self.db.execute(
                    "SELECT 1 FROM requests WHERE status='UNKNOWN'"
                ).fetchone()
                or self.db.execute("SELECT 1 FROM reconciliation_issues").fetchone()
            ):
                raise DemoError(
                    "Resolve ambiguous demo request before submitting another intent"
                )
            # Persist before any network call. A crash leaves UNKNOWN, never resubmit.
            self.db.execute(
                "INSERT INTO requests VALUES (?,?,?,?,?)",
                (intent_id, fingerprint, "UNKNOWN", "{}", now),
            )
            # Retain immutable requested terms, without account IDs or credentials.
            self.db.execute(
                "INSERT INTO intents VALUES (?,?,?,?)",
                (
                    intent_id,
                    endpoint,
                    tr_id,
                    json.dumps(
                        {
                            k: v
                            for k, v in body.items()
                            if k not in {"CANO", "ACNT_PRDT_CD"}
                        }
                    ),
                ),
            )
            self.db.execute("COMMIT")
        except Exception:
            self.db.execute("ROLLBACK")
            raise
        status, result = "UNKNOWN", {}
        try:
            payload, _ = self.client.request(
                "POST", endpoint, tr_id, body=body, deadline=deadline, not_before=now
            )
            output = payload.get("output") or {}
            if not isinstance(output, dict):
                raise DemoError("VTS malformed order receipt")
            broker_id = str(output.get("ODNO") or output.get("odno") or "")
            if str(payload.get("rt_cd")) == "0" and broker_id:
                status = "ACKNOWLEDGED"
                result = {
                    "broker_order_id": broker_id,
                    "organization": str(
                        output.get("KRX_FWDG_ORD_ORGNO")
                        or output.get("krx_fwdg_ord_orgno")
                        or ""
                    ),
                }
            elif str(payload.get("rt_cd")) == "1":
                status = "REJECTED"
        except DemoNotSentError:
            status = "NOT_SENT"
        except DemoError:
            pass
        self.db.execute(
            "UPDATE requests SET status=?,response=? WHERE id=?",
            (status, json.dumps(result), intent_id),
        )
        return {"status": status, **result}

    def submit(
        self,
        *,
        intent_id,
        ticker,
        side,
        quantity,
        limit_price,
        available_at,
        valid_until,
        now,
    ):
        if not stamp(available_at) <= stamp(now) < stamp(valid_until):
            raise DemoError("Order intent expired or not yet available")
        preview = kis_demo_order_preview(
            ticker=ticker, side=side, quantity=quantity, limit_price=limit_price
        )
        body = {
            **preview["body"],
            **self.client._account(),
            "SLL_TYPE": "01" if side == "SELL" else "",
            "CNDT_PRIC": "",
        }
        return self._write_once(
            intent_id, "order-cash", preview["tr_id"], body, now, deadline=valid_until
        )

    def reconcile(self, *, intent_id, trade_date, reports=None):
        row = self.db.execute(
            "SELECT * FROM requests WHERE id=?", (intent_id,)
        ).fetchone()
        if not row:
            raise DemoError("Unknown local intent")
        if (
            stamp(row["created_at"])
            .astimezone(ZoneInfo("Asia/Seoul"))
            .strftime("%Y%m%d")
            != trade_date
        ):
            raise DemoError("Reconciliation date differs from original order session")
        result = json.loads(row["response"])
        broker_id = result.get("broker_order_id")
        if not broker_id:
            return {
                "status": row["status"],
                "requires_manual_reconciliation": row["status"] == "UNKNOWN",
            }
        try:
            reports = self.client.orders(trade_date) if reports is None else reports
            if not isinstance(reports, list) or any(not isinstance(item, dict) for item in reports):
                raise DemoError("VTS invalid order rows")
        except DemoError:
            self._block(intent_id, "broker_query_unavailable")
            raise
        matches = [r for r in reports if str(r.get("odno")) == broker_id]
        if len(matches) != 1:
            self._block(intent_id, "missing_or_duplicate_order")
            return {"status": "UNRESOLVED", "requires_manual_reconciliation": True}
        r = matches[0]
        intent = self.db.execute(
            "SELECT * FROM intents WHERE id=?", (intent_id,)
        ).fetchone()
        if not intent or intent["endpoint"] != "order-cash":
            self._block(intent_id, "original_terms_unavailable")
            raise DemoError("Original cash-order terms unavailable for reconciliation")
        terms = json.loads(intent["body"])
        try:
            ordered, filled, remaining = [
                int(r[k]) for k in ("ord_qty", "tot_ccld_qty", "rmn_qty")
            ]
            if (
                ordered <= 0
                or not 0 <= filled <= ordered
                or not 0 <= remaining <= ordered - filled
                or ordered != int(terms["ORD_QTY"])
                or str(r.get("pdno")) != terms["PDNO"]
                or str(r.get("sll_buy_dvsn_cd"))
                != ("02" if intent["tr_id"] == "VTTC0012U" else "01")
                or float(r.get("ord_unpr", "nan")) != float(terms["ORD_UNPR"])
            ):
                raise ValueError()
        except (KeyError, TypeError, ValueError):
            self._block(intent_id, "order_terms_or_fill_mismatch")
            raise DemoError("VTS invalid fill quantities") from None
        # VTS keeps cncl_yn=N on the original order after a successful cancel;
        # its confirmed cancelled quantity closes the original remainder. The
        # separate cancellation row has cncl_yn=Y and a different order ID.
        # Accept only explicit, consistent quantities on the matched original.
        confirmed = None
        try:
            values = [r[key] for key in ("cncl_cfrm_qty", "cnc_cfrm_qty") if key in r]
            if values:
                if any(not isinstance(value, str) or not re.fullmatch(r"[0-9]+", value) for value in values):
                    raise ValueError()
                quantities = {int(value) for value in values}
                if len(quantities) != 1:
                    raise ValueError()
                confirmed = quantities.pop()
                if confirmed > ordered - filled or (confirmed > 0 and filled + remaining + confirmed != ordered):
                    raise ValueError()
        except (TypeError, ValueError):
            self._block(intent_id, "invalid_confirmed_cancellation_quantity")
            raise DemoError("VTS cancellation quantity missing or inconsistent") from None
        cancelled = str(r.get("cncl_yn", "")).upper() == "Y" or (
            confirmed is not None and confirmed > 0 and remaining == 0
        )
        if cancelled and remaining:
            self._block(intent_id, "cancelled_with_remainder")
            raise DemoError("VTS cancelled order still reports a remainder")
        status = (
            "FILLED"
            if filled == ordered
            else "CANCELLED"
            if cancelled
            else "UNRESOLVED"
            if filled + remaining != ordered
            else "PARTIAL"
            if filled
            else "OPEN"
        )
        receipt = {
            "status": status,
            "filled_qty": filled,
            "remaining_qty": remaining,
            "broker_order_id": broker_id,
            "organization": result.get("organization", ""),
        }
        self.db.execute("BEGIN IMMEDIATE")
        try:
            previous = self.db.execute(
                "SELECT * FROM order_state WHERE id=?", (intent_id,)
            ).fetchone()
            if previous and (
                filled < previous["filled"]
                or (
                    previous["status"] in {"FILLED", "CANCELLED"}
                    and (
                        status != previous["status"]
                        or filled != previous["filled"]
                        or remaining != previous["remaining"]
                    )
                )
            ):
                raise DemoError(
                    "VTS reconciliation regressed; investigate before trading"
                )
            self.db.execute(
                "INSERT INTO reconciliations VALUES (?,?,?)",
                (
                    intent_id,
                    self.client.utcnow().isoformat(),
                    json.dumps(receipt),
                ),
            )
            if status != "UNRESOLVED":
                self.db.execute(
                    "INSERT OR REPLACE INTO order_state VALUES (?,?,?,?)",
                    (intent_id, status, filled, remaining),
                )
                self._clear_issue(intent_id)
            else:
                self._block(intent_id, "unresolved_fill_arithmetic")
            self.db.execute("COMMIT")
        except Exception:
            self.db.execute("ROLLBACK")
            self._block(intent_id, "reconciliation_regressed_or_failed")
            raise
        return receipt

    def cancel(self, *, intent_id, trade_date, now, reconciled_receipt=None, deadline=None):
        if (
            stamp(now).astimezone(ZoneInfo("Asia/Seoul")).strftime("%Y%m%d")
            != trade_date
            or self.client.utcnow()
            .astimezone(ZoneInfo("Asia/Seoul"))
            .strftime("%Y%m%d")
            != trade_date
        ):
            raise DemoError("DAY order cancellation requires the original session")
        previous = self.db.execute(
            "SELECT status,response FROM requests WHERE id=?", ("cancel:" + intent_id,)
        ).fetchone()
        if previous:
            return {"status": previous["status"], **json.loads(previous["response"])}
        receipt = (self.reconcile(intent_id=intent_id, trade_date=trade_date)
                   if reconciled_receipt is None else reconciled_receipt)
        if (
            receipt["status"] not in {"OPEN", "PARTIAL"}
            or receipt.get("remaining_qty", 0) <= 0
            or not receipt.get("organization")
        ):
            raise DemoError("No reconciled cancellable demo remainder")
        body = {
            **self.client._account(),
            "KRX_FWDG_ORD_ORGNO": receipt["organization"],
            "ORGN_ODNO": receipt["broker_order_id"],
            "ORD_DVSN": "00",
            "RVSE_CNCL_DVSN_CD": "02",
            "ORD_QTY": str(receipt["remaining_qty"]),
            "ORD_UNPR": "0",
            "QTY_ALL_ORD_YN": "Y",
            "EXCG_ID_DVSN_CD": "KRX",
        }
        return self._write_once(
            "cancel:" + intent_id,
            "order-rvsecncl",
            "VTTC0013U",
            body,
            now,
            deadline=deadline or (
                stamp(now)
                .astimezone(ZoneInfo("Asia/Seoul"))
                .replace(hour=0, minute=0, second=0, microsecond=0)
                + timedelta(days=1)
            ).isoformat(),
        )
