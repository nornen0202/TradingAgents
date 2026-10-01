"""Evidence-bound, whole-share scenarios for the investor strategy table.

This module does not approve or transmit orders. Prices are declared research
levels, and all quantities are scenarios at those levels, never market orders.
The raw account input is deliberately not returned or copied into the payload.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from math import floor, isfinite
from pathlib import Path
from typing import Any

from tradingagents.execution.risk_trigger import risk_trigger


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _items(value: Any) -> list[Any] | tuple[Any, ...]:
    return value if isinstance(value, (list, tuple)) else []


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        result = float(value)
        return result if isfinite(result) else None
    except (TypeError, ValueError):
        return None


def _positive(value: Any) -> float | None:
    number = _number(value)
    return number if number is not None and number > 0 else None


def _identity(value: Any) -> str:
    return str(value or "").strip().upper().removesuffix(".KS").removesuffix(".KQ")


def _side(value: Any) -> str | None:
    code = str(value or "").upper()
    if code in {
        "BUY",
        "ADD",
        "STARTER",
        "BUY_NOW",
        "ADD_NOW",
        "STARTER_NOW",
        "BUY_IF_TRIGGERED",
        "ADD_IF_TRIGGERED",
        "STARTER_IF_TRIGGERED",
    }:
        return "BUY"
    if code in {
        "SELL",
        "REDUCE",
        "EXIT",
        "STOP_LOSS",
        "TAKE_PROFIT",
        "REDUCE_RISK",
        "TRIM_TO_FUND",
        "SELL_NOW",
        "REDUCE_NOW",
        "TRIM_NOW",
        "EXIT_NOW",
        "STOP_LOSS_NOW",
        "TAKE_PROFIT_NOW",
        "SELL_IF_TRIGGERED",
        "REDUCE_IF_TRIGGERED",
        "TRIM_IF_TRIGGERED",
        "EXIT_IF_TRIGGERED",
        "STOP_LOSS_IF_TRIGGERED",
        "TAKE_PROFIT_IF_TRIGGERED",
    }:
        return "SELL"
    return None


def _timestamp(value: Any) -> datetime | None:
    try:
        result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return result if result.tzinfo is not None else None
    except (TypeError, ValueError):
        return None


def _pending_constraints(snapshot: dict[str, Any]) -> tuple[bool, bool, set[str]]:
    """Do not assume an absent pending-order response means no open orders."""
    orders = snapshot.get("pending_orders")
    if not isinstance(orders, (list, tuple)):
        return True, False, set()
    unknown, has_buy, tickers = False, False, set()
    for order in orders:
        if not isinstance(order, dict):
            unknown = True
            continue
        remaining = _number(order.get("remaining_qty"))
        if remaining is None or remaining < 0:
            unknown = True
            continue
        if remaining == 0:
            continue
        ticker = _identity(order.get("canonical_ticker"))
        side = str(order.get("side") or "").upper()
        if not ticker or side not in {"BUY", "SELL"}:
            unknown = True
            continue
        tickers.add(ticker)
        has_buy = has_buy or side == "BUY"
    return unknown, has_buy, tickers


def _cost_profile(config: dict[str, Any] | None, market: str) -> dict[str, Any]:
    if config is None:
        path = (
            Path(__file__).resolve().parents[2]
            / "config"
            / "account_cost_replay_20260929.json"
        )
        try:
            config = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            config = {}
    config = _mapping(config)
    markets = _mapping(config.get("markets"))
    market_config = _mapping(markets.get(market))
    stock_config = _mapping(config.get("stock_cost_illustrations"))
    spread = _number(market_config.get("fx_base_spread"))
    discount = _number(market_config.get("fx_discount"))
    effective_spread = (
        spread * (1 - discount)
        if spread is not None
        and discount is not None
        and 0 <= spread < 1
        and 0 <= discount <= 1
        else None
    )
    return {
        "commission_rate": _number(market_config.get("commission_rate")),
        "sell_levy_rate": _number(
            stock_config.get("kr_common_stock_sell_tax")
            if market == "KR"
            else market_config.get("sell_levy_rate")
        ),
        "fx_spread_scenario": effective_spread,
        "evidence_as_of": config.get("evidence_as_of"),
    }


def _price_level(
    row: dict[str, Any], action: dict[str, Any], side: str, currency: str
) -> dict[str, Any]:
    thesis = _mapping(row.get("thesis"))
    if side == "SELL":
        level = _mapping(action.get("risk_action_level")) or _mapping(
            thesis.get("risk_action_level")
        )
        source = (
            "portfolio_action.risk_action_level"
            if action.get("risk_action_level")
            else "thesis.risk_action_level"
        )
    else:
        levels = _items(_mapping(thesis.get("execution_levels")).get("levels"))
        # A support/stop level is not evidence of an entry order price.
        candidates = [
            item
            for item in levels
            if isinstance(item, dict)
            and str(item.get("level_type") or "").upper() in {"PULLBACK", "BREAKOUT"}
        ]
        level = candidates[0] if candidates else {}
        source = "thesis.execution_levels"
    if not level or str(level.get("currency") or currency).upper() != currency:
        return {
            "price_low": None,
            "price_high": None,
            "price_kind": "UNAVAILABLE",
            "price_source": None,
            "price_comparator": None,
            "price_confirmation": None,
        }
    low, high, point = (
        _positive(level.get("low")),
        _positive(level.get("high")),
        _positive(level.get("price")),
    )
    if low is not None and high is not None and low > high:
        return {
            "price_low": None,
            "price_high": None,
            "price_kind": "UNAVAILABLE",
            "price_source": source,
            "price_comparator": None,
            "price_confirmation": None,
        }
    if side == "SELL":
        trigger = risk_trigger(
            str(
                action.get("risk_action") or thesis.get("risk_action") or "REDUCE_RISK"
            ),
            level,
        )
        point = trigger["price"]
        return {
            "price_low": point,
            "price_high": point,
            "price_kind": "TRIGGER",
            "price_source": source,
            "price_comparator": trigger["comparator"],
            "price_confirmation": trigger["confirmation"],
        }
    if low is not None and high is not None:
        kind = (
            "RANGE"
            if str(level.get("level_type")).upper() == "PULLBACK"
            else "TRIGGER_RANGE"
        )
    else:
        low = high = point or high or low
        kind = (
            "TRIGGER"
            if str(level.get("level_type")).upper() == "BREAKOUT"
            else "REFERENCE"
        )
    return {
        "price_low": low,
        "price_high": high,
        "price_kind": kind if high is not None else "UNAVAILABLE",
        "price_source": source,
        "price_comparator": ">="
        if str(level.get("level_type")).upper() == "BREAKOUT"
        else None,
        "price_confirmation": level.get("confirmation"),
    }


def build_trade_plan(
    market_payload: dict[str, Any],
    *,
    account_snapshot: dict[str, Any] | None = None,
    fee_config: dict[str, Any] | None = None,
    fx_krw_per_usd: float | None = None,
    fx_asof: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Build manual scenarios from explicit allocations, not free-text guesses.

    Allocation deltas are KRW. A US delta requires an independently supplied FX
    rate; current USD prices and old KRW position marks cannot establish that FX.
    All buy scenarios share one cash ledger, even when triggers are alternatives.
    Sales never replenish that ledger before an actual fill and account refresh.
    """
    market = str(market_payload.get("market") or "").upper()
    if market not in {"KR", "US"}:
        raise ValueError("trade plans support only KR and US")
    currency = "KRW" if market == "KR" else "USD"
    clock = now or datetime.now(timezone.utc)
    snapshot = _mapping(account_snapshot)
    costs = _cost_profile(fee_config, market)
    commission = costs["commission_rate"]
    if commission is not None and not 0 <= commission < 1:
        commission = None
    fx = 1.0 if market == "KR" else _positive(fx_krw_per_usd)
    fx_reserve_rate = costs["fx_spread_scenario"] if market == "US" else 0.0
    available = _number(snapshot.get("available_cash_krw"))
    buying_power = _number(snapshot.get("buying_power_krw"))
    buffer = _number(_mapping(snapshot.get("constraints")).get("min_cash_buffer_krw"))
    # Both cash and orderability must be known. In particular, 0 is evidence.
    initial_budget = (
        max(0.0, min(available, buying_power) - buffer)
        if available is not None
        and buying_power is not None
        and buffer is not None
        and buffer >= 0
        else None
    )
    cash_left = initial_budget
    pending_unknown, pending_buy, pending_tickers = _pending_constraints(snapshot)
    positions = {
        _identity(p.get("canonical_ticker")): p
        for p in _items(snapshot.get("positions"))
        if isinstance(p, dict)
    }
    shares_left: dict[str, int | None] = {}
    for ticker, position in positions.items():
        quantity, available_qty = (
            _number(position.get("quantity")),
            _number(position.get("available_qty")),
        )
        shares_left[ticker] = (
            floor(max(0, min(quantity, available_qty)))
            if quantity is not None and available_qty is not None
            else None
        )
    account_asof = snapshot.get("as_of")
    account_time = _timestamp(account_asof)
    account_fresh = (
        account_time is not None
        and 0 <= (clock - account_time).total_seconds() <= 86400
        and str(snapshot.get("snapshot_health") or "").upper() == "VALID"
    )
    rows = []
    ordered = [
        row for row in _items(market_payload.get("rows")) if isinstance(row, dict)
    ]
    ordered.sort(
        key=lambda row: (
            _number(_mapping(row.get("portfolio_action")).get("priority"))
            if _number(_mapping(row.get("portfolio_action")).get("priority"))
            is not None
            else 999,
            str(row.get("ticker") or ""),
        )
    )
    seen: set[str] = set()
    for source in ordered:
        ticker = str(source.get("ticker") or "")
        identity = _identity(ticker)
        if not identity or identity in seen:
            continue
        seen.add(identity)
        action = _mapping(source.get("portfolio_action"))
        thesis = _mapping(source.get("thesis"))
        held = source.get("is_held") is True or (
            _positive(_mapping(positions.get(identity)).get("quantity")) is not None
        )
        current_action = str(action.get("action_now") or ("HOLD" if held else "WAIT"))
        delta_now = _number(action.get("delta_krw_now"))
        delta_triggered = _number(action.get("delta_krw_if_triggered"))
        side, phase, delta = _side(current_action), "NOW", delta_now
        # HOLD + a portfolio-relative trim never becomes an immediate sell.
        if side is None or delta is None or delta == 0:
            side, phase, delta = (
                _side(action.get("action_if_triggered")),
                "CONDITIONAL",
                delta_triggered,
            )
            if (
                side is None
                and delta is not None
                and delta < 0
                and held
                and (
                    _mapping(action.get("risk_action_level"))
                    or _mapping(thesis.get("risk_action_level"))
                )
            ):
                side = "SELL"
            if side is None and str(
                thesis.get("conditional_entry_action") or ""
            ).upper() in {"STARTER", "ADD"}:
                side = "BUY"
        if side is None:
            side, phase, delta = ("HOLD" if held else "WAIT"), "OBSERVE", 0.0
        reasons: list[str] = []
        price = (
            _price_level(source, action, side, currency)
            if side in {"BUY", "SELL"}
            else {
                "price_low": None,
                "price_high": None,
                "price_kind": "NONE",
                "price_source": None,
                "price_comparator": None,
                "price_confirmation": None,
            }
        )
        quantity = None
        sizing_basis = None
        fx_budget_reserve = 0.0
        sell_fraction = (
            {"FULL_EXIT": 1.0, "PARTIAL_20": 0.2, "PARTIAL_35": 0.35}.get(
                str(action.get("sell_size_plan") or "").upper()
            )
            if side == "SELL"
            else None
        )
        structured_sell = (
            sell_fraction is not None and delta != 0 and (delta is None or delta < 0)
        )
        if side in {"HOLD", "WAIT"}:
            quantity = 0
            reasons.append(
                "현재 추가 매매 배정이 없습니다."
                if held
                else "진입 조건과 계좌 배정이 확정되지 않았습니다."
            )
        elif delta == 0:
            quantity = 0
            reasons.append("분석 방향은 있으나 배정 금액이 0원입니다.")
        elif side == "SELL" and shares_left.get(identity) == 0:
            quantity = 0
            reasons.append(
                "매도 가능한 정수 수량이 0주입니다. 소수점 보유분은 별도 확인합니다."
            )
        elif pending_unknown:
            reasons.append(
                "미체결 주문 확인이 완료되지 않아 중복 주문 수량을 산정하지 않았습니다."
            )
        elif (side == "BUY" and pending_buy) or identity in pending_tickers:
            reasons.append(
                "미체결 주문을 정리·대사하고 계좌를 갱신한 뒤 추가 매매 수량을 계산합니다."
            )
        elif delta is None and not structured_sell:
            reasons.append("계좌별 매매 배정 금액이 없어 수량을 정하지 않았습니다.")
        elif delta is not None and (
            (side == "BUY" and delta < 0) or (side == "SELL" and delta > 0)
        ):
            reasons.append("행동과 배정 금액의 방향이 달라 재검토가 필요합니다.")
        elif price["price_high"] is None:
            reasons.append(
                "구조화된 진입·위험 가격이 없어 임의의 주문 범위를 만들지 않았습니다."
            )
        elif structured_sell:
            available_shares = shares_left.get(identity)
            held_shares = _number(_mapping(positions.get(identity)).get("quantity"))
            if available_shares is None or held_shares is None:
                reasons.append("보유 수량과 매도 가능 수량이 확인되지 않았습니다.")
            else:
                quantity = min(
                    available_shares, floor(max(held_shares, 0) * sell_fraction)
                )
                sizing_basis = f"STRUCTURED_{str(action.get('sell_size_plan')).upper()}_OF_HELD_SHARES"
                if fx is not None and delta is not None:
                    quantity = min(
                        quantity, floor(abs(delta) / (price["price_high"] * fx))
                    )
                elif delta is not None:
                    reasons.append(
                        "명시된 보유분 매도 비율 기준 수량입니다. 원화 배정액 상한은 환율 확인 후 대조합니다."
                    )
                shares_left[identity] = available_shares - quantity
                if quantity == 0:
                    reasons.append(
                        "명시된 비율·배정액·매도 가능 수량이 정수 1주에 못 미칩니다."
                    )
        elif fx is None:
            reasons.append("원화 배정액을 달러 수량으로 환산할 기준 환율이 없습니다.")
        elif side == "BUY" and fx_reserve_rate is None:
            reasons.append(
                "환전 비용 기준이 없어 원화 매수 예산을 산정하지 않았습니다."
            )
        elif commission is None:
            reasons.append(
                "수수료 기준이 없어 비용을 포함한 수량을 계산하지 않았습니다."
            )
        else:
            unit_krw = price["price_high"] * fx
            sizing_basis = "EXPLICIT_KRW_ALLOCATION_AT_DECLARED_LEVEL"
            if side == "BUY":
                if buffer is None or buffer < 0:
                    reasons.append(
                        "최소 보유 현금 기준이 없어 매수 수량을 산정하지 않았습니다."
                    )
                elif cash_left is None:
                    reasons.append(
                        "가용 현금·주문가능금액 확인 전에는 매수 수량을 정하지 않습니다."
                    )
                else:
                    buy_unit_cost = unit_krw * (1 + commission) * (1 + fx_reserve_rate)
                    requested = floor(abs(delta) / buy_unit_cost)
                    quantity = min(requested, floor(cash_left / buy_unit_cost))
                    cash_left = max(0, cash_left - quantity * buy_unit_cost)
                    fx_budget_reserve = (
                        quantity * unit_krw * (1 + commission) * fx_reserve_rate
                    )
                    if quantity < requested:
                        reasons.append(
                            "앞선 매수 계획의 비용을 차감한 잔여 현금으로 수량을 제한했습니다."
                        )
            else:
                available_shares = shares_left.get(identity)
                if available_shares is None:
                    reasons.append("보유 수량과 매도 가능 수량이 확인되지 않았습니다.")
                else:
                    requested = floor(abs(delta) / unit_krw)
                    quantity = min(requested, available_shares)
                    shares_left[identity] = available_shares - quantity
                    if quantity < requested:
                        reasons.append("매도 가능 정수 수량으로 제한했습니다.")
            if quantity == 0:
                reasons.append(
                    "배정 금액·잔여 현금 또는 매도 가능 수량이 1주 기준에 못 미칩니다."
                )
        if side in {"BUY", "SELL"} and price["price_kind"] in {
            "TRIGGER",
            "TRIGGER_RANGE",
            "REFERENCE",
        }:
            reasons.append(
                "표시 가격은 조건 기준값이며 체결 보장 범위가 아닙니다. 조건 충족 후 호가와 수량을 다시 계산합니다."
            )
        if side in {"BUY", "SELL"} and not account_fresh:
            reasons.append(
                "계좌 시점·상태를 갱신한 뒤 주문가능 현금과 수량을 다시 확인합니다."
            )
        fx_time = _timestamp(fx_asof)
        fx_fresh = market == "KR" or (
            fx_time is not None and 0 <= (clock - fx_time).total_seconds() <= 86400
        )
        if side in {"BUY", "SELL"} and market == "US" and not fx_fresh:
            reasons.append(
                "환율 시점 확인 후 원화 배정액과 달러 매매 금액을 다시 대조합니다."
            )
        levy = costs["sell_levy_rate"] if side == "SELL" else 0.0
        if (
            side == "SELL"
            and market == "KR"
            and str(source.get("asset_type") or "").lower() == "domestic_equity_etf"
        ):
            levy = 0.0
        if levy is not None and not 0 <= levy < 1:
            levy = None
        low, high = price["price_low"], price["price_high"]
        gross_low = quantity * low if quantity is not None and low is not None else None
        gross_high = (
            quantity * high if quantity is not None and high is not None else None
        )
        fee_rate = (
            commission + levy if commission is not None and levy is not None else None
        )
        fees = (
            gross_high * fee_rate
            if gross_high is not None and fee_rate is not None
            else None
        )
        cash_effect = (
            (-(gross_high + fees) if side == "BUY" else gross_high - fees)
            if fees is not None
            else None
        )
        if quantity == 0:
            gross_low = gross_high = fees = cash_effect = 0.0
        valid_until = _mapping(source.get("quality")).get("row_valid_until")
        valid_time = _timestamp(valid_until)
        status = "OBSERVE" if phase == "OBSERVE" else "CONDITIONAL"
        market_expiry = _timestamp(
            _mapping(market_payload.get("guardrails")).get("valid_until")
        )
        market_current = (
            market_payload.get("source_health") == "OK"
            and market_expiry is not None
            and market_expiry > clock
            and _mapping(market_payload.get("guardrails")).get("expired_at_build")
            is not True
        )
        if phase != "OBSERVE" and (
            not account_fresh
            or not fx_fresh
            or not market_current
            or valid_time is None
            or valid_time <= clock
        ):
            status = "RECHECK"
        if side in {"BUY", "SELL"} and (quantity is None or quantity == 0):
            status = "UNSIZED" if quantity is None else "NO_QUANTITY"
        constraints = _mapping(snapshot.get("constraints"))
        constraint_reasons = []
        target_weight = action.get(
            "target_weight_now" if phase == "NOW" else "target_weight_if_triggered"
        )
        if quantity is not None and quantity > 0:
            min_trade = _number(constraints.get("min_trade_krw"))
            if (
                min_trade is not None
                and fx is not None
                and gross_high is not None
                and gross_high * fx < min_trade
            ):
                constraint_reasons.append(
                    f"계획 거래대금이 계좌 최소 거래금액 {min_trade:,.0f}원 미만입니다. 표시 수량은 참고값이며 실행 수량을 재검토합니다."
                )
            order_limit = _number(constraints.get("max_order_count_per_day"))
            turnover_limit = _number(constraints.get("max_daily_turnover_ratio"))
            weight_limit = _number(constraints.get("max_single_name_weight"))
            if order_limit is not None and order_limit <= 0:
                constraint_reasons.append(
                    "계좌 일일 주문 허용 건수가 0건입니다. 주문 한도를 재확인합니다."
                )
            if turnover_limit is not None and turnover_limit <= 0:
                constraint_reasons.append(
                    "계좌 일일 회전율 허용 한도가 0입니다. 주문 한도를 재확인합니다."
                )
            if (
                side == "BUY"
                and weight_limit is not None
                and _number(target_weight) is not None
                and _number(target_weight) > weight_limit
            ):
                constraint_reasons.append(
                    "원천 목표 비중이 계좌 종목별 비중 상한을 넘습니다. 배정을 재검토합니다."
                )
        if constraint_reasons:
            reasons = constraint_reasons + reasons
            status = "RECHECK"
        condition = (
            source.get("risk_condition_ko")
            if side == "SELL"
            else source.get("execution_condition_ko")
        )
        rows.append(
            {
                "id": f"{ticker}:{'RISK' if side == 'SELL' else 'ENTRY' if side == 'BUY' else 'OBSERVE'}",
                "ticker": ticker,
                "display_name": source.get("display_name") or ticker,
                "action": side,
                "action_label": {
                    "BUY": "매수",
                    "SELL": "매도·축소",
                    "HOLD": "보유 유지",
                    "WAIT": "대기",
                }[side],
                "action_now": current_action,
                "phase": phase,
                "quantity": quantity,
                "quantity_basis": sizing_basis,
                **price,
                "currency": currency,
                "estimated_gross_low": gross_low,
                "estimated_gross_high": gross_high,
                "estimated_fees": fees,
                "estimated_net_cash": cash_effect,
                "fx_budget_reserve_krw": fx_budget_reserve,
                "commission_rate": commission,
                "sell_levy_rate": levy,
                "target_weight": target_weight,
                "constraint_review_required": bool(constraint_reasons),
                "condition": condition,
                "trigger_conditions": ([condition] if condition else [])
                if side == "SELL"
                else _items(action.get("trigger_conditions")),
                "status": status,
                "status_label": {
                    "OBSERVE": "매매 없음",
                    "CONDITIONAL": "조건 확인 후 재계산",
                    "RECHECK": "최신 정보 재확인",
                    "UNSIZED": "수량 산정 보류",
                    "NO_QUANTITY": "계획 수량 0주",
                }[status],
                "reasons": reasons,
                "account_asof": account_asof,
                "price_asof": thesis.get("analysis_asof")
                or thesis.get("decision_asof"),
                "quote_asof": source.get("market_data_asof"),
                "valid_until": valid_until,
                "source": "CURRENT_PORTFOLIO_ALLOCATION_AND_STRUCTURED_THESIS",
                "order_ready": False,
            }
        )
    return {
        "schema": "tradingagents.manual-trade-plan/v1",
        "market": market,
        "currency": currency,
        "account_asof": account_asof,
        "account_fresh": account_fresh,
        "fx_krw_per_usd": fx if market == "US" else None,
        "fx_asof": fx_asof if market == "US" else None,
        "fee_evidence_asof": costs["evidence_as_of"],
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "buy_count": sum(r["action"] == "BUY" for r in rows),
            "sell_count": sum(r["action"] == "SELL" for r in rows),
            "sized_count": sum(
                r["quantity"] is not None and r["quantity"] > 0 for r in rows
            ),
            "buy_budget_used_krw": initial_budget - cash_left
            if initial_budget is not None and cash_left is not None
            else None,
        },
        "assumptions": [
            "기존 계좌 배정액을 가격 조건에 대입한 수동 매매 계획이며 주문 승인이 아닙니다.",
            "정수 수량으로 내림하며 매도 예정 대금은 매수 재원에 미리 더하지 않습니다.",
            "가격 범위의 상단과 수수료를 적용해 매수 예산을 차감합니다.",
            "호가 단위·슬리피지·개인별 양도세·실제 수수료 반올림은 주문 전 확인합니다.",
            "조건부 계획의 일일 주문 건수·회전율·비중 한도는 체결 순서와 당일 거래를 반영해 다시 확인합니다.",
            (
                "예상 달러 거래금액과 환전 비용은 구분합니다. 달러 현금 보유 여부를 확인하기 전에는 "
                f"편도 환전 비용 가정 {fx_reserve_rate * 100:.2f}%를 원화 매수 예산에 추가로 유보합니다."
                if market == "US" and fx_reserve_rate is not None
                else "환전 비용 기준이 확인되지 않아 원화 매수 예산을 계산하지 않습니다."
                if market == "US"
                else "국내 자산 분류가 없는 매도는 일반주식 거래세로 보수적으로 추정합니다."
            ),
        ],
    }
