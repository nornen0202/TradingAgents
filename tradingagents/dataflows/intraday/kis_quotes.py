from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from tradingagents.portfolio.instrument_identity import resolve_identity
from tradingagents.portfolio.kis import KisClient
from tradingagents.schemas import IntradayMarketSnapshot


class KISQuoteProvider:
    name = "kis_quote"
    realtime_capable = True

    def fetch(
        self,
        ticker: str,
        *,
        interval: str = "5m",
        market_timezone: str = "Asia/Seoul",
    ) -> IntradayMarketSnapshot:
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
        last_price = _to_float(output.get("stck_prpr"))
        if last_price is None:
            raise RuntimeError(f"KIS quote response did not include a usable price for {ticker}.")

        day_high = _to_float(output.get("stck_hgpr")) or last_price
        day_low = _to_float(output.get("stck_lwpr")) or last_price
        volume = int(_to_float(output.get("acml_vol")) or 0)

        return IntradayMarketSnapshot(
            ticker=ticker,
            asof=now.isoformat(),
            provider=self.name,
            interval=interval,
            last_price=last_price,
            session_vwap=None,
            day_high=day_high,
            day_low=day_low,
            volume=volume,
            avg20_daily_volume=None,
            relative_volume=None,
            bar_timestamp=now.isoformat(),
            provider_timestamp=now.isoformat(),
            quote_delay_seconds=0,
            provider_realtime_capable=self.realtime_capable,
            market_session=_kr_market_session(now),
        )


def _to_float(value: object) -> float | None:
    text = str(value or "").replace(",", "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _kr_market_session(now: datetime) -> str:
    current = now.astimezone(ZoneInfo("Asia/Seoul")).time()
    if current.hour < 8:
        return "overnight"
    if (current.hour, current.minute) < (9, 0):
        return "pre_open"
    if (current.hour, current.minute) <= (15, 30):
        return "regular"
    return "post_close"

