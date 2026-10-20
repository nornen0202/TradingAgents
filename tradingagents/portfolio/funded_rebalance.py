"""Costed sell-then-buy alternatives, never current buying power or orders."""

from __future__ import annotations

from datetime import datetime, timedelta
from itertools import combinations, product
from math import ceil, floor

from tradingagents.schemas.decision import explicit_price_range_conflicts
from tradingagents.scheduled.trade_plan import (
    _cost_profile,
    _mapping,
    _number,
    _pending_constraints,
    _positive,
    _timestamp,
)


# A small diversification sleeve, not a ranking inferred from historical returns.
BUY_UNIVERSE = {
    "KR": (("033780.KS", "KT&G"),),
    "US": (("PG", "Procter & Gamble"), ("ABBV", "AbbVie")),
}
PROTECTED = {"SGOV", "GLDM", "RSP"}


def _tick(price: float, market: str) -> float:
    if market == "US":
        return 0.01
    return next(
        tick
        for bound, tick in (
            (2000, 1),
            (5000, 5),
            (20000, 10),
            (50000, 50),
            (200000, 100),
            (500000, 500),
            (float("inf"), 1000),
        )
        if price < bound
    )


def _rounded(price: float, market: str, *, up: bool) -> float:
    tick = _tick(price, market)
    return round(
        (ceil if up else floor)(price / tick - (1e-10 if up else -1e-10)) * tick, 2
    )


def _valid_row(row: dict, now: datetime) -> bool:
    quote = _timestamp(row.get("market_data_asof"))
    thesis = _mapping(row.get("thesis"))
    decision = _timestamp(thesis.get("analysis_asof") or thesis.get("decision_asof"))
    # Stale evidence remains a dated scenario; missing/future evidence cannot size it.
    return bool(
        quote
        and now - timedelta(days=4) <= quote <= now
        and decision
        and now - timedelta(days=4) <= decision <= now
        and _positive(row.get("last_price"))
        and not explicit_price_range_conflicts(thesis)
        and "structured_price_range_conflict"
        not in _mapping(row.get("execution")).get("blockers", [])
    )


def build_funded_rebalance(
    payload: dict,
    snapshot: dict | None,
    trade_plan: dict,
    *,
    now: datetime,
    cost_config: dict | None = None,
) -> dict:
    """Enumerate a bounded whole-share rotation with conservative cash accounting.

    The planned sell limit is 0.5% below the observed quote, never a promised fill.
    No tax-loss credit or annual allowance funds a buy. US tax reserve treats all
    proceeds as taxable gains, an upper-bound funding scenario, not a tax estimate.
    """
    market = str(payload.get("market") or trade_plan.get("market") or "").upper()
    result = {
        "version": "funded-rebalance-v1",
        "market": market,
        "calculated_at": now.isoformat(),
        "account_asof": (snapshot or {}).get("as_of"),
        "order_ready": False,
        "status": "UNAVAILABLE",
        "sell_legs": [],
        "buy_legs": [],
        "cash_ledger": None,
        "excluded": [],
        "conditions": [
            "원래 종목별 손절 계획과 중복 집행하지 않는 별도의 포트폴리오 교체안입니다.",
            "매도 전 최신 잔고·시세·미체결·당일 기집행을 확인하고 매도 지정가 아래에서는 재계산합니다.",
            "원분석의 현재 매수 보류를 해제하는 주문 승인이 아닙니다. 매수 논지·손익비·업종 한도 재심사가 먼저입니다.",
            "실제 매도 체결·결제와 통화별 주문가능금액을 확인한 뒤 매수합니다. 휴일을 포함한 결제일을 확인합니다.",
            "매수는 표시한 지지 구간의 안정과 원래 투자 논지·손익비 재확인 후 검토합니다. 가격 접촉만으로 실행하지 않습니다.",
            "KR·US에 중복 표시된 원화 현금을 합산하지 않습니다. 두 시장 계획은 각각 검토하고 합산 집행 전 잔고를 재조회합니다.",
        ],
    }

    def unavailable(reason):
        result["reason"] = reason
        return result

    if now.tzinfo is None or market not in BUY_UNIVERSE or not snapshot:
        return unavailable("동일 실행의 계좌·시장·계산 시점을 확인할 수 없습니다.")
    asof = _timestamp(snapshot.get("as_of"))
    nav = _positive(snapshot.get("account_value_krw"))
    cash = _number(snapshot.get("available_cash_krw"))
    buffer = _positive(
        _mapping(trade_plan.get("capital_context")).get("min_cash_buffer_krw")
    )
    unknown, _, pending = _pending_constraints(snapshot)
    if (
        not asof
        or not now - timedelta(days=4) <= asof <= now
        or not nav
        or cash is None
        or cash < 0
        or buffer is None
    ):
        return unavailable("계좌 순자산·현금·기준 시각이 불명확합니다.")
    if unknown or pending:
        return unavailable("미체결 주문 확인·해소 후 교체안을 다시 계산합니다.")
    fx = 1.0 if market == "KR" else _positive(trade_plan.get("fx_krw_per_usd"))
    fx_time = _timestamp(trade_plan.get("fx_asof"))
    if not fx or (
        market == "US"
        and (not fx_time or not now - timedelta(days=4) <= fx_time <= now)
    ):
        return unavailable("검증된 동일 실행 환율이 없습니다.")
    costs = _cost_profile(cost_config, market)
    commission, levy = costs["commission_rate"], costs["sell_levy_rate"]
    if any(v is None or not 0 <= v < 1 for v in (commission, levy)):
        return unavailable("수수료·거래세를 확인할 수 없습니다.")
    positions = {p["canonical_ticker"]: p for p in snapshot.get("positions", [])}
    rows = {r["ticker"]: r for r in payload.get("rows", [])}
    constraints = snapshot.get("constraints") or {}
    order_cap = _number(constraints.get("max_order_count_per_day"))
    turnover_ratio = _number(constraints.get("max_daily_turnover_ratio"))
    name_cap = _number(constraints.get("max_single_name_weight"))
    min_trade = _number(constraints.get("min_trade_krw"))
    if any(v is None for v in (order_cap, turnover_ratio, name_cap, min_trade)):
        return unavailable("주문 건수·회전율·종목 비중 한도를 확인할 수 없습니다.")
    if order_cap < 2 or turnover_ratio <= 0 or name_cap <= 0:
        return unavailable("계좌 거래 한도에서 매도·매수 교체가 불가능합니다.")
    currency = "KRW" if market == "KR" else "USD"
    # Reserve 15bp of buy notional for adverse fills/fee rounding. Sell estimates
    # use the lower limit price, not an upper-bound stop-trigger receipt.
    buy_buffer = 0.0015
    buyer_budget = nav * 0.025
    buy_legs = []
    for ticker, name in BUY_UNIVERSE[market]:
        row = rows.get(ticker) or {}
        action = _mapping(row.get("portfolio_action"))
        if not _valid_row(row, now) or action.get("action_if_triggered") not in {
            "ADD_IF_TRIGGERED",
            "STARTER_IF_TRIGGERED",
            "BUY_IF_TRIGGERED",
        }:
            result["excluded"].append(
                {"ticker": ticker, "reason": "유효한 가격 근거·재배치 후보 조건 없음"}
            )
            continue
        levels = _mapping(_mapping(row.get("thesis")).get("execution_levels")).get(
            "levels", []
        )
        levels = [
            x
            for x in levels
            if x.get("level_type") == "PULLBACK"
            and (x.get("currency") or currency) == currency
        ]
        level = next(
            (
                x
                for x in levels
                if _positive(x.get("low"))
                and _positive(x.get("high"))
                and x["low"] <= x["high"]
            ),
            None,
        )
        if not level:
            result["excluded"].append(
                {"ticker": ticker, "reason": "명시된 눌림 매수 범위 없음"}
            )
            continue
        low, high = (
            _rounded(level["low"], market, up=True),
            _rounded(level["high"], market, up=False),
        )
        if low > high:
            continue
        required = high * fx * (1 + commission + buy_buffer)
        held = _number(positions.get(ticker, {}).get("quantity")) or 0
        if (
            high * fx < min_trade
            or required > buyer_budget
            or (held + 1) * high * fx > nav * name_cap
        ):
            result["excluded"].append(
                {"ticker": ticker, "reason": "1주가 신규 편입·종목 한도 초과"}
            )
            continue
        buyer_budget -= required
        buy_legs.append(
            {
                "ticker": ticker,
                "display_name": name,
                "side": "BUY",
                "quantity": 1,
                "price_low": low,
                "price_high": high,
                "currency": currency,
                "gross_krw": high * fx,
                "commission_krw": high * fx * commission,
                "execution_buffer_krw": high * fx * buy_buffer,
                "cash_required_krw": required,
                "conditions": list(
                    _mapping(row.get("thesis")).get("entry_conditions") or []
                ),
                "source_asof": row["market_data_asof"],
            }
        )
    if not buy_legs:
        return unavailable(
            "검증된 가격 범위와 2.5% 신규 편입 한도에 맞는 후보가 없습니다."
        )
    total_buy = sum(x["cash_required_krw"] for x in buy_legs)
    tax_rate = 0.22 if market == "US" else 0.0
    donors = []
    for ticker, position in positions.items():
        row = rows.get(ticker) or {}
        if (
            ticker in PROTECTED
            or ticker in {x["ticker"] for x in buy_legs}
            or not _valid_row(row, now)
        ):
            continue
        held, available = (
            _positive(position.get("quantity")),
            _number(position.get("available_qty")),
        )
        if not held or available is None or not 0 <= available <= held:
            continue
        action = _mapping(row.get("portfolio_action"))
        price = row["last_price"]
        weight = held * price * fx / nav
        if weight <= 0.20 and action.get("sell_intent") not in {
            "REDUCE_RISK",
            "STOP_LOSS",
            "EXIT",
            "TRIM_TO_FUND",
        }:
            continue
        cap = min(floor(available), 1 if held == 1 else floor(held / 2), 12)
        if cap < 1:
            continue
        low, high = (
            _rounded(price * 0.995, market, up=True),
            _rounded(price, market, up=False),
        )
        if low > high:
            continue
        per_unit = low * fx
        donors.append(
            {
                "ticker": ticker,
                "display_name": row.get("display_name") or ticker,
                "side": "SELL",
                "price_low": low,
                "price_high": high,
                "currency": currency,
                "source_asof": row["market_data_asof"],
                "holding_quantity": held,
                "cap": cap,
                "per_unit": per_unit,
                "weight": weight,
                "reason": "큰 보유 비중 분산"
                if weight > 0.20
                else "기존 위험 축소 검토 종목의 자금 재배치",
            }
        )
    donors.sort(key=lambda x: (-x["weight"], x["ticker"]))
    donors = donors[:8]
    best = None
    tested = 0
    max_sells = min(3, int(order_cap) - len(buy_legs))
    for n in range(1, max_sells + 1):
        for group in combinations(donors, n):
            for quantities in product(*(range(1, d["cap"] + 1) for d in group)):
                tested += 1
                if any(
                    d["per_unit"] * q < min_trade for d, q in zip(group, quantities)
                ):
                    continue
                gross = sum(d["per_unit"] * q for d, q in zip(group, quantities))
                sell_fees = gross * (commission + levy)
                tax = gross * tax_rate
                proceeds = gross - sell_fees - tax
                turnover = gross + sum(b["gross_krw"] for b in buy_legs)
                cash_after = cash + proceeds - total_buy
                # Buys use same-currency sale proceeds only; initial cash stays
                # protected. No assumed conversion of KRW cash to USD.
                if (
                    proceeds < total_buy
                    or cash_after < buffer + nav * 0.005
                    or turnover > nav * turnover_ratio
                ):
                    continue
                # Fewer dependent fills first, then minimum gross liquidation.
                score = (
                    n,
                    round(gross, 2),
                    sum(q >= d["holding_quantity"] for d, q in zip(group, quantities)),
                    sum(
                        (d["holding_quantity"] - q) ** 2 * d["per_unit"] ** 2
                        for d, q in zip(group, quantities)
                    ),
                )
                if best is None or score < best[0]:
                    best = (
                        score,
                        group,
                        quantities,
                        gross,
                        sell_fees,
                        tax,
                        proceeds,
                        cash_after,
                        turnover,
                    )
    result["combinations_tested"] = tested
    if best is None:
        result["unfunded_buy_candidates"] = buy_legs
        return unavailable(
            "현금·세금 충당·주문·회전율 한도를 모두 지키는 교체 조합이 없습니다. 강제 매수하지 않습니다."
        )
    _, group, quantities, gross, sell_fees, tax, proceeds, cash_after, turnover = best
    legs = []
    for donor, quantity in zip(group, quantities):
        leg = {k: v for k, v in donor.items() if k not in {"cap", "per_unit", "weight"}}
        leg.update(
            quantity=quantity,
            full_exit=quantity >= donor["holding_quantity"],
            gross_krw=donor["per_unit"] * quantity,
            commission_krw=donor["per_unit"] * quantity * commission,
            transaction_tax_krw=donor["per_unit"] * quantity * levy,
            capital_tax_reserve_krw=donor["per_unit"] * quantity * tax_rate,
            net_funding_krw=donor["per_unit"]
            * quantity
            * (1 - commission - levy - tax_rate),
        )
        legs.append(leg)
    result.update(
        status="CONDITIONAL_FUNDED",
        reason="매도 체결·결제와 매수 논지 재확인 후 실행을 검토하는 자금 연결안",
        sell_legs=legs,
        buy_legs=buy_legs,
        cash_ledger={
            "initial_cash_krw": cash,
            "nav_krw": nav,
            "reserve_krw": buffer,
            "sell_gross_krw": gross,
            "sell_fees_and_levy_krw": sell_fees,
            "capital_tax_reserve_krw": tax,
            "net_sale_funding_krw": proceeds,
            "after_sales_cash_krw": cash + proceeds,
            "buy_total_krw": total_buy,
            "after_buys_cash_krw": cash_after,
            "reserve_surplus_krw": cash_after - buffer,
            "turnover_ratio": turnover / nav,
            "extra_cash_margin_krw": nav * 0.005,
            "order_count": len(legs) + len(buy_legs),
            "fx_conversion_cost_krw": 0,
            "tax_basis": "US_GROSS_PROCEEDS_22PCT_UPPER_RESERVE"
            if market == "US"
            else "KR_LISTED_COMMON_STOCK_TRANSACTION_TAX",
        },
        assumptions=[
            "신규 편입은 순자산 2.5% 이내, 후보당 1주로 시작합니다. 통계적 최적 비중이라는 의미는 아닙니다.",
            "매도 하한은 입력 시세 대비 -0.5%를 호가 단위로 올린 지정가 검토값이며 체결을 보장하지 않습니다.",
            "기존 현금 20% 기준과 일일 주문·회전율 한도를 유지합니다. 당일 기집행은 실행 전 별도로 차감합니다.",
            "현금 기준 외 순자산 0.5% 여유를 확보하고 필요한 매도 종목 수, 매도 금액 순으로 줄입니다.",
            "매수 상단 금액에 수수료와 0.15% 체결 여유를 확보합니다. 실제 체결가가 상단을 넘으면 재계산합니다.",
            "미국 매도액 22%는 취득원가·공제 불명 상태의 보수적 세금 충당 상한이며 실제 양도세 추정액이 아닙니다.",
            "동일 통화 매도 대금을 재사용해 예상 환전 비용은 0입니다. 원화 인출·다른 통화 사용 시 60% 우대 환전 비용을 별도 재계산합니다.",
            "현재 주문 수량·매수 가능금액을 변경하지 않습니다. 기존 위험 대응 계획과 이 교체안을 더해서 실행하지 않습니다.",
        ],
    )
    return result
