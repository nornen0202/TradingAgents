from __future__ import annotations

import json
import re
from json import JSONDecodeError
from typing import Any, Mapping

from tradingagents.llm_clients import create_llm_client
from tradingagents.presentation import (
    is_korean,
    present_account_action,
    present_decision,
    present_market_regime,
    present_snapshot_mode,
    sanitize_investor_text,
)
from tradingagents.schemas import StructuredDecision, parse_structured_decision


def polish_ticker_report(
    final_state: Mapping[str, Any],
    *,
    ticker: str,
    language: str,
    llm_settings: Any | None,
    enabled: bool = True,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Attach an investor-facing writer summary without changing the decision payload."""

    state = dict(final_state)
    metadata = _base_metadata(llm_settings, scope="ticker")
    if not enabled:
        metadata["status"] = "disabled"
        return state, metadata

    raw_decision = _select_decision_payload(state)
    parsed_decision = _parse_optional_decision(raw_decision)
    fallback_payload = _fallback_ticker_payload(
        ticker=ticker,
        raw_decision=raw_decision,
        decision=parsed_decision,
        language=language,
    )

    writer_payload = fallback_payload
    try:
        llm = _create_writer_llm(llm_settings)
        if llm is None:
            metadata["status"] = "fallback"
            metadata["reason"] = "writer_llm_unavailable"
        else:
            result = _invoke_writer_llm(
                llm,
                _build_ticker_prompt(
                    ticker=ticker,
                    state=state,
                    raw_decision=raw_decision,
                    decision=parsed_decision,
                    fallback_payload=fallback_payload,
                    language=language,
                ),
            )
            writer_payload = _normalize_writer_payload(result, fallback_payload, language=language)
            metadata["status"] = "success"
    except Exception as exc:
        metadata["status"] = "fallback"
        metadata["reason"] = "writer_failed"
        metadata["error"] = str(exc)

    state["investor_summary_report"] = _format_writer_summary(
        writer_payload,
        language=language,
        scope="ticker",
    )
    state["investor_writer_status"] = metadata
    return state, metadata


def polish_portfolio_report_markdown(
    markdown: str,
    *,
    snapshot: Any,
    recommendation: Any,
    language: str,
    llm_settings: Any | None,
    enabled: bool = True,
) -> tuple[str, dict[str, Any]]:
    """Prepend an investor-facing account summary without changing actions."""

    metadata = _base_metadata(llm_settings, scope="portfolio")
    if not enabled:
        metadata["status"] = "disabled"
        return markdown, metadata

    fallback_payload = _fallback_portfolio_payload(
        snapshot=snapshot,
        recommendation=recommendation,
        language=language,
    )
    writer_payload = fallback_payload

    try:
        llm = _create_writer_llm(llm_settings)
        if llm is None:
            metadata["status"] = "fallback"
            metadata["reason"] = "writer_llm_unavailable"
        else:
            result = _invoke_writer_llm(
                llm,
                _build_portfolio_prompt(
                    snapshot=snapshot,
                    recommendation=recommendation,
                    fallback_payload=fallback_payload,
                    language=language,
                ),
            )
            writer_payload = _normalize_writer_payload(result, fallback_payload, language=language)
            metadata["status"] = "success"
    except Exception as exc:
        metadata["status"] = "fallback"
        metadata["reason"] = "writer_failed"
        metadata["error"] = str(exc)

    summary = _format_writer_summary(writer_payload, language=language, scope="portfolio")
    return _insert_summary_after_title(markdown, summary), metadata


def _select_decision_payload(state: Mapping[str, Any]) -> Any:
    risk = state.get("risk_debate_state") or {}
    investment = state.get("investment_debate_state") or {}
    for candidate in (
        state.get("final_trade_decision"),
        risk.get("judge_decision"),
        investment.get("judge_decision"),
        state.get("trader_investment_plan"),
    ):
        if isinstance(candidate, str) and candidate.strip():
            return candidate
    return ""


def _parse_optional_decision(raw_decision: Any) -> StructuredDecision | None:
    if not isinstance(raw_decision, str) or not raw_decision.strip().startswith("{"):
        return None
    try:
        return parse_structured_decision(raw_decision)
    except Exception:
        return None


def _fallback_ticker_payload(
    *,
    ticker: str,
    raw_decision: Any,
    decision: StructuredDecision | None,
    language: str,
) -> dict[str, Any]:
    korean = is_korean(language)
    if decision is None:
        summary = sanitize_investor_text(raw_decision, language=language)
        return {
            "headline_action": "관찰 유지" if korean else "Keep watching",
            "one_sentence_summary": _shorten(summary, 220),
            "why_now": [_shorten(summary, 180)] if summary else [],
            "how_to_execute": "즉시 주문보다 다음 확인 조건을 먼저 점검합니다." if korean else "Check the next confirmation before placing an order.",
            "add_if": "분석 리포트의 조건이 충족될 때만 실행합니다." if korean else "Act only when the report conditions are met.",
            "cut_if": "핵심 논리가 훼손되면 보수적으로 축소합니다." if korean else "Reduce exposure if the thesis breaks.",
            "key_risks": [],
            "watch_next": [ticker],
            "confidence_text": "보통" if korean else "Moderate",
            "data_caveat_text": "자료 상태는 본문을 함께 확인하세요." if korean else "Review the source notes in the body.",
        }

    presentation = present_decision(decision, language=language)
    catalysts = [sanitize_investor_text(item, language=language) for item in decision.catalysts]
    invalidators = [sanitize_investor_text(item, language=language) for item in decision.invalidators]
    watch_next = [
        sanitize_investor_text(item, language=language)
        for item in (decision.watchlist_triggers or decision.catalysts or decision.invalidators)
    ]
    return {
        "headline_action": presentation.action_summary,
        "one_sentence_summary": f"{presentation.market_view}: {sanitize_investor_text(decision.entry_logic, language=language)}",
        "why_now": catalysts[:3],
        "how_to_execute": sanitize_investor_text(decision.position_sizing, language=language),
        "add_if": sanitize_investor_text(decision.entry_logic, language=language),
        "cut_if": sanitize_investor_text(decision.exit_logic, language=language),
        "key_risks": invalidators[:2],
        "watch_next": watch_next[:3],
        "confidence_text": presentation.conviction_label,
        "data_caveat_text": presentation.data_status,
    }


def _fallback_portfolio_payload(
    *,
    snapshot: Any,
    recommendation: Any,
    language: str,
) -> dict[str, Any]:
    korean = is_korean(language)
    immediate_actions = [action for action in recommendation.actions if action.delta_krw_now != 0]
    conditional_actions = [action for action in recommendation.actions if action.delta_krw_if_triggered != 0]
    top_actions = list(recommendation.actions[:3])
    mode = present_snapshot_mode(snapshot.snapshot_health, language=language)
    market = present_market_regime(recommendation.market_regime, language=language)

    if immediate_actions:
        headline = "즉시 실행 후보 있음" if korean else "Immediate actions available"
    elif snapshot.snapshot_health == "WATCHLIST_ONLY":
        headline = "워치리스트 모드" if korean else "Watchlist mode"
    else:
        headline = "조건 확인 후 실행" if korean else "Wait for confirmation"

    why_now = [
        f"{action.display_name}: {sanitize_investor_text(action.rationale, language=language)}"
        for action in top_actions
    ]
    watch_next = []
    for action in top_actions:
        label = present_account_action(action.action_if_triggered, conditional=True, language=language)
        condition = "; ".join(sanitize_investor_text(item, language=language) for item in action.trigger_conditions[:2])
        watch_next.append(f"{action.display_name}: {label}" + (f" ({condition})" if condition else ""))

    return {
        "headline_action": headline,
        "one_sentence_summary": (
            f"{mode} / {market}. "
            + (
                f"지금 실행 후보 {len(immediate_actions)}개, 조건부 후보 {len(conditional_actions)}개입니다."
                if korean
                else f"{len(immediate_actions)} immediate candidate(s), {len(conditional_actions)} conditional candidate(s)."
            )
        ),
        "why_now": why_now[:3],
        "how_to_execute": (
            "실계좌 스냅샷 연결 전에는 주문 없이 관찰 우선순위만 확인합니다."
            if korean and snapshot.snapshot_health == "WATCHLIST_ONLY"
            else "현금, 기존 비중, 우선순위를 확인한 뒤 표의 지금 할 일만 실행합니다."
            if korean
            else "Execute only the table's current actions after checking cash, existing weights, and priority."
        ),
        "add_if": (
            "조건부 후보는 표의 트리거가 충족될 때만 검토합니다."
            if korean
            else "Review conditional candidates only when their table triggers are met."
        ),
        "cut_if": (
            "리스크 조건이 깨지거나 계좌 현금이 부족하면 보수적으로 축소합니다."
            if korean
            else "Reduce risk if invalidation conditions appear or cash is constrained."
        ),
        "key_risks": [sanitize_investor_text(item, language=language) for item in recommendation.portfolio_risks[:2]],
        "watch_next": watch_next[:3],
        "confidence_text": "보통" if korean else "Moderate",
        "data_caveat_text": (
            "실계좌 스냅샷 없이 관심종목 기준으로 작성했습니다."
            if snapshot.snapshot_health == "WATCHLIST_ONLY"
            else ("계좌 데이터 기준으로 작성했습니다." if korean else "Prepared from account data.")
        ),
    }


def _build_ticker_prompt(
    *,
    ticker: str,
    state: Mapping[str, Any],
    raw_decision: Any,
    decision: StructuredDecision | None,
    fallback_payload: dict[str, Any],
    language: str,
) -> str:
    compact_payload = {
        "ticker": ticker,
        "language": language,
        "decision": decision.to_dict() if decision else str(raw_decision)[:2000],
        "required_meaning": fallback_payload,
        "evidence_excerpt": {
            "market": _shorten(state.get("market_report"), 1200),
            "sentiment": _shorten(state.get("sentiment_report"), 900),
            "news": _shorten(state.get("news_report"), 900),
            "fundamentals": _shorten(state.get("fundamentals_report"), 900),
            "trader_plan": _shorten(state.get("trader_investment_plan") or state.get("investment_plan"), 1000),
        },
    }
    return _writer_prompt_header(language) + (
        "\nContext JSON:\n"
        f"{json.dumps(compact_payload, ensure_ascii=False)}"
    )


def _build_portfolio_prompt(
    *,
    snapshot: Any,
    recommendation: Any,
    fallback_payload: dict[str, Any],
    language: str,
) -> str:
    compact_payload = {
        "language": language,
        "snapshot": {
            "snapshot_health": snapshot.snapshot_health,
            "account_value_krw": snapshot.account_value_krw,
            "available_cash_krw": snapshot.available_cash_krw,
            "position_count": len(snapshot.positions),
            "warnings": list(snapshot.warnings),
        },
        "recommendation": {
            "market_regime": recommendation.market_regime,
            "recommended_cash_after_now_krw": recommendation.recommended_cash_after_now_krw,
            "recommended_cash_after_triggered_krw": recommendation.recommended_cash_after_triggered_krw,
            "portfolio_risks": list(recommendation.portfolio_risks),
            "actions": [
                {
                    "display_name": action.display_name,
                    "action_now": action.action_now,
                    "delta_krw_now": action.delta_krw_now,
                    "action_if_triggered": action.action_if_triggered,
                    "delta_krw_if_triggered": action.delta_krw_if_triggered,
                    "trigger_conditions": list(action.trigger_conditions),
                    "rationale": action.rationale,
                    "priority": action.priority,
                    "review_required": action.review_required,
                }
                for action in recommendation.actions[:8]
            ],
        },
        "required_meaning": fallback_payload,
    }
    return _writer_prompt_header(language) + (
        "\nPortfolio context JSON:\n"
        f"{json.dumps(compact_payload, ensure_ascii=False)}"
    )


def _writer_prompt_header(language: str) -> str:
    return (
        "You are the final investor-facing writer for TradingAgents.\n"
        "Return exactly one JSON object and nothing else.\n"
        "Do not change the investment decision, action, sizing, trigger, exit, or risk meaning. "
        "Only rewrite and prioritize the presentation for a non-engineer investor.\n"
        "Do not expose internal terms such as legacy rating, decision scope, confidence number, "
        "setup quality enum, RULE_ONLY, fallback, vendor, token, telemetry, semantic judge, or raw codes.\n"
        f"Write in {language}.\n"
        "Schema: "
        '{"headline_action":"...","one_sentence_summary":"...","why_now":["..."],'
        '"how_to_execute":"...","add_if":"...","cut_if":"...","key_risks":["..."],'
        '"watch_next":["..."],"confidence_text":"...","data_caveat_text":"..."}.\n'
        "Keep lists short: why_now up to 3, key_risks up to 2, watch_next up to 3."
    )


def _create_writer_llm(llm_settings: Any | None) -> Any | None:
    if llm_settings is None:
        return None
    provider = str(getattr(llm_settings, "provider", "") or "").strip().lower()
    model = str(
        getattr(llm_settings, "output_model", "")
        or getattr(llm_settings, "deep_model", "")
        or getattr(llm_settings, "quick_model", "")
        or ""
    ).strip()
    if provider == "codex" and not model:
        model = "gpt-5.4"
    if not provider or not model:
        return None

    kwargs: dict[str, Any] = {}
    if provider == "codex":
        kwargs = {
            "codex_binary": getattr(llm_settings, "codex_binary", None),
            "codex_reasoning_effort": getattr(llm_settings, "codex_reasoning_effort", "medium"),
            "codex_summary": getattr(llm_settings, "codex_summary", "none"),
            "codex_personality": getattr(llm_settings, "codex_personality", "none"),
            "codex_workspace_dir": getattr(llm_settings, "codex_workspace_dir", None),
            "codex_request_timeout": getattr(llm_settings, "codex_request_timeout", 120.0),
            "codex_max_retries": getattr(llm_settings, "codex_max_retries", 2),
            "codex_cleanup_threads": getattr(llm_settings, "codex_cleanup_threads", True),
        }
    return create_llm_client(provider=provider, model=model, **kwargs).get_llm()


def _invoke_writer_llm(llm: Any, prompt: str) -> Mapping[str, Any]:
    response = llm.invoke(prompt)
    content = getattr(response, "content", response)
    return _extract_json_object(_normalize_content(content))


def _normalize_writer_payload(
    payload: Mapping[str, Any],
    fallback: dict[str, Any],
    *,
    language: str,
) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        payload = {}

    normalized = {
        "headline_action": _text_field(payload, fallback, "headline_action", language=language),
        "one_sentence_summary": _text_field(payload, fallback, "one_sentence_summary", language=language),
        "why_now": _list_field(payload, fallback, "why_now", limit=3, language=language),
        "how_to_execute": _text_field(payload, fallback, "how_to_execute", language=language),
        "add_if": _text_field(payload, fallback, "add_if", language=language),
        "cut_if": _text_field(payload, fallback, "cut_if", language=language),
        "key_risks": _list_field(payload, fallback, "key_risks", limit=2, language=language),
        "watch_next": _list_field(payload, fallback, "watch_next", limit=3, language=language),
        "confidence_text": _text_field(payload, fallback, "confidence_text", language=language),
        "data_caveat_text": _text_field(payload, fallback, "data_caveat_text", language=language),
    }
    for field in ("headline_action", "how_to_execute", "add_if", "cut_if"):
        if _looks_like_core_change(normalized[field], fallback.get(field), language=language):
            normalized[field] = sanitize_investor_text(fallback.get(field), language=language)
    return normalized


def _format_writer_summary(payload: dict[str, Any], *, language: str, scope: str) -> str:
    korean = is_korean(language)
    if korean:
        headline_label = "오늘 계좌 상태" if scope == "portfolio" else "오늘의 판단"
        labels = {
            "title": "투자자 요약",
            "headline": headline_label,
            "summary": "한 줄 요약",
            "confidence": "판단 강도",
            "data": "자료 상태",
            "why": "핵심 이유",
            "execute": "실행 계획",
            "add": "조건 충족 시",
            "cut": "철회/축소 조건",
            "risks": "주요 리스크",
            "watch": "다음 체크포인트",
        }
    else:
        headline_label = "Account status today" if scope == "portfolio" else "Today"
        labels = {
            "title": "Investor Summary",
            "headline": headline_label,
            "summary": "One-line summary",
            "confidence": "Conviction",
            "data": "Source status",
            "why": "Why It Matters",
            "execute": "Execution Plan",
            "add": "Add If",
            "cut": "Cut If",
            "risks": "Key Risks",
            "watch": "Next Checkpoints",
        }

    lines = [
        f"## {labels['title']}",
        "",
        f"- {labels['headline']}: {payload['headline_action']}",
        f"- {labels['summary']}: {payload['one_sentence_summary']}",
        f"- {labels['confidence']}: {payload['confidence_text']}",
        f"- {labels['data']}: {payload['data_caveat_text']}",
        "",
        f"### {labels['why']}",
        *_bullet_lines(payload["why_now"], language=language),
        "",
        f"### {labels['execute']}",
        f"- {payload['how_to_execute']}",
        "",
        f"### {labels['add']}",
        f"- {payload['add_if']}",
        "",
        f"### {labels['cut']}",
        f"- {payload['cut_if']}",
    ]
    if payload["key_risks"]:
        lines.extend(["", f"### {labels['risks']}", *_bullet_lines(payload["key_risks"], language=language)])
    if payload["watch_next"]:
        lines.extend(["", f"### {labels['watch']}", *_bullet_lines(payload["watch_next"], language=language)])
    return "\n".join(lines)


def _insert_summary_after_title(markdown: str, summary: str) -> str:
    text = str(markdown or "").strip()
    if not text:
        return summary
    if "\n\n" not in text:
        return f"{text}\n\n{summary}\n"
    title, rest = text.split("\n\n", 1)
    return f"{title}\n\n{summary}\n\n{rest}"


def _base_metadata(llm_settings: Any | None, *, scope: str) -> dict[str, Any]:
    return {
        "status": "skipped",
        "scope": scope,
        "provider": str(getattr(llm_settings, "provider", "") or ""),
        "model": str(
            getattr(llm_settings, "output_model", "")
            or getattr(llm_settings, "deep_model", "")
            or getattr(llm_settings, "quick_model", "")
            or ""
        ),
    }


def _text_field(
    payload: Mapping[str, Any],
    fallback: Mapping[str, Any],
    field: str,
    *,
    language: str,
) -> str:
    value = payload.get(field)
    if isinstance(value, list):
        value = " / ".join(str(item) for item in value if str(item).strip())
    text = sanitize_investor_text(value, language=language)
    if text in {"", "없음", "None"}:
        text = sanitize_investor_text(fallback.get(field), language=language)
    return _shorten(text, 280)


def _list_field(
    payload: Mapping[str, Any],
    fallback: Mapping[str, Any],
    field: str,
    *,
    limit: int,
    language: str,
) -> list[str]:
    raw_value = payload.get(field)
    if not isinstance(raw_value, list):
        raw_value = fallback.get(field)
    if not isinstance(raw_value, list):
        raw_value = [raw_value]

    values: list[str] = []
    for item in raw_value:
        text = sanitize_investor_text(item, language=language)
        if text and text not in {"없음", "None"} and text not in values:
            values.append(_shorten(text, 220))
        if len(values) >= limit:
            break
    return values


def _bullet_lines(values: list[str], *, language: str) -> list[str]:
    if not values:
        values = ["없음" if is_korean(language) else "None"]
    return [f"- {value}" for value in values]


def _normalize_content(content: Any) -> Any:
    if not isinstance(content, list):
        return content
    pieces: list[str] = []
    for item in content:
        if isinstance(item, str):
            pieces.append(item)
        elif isinstance(item, Mapping) and item.get("type") == "text":
            pieces.append(str(item.get("text") or ""))
    return "\n".join(piece for piece in pieces if piece)


def _looks_like_core_change(candidate: str, fallback: Any, *, language: str) -> bool:
    fallback_text = sanitize_investor_text(fallback, language=language)
    candidate_text = sanitize_investor_text(candidate, language=language)
    if not fallback_text or fallback_text in {"없음", "None"}:
        return False

    # Numeric levels and sizing are decision facts, not prose style. If the
    # writer drops or changes them, fall back to the deterministic template.
    numbers = re.findall(r"\d+(?:\.\d+)?%?", fallback_text)
    if numbers and any(number not in candidate_text for number in numbers):
        return True

    fallback_lower = fallback_text.lower()
    candidate_lower = candidate_text.lower()
    positive = ("매수", "진입", "add", "buy", "starter", "entry")
    defensive = ("매도", "청산", "축소", "reduce", "trim", "sell", "exit")
    wait = ("관찰", "관망", "확인", "wait", "watch", "confirm")
    immediate = ("즉시", "지금", "now", "immediate")

    if _has_any(fallback_lower, positive) and _has_any(candidate_lower, defensive):
        return True
    if _has_any(fallback_lower, defensive) and _has_any(candidate_lower, positive):
        return True
    if _has_any(fallback_lower, wait) and _has_any(candidate_lower, immediate):
        return True
    return False


def _has_any(text: str, tokens: tuple[str, ...]) -> bool:
    return any(token in text for token in tokens)


def _extract_json_object(payload: Any) -> Mapping[str, Any]:
    if isinstance(payload, Mapping):
        return payload
    if not isinstance(payload, str) or not payload.strip():
        raise ValueError("writer payload must be a non-empty JSON string")

    text = payload.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3 and lines[0].startswith("```") and lines[-1].startswith("```"):
            text = "\n".join(lines[1:-1]).strip()

    try:
        parsed = json.loads(text)
        if isinstance(parsed, Mapping):
            return parsed
    except JSONDecodeError:
        pass

    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            parsed, _ = decoder.raw_decode(text[index:])
        except JSONDecodeError:
            continue
        if isinstance(parsed, Mapping):
            return parsed
    raise ValueError("writer did not return a JSON object")


def _shorten(value: Any, limit: int) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "..."
