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
from zoneinfo import ZoneInfo

import requests

from tradingagents.dataflows.api_keys import get_api_key
from .paper import kis_demo_order_preview, stamp

DEMO_HOST = "https://openapivts.koreainvestment.com:29443"
PREFIX = "/uapi/domestic-stock/v1/trading/"
DEMO_KEYS = (
    "KIS_DEMO_APP_KEY",
    "KIS_DEMO_APP_SECRET",
    "KIS_DEMO_ACCOUNT_NO",
    "KIS_DEMO_PRODUCT_CODE",
)


class DemoError(RuntimeError):
    """Sanitized error: never include broker bodies, URLs, account IDs or keys."""


def configuration_status():
    return {key: bool(get_api_key(key)) for key in DEMO_KEYS}


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
        values = [get_api_key(key) for key in DEMO_KEYS]
        if not all(values):
            raise DemoError(
                "Dedicated KIS_DEMO settings required; real credentials are not a fallback"
            )
        return cls(*values)

    def scope(self):
        return hashlib.sha256(
            f"demo:{self.account_no}:{self.product_code}".encode()
        ).hexdigest()


class KisDemoClient:
    def __init__(self, credentials: DemoCredentials, *, session=None, timeout=15):
        self.credentials = credentials
        self.session = session or requests.Session()
        self.timeout = max(1, min(float(timeout), 30))
        self._token = None
        self._expires = datetime.min.replace(tzinfo=timezone.utc)

    def close(self):
        self.session.close()

    def _http(self, method, path, **kwargs):
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
            return payload, response.headers
        except (requests.RequestException, ValueError):
            raise DemoError("VTS response unavailable or invalid") from None

    def authenticate(self):
        now = datetime.now(timezone.utc)
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
        self, method, endpoint, tr_id, *, params=None, body=None, continuation=""
    ):
        allowed = {
            ("GET", "inquire-balance", "VTTC8434R"),
            ("GET", "inquire-daily-ccld", "VTTC0081R"),
            ("POST", "order-cash", "VTTC0012U"),
            ("POST", "order-cash", "VTTC0011U"),
            ("POST", "order-rvsecncl", "VTTC0013U"),
        }
        if (method, endpoint, tr_id) not in allowed:
            raise DemoError("Request is outside the VTS allowlist")
        supplied = body if body is not None else params or {}
        if any(supplied.get(k) != v for k, v in self._account().items()):
            raise DemoError("VTS account scope mismatch")
        self.authenticate()
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
            method, PREFIX + endpoint, headers=headers, params=params, json=body
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
            if not isinstance(payload.get("output1"), list):
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
        datetime.strptime(trade_date, "%Y%m%d")
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


class DemoOrderJournal:
    def __init__(self, path: Path, client: KisDemoClient):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.client = client
        self.db = sqlite3.connect(path, isolation_level=None, timeout=20)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
          CREATE TABLE IF NOT EXISTS owner(scope TEXT PRIMARY KEY);
          CREATE TABLE IF NOT EXISTS requests(id TEXT PRIMARY KEY, fingerprint TEXT NOT NULL,
            status TEXT NOT NULL, response TEXT NOT NULL, created_at TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS reconciliations(id TEXT NOT NULL, observed_at TEXT NOT NULL,
            evidence TEXT NOT NULL);
        """)
        self.db.execute("BEGIN IMMEDIATE")
        try:
            owner = self.db.execute("SELECT scope FROM owner").fetchone()
            if owner and owner[0] != client.credentials.scope():
                raise DemoError("Journal belongs to another demo account")
            self.db.execute(
                "INSERT OR IGNORE INTO owner VALUES (?)", (client.credentials.scope(),)
            )
            self.db.execute("COMMIT")
        except Exception:
            self.db.execute("ROLLBACK")
            self.db.close()
            raise

    def close(self):
        self.db.close()

    def _write_once(self, intent_id, endpoint, tr_id, body, now):
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
            if self.db.execute(
                "SELECT 1 FROM requests WHERE status='UNKNOWN'"
            ).fetchone():
                raise DemoError(
                    "Resolve ambiguous demo request before submitting another intent"
                )
            # Persist before any network call. A crash leaves UNKNOWN, never resubmit.
            self.db.execute(
                "INSERT INTO requests VALUES (?,?,?,?,?)",
                (intent_id, fingerprint, "UNKNOWN", "{}", now),
            )
            self.db.execute("COMMIT")
        except Exception:
            self.db.execute("ROLLBACK")
            raise
        status, result = "UNKNOWN", {}
        try:
            payload, _ = self.client.request("POST", endpoint, tr_id, body=body)
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
            elif str(payload.get("rt_cd")) not in {"0", "None"}:
                status = "REJECTED"
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
        return self._write_once(intent_id, "order-cash", preview["tr_id"], body, now)

    def reconcile(self, *, intent_id, trade_date):
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
        matches = [
            r for r in self.client.orders(trade_date) if str(r.get("odno")) == broker_id
        ]
        if len(matches) != 1:
            return {"status": "UNRESOLVED", "requires_manual_reconciliation": True}
        r = matches[0]
        try:
            ordered, filled, remaining = [
                int(r[k]) for k in ("ord_qty", "tot_ccld_qty", "rmn_qty")
            ]
            if (
                ordered <= 0
                or not 0 <= filled <= ordered
                or not 0 <= remaining <= ordered - filled
            ):
                raise ValueError()
        except (KeyError, TypeError, ValueError):
            raise DemoError("VTS invalid fill quantities") from None
        cancelled = str(r.get("cncl_yn", "")).upper() == "Y"
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
        self.db.execute(
            "INSERT INTO reconciliations VALUES (?,?,?)",
            (intent_id, datetime.now(timezone.utc).isoformat(), json.dumps(receipt)),
        )
        return receipt

    def cancel(self, *, intent_id, trade_date, now):
        if (
            stamp(now).astimezone(ZoneInfo("Asia/Seoul")).strftime("%Y%m%d")
            != trade_date
        ):
            raise DemoError("DAY order cancellation requires the original session")
        receipt = self.reconcile(intent_id=intent_id, trade_date=trade_date)
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
            "cancel:" + intent_id, "order-rvsecncl", "VTTC0013U", body, now
        )
