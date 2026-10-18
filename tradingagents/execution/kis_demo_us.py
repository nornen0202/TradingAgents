"""Dedicated US VTS read probe. Token POST and two account GETs only.

Current balance receipt is not historical point-in-time evidence. This module
cannot submit, cancel or amend an order, and cannot select the production host.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import re
from zoneinfo import ZoneInfo

import requests

from .demo_secrets import DEMO_KEYS, load_demo_settings, storage_path
from .kis_demo import (
    DEMO_HOST, DemoCredentials, DemoError, _assert_no_http_retries, _pacer,
)

PREFIX = "/uapi/overseas-stock/v1/trading/"
EXCHANGES = ("NASD", "NYSE", "AMEX")
NEW_YORK = ZoneInfo("America/New_York")
SEOUL = ZoneInfo("Asia/Seoul")


def us_settings():
    """US-specific protected bundle only; never consume domestic or live keys."""
    return load_demo_settings(path=storage_path().with_name("kis-demo-us.dpapi"))


def configuration_status():
    bundle = us_settings()
    return {key: bool(bundle.get(key)) for key in DEMO_KEYS}


def credentials_from_settings():
    bundle = us_settings()
    if not all(bundle.get(key) for key in DEMO_KEYS):
        raise DemoError("Dedicated US demo settings required")
    return DemoCredentials(*(bundle[key] for key in DEMO_KEYS))


def _date(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{8}", value):
        raise DemoError("Explicit valid order date required")
    try:
        return datetime.strptime(value, "%Y%m%d").date()
    except ValueError:
        raise DemoError("Explicit valid order date required") from None


def _rows(value):
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise DemoError("VTS missing rows; not an empty account")
    return value


class KisDemoUSReadClient:
    def __init__(self, credentials, *, session=None, pacer=None, utcnow=None, timeout=15):
        self.credentials = credentials
        self.session = session or requests.Session()
        _assert_no_http_retries(self.session)
        self.pacer = pacer or _pacer(credentials)
        self.utcnow = utcnow or (lambda: datetime.now(timezone.utc))
        self.timeout = max(1, min(float(timeout), 30))
        self._token = None
        self._expires = datetime.min.replace(tzinfo=timezone.utc)

    def close(self):
        self.session.close()

    def _now(self):
        value = self.utcnow()
        if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
            raise DemoError("Aware observation clock required")
        return value.astimezone(timezone.utc)

    def _http(self, method, path, **kwargs):
        if (method, path) not in {
            ("POST", "/oauth2/tokenP"),
            ("GET", PREFIX + "inquire-balance"),
            ("GET", PREFIX + "inquire-ccnl"),
        }:
            raise DemoError("Request is outside the read-only US VTS allowlist")
        _assert_no_http_retries(self.session)
        self.pacer.wait()
        try:
            response = self.session.request(
                method, DEMO_HOST + path, timeout=self.timeout,
                allow_redirects=False, **kwargs,
            )
            if not 200 <= response.status_code < 300:
                raise DemoError("US VTS HTTP response rejected")
            payload = response.json()
            if not isinstance(payload, dict):
                raise DemoError("US VTS invalid response")
            return payload, response.headers
        except (requests.RequestException, ValueError):
            raise DemoError("US VTS response unavailable or invalid") from None

    def authenticate(self):
        now = self._now()
        if self._token and now < self._expires:
            return
        payload, _ = self._http("POST", "/oauth2/tokenP", json={
            "grant_type": "client_credentials", "appkey": self.credentials.app_key,
            "appsecret": self.credentials.app_secret,
        })
        token, expiry = payload.get("access_token"), payload.get("expires_in")
        if not isinstance(token, str) or not token or isinstance(expiry, bool):
            raise DemoError("US VTS authentication rejected")
        try:
            seconds = int(expiry)
        except (TypeError, ValueError, OverflowError):
            raise DemoError("US VTS invalid token expiry") from None
        if seconds <= 120:
            raise DemoError("US VTS invalid token expiry")
        self._token = token
        self._expires = now + timedelta(seconds=min(seconds, 86400) - 120)

    def _account(self):
        return {"CANO": self.credentials.account_no, "ACNT_PRDT_CD": self.credentials.product_code}

    def request(self, endpoint, tr_id, *, params, continuation=""):
        if (endpoint, tr_id) not in {
            ("inquire-balance", "VTTS3012R"), ("inquire-ccnl", "VTTS3035R"),
        } or continuation not in {"", "N"}:
            raise DemoError("Request is outside the read-only US VTS allowlist")
        if any(params.get(key) != value for key, value in self._account().items()):
            raise DemoError("US VTS account scope mismatch")
        self.authenticate()
        return self._http("GET", PREFIX + endpoint, params=params, headers={
            "authorization": f"Bearer {self._token}", "appkey": self.credentials.app_key,
            "appsecret": self.credentials.app_secret, "tr_id": tr_id,
            "custtype": "P", "content-type": "application/json", "tr_cont": continuation,
        })

    def _pages(self, endpoint, tr_id, params, *, field):
        rows, totals, seen, continuation = [], None, set(), ""
        for _ in range(20):
            payload, headers = self.request(endpoint, tr_id, params=params, continuation=continuation)
            if str(payload.get("rt_cd")) != "0":
                raise DemoError("US VTS read rejected")
            rows.extend(_rows(payload.get(field)))
            if endpoint == "inquire-balance":
                value = payload.get("output2")
                if not isinstance(value, (dict, list)) or not value:
                    raise DemoError("US VTS missing balance totals")
                if isinstance(value, list) and any(not isinstance(row, dict) for row in value):
                    raise DemoError("US VTS invalid balance totals")
                totals = value
            flag = next((str(v).strip() for k, v in headers.items() if k.lower() == "tr_cont"), "")
            if flag not in {"", "D", "E", "M", "F"}:
                raise DemoError("US VTS unknown continuation state")
            if flag not in {"M", "F"}:
                return rows, totals
            cursor = (payload.get("ctx_area_fk200"), payload.get("ctx_area_nk200"))
            if any(not isinstance(value, str) for value in cursor) or not any(value.strip() for value in cursor) or cursor in seen:
                raise DemoError("US VTS pagination incomplete")
            seen.add(cursor)
            params = {**params, "CTX_AREA_FK200": cursor[0], "CTX_AREA_NK200": cursor[1]}
            continuation = "N"
        raise DemoError("US VTS pagination limit reached")

    def balance(self, exchange):
        if exchange not in EXCHANGES:
            raise DemoError("Explicit supported US mock exchange required")
        return self._pages("inquire-balance", "VTTS3012R", {
            **self._account(), "OVRS_EXCG_CD": exchange, "TR_CRCY_CD": "USD",
            "CTX_AREA_FK200": "", "CTX_AREA_NK200": "",
        }, field="output1")

    def orders(self, trade_date):
        requested = _date(trade_date)
        if requested > self._now().astimezone(NEW_YORK).date():
            raise DemoError("Future US order date is not allowed")
        rows, _ = self._pages("inquire-ccnl", "VTTS3035R", {
            **self._account(), "PDNO": "", "ORD_STRT_DT": trade_date,
            "ORD_END_DT": trade_date, "SLL_BUY_DVSN": "00", "CCLD_NCCS_DVSN": "00",
            "OVRS_EXCG_CD": "", "SORT_SQN": "DS", "ORD_DT": "",
            "ORD_GNO_BRNO": "", "ODNO": "", "CTX_AREA_FK200": "", "CTX_AREA_NK200": "",
        }, field="output")
        selected = []
        now = self._now()
        for row in rows:
            # Mock endpoint cannot filter by exchange; never count foreign rows
            # as US evidence. Unknown exchanges fail rather than guess.
            if row.get("ovrs_excg_cd") not in EXCHANGES:
                raise DemoError("US VTS order exchange cannot be verified")
            if _date(row.get("ord_dt")) != requested:
                raise DemoError("US VTS order is outside requested date")
            _date(row.get("dmst_ord_dt"))
            clock = row.get("thco_ord_tmd")
            if not isinstance(clock, str) or not re.fullmatch(r"[0-9]{6}", clock):
                raise DemoError("US VTS order observation time cannot be verified")
            try:
                domestic = datetime.strptime(row["dmst_ord_dt"] + clock, "%Y%m%d%H%M%S").replace(tzinfo=SEOUL)
            except ValueError:
                raise DemoError("US VTS invalid order time") from None
            if domestic > now or domestic.astimezone(NEW_YORK).date() != requested:
                raise DemoError("US VTS future or inconsistent order time")
            selected.append(row)
        return selected
