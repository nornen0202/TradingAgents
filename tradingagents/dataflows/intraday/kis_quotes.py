from __future__ import annotations

from datetime import datetime
import math
from zoneinfo import ZoneInfo

from tradingagents.portfolio.instrument_identity import resolve_identity
from tradingagents.portfolio.kis import KisClient
from tradingagents.scheduled.market_calendar import market_session_state
from tradingagents.schemas import IntradayMarketSnapshot

from ..vendor_exceptions import VendorUnavailableError


class KISQuoteProvider:
    name = "kis_quote"
    realtime_capable = True

    def fetch(
        self,
        ticker: str,
        *,
        interval: str = "5m",
        market_timezone: str = "Asia/Seoul",
        checkpoint_id: str | None = None,
    ) -> IntradayMarketSnapshot:
        from .providers import require_live_intraday_clock

        require_live_intraday_clock(market_timezone, provider_name=getattr(self, "name", "kis"))
        identity = resolve_identity(ticker)
        code = identity.krx_code or identity.broker_symbol or ticker.split(".")[0]
        if not code or not str(code).isdigit():
            raise RuntimeError(f"KIS quote provider requires a domestic KR code, got {ticker!r}.")

        client = KisClient.from_api_keys(environment="real")
        payload, _headers = client.request_json(
            method="GET",
            path="/uapi/domestic-stock/v1/quotations/inquire-price",
            tr_id="FHKST01010100",
            params={
                "FID_COND_MRKT_DIV_CODE": "J",
                "FID_INPUT_ISCD": str(code).zfill(6),
            },
        )
        output = payload.get("output") or {}
        now = datetime.now(ZoneInfo(market_timezone))
        day = str(output.get("stck_bsop_date") or "").strip()
        clock = str(output.get("stck_cntg_hour") or "").strip()
        try:
            if len(day) != 8 or len(clock) != 6:
                raise ValueError("Missing date or time")
            asof = datetime.strptime(day + clock, "%Y%m%d%H%M%S").replace(tzinfo=ZoneInfo("Asia/Seoul"))
        except ValueError as exc:
            raise VendorUnavailableError("KIS quote response omitted a verifiable trade date or time.") from exc
        if asof > now:
            raise VendorUnavailableError("KIS quote timestamp is after receipt.")
        last_price = _to_float(output.get("stck_prpr"))
        if last_price is None or last_price <= 0:
            raise RuntimeError(f"KIS quote response did not include a usable price for {ticker}.")

        day_high = _to_float(output.get("stck_hgpr")) or last_price
        day_low = _to_float(output.get("stck_lwpr")) or last_price
        volume = int(_to_float(output.get("acml_vol")) or 0)

        return IntradayMarketSnapshot(
            ticker=ticker,
            asof=asof.isoformat(),
            provider=self.name,
            interval=interval,
            last_price=last_price,
            session_vwap=None,
            day_high=day_high,
            day_low=day_low,
            volume=volume,
            avg20_daily_volume=None,
            relative_volume=None,
            provider_timestamp=asof.isoformat(),
            quote_delay_seconds=math.ceil((now - asof).total_seconds()),
            provider_realtime_capable=self.realtime_capable,
            market_session=market_session_state(market="KR", now_local=now)["phase"],
            market="KR",
            exchange="KRX",
            checkpoint_id=checkpoint_id,
        )


def _to_float(value: object) -> float | None:
    text = str(value or "").replace(",", "").strip()
    if not text:
        return None
    try:
        number = float(text)
        return number if math.isfinite(number) else None
    except ValueError:
        return None

