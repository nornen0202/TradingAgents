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
    DEMO_HOST, DemoCredentials, DemoError, DemoNotSentError, _assert_no_http_retries, _pacer,
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
            raise DemoNotSentError("Aware observation clock required")
        return value.astimezone(timezone.utc)

    def _http(self, method, path, *, not_before=None, **kwargs):
        if (method, path) not in {
            ("POST", "/oauth2/tokenP"),
            ("GET", PREFIX + "inquire-balance"),
            ("GET", PREFIX + "inquire-ccnl"),
        }:
            raise DemoError("Request is outside the read-only US VTS allowlist")
        _assert_no_http_retries(self.session)
        started = self._now()
        if not_before is not None and started < not_before:
            raise DemoNotSentError("US VTS clock regressed before transport")
        self.pacer.wait()
        sent_at = self._now()
        if sent_at < started:
            raise DemoNotSentError("US VTS clock regressed during pacing")
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
            try:
                received_at = self._now()
            except DemoNotSentError:
                raise DemoError("US VTS response clock unavailable after transport") from None
            if received_at < sent_at:
                raise DemoError("US VTS clock regressed during response")
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
        started = self._now()
        self.authenticate()
        return self._http("GET", PREFIX + endpoint, params=params, not_before=started, headers={
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


class KisDemoUSClient(KisDemoUSReadClient):
    """Dedicated VTS writes; the separate read client remains incapable of writes.

    Explicit US sell VTS ID follows the official API description/legacy example,
    not the newer sample's generic leading-character replacement (1006 != 1001).
    """
    def _http(self, method, path, *, deadline=None, not_before=None, **kwargs):
        allowed = {("POST", "/oauth2/tokenP"),
                   *( ("GET", PREFIX + endpoint) for endpoint in
                      ("inquire-balance", "inquire-ccnl", "inquire-psamount") ),
                   ("POST", PREFIX + "order"), ("POST", PREFIX + "order-rvsecncl")}
        if (method, path) not in allowed:
            raise DemoNotSentError("Request is outside the US VTS allowlist")
        _assert_no_http_retries(self.session)
        started = self._now()
        if not_before is not None and started < not_before:
            raise DemoNotSentError("US VTS clock regressed before transport")
        self.pacer.wait()
        sent_at = self._now()
        if sent_at < started:
            raise DemoNotSentError("US VTS clock regressed during pacing")
        if deadline is not None:
            from .paper import stamp
            if sent_at >= stamp(deadline):
                raise DemoNotSentError("US VTS request deadline elapsed before sending")
        try:
            response = self.session.request(method, DEMO_HOST + path, timeout=self.timeout,
                                           allow_redirects=False, **kwargs)
            if not 200 <= response.status_code < 300:
                raise DemoError("US VTS HTTP response rejected")
            payload = response.json()
            if not isinstance(payload, dict):
                raise DemoError("US VTS invalid response")
            try:
                received_at = self._now()
            except DemoNotSentError:
                raise DemoError("US VTS response clock unavailable after transport") from None
            if received_at < sent_at:
                raise DemoError("US VTS clock regressed during response")
            return payload, response.headers
        except (requests.RequestException, ValueError):
            raise DemoError("US VTS response unavailable or invalid") from None

    def request(self, *args, params=None, body=None, continuation="", deadline=None, not_before=None):
        # Existing complete read pagination uses the two-argument form; the
        # shared durable journal uses the explicit method form for writes.
        if len(args) == 2:
            method, endpoint, tr_id = "GET", *args
        elif len(args) == 3:
            method, endpoint, tr_id = args
        else:
            raise DemoNotSentError("Explicit US VTS method and endpoint required")
        allowed = {("GET", "inquire-balance", "VTTS3012R"),
                   ("GET", "inquire-ccnl", "VTTS3035R"),
                   ("GET", "inquire-psamount", "VTTS3007R"),
                   ("POST", "order", "VTTT1002U"), ("POST", "order", "VTTT1001U"),
                   ("POST", "order-rvsecncl", "VTTT1004U")}
        if (method, endpoint, tr_id) not in allowed or continuation not in {"", "N"}:
            raise DemoNotSentError("Request is outside the US VTS allowlist")
        supplied = body if body is not None else params or {}
        if any(supplied.get(key) != value for key, value in self._account().items()):
            raise DemoNotSentError("US VTS account scope mismatch")
        if method == "POST" and (supplied.get("OVRS_EXCG_CD") not in EXCHANGES
                or supplied.get("ORD_SVR_DVSN_CD") != "0"
                or (endpoint == "order" and supplied.get("ORD_DVSN") != "00")
                or (endpoint == "order-rvsecncl" and
                    (supplied.get("RVSE_CNCL_DVSN_CD") != "02" or supplied.get("OVRS_ORD_UNPR") != "0"))):
            raise DemoNotSentError("US VTS permits regular US limit orders and cancellations only")
        started = self._now()
        if not_before is not None:
            from .paper import stamp
            if started < stamp(not_before):
                raise DemoNotSentError("US VTS clock regressed since intent validation")
        try:
            self.authenticate()
        except DemoError:
            raise DemoNotSentError("US VTS authentication failed before sending request") from None
        if self._now() < started:
            raise DemoNotSentError("US VTS clock regressed during authentication")
        return self._http(method, PREFIX + endpoint, params=params, json=body, deadline=deadline, not_before=started,
                          headers={"authorization": f"Bearer {self._token}",
                                   "appkey": self.credentials.app_key, "appsecret": self.credentials.app_secret,
                                   "tr_id": tr_id, "custtype": "P", "content-type": "application/json",
                                   "tr_cont": continuation})

    def buying_power(self, *, ticker, exchange, limit_price):
        from .kis_paper_us import _price, _instrument
        _instrument(ticker, exchange)
        price = _price(limit_price)
        payload, headers = self.request("GET", "inquire-psamount", "VTTS3007R", params={
            **self._account(), "OVRS_EXCG_CD": exchange, "OVRS_ORD_UNPR": price, "ITEM_CD": ticker})
        flag = next((str(v).strip() for k, v in headers.items() if k.lower() == "tr_cont"), "")
        if (str(payload.get("rt_cd")) != "0" or not isinstance(payload.get("output"), dict)
                or flag not in {"", "D", "E"}):
            raise DemoError("US VTS complete buying capacity unavailable")
        return payload["output"]
