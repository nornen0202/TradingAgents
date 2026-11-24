"""Private outbox events for verified normal KIS virtual-account execution."""
import hashlib
import math
from zoneinfo import ZoneInfo

from tradingagents.charting.bars import instant
from tradingagents.kis_strategy_contract import MODE, SCHEMA, ZONES
from .telegram import NotificationError


KIND = "kis_strategy"
_ALERTS = {
    "AMBIGUOUS_ORDER": "미확정 주문 응답",
    "ORDER_REPORT_UNVERIFIED": "주문 조회 결과 확인 필요",
    "STRATEGY_ACCOUNT_POSITION_UNVERIFIED": "전략 보유분과 계좌 보유분 대사 필요",
    "PREVIOUS_SESSION_ORDER_UNRESOLVED": "이전 거래일 주문 대사 필요",
    "RUNTIME_EVIDENCE_UNVERIFIED": "전략 실행 근거 확인 필요",
}


def enabled_at(state):
    from .local import read

    settings = read(state / "notifications" / "kis-strategy-enabled.json")
    if (isinstance(settings, dict) and settings.get("enabled") is True and settings.get("mode") == MODE
            and settings.get("real_orders_enabled") is False):
        return instant(settings.get("enabled_at"))
    return None


def queue_receipt(state, receipt):
    from .local import queue

    enabled = enabled_at(state)
    checked = instant(receipt.get("checked_at"))
    if (receipt.get("schema") != SCHEMA
            or receipt.get("mode") != MODE or receipt.get("enabled") is not True
            or receipt.get("real_orders_enabled") is not False or receipt.get("evidence_scope") is not None
            or enabled is None or checked is None or enabled > checked):
        return []

    keys = []
    for market, row in receipt["markets"].items():
        if market not in ZONES:
            continue
        base = {"kind": KIND, "market": market, "mode": MODE}
        for order in row.get("orders", []):
            progress = instant(order.get("fill_progress_available_at"))
            observed = instant(order.get("ingested_at"))
            quantity = order.get("filled_quantity")
            status = order.get("status")
            if (order.get("source") != "KIS_DEMO_BROKER_REPORT" or order.get("strategy_performance") is not True
                    or order.get("mode") != "demo" or type(quantity) is not int or quantity <= 0
                    or status not in {"PARTIAL", "FILLED", "CANCELLED"} or progress is None or observed is None
                    or not enabled <= progress <= observed <= checked or not isinstance(order.get("id"), str)):
                continue
            key = hashlib.sha256(f"{market}:{order['id']}:{quantity}:{status}".encode()).hexdigest()
            keys.append(queue(state, {**base, "event": "FILL", "state": status, "progress_key": key,
                                      "finished_at": progress.isoformat()}))

        day = checked.astimezone(ZoneInfo(ZONES[market])).replace(hour=0, minute=0, second=0, microsecond=0)
        for reason in sorted(set(row.get("blockers", ())) & _ALERTS.keys()):
            keys.append(queue(state, {**base, "event": "ISSUE", "reason": reason, "finished_at": day.isoformat()}))

        performance = row.get("evaluation") or {}
        available = instant(performance.get("settlement_available_at"))
        net = performance.get("realized_net_pnl")
        if (performance.get("cost_evidence_status") == "COMPLETE_REVIEWED_IMPORT"
                and performance.get("exact_fifo_available") is True and available is not None
                and enabled <= available <= checked and type(net) in {int, float} and math.isfinite(net)):
            keys.append(queue(state, {**base, "event": "REALIZED_PNL", "amount": net, "finished_at": available.isoformat()}))
    return keys


def compose(event):
    market, kind = event.get("market"), event.get("event")
    if event.get("mode") != MODE or market not in ZONES:
        raise NotificationError("Unknown virtual-account strategy event.")
    title = f"TradingAgents {market} KIS 정상 모의 전략"
    if kind == "FILL" and event.get("state") in {"PARTIAL", "FILLED", "CANCELLED"}:
        status = {"PARTIAL": "부분체결 확인", "FILLED": "전량체결 확인", "CANCELLED": "부분체결 후 잔량 취소 확인"}[event["state"]]
        detail = f"{status}\n상태 확인 {event['finished_at']}"
    elif kind == "ISSUE" and event.get("reason") in _ALERTS:
        detail = f"{_ALERTS[event['reason']]}\n거래일 {event['finished_at'][:10]}"
    elif kind == "REALIZED_PNL" and type(event.get("amount")) in {int, float} and math.isfinite(event["amount"]):
        currency = "KRW" if market == "KR" else "USD"
        detail = f"검토한 정산 근거의 누적 실현 순손익 {event['amount']:,.4f} {currency}"
    else:
        raise NotificationError("Virtual-account strategy notification could not be verified.")
    return f"{title}\n{detail}", [], {"conclusion": "strategy_event", "surfaces": [market.lower()]}
