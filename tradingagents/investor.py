"""Deterministic investment planning aids; never authorizes or submits an order."""

from __future__ import annotations

import argparse
import json
import math
from typing import Any, Mapping

from tradingagents.schemas import parse_structured_decision, StructuredDecisionValidationError


def _number(value, *, positive=False):
    if isinstance(value, bool):
        raise ValueError("A finite number is required")
    number = float(value)
    if not math.isfinite(number) or number < 0 or (positive and number == 0):
        raise ValueError("A finite non-negative number is required")
    return number


def trade_economics(entry: float, stop: float, target: float, *, cost_bps: float = 10) -> dict:
    entry, stop, target = (_number(value, positive=True) for value in (entry, stop, target))
    fee = _number(cost_bps) / 10000
    if not stop < entry < target or fee >= 1:
        raise ValueError("Long-only plan requires stop < entry < target and costs below 100%")
    risk = entry * (1 + fee) - stop * (1 - fee)
    reward = target * (1 - fee) - entry * (1 + fee)
    return {
        "entry": entry, "stop": stop, "target": target,
        "cost_bps_per_side": cost_bps, "risk_per_share": risk,
        "reward_per_share": reward, "reward_risk_ratio": reward / risk,
        "break_even_win_rate": risk / (risk + reward) if reward > 0 else None,
        "stop_distance_pct": (entry - stop) / entry * 100,
        "target_distance_pct": (target - entry) / entry * 100,
    }


def position_size(*, capital: float, cash: float, entry: float, stop: float,
                  risk_fraction: float = 0.005, max_position_fraction: float = 0.10,
                  existing_position_value: float = 0, cost_bps: float = 10) -> dict:
    """Whole-share ceiling under cash, incremental weight and planned-loss budgets.

    All amounts must be in the same currency. Gap losses can exceed stop risk.
    Risk budget applies to this proposed order, not total portfolio risk.
    """
    capital, cash, existing = (_number(v) for v in (capital, cash, existing_position_value))
    entry, stop = (_number(v, positive=True) for v in (entry, stop))
    risk_fraction, cap = (_number(v) for v in (risk_fraction, max_position_fraction))
    fee = _number(cost_bps) / 10000
    if risk_fraction > 1 or cap > 1 or fee >= 1 or stop >= entry:
        raise ValueError("Invalid risk/weight/cost bounds or long-only stop")
    per_share = entry * (1 + fee)
    risk_per_share = per_share - stop * (1 - fee)
    loss_budget = capital * risk_fraction
    room = max(0, capital * cap - existing)
    bounds = {"cash": math.floor(cash / per_share), "position_cap": math.floor(room / per_share),
              "loss_budget": math.floor(loss_budget / risk_per_share)}
    shares = min(bounds.values())
    return {"shares": shares, "estimated_outlay": shares * per_share,
            "planned_stop_loss": shares * risk_per_share, "loss_budget": loss_budget,
            "binding_constraints": [key for key, value in bounds.items() if value == shares],
            "order_authorized": False}


def build_investor_playbook(state: Mapping[str, Any], *, cost_bps: float = 10) -> dict:
    raw = (state.get("risk_debate_state") or {}).get("judge_decision") or state.get("final_trade_decision")
    base = {"schema_version": 1, "as_of": state.get("trade_date"), "order_authorized": False,
            "cost_assumption_bps_per_side": cost_bps}
    try:
        decision = parse_structured_decision(raw)
    except (StructuredDecisionValidationError, TypeError, ValueError):
        return {**base, "status": "REVIEW", "reason": "invalid_decision", "economics": None}
    if "CODEX_PROVIDER_UNAVAILABLE" in decision.risk_action_reason_codes:
        return {**base, "status": "REVIEW", "reason": "decision_unvalidated", "economics": None}
    levels = decision.execution_levels.levels
    def prices(kinds, side):
        return [(level.high if side == "high" else level.low) or level.price
                for level in levels if level.level_type.value in kinds]
    entries = prices({"BREAKOUT", "PULLBACK"}, "high")
    stops = prices({"STOP_LOSS", "INVALIDATION"}, "low")
    targets = prices({"TAKE_PROFIT", "RESISTANCE"}, "low")
    # Do not silently combine alternative entry plans or mix currencies.
    currencies = {level.currency.upper() for level in levels if level.currency}
    unique_entries = set(entries)
    economics, reason = None, "missing_or_ambiguous_levels"
    if len(unique_entries) == 1 and len(currencies) <= 1:
        entry = entries[0]
        try:
            valid_stops = [v for v in stops if v is not None and 0 < v < entry]
            valid_targets = [v for v in targets if v is not None and v > entry]
            if valid_stops and valid_targets:
                economics = trade_economics(entry, min(valid_stops), min(valid_targets), cost_bps=cost_bps)
                reason = "costs_exceed_reward" if economics["reward_per_share"] <= 0 else "scenario_only"
        except (TypeError, ValueError):
            pass
    return {**base, "status": "CONDITIONAL" if economics else "REVIEW", "reason": reason,
            "rating": decision.rating.value, "entry_action": decision.entry_action.value,
            "risk_action": decision.risk_action.value, "currency": next(iter(currencies), (state.get("instrument_profile") or {}).get("currency", "")),
            "confidence_is_probability": False, "economics": economics,
            "entry_condition": decision.entry_logic, "exit_condition": decision.exit_logic,
            "invalidators": list(decision.invalidators), "watchlist_triggers": list(decision.watchlist_triggers)}


def render_investor_playbook(plan: dict, *, language: str = "Korean") -> str:
    korean = language.lower() in {"korean", "ko", "한국어"}
    if not korean:
        lines = ["## Before investing", "", "This is a conditional plan, not order approval. Confirm current price, liquidity and the entry conditions first.",
                 "Model confidence is evidence strength, not a calibrated chance of profit."]
        if plan.get("reason") in {"invalid_decision", "decision_unvalidated"}:
            lines += ["**Analysis requires review:** no validated decision was produced. Rerun the analysis; this is not a HOLD recommendation."]
        if plan.get("economics"):
            e = plan["economics"]
            lines += [f"- Scenario entry / stop / target: {e['entry']:,.2f} / {e['stop']:,.2f} / {e['target']:,.2f} {plan.get('currency', '')}",
                      f"- After assumed costs: reward/risk {e['reward_risk_ratio']:.2f}; planned loss per share {e['risk_per_share']:,.2f}."]
        else:
            lines += ["- Price evidence is missing or ambiguous. Review before sizing a position."]
        lines += [f"- Cost assumption: {plan['cost_assumption_bps_per_side']:g} bps per side; replace with actual fees, spread and slippage. Taxes and FX are excluded.",
                  "- Size = minimum of cash capacity, remaining position limit, and loss budget / loss per share. Stops do not guarantee an execution price.",
                  "- Compare the same holding period against a regional diversified ETF and cash; verify earnings and other event dates."]
        return "\n".join(lines)
    lines = ["## 투자 전 한눈에 확인", "", "아래 가격은 조건부 계획입니다. 현재 가격·거래량·진입 조건을 다시 확인해야 하며, 이 표만으로 매수가 승인되지는 않습니다.",
             "AI 확신도는 근거의 강도를 뜻하며 수익이 날 확률이 아닙니다."]
    if plan.get("reason") in {"invalid_decision", "decision_unvalidated"}:
        lines += ["**분석 재검토 필요:** 검증된 최종 판단을 얻지 못했습니다. 분석을 다시 실행해야 하며, 이를 보유 유지 추천으로 해석하면 안 됩니다."]
    if plan.get("as_of"):
        lines += [f"근거 기준일: {plan['as_of']}. 이후 가격 변화는 별도 확인이 필요합니다."]
    entries = {"NONE": "새 매수 계획 없음", "WAIT": "조건 충족 전 대기", "STARTER": "조건부 소액 분할 진입", "ADD": "조건부 추가 매수", "EXIT": "보유 정리 검토"}
    risks = {"NONE": "별도 축소 판단 없음", "HOLD": "보유 유지", "TRIM_TO_FUND": "다른 투자 재원 확보용 일부 축소", "REDUCE_RISK": "위험을 줄이기 위한 축소", "TAKE_PROFIT": "일부 이익 실현", "STOP_LOSS": "손절 조건 확인", "EXIT": "보유 정리 검토"}
    if plan.get("entry_action") in entries:
        lines += [f"진입 판단: **{entries[plan['entry_action']]}** / 보유 위험 대응: **{risks.get(plan.get('risk_action'), '별도 확인')}**"]
    e = plan.get("economics")
    if e:
        lines += ["", "| 확인할 항목 | 계산 결과 |", "|---|---|",
                  f"| 계획 진입가 | {e['entry']:,.2f} {plan.get('currency', '')} |",
                  f"| 손절 기준가 | {e['stop']:,.2f} (진입가 대비 −{e['stop_distance_pct']:.2f}%) |",
                  f"| 첫 목표가 | {e['target']:,.2f} (진입가 대비 +{e['target_distance_pct']:.2f}%) |",
                  f"| 비용 반영 손익비 | {e['reward_risk_ratio']:.2f}배 — 잃을 금액 1에 대한 목표 이익 |",
                  f"| 1주당 계획 손실 | {e['risk_per_share']:,.2f} {plan.get('currency', '')} |"]
        if e["break_even_win_rate"] is not None:
            lines += [f"| 손익분기 승률 | {100 * e['break_even_win_rate']:.1f}% — 목표/손절로만 끝난다는 가정의 계산값이며 예측 확률이 아님 |"]
        else:
            lines += ["", "목표 이익보다 가정한 거래비용이 큽니다. 진입 계획을 재검토하세요."]
    else:
        lines += ["", "**가격 근거 확인 필요:** 진입가·손절가·목표가가 없거나 여러 계획이 섞여 있어 손익비를 계산하지 않았습니다. 숫자를 확인하기 전에는 투자 수량을 정하지 마세요."]
    lines += ["", f"- 비용 가정: 매수·매도 각각 {plan['cost_assumption_bps_per_side']:g}bp(1bp=0.01%). 실제 수수료·호가 차이·체결 오차로 바꿔야 하며 세금·환전 비용은 별도입니다.",
              "- 수량 계산: 사용 가능 현금, 종목 비중 한도, 허용 손실액÷1주당 계획 손실로 구한 수량 중 가장 작은 값으로 제한합니다. 기존 보유액도 비중 한도에 포함합니다.",
              "- 손절 가격은 손실 보장이 아닙니다. 급락·거래 정지 때는 더 불리한 가격에 팔릴 수 있습니다.",
              "- 같은 투자 기간의 분산 ETF·현금 보유와 비교하고, 실적 발표·공시 일정과 투자 근거가 깨지는 조건을 확인하세요."]
    lines += ["", "**자주 나오는 용어:** 지지선은 하락을 멈출 것으로 보는 가격대, 저항선은 상승이 막힐 것으로 보는 가격대입니다. 돌파는 그 가격대를 넘어서는 움직임이며 실패할 수 있습니다. VWAP은 거래량을 반영한 당일 평균 거래가격, 상대거래량은 평소 대비 거래량입니다. 무효화 조건은 매수 근거가 더 이상 성립하지 않는 상황을 뜻합니다."]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Calculate a whole-share plan in one currency; no order is submitted.")
    for name in ("capital", "cash", "entry", "stop"):
        parser.add_argument(f"--{name}", type=float, required=True)
    parser.add_argument("--risk-fraction", type=float, default=0.005)
    parser.add_argument("--max-position-fraction", type=float, default=0.10)
    parser.add_argument("--existing-position-value", type=float, default=0)
    parser.add_argument("--cost-bps", type=float, default=10)
    print(json.dumps(position_size(**vars(parser.parse_args())), ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
