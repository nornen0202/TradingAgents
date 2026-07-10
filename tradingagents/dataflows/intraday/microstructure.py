from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime, time, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

from tradingagents.dataflows.intraday_market import DELAYED_ANALYSIS_ONLY
from tradingagents.dataflows.intraday.us_microstructure_sources import (
    CompositeUSMicrostructureSupplementProvider,
)
from tradingagents.portfolio.instrument_identity import resolve_identity
from tradingagents.portfolio.kis import KisClient
from tradingagents.schemas import IntradayMarketSnapshot


_DEFAULT_SUPPLEMENT_PROVIDER = object()


class KISMicrostructureProvider:
    name = "kis_microstructure"
    realtime_capable = True

    def __init__(
        self,
        *,
        client: Any | None = None,
        client_factory: Callable[[], Any] | None = None,
        us_daily_volume_fallback: Callable[[str], float | None] | None = None,
        us_supplement_provider: Any = _DEFAULT_SUPPLEMENT_PROVIDER,
    ) -> None:
        self._client = client
        self._client_factory = client_factory or (lambda: KisClient.from_api_keys(environment="real"))
        self._us_daily_volume_fallback = us_daily_volume_fallback or _avg20_daily_volume_from_yfinance
        if us_supplement_provider is _DEFAULT_SUPPLEMENT_PROVIDER:
            self._us_supplement_provider = (
                None if client is not None else CompositeUSMicrostructureSupplementProvider.from_api_keys()
            )
        else:
            self._us_supplement_provider = us_supplement_provider

    def fetch(
        self,
        ticker: str,
        *,
        interval: str = "5m",
        market_timezone: str | None = None,
        checkpoint_id: str | None = None,
    ) -> IntradayMarketSnapshot:
        identity = resolve_identity(ticker)
        market = "KR" if (identity.country or "").upper() == "KR" or _looks_like_kr_symbol(ticker) else "US"
        if market == "KR":
            return self._fetch_kr(
                ticker=ticker,
                code=identity.krx_code or identity.broker_symbol or ticker.split(".", 1)[0],
                interval=interval,
                market_timezone=market_timezone or "Asia/Seoul",
                checkpoint_id=checkpoint_id,
            )
        return self._fetch_us(
            ticker=ticker,
            symbol=identity.broker_symbol or identity.yahoo_symbol or ticker,
            interval=interval,
            market_timezone=market_timezone or "America/New_York",
            checkpoint_id=checkpoint_id,
        )

    @property
    def _kis(self) -> Any:
        if self._client is None:
            self._client = self._client_factory()
        return self._client

    def _fetch_kr(
        self,
        *,
        ticker: str,
        code: str,
        interval: str,
        market_timezone: str,
        checkpoint_id: str | None,
    ) -> IntradayMarketSnapshot:
        now_local = datetime.now(ZoneInfo(market_timezone))
        now_utc = now_local.astimezone(timezone.utc)
        hour = now_local.strftime("%H%M%S")
        code = str(code).zfill(6)
        raw_source_names: list[str] = []
        missing: dict[str, str] = {}

        price = self._kis.domestic_price(code)
        raw_source_names.append("kis.domestic_price")
        price_row = _first_record(price, "output")

        bars = []
        chart = _call_optional(
            lambda: self._kis.domestic_time_itemchartprice(code, input_hour=hour, include_past_data="Y"),
            missing,
            "minute_bars",
        )
        if chart:
            raw_source_names.append("kis.domestic_time_itemchartprice")
            bars = _records(chart, "output2")

        orderbook = _call_optional(lambda: self._kis.domestic_asking_price(code), missing, "orderbook")
        orderbook_row = {}
        if orderbook:
            raw_source_names.append("kis.domestic_asking_price")
            orderbook_row = _first_record(orderbook, "output1")

        tape = _call_optional(lambda: self._kis.domestic_time_itemconclusion(code, input_hour=hour), missing, "trade_tape")
        tape_rows: list[dict[str, Any]] = []
        if tape:
            raw_source_names.append("kis.domestic_time_itemconclusion")
            tape_rows = _records(tape, "output2")

        investor_raw = _call_optional(lambda: self._kis.domestic_investor_trend_estimate(code), missing, "investor_flow")
        investor_flow = _summarize_kr_investor_flow(investor_raw)
        if investor_raw:
            raw_source_names.append("kis.domestic_investor_trend_estimate")

        program_raw = _call_optional(lambda: self._kis.domestic_program_trade_by_stock(code), missing, "program_flow")
        program_flow = _summarize_kr_program_flow(program_raw)
        if program_raw:
            raw_source_names.append("kis.domestic_program_trade_by_stock")

        market_class = "Q" if str(ticker).upper().endswith(".KQ") else "K"
        market_program_raw = _call_optional(
            lambda: self._kis.domestic_comp_program_trade_today(market_class=market_class, input_hour=hour),
            missing,
            "market_program_flow",
        )
        if market_program_raw:
            raw_source_names.append("kis.domestic_comp_program_trade_today")
            program_flow["market_program"] = _last_record(market_program_raw, "output")

        daily_rows = []
        daily = _call_optional(
            lambda: self._kis.domestic_daily_itemchartprice(
                code,
                start_date=now_local.date() - timedelta(days=60),
                end_date=now_local.date(),
            ),
            missing,
            "daily_volume",
        )
        if daily:
            raw_source_names.append("kis.domestic_daily_itemchartprice")
            daily_rows = _records(daily, "output2") or _records(daily, "output")

        last_price = _find_float(
            price_row,
            "stck_prpr",
            "prpr",
            "last",
            "LAST",
            default=_last_bar_price(bars),
        )
        if last_price is None:
            raise RuntimeError(f"KIS domestic microstructure response did not include price for {ticker}.")
        volume = int(_find_float(price_row, "acml_vol", "volume", default=_sum_volume(bars)) or 0)
        trading_value = _find_float(price_row, "acml_tr_pbmn", "tr_pbmn", "amount")
        if trading_value is None and volume > 0:
            trading_value = float(last_price * volume)
        price_change_pct = _find_float(price_row, "prdy_ctrt", "change_rate", "rate")
        day_high = _find_float(price_row, "stck_hgpr", "high", default=_max_value(bars, ("stck_hgpr", "high", "hprc"))) or last_price
        day_low = _find_float(price_row, "stck_lwpr", "low", default=_min_value(bars, ("stck_lwpr", "low", "lprc"))) or last_price
        session_vwap = _vwap_from_cumulative(price_row) or _vwap_from_bars(bars)
        avg20_daily_volume = _avg_daily_volume(daily_rows)
        relative_volume = _relative_volume(volume, avg20_daily_volume, now_local, market="KR")
        if session_vwap is None:
            missing.setdefault("session_vwap", "minute_or_cumulative_traded_value_unavailable")
        if relative_volume is None:
            missing.setdefault("relative_volume", "avg20_daily_volume_unavailable")

        orderbook_metrics = _orderbook_metrics(orderbook_row)
        execution_strength = _find_float(
            price_row,
            "cttr",
            "tbuy_cntg_strength",
            "execution_strength",
            "tday_rltv",
        )
        if execution_strength is None:
            execution_strength = _find_float(
                orderbook_row,
                "cttr",
                "tbuy_cntg_strength",
                "execution_strength",
                "tday_rltv",
            )
        if execution_strength is None:
            execution_strength = _execution_strength_from_tape(tape_rows)
        if execution_strength is None:
            missing.setdefault("execution_strength", "kis_trade_strength_field_unavailable")

        if orderbook_metrics["spread_bps"] is None and orderbook_metrics["orderbook_imbalance"] is None:
            missing.setdefault("orderbook", "kis_orderbook_fields_unavailable")

        vi_status = _status_from_keys(price_row, ("vi",), default_name="unknown")
        market_alert_status = _status_from_keys(price_row, ("mrkt_warn", "market_alert", "trht", "halt"), default_name="unknown")
        if not vi_status.get("is_clear"):
            missing.setdefault("vi_status", "vi_status_not_confirmed_by_rest_snapshot")
        if not market_alert_status.get("is_clear"):
            missing.setdefault("market_alert_status", "market_alert_not_confirmed_by_rest_snapshot")

        quality = _microstructure_quality(
            market="KR",
            session_vwap=session_vwap,
            relative_volume=relative_volume,
            spread_bps=orderbook_metrics["spread_bps"],
            orderbook_imbalance=orderbook_metrics["orderbook_imbalance"],
            execution_strength=execution_strength,
            investor_flow_status="available" if investor_flow.get("rows") else "missing",
            program_flow_status="available" if program_flow.get("rows") else "missing",
            vi_status=vi_status,
            market_alert_status=market_alert_status,
        )

        asof = _bar_asof(bars, fallback=now_local, timezone_name=market_timezone)
        return IntradayMarketSnapshot(
            ticker=ticker,
            asof=asof.isoformat(),
            provider=self.name,
            interval=interval,
            last_price=last_price,
            session_vwap=session_vwap,
            day_high=day_high,
            day_low=day_low,
            volume=volume,
            avg20_daily_volume=avg20_daily_volume,
            relative_volume=relative_volume,
            trading_value=trading_value,
            price_change_pct=price_change_pct,
            bar_timestamp=asof.isoformat(),
            provider_timestamp=now_local.isoformat(),
            quote_delay_seconds=max(0, int((now_local - asof).total_seconds())),
            provider_realtime_capable=self.realtime_capable,
            market_session=_market_session(now_local, market="KR"),
            execution_data_quality=quality,
            market="KR",
            exchange="KRX",
            checkpoint_id=checkpoint_id,
            asof_utc=now_utc.isoformat(),
            asof_local=now_local.isoformat(),
            spread_bps=orderbook_metrics["spread_bps"],
            orderbook_imbalance=orderbook_metrics["orderbook_imbalance"],
            execution_strength=execution_strength,
            source_latency_seconds=max(0, int((now_local - asof).total_seconds())),
            data_quality=quality,
            microstructure_required=True,
            investor_flow=investor_flow,
            program_flow=program_flow,
            vi_status=vi_status,
            market_alert_status=market_alert_status,
            investor_flow_status="available" if investor_flow.get("rows") else "missing",
            program_flow_status="available" if program_flow.get("rows") else "missing",
            trade_tape_summary=_trade_tape_summary(tape_rows),
            missing_reason=missing,
            raw_source_names=tuple(raw_source_names),
        )

    def _fetch_us(
        self,
        *,
        ticker: str,
        symbol: str,
        interval: str,
        market_timezone: str,
        checkpoint_id: str | None,
    ) -> IntradayMarketSnapshot:
        now_local = datetime.now(ZoneInfo(market_timezone))
        now_utc = now_local.astimezone(timezone.utc)
        symbol = str(symbol).upper().split(".", 1)[0]
        missing: dict[str, str] = {}
        raw_source_names: list[str] = []

        exchange, price = self._first_successful_us_price(symbol)
        raw_source_names.append("kis.overseas_price")
        price_row = _price_row_from_payload(price)

        detail = _call_optional(lambda: self._kis.overseas_price_detail(symbol, exchange=exchange), missing, "price_detail")
        detail_row = {}
        if detail:
            raw_source_names.append("kis.overseas_price_detail")
            detail_row = _first_record(detail, "output")

        bars: list[dict[str, Any]] = []
        chart_result = _call_optional(
            lambda: self._kis.overseas_time_itemchartprice(
                symbol,
                exchange=exchange,
                nmin=str(max(1, _interval_minutes(interval))),
                include_previous="1",
                nrec="120",
            ),
            missing,
            "minute_bars",
        )
        if chart_result:
            raw_source_names.append("kis.overseas_time_itemchartprice")
            chart_payload = chart_result[0] if isinstance(chart_result, tuple) else chart_result
            bars = _records(chart_payload, "output2")

        orderbook = _call_optional(lambda: self._kis.overseas_asking_price(symbol, exchange=exchange), missing, "orderbook")
        orderbook_row = {}
        if orderbook:
            raw_source_names.append("kis.overseas_asking_price")
            orderbook_row = (
                _first_record(orderbook, "output1")
                or _first_record(orderbook, "output2")
                or _first_record(orderbook, "output3")
            )

        tape_result = _call_optional(
            lambda: self._kis.overseas_quot_inquire_ccnl(symbol, exchange=exchange, today="1"),
            missing,
            "trade_tape",
        )
        tape_rows: list[dict[str, Any]] = []
        if tape_result:
            raw_source_names.append("kis.overseas_quot_inquire_ccnl")
            tape_payload = tape_result[0] if isinstance(tape_result, tuple) else tape_result
            tape_rows = _records(tape_payload, "output1") or _records(tape_payload, "output")

        volume_power = _call_optional(lambda: self._kis.overseas_volume_power(exchange=exchange), missing, "volume_power")
        volume_power_rank = {}
        if volume_power:
            raw_source_names.append("kis.overseas_volume_power")
            volume_power_payload = volume_power[0] if isinstance(volume_power, tuple) else volume_power
            volume_power_rank = _ranking_for_symbol(volume_power_payload, symbol)

        supplement = None
        if self._us_supplement_provider is not None:
            supplement = _call_optional(
                lambda: self._us_supplement_provider.fetch(symbol, now_local=now_local, interval=interval),
                missing,
                "us_market_data_supplement",
            )
            if supplement:
                raw_source_names.extend(getattr(supplement, "raw_source_names", ()))

        avg20_daily_volume = getattr(supplement, "avg20_daily_volume", None) if supplement is not None else None
        if avg20_daily_volume is None:
            avg20_daily_volume = self._us_daily_volume_fallback(symbol)
            if avg20_daily_volume is not None:
                raw_source_names.append("yfinance.daily_history")

        daily_rows = []
        if avg20_daily_volume is None and hasattr(self._kis, "fetch_overseas_daily_price_history"):
            daily_rows = _call_optional(
                lambda: self._kis.fetch_overseas_daily_price_history(
                    symbol=symbol,
                    exchange_code=exchange,
                    start_date=now_local.date() - timedelta(days=60),
                    end_date=now_local.date(),
                ),
                missing,
                "daily_volume",
            ) or []
            avg20_daily_volume = _avg_daily_volume(daily_rows)
            if avg20_daily_volume is not None:
                raw_source_names.append("kis.overseas_daily_price_history")

        combined_price = {**detail_row, **price_row}
        last_price = _find_float(
            combined_price,
            "last",
            "LAST",
            "ovrs_nmix_prpr",
            "stck_prpr",
            "base",
            default=_last_bar_price(bars),
        )
        if last_price is None:
            raise RuntimeError(f"KIS overseas microstructure response did not include price for {ticker}.")
        volume = int(_find_float(combined_price, "tvol", "TVOL", "acml_vol", "evol", "EVOL", default=_sum_volume(bars)) or 0)
        trading_value = _find_float(combined_price, "tamt", "TAMT", "acml_tr_pbmn", "amount")
        if trading_value is None and volume > 0:
            trading_value = float(last_price * volume)
        price_change_pct = _find_float(combined_price, "rate", "RATE", "prdy_ctrt", "change_rate")
        day_high = _find_float(combined_price, "high", "HIGH", "ovrs_nmix_hgpr", default=_max_value(bars, ("high", "HIGH", "hprc"))) or last_price
        day_low = _find_float(combined_price, "low", "LOW", "ovrs_nmix_lwpr", default=_min_value(bars, ("low", "LOW", "lprc"))) or last_price
        session_vwap = _vwap_from_cumulative(combined_price) or _vwap_from_bars(bars)
        relative_volume = _relative_volume(volume, avg20_daily_volume, now_local, market="US")
        if session_vwap is None:
            missing.setdefault("session_vwap", "minute_or_cumulative_traded_value_unavailable")
        if relative_volume is None:
            missing.setdefault("relative_volume", "avg20_daily_volume_unavailable")
        elif avg20_daily_volume is not None:
            missing.pop("daily_volume", None)
            missing.pop("relative_volume", None)

        orderbook_metrics = _orderbook_metrics(orderbook_row or combined_price)
        if (
            supplement is not None
            and orderbook_metrics["spread_bps"] is None
            and orderbook_metrics["orderbook_imbalance"] is None
        ):
            supplement_spread = getattr(supplement, "spread_bps", None)
            supplement_imbalance = getattr(supplement, "orderbook_imbalance", None)
            if supplement_spread is not None or supplement_imbalance is not None:
                orderbook_metrics = {"spread_bps": supplement_spread, "orderbook_imbalance": supplement_imbalance}
                missing.pop("orderbook", None)
        if orderbook_metrics["spread_bps"] is None and orderbook_metrics["orderbook_imbalance"] is None:
            missing.setdefault("orderbook", "kis_orderbook_fields_unavailable")

        execution_strength = _find_float(combined_price, "strn", "STRN", "execution_strength")
        if execution_strength is None:
            execution_strength = _find_float(orderbook_row, "strn", "STRN", "execution_strength")
        if execution_strength is None:
            execution_strength = _execution_strength_from_tape(tape_rows)
        if execution_strength is None and supplement is not None:
            execution_strength = getattr(supplement, "execution_strength", None)
            if execution_strength is not None:
                missing.pop("execution_strength", None)
        if execution_strength is None:
            missing.setdefault("execution_strength", "kis_trade_strength_field_unavailable")

        if supplement is not None:
            for key, reason in getattr(supplement, "limited_reason", {}).items():
                missing.setdefault(key, reason)

        halt_status = _status_from_keys(combined_price, ("halt", "trht", "mtyp", "stat"), default_name="normal")
        if not halt_status.get("is_clear"):
            missing.setdefault("halt_status", "halt_status_not_confirmed_by_snapshot")
        luld_status = _unavailable_us_market_status("luld_status", raw_source_names)
        reg_sho_status = _unavailable_us_market_status("reg_sho_status", raw_source_names)
        news_halt_status = _unavailable_us_market_status("news_halt_status", raw_source_names)
        source_limit_reasons = tuple(getattr(supplement, "pilot_blockers", ()) or ()) if supplement is not None else ()
        quality = _microstructure_quality(
            market="US",
            session_vwap=session_vwap,
            relative_volume=relative_volume,
            spread_bps=orderbook_metrics["spread_bps"],
            orderbook_imbalance=orderbook_metrics["orderbook_imbalance"],
            execution_strength=execution_strength,
            halt_status=halt_status,
            source_limit_reasons=source_limit_reasons,
        )
        asof = _bar_asof(bars, fallback=now_local, timezone_name=market_timezone)
        source_latency_seconds = max(0, int((now_local - asof).total_seconds()))
        if supplement is not None and getattr(supplement, "source_latency_seconds", None) is not None:
            source_latency_seconds = max(source_latency_seconds, int(supplement.source_latency_seconds))
        trade_tape_summary = _trade_tape_summary(tape_rows)
        if not tape_rows and supplement is not None and getattr(supplement, "trade_tape_summary", None):
            trade_tape_summary = supplement.trade_tape_summary
        return IntradayMarketSnapshot(
            ticker=ticker,
            asof=asof.isoformat(),
            provider=self.name,
            interval=interval,
            last_price=last_price,
            session_vwap=session_vwap,
            day_high=day_high,
            day_low=day_low,
            volume=volume,
            avg20_daily_volume=avg20_daily_volume,
            relative_volume=relative_volume,
            trading_value=trading_value,
            price_change_pct=price_change_pct,
            bar_timestamp=asof.isoformat(),
            provider_timestamp=now_local.isoformat(),
            quote_delay_seconds=max(0, int((now_local - asof).total_seconds())),
            provider_realtime_capable=self.realtime_capable,
            market_session=_market_session(now_local, market="US"),
            execution_data_quality=quality,
            market="US",
            exchange=exchange,
            checkpoint_id=checkpoint_id,
            asof_utc=now_utc.isoformat(),
            asof_local=now_local.isoformat(),
            spread_bps=orderbook_metrics["spread_bps"],
            orderbook_imbalance=orderbook_metrics["orderbook_imbalance"],
            execution_strength=execution_strength,
            source_latency_seconds=source_latency_seconds,
            data_quality=quality,
            microstructure_required=True,
            halt_status=halt_status,
            luld_status=luld_status,
            reg_sho_status=reg_sho_status,
            news_halt_status=news_halt_status,
            trade_tape_summary=trade_tape_summary,
            volume_power_rank=volume_power_rank,
            investor_flow_status="not_applicable",
            program_flow_status="not_applicable",
            missing_reason=missing,
            raw_source_names=tuple(raw_source_names),
        )

    def _first_successful_us_price(self, symbol: str) -> tuple[str, dict[str, Any]]:
        errors: list[str] = []
        for exchange in ("NAS", "NYS", "AMS"):
            try:
                payload = self._kis.overseas_price(symbol, exchange=exchange)
            except Exception as exc:
                errors.append(f"{exchange}:{exc.__class__.__name__}")
                continue
            if _price_row_has_last(_price_row_from_payload(payload)):
                return exchange, payload
            errors.append(f"{exchange}:no_price")
        raise RuntimeError(f"KIS overseas price lookup failed for {symbol}: {', '.join(errors)}")


def render_microstructure_report(snapshot: IntradayMarketSnapshot) -> str:
    payload = snapshot.to_dict()
    micro = payload.get("microstructure") or {}
    rows = [
        ("Market", micro.get("market") or ""),
        ("Ticker", snapshot.ticker),
        ("Exchange", micro.get("exchange") or ""),
        ("Checkpoint", micro.get("checkpoint_id") or ""),
        ("As-of", micro.get("asof_local") or snapshot.asof),
        ("Last price", _format_number(snapshot.last_price)),
        ("Session VWAP", _format_number(snapshot.session_vwap)),
        ("Relative volume", _format_number(snapshot.relative_volume)),
        ("Spread bps", _format_number(snapshot.spread_bps)),
        ("Orderbook imbalance", _format_number(snapshot.orderbook_imbalance)),
        ("Execution strength", _format_number(snapshot.execution_strength)),
        ("Data quality", snapshot.data_quality or snapshot.execution_data_quality),
        ("Investor flow", snapshot.investor_flow_status or ""),
        ("Program flow", snapshot.program_flow_status or ""),
    ]
    if snapshot.market == "KR":
        rows.extend(
            [
                ("VI status", _status_label(snapshot.vi_status)),
                ("Market alert", _status_label(snapshot.market_alert_status)),
            ]
        )
    if snapshot.market == "US":
        rows.append(("Halt status", _status_label(snapshot.halt_status)))
        rows.append(("LULD status", _status_label(snapshot.luld_status)))
        rows.append(("Reg SHO status", _status_label(snapshot.reg_sho_status)))
        rows.append(("News halt status", _status_label(snapshot.news_halt_status)))
        rows.append(("Trade tape", _summary_label(snapshot.trade_tape_summary)))
        rows.append(("Volume power", _summary_label(snapshot.volume_power_rank)))
    rows.extend(
        [
            ("Generated in current run", _format_bool(snapshot.generated_in_current_run)),
            ("Freshness class", snapshot.freshness_class or ""),
            ("Execution eligibility", snapshot.execution_eligibility or ""),
            ("Source run", snapshot.microstructure_source_run_id or ""),
            ("Backfilled from run", snapshot.backfilled_from_run_id or ""),
            ("Published in run", snapshot.published_in_run_id or ""),
            ("Artifact age seconds", _format_number(snapshot.artifact_age_seconds_at_publish)),
        ]
    )
    missing = snapshot.missing_reason or {}
    missing_lines = "\n".join(f"- {key}: {value}" for key, value in sorted(missing.items())) or "- none"
    table = "\n".join(f"| {name} | {value} |" for name, value in rows)
    return (
        f"# Microstructure Report - {snapshot.ticker}\n\n"
        "| Field | Value |\n"
        "|---|---|\n"
        f"{table}\n\n"
        "## Missing Or Limited Fields\n"
        f"{missing_lines}\n\n"
        "## Source Notes\n"
        f"- Provider: {snapshot.provider}\n"
        f"- Raw source names: {', '.join(snapshot.raw_source_names) if snapshot.raw_source_names else 'none'}\n"
        "- Account identifiers, balances, position sizes, order IDs, and fill IDs are intentionally excluded.\n"
    )


def _call_optional(func: Callable[[], Any], missing: dict[str, str], key: str) -> Any:
    try:
        return func()
    except Exception as exc:
        missing[key] = f"{exc.__class__.__name__}: {str(exc)[:160]}"
        return None


def _unavailable_us_market_status(field: str, raw_source_names: list[str]) -> dict[str, Any]:
    return {
        "status": "not_available_by_provider",
        "is_clear": None,
        "source": "configured_us_market_data_sources",
        "field": field,
        "raw_source_names": list(raw_source_names),
    }


def _looks_like_kr_symbol(ticker: str) -> bool:
    normalized = str(ticker or "").strip().upper()
    return normalized.endswith((".KS", ".KQ")) or (len(normalized) == 6 and normalized.isdigit())


def _records(payload: Any, key: str) -> list[dict[str, Any]]:
    if isinstance(payload, tuple):
        payload = payload[0]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    value = payload.get(key)
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return []


def _price_row_from_payload(payload: Any) -> dict[str, Any]:
    if isinstance(payload, tuple):
        payload = payload[0]
    if isinstance(payload, dict):
        row = _first_record(payload, "output")
        if row:
            return row
        if _price_row_has_last(payload):
            return payload
    return {}


def _price_row_has_last(row: dict[str, Any]) -> bool:
    return (
        _find_float(
            row,
            "last",
            "LAST",
            "ovrs_nmix_prpr",
            "stck_prpr",
            "base",
        )
        is not None
    )


def _first_record(payload: Any, key: str) -> dict[str, Any]:
    rows = _records(payload, key)
    return rows[0] if rows else {}


def _last_record(payload: Any, key: str) -> dict[str, Any]:
    rows = _records(payload, key)
    return rows[-1] if rows else {}


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).replace(",", "").replace("%", "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _find_float(mapping: dict[str, Any], *keys: str, default: float | None = None) -> float | None:
    lower_map = {str(key).lower(): value for key, value in mapping.items()}
    for key in keys:
        value = mapping.get(key)
        if value is None:
            value = lower_map.get(str(key).lower())
        parsed = _to_float(value)
        if parsed is not None:
            return parsed
    return default


def _vwap_from_cumulative(row: dict[str, Any]) -> float | None:
    amount = _find_float(row, "acml_tr_pbmn", "tamt", "TAMT", "tr_pbmn", "amount")
    volume = _find_float(row, "acml_vol", "tvol", "TVOL", "volume")
    if amount is not None and volume and volume > 0:
        return float(amount / volume)
    return None


def _vwap_from_bars(rows: list[dict[str, Any]]) -> float | None:
    total_amount = 0.0
    total_volume = 0.0
    for row in rows:
        volume = _find_float(row, "cntg_vol", "volume", "tvol", "TVOL", "xymd_vol")
        if not volume or volume <= 0:
            continue
        amount = _find_float(row, "tr_pbmn", "acml_tr_pbmn", "tamt", "TAMT")
        if amount is None:
            high = _find_float(row, "stck_hgpr", "high", "HIGH", "hprc")
            low = _find_float(row, "stck_lwpr", "low", "LOW", "lprc")
            close = _find_float(row, "stck_prpr", "close", "last", "LAST", "ovrs_nmix_prpr")
            if close is None:
                continue
            price = (high + low + close) / 3.0 if high is not None and low is not None else close
            amount = price * volume
        total_amount += amount
        total_volume += volume
    if total_volume <= 0:
        return None
    return float(total_amount / total_volume)


def _sum_volume(rows: list[dict[str, Any]]) -> float | None:
    total = 0.0
    found = False
    for row in rows:
        value = _find_float(row, "cntg_vol", "volume", "tvol", "TVOL")
        if value is not None:
            total += value
            found = True
    return total if found else None


def _last_bar_price(rows: list[dict[str, Any]]) -> float | None:
    if not rows:
        return None
    return _find_float(rows[0], "stck_prpr", "close", "last", "LAST", "ovrs_nmix_prpr")


def _max_value(rows: list[dict[str, Any]], keys: tuple[str, ...]) -> float | None:
    values = [_find_float(row, *keys) for row in rows]
    values = [value for value in values if value is not None]
    return max(values) if values else None


def _min_value(rows: list[dict[str, Any]], keys: tuple[str, ...]) -> float | None:
    values = [_find_float(row, *keys) for row in rows]
    values = [value for value in values if value is not None]
    return min(values) if values else None


def _avg_daily_volume(rows: list[dict[str, Any]]) -> float | None:
    values: list[float] = []
    for row in rows[:20]:
        value = _find_float(row, "acml_vol", "volume", "tvol", "TVOL")
        if value is not None and value > 0:
            values.append(value)
    if not values:
        return None
    return float(sum(values) / len(values))


def _avg20_daily_volume_from_yfinance(symbol: str) -> float | None:
    try:
        import yfinance as yf

        from tradingagents.dataflows.stockstats_utils import yf_retry

        ticker_obj = yf.Ticker(str(symbol).upper())
        daily = yf_retry(lambda: ticker_obj.history(period="3mo", interval="1d", auto_adjust=False))
    except Exception:
        return None
    if daily is None or daily.empty or "Volume" not in daily:
        return None
    volume = daily["Volume"].dropna().tail(20)
    if volume.empty:
        return None
    avg = float(volume.mean())
    return avg if avg > 0 else None


def _relative_volume(volume: int, avg20: float | None, now_local: datetime, *, market: str) -> float | None:
    if not avg20 or avg20 <= 0:
        return None
    progress = _session_progress_fraction(now_local, market=market)
    baseline = max(avg20 * progress, avg20 * 0.05)
    return float(volume / baseline)


def _session_progress_fraction(now_local: datetime, *, market: str) -> float:
    if market == "KR":
        session_open = datetime.combine(now_local.date(), time(hour=9, minute=0), tzinfo=now_local.tzinfo)
        session_close = datetime.combine(now_local.date(), time(hour=15, minute=30), tzinfo=now_local.tzinfo)
    else:
        session_open = datetime.combine(now_local.date(), time(hour=9, minute=30), tzinfo=now_local.tzinfo)
        session_close = datetime.combine(now_local.date(), time(hour=16, minute=0), tzinfo=now_local.tzinfo)
    total = max(1.0, (session_close - session_open).total_seconds())
    elapsed = min(max(0.0, (now_local - session_open).total_seconds()), total)
    return max(0.01, min(1.0, elapsed / total))


def _orderbook_metrics(row: dict[str, Any]) -> dict[str, float | None]:
    bid = _find_float(row, "bidp1", "pbid1", "PBID", "bid", "vbid1")
    ask = _find_float(row, "askp1", "pask1", "PASK", "ask", "vask1")
    spread_bps = None
    if bid is not None and ask is not None and bid > 0 and ask >= bid:
        spread_bps = float((ask - bid) / ((ask + bid) / 2.0) * 10_000.0)

    bid_volume = 0.0
    ask_volume = 0.0
    for idx in range(1, 11):
        bid_volume += _find_float(row, f"bidp_rsqn{idx}", f"bidp_rsqn_{idx}", f"vbid{idx}", f"VBID{idx}") or 0.0
        ask_volume += _find_float(row, f"askp_rsqn{idx}", f"askp_rsqn_{idx}", f"vask{idx}", f"VASK{idx}") or 0.0
    imbalance = None
    if bid_volume + ask_volume > 0:
        imbalance = float((bid_volume - ask_volume) / (bid_volume + ask_volume))
    return {"spread_bps": spread_bps, "orderbook_imbalance": imbalance}


def _execution_strength_from_tape(rows: list[dict[str, Any]]) -> float | None:
    for row in rows:
        direct = _find_float(row, "tday_rltv", "cttr", "tbuy_cntg_strength", "execution_strength")
        if direct is not None:
            return direct

    buy_volume = 0.0
    sell_volume = 0.0
    for row in rows:
        volume = abs(_find_float(row, "cntg_vol", "cnqn", "volume", "EVOL", "evol") or 0.0)
        sign_text = " ".join(str(row.get(key) or "") for key in ("ccld_dvsn", "sign", "MTYP", "mtyp")).lower()
        if any(token in sign_text for token in ("buy", "bid", "매수", "+", "2")):
            buy_volume += volume
        elif any(token in sign_text for token in ("sell", "ask", "매도", "-", "1")):
            sell_volume += volume
    if sell_volume > 0:
        return float(buy_volume / sell_volume * 100.0)
    return None


def _summarize_kr_investor_flow(payload: Any) -> dict[str, Any]:
    rows = _records(payload, "output2") or _records(payload, "output")
    latest = rows[-1] if rows else {}
    return {
        "status": "available" if rows else "missing",
        "rows": len(rows),
        "latest": _compact_record(latest),
    }


def _summarize_kr_program_flow(payload: Any) -> dict[str, Any]:
    rows = _records(payload, "output")
    latest = rows[-1] if rows else {}
    return {
        "status": "available" if rows else "missing",
        "rows": len(rows),
        "latest": _compact_record(latest),
    }


def _trade_tape_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "rows": len(rows),
        "latest": _compact_record(rows[0] if rows else {}),
    }


def _ranking_for_symbol(payload: Any, symbol: str) -> dict[str, Any]:
    rows = _records(payload, "output2") or _records(payload, "output")
    symbol_upper = symbol.upper()
    for index, row in enumerate(rows, start=1):
        row_symbol = str(row.get("symb") or row.get("SYMB") or row.get("ovrs_pdno") or "").upper()
        if row_symbol == symbol_upper:
            result = _compact_record(row)
            result["rank"] = index
            return result
    return {"status": "not_in_top_list", "rows_scanned": len(rows)}


def _compact_record(row: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(row, dict):
        return {}
    result: dict[str, Any] = {}
    for key, value in row.items():
        if value in (None, ""):
            continue
        result[str(key)] = value
        if len(result) >= 16:
            break
    return result


def _status_from_keys(row: dict[str, Any], tokens: tuple[str, ...], *, default_name: str) -> dict[str, Any]:
    relevant = {
        key: value
        for key, value in row.items()
        if any(token.lower() in str(key).lower() for token in tokens)
    }
    matched = {
        key: value
        for key, value in relevant.items()
        if str(value or "").strip() not in {"", "0", "00", "000", "N", "n", "normal", "NORMAL", "none", "NONE"}
    }
    if matched:
        return {"status": "flagged", "is_clear": False, "raw": _compact_record(matched)}
    if relevant:
        return {"status": "clear", "is_clear": True, "raw": _compact_record(relevant)}
    return {"status": default_name, "is_clear": default_name in {"normal", "clear"}}


def _status_label(value: dict[str, Any] | None) -> str:
    if not value:
        return ""
    return str(value.get("status") or "")


def _summary_label(value: dict[str, Any] | None) -> str:
    if not value:
        return ""
    status = str(value.get("status") or "").strip()
    rank = value.get("rank")
    rows = value.get("rows") or value.get("rows_scanned")
    if rank not in (None, ""):
        return f"rank {rank}"
    if status:
        return f"{status} ({rows} rows)" if rows not in (None, "") else status
    if rows not in (None, ""):
        return f"{rows} rows"
    return str(value)


def _microstructure_quality(
    *,
    market: str,
    session_vwap: float | None,
    relative_volume: float | None,
    spread_bps: float | None,
    orderbook_imbalance: float | None,
    execution_strength: float | None,
    investor_flow_status: str | None = None,
    program_flow_status: str | None = None,
    vi_status: dict[str, Any] | None = None,
    market_alert_status: dict[str, Any] | None = None,
    halt_status: dict[str, Any] | None = None,
    source_limit_reasons: tuple[str, ...] = (),
) -> str:
    missing_required = (
        session_vwap is None
        or relative_volume is None
        or (spread_bps is None and orderbook_imbalance is None)
        or execution_strength is None
        or bool(source_limit_reasons)
    )
    if market == "KR":
        missing_required = (
            missing_required
            or str(investor_flow_status or "").lower() != "available"
            or str(program_flow_status or "").lower() != "available"
            or not _status_is_clear(vi_status)
            or not _status_is_clear(market_alert_status)
        )
    if market == "US":
        missing_required = missing_required or not _status_is_clear(halt_status)
    return DELAYED_ANALYSIS_ONLY if missing_required else ""


def _status_is_clear(value: dict[str, Any] | None) -> bool:
    return bool(value and value.get("is_clear") is True)


def _bar_asof(rows: list[dict[str, Any]], *, fallback: datetime, timezone_name: str) -> datetime:
    if not rows:
        return fallback
    row = rows[0]
    raw = str(row.get("stck_cntg_hour") or row.get("XHMS") or row.get("xhms") or "").strip()
    date_text = str(
        row.get("stck_bsop_date")
        or row.get("XYMD")
        or row.get("xymd")
        or row.get("TYMD")
        or row.get("tymd")
        or fallback.strftime("%Y%m%d")
    )
    if len(raw) >= 6:
        try:
            parsed = datetime.strptime(date_text[:8] + raw[:6], "%Y%m%d%H%M%S")
            return parsed.replace(tzinfo=ZoneInfo(timezone_name))
        except ValueError:
            return fallback
    return fallback


def _interval_minutes(interval: str) -> int:
    text = str(interval or "5m").strip().lower()
    if text.endswith("m"):
        text = text[:-1]
    try:
        return int(text)
    except ValueError:
        return 5


def _market_session(ts: datetime, *, market: str) -> str:
    current = ts.time()
    if market == "KR":
        if current < time(hour=8):
            return "overnight"
        if current < time(hour=9):
            return "pre_open"
        if current <= time(hour=15, minute=30):
            return "regular"
        return "post_close"
    if current < time(hour=4):
        return "overnight"
    if current < time(hour=9, minute=30):
        return "pre_open"
    if current <= time(hour=16):
        return "regular"
    return "post_close"


def _format_number(value: Any) -> str:
    number = _to_float(value)
    if number is None:
        return ""
    if float(number).is_integer():
        return f"{int(number):,}"
    return f"{number:,.4f}".rstrip("0").rstrip(".")


def _format_bool(value: bool | None) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    return ""
