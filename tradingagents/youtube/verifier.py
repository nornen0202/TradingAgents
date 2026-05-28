from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
import json
import re
from typing import Any, Callable, Mapping

import yfinance as yf

from tradingagents.dataflows.youtube_video import YouTubeVideoBundle
from tradingagents.llm_clients import create_llm_client
from tradingagents.youtube.config import LLMSettings, VerificationSettings
from tradingagents.youtube_report import EntitySummary, summarize_financial_entities


VERIFIED = "verified"
CONTRADICTED = "contradicted"
UNVERIFIED = "unverified"
STALE = "stale"
LLM_FAILED = "llm_failed"


@dataclass(frozen=True)
class MarketSnapshot:
    ticker: str
    as_of: str
    current_price: float | None = None
    market_cap: float | None = None
    forward_pe: float | None = None
    trailing_pe: float | None = None
    fifty_two_week_high: float | None = None
    fifty_two_week_low: float | None = None
    average_target_price: float | None = None
    source: str = "yfinance"
    status: str = VERIFIED
    error: str = ""


@dataclass(frozen=True)
class VerifiedVideoReport:
    status: str
    final_report_markdown: str
    verification: dict[str, Any]


MarketDataProvider = Callable[[str], MarketSnapshot]
ExternalDataProvider = Callable[[str, datetime], dict[str, Any]]
LLMFactory = Callable[[LLMSettings], Any | None]


def verify_youtube_bundle(
    bundle: YouTubeVideoBundle,
    draft_report: str,
    *,
    llm_settings: LLMSettings,
    verification_settings: VerificationSettings,
    market_data_provider: MarketDataProvider | None = None,
    external_data_provider: ExternalDataProvider | None = None,
    llm_factory: LLMFactory | None = None,
    generated_at: datetime | None = None,
) -> VerifiedVideoReport:
    generated_at = generated_at or datetime.now(timezone.utc)
    market_data_provider = market_data_provider or fetch_market_snapshot
    external_data_provider = external_data_provider or fetch_external_context
    entity_summaries = summarize_financial_entities(bundle.transcript.raw_text if bundle.transcript else "")
    llm = (llm_factory or _create_llm)(llm_settings)

    extracted_claims: dict[str, Any]
    llm_status = "success"
    if llm is None:
        llm_status = LLM_FAILED
        extracted_claims = _claims_from_entities(entity_summaries, verification_settings.max_claims_per_video)
    else:
        try:
            extracted_claims = _extract_claims_with_llm(
                llm,
                bundle=bundle,
                draft_report=draft_report,
                entity_summaries=entity_summaries,
                max_claims=verification_settings.max_claims_per_video,
            )
        except Exception as exc:
            llm_status = LLM_FAILED
            extracted_claims = _claims_from_entities(entity_summaries, verification_settings.max_claims_per_video)
            extracted_claims["llm_error"] = str(exc)

    market_evidence = _collect_market_evidence(
        extracted_claims,
        market_data_provider,
        external_data_provider=external_data_provider,
        generated_at=generated_at,
    )
    verification = _build_verification_payload(
        bundle=bundle,
        extracted_claims=extracted_claims,
        market_evidence=market_evidence,
        generated_at=generated_at,
        llm_status=llm_status,
    )

    final_report = ""
    if llm is not None and llm_status == "success":
        try:
            final_report = _write_final_report_with_llm(
                llm,
                bundle=bundle,
                draft_report=draft_report,
                verification=verification,
            )
        except Exception as exc:
            llm_status = LLM_FAILED
            verification["llm_status"] = llm_status
            verification["llm_error"] = str(exc)
    if not final_report:
        final_report = render_fallback_final_report(bundle, draft_report, verification)

    status = _aggregate_status(verification, llm_status=llm_status)
    verification["status"] = status
    return VerifiedVideoReport(status=status, final_report_markdown=final_report, verification=verification)


def fetch_market_snapshot(ticker: str) -> MarketSnapshot:
    symbol = str(ticker or "").strip().upper()
    if not symbol:
        return MarketSnapshot(ticker=symbol, as_of=datetime.now(timezone.utc).isoformat(), status=UNVERIFIED, error="empty_ticker")
    try:
        instrument = yf.Ticker(symbol)
        info = instrument.info or {}
        fast_info = getattr(instrument, "fast_info", {}) or {}
        return MarketSnapshot(
            ticker=symbol,
            as_of=datetime.now(timezone.utc).isoformat(),
            current_price=_first_float(fast_info, info, ("last_price", "lastPrice", "currentPrice", "regularMarketPrice")),
            market_cap=_first_float(fast_info, info, ("market_cap", "marketCap")),
            forward_pe=_first_float(info, fast_info, ("forwardPE", "forward_pe")),
            trailing_pe=_first_float(info, fast_info, ("trailingPE", "trailing_pe")),
            fifty_two_week_high=_first_float(info, fast_info, ("fiftyTwoWeekHigh", "yearHigh", "fifty_two_week_high")),
            fifty_two_week_low=_first_float(info, fast_info, ("fiftyTwoWeekLow", "yearLow", "fifty_two_week_low")),
            average_target_price=_first_float(info, fast_info, ("targetMeanPrice", "averageAnalystRating")),
            status=VERIFIED,
        )
    except Exception as exc:
        return MarketSnapshot(
            ticker=symbol,
            as_of=datetime.now(timezone.utc).isoformat(),
            status=UNVERIFIED,
            error=str(exc),
        )


def fetch_external_context(ticker: str, generated_at: datetime) -> dict[str, Any]:
    symbol = str(ticker or "").strip().upper()
    if not symbol:
        return {"status": UNVERIFIED, "error": "empty_ticker"}
    if generated_at.tzinfo is None:
        generated_at = generated_at.replace(tzinfo=timezone.utc)
    end_date = generated_at.date()
    start_date = end_date - timedelta(days=7)
    context: dict[str, Any] = {
        "status": UNVERIFIED,
        "source": "tradingagents.dataflows",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }
    try:
        from tradingagents.dataflows.interface import route_to_vendor

        news = route_to_vendor("get_company_news", symbol, start_date.isoformat(), end_date.isoformat())
        context["company_news_excerpt"] = _shorten(str(news), 700)
        if news and "provider unavailable" not in str(news).lower():
            context["status"] = VERIFIED
    except Exception as exc:
        context["company_news_error"] = str(exc)
    try:
        from tradingagents.dataflows.interface import route_to_vendor

        disclosures = route_to_vendor("get_disclosures", symbol, start_date.isoformat(), end_date.isoformat())
        context["disclosure_excerpt"] = _shorten(str(disclosures), 700)
        if disclosures and "provider unavailable" not in str(disclosures).lower() and "no disclosures found" not in str(disclosures).lower():
            context["status"] = VERIFIED
    except Exception as exc:
        context["disclosure_error"] = str(exc)
    if context["status"] != VERIFIED:
        context.setdefault("note", "공개 뉴스/공시 vendor에서 자동 확인 가능한 근거를 충분히 확보하지 못했습니다.")
    return context


def render_fallback_final_report(
    bundle: YouTubeVideoBundle,
    draft_report: str,
    verification: Mapping[str, Any],
) -> str:
    title = bundle.metadata.title or bundle.metadata.video_id
    lines = [
        f"# 투자자용 YouTube 검증 리포트: {title}",
        "",
        "## 핵심 결론",
        "",
        "- 이 리포트는 영상 자막 기반 초안과 공개 시장 데이터로 자동 생성한 검증 결과입니다.",
        "- LLM 정제 단계가 실패했거나 사용할 수 없어 deterministic 형식으로 작성했습니다.",
        "- 영상 속 주장과 검증된 사실은 구분해서 읽어야 하며, 매수/매도 지시가 아닙니다.",
        "",
        "## 검증 상태",
        "",
        f"- 전체 상태: `{verification.get('status') or verification.get('llm_status') or 'unknown'}`",
        f"- LLM 상태: `{verification.get('llm_status') or 'unknown'}`",
        f"- 영상 URL: {bundle.metadata.url}",
        "",
        "## 종목별 공개 데이터 확인",
        "",
    ]
    entity_results = verification.get("entity_results") if isinstance(verification.get("entity_results"), list) else []
    if not entity_results:
        lines.append("- 식별된 종목 또는 검증 가능한 시장 데이터가 없습니다.")
    for item in entity_results:
        snapshot = item.get("market_snapshot") if isinstance(item.get("market_snapshot"), dict) else {}
        lines.extend(
            [
                f"### {item.get('name') or item.get('ticker') or '-'} ({item.get('ticker') or '-'})",
                f"- 검증 상태: `{item.get('status') or UNVERIFIED}`",
                f"- 현재가: `{_display_number(snapshot.get('current_price'))}`",
                f"- 52주 고점/저점: `{_display_number(snapshot.get('fifty_two_week_high'))}` / `{_display_number(snapshot.get('fifty_two_week_low'))}`",
                f"- 시가총액: `{_display_number(snapshot.get('market_cap'))}`",
                f"- 확인 필요: {_join_text(item.get('verification_notes') or [])}",
                "",
            ]
        )
    lines.extend(["## Deterministic 초안", "", draft_report.strip()])
    return "\n".join(lines).strip() + "\n"


def _create_llm(llm_settings: LLMSettings) -> Any | None:
    provider = str(llm_settings.provider or "").strip().lower()
    model = str(llm_settings.deep_model or "").strip()
    if not provider or not model:
        return None
    kwargs: dict[str, Any] = {}
    if provider == "codex":
        kwargs = {
            "codex_binary": llm_settings.codex_binary,
            "codex_reasoning_effort": llm_settings.codex_reasoning_effort,
            "codex_summary": llm_settings.codex_summary,
            "codex_personality": llm_settings.codex_personality,
            "codex_workspace_dir": llm_settings.codex_workspace_dir,
            "codex_request_timeout": llm_settings.codex_request_timeout,
            "codex_max_retries": llm_settings.codex_max_retries,
            "codex_cleanup_threads": llm_settings.codex_cleanup_threads,
            "codex_preflight_mode": llm_settings.codex_preflight_mode,
        }
    return create_llm_client(provider=provider, model=model, **kwargs).get_llm()


def _extract_claims_with_llm(
    llm: Any,
    *,
    bundle: YouTubeVideoBundle,
    draft_report: str,
    entity_summaries: tuple[EntitySummary, ...],
    max_claims: int,
) -> dict[str, Any]:
    payload = {
        "video": _public_metadata(bundle),
        "deterministic_entities": [_entity_to_dict(item) for item in entity_summaries],
        "draft_report": draft_report[:12000],
        "caption_source": {
            "status": bundle.transcript_status,
            "source": getattr(bundle.transcript, "source", None),
            "language": getattr(bundle.transcript, "language_name", None),
        },
    }
    prompt = (
        "You are TradingAgents' YouTube claim extractor.\n"
        "Return exactly one JSON object and nothing else.\n"
        "Extract investor-relevant claims from the report without adding new facts.\n"
        "Schema: {\"overall_thesis\":\"...\",\"entities\":[{\"ticker\":\"...\",\"name\":\"...\","
        "\"claims\":[\"...\"],\"numeric_claims\":[\"...\"],\"risks\":[\"...\"],"
        "\"watch_items\":[\"...\"]}],\"verification_items\":[\"...\"]}.\n"
        f"Limit total claims per video to {max_claims}. Write Korean text where possible.\n\n"
        f"Context JSON:\n{json.dumps(payload, ensure_ascii=False)}"
    )
    response = llm.invoke(prompt)
    content = _normalize_content(getattr(response, "content", response))
    parsed = _extract_json_object(content)
    return _normalize_claims(parsed, fallback=_claims_from_entities(entity_summaries, max_claims))


def _write_final_report_with_llm(
    llm: Any,
    *,
    bundle: YouTubeVideoBundle,
    draft_report: str,
    verification: Mapping[str, Any],
) -> str:
    payload = {
        "video": _public_metadata(bundle),
        "verification": verification,
        "draft_report": draft_report[:12000],
    }
    prompt = (
        "You are the final investor-facing writer for TradingAgents.\n"
        "Write a Korean Markdown report for investors using only the supplied payload.\n"
        "Separate video claims from verified facts. Do not issue buy/sell instructions.\n"
        "Mark unavailable Bloomberg/Morningstar/closed-source claims as unverified/manual check required.\n"
        "Do not include raw transcript text. Keep excerpts short.\n\n"
        f"Payload JSON:\n{json.dumps(payload, ensure_ascii=False)}"
    )
    response = llm.invoke(prompt)
    text = str(_normalize_content(getattr(response, "content", response)) or "").strip()
    return text if text.startswith("#") else f"# 투자자용 YouTube 검증 리포트\n\n{text}".strip() + "\n"


def _collect_market_evidence(
    claims: Mapping[str, Any],
    market_data_provider: MarketDataProvider,
    *,
    external_data_provider: ExternalDataProvider,
    generated_at: datetime,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for entity in _claim_entities(claims):
        ticker = str(entity.get("ticker") or "").strip().upper()
        if not ticker or ticker in {"N/A", "UNKNOWN", "-"}:
            continue
        snapshot = market_data_provider(ticker)
        external_context = external_data_provider(ticker, generated_at)
        entity_claims = [str(item) for item in (entity.get("claims") or [])]
        numeric_claims = [str(item) for item in (entity.get("numeric_claims") or [])]
        notes, status = _verify_claims(entity_claims + numeric_claims, snapshot, external_context)
        results.append(
            {
                "ticker": ticker,
                "name": str(entity.get("name") or ticker),
                "claims": entity_claims[:5],
                "numeric_claims": numeric_claims[:5],
                "risks": [str(item) for item in (entity.get("risks") or [])][:5],
                "watch_items": [str(item) for item in (entity.get("watch_items") or [])][:5],
                "status": status,
                "verification_notes": notes,
                "market_snapshot": asdict(snapshot),
                "external_context": external_context,
            }
        )
    return results


def _verify_claims(
    claims: list[str],
    snapshot: MarketSnapshot,
    external_context: Mapping[str, Any] | None = None,
) -> tuple[list[str], str]:
    if snapshot.status != VERIFIED:
        return ([f"시장 데이터 조회 실패: {snapshot.error or snapshot.status}"], UNVERIFIED)
    notes: list[str] = []
    status = VERIFIED
    if _is_stale(snapshot.as_of):
        status = STALE
        notes.append("시장 데이터 기준시각이 오래되어 stale로 분류했습니다.")
    for claim in claims:
        claim_status, note = _verify_numeric_claim_against_snapshot(claim, snapshot)
        if note:
            notes.append(note)
        if claim_status == CONTRADICTED:
            status = CONTRADICTED
        elif claim_status == UNVERIFIED and status == VERIFIED:
            status = UNVERIFIED
    if any(_requires_closed_source_check(claim) for claim in claims):
        notes.append("Bloomberg/Morningstar 등 폐쇄형 출처 주장은 자동 검증하지 못했습니다.")
        if status == VERIFIED:
            status = UNVERIFIED
    if external_context and external_context.get("status") != VERIFIED:
        notes.append("공개 뉴스/공시 보조 근거를 자동 확보하지 못해 일부 정성 주장은 미검증으로 남겼습니다.")
        if status == VERIFIED:
            status = UNVERIFIED
    if not notes:
        notes.append("공개 시장 스냅샷은 조회됐지만 모든 영상 주장을 완전 검증한 것은 아닙니다.")
    return notes, status


def _verify_numeric_claim_against_snapshot(claim: str, snapshot: MarketSnapshot) -> tuple[str, str]:
    text = str(claim or "")
    if "52주" not in text and "52-week" not in text.lower():
        return VERIFIED, ""
    target = None
    label = ""
    if "고점" in text or "high" in text.lower():
        target = snapshot.fifty_two_week_high
        label = "52주 고점"
    elif "저점" in text or "low" in text.lower():
        target = snapshot.fifty_two_week_low
        label = "52주 저점"
    if target is None:
        return UNVERIFIED, f"{label or '52주 가격'} 데이터가 없어 숫자 주장을 확인하지 못했습니다."
    numbers = [_parse_number(match.group(0)) for match in re.finditer(r"\d+(?:,\d{3})*(?:\.\d+)?", text)]
    numbers = [number for number in numbers if number is not None]
    if not numbers:
        return VERIFIED, ""
    closest = min(numbers, key=lambda value: abs(value - target))
    if target and abs(closest - target) / target > 0.15:
        return CONTRADICTED, f"{label} 주장값({closest:g})이 공개 데이터({target:g})와 15% 이상 다릅니다."
    return VERIFIED, f"{label} 주장값({closest:g})이 공개 데이터({target:g})와 대체로 일치합니다."


def _build_verification_payload(
    *,
    bundle: YouTubeVideoBundle,
    extracted_claims: Mapping[str, Any],
    market_evidence: list[dict[str, Any]],
    generated_at: datetime,
    llm_status: str,
) -> dict[str, Any]:
    return {
        "version": 1,
        "status": llm_status if llm_status == LLM_FAILED else "verified_with_caveats",
        "llm_status": llm_status,
        "generated_at": generated_at.isoformat(),
        "video": _public_metadata(bundle),
        "claims": extracted_claims,
        "entity_results": market_evidence,
        "source_policy": {
            "raw_transcript_published": False,
            "closed_source_claims": "unverified_external_source",
            "auto_caption_warning": bundle.transcript is not None and bundle.transcript.source == "automatic",
        },
    }


def _aggregate_status(verification: Mapping[str, Any], *, llm_status: str) -> str:
    if llm_status == LLM_FAILED:
        return LLM_FAILED
    statuses = {
        str(item.get("status") or "")
        for item in (verification.get("entity_results") or [])
        if isinstance(item, Mapping)
    }
    if CONTRADICTED in statuses:
        return CONTRADICTED
    if STALE in statuses:
        return STALE
    if UNVERIFIED in statuses:
        return UNVERIFIED
    return VERIFIED if statuses else UNVERIFIED


def _claims_from_entities(entity_summaries: tuple[EntitySummary, ...], max_claims: int) -> dict[str, Any]:
    entities: list[dict[str, Any]] = []
    claim_budget = max_claims
    for summary in entity_summaries:
        claims = list(summary.key_points)[: max(1, min(3, claim_budget))]
        claim_budget -= len(claims)
        entities.append(
            {
                "ticker": summary.entity.ticker,
                "name": summary.entity.name,
                "claims": claims,
                "numeric_claims": list(summary.numeric_claims)[:4],
                "risks": list(summary.risk_points)[:3],
                "watch_items": [],
            }
        )
    return {
        "overall_thesis": "영상 자막 기반 deterministic 추출 결과입니다.",
        "entities": entities,
        "verification_items": [],
    }


def _normalize_claims(payload: Mapping[str, Any], *, fallback: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        return fallback
    entities = payload.get("entities")
    if not isinstance(entities, list):
        return fallback
    normalized_entities: list[dict[str, Any]] = []
    for entity in entities:
        if not isinstance(entity, Mapping):
            continue
        normalized_entities.append(
            {
                "ticker": str(entity.get("ticker") or "").strip().upper(),
                "name": str(entity.get("name") or "").strip(),
                "claims": _text_list(entity.get("claims")),
                "numeric_claims": _text_list(entity.get("numeric_claims")),
                "risks": _text_list(entity.get("risks")),
                "watch_items": _text_list(entity.get("watch_items")),
            }
        )
    return {
        "overall_thesis": str(payload.get("overall_thesis") or fallback.get("overall_thesis") or ""),
        "entities": normalized_entities or fallback.get("entities") or [],
        "verification_items": _text_list(payload.get("verification_items")),
    }


def _claim_entities(claims: Mapping[str, Any]) -> list[dict[str, Any]]:
    entities = claims.get("entities")
    if not isinstance(entities, list):
        return []
    return [dict(item) for item in entities if isinstance(item, Mapping)]


def _entity_to_dict(summary: EntitySummary) -> dict[str, Any]:
    return {
        "ticker": summary.entity.ticker,
        "name": summary.entity.name,
        "key_points": list(summary.key_points),
        "numeric_claims": list(summary.numeric_claims),
        "risks": list(summary.risk_points),
        "evidence_excerpt": summary.evidence_excerpt,
    }


def _public_metadata(bundle: YouTubeVideoBundle) -> dict[str, Any]:
    metadata = bundle.metadata
    return {
        "video_id": metadata.video_id,
        "url": metadata.url,
        "title": metadata.title,
        "channel": metadata.channel,
        "channel_id": metadata.channel_id,
        "published_at": metadata.published_at.isoformat() if metadata.published_at else metadata.upload_date,
        "duration_seconds": metadata.duration_seconds,
        "view_count": metadata.view_count,
        "thumbnail_url": metadata.thumbnail_url,
    }


def _extract_json_object(payload: Any) -> Mapping[str, Any]:
    if isinstance(payload, Mapping):
        return payload
    text = str(payload or "").strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3 and lines[0].startswith("```") and lines[-1].startswith("```"):
            text = "\n".join(lines[1:-1]).strip()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, Mapping):
            return parsed
    except json.JSONDecodeError:
        pass
    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            parsed, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, Mapping):
            return parsed
    raise ValueError("LLM response did not contain a JSON object")


def _normalize_content(content: Any) -> str:
    if isinstance(content, list):
        pieces = []
        for item in content:
            if isinstance(item, str):
                pieces.append(item)
            elif isinstance(item, Mapping) and item.get("type") == "text":
                pieces.append(str(item.get("text") or ""))
        return "\n".join(piece for piece in pieces if piece)
    return str(content or "")


def _first_float(primary: Mapping[str, Any], secondary: Mapping[str, Any], keys: tuple[str, ...]) -> float | None:
    for mapping in (primary, secondary):
        for key in keys:
            try:
                value = mapping.get(key)  # type: ignore[attr-defined]
            except Exception:
                continue
            parsed = _parse_number(value)
            if parsed is not None:
                return parsed
    return None


def _parse_number(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None


def _requires_closed_source_check(text: str) -> bool:
    lowered = str(text or "").lower()
    return any(token in lowered for token in ("블룸버그", "bloomberg", "모닝스타", "morningstar", "그룹 포커스", "gurufocus"))


def _is_stale(as_of: str) -> bool:
    try:
        value = datetime.fromisoformat(str(as_of).replace("Z", "+00:00"))
    except ValueError:
        return False
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - value.astimezone(timezone.utc)).days > 3


def _text_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if value in (None, ""):
        return []
    return [str(value).strip()]


def _display_number(value: Any) -> str:
    number = _parse_number(value)
    if number is None:
        return "-"
    if abs(number) >= 1_000_000_000:
        return f"{number / 1_000_000_000:.2f}B"
    return f"{number:,.2f}"


def _join_text(values: list[Any]) -> str:
    return " / ".join(str(item) for item in values if str(item).strip()) or "-"


def _shorten(value: str, limit: int) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)].rstrip() + "..."
