from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

import requests

from tradingagents.dataflows.api_keys import get_api_key


DEFAULT_TIMEOUT_SECONDS = 12.0
MASSIVE_BASE_URL = "https://api.massive.com"
ALPACA_DATA_BASE_URL = "https://data.alpaca.markets"


@dataclass(frozen=True)
class USMicrostructureSupplement:
    avg20_daily_volume: float | None = None
    spread_bps: float | None = None
    orderbook_imbalance: float | None = None
    execution_strength: float | None = None
    source_latency_seconds: int | None = None
    trade_tape_summary: dict[str, Any] = field(default_factory=dict)
    raw_source_names: tuple[str, ...] = field(default_factory=tuple)
    limited_reason: dict[str, str] = field(default_factory=dict)
    missing_reason: dict[str, str] = field(default_factory=dict)
    pilot_blockers: tuple[str, ...] = field(default_factory=tuple)

    def merge_fill_missing(self, other: "USMicrostructureSupplement") -> "USMicrostructureSupplement":
        latest_summary = self.trade_tape_summary
        if self.execution_strength is None and other.execution_strength is not None:
            latest_summary = other.trade_tape_summary
        elif not latest_summary and other.trade_tape_summary:
            latest_summary = other.trade_tape_summary
        latency = _max_optional(self.source_latency_seconds, other.source_latency_seconds)
        raw_sources = _dedupe((*self.raw_source_names, *other.raw_source_names))
        limited = {**self.limited_reason, **other.limited_reason}
        missing = {**self.missing_reason, **other.missing_reason}
        blockers = _dedupe((*self.pilot_blockers, *other.pilot_blockers))
        return USMicrostructureSupplement(
            avg20_daily_volume=self.avg20_daily_volume
            if self.avg20_daily_volume is not None
            else other.avg20_daily_volume,
            spread_bps=self.spread_bps if self.spread_bps is not None else other.spread_bps,
            orderbook_imbalance=self.orderbook_imbalance
            if self.orderbook_imbalance is not None
            else other.orderbook_imbalance,
            execution_strength=self.execution_strength
            if self.execution_strength is not None
            else other.execution_strength,
            source_latency_seconds=latency,
            trade_tape_summary=latest_summary,
            raw_source_names=raw_sources,
            limited_reason=limited,
            missing_reason=missing,
            pilot_blockers=blockers,
        )


class CompositeUSMicrostructureSupplementProvider:
    def __init__(self, sources: list[Any] | None = None) -> None:
        self._sources = sources or []

    @classmethod
    def from_api_keys(cls) -> "CompositeUSMicrostructureSupplementProvider":
        sources: list[Any] = []
        massive_key = get_api_key("MASSIVE_API_KEY")
        if massive_key:
            sources.append(MassiveUSMicrostructureSource(api_key=massive_key))

        alpaca_key = get_api_key("ALPACA_API_KEY_ID")
        alpaca_secret = get_api_key("ALPACA_SECRET_KEY")
        if alpaca_key and alpaca_secret:
            sources.append(
                AlpacaUSMicrostructureSource(
                    key_id=alpaca_key,
                    secret_key=alpaca_secret,
                    preferred_feed=get_api_key("ALPACA_DATA_FEED"),
                )
            )
        return cls(sources)

    def fetch(
        self,
        symbol: str,
        *,
        now_local: datetime,
        interval: str = "5m",
    ) -> USMicrostructureSupplement:
        result = USMicrostructureSupplement()
        for source in self._sources:
            try:
                supplement = source.fetch(symbol, now_local=now_local, interval=interval)
            except Exception as exc:
                supplement = USMicrostructureSupplement(
                    missing_reason={source.name: f"{exc.__class__.__name__}: {str(exc)[:160]}"}
                )
            result = result.merge_fill_missing(supplement)

            if (
                result.avg20_daily_volume is not None
                and (result.spread_bps is not None or result.orderbook_imbalance is not None)
                and result.execution_strength is not None
            ):
                break
        return result


class MassiveUSMicrostructureSource:
    name = "massive"

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = MASSIVE_BASE_URL,
        session: requests.Session | None = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._session = session or requests.Session()
        self._timeout_seconds = timeout_seconds

    def fetch(
        self,
        symbol: str,
        *,
        now_local: datetime,
        interval: str = "5m",
    ) -> USMicrostructureSupplement:
        symbol = symbol.upper()
        missing: dict[str, str] = {}
        limited: dict[str, str] = {}
        raw_sources: list[str] = []
        blockers: list[str] = []

        daily_volume = self._fetch_avg20_daily_volume(symbol, now_local=now_local, missing=missing, raw_sources=raw_sources)
        quote = self._fetch_last_quote(symbol, missing=missing, raw_sources=raw_sources)
        trades = self._fetch_recent_trades(symbol, now_local=now_local, missing=missing, raw_sources=raw_sources)

        spread_bps, imbalance = _quote_metrics(quote)
        trade_strength, tape_summary = _execution_strength_from_trade_rows(
            trades,
            quote=quote,
            source="massive.trades_quotes",
            window_minutes=15,
        )
        if trade_strength is not None:
            limited.setdefault("execution_strength", "estimated_from_massive_trades_and_nbbo_quote")

        latency = _latest_latency_seconds(now_local=now_local, rows=[quote, *(trades[:1] if trades else [])])
        if latency is not None and latency > 15 * 60:
            blockers.append("massive_market_data_stale_or_delayed")
            limited.setdefault("source_latency", f"massive_latest_timestamp_age_seconds={latency}")

        return USMicrostructureSupplement(
            avg20_daily_volume=daily_volume,
            spread_bps=spread_bps,
            orderbook_imbalance=imbalance,
            execution_strength=trade_strength,
            source_latency_seconds=latency,
            trade_tape_summary=tape_summary,
            raw_source_names=tuple(raw_sources),
            limited_reason=limited,
            missing_reason=missing,
            pilot_blockers=tuple(blockers),
        )

    def _fetch_avg20_daily_volume(
        self,
        symbol: str,
        *,
        now_local: datetime,
        missing: dict[str, str],
        raw_sources: list[str],
    ) -> float | None:
        end_date = now_local.date() - timedelta(days=1)
        start_date = end_date - timedelta(days=90)
        payload = self._optional_json(
            f"/v2/aggs/ticker/{symbol}/range/1/day/{start_date.isoformat()}/{end_date.isoformat()}",
            params={"adjusted": "true", "sort": "desc", "limit": "40"},
            missing=missing,
            key="daily_volume_massive",
        )
        rows = _payload_results(payload)
        volumes = [_find_float(row, "v", "volume") for row in rows]
        volumes = [value for value in volumes if value is not None and value > 0][:20]
        if not volumes:
            return None
        raw_sources.append("massive.aggregates_daily")
        return float(sum(volumes) / len(volumes))

    def _fetch_last_quote(
        self,
        symbol: str,
        *,
        missing: dict[str, str],
        raw_sources: list[str],
    ) -> dict[str, Any]:
        payload = self._optional_json(f"/v2/last/nbbo/{symbol}", params={}, missing=missing, key="orderbook_massive")
        row = _payload_result(payload)
        if row:
            raw_sources.append("massive.last_nbbo")
        return row

    def _fetch_recent_trades(
        self,
        symbol: str,
        *,
        now_local: datetime,
        missing: dict[str, str],
        raw_sources: list[str],
    ) -> list[dict[str, Any]]:
        end_utc = now_local.astimezone(timezone.utc)
        start_utc = end_utc - timedelta(minutes=15)
        payload = self._optional_json(
            f"/v3/trades/{symbol}",
            params={
                "timestamp.gte": str(_ns_timestamp(start_utc)),
                "timestamp.lte": str(_ns_timestamp(end_utc)),
                "order": "desc",
                "sort": "timestamp",
                "limit": "5000",
            },
            missing=missing,
            key="execution_strength_massive",
        )
        rows = _payload_results(payload)
        if rows:
            raw_sources.append("massive.trades")
        return rows

    def _optional_json(
        self,
        path: str,
        *,
        params: dict[str, str],
        missing: dict[str, str],
        key: str,
    ) -> dict[str, Any]:
        try:
            response = self._session.get(
                f"{self._base_url}{path}",
                headers={"Authorization": f"Bearer {self._api_key}"},
                params=params,
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
            return payload if isinstance(payload, dict) else {}
        except Exception as exc:
            missing[key] = f"{exc.__class__.__name__}: {str(exc)[:160]}"
            return {}


class AlpacaUSMicrostructureSource:
    name = "alpaca"

    def __init__(
        self,
        *,
        key_id: str,
        secret_key: str,
        preferred_feed: str | None = None,
        base_url: str = ALPACA_DATA_BASE_URL,
        session: requests.Session | None = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self._key_id = key_id
        self._secret_key = secret_key
        self._preferred_feed = _normalize_feed(preferred_feed)
        self._base_url = base_url.rstrip("/")
        self._session = session or requests.Session()
        self._timeout_seconds = timeout_seconds

    def fetch(
        self,
        symbol: str,
        *,
        now_local: datetime,
        interval: str = "5m",
    ) -> USMicrostructureSupplement:
        symbol = symbol.upper()
        missing: dict[str, str] = {}
        limited: dict[str, str] = {}
        raw_sources: list[str] = []
        blockers: list[str] = []

        daily_volume, daily_feed = self._fetch_avg20_daily_volume(
            symbol,
            now_local=now_local,
            missing=missing,
            raw_sources=raw_sources,
        )
        quote, quote_feed = self._fetch_latest_quote(symbol, missing=missing, raw_sources=raw_sources)
        trades, trade_feed = self._fetch_recent_trades(
            symbol,
            now_local=now_local,
            missing=missing,
            raw_sources=raw_sources,
        )

        spread_bps, imbalance = _quote_metrics(quote)
        trade_strength, tape_summary = _execution_strength_from_trade_rows(
            trades,
            quote=quote,
            source=f"alpaca.{trade_feed or 'unknown'}_trades_quotes",
            window_minutes=15,
        )
        if trade_strength is not None:
            limited.setdefault("execution_strength", f"estimated_from_alpaca_trades_and_quote(feed={trade_feed or quote_feed})")

        for field, feed in (
            ("daily_volume", daily_feed),
            ("orderbook", quote_feed),
            ("execution_strength", trade_feed),
        ):
            if feed in {"iex", "delayed_sip"}:
                reason = f"alpaca_feed={feed}; {'non_consolidated' if feed == 'iex' else 'delayed'}"
                limited.setdefault(field, reason)
                blockers.append(f"{field}_{feed}_limited")

        latency = _latest_latency_seconds(now_local=now_local, rows=[quote, *(trades[:1] if trades else [])])
        if latency is not None and latency > 15 * 60:
            blockers.append("alpaca_market_data_stale_or_delayed")
            limited.setdefault("source_latency", f"alpaca_latest_timestamp_age_seconds={latency}")

        return USMicrostructureSupplement(
            avg20_daily_volume=daily_volume,
            spread_bps=spread_bps,
            orderbook_imbalance=imbalance,
            execution_strength=trade_strength,
            source_latency_seconds=latency,
            trade_tape_summary=tape_summary,
            raw_source_names=tuple(raw_sources),
            limited_reason=limited,
            missing_reason=missing,
            pilot_blockers=tuple(blockers),
        )

    def _fetch_avg20_daily_volume(
        self,
        symbol: str,
        *,
        now_local: datetime,
        missing: dict[str, str],
        raw_sources: list[str],
    ) -> tuple[float | None, str | None]:
        end_date = now_local.date() - timedelta(days=1)
        start_date = end_date - timedelta(days=90)
        for feed in self._historical_feed_candidates():
            payload = self._optional_json(
                "/v2/stocks/bars",
                params={
                    "symbols": symbol,
                    "timeframe": "1Day",
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "limit": "10000",
                    "adjustment": "raw",
                    "feed": feed,
                },
                missing=missing,
                key=f"daily_volume_alpaca_{feed}",
            )
            rows = _alpaca_symbol_rows(payload, symbol, "bars")
            volumes = [_find_float(row, "v", "volume") for row in reversed(rows)]
            volumes = [value for value in volumes if value is not None and value > 0][-20:]
            if volumes:
                raw_sources.append(f"alpaca.{feed}.daily_bars")
                return float(sum(volumes) / len(volumes)), feed
        return None, None

    def _fetch_latest_quote(
        self,
        symbol: str,
        *,
        missing: dict[str, str],
        raw_sources: list[str],
    ) -> tuple[dict[str, Any], str | None]:
        for feed in self._quote_feed_candidates():
            payload = self._optional_json(
                f"/v2/stocks/{symbol}/quotes/latest",
                params={"feed": feed},
                missing=missing,
                key=f"orderbook_alpaca_{feed}",
            )
            row = payload.get("quote") if isinstance(payload, dict) else {}
            if isinstance(row, dict) and row:
                raw_sources.append(f"alpaca.{feed}.latest_quote")
                return row, feed
        return {}, None

    def _fetch_recent_trades(
        self,
        symbol: str,
        *,
        now_local: datetime,
        missing: dict[str, str],
        raw_sources: list[str],
    ) -> tuple[list[dict[str, Any]], str | None]:
        end_utc = now_local.astimezone(timezone.utc)
        start_utc = end_utc - timedelta(minutes=15)
        for feed in self._historical_feed_candidates():
            payload = self._optional_json(
                "/v2/stocks/trades",
                params={
                    "symbols": symbol,
                    "start": start_utc.isoformat().replace("+00:00", "Z"),
                    "end": end_utc.isoformat().replace("+00:00", "Z"),
                    "limit": "10000",
                    "feed": feed,
                    "sort": "asc",
                },
                missing=missing,
                key=f"execution_strength_alpaca_{feed}",
            )
            rows = _alpaca_symbol_rows(payload, symbol, "trades")
            if rows:
                raw_sources.append(f"alpaca.{feed}.trades")
                return rows, feed
        return [], None

    def _quote_feed_candidates(self) -> tuple[str, ...]:
        if self._preferred_feed == "iex":
            return ("iex",)
        if self._preferred_feed == "delayed_sip":
            return ("delayed_sip", "iex")
        return ("sip", "delayed_sip", "iex")

    def _historical_feed_candidates(self) -> tuple[str, ...]:
        if self._preferred_feed == "iex":
            return ("iex",)
        return ("sip", "iex")

    def _optional_json(
        self,
        path: str,
        *,
        params: dict[str, str],
        missing: dict[str, str],
        key: str,
    ) -> dict[str, Any]:
        try:
            response = self._session.get(
                f"{self._base_url}{path}",
                headers={
                    "APCA-API-KEY-ID": self._key_id,
                    "APCA-API-SECRET-KEY": self._secret_key,
                },
                params=params,
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
            return payload if isinstance(payload, dict) else {}
        except Exception as exc:
            missing[key] = f"{exc.__class__.__name__}: {str(exc)[:160]}"
            return {}


def _quote_metrics(row: dict[str, Any]) -> tuple[float | None, float | None]:
    bid = _find_float(row, "bidp1", "pbid1", "PBID", "bid", "bp", "p", "bid_price")
    ask = _find_float(row, "askp1", "pask1", "PASK", "ask", "ap", "P", "ask_price")
    spread_bps = None
    if bid is not None and ask is not None and bid > 0 and ask >= bid:
        spread_bps = float((ask - bid) / ((ask + bid) / 2.0) * 10_000.0)

    bid_size = _find_float(row, "bidp_rsqn1", "vbid1", "VBID1", "bs", "s", "bid_size")
    ask_size = _find_float(row, "askp_rsqn1", "vask1", "VASK1", "as", "S", "ask_size")
    imbalance = None
    if bid_size is not None and ask_size is not None and bid_size + ask_size > 0:
        imbalance = float((bid_size - ask_size) / (bid_size + ask_size))
    return spread_bps, imbalance


def _execution_strength_from_trade_rows(
    rows: list[dict[str, Any]],
    *,
    quote: dict[str, Any],
    source: str,
    window_minutes: int,
) -> tuple[float | None, dict[str, Any]]:
    bid = _find_float(quote, "bidp1", "pbid1", "PBID", "bid", "bp", "p", "bid_price")
    ask = _find_float(quote, "askp1", "pask1", "PASK", "ask", "ap", "P", "ask_price")
    buy_volume = 0.0
    sell_volume = 0.0
    classified = 0
    previous_price: float | None = None
    ordered_rows = sorted(rows, key=lambda row: str(row.get("t") or row.get("sip_timestamp") or row.get("participant_timestamp") or ""))
    for row in ordered_rows:
        price = _find_float(row, "p", "price", "LAST", "last")
        size = _find_float(row, "s", "size", "volume", "v")
        if price is None or size is None or size <= 0:
            continue
        side = _trade_side(price, previous_price=previous_price, bid=bid, ask=ask)
        if side == "buy":
            buy_volume += size
            classified += 1
        elif side == "sell":
            sell_volume += size
            classified += 1
        previous_price = price if previous_price != price else previous_price

    strength = None
    if sell_volume > 0:
        strength = float(buy_volume / sell_volume * 100.0)
    elif buy_volume > 0:
        strength = 999.0

    latest = rows[-1] if rows else {}
    summary = {
        "rows": len(rows),
        "classified_rows": classified,
        "method": "quote_rule_then_tick_rule",
        "source": source,
        "window_minutes": window_minutes,
        "buy_initiated_volume": buy_volume,
        "sell_initiated_volume": sell_volume,
        "latest": _compact_record(latest),
    }
    return strength, summary


def _trade_side(price: float, *, previous_price: float | None, bid: float | None, ask: float | None) -> str | None:
    if ask is not None and price >= ask:
        return "buy"
    if bid is not None and price <= bid:
        return "sell"
    if previous_price is not None:
        if price > previous_price:
            return "buy"
        if price < previous_price:
            return "sell"
    return None


def _payload_results(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("results") if isinstance(payload, dict) else []
    if isinstance(rows, list):
        return [row for row in rows if isinstance(row, dict)]
    return []


def _payload_result(payload: dict[str, Any]) -> dict[str, Any]:
    row = payload.get("results") if isinstance(payload, dict) else {}
    return row if isinstance(row, dict) else {}


def _alpaca_symbol_rows(payload: dict[str, Any], symbol: str, key: str) -> list[dict[str, Any]]:
    container = payload.get(key) if isinstance(payload, dict) else {}
    if not isinstance(container, dict):
        return []
    rows = container.get(symbol.upper()) or container.get(symbol)
    if isinstance(rows, list):
        return [row for row in rows if isinstance(row, dict)]
    return []


def _find_float(row: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        if key not in row:
            continue
        value = row.get(key)
        try:
            if value in (None, ""):
                continue
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def _latest_latency_seconds(*, now_local: datetime, rows: list[dict[str, Any]]) -> int | None:
    latest: datetime | None = None
    for row in rows:
        ts = _timestamp_from_row(row)
        if ts is None:
            continue
        latest = ts if latest is None else max(latest, ts)
    if latest is None:
        return None
    return int(max(0, (now_local.astimezone(timezone.utc) - latest).total_seconds()))


def _timestamp_from_row(row: dict[str, Any]) -> datetime | None:
    for key in ("t", "sip_timestamp", "participant_timestamp", "trf_timestamp", "q", "timestamp"):
        raw = row.get(key)
        if raw in (None, ""):
            continue
        if isinstance(raw, (int, float)):
            value = float(raw)
            if value > 10_000_000_000_000:
                value = value / 1_000_000_000
            elif value > 10_000_000_000:
                value = value / 1_000
            return datetime.fromtimestamp(value, tz=timezone.utc)
        if isinstance(raw, str):
            text = raw.replace("Z", "+00:00")
            try:
                parsed = datetime.fromisoformat(text)
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                return parsed.astimezone(timezone.utc)
            except ValueError:
                continue
    return None


def _ns_timestamp(value: datetime) -> int:
    return int(value.astimezone(timezone.utc).timestamp() * 1_000_000_000)


def _normalize_feed(value: str | None) -> str:
    normalized = str(value or "sip").strip().lower()
    return normalized if normalized in {"sip", "iex", "delayed_sip"} else "sip"


def _compact_record(row: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(row, dict):
        return {}
    result: dict[str, Any] = {}
    for key, value in row.items():
        if value in (None, ""):
            continue
        result[str(key)] = value
        if len(result) >= 12:
            break
    return result


def _dedupe(values: tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return tuple(result)


def _max_optional(left: int | None, right: int | None) -> int | None:
    values = [value for value in (left, right) if value is not None]
    return max(values) if values else None
