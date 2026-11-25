"""Point-in-time data bridge connecting OHLCV + LLM risk decisions to quant_policy.propose_weights."""
from __future__ import annotations

from datetime import date, datetime, timezone
import math
from statistics import mean, stdev
from typing import Any, Mapping, Sequence

from .experiments import _stamp
from .quant_policy import propose_weights


def _to_utc_cutoff(analysis_as_of: str | datetime) -> datetime:
    if isinstance(analysis_as_of, datetime):
        if analysis_as_of.tzinfo is None:
            raise ValueError("Aware analysis_as_of datetime required")
        return analysis_as_of.astimezone(timezone.utc)
    text = str(analysis_as_of or "").strip()
    if not text:
        raise ValueError("Explicit analysis_as_of required")
    if "T" not in text:
        parsed_day = date.fromisoformat(text[:10])
        return datetime(parsed_day.year, parsed_day.month, parsed_day.day, 23, 59, 59, tzinfo=timezone.utc)
    return _stamp(text).astimezone(timezone.utc)


def _clamp_unit(value: float) -> float:
    if not math.isfinite(value):
        return 0.0
    return round(max(-1.0, min(1.0, value)), 6)


def build_pit_market_evidence(
    raw_bars_by_ticker: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    analysis_as_of: str | datetime,
    currency: str,
    satellite_tickers: set[str] | Sequence[str],
    source: str = "pit_daily_ohlcv",
) -> dict[str, dict[str, Any]]:
    """Build strictly point-in-time bounded market_evidence for quant_policy.propose_weights.

    Every bar and factor timestamp is locally validated against analysis_as_of;
    future, undated, non-positive, or malformed bars are excluded before any computation.
    """
    cutoff = _to_utc_cutoff(analysis_as_of)
    satellite_set = {str(t).strip().upper() for t in satellite_tickers}
    evidence: dict[str, dict[str, Any]] = {}

    for raw_ticker, bars in raw_bars_by_ticker.items():
        ticker = str(raw_ticker or "").strip().upper()
        if not ticker or not isinstance(bars, Sequence):
            continue
        valid_bars: list[tuple[datetime, float, float]] = []
        seen_stamps: set[datetime] = set()
        for row in bars:
            if not isinstance(row, Mapping):
                continue
            raw_dt = row.get("known_at") or row.get("effective_at") or row.get("date")
            if not raw_dt:
                continue
            try:
                dt_str = str(raw_dt).strip()
                if "T" not in dt_str:
                    d = date.fromisoformat(dt_str[:10])
                    bar_dt = datetime(d.year, d.month, d.day, 21, 0, 0, tzinfo=timezone.utc)
                else:
                    bar_dt = _stamp(dt_str).astimezone(timezone.utc)
            except Exception:
                continue
            if bar_dt > cutoff or bar_dt in seen_stamps:
                continue
            close_val = row.get("adj_close", row.get("close", row.get("price")))
            vol_val = row.get("volume", 1_000_000)
            try:
                price = float(close_val)
                volume = float(vol_val)
            except (TypeError, ValueError):
                continue
            if not (math.isfinite(price) and price > 0 and math.isfinite(volume) and volume >= 0):
                continue
            seen_stamps.add(bar_dt)
            valid_bars.append((bar_dt, price, volume))

        valid_bars.sort(key=lambda item: item[0])
        if not valid_bars:
            continue

        latest_dt = valid_bars[-1][0]
        latest_iso = latest_dt.isoformat()
        recent_turnovers = [p * v for _, p, v in valid_bars[-20:]]
        avg_turnover = mean(recent_turnovers) if recent_turnovers else 0.0

        closes_payload = [
            {
                "effective_at": dt.isoformat(),
                "known_at": dt.isoformat(),
                "price": p,
                "basis": "total_return",
                "currency": currency,
                "source": source,
            }
            for dt, p, _ in valid_bars
        ]

        item_evidence: dict[str, Any] = {
            "security": {
                "eligible": True,
                "currency": currency,
                "effective_at": valid_bars[0][0].isoformat(),
                "known_at": valid_bars[0][0].isoformat(),
                "source": source,
            },
            "liquidity": {
                "turnover": round(avg_turnover, 2),
                "effective_at": latest_iso,
                "known_at": latest_iso,
                "source": source,
            },
            "closes": closes_payload,
        }

        if ticker in satellite_set and len(valid_bars) >= 65:
            prices = [p for _, p, _ in valid_bars]
            rets_60 = [right / left - 1.0 for left, right in zip(prices[-61:-1], prices[-60:])]
            vol_60 = stdev(rets_60) * math.sqrt(252) if len(rets_60) > 1 else 0.30
            mom_60 = prices[-1] / prices[-61] - 1.0
            mom_20 = prices[-1] / prices[-21] - 1.0
            # Quality proxy: risk-adjusted stability; Revision proxy: short-vs-medium acceleration; Strength: 60d momentum
            quality_score = _clamp_unit((mom_60 / max(vol_60, 0.10)) / 2.0)
            revision_score = _clamp_unit((mom_20 - (mom_60 / 3.0)) * 5.0)
            strength_score = _clamp_unit(mom_60 * 2.5)
            item_evidence["factors"] = {
                name: {
                    "value": val,
                    "effective_at": latest_iso,
                    "known_at": latest_iso,
                    "source": source,
                }
                for name, val in (
                    ("quality", quality_score),
                    ("revision", revision_score),
                    ("strength", strength_score),
                )
            }

        evidence[ticker] = item_evidence
    return evidence


def build_pit_vetoes_from_decisions(
    decisions: Mapping[str, Mapping[str, Any]],
    *,
    analysis_as_of: str | datetime,
    source: str = "structured_decision_risk_gate",
) -> dict[str, dict[str, Any]]:
    cutoff = _to_utc_cutoff(analysis_as_of)
    vetoes: dict[str, dict[str, Any]] = {}
    for raw_ticker, dec in decisions.items():
        ticker = str(raw_ticker or "").strip().upper()
        if not ticker or not isinstance(dec, Mapping):
            continue
        raw_known = dec.get("known_at") or dec.get("asof") or dec.get("finished_at")
        if not raw_known:
            continue
        try:
            known_dt = _to_utc_cutoff(str(raw_known))
        except Exception:
            continue
        if known_dt > cutoff:
            continue
        risk_action = str(dec.get("risk_action") or "NONE").strip().upper()
        stance = str(dec.get("portfolio_stance") or dec.get("stance") or "").strip().upper()
        if risk_action in {"EXIT", "STOP_LOSS"} or stance == "BEARISH":
            vetoes[ticker] = {
                "decision": "VETO",
                "reason": f"risk_action={risk_action},stance={stance}",
                "effective_at": known_dt.isoformat(),
                "known_at": known_dt.isoformat(),
                "source": source,
            }
        elif risk_action == "REDUCE_RISK":
            vetoes[ticker] = {
                "decision": "DEFER",
                "reason": "risk_action=REDUCE_RISK",
                "effective_at": known_dt.isoformat(),
                "known_at": known_dt.isoformat(),
                "source": source,
            }
    return vetoes


def evaluate_hybrid_portfolio_proposal(
    policy: Mapping[str, Any],
    raw_bars_by_ticker: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    analysis_as_of: str | datetime,
    decisions: Mapping[str, Mapping[str, Any]] | None = None,
    settled_cash_amount: float | None = None,
) -> dict[str, Any]:
    cutoff = _to_utc_cutoff(analysis_as_of)
    evidence = build_pit_market_evidence(
        raw_bars_by_ticker,
        analysis_as_of=cutoff,
        currency=str(policy["currency"]),
        satellite_tickers=policy.get("satellite") or (),
    )
    vetoes = build_pit_vetoes_from_decisions(decisions or {}, analysis_as_of=cutoff)
    cash_record = (
        {
            "amount": float(settled_cash_amount),
            "currency": str(policy["currency"]),
            "effective_at": cutoff.isoformat(),
            "known_at": cutoff.isoformat(),
            "source": "account_snapshot",
        }
        if settled_cash_amount is not None
        else None
    )
    return propose_weights(
        dict(policy),
        evidence,
        analysis_as_of=cutoff.isoformat(),
        vetoes=vetoes,
        settled_cash=cash_record,
    )
