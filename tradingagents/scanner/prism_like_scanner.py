from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from tradingagents.external.prism_conflicts import best_prism_signal_by_ticker
from tradingagents.external.prism_models import PrismExternalSignal, PrismSignalAction
from tradingagents.external.prism_normalize import canonicalize_ticker, coerce_float, normalize_market

from .models import ScannerCandidate, ScannerResult, TriggerType


def run_prism_like_scanner(
    *,
    ohlcv_rows: Iterable[dict[str, Any]] | None = None,
    ohlcv_path: str | Path | None = None,
    market: str = "KR",
    regime: str = "unknown",
    run_id: str | None = None,
    asof: str | None = None,
    max_candidates: int = 10,
    min_traded_value_krw: float = 10_000_000_000,
    min_market_cap_krw: float = 500_000_000_000,
    max_daily_change_pct: float = 20.0,
    min_volume_ratio_to_market_avg: float = 0.2,
    exclude_halted_or_low_liquidity: bool = True,
    external_signals: Iterable[PrismExternalSignal] | None = None,
    output_path: str | Path | None = None,
) -> ScannerResult:
    warnings: list[str] = []
    rows = list(ohlcv_rows or [])
    if ohlcv_path and not rows:
        loaded, load_warnings = _load_ohlcv_fixture(ohlcv_path)
        rows = loaded
        warnings.extend(load_warnings)
    signal_by_ticker = best_prism_signal_by_ticker(external_signals or [])
    candidates: list[ScannerCandidate] = []
    for row in rows:
        candidate = _scan_row(
            row,
            market=market,
            min_traded_value_krw=min_traded_value_krw,
            min_market_cap_krw=min_market_cap_krw,
            max_daily_change_pct=max_daily_change_pct,
            min_volume_ratio_to_market_avg=min_volume_ratio_to_market_avg,
            exclude_halted_or_low_liquidity=exclude_halted_or_low_liquidity,
            prism_signal=signal_by_ticker.get(_row_ticker(row, market=market) or ""),
        )
        if candidate is not None:
            candidates.append(candidate)
    candidates.sort(key=lambda item: item.final_score, reverse=True)
    result = ScannerResult(
        run_id=run_id or f"scanner_{datetime.now().strftime('%Y%m%dT%H%M%S')}",
        asof=asof or datetime.now().astimezone().isoformat(),
        market=market,
        regime=regime,
        candidates=tuple(candidates[: max(0, int(max_candidates))]),
        warnings=tuple(warnings),
    )
    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return result


def augment_universe_with_scanner(
    base_tickers: Iterable[str],
    scanner_result: ScannerResult | None,
    *,
    max_new_tickers: int = 5,
) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for ticker in base_tickers:
        text = str(ticker or "").strip().upper()
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    added = 0
    for candidate in (scanner_result.candidates if scanner_result else ()):
        ticker = str(candidate.ticker or "").strip().upper()
        if not ticker or ticker in seen:
            continue
        seen.add(ticker)
        result.append(ticker)
        added += 1
        if added >= max_new_tickers:
            break
    return result


def _load_ohlcv_fixture(path: str | Path) -> tuple[list[dict[str, Any]], list[str]]:
    source = Path(path).expanduser()
    if not source.exists():
        return [], [f"scanner_ohlcv_missing:{source}"]
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except Exception as exc:
        return [], [f"scanner_ohlcv_invalid:{source}:{exc}"]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)], []
    if isinstance(payload, dict):
        for key in ("rows", "ohlcv", "snapshot", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)], []
    return [], ["scanner_ohlcv_no_rows"]


def _scan_row(
    row: dict[str, Any],
    *,
    market: str,
    min_traded_value_krw: float,
    min_market_cap_krw: float,
    max_daily_change_pct: float,
    min_volume_ratio_to_market_avg: float,
    exclude_halted_or_low_liquidity: bool,
    prism_signal: PrismExternalSignal | None,
) -> ScannerCandidate | None:
    ticker = _row_ticker(row, market=market)
    if not ticker:
        return None
    open_price = _num(row, "open", "open_price")
    high = _num(row, "high", "high_price")
    low = _num(row, "low", "low_price")
    close = _num(row, "close", "current_price", "price", "last_price")
    prev_close = _num(row, "prev_close", "previous_close", "yesterday_close")
    volume = _num(row, "volume", "current_volume")
    prev_volume = _num(row, "prev_volume", "previous_volume", "volume_prev")
    trading_value = _num(row, "trading_value", "traded_value", "turnover", "value")
    market_cap = _num(row, "market_cap", "market_cap_krw", "cap")
    volume_ratio_to_market = _num(row, "volume_ratio_to_market_avg", "market_volume_ratio")
    halted = bool(row.get("halted") or row.get("is_halted"))

    if exclude_halted_or_low_liquidity and halted:
        return None
    if trading_value is not None and trading_value < min_traded_value_krw:
        return None
    if market_cap is not None and market_cap < min_market_cap_krw:
        return None
    if volume_ratio_to_market is not None and volume_ratio_to_market < min_volume_ratio_to_market_avg:
        return None
    if close is None or open_price is None or high is None or low is None or prev_close in (None, 0):
        return None

    change_pct = ((close - prev_close) / prev_close) * 100.0
    if abs(change_pct) > max_daily_change_pct:
        return None
    gap_rate = ((open_price - prev_close) / prev_close) * 100.0
    volume_ratio = (volume / prev_volume) if volume is not None and prev_volume not in (None, 0) else 1.0
    close_strength = (close - low) / (high - low) if high and low is not None and high > low else 0.5
    value_to_cap = (trading_value / market_cap) if trading_value is not None and market_cap not in (None, 0) else 0.0

    triggers: list[tuple[TriggerType, float, str]] = []
    if volume_ratio >= 1.3 and close > open_price and (trading_value or 0) >= min_traded_value_krw:
        triggers.append((TriggerType.VOLUME_SURGE, min(volume_ratio / 3.0, 1.0), "거래대금 기준 이상 + 전일 대비 거래량 급증"))
    if gap_rate >= 1.0 and close > open_price and (trading_value or 0) >= min_traded_value_krw:
        triggers.append((TriggerType.GAP_UP_MOMENTUM, min(gap_rate / 6.0 + 0.35, 1.0), "갭 상승 후 시가 상회 유지"))
    if value_to_cap >= 0.015 and close > open_price:
        triggers.append((TriggerType.VALUE_TO_MARKET_CAP_INFLOW, min(value_to_cap / 0.05, 1.0), "시가총액 대비 거래대금 유입"))
    if 3.0 <= change_pct <= max_daily_change_pct:
        triggers.append((TriggerType.DAILY_RISE_TOP, min(change_pct / max_daily_change_pct, 1.0), "일간 상승률 상위권"))
    if close_strength >= 0.75 and volume_ratio >= 1.0:
        triggers.append((TriggerType.CLOSING_STRENGTH, min(close_strength, 1.0), "고가 부근 종가 유지"))
    if volume_ratio >= 1.5 and abs(change_pct) <= 5.0:
        triggers.append((TriggerType.VOLUME_SURGE_FLAT, min(volume_ratio / 3.0, 1.0), "가격 과열 없이 거래량 증가"))
    high_52w = _num(row, "high_52w", "52w_high", "week_52_high")
    if high_52w and close >= high_52w * 0.95:
        triggers.append((TriggerType.NEAR_52W_HIGH, min(close / high_52w, 1.0), "52주 신고가 근접"))
    sector_rank = _num(row, "sector_rank", "sector_momentum_rank")
    sector_score = _num(row, "sector_leadership_score", "sector_score")
    if (sector_rank is not None and sector_rank <= 3) or (sector_score is not None and sector_score >= 0.75):
        triggers.append((TriggerType.SECTOR_LEADER, sector_score if sector_score is not None else 0.75, "섹터 내 상대 강도 상위"))
    if -3.0 <= change_pct <= 2.0 and close_strength >= 0.65 and value_to_cap >= 0.008:
        triggers.append((TriggerType.CONTRARIAN_VALUE_SUPPORT, min(close_strength * 0.8, 1.0), "하락 제한과 저가 매수 유입"))

    if not triggers:
        return None
    trigger_type, trigger_score, reason = max(triggers, key=lambda item: item[1])
    rr = _num(row, "risk_reward_ratio", "rr") or _estimate_rr(close=close, high=high, low=low)
    agent_fit = _agent_fit_score(row, close_strength=close_strength, volume_ratio=volume_ratio, rr=rr)
    prism_boost = 0.0
    if prism_signal and prism_signal.signal_action in {PrismSignalAction.BUY, PrismSignalAction.ADD, PrismSignalAction.WATCH}:
        prism_boost = min(float(prism_signal.confidence or 0.5) * 0.10, 0.10)
    final = min(trigger_score * 0.45 + agent_fit * 0.30 + min((rr or 1.0) / 2.5, 1.0) * 0.15 + prism_boost + 0.10, 1.0)
    stop_loss_pct = _num(row, "stop_loss_pct") or 0.05
    display_name = str(row.get("display_name") or row.get("name") or row.get("종목명") or "").strip() or None
    return ScannerCandidate(
        ticker=ticker,
        display_name=display_name,
        trigger_type=trigger_type.value,
        trigger_score=round(trigger_score, 4),
        agent_fit_score=round(agent_fit, 4),
        final_score=round(final, 4),
        stop_loss_pct=stop_loss_pct,
        risk_reward_ratio=rr,
        sector=str(row.get("sector") or "").strip() or None,
        market=normalize_market(row.get("market") or market, ticker=ticker),
        reasons=tuple(dict.fromkeys([reason, *_reason_fragments(row, volume_ratio=volume_ratio, trading_value=trading_value)])),
        raw=row,
    )


def _row_ticker(row: dict[str, Any], *, market: str) -> str | None:
    for key in ("ticker", "symbol", "canonical_ticker", "code", "종목코드"):
        value = row.get(key)
        if value not in (None, ""):
            return canonicalize_ticker(value, display_name=str(row.get("name") or row.get("display_name") or "") or None, market=market)
    return None


def _num(row: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return coerce_float(value)
    return None


def _estimate_rr(*, close: float, high: float, low: float) -> float:
    downside = max(close - low, close * 0.03)
    upside = max(high - close, close * 0.03)
    return round(upside / downside, 4)


def _agent_fit_score(row: dict[str, Any], *, close_strength: float, volume_ratio: float, rr: float | None) -> float:
    score = 0.35 + min(volume_ratio / 4.0, 0.25) + min(close_strength, 1.0) * 0.20
    if rr is not None:
        score += min(rr / 3.0, 0.20)
    if str(row.get("quality_flag") or "").lower() in {"halted", "low_liquidity"}:
        score -= 0.25
    return max(0.0, min(1.0, score))


def _reason_fragments(row: dict[str, Any], *, volume_ratio: float, trading_value: float | None) -> list[str]:
    reasons: list[str] = []
    if trading_value:
        reasons.append(f"거래대금 {int(trading_value):,} 이상")
    if volume_ratio >= 1.3:
        reasons.append(f"전일 대비 거래량 {volume_ratio:.1f}배")
    sector = str(row.get("sector") or "").strip()
    if sector:
        reasons.append(f"섹터 {sector}")
    return reasons
