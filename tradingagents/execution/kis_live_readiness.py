"""Offline contract for explicitly approved KIS production order plans.

This does not register a broker or accept credentials. The existing dispatcher
continues to reject live routing, including plans that pass this fixture gate.
"""
from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
from zoneinfo import ZoneInfo

from tradingagents.atomic_io import atomic_write_json, interprocess_file_lock
from tradingagents.charting.bars import instant
from tradingagents.portfolio.kis import REAL_BASE_URL
from .broker_adapter import Account, Intent, _money
from .kis_strategy_limits import CAPS


MODE = "KIS_LIVE_READINESS"
SCHEMA = "tradingagents.kis-live-readiness/v1"
_DESTINATIONS = {
    "KR": ("/uapi/domestic-stock/v1/trading/order-cash", {"BUY": "TTTC0012U", "SELL": "TTTC0011U"}),
    "US": ("/uapi/overseas-stock/v1/trading/order", {"BUY": "TTTT1002U", "SELL": "TTTT1006U"}),
}


@dataclass(frozen=True)
class MarketUsage:
    session_date: str
    orders: int
    buy_notional: str
    unresolved: bool


def _admit(state, config, intent, account, usage, quote, session, now):
    approved = instant(config.get("approved_at"))
    expires = instant(config.get("expires_at"))
    if (config.get("schema") != SCHEMA or config.get("mode") != MODE or config.get("enabled") is not True
            or config.get("environment") != "real" or config.get("real_orders_enabled") is not False
            or config.get("evidence_scope") != "ISOLATED_FIXTURE" or config.get("host") != REAL_BASE_URL
            or approved is None or expires is None or not approved <= now < expires
            or config.get("revoked") is not False or (state / "HALT").exists()):
        raise ValueError("LIVE_FIXTURE_APPROVAL_REQUIRED")

    scope = config.get("account_scope")
    if (not isinstance(scope, str) or not re.fullmatch(r"fixture:[a-f0-9]{64}", scope)
            or not isinstance(account, Account) or account.scope != scope or not isinstance(intent, Intent)):
        raise ValueError("LIVE_ACCOUNT_SCOPE_UNVERIFIED")
    market = config.get("market")
    currency = {"KR": "KRW", "US": "USD"}.get(market)
    allowed = config.get("allowed_instruments")
    venue = allowed.get(intent.ticker) if isinstance(allowed, dict) else None
    if (currency is None or account.currency != currency or intent.currency != currency
            or not isinstance(intent.id, str) or not re.fullmatch(r"[A-Za-z0-9:_-]{1,128}", intent.id)
            or intent.side not in {"BUY", "SELL"} or not isinstance(intent.ticker, str)
            or (market == "KR" and (venue != "KRX" or not re.fullmatch(r"\d{6}", intent.ticker)))
            or (market == "US" and (venue not in {"NASD", "NYSE", "AMEX"} or not re.fullmatch(r"[A-Z][A-Z0-9.]{0,14}", intent.ticker)))):
        raise ValueError("LIVE_INSTRUMENT_NOT_APPROVED")

    opening, closing = instant(session.get("session_open")), instant(session.get("session_close"))
    market_zone = ZoneInfo("Asia/Seoul" if market == "KR" else "America/New_York")
    exchange_date = now.astimezone(market_zone).date().isoformat()
    if (session.get("source") != "exchange_calendars" or session.get("is_open") is not True
            or session.get("phase") != "regular" or opening is None or closing is None
            or not opening + timedelta(minutes=2) <= now < closing - timedelta(minutes=10)
            or not isinstance(usage, MarketUsage) or usage.session_date != exchange_date
            or opening.astimezone(market_zone).date().isoformat() != exchange_date
            or usage.unresolved is not False):
        raise ValueError("LIVE_SESSION_OR_RECONCILIATION_UNVERIFIED")

    deadline = instant(intent.expires_at)
    account_at, quote_at = instant(account.observed_at), instant(quote.get("observed_at"))
    if (deadline is None or now >= deadline or account_at is None or quote_at is None
            or not timedelta(0) <= now - account_at < timedelta(seconds=120)
            or not opening <= quote_at <= now < quote_at + timedelta(seconds=120)
            or quote.get("currency") != currency or quote.get("ticker") != intent.ticker
            or quote.get("exchange") != venue or quote.get("execution_ready") is not True):
        raise ValueError("LIVE_ORDER_INPUT_UNVERIFIED")

    quantity, limit = _money(intent.quantity), _money(intent.limit)
    amount = quantity * limit
    price = _money(quote.get("ask" if intent.side == "BUY" else "bid"))
    cap, daily = _money(config.get("max_order_native")), _money(config.get("max_daily_buy_native"))
    maximum = config.get("max_daily_orders")
    precision = Decimal("1") if market == "KR" else Decimal("0.01")
    if (quantity != quantity.to_integral_value() or not 0 < amount <= cap <= CAPS[market]
            or limit % precision or not 0 < cap <= daily <= CAPS[market] * 3
            or type(maximum) is not int or not 1 <= maximum <= 3
            or type(usage.orders) is not int or not 0 <= usage.orders < maximum
            or not price or abs(limit - price) > price * Decimal("0.01")):
        raise ValueError("LIVE_ORDER_LIMITS_EXCEEDED")
    if intent.side == "BUY":
        if (amount + _money(usage.buy_notional) > daily
                or amount * Decimal("1.003") > _money(account.settled_cash)):
            raise ValueError("LIVE_ORDER_CASH_EXCEEDED")
    elif quantity > _money(account.sellable.get(intent.ticker, "0")):
        raise ValueError("LIVE_ORDER_HOLDINGS_EXCEEDED")

    path, transaction_ids = _DESTINATIONS[market]
    body = {"CANO": "00000000", "ACNT_PRDT_CD": "01", "PDNO": intent.ticker,
            "ORD_DVSN": "00", "ORD_QTY": str(int(quantity))}
    if market == "KR":
        body.update(ORD_UNPR=f"{limit:.0f}", EXCG_ID_DVSN_CD=venue,
                    SLL_TYPE="01" if intent.side == "SELL" else "", CNDT_PRIC="")
    else:
        body.update(OVRS_EXCG_CD=venue, OVRS_ORD_UNPR=f"{limit:.2f}", CTAC_TLNO="", MGCO_APTM_ODNO="",
                    SLL_TYPE="00" if intent.side == "SELL" else "", ORD_SVR_DVSN_CD="0")
    return {"method": "POST", "host": REAL_BASE_URL, "path": path, "tr_id": transaction_ids[intent.side], "body": body}


def preview(state, intent, *, account, usage, quote, session, now):
    """Read the separately selected policy and audit a fixture request without I/O to KIS."""
    state = Path(state)
    if state.name != "kis-live-readiness" or instant(now) is None:
        raise ValueError("LIVE_FIXTURE_ROOT_REQUIRED")
    with interprocess_file_lock(state / "readiness.lock"):
        config_path = state / "approval.json"
        report = {"mode": MODE, "evidence_scope": "ISOLATED_FIXTURE", "recorded_at": instant(now).isoformat(),
                  "configuration_sha256": None, "live_order_requests": 0, "status": "BLOCKED"}
        try:
            raw = config_path.read_bytes() if config_path.is_file() else b"{}"
            report["configuration_sha256"] = hashlib.sha256(raw).hexdigest()
            config = json.loads(raw.decode("utf-8-sig"))
            request = _admit(state, config, intent, account, usage, quote, session, instant(now))
            report.update(status="CONTRACT_READY", tr_id=request["tr_id"])
        except (ArithmeticError, AttributeError, OSError, TypeError, ValueError) as exc:
            report["error_code"] = str(exc) if re.fullmatch(r"LIVE_[A-Z_]+", str(exc)) else "LIVE_INPUT_INVALID"
            raise ValueError(report["error_code"]) from None
        finally:
            # The audit stores the decision, never the selected account, symbol or terms.
            key = hashlib.sha256(json.dumps(report, sort_keys=True).encode()).hexdigest()
            atomic_write_json(state / "audit" / f"{key}.json", report)
        return {**report, "fixture_request": request}
