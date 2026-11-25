"""PRISM-inspired shadow simulation and VTS candidate production.

Implements the end-to-end execution architecture benchmarked from dragon1086/prism-insight:
1. 10-slot account sizing with volatility/score micro-split (35%~85% of 1 slot) and sector cap (max 3).
2. Deterministic regime-aware Buy Gate (effective score, reward:risk floor, max stop distance).
3. Off-hours pending entries and deterministic stop/target/trailing exit suggestions.
4. Only the existing normal strategy can submit and reconcile an order. This
   module's shadow ledger is simulation evidence only.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_FLOOR
import hashlib
import json
import math
import os
from pathlib import Path
import sqlite3
from typing import Any, Callable, Mapping
from zoneinfo import ZoneInfo

from tradingagents.atomic_io import atomic_write_json, interprocess_file_lock
from tradingagents.charting.bars import instant

AUTOTRADER_SCHEMA = "tradingagents.prism-autotrader/v1"
MARKET_ZONES = {"KR": "Asia/Seoul", "US": "America/New_York"}
MARKET_CURRENCIES = {"KR": "KRW", "US": "USD"}

REGIME_BUY_RULES: dict[str, dict[str, float]] = {
    "parabolic": {"min_score": 5.2, "rr_floor": 1.0, "max_loss_pct": 7.0},
    "strong_bull": {"min_score": 5.5, "rr_floor": 1.0, "max_loss_pct": 7.0},
    "constructive": {"min_score": 5.5, "rr_floor": 1.1, "max_loss_pct": 7.0},
    "constructive_but_selective": {"min_score": 5.8, "rr_floor": 1.2, "max_loss_pct": 6.5},
    "mixed": {"min_score": 6.0, "rr_floor": 1.25, "max_loss_pct": 6.0},
    "sideways": {"min_score": 6.2, "rr_floor": 1.3, "max_loss_pct": 6.0},
    "defensive": {"min_score": 7.0, "rr_floor": 1.5, "max_loss_pct": 5.0},
}


@dataclass(frozen=True)
class AutotraderPolicy:
    mode: str = "shadow"  # "shadow" | "kis_vts" | "kis_live"
    enabled: bool = True
    live_orders_confirmed: bool = False
    live_promotion_override: str = ""
    kill_switch: bool = False
    max_slots: int = 10
    max_same_sector: int = 3
    kr_initial_capital: float = 10_000_000.0
    us_initial_capital: float = 10_000.0
    micro_split_enabled: bool = True
    one_share_nav_ceiling: float = 0.16
    session_entry_ttl_hours: int = 18
    buy_max_premium_pct: float = 3.0
    default_stop_loss_pct: float = 6.0
    default_target_profit_pct: float = 14.0
    runner_activate_pct: float = 20.0
    runner_trail_drawdown_pct: float = 10.0
    losing_time_stop_days: int = 30
    max_daily_loss_pct: float = 3.0
    fee_bps: float = 5.0
    slippage_bps: float = 5.0
    kr_sell_tax_bps: float = 20.0
    min_vts_trades_for_live: int = 20
    telegram_enabled: bool = False

    def __post_init__(self) -> None:
        if self.mode not in {"shadow", "kis_vts", "kis_live"}:
            raise ValueError(f"Unsupported autotrader mode: {self.mode}")
        if not 1 <= int(self.max_slots) <= 20:
            raise ValueError("max_slots must be between 1 and 20")
        if not 1 <= int(self.max_same_sector) <= int(self.max_slots):
            raise ValueError("max_same_sector must be between 1 and max_slots")
        if self.kr_initial_capital <= 0 or self.us_initial_capital <= 0:
            raise ValueError("Initial capital must be positive")
        if not 0.5 <= self.max_daily_loss_pct <= 15.0:
            raise ValueError("max_daily_loss_pct must be between 0.5 and 15.0")


@dataclass(frozen=True)
class PrismBuyGateResult:
    allowed: bool
    effective_score: float
    required_score: float
    regime: str
    stop_loss: float
    target_price: float
    reward_risk: float
    stop_distance_pct: float
    slot_fraction: float
    reasons: tuple[str, ...]


def _num(value: Any, default: float | None = None) -> float | None:
    if value in (None, "") or isinstance(value, bool):
        return default
    try:
        parsed = float(value)
        return parsed if math.isfinite(parsed) else default
    except (TypeError, ValueError):
        return default


def whole_share_quantity(budget: float, price: float) -> int:
    if not (math.isfinite(budget) and math.isfinite(price)) or budget <= 0 or price <= 0:
        return 0
    return int((Decimal(str(budget)) / Decimal(str(price))).to_integral_value(rounding=ROUND_FLOOR))


def compute_micro_split_fraction(effective_score: float, stop_distance_pct: float, *, enabled: bool = True) -> float:
    if not enabled:
        return 1.0
    base = 0.50
    if effective_score >= 8.0:
        base = 0.85
    elif effective_score >= 7.0:
        base = 0.70
    elif effective_score >= 6.0:
        base = 0.55
    else:
        base = 0.40
    if stop_distance_pct >= 5.5:
        base = max(0.35, base - 0.10)
    return round(min(1.0, max(0.35, base)), 4)


def _derive_candidate_score(candidate: Mapping[str, Any]) -> float:
    confidence = _num(candidate.get("confidence"), 0.5) or 0.5
    thesis = _num(candidate.get("thesis_strength"), confidence) or confidence
    buy_matrix = candidate.get("buy_matrix") if isinstance(candidate.get("buy_matrix"), Mapping) else {}
    matrix_total = _num(buy_matrix.get("total_score"))
    setup = str(candidate.get("setup_quality") or "DEVELOPING").strip().upper()
    setup_bonus = {"COMPELLING": 1.2, "DEVELOPING": 0.4, "WEAK": -1.2}.get(setup, 0.0)
    prism = str(candidate.get("prism_agreement") or "").strip().lower()
    prism_bonus = 0.6 if prism == "confirmed_buy" else (-0.8 if prism.startswith("conflict_") else 0.0)
    if matrix_total is not None and matrix_total > 0:
        # buy_matrix total_score is typically 0..100 or 0..10
        scaled = matrix_total / 10.0 if matrix_total > 10.0 else matrix_total
        score = 0.55 * scaled + 0.45 * (confidence * 10.0) + prism_bonus
    else:
        score = (0.60 * confidence + 0.40 * thesis) * 10.0 + setup_bonus + prism_bonus
    return round(max(0.0, min(10.0, score)), 2)


def _derive_stop_and_target(
    candidate: Mapping[str, Any],
    *,
    current_price: float,
    default_stop_pct: float,
    default_target_pct: float,
) -> tuple[float, float]:
    structured = candidate.get("structured_decision") if isinstance(candidate.get("structured_decision"), Mapping) else {}
    exec_levels = structured.get("execution_levels") if isinstance(structured.get("execution_levels"), Mapping) else {}
    levels = exec_levels.get("levels") if isinstance(exec_levels.get("levels"), list) else []
    stop_candidates: list[float] = []
    target_candidates: list[float] = []

    risk_level = candidate.get("risk_action_level")
    if isinstance(risk_level, Mapping):
        rp = _num(risk_level.get("price")) or _num(risk_level.get("low"))
        if rp and 0 < rp < current_price:
            stop_candidates.append(rp)

    profit_plan = candidate.get("profit_taking_plan")
    if isinstance(profit_plan, Mapping):
        for key in ("stage_2_price", "stage_1_price"):
            tp = _num(profit_plan.get(key))
            if tp and tp > current_price:
                target_candidates.append(tp)

    for item in levels:
        if not isinstance(item, Mapping):
            continue
        ltype = str(item.get("level_type") or "").strip().upper()
        val = _num(item.get("price")) or _num(item.get("low")) or _num(item.get("high"))
        if val is None or val <= 0:
            continue
        if ltype in {"STOP_LOSS", "INVALIDATION", "SUPPORT"} and val < current_price:
            stop_candidates.append(val)
        elif ltype in {"TAKE_PROFIT", "RESISTANCE"} and val > current_price:
            target_candidates.append(val)

    default_stop = current_price * (1.0 - default_stop_pct / 100.0)
    min_allowed_stop = current_price * 0.931  # keep within 7% hard ceiling when derived
    stop_loss = max(stop_candidates) if stop_candidates else default_stop
    if (current_price - stop_loss) / current_price > 0.07:
        stop_loss = max(stop_loss, min_allowed_stop) if not stop_candidates else stop_loss
    target_price = max(target_candidates) if target_candidates else current_price * (1.0 + default_target_pct / 100.0)
    return round(stop_loss, 4), round(target_price, 4)


def evaluate_prism_buy_gate(
    candidate: Mapping[str, Any],
    *,
    current_price: float,
    regime: str,
    slots_used: int,
    max_slots: int = 10,
    same_sector_count: int = 0,
    max_same_sector: int = 3,
    policy: AutotraderPolicy | None = None,
    defer_price: bool = False,
) -> PrismBuyGateResult:
    policy = policy or AutotraderPolicy()
    normalized_regime = str(regime or "constructive_but_selective").strip().lower()
    rule = REGIME_BUY_RULES.get(normalized_regime, REGIME_BUY_RULES["constructive_but_selective"])
    reasons: list[str] = []

    valid_price = current_price is not None and math.isfinite(current_price) and current_price > 0
    if not valid_price and not defer_price:
        return PrismBuyGateResult(False, 0.0, rule["min_score"], normalized_regime, 0.0, 0.0, 0.0, 0.0, 0.0, ("invalid_price",))

    stance = str(candidate.get("stance") or "").strip().upper()
    action_now = str(candidate.get("suggested_action_now") or candidate.get("action_now") or "").strip().upper()
    action_trig = str(candidate.get("suggested_action_if_triggered") or candidate.get("action_if_triggered") or "").strip().upper()
    risk_action = str(candidate.get("risk_action") or "NONE").strip().upper()

    if stance != "BULLISH":
        reasons.append("non_bullish_stance")
    if risk_action in {"EXIT", "STOP_LOSS", "REDUCE_RISK"}:
        reasons.append("conflicting_risk_action")
    if action_now not in {"STARTER_NOW", "ADD_NOW", "BUY_NOW"} and action_trig not in {"STARTER_IF_TRIGGERED", "ADD_IF_TRIGGERED"}:
        reasons.append("no_actionable_or_conditional_buy_intent")

    if slots_used >= max_slots:
        reasons.append("max_slots_reached")
    sector = str(candidate.get("sector") or "").strip()
    if sector and sector.upper() != "UNKNOWN" and same_sector_count >= max_same_sector:
        reasons.append("sector_cap_reached")

    score = _derive_candidate_score(candidate)
    if score < rule["min_score"]:
        reasons.append(f"score_below_floor:{score:.2f}<{rule['min_score']:.2f}")

    if not valid_price:
        return PrismBuyGateResult(not reasons, score, rule["min_score"], normalized_regime,
                                  0.0, 0.0, 0.0, 0.0, 0.0, tuple(reasons))

    stop_loss, target_price = _derive_stop_and_target(
        candidate,
        current_price=current_price,
        default_stop_pct=policy.default_stop_loss_pct,
        default_target_pct=policy.default_target_profit_pct,
    )
    if stop_loss <= 0 or stop_loss >= current_price:
        reasons.append("invalid_stop_loss")
        stop_dist_pct = 100.0
    else:
        stop_dist_pct = (current_price - stop_loss) / current_price * 100.0
        if stop_dist_pct > rule["max_loss_pct"] + 1e-6:
            reasons.append(f"stop_too_wide:{stop_dist_pct:.2f}%>{rule['max_loss_pct']:.2f}%")

    if target_price <= current_price or stop_loss >= current_price:
        rr = 0.0
        reasons.append("invalid_target_price")
    else:
        rr = (target_price - current_price) / max(current_price - stop_loss, 1e-9)
        if rr + 1e-6 < rule["rr_floor"]:
            reasons.append(f"rr_below_floor:{rr:.2f}<{rule['rr_floor']:.2f}")

    slot_fraction = compute_micro_split_fraction(score, stop_dist_pct, enabled=policy.micro_split_enabled)
    return PrismBuyGateResult(
        allowed=len(reasons) == 0,
        effective_score=score,
        required_score=rule["min_score"],
        regime=normalized_regime,
        stop_loss=stop_loss,
        target_price=target_price,
        reward_risk=round(rr, 3),
        stop_distance_pct=round(stop_dist_pct, 3),
        slot_fraction=slot_fraction,
        reasons=tuple(reasons),
    )


def initialize_autotrader_db(db_path: Path, policy: AutotraderPolicy | None = None) -> None:
    policy = policy or AutotraderPolicy()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path, timeout=30) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS autotrader_accounts (
                market TEXT PRIMARY KEY,
                currency TEXT NOT NULL,
                initial_capital REAL NOT NULL,
                cash REAL NOT NULL,
                started_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS autotrader_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                market TEXT NOT NULL,
                ticker TEXT NOT NULL,
                display_name TEXT,
                sector TEXT,
                mode TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                buy_price REAL NOT NULL,
                current_price REAL NOT NULL,
                peak_price REAL NOT NULL,
                stop_loss REAL NOT NULL,
                target_price REAL NOT NULL,
                slot_fraction REAL NOT NULL DEFAULT 1.0,
                runner_active INTEGER NOT NULL DEFAULT 0,
                buy_score REAL,
                regime TEXT,
                source_run_id TEXT,
                opened_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(market, ticker, mode)
            );
            CREATE TABLE IF NOT EXISTS autotrader_pending_entries (
                intent_id TEXT PRIMARY KEY,
                market TEXT NOT NULL,
                ticker TEXT NOT NULL,
                display_name TEXT,
                sector TEXT,
                mode TEXT NOT NULL,
                reference_price REAL NOT NULL,
                max_entry_price REAL NOT NULL,
                stop_loss REAL NOT NULL,
                target_price REAL NOT NULL,
                slot_fraction REAL NOT NULL,
                buy_score REAL NOT NULL,
                regime TEXT NOT NULL,
                source_run_id TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS autotrader_order_intents (
                intent_id TEXT PRIMARY KEY,
                market TEXT NOT NULL,
                ticker TEXT NOT NULL,
                side TEXT NOT NULL,
                mode TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                broker_order_no TEXT,
                status TEXT NOT NULL,
                reason TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS autotrader_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intent_id TEXT UNIQUE,
                market TEXT NOT NULL,
                ticker TEXT NOT NULL,
                display_name TEXT,
                sector TEXT,
                mode TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                buy_price REAL NOT NULL,
                sell_price REAL NOT NULL,
                fee_and_tax REAL NOT NULL,
                net_pnl REAL NOT NULL,
                return_pct REAL NOT NULL,
                slot_fraction REAL NOT NULL,
                holding_days INTEGER NOT NULL,
                exit_reason TEXT NOT NULL,
                source_run_id TEXT,
                opened_at TEXT NOT NULL,
                closed_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS autotrader_equity_curve (
                market TEXT NOT NULL,
                mode TEXT NOT NULL,
                session_date TEXT NOT NULL,
                observed_at TEXT NOT NULL,
                nav REAL NOT NULL,
                cash REAL NOT NULL,
                positions_value REAL NOT NULL,
                return_pct REAL NOT NULL,
                open_slots INTEGER NOT NULL,
                PRIMARY KEY (market, mode, session_date)
            );
            CREATE TABLE IF NOT EXISTS autotrader_notifications (
                delivery_key TEXT PRIMARY KEY,
                market TEXT NOT NULL,
                kind TEXT NOT NULL,
                message TEXT NOT NULL,
                sent INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );
            """
        )
        now_iso = datetime.now(timezone.utc).isoformat()
        for market, capital in (("KR", policy.kr_initial_capital), ("US", policy.us_initial_capital)):
            conn.execute(
                "INSERT OR IGNORE INTO autotrader_accounts (market, currency, initial_capital, cash, started_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (market, MARKET_CURRENCIES[market], float(capital), float(capital), now_iso, now_iso),
            )
        conn.commit()


def evaluate_live_promotion_gate(
    db_path: Path,
    market: str,
    *,
    min_vts_trades: int = 20,
) -> dict[str, Any]:
    """Legacy simulator rows do not constitute reconciled VTS promotion evidence."""
    return {
        "eligible": False,
        "closed_vts_trades": 0,
        "closed_burn_in_trades": 0,
        "required_trades": min_vts_trades,
        "blockers": ["LIVE_PROMOTION_GATE_BLOCKED", "NATIVE_VTS_SETTLEMENT_REVIEW_REQUIRED"],
    }


def compute_performance_metrics(db_path: Path, market: str, mode: str) -> dict[str, Any]:
    market = market.upper()
    with sqlite3.connect(db_path, timeout=20) as conn:
        conn.row_factory = sqlite3.Row
        acct = conn.execute("SELECT * FROM autotrader_accounts WHERE market=?", (market,)).fetchone()
        positions = [dict(r) for r in conn.execute(
            "SELECT * FROM autotrader_positions WHERE market=? AND mode=? ORDER BY opened_at ASC",
            (market, mode),
        )]
        trades = [dict(r) for r in conn.execute(
            "SELECT * FROM autotrader_trades WHERE market=? AND mode=? ORDER BY closed_at DESC",
            (market, mode),
        )]
        curve = [dict(r) for r in conn.execute(
            "SELECT * FROM autotrader_equity_curve WHERE market=? AND mode=? ORDER BY session_date ASC",
            (market, mode),
        )]
        pending = [dict(r) for r in conn.execute(
            "SELECT * FROM autotrader_pending_entries WHERE market=? AND mode=? AND status='QUEUED' ORDER BY buy_score DESC",
            (market, mode),
        )]

    initial = float(acct["initial_capital"]) if acct else (10_000_000.0 if market == "KR" else 10_000.0)
    cash = float(acct["cash"]) if acct else initial
    pos_value = sum(float(p["current_price"]) * int(p["quantity"]) for p in positions)
    nav = cash + pos_value
    season_return_pct = (nav - initial) / initial * 100.0 if initial > 0 else 0.0

    wins = [float(t["return_pct"]) for t in trades if float(t["return_pct"]) > 0]
    losses = [float(t["return_pct"]) for t in trades if float(t["return_pct"]) <= 0]
    avg_win = sum(wins) / len(wins) if wins else 0.0
    avg_loss = sum(losses) / len(losses) if losses else 0.0
    payoff_ratio = (avg_win / abs(avg_loss)) if avg_loss < 0 else (round(avg_win, 2) if wins else 0.0)
    slot_return_pct = sum(float(t["return_pct"]) * (float(t["slot_fraction"]) / 10.0) for t in trades)

    peak = initial
    mdd_pct = 0.0
    for point in curve:
        val = float(point["nav"])
        peak = max(peak, val)
        if peak > 0:
            mdd_pct = min(mdd_pct, (val - peak) / peak * 100.0)
    peak = max(peak, nav)
    if peak > 0:
        mdd_pct = min(mdd_pct, (nav - peak) / peak * 100.0)

    return {
        "market": market,
        "currency": MARKET_CURRENCIES[market],
        "mode": mode,
        "started_at": acct["started_at"] if acct else None,
        "initial_capital": round(initial, 2),
        "cash": round(cash, 2),
        "positions_value": round(pos_value, 2),
        "nav": round(nav, 2),
        "cash_ratio_pct": round((cash / nav * 100.0) if nav > 0 else 100.0, 2),
        "season_return_pct": round(season_return_pct, 2),
        "slot_realized_return_pct": round(slot_return_pct, 2),
        "closed_trades": len(trades),
        "win_count": len(wins),
        "loss_count": len(losses),
        "win_rate_pct": round((len(wins) / len(trades) * 100.0), 2) if trades else 0.0,
        "avg_win_pct": round(avg_win, 2),
        "avg_loss_pct": round(avg_loss, 2),
        "payoff_ratio": round(payoff_ratio, 2),
        "max_drawdown_pct": round(mdd_pct, 2),
        "open_slots": len(positions),
        "positions": positions,
        "pending_entries": pending,
        "recent_trades": trades[:50],
        "equity_curve": curve,
    }


def format_buy_telegram_message(market: str, ticker: str, name: str, price: float, qty: int, gate: PrismBuyGateResult, mode: str) -> str:
    unit = "원" if market == "KR" else "USD"
    price_str = f"{price:,.0f}원" if market == "KR" else f"${price:,.2f}"
    stop_str = f"{gate.stop_loss:,.0f}원" if market == "KR" else f"${gate.stop_loss:,.2f}"
    target_str = f"{gate.target_price:,.0f}원" if market == "KR" else f"${gate.target_price:,.2f}"
    mode_badge = {"shadow": "🧪 모의(Shadow)", "kis_vts": "🧪 KIS 모의투자", "kis_live": "💰 KIS 실전투자"}.get(mode, mode)
    notional = price * qty
    notional_str = f"{notional:,.0f}{unit}" if market == "KR" else f"${notional:,.2f}"
    return (
        f"📈 매수 체결 [{mode_badge}]\n"
        f"• 종목: {name} ({ticker})\n"
        f"• 체결가/수량: {price_str} × {qty}주 ({notional_str})\n"
        f"• 슬롯 비중: 1슬롯의 {gate.slot_fraction * 100:.0f}% (점수 {gate.effective_score:.1f}/10, 국면 {gate.regime})\n"
        f"• 목표가: {target_str} | 손절가: {stop_str} (손익비 {gate.reward_risk:.2f})"
    )


def format_sell_telegram_message(
    market: str,
    ticker: str,
    name: str,
    buy_price: float,
    sell_price: float,
    qty: int,
    return_pct: float,
    holding_days: int,
    reason: str,
    mode: str,
) -> str:
    buy_str = f"{buy_price:,.0f}원" if market == "KR" else f"${buy_price:,.2f}"
    sell_str = f"{sell_price:,.0f}원" if market == "KR" else f"${sell_price:,.2f}"
    arrow = "⬆️" if return_pct > 0 else ("⬇️" if return_pct < 0 else "➖")
    mode_badge = {"shadow": "🧪 모의(Shadow)", "kis_vts": "🧪 KIS 모의투자", "kis_live": "💰 KIS 실전투자"}.get(mode, mode)
    return (
        f"📉 매도 체결 [{mode_badge}]\n"
        f"• 종목: {name} ({ticker}) {qty}주\n"
        f"• 매수가: {buy_str} → 매도가: {sell_str}\n"
        f"• 실현 수익률: {arrow} {return_pct:+.2f}% (보유 {holding_days}일)\n"
        f"• 매도 사유: {reason}"
    )


def format_portfolio_telegram_report(kr_metrics: Mapping[str, Any], us_metrics: Mapping[str, Any], *, now_kst: datetime) -> str:
    mode = str(kr_metrics.get("mode") or "shadow")
    badge = "💰 실전투자" if mode == "kis_live" else "🧪 모의투자"
    lines = [
        f"📊 TradingAgents 자동매매 포트폴리오 리포트 ({badge})",
        f"🕐 {now_kst.strftime('%Y-%m-%d %H:%M')} KST",
        "",
        f"🇰🇷 한국 포트폴리오 ({kr_metrics['open_slots']}/10 슬롯)",
        f"• 총 자산: {kr_metrics['nav']:,.0f}원 ({kr_metrics['season_return_pct']:+.2f}%)",
        f"• 현금 비중: {kr_metrics['cash']:,.0f}원 ({kr_metrics['cash_ratio_pct']:.1f}%)",
        f"• 청산 {kr_metrics['closed_trades']}건 | 승률 {kr_metrics['win_rate_pct']:.1f}% | 평균수익 {kr_metrics['avg_win_pct']:+.2f}% | 평균손실 {kr_metrics['avg_loss_pct']:+.2f}% | 손익비 {kr_metrics['payoff_ratio']:.2f}",
        "",
        f"🇺🇸 미국 포트폴리오 ({us_metrics['open_slots']}/10 슬롯)",
        f"• 총 자산: ${us_metrics['nav']:,.2f} ({us_metrics['season_return_pct']:+.2f}%)",
        f"• 현금 비중: ${us_metrics['cash']:,.2f} ({us_metrics['cash_ratio_pct']:.1f}%)",
        f"• 청산 {us_metrics['closed_trades']}건 | 승률 {us_metrics['win_rate_pct']:.1f}% | 평균수익 {us_metrics['avg_win_pct']:+.2f}% | 평균손실 {us_metrics['avg_loss_pct']:+.2f}% | 손익비 {us_metrics['payoff_ratio']:.2f}",
    ]
    return "\n".join(lines)


def _default_session_resolver(*, market: str, now_local: datetime) -> dict[str, Any]:
    from tradingagents.execution.paper_runtime import _runtime_session
    return _runtime_session(market=market.lower(), now_local=now_local)


def _default_quote_loader(market: str, ticker: str, now: datetime) -> float | None:
    try:
        from tradingagents.dataflows.intraday.kis_quotes import KISQuoteProvider
        snap = KISQuoteProvider().fetch(ticker)
        if snap and snap.last_price and snap.last_price > 0:
            return float(snap.last_price)
    except Exception:
        return None
    return None


def _default_broker_executor(mode: str, market: str, side: str, ticker: str, quantity: int, price: float, now: datetime) -> dict[str, Any]:
    if mode != "shadow":
        raise ValueError("Only the shadow lane can use the local fill simulator")
    return {"accepted": True, "order_no": f"SHADOW-{market}-{int(now.timestamp())}", "fill_price": price}


def risk_exit_reason(*, price, entry, stop, target, peak, runner, days, risk, policy):
    ret = (price - entry) / entry * 100.0
    if price <= stop:
        return f"손절가 도달 ({stop:,.2f})"
    if ret <= -7.0:
        return f"절대 손절 한도 도달 ({ret:.2f}%)"
    if risk in {"STOP_LOSS", "EXIT"}:
        return f"AI 리스크 청산 ({risk})"
    if runner:
        drawdown = (peak - price) / peak * 100.0
        if price <= entry * 1.005:
            return "주도주 본전 보호선 이탈"
        if drawdown >= policy.runner_trail_drawdown_pct:
            return f"주도주 고점 대비 -{drawdown:.1f}% 트레일링 청산"
    elif price >= target:
        return f"목표가 달성 ({target:,.2f})"
    elif days >= policy.losing_time_stop_days and ret < 0:
        return f"{days}일 보유 손실 시간청산 ({ret:.2f}%)"
    return None


class PrismAutoTrader:
    """Local simulation or independent candidate generation."""

    def __init__(
        self,
        archive_dir: Path,
        state_dir: Path,
        *,
        policy: AutotraderPolicy | None = None,
        clock: Callable[[], datetime] | None = None,
        session_resolver: Callable[..., dict[str, Any]] | None = None,
        quote_loader: Callable[[str, str, datetime], float | None] | None = None,
        broker_executor: Callable[[str, str, str, str, int, float, datetime], dict[str, Any]] | None = None,
        telegram_sender: Callable[[str], bool] | None = None,
    ) -> None:
        self.archive_dir = Path(archive_dir)
        self.state_dir = Path(state_dir)
        self.policy = policy or AutotraderPolicy()
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.session_resolver = session_resolver or _default_session_resolver
        self.quote_loader = quote_loader or _default_quote_loader
        self.broker_executor = broker_executor or _default_broker_executor
        self.telegram_sender = telegram_sender
        self.db_path = self.archive_dir / "paper" / "autotrader.sqlite"
        if self.policy.mode == "shadow" and self.policy.enabled is True and not self.policy.kill_switch and not (self.state_dir / "HALT").exists():
            initialize_autotrader_db(self.db_path, self.policy)

    def _now(self) -> datetime:
        at = instant(self.clock())
        if at is None:
            raise ValueError("Aware autotrader clock required")
        return at

    def _latest_market_run(self, market: str, now: datetime) -> tuple[Path | None, dict[str, Any] | None]:
        runs_root = self.archive_dir / "runs"
        if not runs_root.is_dir():
            return None, None
        ttl = timedelta(hours=self.policy.session_entry_ttl_hours)
        for year_dir in sorted((p for p in runs_root.iterdir() if p.is_dir()), reverse=True):
            for run_dir in sorted((p for p in year_dir.iterdir() if p.is_dir()), reverse=True):
                manifest_path = run_dir / "run.json"
                candidates_path = run_dir / "portfolio-private" / "portfolio_candidates.json"
                if not manifest_path.is_file() or not candidates_path.is_file():
                    continue
                try:
                    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                    if str((manifest.get("settings") or {}).get("market") or "").upper() != market.upper():
                        continue
                    finished = instant(manifest.get("finished_at"))
                    if finished is None or not timedelta(0) <= (now - finished) <= ttl:
                        continue
                    if str(manifest.get("status") or "").lower() not in {"success", "partial_failure"}:
                        continue
                    return run_dir, manifest
                except Exception:
                    continue
        return None, None

    def _queue_notification(self, conn: sqlite3.Connection, market: str, kind: str, key: str, message: str, now: datetime) -> None:
        cur = conn.execute(
            "INSERT OR IGNORE INTO autotrader_notifications (delivery_key, market, kind, message, sent, created_at) "
            "VALUES (?, ?, ?, ?, 0, ?)",
            (key, market, kind, message, now.isoformat()),
        )
        if cur.rowcount and self.policy.telegram_enabled and self.telegram_sender is not None:
            if self.telegram_sender(message):
                conn.execute("UPDATE autotrader_notifications SET sent=1 WHERE delivery_key=?", (key,))

    def _check_mode_safety(self, market: str) -> tuple[bool, list[str]]:
        blockers: list[str] = []
        if self.policy.enabled is not True:
            blockers.append("AUTOTRADER_DISABLED")
        if self.policy.kill_switch or (self.state_dir / "HALT").exists():
            blockers.append("KILL_SWITCH_ACTIVE")
        if self.policy.mode == "kis_live":
            blockers.append("LIVE_PROMOTION_GATE_BLOCKED")
        return len(blockers) == 0, blockers

    def tick_market(self, market: str) -> dict[str, Any]:
        market = market.upper()
        if market not in {"KR", "US"}:
            raise ValueError(f"Unsupported market: {market}")
        now = self._now()
        zone = ZoneInfo(MARKET_ZONES[market])
        local_now = now.astimezone(zone)
        safe, blockers = self._check_mode_safety(market)
        candidate_runtime = None
        if self.policy.mode == "kis_vts":
            from . import prism_candidate_runtime
            if prism_candidate_runtime.observes(self.policy):
                candidate_runtime = prism_candidate_runtime
        session = self.session_resolver(market=market, now_local=now) if safe or candidate_runtime else {}
        is_open = bool(session.get("is_open") and session.get("phase") == "regular")

        if not safe or self.policy.mode != "shadow":
            receipt = {
                "schema": AUTOTRADER_SCHEMA, "market": market, "mode": self.policy.mode,
                "live_orders_enabled": False, "checked_at": now.isoformat(), "session_open": is_open,
                "source_revision": os.getenv("TRADINGAGENTS_SOURCE_SHA"),
                "source_run_id": None, "blockers": blockers, "entries_queued": [],
                "entries_executed": [], "exits_executed": [],
            }
            if candidate_runtime:
                observed = candidate_runtime.produce(self.archive_dir, self.state_dir, market, now, session, self.policy)
                receipt.update(observed, blockers=list(dict.fromkeys([*blockers, *observed["blockers"]])))
            atomic_write_json(self.state_dir / f"autotrader-{market.lower()}-status.json", receipt)
            return receipt

        exits_executed: list[dict[str, Any]] = []
        entries_executed: list[dict[str, Any]] = []
        entries_queued: list[str] = []

        run_dir, manifest = self._latest_market_run(market, now)
        candidates_payload: dict[str, Any] = {}
        if run_dir is not None:
            try:
                candidates_payload = json.loads(
                    (run_dir / "portfolio-private" / "portfolio_candidates.json").read_text(encoding="utf-8")
                )
            except Exception:
                candidates_payload = {}
        candidate_list = candidates_payload.get("candidates") if isinstance(candidates_payload.get("candidates"), list) else []
        regime = str((candidates_payload.get("batch_metrics") or {}).get("market_regime") or "constructive_but_selective")
        risk_veto_map = {
            str(c.get("canonical_ticker") or "").upper(): str(c.get("risk_action") or "NONE").upper()
            for c in candidate_list
            if isinstance(c, Mapping)
        }

        with interprocess_file_lock(self.state_dir / f"autotrader-{market.lower()}.lock", timeout=10), sqlite3.connect(
            self.db_path, timeout=30
        ) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute("BEGIN IMMEDIATE")

            # Expire stale pending entries
            conn.execute(
                "UPDATE autotrader_pending_entries SET status='EXPIRED', updated_at=? "
                "WHERE market=? AND mode=? AND status='QUEUED' AND expires_at<=?",
                (now.isoformat(), market, self.policy.mode, now.isoformat()),
            )

            # Loop A + B: Mark-to-market & Intraday LLM-free Exit Guard
            positions = [dict(r) for r in conn.execute(
                "SELECT * FROM autotrader_positions WHERE market=? AND mode=? ORDER BY opened_at ASC",
                (market, self.policy.mode),
            )]
            for pos in positions:
                ticker = pos["ticker"]
                live_price = self.quote_loader(market, ticker, now) if is_open else None
                if live_price is not None and live_price > 0:
                    peak_price = max(float(pos["peak_price"]), live_price)
                    peak_ret = (peak_price - float(pos["buy_price"])) / float(pos["buy_price"]) * 100.0
                    runner_active = int(pos["runner_active"]) or int(peak_ret >= self.policy.runner_activate_pct)
                    conn.execute(
                        "UPDATE autotrader_positions SET current_price=?, peak_price=?, runner_active=?, updated_at=? WHERE id=?",
                        (live_price, peak_price, runner_active, now.isoformat(), pos["id"]),
                    )
                    pos.update(current_price=live_price, peak_price=peak_price, runner_active=runner_active)

                if not is_open or not safe:
                    continue

                curr = float(pos["current_price"])
                buy_p = float(pos["buy_price"])
                opened_dt = instant(pos["opened_at"]) or now
                holding_days = max(0, (local_now.date() - opened_dt.astimezone(zone).date()).days)

                exit_reason = risk_exit_reason(
                    price=curr, entry=buy_p, stop=float(pos["stop_loss"]), target=float(pos["target_price"]),
                    peak=float(pos["peak_price"]), runner=bool(pos["runner_active"]), days=holding_days,
                    risk=risk_veto_map.get(ticker.upper()), policy=self.policy,
                )

                if exit_reason:
                    sell_intent_id = hashlib.sha256(
                        f"SELL|{market}|{self.policy.mode}|{ticker}|{pos['opened_at']}|{local_now.date().isoformat()}".encode()
                    ).hexdigest()[:32]
                    if conn.execute(
                        "SELECT 1 FROM autotrader_order_intents WHERE intent_id=? AND status IN ('SUBMITTING','UNKNOWN','SUBMITTED')",
                        (sell_intent_id,),
                    ).fetchone():
                        continue
                    conn.execute(
                        "INSERT OR REPLACE INTO autotrader_order_intents VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                        (sell_intent_id, market, ticker, "SELL", self.policy.mode, int(pos["quantity"]), curr, None, "SUBMITTING", exit_reason, now.isoformat(), now.isoformat()),
                    )
                    conn.commit()
                    conn.execute("BEGIN IMMEDIATE")
                    try:
                        exec_res = self.broker_executor(self.policy.mode, market, "SELL", ticker, int(pos["quantity"]), curr, now)
                    except Exception as exc:
                        conn.execute(
                            "UPDATE autotrader_order_intents SET status='UNKNOWN', reason=?, updated_at=? WHERE intent_id=?",
                            (type(exc).__name__, now.isoformat(), sell_intent_id),
                        )
                        blockers.append(f"ORDER_OUTCOME_UNKNOWN:{ticker}")
                        continue
                    if not exec_res.get("accepted"):
                        conn.execute(
                            "UPDATE autotrader_order_intents SET status='FAILED', updated_at=? WHERE intent_id=?",
                            (now.isoformat(), sell_intent_id),
                        )
                        continue
                    raw_fill = float(exec_res.get("fill_price") or curr)
                    slip = (self.policy.slippage_bps / 10_000.0) if self.policy.mode == "shadow" else 0.0
                    eff_sell = raw_fill * (1.0 - slip)
                    gross = eff_sell * int(pos["quantity"])
                    tax_bps = self.policy.kr_sell_tax_bps if market == "KR" else 0.0
                    sell_cost = gross * ((self.policy.fee_bps + tax_bps) / 10_000.0)
                    buy_cost = buy_p * int(pos["quantity"]) * (self.policy.fee_bps / 10_000.0)
                    net_proceeds = gross - sell_cost
                    net_pnl = net_proceeds - (buy_p * int(pos["quantity"]) + buy_cost)
                    realized_ret_pct = net_pnl / (buy_p * int(pos["quantity"])) * 100.0

                    conn.execute("UPDATE autotrader_accounts SET cash = cash + ?, updated_at=? WHERE market=?", (net_proceeds, now.isoformat(), market))
                    conn.execute("DELETE FROM autotrader_positions WHERE id=?", (pos["id"],))
                    conn.execute(
                        "UPDATE autotrader_order_intents SET status='SUBMITTED', broker_order_no=?, updated_at=? WHERE intent_id=?",
                        (exec_res.get("order_no"), now.isoformat(), sell_intent_id),
                    )
                    conn.execute(
                        """
                        INSERT INTO autotrader_trades (
                            intent_id, market, ticker, display_name, sector, mode, quantity,
                            buy_price, sell_price, fee_and_tax, net_pnl, return_pct, slot_fraction,
                            holding_days, exit_reason, source_run_id, opened_at, closed_at
                        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                        """,
                        (
                            sell_intent_id, market, ticker, pos.get("display_name") or ticker, pos.get("sector"),
                            self.policy.mode, int(pos["quantity"]), buy_p, round(eff_sell, 4),
                            round(buy_cost + sell_cost, 4), round(net_pnl, 4), round(realized_ret_pct, 4),
                            float(pos["slot_fraction"]), holding_days, exit_reason, pos.get("source_run_id"),
                            pos["opened_at"], now.isoformat(),
                        ),
                    )
                    msg = format_sell_telegram_message(
                        market, ticker, pos.get("display_name") or ticker, buy_p, eff_sell,
                        int(pos["quantity"]), realized_ret_pct, holding_days, exit_reason, self.policy.mode,
                    )
                    self._queue_notification(conn, market, "SELL", f"sell:{sell_intent_id}", msg, now)
                    exits_executed.append({"ticker": ticker, "quantity": int(pos["quantity"]), "return_pct": round(realized_ret_pct, 2), "reason": exit_reason})

            # Refresh holdings & daily loss circuit breaker before any new BUY
            acct = conn.execute("SELECT * FROM autotrader_accounts WHERE market=?", (market,)).fetchone()
            open_positions = [dict(r) for r in conn.execute(
                "SELECT * FROM autotrader_positions WHERE market=? AND mode=?", (market, self.policy.mode)
            )]
            held_tickers = {p["ticker"].upper() for p in open_positions}
            sector_counts: dict[str, int] = {}
            for p in open_positions:
                sec = str(p.get("sector") or "").strip()
                if sec:
                    sector_counts[sec] = sector_counts.get(sec, 0) + 1

            today_prefix = local_now.date().isoformat()
            today_realized = float(
                conn.execute(
                    "SELECT COALESCE(SUM(net_pnl), 0.0) FROM autotrader_trades WHERE market=? AND mode=? AND substr(closed_at,1,10)=?",
                    (market, self.policy.mode, today_prefix),
                ).fetchone()[0]
                or 0.0
            )
            nav_now = float(acct["cash"]) + sum(float(p["current_price"]) * int(p["quantity"]) for p in open_positions)
            daily_loss_hit = nav_now > 0 and (today_realized / nav_now * 100.0) <= -self.policy.max_daily_loss_pct
            if daily_loss_hit:
                blockers.append("DAILY_LOSS_CIRCUIT_BREAKER")

            unknown_count = int(
                conn.execute(
                    "SELECT COUNT(*) FROM autotrader_order_intents WHERE market=? AND mode=? AND status='UNKNOWN'",
                    (market, self.policy.mode),
                ).fetchone()[0]
                or 0
            )
            if unknown_count > 0:
                blockers.append("UNRESOLVED_UNKNOWN_ORDER")

            # Ingest candidates from latest run into queue (if closed) or direct evaluation
            source_run_id = str((manifest or {}).get("run_id") or "")
            if safe and not daily_loss_hit and unknown_count == 0 and candidate_list and source_run_id:
                for cand in candidate_list:
                    if not isinstance(cand, Mapping):
                        continue
                    ticker = str(cand.get("canonical_ticker") or "").strip().upper()
                    if not ticker or ticker in held_tickers:
                        continue
                    from tradingagents.performance.price_evidence import native_reference
                    dh = cand.get("data_health") if isinstance(cand.get("data_health"), Mapping) else {}
                    pm = cand.get("position_metrics") if isinstance(cand.get("position_metrics"), Mapping) else {}
                    verified_ref, _ = native_reference(dh.get("price_reference"), market, now.isoformat())
                    dh_curr = str(dh.get("currency") or dh.get("price_currency") or "").strip().upper()
                    pm_curr = str(pm.get("currency") or pm.get("price_currency") or "").strip().upper()
                    expected_curr = MARKET_CURRENCIES[market]
                    ref_price = verified_ref.price if verified_ref else None
                    if ref_price is None or ref_price <= 0:
                        if not dh_curr or dh_curr == expected_curr:
                            ref_price = _num(dh.get("last_price")) or _num(dh.get("current_price"))
                    if (ref_price is None or ref_price <= 0) and market == "KR" and (not pm_curr or pm_curr == "KRW"):
                        ref_price = _num(pm.get("current_price"))
                    if (ref_price is None or ref_price <= 0) and is_open:
                        ref_price = self.quote_loader(market, ticker, now)
                    if ref_price is None or ref_price <= 0:
                        continue
                    sec = str(cand.get("sector") or "").strip()
                    gate = evaluate_prism_buy_gate(
                        cand,
                        current_price=ref_price,
                        regime=regime,
                        slots_used=len(open_positions),
                        max_slots=self.policy.max_slots,
                        same_sector_count=sector_counts.get(sec, 0),
                        max_same_sector=self.policy.max_same_sector,
                        policy=self.policy,
                    )
                    if not gate.allowed:
                        continue
                    intent_id = hashlib.sha256(f"BUY|{market}|{self.policy.mode}|{source_run_id}|{ticker}".encode()).hexdigest()[:32]
                    existing_pending = conn.execute(
                        "SELECT status FROM autotrader_pending_entries WHERE intent_id=?", (intent_id,)
                    ).fetchone()
                    if existing_pending is not None:
                        continue
                    max_entry = round(ref_price * (1.0 + self.policy.buy_max_premium_pct / 100.0), 4)
                    expires = (now + timedelta(hours=self.policy.session_entry_ttl_hours)).isoformat()
                    conn.execute(
                        """
                        INSERT INTO autotrader_pending_entries (
                            intent_id, market, ticker, display_name, sector, mode,
                            reference_price, max_entry_price, stop_loss, target_price,
                            slot_fraction, buy_score, regime, source_run_id, status,
                            created_at, expires_at, updated_at
                        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                        """,
                        (
                            intent_id, market, ticker, str(cand.get("display_name") or ticker), sec,
                            self.policy.mode, ref_price, max_entry, gate.stop_loss, gate.target_price,
                            gate.slot_fraction, gate.effective_score, gate.regime, source_run_id,
                            "QUEUED", now.isoformat(), expires, now.isoformat(),
                        ),
                    )
                    entries_queued.append(ticker)

            # Execute queued entries if regular session is open!
            if is_open and safe and not daily_loss_hit and unknown_count == 0:
                queued_rows = [dict(r) for r in conn.execute(
                    "SELECT * FROM autotrader_pending_entries WHERE market=? AND mode=? AND status='QUEUED' "
                    "ORDER BY buy_score DESC, created_at ASC",
                    (market, self.policy.mode),
                )]
                for item in queued_rows:
                    if len(open_positions) >= self.policy.max_slots:
                        break
                    ticker = item["ticker"]
                    if ticker in held_tickers:
                        conn.execute("UPDATE autotrader_pending_entries SET status='SKIPPED_HELD', updated_at=? WHERE intent_id=?", (now.isoformat(), item["intent_id"]))
                        continue
                    sec = str(item.get("sector") or "").strip()
                    if sec and sec.upper() != "UNKNOWN" and sector_counts.get(sec, 0) >= self.policy.max_same_sector:
                        continue
                    live_price = self.quote_loader(market, ticker, now)
                    if live_price is None or live_price <= 0:
                        continue
                    if live_price > float(item["max_entry_price"]) or live_price <= float(item["stop_loss"]):
                        conn.execute(
                            "UPDATE autotrader_pending_entries SET status='CANCELLED_PRICE_BAND', updated_at=? WHERE intent_id=?",
                            (now.isoformat(), item["intent_id"]),
                        )
                        continue
                    acct_cash = float(conn.execute("SELECT cash FROM autotrader_accounts WHERE market=?", (market,)).fetchone()[0])
                    slot_unit = nav_now / float(self.policy.max_slots)
                    order_budget = min(acct_cash * 0.98, slot_unit * float(item["slot_fraction"]))
                    slip = (self.policy.slippage_bps / 10_000.0) if self.policy.mode == "shadow" else 0.0
                    eff_buy = live_price * (1.0 + slip)
                    unit_cost = eff_buy * (1.0 + self.policy.fee_bps / 10_000.0)
                    qty = whole_share_quantity(order_budget, unit_cost)
                    if qty <= 0 and unit_cost <= min(acct_cash * 0.95, nav_now * float(self.policy.one_share_nav_ceiling)):
                        qty = 1
                    if qty <= 0:
                        conn.execute(
                            "UPDATE autotrader_pending_entries SET status='SKIPPED_BUDGET', updated_at=? WHERE intent_id=?",
                            (now.isoformat(), item["intent_id"]),
                        )
                        continue
                    conn.execute(
                        "INSERT OR REPLACE INTO autotrader_order_intents VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                        (item["intent_id"], market, ticker, "BUY", self.policy.mode, qty, eff_buy, None, "SUBMITTING", "PRISM_BUY_GATE_PASS", now.isoformat(), now.isoformat()),
                    )
                    conn.commit()
                    conn.execute("BEGIN IMMEDIATE")
                    try:
                        exec_res = self.broker_executor(self.policy.mode, market, "BUY", ticker, qty, live_price, now)
                    except Exception as exc:
                        conn.execute(
                            "UPDATE autotrader_order_intents SET status='UNKNOWN', reason=?, updated_at=? WHERE intent_id=?",
                            (type(exc).__name__, now.isoformat(), item["intent_id"]),
                        )
                        conn.execute(
                            "UPDATE autotrader_pending_entries SET status='UNKNOWN_OUTCOME', updated_at=? WHERE intent_id=?",
                            (now.isoformat(), item["intent_id"]),
                        )
                        blockers.append(f"ORDER_OUTCOME_UNKNOWN:{ticker}")
                        continue
                    if not exec_res.get("accepted"):
                        conn.execute("UPDATE autotrader_order_intents SET status='FAILED', updated_at=? WHERE intent_id=?", (now.isoformat(), item["intent_id"]))
                        continue

                    total_cost = eff_buy * qty * (1.0 + self.policy.fee_bps / 10_000.0)
                    conn.execute("UPDATE autotrader_accounts SET cash = cash - ?, updated_at=? WHERE market=?", (total_cost, now.isoformat(), market))
                    conn.execute(
                        """
                        INSERT INTO autotrader_positions (
                            market, ticker, display_name, sector, mode, quantity, buy_price,
                            current_price, peak_price, stop_loss, target_price, slot_fraction,
                            runner_active, buy_score, regime, source_run_id, opened_at, updated_at
                        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,0,?,?,?,?,?)
                        """,
                        (
                            market, ticker, item.get("display_name") or ticker, sec, self.policy.mode,
                            qty, round(eff_buy, 4), round(eff_buy, 4), round(eff_buy, 4),
                            float(item["stop_loss"]), float(item["target_price"]), float(item["slot_fraction"]),
                            float(item["buy_score"]), item["regime"], item["source_run_id"],
                            now.isoformat(), now.isoformat(),
                        ),
                    )
                    conn.execute("UPDATE autotrader_pending_entries SET status='EXECUTED', updated_at=? WHERE intent_id=?", (now.isoformat(), item["intent_id"]))
                    conn.execute(
                        "UPDATE autotrader_order_intents SET status='SUBMITTED', broker_order_no=?, updated_at=? WHERE intent_id=?",
                        (exec_res.get("order_no"), now.isoformat(), item["intent_id"]),
                    )
                    rr = (float(item["target_price"]) - eff_buy) / max(eff_buy - float(item["stop_loss"]), 1e-9)
                    gate_summary = PrismBuyGateResult(
                        True, float(item["buy_score"]), 5.5, item["regime"], float(item["stop_loss"]),
                        float(item["target_price"]), round(rr, 2),
                        round((eff_buy - float(item["stop_loss"])) / eff_buy * 100.0, 2),
                        float(item["slot_fraction"]), (),
                    )
                    msg = format_buy_telegram_message(market, ticker, item.get("display_name") or ticker, eff_buy, qty, gate_summary, self.policy.mode)
                    self._queue_notification(conn, market, "BUY", f"buy:{item['intent_id']}", msg, now)
                    held_tickers.add(ticker)
                    open_positions.append({"ticker": ticker, "current_price": eff_buy, "quantity": qty})
                    if sec:
                        sector_counts[sec] = sector_counts.get(sec, 0) + 1
                    entries_executed.append({"ticker": ticker, "quantity": qty, "buy_price": round(eff_buy, 4)})

            # Record daily equity curve point
            final_acct = conn.execute("SELECT * FROM autotrader_accounts WHERE market=?", (market,)).fetchone()
            final_pos = [dict(r) for r in conn.execute("SELECT * FROM autotrader_positions WHERE market=? AND mode=?", (market, self.policy.mode))]
            pos_val = sum(float(p["current_price"]) * int(p["quantity"]) for p in final_pos)
            cash_val = float(final_acct["cash"])
            nav_val = cash_val + pos_val
            init_val = float(final_acct["initial_capital"])
            ret_val = (nav_val - init_val) / init_val * 100.0 if init_val > 0 else 0.0
            conn.execute(
                """
                INSERT OR REPLACE INTO autotrader_equity_curve
                (market, mode, session_date, observed_at, nav, cash, positions_value, return_pct, open_slots)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    market, self.policy.mode, local_now.date().isoformat(), now.isoformat(),
                    round(nav_val, 2), round(cash_val, 2), round(pos_val, 2), round(ret_val, 2), len(final_pos),
                ),
            )
            conn.commit()

        metrics = compute_performance_metrics(self.db_path, market, self.policy.mode)
        promotion = evaluate_live_promotion_gate(self.db_path, market, min_vts_trades=self.policy.min_vts_trades_for_live)
        receipt = {
            "schema": AUTOTRADER_SCHEMA,
            "market": market,
            "mode": self.policy.mode,
            "source_revision": os.getenv("TRADINGAGENTS_SOURCE_SHA"),
            "live_orders_enabled": False,
            "checked_at": now.isoformat(),
            "session_open": is_open,
            "source_run_id": source_run_id or None,
            "blockers": blockers,
            "entries_queued": entries_queued,
            "entries_executed": entries_executed,
            "exits_executed": exits_executed,
            "metrics": metrics,
            "promotion_gate": promotion,
        }
        atomic_write_json(self.state_dir / f"autotrader-{market.lower()}-status.json", receipt)
        return receipt

    def tick_all(self) -> dict[str, Any]:
        kr = self.tick_market("KR")
        us = self.tick_market("US")
        now = self._now()
        summary = {
            "schema": AUTOTRADER_SCHEMA,
            "mode": self.policy.mode,
            "live_orders_enabled": bool(kr["live_orders_enabled"] or us["live_orders_enabled"]),
            "checked_at": now.isoformat(),
            "markets": {"KR": kr, "US": us},
        }
        atomic_write_json(self.archive_dir / "paper" / "autotrader-status.json", summary)
        return summary


def load_autotrader_policy(state_dir: Path) -> AutotraderPolicy:
    base = Path(state_dir)
    direct = base / "enabled.json"
    nested = base / "autotrader" / "enabled.json"
    config_path = direct if (base.name == "autotrader" or (direct.is_file() and not nested.is_file())) else nested
    if not config_path.is_file():
        return AutotraderPolicy(enabled=False)
    raw = json.loads(config_path.read_text(encoding="utf-8-sig"))
    if not isinstance(raw, dict):
        return AutotraderPolicy(enabled=False)
    allowed = set(AutotraderPolicy.__dataclass_fields__.keys())
    filtered = {k: v for k, v in raw.items() if k in allowed}
    return AutotraderPolicy(**filtered)


def run_autotrader_tick(archive_dir: Path, state_dir: Path, **kwargs: Any) -> dict[str, Any]:
    """Load policy from state_dir and execute a full KR+US PrismAutoTrader tick."""
    base = Path(state_dir)
    lane_dir = base if base.name == "autotrader" else (base / "autotrader")
    lane_dir.mkdir(parents=True, exist_ok=True)
    policy = kwargs.pop("policy", None) or load_autotrader_policy(lane_dir)
    trader = PrismAutoTrader(Path(archive_dir), lane_dir, policy=policy, **kwargs)
    return trader.tick_all()
