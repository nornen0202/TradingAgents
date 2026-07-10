from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tradingagents.schemas import StructuredDecision, parse_structured_decision


@dataclass(frozen=True)
class DecisionPresentation:
    investment_view: str
    market_view: str
    action_summary: str
    setup_summary: str
    conviction_label: str
    horizon_label: str
    data_status: str
    primary_condition: str


def is_korean(language: str | None) -> bool:
    return str(language or "").strip().lower() == "korean"


def present_decision(decision: StructuredDecision, *, language: str = "English") -> DecisionPresentation:
    korean = is_korean(language)
    primary_condition = _primary_condition(decision, korean)
    return DecisionPresentation(
        investment_view=_rating_label(decision.rating.value, korean),
        market_view=_stance_label(decision.portfolio_stance.value, korean),
        action_summary=_action_label(decision.entry_action.value, korean, condition=primary_condition),
        setup_summary=_setup_label(decision.setup_quality.value, korean),
        conviction_label=_conviction_label(decision.confidence, korean),
        horizon_label=_horizon_label(decision.time_horizon.value, korean),
        data_status=_data_status(decision, korean),
        primary_condition=primary_condition,
    )


def present_decision_payload(raw_decision: Any, *, language: str = "English") -> DecisionPresentation | None:
    if not isinstance(raw_decision, str) or not raw_decision.strip().startswith("{"):
        return None
    try:
        return present_decision(parse_structured_decision(raw_decision), language=language)
    except Exception:
        return None


def present_investment_view(raw_decision: Any, *, language: str = "English") -> str:
    presentation = present_decision_payload(raw_decision, language=language)
    if presentation is not None:
        return presentation.investment_view
    value = str(raw_decision or "-").strip()
    if not value or value == "-":
        return "-"
    return _rating_label(value.upper(), is_korean(language))


def present_action_summary(raw_decision: Any, *, language: str = "English") -> str:
    presentation = present_decision_payload(raw_decision, language=language)
    if presentation is not None:
        return presentation.action_summary
    value = str(raw_decision or "").strip().upper()
    if not value:
        return "-"
    korean = is_korean(language)
    if korean:
        mapping = {
            "BUY": "매수 검토",
            "OVERWEIGHT": "분할 증액 검토",
            "HOLD": "보유 유지",
            "UNDERWEIGHT": "일부 축소 검토",
            "SELL": "청산 검토",
            "NO_TRADE": "관망",
        }
        return mapping.get(value, _humanize_code(value, korean=True))
    mapping = {
        "BUY": "Consider buying",
        "OVERWEIGHT": "Consider gradual add",
        "HOLD": "Hold",
        "UNDERWEIGHT": "Consider trimming",
        "SELL": "Consider exit",
        "NO_TRADE": "Wait",
    }
    return mapping.get(value, _humanize_code(value, korean=False))


def present_primary_condition(raw_decision: Any, *, language: str = "English") -> str:
    presentation = present_decision_payload(raw_decision, language=language)
    if presentation is not None:
        return presentation.primary_condition
    return "-"


def present_data_status(
    raw_decision: Any,
    *,
    quality_flags: list[str] | tuple[str, ...] | None = None,
    language: str = "English",
) -> str:
    korean = is_korean(language)
    if quality_flags:
        return "일부 자료 확인 필요" if korean else "Some source checks needed"
    presentation = present_decision_payload(raw_decision, language=language)
    if presentation is not None:
        return presentation.data_status
    return "정상" if korean else "Available"


def present_account_action(action: str, *, conditional: bool = False, language: str = "Korean") -> str:
    korean = is_korean(language)
    normalized = str(action or "").strip().upper()
    if korean:
        mapping = {
            "ADD_NOW": "지금 추가 매수",
            "STARTER_NOW": "소액 신규 진입",
            "ADD": "조건부 소액 진입",
            "WATCH_TRIGGER": "조건부 관찰",
            "REDUCE_NOW": "일부 축소",
            "TAKE_PROFIT_NOW": "이익실현성 일부 축소",
            "STOP_LOSS_NOW": "손절 조건 충족",
            "TRIM_NOW": "일부 이익 실현",
            "EXIT_NOW": "청산 검토",
            "TRIM_TO_FUND": "강한 후보 매수를 위한 일부 축소 (줄여서 강한 후보로 자금 이동)",
            "REDUCE_RISK": "리스크 축소",
            "TAKE_PROFIT": "이익실현성 축소",
            "STOP_LOSS": "손절 조건",
            "EXIT": "청산 후보",
            "HOLD": "보유 유지",
            "WATCH": "관찰 유지",
            "WATCH_RISK": "위험 조건 관찰",
            "AVOID": "신규 매수 회피",
            "NONE": "추가 행동 없음",
            "ADD_IF_TRIGGERED": "조건 충족 시 추가 매수",
            "STARTER_IF_TRIGGERED": "조건 충족 시 소액 진입",
            "REDUCE_IF_TRIGGERED": "조건 이탈 시 축소",
            "TAKE_PROFIT_IF_TRIGGERED": "조건 충족 시 이익실현",
            "STOP_LOSS_IF_TRIGGERED": "조건 충족 시 손절",
            "EXIT_IF_TRIGGERED": "조건 이탈 시 청산 검토",
        }
        return mapping.get(normalized, _humanize_code(normalized, korean=True))

    mapping = {
        "ADD_NOW": "Add now",
        "STARTER_NOW": "Open starter position",
        "ADD": "Conditional starter add",
        "WATCH_TRIGGER": "Conditional watch",
        "REDUCE_NOW": "Reduce now",
        "TAKE_PROFIT_NOW": "Take profit now",
        "STOP_LOSS_NOW": "Stop-loss now",
        "TRIM_NOW": "Trim now",
        "EXIT_NOW": "Consider exit",
        "TRIM_TO_FUND": "Trim to fund stronger candidates",
        "REDUCE_RISK": "Reduce risk",
        "TAKE_PROFIT": "Take profit",
        "STOP_LOSS": "Stop-loss condition",
        "EXIT": "Exit candidate",
        "HOLD": "Hold",
        "WATCH": "Watch",
        "WATCH_RISK": "Watch risk",
        "AVOID": "Avoid",
        "NONE": "No further action",
        "ADD_IF_TRIGGERED": "Add if triggered",
        "STARTER_IF_TRIGGERED": "Start if triggered",
        "REDUCE_IF_TRIGGERED": "Reduce if triggered",
        "TAKE_PROFIT_IF_TRIGGERED": "Take profit if triggered",
        "STOP_LOSS_IF_TRIGGERED": "Stop-loss if triggered",
        "EXIT_IF_TRIGGERED": "Exit if triggered",
    }
    return mapping.get(normalized, _humanize_code(normalized, korean=False))


def present_execution_state(value: str, *, language: str = "Korean") -> str:
    normalized = str(value or "").strip().upper()
    if is_korean(language):
        return {
            "WAIT": "조건 충족 전 대기",
            "ARMED": "실행 조건 감시 중",
            "TRIGGERED_PENDING_CLOSE": "조건 충족, 종가 확인 대기",
            "ACTIONABLE_NOW": "지금 실행 검토 가능",
            "INVALIDATED": "투자 근거 무효화",
            "DEGRADED": "데이터 확인 전 대기",
        }.get(normalized, _humanize_code(normalized, korean=True))
    return _humanize_code(normalized, korean=False)


def present_execution_timing(value: str, *, language: str = "Korean") -> str:
    normalized = str(value or "").strip().upper()
    if is_korean(language):
        return {
            "WAITING": "대기",
            "NO_LIVE_DATA": "실시간 데이터 없음",
            "PRE_OPEN_THESIS_ONLY": "장 시작 전 연구만 유효",
            "PILOT_READY": "소액 시험 진입 검토 가능",
            "PILOT_BLOCKED_VOLUME": "거래량 부족으로 진입 보류",
            "PILOT_BLOCKED_FAILED_BREAKOUT": "돌파 실패로 진입 보류",
            "CLOSE_CONFIRM_PENDING": "종가 확인 대기",
            "CLOSE_CONFIRMED": "종가 조건 확인 완료",
            "NEXT_DAY_FOLLOWTHROUGH_PENDING": "다음 거래일 추세 확인 대기",
            "FAILED_BREAKOUT": "돌파 실패",
            "SUPPORT_HOLD": "지지선 유지",
            "SUPPORT_FAIL": "지지선 이탈",
            "STALE_TRIGGERABLE": "과거 조건, 최신 데이터 재확인 필요",
            "INVALIDATED": "투자 근거 무효화",
            "DEGRADED": "데이터 품질 저하",
            "LIVE_BREAKOUT": "장중 돌파 확인",
            "LATE_SESSION_CONFIRM": "장 후반 확인",
            "CLOSE_CONFIRM": "종가 확인",
            "ACTIONABLE_LIVE": "장중 실행 검토 가능",
        }.get(normalized, _humanize_code(normalized, korean=True))
    return _humanize_code(normalized, korean=False)


def present_strategy_category(value: str, *, language: str = "Korean") -> str:
    normalized = str(value or "").strip().upper()
    if is_korean(language):
        return {
            "BUY_NOW": "지금 분할매수 검토",
            "BUY_ON_CONFIRMATION": "조건 확인 후 분할매수 검토",
            "HOLD": "보유 유지",
            "REDUCE": "비중 축소 검토",
            "SELL": "매도·청산 검토",
            "WAIT": "조건 충족 전 대기",
            "AVOID": "신규 매수 회피",
            "DATA_CHECK": "데이터 확인 전 대기",
            "WAIT_CLOSE": "종가 확인 후 판단",
            "WAIT_NEXT_SESSION": "다음 거래일 확인 후 판단",
            "WATCH_ONLY": "관심종목으로 관찰",
            "INSUFFICIENT_DATA": "판단 자료 부족",
            "AVOID_OR_EXCLUDE": "신규 매수 회피·후보 제외",
            "TRIM_OR_RISK_REDUCE_REVIEW": "비중 축소·위험 완화 검토",
            "HOLD_MAINTAIN": "보유 유지",
            "ORDER_REVIEW_NOW": "지금 주문 조건 검토",
            "PILOT_REVIEW_ONLY": "소액 시험 진입만 검토",
            "WAIT_INTRADAY": "장중 조건 확인 대기",
            "WAIT_CLOSE_CONFIRMATION": "종가 확인 대기",
        }.get(normalized, _humanize_code(normalized, korean=True))
    return _humanize_code(normalized, korean=False)


def present_reason_code(value: str, *, language: str = "Korean") -> str:
    normalized = str(value or "").strip().upper()
    if not is_korean(language):
        return _humanize_code(normalized, korean=False)
    direct = {
        "PRICE_ABOVE_TRIGGER": "매수 기준가 상회",
        "PRICE_BELOW_TRIGGER": "매수 기준가 미충족",
        "VWAP_OK": "VWAP 위에서 거래",
        "VWAP_NOT_OK": "VWAP 조건 미충족",
        "VOLUME_OK": "거래량 조건 충족",
        "VOLUME_NOT_OK": "거래량 조건 미충족",
        "SUPPORT_HOLD": "지지선 유지",
        "SUPPORT_FAIL": "지지선 이탈",
        "FAILED_BREAKOUT": "돌파 후 안착 실패",
        "NO_LIVE_DATA": "실시간 데이터 없음",
        "STALE_DATA": "데이터 기준시각 경과",
        "DELAYED_DATA": "지연 데이터",
        "CASH_BUFFER_BLOCK": "최소 현금 여유 부족",
        "HALT_STATUS_RECHECK_REQUIRED": "거래정지 여부 재확인 필요",
    }
    if normalized in direct:
        return direct[normalized]
    if normalized.startswith("MISSING_"):
        return f"{_humanize_code(normalized.removeprefix('MISSING_'), korean=True)} 누락"
    if normalized.startswith("LIMITED_"):
        return f"{_humanize_code(normalized.removeprefix('LIMITED_'), korean=True)} 제한"
    return _humanize_code(normalized, korean=True)


def present_market_regime(value: str, *, language: str = "Korean") -> str:
    korean = is_korean(language)
    normalized = str(value or "").strip().lower()
    if korean:
        mapping = {
            "constructive_but_selective": "우호적이지만 선별 필요",
            "constructive": "우호적",
            "defensive": "방어적",
            "mixed": "혼조",
        }
        return mapping.get(normalized, _humanize_code(normalized, korean=True))

    mapping = {
        "constructive_but_selective": "Constructive but selective",
        "constructive": "Constructive",
        "defensive": "Defensive",
        "mixed": "Mixed",
    }
    return mapping.get(normalized, _humanize_code(normalized, korean=False))


def present_snapshot_mode(value: str, *, language: str = "Korean") -> str:
    korean = is_korean(language)
    normalized = str(value or "").strip().upper()
    if korean:
        mapping = {
            "VALID": "계좌 기준",
            "WATCHLIST_ONLY": "관심종목 전용",
            "CAPITAL_CONSTRAINED": "현금 제약",
            "INVALID_SNAPSHOT": "확인 필요",
        }
        return mapping.get(normalized, "확인 필요")

    mapping = {
        "VALID": "Account-aware",
        "WATCHLIST_ONLY": "Watchlist only",
        "CAPITAL_CONSTRAINED": "Capital constrained",
        "INVALID_SNAPSHOT": "Needs review",
    }
    return mapping.get(normalized, "Needs review")


def present_review_required(value: bool, *, language: str = "Korean") -> str:
    if is_korean(language):
        return "예" if value else "아니오"
    return "Yes" if value else "No"


def sanitize_investor_text(value: Any, *, language: str = "Korean") -> str:
    text = str(value or "").strip()
    if not text:
        return "없음" if is_korean(language) else "None"

    lower = text.lower()
    if "run_time_budget_exhausted" in lower or (
        "remaining_seconds" in lower and "min_required_seconds" in lower
    ):
        return (
            "일부 종목은 분석 시간이 부족해 재분석 전까지 투자 후보에서 제외합니다."
            if is_korean(language)
            else "Some tickers need reanalysis before they should be treated as investable candidates."
        )
    if "wait-heavy constructive" in lower or "bullish_wait_concentration" in lower:
        return (
            "우호적 관점은 많지만 즉시 실행 조건을 통과한 종목은 적어 조건 확인이 우선입니다."
            if is_korean(language)
            else "Constructive views are broad, but few names meet immediate execution conditions."
        )
    if "delayed_or_invalid_market_data" in lower or "stale/degraded" in lower:
        return (
            "장중 데이터가 지연되거나 불완전해 종가와 거래량 확인을 우선합니다."
            if is_korean(language)
            else "Intraday data is delayed or incomplete, so close and volume confirmation come first."
        )
    if any(token in lower for token in ("semantic_judge", "rule_only", "fallback", "vendor", "tool", "token")):
        return "일부 분석 자료 또는 자동 판단 결과는 확인이 필요합니다." if is_korean(language) else "Some source or automation checks need review."
    if "no broker account snapshot" in lower or "watchlist-only" in lower:
        return "실계좌 스냅샷 없이 관심종목 기준으로 작성했습니다." if is_korean(language) else "Prepared from a watchlist without a live account snapshot."
    if "no_trade" in lower:
        return "즉시 실행보다 관찰 신호가 많은 장입니다." if is_korean(language) else "Signals favor patience over immediate action."
    if "decision payload" in lower and "missing required fields" in lower:
        return "decision payload missing required fields"
    if is_korean(language):
        localized = _localized_english_investor_text(text)
        if localized is not None:
            return localized
    return text.replace("_", " ")


def _localized_english_investor_text(text: str) -> str | None:
    compact = " ".join(str(text or "").split())
    if not compact:
        return "없음"
    lower = compact.lower()
    if "close above" in lower:
        level = compact.split("above", 1)[1].strip()
        return f"종가 {level} 이상 확인 시 검토"
    if "close below" in lower:
        level = compact.split("below", 1)[1].strip()
        return f"종가 {level} 이탈 시 축소 검토"
    if "volume" in lower and any(token in lower for token in ("above", "surge", "breakout")):
        return "거래량 확인을 동반한 조건 충족 시 검토"
    if len(compact.split()) <= 4:
        return None
    ascii_letters = sum(1 for char in compact if "a" <= char.lower() <= "z")
    non_space = sum(1 for char in compact if not char.isspace())
    if ascii_letters >= 12 and any(
        token in lower
        for token in (
            "current setup",
            "existing-position",
            "dominant near-term",
            "support",
            "breakout",
            "follow-through",
            "wait",
            "confirm",
            "requires",
        )
    ):
        if any(token in lower for token in ("risk", "invalid", "below", "reduce", "trim", "exit")):
            return "리스크 조건 이탈 시 축소를 검토합니다."
        return "조건 충족 전까지 대기합니다."
    if non_space and ascii_letters / non_space >= 0.45:
        if any(token in lower for token in ("trigger", "condition", "confirm", "wait", "pending", "breakout")):
            return "조건 충족 전까지 대기합니다."
        if any(token in lower for token in ("risk", "invalid", "below", "reduce", "trim", "exit")):
            return "리스크 조건 이탈 시 축소를 검토합니다."
        return "근거 요약 생성 실패: 원문은 투자자 화면에서 숨깁니다."
    return None


def _rating_label(value: str, korean: bool) -> str:
    normalized = str(value or "").strip().upper()
    if korean:
        mapping = {
            "BUY": "매수",
            "OVERWEIGHT": "비중 확대",
            "HOLD": "보유",
            "UNDERWEIGHT": "비중 축소",
            "SELL": "매도",
            "NO_TRADE": "관망",
        }
        return mapping.get(normalized, _humanize_code(normalized, korean=True))

    mapping = {
        "BUY": "Buy",
        "OVERWEIGHT": "Overweight",
        "HOLD": "Hold",
        "UNDERWEIGHT": "Underweight",
        "SELL": "Sell",
        "NO_TRADE": "No immediate trade",
    }
    return mapping.get(normalized, _humanize_code(normalized, korean=False))


def _stance_label(value: str, korean: bool) -> str:
    normalized = str(value or "").strip().upper()
    if korean:
        return {
            "BULLISH": "상승 우위",
            "NEUTRAL": "중립",
            "BEARISH": "하방 리스크 우위",
        }.get(normalized, _humanize_code(normalized, korean=True))
    return {
        "BULLISH": "Constructive",
        "NEUTRAL": "Balanced",
        "BEARISH": "Defensive",
    }.get(normalized, _humanize_code(normalized, korean=False))


def _action_label(value: str, korean: bool, *, condition: str | None = None) -> str:
    normalized = str(value or "").strip().upper()
    if korean:
        label = {
            "NONE": "추가 행동 없음",
            "WAIT": "조건 확인 후 검토",
            "STARTER": "소액/분할 진입 후보",
            "ADD": "추가 매수 후보",
            "EXIT": "비중 축소 또는 청산 검토",
        }.get(normalized, _humanize_code(normalized, korean=True))
    else:
        label = {
            "NONE": "No further action",
            "WAIT": "Wait for confirmation",
            "STARTER": "Starter position candidate",
            "ADD": "Add candidate",
            "EXIT": "Reduce or exit",
        }.get(normalized, _humanize_code(normalized, korean=False))
    if normalized == "WAIT" and _has_condition_text(condition):
        return f"{label}: {_shorten_condition(str(condition))}"
    return label


def _primary_condition(decision: StructuredDecision, korean: bool) -> str:
    language = "Korean" if korean else "English"
    for values in (decision.watchlist_triggers, decision.catalysts, decision.invalidators):
        for value in values:
            text = sanitize_investor_text(value, language=language)
            if _has_condition_text(text):
                return _shorten_condition(text)
    return "-"


def _has_condition_text(value: str | None) -> bool:
    text = str(value or "").strip()
    return bool(text) and text not in {"-", "None", "없음"}


def _shorten_condition(value: str, *, max_chars: int = 140) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def _setup_label(value: str, korean: bool) -> str:
    normalized = str(value or "").strip().upper()
    if korean:
        return {
            "WEAK": "근거 약함",
            "DEVELOPING": "조건 확인 필요",
            "COMPELLING": "실행 근거 양호",
        }.get(normalized, _humanize_code(normalized, korean=True))
    return {
        "WEAK": "Weak evidence",
        "DEVELOPING": "Needs confirmation",
        "COMPELLING": "Actionable evidence",
    }.get(normalized, _humanize_code(normalized, korean=False))


def _conviction_label(confidence: float, korean: bool) -> str:
    if confidence >= 0.75:
        return "높음" if korean else "High"
    if confidence >= 0.55:
        return "보통" if korean else "Moderate"
    return "낮음" if korean else "Low"


def _horizon_label(value: str, korean: bool) -> str:
    normalized = str(value or "").strip().lower()
    if korean:
        return {
            "short": "단기",
            "medium": "중기",
            "long": "장기",
        }.get(normalized, _humanize_code(normalized, korean=True))
    return {
        "short": "Short term",
        "medium": "Medium term",
        "long": "Long term",
    }.get(normalized, _humanize_code(normalized, korean=False))


def _data_status(decision: StructuredDecision, korean: bool) -> str:
    coverage = decision.data_coverage
    limited = (
        coverage.company_news_count <= 0
        or coverage.social_source.value == "unavailable"
        or coverage.macro_items_count <= 0
    )
    if korean:
        label = "일부 제한 있음" if limited else "정상"
        return f"{label} (기업 뉴스 {coverage.company_news_count}건, 공시 {coverage.disclosures_count}건)"
    label = "Some limits" if limited else "Available"
    return f"{label} (company news {coverage.company_news_count}, filings {coverage.disclosures_count})"


def _humanize_code(value: str, *, korean: bool) -> str:
    text = str(value or "").strip()
    if not text:
        return "-"
    humanized = text.replace("_", " ").strip().lower()
    if korean:
        return humanized
    return humanized.capitalize()
