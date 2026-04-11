from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests

from tradingagents.dataflows.api_keys import get_api_key

from .account_models import AccountSnapshot, PendingOrder, PortfolioProfile, Position
from .instrument_identity import resolve_identity


REAL_BASE_URL = "https://openapi.koreainvestment.com:9443"
DEMO_BASE_URL = "https://openapivts.koreainvestment.com:29443"


class PortfolioConfigurationError(ValueError):
    """Raised when account portfolio configuration is incomplete."""


class KisApiError(RuntimeError):
    """Raised when KIS returns an API error."""


class KisClient:
    def __init__(
        self,
        *,
        app_key: str,
        app_secret: str,
        environment: str = "real",
        session: requests.Session | None = None,
        timeout_seconds: float = 15.0,
        token_ttl_seconds_default: int | None = None,
        token_refresh_skew_seconds: int | None = None,
        token_file_cache_enabled: bool | None = None,
        token_cache_path: str | Path | None = None,
    ) -> None:
        self.app_key = app_key
        self.app_secret = app_secret
        self.environment = "demo" if environment == "demo" else "real"
        self.base_url = DEMO_BASE_URL if self.environment == "demo" else REAL_BASE_URL
        self.session = session or requests.Session()
        self.timeout_seconds = timeout_seconds
        self._access_token: str | None = None
        self._token_expires_at: datetime | None = None
        self._token_ttl_seconds_default = max(
            60,
            int(token_ttl_seconds_default or os.getenv("KIS_TOKEN_TTL_SECONDS_DEFAULT", "86400")),
        )
        self._token_refresh_skew_seconds = max(
            0,
            int(token_refresh_skew_seconds or os.getenv("KIS_TOKEN_REFRESH_SKEW_SECONDS", "1200")),
        )
        self._token_file_cache_enabled = (
            _read_bool_env("KIS_TOKEN_FILE_CACHE_ENABLED", default=True)
            if token_file_cache_enabled is None
            else bool(token_file_cache_enabled)
        )
        self._token_cache_path = (
            Path(token_cache_path).expanduser()
            if token_cache_path
            else _default_token_cache_path(environment=self.environment, app_key=self.app_key)
        )

    @classmethod
    def from_api_keys(cls, *, environment: str = "real") -> "KisClient":
        app_key = get_api_key("KIS_APP_KEY")
        app_secret = get_api_key("KIS_APP_SECRET")
        if not app_key or not app_secret:
            raise PortfolioConfigurationError(
                "KIS app credentials are missing. Configure KIS_APP_KEY/KIS_APP_SECRET "
                "or KIS_Developers_APP_KEY/KIS_Developers_APP_SECRET."
            )
        return cls(app_key=app_key, app_secret=app_secret, environment=environment)

    def issue_access_token(self, *, force: bool = False) -> str:
        if not force:
            cached = self._load_cached_token()
            if cached:
                return cached

        response = self.session.post(
            f"{self.base_url}/oauth2/tokenP",
            headers={"content-type": "application/json"},
            data=json.dumps(
                {
                    "grant_type": "client_credentials",
                    "appkey": self.app_key,
                    "appsecret": self.app_secret,
                }
            ),
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        token = str(payload.get("access_token") or "").strip()
        if not token:
            raise KisApiError(f"KIS token response did not include access_token: {payload}")
        expires_in = _parse_positive_int(payload.get("expires_in"), default=self._token_ttl_seconds_default)
        now = datetime.now(timezone.utc)
        self._access_token = token
        self._token_expires_at = now + timedelta(seconds=expires_in)
        self._save_cached_token()
        return token

    def ensure_access_token(self) -> str:
        if self._is_token_usable():
            return self._access_token or self.issue_access_token(force=True)

        cached = self._load_cached_token()
        if cached:
            return cached

        return self.issue_access_token(force=True)

    def invalidate_access_token(self) -> None:
        self._access_token = None
        self._token_expires_at = None

    def request_json(
        self,
        *,
        method: str,
        path: str,
        tr_id: str,
        params: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        tr_cont: str = "",
    ) -> tuple[dict[str, Any], requests.structures.CaseInsensitiveDict[str]]:
        url = f"{self.base_url}{path}"
        for attempt in range(2):
            headers = {
                "content-type": "application/json",
                "authorization": f"Bearer {self.ensure_access_token()}",
                "appkey": self.app_key,
                "appsecret": self.app_secret,
                "tr_id": tr_id,
                "custtype": "P",
                "tr_cont": tr_cont,
            }
            response = self.session.request(
                method=method.upper(),
                url=url,
                headers=headers,
                params=params,
                json=body,
                timeout=self.timeout_seconds,
            )
            if response.status_code == 401 and attempt == 0:
                self.invalidate_access_token()
                self.issue_access_token(force=True)
                continue

            response.raise_for_status()
            payload = response.json()
            rt_cd = str(payload.get("rt_cd", "0"))
            if rt_cd not in {"0", ""}:
                if attempt == 0 and _looks_like_auth_error(payload):
                    self.invalidate_access_token()
                    self.issue_access_token(force=True)
                    continue
                raise KisApiError(
                    f"KIS API error for {path}: {payload.get('msg_cd')} {payload.get('msg1')}"
                )
            return payload, response.headers

        raise KisApiError(f"KIS API authentication retry exhausted for path: {path}")

    def _is_token_usable(self) -> bool:
        if not self._access_token or not self._token_expires_at:
            return False
        refresh_at = self._token_expires_at - timedelta(seconds=self._token_refresh_skew_seconds)
        return datetime.now(timezone.utc) < refresh_at

    def _load_cached_token(self) -> str | None:
        if not self._token_file_cache_enabled or not self._token_cache_path.exists():
            return None
        try:
            payload = json.loads(self._token_cache_path.read_text(encoding="utf-8"))
            token = str(payload.get("access_token") or "").strip()
            expires_at_raw = str(payload.get("expires_at") or "").strip()
            if not token or not expires_at_raw:
                return None
            expires_at = datetime.fromisoformat(expires_at_raw)
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            self._access_token = token
            self._token_expires_at = expires_at.astimezone(timezone.utc)
            if not self._is_token_usable():
                return None
            return token
        except Exception:
            return None

    def _save_cached_token(self) -> None:
        if (
            not self._token_file_cache_enabled
            or not self._access_token
            or self._token_expires_at is None
        ):
            return
        payload = {
            "access_token": self._access_token,
            "expires_at": self._token_expires_at.astimezone(timezone.utc).isoformat(),
            "issued_at": datetime.now(timezone.utc).isoformat(),
            "source": "api",
        }
        try:
            self._token_cache_path.parent.mkdir(parents=True, exist_ok=True)
            self._token_cache_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            os.chmod(self._token_cache_path, 0o600)
        except Exception:
            return

    def fetch_balance(self, *, account_no: str, product_code: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        tr_id = "VTTC8434R" if self.environment == "demo" else "TTTC8434R"
        params = {
            "CANO": account_no,
            "ACNT_PRDT_CD": product_code,
            "AFHR_FLPR_YN": "N",
            "OFL_YN": "",
            "INQR_DVSN": "01",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": "00",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": "",
        }
        positions: list[dict[str, Any]] = []
        summary: dict[str, Any] = {}
        tr_cont = ""

        while True:
            payload, headers = self.request_json(
                method="GET",
                path="/uapi/domestic-stock/v1/trading/inquire-balance",
                tr_id=tr_id,
                params=params,
                tr_cont=tr_cont,
            )
            positions.extend(payload.get("output1") or [])
            output2 = payload.get("output2") or []
            if isinstance(output2, list) and output2:
                summary = output2[0]
            elif isinstance(output2, dict):
                summary = output2
            tr_cont_header = str(headers.get("tr_cont") or "")
            next_fk = str(payload.get("ctx_area_fk100") or "")
            next_nk = str(payload.get("ctx_area_nk100") or "")
            if tr_cont_header not in {"M", "F"}:
                break
            params["CTX_AREA_FK100"] = next_fk
            params["CTX_AREA_NK100"] = next_nk
            tr_cont = "N"

        return positions, summary

    def fetch_pending_orders(
        self,
        *,
        account_no: str,
        product_code: str,
        query_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        current = (query_date or datetime.now()).strftime("%Y%m%d")
        tr_id = "VTTC0081R" if self.environment == "demo" else "TTTC0081R"
        params = {
            "CANO": account_no,
            "ACNT_PRDT_CD": product_code,
            "INQR_STRT_DT": current,
            "INQR_END_DT": current,
            "SLL_BUY_DVSN_CD": "00",
            "PDNO": "",
            "CCLD_DVSN": "02",
            "INQR_DVSN": "00",
            "INQR_DVSN_3": "00",
            "ORD_GNO_BRNO": "",
            "ODNO": "",
            "INQR_DVSN_1": "",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": "",
            "EXCG_ID_DVSN_CD": "KRX",
        }
        orders: list[dict[str, Any]] = []
        tr_cont = ""

        while True:
            payload, headers = self.request_json(
                method="GET",
                path="/uapi/domestic-stock/v1/trading/inquire-daily-ccld",
                tr_id=tr_id,
                params=params,
                tr_cont=tr_cont,
            )
            orders.extend(payload.get("output1") or [])
            tr_cont_header = str(headers.get("tr_cont") or "")
            next_fk = str(payload.get("ctx_area_fk100") or "")
            next_nk = str(payload.get("ctx_area_nk100") or "")
            if tr_cont_header not in {"M", "F"}:
                break
            params["CTX_AREA_FK100"] = next_fk
            params["CTX_AREA_NK100"] = next_nk
            tr_cont = "N"

        return orders


def validate_kis_credentials(
    *,
    require_account: bool = False,
    account_no: str | None = None,
    product_code: str | None = None,
) -> dict[str, Any]:
    client = KisClient.from_api_keys()
    token = client.issue_access_token()
    result = {
        "environment": client.environment,
        "token_issued": bool(token),
    }
    if require_account:
        acct = account_no or get_api_key("KIS_ACCOUNT_NO")
        prod = product_code or get_api_key("KIS_PRODUCT_CODE") or "01"
        if not acct:
            raise PortfolioConfigurationError("KIS account number is required for account snapshot validation.")
        positions, summary = client.fetch_balance(account_no=acct, product_code=prod)
        result["positions_count"] = len(positions)
        result["summary_fields"] = sorted(summary.keys())
    return result


def load_account_snapshot_from_kis(profile: PortfolioProfile) -> AccountSnapshot:
    if not profile.account_no:
        raise PortfolioConfigurationError(
            "Portfolio profile is missing account_no. Add it to config/portfolio_profiles.toml "
            "or provide KIS_ACCOUNT_NO / KIS_Developers_ACCOUNT_NO."
        )
    if not profile.product_code:
        raise PortfolioConfigurationError("Portfolio profile is missing product_code.")

    client = KisClient.from_api_keys(environment=profile.broker_environment)
    now = datetime.now().astimezone()
    positions_payload, summary_payload = client.fetch_balance(
        account_no=profile.account_no,
        product_code=profile.product_code,
    )
    pending_payload = client.fetch_pending_orders(
        account_no=profile.account_no,
        product_code=profile.product_code,
        query_date=now,
    )

    positions: list[Position] = []
    warnings: list[str] = []
    for item in positions_payload:
        broker_symbol = str(item.get("pdno") or "").strip()
        holding_qty = float(item.get("hldg_qty", 0) or 0)
        if not broker_symbol:
            continue
        try:
            identity = resolve_identity(broker_symbol, str(item.get("prdt_name") or "").strip() or None)
        except Exception:
            warnings.append(f"Could not resolve broker symbol '{broker_symbol}'.")
            continue
        positions.append(
            Position(
                broker_symbol=broker_symbol,
                canonical_ticker=identity.canonical_ticker,
                display_name=identity.display_name,
                sector=None,
                quantity=holding_qty,
                available_qty=float(item.get("ord_psbl_qty", holding_qty) or holding_qty),
                avg_cost_krw=int(float(item.get("pchs_avg_pric", 0) or 0)),
                market_price_krw=int(float(item.get("prpr", 0) or 0)),
                market_value_krw=int(float(item.get("evlu_amt", 0) or 0)),
                unrealized_pnl_krw=int(float(item.get("evlu_pfls_amt", 0) or 0)),
            )
        )

    pending_orders: list[PendingOrder] = []
    for item in pending_payload:
        broker_symbol = str(item.get("pdno") or "").strip()
        identity_ticker = None
        if broker_symbol:
            try:
                identity_ticker = resolve_identity(
                    broker_symbol,
                    str(item.get("prdt_name") or "").strip() or None,
                ).canonical_ticker
            except Exception:
                identity_ticker = None
        pending_orders.append(
            PendingOrder(
                broker_order_id=str(item.get("odno") or ""),
                broker_symbol=broker_symbol,
                canonical_ticker=identity_ticker,
                side="buy" if str(item.get("sll_buy_dvsn_cd") or "") == "02" else "sell",
                qty=float(item.get("ord_qty", item.get("tot_ccld_qty", 0)) or 0),
                remaining_qty=float(item.get("nccs_qty", item.get("rmn_qty", 0)) or 0),
                status=str(item.get("ord_stat_name") or item.get("ccld_dvsn_name") or "open"),
            )
        )

    positions_market_value = sum(position.market_value_krw for position in positions)
    cash_snapshot = _extract_cash_snapshot(
        summary_payload=summary_payload,
        positions_market_value=positions_market_value,
        profile=profile,
    )
    warnings.extend(cash_snapshot["warnings"])

    return AccountSnapshot(
        snapshot_id=f"{now.strftime('%Y%m%dT%H%M%S')}_kis_{profile.account_no}-{profile.product_code}",
        as_of=now.isoformat(),
        broker="kis",
        account_id=f"{profile.account_no}-{profile.product_code}",
        currency="KRW",
        settled_cash_krw=int(cash_snapshot["settled_cash_krw"]),
        available_cash_krw=int(cash_snapshot["available_cash_krw"]),
        buying_power_krw=int(cash_snapshot["buying_power_krw"]),
        total_equity_krw=int(cash_snapshot["total_equity_krw"]),
        snapshot_health=str(cash_snapshot["snapshot_health"]),
        cash_diagnostics=dict(cash_snapshot["cash_diagnostics"]),
        pending_orders=tuple(pending_orders),
        positions=tuple(positions),
        constraints=profile.constraints,
        warnings=tuple(warnings),
    )


def _parse_positive_int(value: object, *, default: int) -> int:
    try:
        parsed = int(value)
        return parsed if parsed > 0 else default
    except (TypeError, ValueError):
        return default


def _read_bool_env(name: str, *, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() not in {"0", "false", "no", "off"}


def _default_token_cache_path(*, environment: str, app_key: str) -> Path:
    key_prefix = (app_key or "unknown").strip()[:8] or "unknown"
    return Path.home() / ".cache" / "tradingagents" / f"kis_token_{environment}_{key_prefix}.json"


def _looks_like_auth_error(payload: dict[str, Any]) -> bool:
    message = f"{payload.get('msg_cd', '')} {payload.get('msg1', '')}".lower()
    auth_markers = ("auth", "token", "access", "expired", "만료", "토큰", "인증")
    return any(marker in message for marker in auth_markers)


def _extract_cash_snapshot(
    *,
    summary_payload: dict[str, Any],
    positions_market_value: int,
    profile: PortfolioProfile,
) -> dict[str, Any]:
    cash_fields = _parse_numeric_fields(
        summary_payload,
        {
            "dnca_tot_amt",
            "ord_psbl_amt",
            "ord_psbl_cash",
            "buy_psbl_amt",
            "buy_psbl_cash",
            "tot_evlu_amt",
            "nass_amt",
            "tot_asst_amt",
        },
    )
    settled_cash = _first_numeric(summary_payload, ("dnca_tot_amt", "ord_psbl_cash", "ord_psbl_amt")) or 0
    available_cash = _first_numeric(
        summary_payload,
        ("ord_psbl_cash", "ord_psbl_amt", "buy_psbl_cash", "buy_psbl_amt", "dnca_tot_amt"),
    ) or settled_cash
    buying_power = _first_numeric(
        summary_payload,
        ("buy_psbl_amt", "buy_psbl_cash", "ord_psbl_amt", "ord_psbl_cash", "dnca_tot_amt"),
    ) or available_cash
    reported_equity = _first_numeric(summary_payload, ("tot_evlu_amt", "nass_amt", "tot_asst_amt"))
    total_equity = max(
        int(reported_equity or 0),
        int(positions_market_value + max(settled_cash, available_cash, buying_power, 0)),
    )

    snapshot_health = "VALID"
    warnings: list[str] = []
    if not summary_payload:
        snapshot_health = "INVALID_SNAPSHOT"
        warnings.append("KIS balance summary payload was empty.")
    elif not cash_fields and positions_market_value == 0:
        snapshot_health = "INVALID_SNAPSHOT"
        warnings.append("Could not parse numeric cash or equity fields from KIS balance summary.")
    elif positions_market_value == 0 and max(available_cash, buying_power, settled_cash) < profile.constraints.min_trade_krw:
        snapshot_health = "WATCHLIST_ONLY"
        warnings.append(
            "Account snapshot has no positions and insufficient cash for the configured minimum trade; portfolio output is watchlist-only."
        )
    elif max(available_cash, buying_power) < profile.constraints.min_trade_krw:
        snapshot_health = "CAPITAL_CONSTRAINED"
        warnings.append("Account snapshot has insufficient deployable cash for the configured minimum trade.")

    if reported_equity is None:
        warnings.append("KIS summary did not expose a trusted total-equity field; account value fell back to cash plus positions.")

    return {
        "settled_cash_krw": int(settled_cash),
        "available_cash_krw": int(available_cash),
        "buying_power_krw": int(buying_power),
        "total_equity_krw": int(total_equity),
        "snapshot_health": snapshot_health,
        "warnings": warnings,
        "cash_diagnostics": {
            "summary_fields_present": sorted(summary_payload.keys()),
            "parsed_numeric_fields": cash_fields,
            "positions_market_value_krw": int(positions_market_value),
            "selected_fields": {
                "settled_cash": _selected_field(summary_payload, ("dnca_tot_amt", "ord_psbl_cash", "ord_psbl_amt")),
                "available_cash": _selected_field(
                    summary_payload,
                    ("ord_psbl_cash", "ord_psbl_amt", "buy_psbl_cash", "buy_psbl_amt", "dnca_tot_amt"),
                ),
                "buying_power": _selected_field(
                    summary_payload,
                    ("buy_psbl_amt", "buy_psbl_cash", "ord_psbl_amt", "ord_psbl_cash", "dnca_tot_amt"),
                ),
                "total_equity": _selected_field(summary_payload, ("tot_evlu_amt", "nass_amt", "tot_asst_amt")),
            },
        },
    }


def _parse_numeric_fields(payload: dict[str, Any], allowed_keys: set[str]) -> dict[str, int]:
    parsed: dict[str, int] = {}
    for key, value in payload.items():
        if key not in allowed_keys:
            continue
        numeric = _maybe_int(value)
        if numeric is None:
            continue
        parsed[key] = numeric
    return parsed


def _selected_field(payload: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    for key in keys:
        if _maybe_int(payload.get(key)) is not None:
            return key
    return None


def _first_numeric(payload: dict[str, Any], keys: tuple[str, ...]) -> int | None:
    for key in keys:
        numeric = _maybe_int(payload.get(key))
        if numeric is not None:
            return numeric
    return None


def _maybe_int(value: object) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None
