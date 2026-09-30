"""Shared price condition semantics for evaluation and investor wording."""
from __future__ import annotations

from math import isfinite
import re
from typing import Any


_NON_PRICE_QUALIFIER = re.compile(
    r"저항.{0,40}(?:거부|밀리|밀림)|재차\s*밀(?:리|림)"
    r"|(?:보유\s*)?비중.{0,15}(?:높|초과|과도)"
    r"|\breject(?:ion|ed|s)\b|\bover(?:weight|concentrat\w*)\b"
    r"|(?:weight|position size|concentration).{0,30}(?:high|excess|above)"
    r"|(?:high|excessive).{0,20}(?:weight|position size|concentration)",
    re.IGNORECASE,
)


def risk_non_price_conditions(level: dict[str, Any]) -> tuple[str, ...]:
    """Preserve known rejection/concentration conditions requiring other evidence.

    This detects explicit qualifiers; it is not a general natural-language
    condition evaluator. A quote cannot prove either a resistance rejection or
    a portfolio concentration condition, even when confirmation is 'intraday'.
    """
    return tuple(dict.fromkeys(
        str(level[key]).strip() for key in ("source_text", "volume_rule")
        if level.get(key) and _NON_PRICE_QUALIFIER.search(str(level[key]))
    ))


def risk_direction(action: str, level: dict[str, Any]) -> str:
    action = str(action or "").upper()
    explicit = str(level.get("direction") or "").lower()
    if explicit in {"upside", "downside"}:
        return explicit
    if action == "TAKE_PROFIT":
        return "upside"
    if action in {"STOP_LOSS", "EXIT"}:
        return "downside"
    kind = str(level.get("level_type") or "").upper().replace(" ", "_")
    if kind in {"TAKE_PROFIT", "RESISTANCE"}:
        return "upside"
    if kind in {"SUPPORT", "INVALIDATION", "STOP_LOSS"}:
        return "downside"
    text = " ".join(str(level.get(key) or "") for key in ("label", "source_text", "reason_code")).lower()
    return "upside" if any(word in text for word in ("profit", "target", "resistance", "ceiling", "이익", "익절", "저항", "고점")) else "downside"


def risk_trigger(action: str, level: dict[str, Any]) -> dict[str, Any]:
    direction = risk_direction(action, level)
    price = None
    for key in ("price", "high", "low") if direction == "upside" else ("price", "low", "high"):
        try:
            candidate = float(level.get(key))
            if isfinite(candidate) and candidate > 0:
                price = candidate
                break
        except (TypeError, ValueError):
            continue
    return {"price": price, "direction": direction,
            "comparator": ">=" if direction == "upside" else "<=",
            "confirmation": str(level.get("confirmation") or "intraday").lower()}


def risk_condition_text(action: str, level: dict[str, Any], response: str) -> str | None:
    condition = risk_trigger(action, level)
    if condition["price"] is None:
        return None
    # HOLD describes the current position, not the response after a support
    # failure. Keep that present-tense decision out of conditional risk wording.
    if str(action or "").upper() in {"HOLD", "WATCH", "NONE", "NO_ACTION"}:
        response = "신규 진입 보류·보유 위험 대응 계획 재확인"
    side = "이상 도달" if condition["direction"] == "upside" else "이하 하락"
    confirmation = {"close": "종가 확인 후", "two_bar": "2개 봉 확인 후", "next_day": "다음 거래일 확인 후",
                    "volume_confirmed": "거래량 조건 확인 후"}.get(condition["confirmation"], "장중 확인 시")
    if condition["confirmation"] == "volume_confirmed" and level.get("volume_rule"):
        confirmation += f" ({level['volume_rule']})"
    text = f"{condition['price']:,.2f}".rstrip("0").rstrip(".") + f" {side}, {confirmation} {response}"
    qualifiers = risk_non_price_conditions(level)
    if qualifiers:
        text += " · 추가 조건 확인 필요: " + " / ".join(qualifiers)
    return text
