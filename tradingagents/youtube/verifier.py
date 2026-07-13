from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
import json
import math
import os
import re
from typing import Any, Callable, Mapping

import yfinance as yf

from tradingagents.dataflows.youtube_video import (
    YouTubeVideoBundle,
    YouTubeTranscriptSegment,
    assess_transcript_reliability,
)
from tradingagents.llm_clients import create_llm_client
from tradingagents.youtube.config import LLMSettings, VerificationSettings
from tradingagents.youtube.research import (
    collect_research_evidence,
    fallback_research_plan,
    public_evidence_summary,
)
from tradingagents.youtube.verification_status import (
    ASR_UNCERTAIN,
    CONTRADICTED,
    LLM_FAILED,
    PARTIALLY_SUPPORTED,
    STALE,
    SUPPORTED,
    UNVERIFIED,
    VERIFIED,
)
from tradingagents.youtube_report import EntitySummary, summarize_financial_entities


RESEARCH_PIPELINE_VERSION = 4


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


@dataclass(frozen=True)
class YouTubeLLMClients:
    quick: Any | None
    judge: Any | None
    writer: Any | None


MarketDataProvider = Callable[[str], MarketSnapshot]
ExternalDataProvider = Callable[[str, datetime], dict[str, Any]]
ResearchEvidenceProvider = Callable[
    [Mapping[str, Any], Mapping[str, Any], datetime], dict[str, Any]
]
LLMFactory = Callable[[LLMSettings], Any | None]


def verify_youtube_bundle(
    bundle: YouTubeVideoBundle,
    draft_report: str,
    *,
    llm_settings: LLMSettings,
    verification_settings: VerificationSettings,
    market_data_provider: MarketDataProvider | None = None,
    external_data_provider: ExternalDataProvider | None = None,
    research_evidence_provider: ResearchEvidenceProvider | None = None,
    llm_factory: LLMFactory | None = None,
    generated_at: datetime | None = None,
) -> VerifiedVideoReport:
    generated_at = generated_at or datetime.now(timezone.utc)
    market_data_provider = market_data_provider or fetch_market_snapshot
    external_data_provider = external_data_provider or fetch_external_context
    entity_summaries = summarize_financial_entities(
        bundle.transcript.raw_text if bundle.transcript else ""
    )
    owns_llms = llm_factory is None
    if llm_factory is not None:
        shared_llm = llm_factory(llm_settings)
        llms = YouTubeLLMClients(
            quick=shared_llm,
            judge=shared_llm,
            writer=shared_llm,
        )
    else:
        llms = _create_role_llms(llm_settings)

    extracted_claims: dict[str, Any]
    llm_status = "success"
    if llms.quick is None:
        llm_status = LLM_FAILED
        extracted_claims = _claims_from_entities(
            entity_summaries, verification_settings.max_claims_per_video
        )
    else:
        try:
            claim_transcript_chars = _adaptive_transcript_chars_for_llm(
                bundle,
                verification_settings=verification_settings,
            )
            extracted_claims = _extract_claims_with_llm(
                llms.quick,
                bundle=bundle,
                draft_report=draft_report,
                entity_summaries=entity_summaries,
                max_claims=verification_settings.max_claims_per_video,
                max_transcript_chars=claim_transcript_chars,
            )
        except Exception as exc:
            llm_status = LLM_FAILED
            extracted_claims = _claims_from_entities(
                entity_summaries, verification_settings.max_claims_per_video
            )
            extracted_claims["llm_error"] = str(exc)

    market_evidence = _collect_market_evidence(
        extracted_claims,
        market_data_provider,
        external_data_provider=external_data_provider,
        generated_at=generated_at,
    )
    research_plan, research_status = _build_research_plan(
        llms.quick,
        bundle=bundle,
        draft_report=draft_report,
        extracted_claims=extracted_claims,
        verification_settings=verification_settings,
    )
    evidence_bundle = _collect_research_bundle(
        research_plan,
        extracted_claims=extracted_claims,
        generated_at=generated_at,
        verification_settings=verification_settings,
        research_evidence_provider=research_evidence_provider,
    )
    claim_verification, claim_verification_status = _build_claim_verification(
        llms.judge,
        bundle=bundle,
        extracted_claims=extracted_claims,
        market_evidence=market_evidence,
        research_plan=research_plan,
        evidence_bundle=evidence_bundle,
        verification_settings=verification_settings,
    )
    if (
        verification_settings.strict_llm
        and llm_status == "success"
        and verification_settings.research_enabled
        and (research_status == LLM_FAILED or claim_verification_status == LLM_FAILED)
    ):
        llm_status = LLM_FAILED
    verification = _build_verification_payload(
        bundle=bundle,
        extracted_claims=extracted_claims,
        market_evidence=market_evidence,
        research_plan=research_plan,
        evidence_bundle=evidence_bundle,
        claim_verification=claim_verification,
        generated_at=generated_at,
        llm_status=llm_status,
        research_status=research_status,
        claim_verification_status=claim_verification_status,
    )
    verification["llm_routing"] = _llm_routing_metadata(llm_settings)

    final_report = ""
    if llms.writer is not None and llm_status == "success":
        try:
            final_report = _write_final_report_with_llm(
                llms.writer,
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
    if owns_llms:
        _close_role_llms(llms)
    return VerifiedVideoReport(
        status=status, final_report_markdown=final_report, verification=verification
    )


def fetch_market_snapshot(ticker: str) -> MarketSnapshot:
    symbol = str(ticker or "").strip().upper()
    if not symbol:
        return MarketSnapshot(
            ticker=symbol,
            as_of=datetime.now(timezone.utc).isoformat(),
            status=UNVERIFIED,
            error="empty_ticker",
        )
    try:
        instrument = yf.Ticker(symbol)
        info = instrument.info or {}
        fast_info = getattr(instrument, "fast_info", {}) or {}
        snapshot = MarketSnapshot(
            ticker=symbol,
            as_of=datetime.now(timezone.utc).isoformat(),
            current_price=_first_float(
                fast_info,
                info,
                ("last_price", "lastPrice", "currentPrice", "regularMarketPrice"),
            ),
            market_cap=_first_float(fast_info, info, ("market_cap", "marketCap")),
            forward_pe=_first_float(info, fast_info, ("forwardPE", "forward_pe")),
            trailing_pe=_first_float(info, fast_info, ("trailingPE", "trailing_pe")),
            fifty_two_week_high=_first_float(
                info, fast_info, ("fiftyTwoWeekHigh", "yearHigh", "fifty_two_week_high")
            ),
            fifty_two_week_low=_first_float(
                info, fast_info, ("fiftyTwoWeekLow", "yearLow", "fifty_two_week_low")
            ),
            average_target_price=_first_float(
                info, fast_info, ("targetMeanPrice", "averageAnalystRating")
            ),
            status=VERIFIED,
        )
        if not any(
            value is not None
            for value in (
                snapshot.current_price,
                snapshot.market_cap,
                snapshot.forward_pe,
                snapshot.trailing_pe,
                snapshot.fifty_two_week_high,
                snapshot.fifty_two_week_low,
                snapshot.average_target_price,
            )
        ):
            return MarketSnapshot(
                ticker=symbol,
                as_of=snapshot.as_of,
                source=snapshot.source,
                status=UNVERIFIED,
                error="no_usable_market_fields",
            )
        return snapshot
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

        news = route_to_vendor(
            "get_company_news", symbol, start_date.isoformat(), end_date.isoformat()
        )
        context["company_news_excerpt"] = _shorten(str(news), 700)
        if news and "provider unavailable" not in str(news).lower():
            context["status"] = VERIFIED
    except Exception as exc:
        context["company_news_error"] = str(exc)
    try:
        from tradingagents.dataflows.interface import route_to_vendor

        disclosures = route_to_vendor(
            "get_disclosures", symbol, start_date.isoformat(), end_date.isoformat()
        )
        context["disclosure_excerpt"] = _shorten(str(disclosures), 700)
        if (
            disclosures
            and "provider unavailable" not in str(disclosures).lower()
            and "no disclosures found" not in str(disclosures).lower()
        ):
            context["status"] = VERIFIED
    except Exception as exc:
        context["disclosure_error"] = str(exc)
    if context["status"] != VERIFIED:
        context.setdefault(
            "note",
            "공개 뉴스/공시 vendor에서 자동 확인 가능한 근거를 충분히 확보하지 못했습니다.",
        )
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
        "- 이 리포트는 영상 자막/ASR 기반 주장, 공개 시장 데이터, 웹/뉴스/공시 근거 묶음으로 자동 생성한 검증 결과입니다.",
        "- LLM 정제 단계가 실패했거나 사용할 수 없어 deterministic 형식으로 작성했습니다.",
        "- 영상 속 주장과 검증된 사실은 구분해서 읽어야 하며, 매수/매도 지시가 아닙니다.",
        "",
        "## 검증 상태",
        "",
        f"- 전체 상태: `{verification.get('status') or verification.get('llm_status') or 'unknown'}`",
        f"- LLM 상태: `{verification.get('llm_status') or 'unknown'}`",
        f"- 리서치 상태: `{verification.get('research_status') or 'unknown'}`",
        f"- 주장 검증 상태: `{verification.get('claim_verification_status') or 'unknown'}`",
        f"- 자막/ASR 품질: `{(verification.get('transcript_quality') or {}).get('status') or 'unknown'}` "
        f"(score={(verification.get('transcript_quality') or {}).get('score') or '-'})",
        f"- 영상 URL: {bundle.metadata.url}",
        "",
        "## 주장별 검증",
        "",
    ]
    claim_items = (
        (verification.get("claim_verification") or {}).get("claims")
        if isinstance(verification.get("claim_verification"), Mapping)
        else []
    )
    if claim_items:
        for claim in claim_items[:10]:
            if not isinstance(claim, Mapping):
                continue
            lines.extend(
                [
                    f"### {claim.get('claim_id') or '-'}",
                    f"- 영상 주장: {claim.get('claim_text') or '-'}",
                    f"- 근거 시각/신뢰도: `{claim.get('timestamp') or '-'}` / source `{_display_number(claim.get('source_confidence'))}` / ASR `{_display_number(claim.get('asr_confidence'))}`",
                    f"- 상태: `{claim.get('status') or UNVERIFIED}`",
                    f"- 확인된 사실: {_join_text(claim.get('verified_facts') or [])}",
                    f"- 반론/한계: {_join_text(claim.get('counterpoints') or [])}",
                    f"- 투자 시사점: {claim.get('investor_implication') or '-'}",
                    "",
                ]
            )
    else:
        lines.append("- 주장별 검증 결과가 없습니다.")
    lines.extend(
        [
            "## 공개 근거",
            "",
        ]
    )
    public_evidence = public_evidence_summary(verification.get("evidence") or {})
    if public_evidence:
        for item in public_evidence[:8]:
            url = item.get("source_url") or ""
            lines.append(
                f"- [{item.get('title') or item.get('publisher') or 'source'}]({url}) - {item.get('excerpt') or '-'}"
            )
    else:
        lines.append("- 공개 가능한 외부 근거를 충분히 확보하지 못했습니다.")
    lines.extend(
        [
            "",
            "## 종목별 공개 데이터 확인",
            "",
        ]
    )
    entity_results = (
        verification.get("entity_results")
        if isinstance(verification.get("entity_results"), list)
        else []
    )
    if not entity_results:
        lines.append("- 식별된 종목 또는 검증 가능한 시장 데이터가 없습니다.")
    for item in entity_results:
        snapshot = (
            item.get("market_snapshot")
            if isinstance(item.get("market_snapshot"), dict)
            else {}
        )
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


def _create_role_llms(llm_settings: LLMSettings) -> YouTubeLLMClients:
    return YouTubeLLMClients(
        quick=_create_llm(llm_settings, role="quick"),
        judge=_create_llm(llm_settings, role="judge"),
        writer=_create_llm(llm_settings, role="writer"),
    )


def _close_role_llms(llms: YouTubeLLMClients) -> None:
    closed: set[int] = set()
    for llm in (llms.quick, llms.judge, llms.writer):
        if llm is None or id(llm) in closed:
            continue
        closed.add(id(llm))
        close = getattr(llm, "close", None)
        if not callable(close):
            continue
        try:
            close()
        except Exception:
            pass


def _create_llm(llm_settings: LLMSettings, *, role: str = "judge") -> Any | None:
    provider = str(llm_settings.provider or "").strip().lower()
    model_by_role = {
        "quick": llm_settings.quick_model or llm_settings.deep_model,
        "judge": llm_settings.deep_model,
        "writer": llm_settings.output_model or llm_settings.deep_model,
    }
    effort_by_role = {
        "quick": llm_settings.codex_quick_reasoning_effort
        or llm_settings.codex_reasoning_effort,
        "judge": llm_settings.codex_deep_reasoning_effort
        or llm_settings.codex_reasoning_effort,
        "writer": llm_settings.codex_output_reasoning_effort
        or llm_settings.codex_reasoning_effort,
    }
    model = str(model_by_role.get(role) or llm_settings.deep_model or "").strip()
    if not provider or not model:
        return None
    kwargs: dict[str, Any] = {}
    if provider == "codex":
        kwargs = {
            "codex_binary": llm_settings.codex_binary,
            "codex_reasoning_effort": effort_by_role.get(role)
            or llm_settings.codex_reasoning_effort,
            "codex_summary": llm_settings.codex_summary,
            "codex_personality": llm_settings.codex_personality,
            "codex_workspace_dir": llm_settings.codex_workspace_dir,
            "codex_request_timeout": llm_settings.codex_request_timeout,
            "codex_max_retries": llm_settings.codex_max_retries,
            "codex_cleanup_threads": llm_settings.codex_cleanup_threads,
            "codex_preflight_mode": llm_settings.codex_preflight_mode,
            "model_role": role,
        }
    return create_llm_client(provider=provider, model=model, **kwargs).get_llm()


def _llm_routing_metadata(llm_settings: LLMSettings) -> dict[str, dict[str, str]]:
    return {
        "claim_extraction_and_research": {
            "model": str(llm_settings.quick_model or llm_settings.deep_model),
            "reasoning_effort": str(
                llm_settings.codex_quick_reasoning_effort
                or llm_settings.codex_reasoning_effort
            ),
            "role": "quick",
        },
        "evidence_verification": {
            "model": str(llm_settings.deep_model),
            "reasoning_effort": str(
                llm_settings.codex_deep_reasoning_effort
                or llm_settings.codex_reasoning_effort
            ),
            "role": "judge",
        },
        "report_writing": {
            "model": str(llm_settings.output_model or llm_settings.deep_model),
            "reasoning_effort": str(
                llm_settings.codex_output_reasoning_effort
                or llm_settings.codex_reasoning_effort
            ),
            "role": "writer",
        },
    }


def _extract_claims_with_llm(
    llm: Any,
    *,
    bundle: YouTubeVideoBundle,
    draft_report: str,
    entity_summaries: tuple[EntitySummary, ...],
    max_claims: int,
    max_transcript_chars: int,
) -> dict[str, Any]:
    payload = {
        "video": _public_metadata(bundle),
        "deterministic_entities": [_entity_to_dict(item) for item in entity_summaries],
        "draft_report": draft_report[:12000],
        "transcript_chunks_for_claim_extraction": _transcript_chunks_for_llm(
            bundle, max_chars=max_transcript_chars
        ),
        "transcript_quality": _transcript_quality_for_payload(bundle),
        "caption_source": {
            "status": bundle.transcript_status,
            "source": getattr(bundle.transcript, "source", None),
            "language": getattr(bundle.transcript, "language_name", None),
        },
    }
    prompt = (
        "You are TradingAgents' YouTube claim extractor.\n"
        "Return exactly one JSON object and nothing else.\n"
        "Extract investor-relevant claims from all timestamped transcript chunks and deterministic draft without adding new facts.\n"
        "Prefer transcript chunks over the draft when they differ. Use chunk start/end timestamps to avoid missing later-video claims. "
        "Preserve concrete numbers, dates, policy names, market moves, and cited external sources as separate "
        "numeric_claims or verification_items.\n"
        'Schema: {"overall_thesis":"...","entities":[{"ticker":"...","name":"...",'
        '"claims":["..."],"numeric_claims":["..."],"risks":["..."],'
        '"watch_items":["..."],"source_timestamps":["00:01:23"],"source_confidence":0.0}],'
        '"verification_items":["..."],"asr_suspect_terms":["..."],"data_quality_notes":["..."]}.\n'
        f"Limit total claims per video to {max_claims}. Write Korean text where possible.\n\n"
        f"Context JSON:\n{json.dumps(payload, ensure_ascii=False)}"
    )
    response = llm.invoke(prompt)
    content = _normalize_content(getattr(response, "content", response))
    parsed = _extract_json_object(content)
    return _normalize_claims(
        parsed, fallback=_claims_from_entities(entity_summaries, max_claims)
    )


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
        "Write a Korean Markdown report for investors from transcript-derived video claims, "
        "host-collected web/news/market/disclosure evidence, and claim-verification results.\n"
        "Use the evidence bundle aggressively, but do not invent facts that are not supported by the supplied evidence. "
        "Separate '영상 주장' from '확인된 사실/근거'. Include source links for the strongest evidence items. "
        "Use claim timestamps, source_confidence, asr_confidence, and transcript_quality to explain uncertainty. "
        "Discuss bullish logic, counterarguments, data-quality limits, near-term checkpoints, invalidation conditions, "
        "and concrete observation items that an investor can monitor. Do not issue buy/sell instructions.\n"
        "Mark unavailable Bloomberg/Morningstar/closed-source claims as unverified/manual check required. "
        "Do not include raw transcript text. Keep evidence excerpts short.\n\n"
        f"Payload JSON:\n{json.dumps(payload, ensure_ascii=False)}"
    )
    response = llm.invoke(prompt)
    text = str(_normalize_content(getattr(response, "content", response)) or "").strip()
    return (
        text
        if text.startswith("#")
        else f"# 투자자용 YouTube 검증 리포트\n\n{text}".strip() + "\n"
    )


def _build_research_plan(
    llm: Any | None,
    *,
    bundle: YouTubeVideoBundle,
    draft_report: str,
    extracted_claims: Mapping[str, Any],
    verification_settings: VerificationSettings,
) -> tuple[dict[str, Any], str]:
    fallback = fallback_research_plan(
        extracted_claims,
        video_title=bundle.metadata.title,
        max_queries=verification_settings.max_research_queries,
    )
    if not verification_settings.research_enabled:
        fallback["status"] = "disabled"
        return fallback, "disabled"
    if llm is None:
        return fallback, LLM_FAILED
    payload = {
        "video": _public_metadata(bundle),
        "claims": extracted_claims,
        "draft_report_excerpt": draft_report[:8000],
        "transcript_private_chunks": _transcript_chunks_for_llm(
            bundle,
            max_chars=_adaptive_transcript_chars_for_llm(
                bundle,
                verification_settings=verification_settings,
            ),
        ),
        "transcript_quality": _transcript_quality_for_payload(bundle),
        "limits": {
            "max_research_queries": verification_settings.max_research_queries,
            "max_claims": verification_settings.max_claims_per_video,
            "transcript_budget_chars": _adaptive_transcript_chars_for_llm(
                bundle,
                verification_settings=verification_settings,
            ),
        },
    }
    prompt = (
        "You are TradingAgents' investor research planner for a YouTube video.\n"
        "Return exactly one JSON object and nothing else.\n"
        "Use the transcript-derived claims and timestamped transcript chunks to create a concrete verification plan. "
        "For each material claim, assign a stable claim_id such as C1, C2, ... and propose Korean/English web, news, "
        "market-data, disclosure, and official-source queries that would verify or refute it. "
        "Route by claim type: company claims to IR/SEC/DART/exchange/news, macro claims to central banks/statistics agencies/FRED, "
        "commodity claims to EIA/CME/ICE or other primary sources, and market-price claims to market data. "
        "Prioritize official sources, exchange/regulator/company IR, and reputable news. "
        "Flag ASR-uncertain terms and closed-source-only claims.\n"
        'Schema: {"version":1,"claims":[{"claim_id":"C1","entity":"...","ticker":"...",'
        '"claim_text":"...","claim_type":"market|policy|company|macro|numeric|source_citation|asr_uncertain",'
        '"time_window":"...","queries":[{"query":"...","language":"ko|en",'
        '"source_priority":["official","news","market"],"reason":"..."}],'
        '"required_evidence":["..."],"asr_suspect_terms":["..."]}],'
        '"global_queries":[{"query":"...","language":"ko","reason":"..."}],'
        '"closed_source_claims":["..."],"asr_suspect_terms":["..."]}.\n'
        f"Keep total queries at or below {verification_settings.max_research_queries}.\n\n"
        f"Payload JSON:\n{json.dumps(payload, ensure_ascii=False)}"
    )
    try:
        response = llm.invoke(prompt)
        parsed = _extract_json_object(
            _normalize_content(getattr(response, "content", response))
        )
        plan = _normalize_research_plan(
            parsed,
            fallback=fallback,
            max_queries=verification_settings.max_research_queries,
        )
        plan["status"] = "success"
        return plan, "success"
    except Exception as exc:
        fallback["status"] = LLM_FAILED
        fallback["llm_error"] = str(exc)
        return fallback, LLM_FAILED


def _collect_research_bundle(
    research_plan: Mapping[str, Any],
    *,
    extracted_claims: Mapping[str, Any],
    generated_at: datetime,
    verification_settings: VerificationSettings,
    research_evidence_provider: ResearchEvidenceProvider | None,
) -> dict[str, Any]:
    if not verification_settings.research_enabled:
        return {
            "version": 1,
            "status": "disabled",
            "generated_at": generated_at.isoformat(),
            "query_count": 0,
            "evidence_count": 0,
            "items": [],
            "errors": [],
            "source_policy": {"raw_transcript_included": False, "excerpts_only": True},
        }
    if research_evidence_provider is not None:
        return dict(
            research_evidence_provider(research_plan, extracted_claims, generated_at)
        )
    return collect_research_evidence(
        research_plan,
        generated_at=generated_at,
        max_queries=verification_settings.max_research_queries,
        max_evidence_items=verification_settings.max_evidence_items,
        max_evidence_per_claim=verification_settings.max_evidence_per_claim,
        fetch_web_pages=verification_settings.fetch_web_pages,
        max_web_pages=verification_settings.max_web_pages,
        evidence_relevance_gate_enabled=verification_settings.evidence_relevance_gate_enabled,
        min_evidence_relevance_score=verification_settings.min_evidence_relevance_score,
    )


def _build_claim_verification(
    llm: Any | None,
    *,
    bundle: YouTubeVideoBundle,
    extracted_claims: Mapping[str, Any],
    market_evidence: list[dict[str, Any]],
    research_plan: Mapping[str, Any],
    evidence_bundle: Mapping[str, Any],
    verification_settings: VerificationSettings,
) -> tuple[dict[str, Any], str]:
    fallback = _fallback_claim_verification(
        extracted_claims=extracted_claims,
        research_plan=research_plan,
        evidence_bundle=evidence_bundle,
        market_evidence=market_evidence,
        bundle=bundle,
    )
    if not verification_settings.research_enabled:
        fallback["status"] = "disabled"
        return fallback, "disabled"
    if llm is None:
        return fallback, LLM_FAILED
    payload = {
        "video": _public_metadata(bundle),
        "claims": extracted_claims,
        "research_plan": research_plan,
        "evidence": _evidence_for_llm(
            evidence_bundle, limit=verification_settings.max_evidence_items
        ),
        "market_evidence": market_evidence,
        "transcript_quality": _transcript_quality_for_payload(bundle),
        "caption_source": {
            "status": bundle.transcript_status,
            "source": getattr(bundle.transcript, "source", None),
            "language": getattr(bundle.transcript, "language_name", None),
        },
    }
    prompt = (
        "You are TradingAgents' evidence arbiter for an investor-facing YouTube report.\n"
        "Return exactly one JSON object and nothing else.\n"
        "For every planned claim, compare the video claim against the supplied web/news/market/disclosure evidence. "
        "Do not use unsupported memory. Mark missing or weak evidence as unverified. "
        "Use statuses: supported, partially_supported, contradicted, unverified, stale, asr_uncertain.\n"
        'Schema: {"version":1,"overall_status":"supported|partially_supported|contradicted|unverified|stale|asr_uncertain",'
        '"claims":[{"claim_id":"C1","claim_text":"...","status":"...",'
        '"confidence":0.0,"supporting_evidence_ids":["E1"],"contradicting_evidence_ids":["E2"],'
        '"verified_facts":["..."],"counterpoints":["..."],"investor_implication":"...",'
        '"manual_check_required":false,"timestamp":"00:01:23","source_confidence":0.0,'
        '"asr_confidence":0.0,"numeric_parse":{"claimed":"...","observed":"..."},"notes":"..."}],'
        '"data_quality_notes":["..."],"investor_checkpoints":["..."]}.\n\n'
        f"Payload JSON:\n{json.dumps(payload, ensure_ascii=False)}"
    )
    try:
        response = llm.invoke(prompt)
        parsed = _extract_json_object(
            _normalize_content(getattr(response, "content", response))
        )
        return _normalize_claim_verification(parsed, fallback=fallback), "success"
    except Exception as exc:
        fallback["llm_error"] = str(exc)
        return fallback, LLM_FAILED


def _collect_market_evidence(
    claims: Mapping[str, Any],
    market_data_provider: MarketDataProvider,
    *,
    external_data_provider: ExternalDataProvider,
    generated_at: datetime,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for entity in _claim_entities(claims):
        lookup_symbol = _resolve_claim_market_symbol(entity)
        if lookup_symbol is None:
            continue
        ticker, is_macro = lookup_symbol
        snapshot = market_data_provider(ticker)
        external_context = (
            _macro_external_context(ticker)
            if is_macro
            else external_data_provider(ticker, generated_at)
        )
        entity_claims = [str(item) for item in (entity.get("claims") or [])]
        numeric_claims = [str(item) for item in (entity.get("numeric_claims") or [])]
        notes, status = _verify_claims(
            entity_claims + numeric_claims, snapshot, external_context
        )
        results.append(
            {
                "ticker": ticker,
                "original_ticker": str(entity.get("ticker") or "").strip().upper(),
                "name": str(entity.get("name") or ticker),
                "claims": entity_claims[:5],
                "numeric_claims": numeric_claims[:5],
                "risks": [str(item) for item in (entity.get("risks") or [])][:5],
                "watch_items": [
                    str(item) for item in (entity.get("watch_items") or [])
                ][:5],
                "status": status,
                "verification_notes": notes,
                "market_snapshot": asdict(snapshot),
                "external_context": external_context,
            }
        )
    return results


def _resolve_claim_market_symbol(entity: Mapping[str, Any]) -> tuple[str, bool] | None:
    raw_ticker = str(entity.get("ticker") or "").strip().upper()
    name = str(entity.get("name") or "").strip()
    normalized_name = name.lower()
    placeholder_tickers = {
        "",
        "N/A",
        "UNKNOWN",
        "-",
        "MARKET",
        "INDEX",
        "OIL",
        "BRENT",
        "CRUDE",
    }

    if "코스피" in name or "kospi" in normalized_name or "한국 증시" in name:
        return "^KS11", True
    if "브렌트" in name or "brent" in normalized_name:
        return "BZ=F", True
    if "유가" in name or "원유" in name or "crude" in normalized_name:
        return "CL=F", True
    if "니케이" in name or "nikkei" in normalized_name:
        return "^N225", True
    if "항셍" in name or "hang seng" in normalized_name:
        return "^HSI", True

    if raw_ticker in placeholder_tickers:
        return None
    return raw_ticker, False


def _macro_external_context(ticker: str) -> dict[str, Any]:
    return {
        "status": VERIFIED,
        "source": "yfinance_macro_snapshot",
        "note": f"{ticker} is treated as a market/index/commodity symbol; company news and disclosure lookup is skipped.",
    }


def _verify_claims(
    claims: list[str],
    snapshot: MarketSnapshot,
    external_context: Mapping[str, Any] | None = None,
) -> tuple[list[str], str]:
    if snapshot.status != VERIFIED:
        return (
            [f"시장 데이터 조회 실패: {snapshot.error or snapshot.status}"],
            UNVERIFIED,
        )
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
        notes.append(
            "Bloomberg/Morningstar 등 폐쇄형 출처 주장은 자동 검증하지 못했습니다."
        )
        if status == VERIFIED:
            status = UNVERIFIED
    if external_context and external_context.get("status") != VERIFIED:
        notes.append(
            "공개 뉴스/공시 보조 근거를 자동 확보하지 못해 일부 정성 주장은 미검증으로 남겼습니다."
        )
        if status == VERIFIED:
            status = UNVERIFIED
    if not notes:
        notes.append(
            "공개 시장 스냅샷은 조회됐지만 영상 주장을 직접 대조할 수 있는 검증 규칙이 없어 미검증으로 분류했습니다."
        )
        if status == VERIFIED:
            status = UNVERIFIED
    return notes, status


def _verify_numeric_claim_against_snapshot(
    claim: str, snapshot: MarketSnapshot
) -> tuple[str, str]:
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
        return (
            UNVERIFIED,
            f"{label or '52주 가격'} 데이터가 없어 숫자 주장을 확인하지 못했습니다.",
        )
    numbers = [
        _parse_number(match.group(0))
        for match in re.finditer(r"\d+(?:,\d{3})*(?:\.\d+)?", text)
    ]
    numbers = [number for number in numbers if number is not None]
    if not numbers:
        return VERIFIED, ""
    closest = min(numbers, key=lambda value: abs(value - target))
    if target and abs(closest - target) / target > 0.15:
        return (
            CONTRADICTED,
            f"{label} 주장값({closest:g})이 공개 데이터({target:g})와 15% 이상 다릅니다.",
        )
    return (
        VERIFIED,
        f"{label} 주장값({closest:g})이 공개 데이터({target:g})와 대체로 일치합니다.",
    )


def _build_verification_payload(
    *,
    bundle: YouTubeVideoBundle,
    extracted_claims: Mapping[str, Any],
    market_evidence: list[dict[str, Any]],
    research_plan: Mapping[str, Any],
    evidence_bundle: Mapping[str, Any],
    claim_verification: Mapping[str, Any],
    generated_at: datetime,
    llm_status: str,
    research_status: str,
    claim_verification_status: str,
) -> dict[str, Any]:
    return {
        "version": RESEARCH_PIPELINE_VERSION,
        "status": llm_status if llm_status == LLM_FAILED else "verified_with_caveats",
        "llm_status": llm_status,
        "research_status": research_status,
        "claim_verification_status": claim_verification_status,
        "generated_at": generated_at.isoformat(),
        "video": _public_metadata(bundle),
        "claims": extracted_claims,
        "research_plan": research_plan,
        "evidence": evidence_bundle,
        "claim_verification": claim_verification,
        "entity_results": market_evidence,
        "transcript_quality": _transcript_quality_for_payload(bundle),
        "source_policy": {
            "raw_transcript_published": False,
            "raw_transcript_in_evidence": False,
            "research_pipeline_version": RESEARCH_PIPELINE_VERSION,
            "closed_source_claims": "unverified_external_source",
            "auto_caption_warning": bundle.transcript is not None
            and bundle.transcript.source == "automatic",
            "local_asr_warning": bundle.transcript is not None
            and bundle.transcript.source == "local_asr",
        },
    }


def _aggregate_status(verification: Mapping[str, Any], *, llm_status: str) -> str:
    if llm_status == LLM_FAILED:
        return LLM_FAILED
    claim_statuses = {
        str(item.get("status") or "")
        for item in ((verification.get("claim_verification") or {}).get("claims") or [])
        if isinstance(item, Mapping)
    }
    if CONTRADICTED in claim_statuses:
        return CONTRADICTED
    if STALE in claim_statuses:
        return STALE
    if ASR_UNCERTAIN in claim_statuses:
        return ASR_UNCERTAIN
    if UNVERIFIED in claim_statuses:
        return UNVERIFIED
    if PARTIALLY_SUPPORTED in claim_statuses:
        return PARTIALLY_SUPPORTED
    if SUPPORTED in claim_statuses and claim_statuses <= {SUPPORTED}:
        return VERIFIED
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


def _claims_from_entities(
    entity_summaries: tuple[EntitySummary, ...], max_claims: int
) -> dict[str, Any]:
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
        "asr_suspect_terms": [],
    }


def _normalize_research_plan(
    payload: Mapping[str, Any],
    *,
    fallback: dict[str, Any],
    max_queries: int,
) -> dict[str, Any]:
    claims = payload.get("claims")
    if not isinstance(claims, list):
        return fallback
    normalized_claims: list[dict[str, Any]] = []
    query_count = 0
    for index, claim in enumerate(claims, 1):
        if not isinstance(claim, Mapping):
            continue
        queries: list[dict[str, Any]] = []
        for query_item in claim.get("queries") or []:
            if query_count >= max_queries:
                break
            if isinstance(query_item, Mapping):
                query = str(query_item.get("query") or "").strip()
                language = str(query_item.get("language") or "ko").strip()
                reason = str(query_item.get("reason") or "").strip()
                priority = _text_list(query_item.get("source_priority"))
            else:
                query = str(query_item or "").strip()
                language = "ko"
                reason = ""
                priority = []
            if not query:
                continue
            queries.append(
                {
                    "query": query,
                    "language": language,
                    "source_priority": priority,
                    "reason": reason,
                }
            )
            query_count += 1
        normalized_claims.append(
            {
                "claim_id": str(claim.get("claim_id") or f"C{index}").strip(),
                "entity": str(claim.get("entity") or "").strip(),
                "ticker": str(claim.get("ticker") or "").strip().upper(),
                "claim_text": str(claim.get("claim_text") or "").strip(),
                "claim_type": str(
                    claim.get("claim_type") or "company_or_macro"
                ).strip(),
                "time_window": str(claim.get("time_window") or "").strip(),
                "queries": queries,
                "required_evidence": _text_list(claim.get("required_evidence")),
                "asr_suspect_terms": _text_list(claim.get("asr_suspect_terms")),
            }
        )
    if not normalized_claims:
        return fallback
    global_queries: list[dict[str, Any]] = []
    for query_item in payload.get("global_queries") or []:
        if query_count >= max_queries:
            break
        if isinstance(query_item, Mapping):
            query = str(query_item.get("query") or "").strip()
            language = str(query_item.get("language") or "ko").strip()
            reason = str(query_item.get("reason") or "").strip()
        else:
            query = str(query_item or "").strip()
            language = "ko"
            reason = ""
        if not query:
            continue
        global_queries.append({"query": query, "language": language, "reason": reason})
        query_count += 1
    return {
        "version": 1,
        "status": "success",
        "claims": normalized_claims,
        "global_queries": global_queries,
        "closed_source_claims": _text_list(payload.get("closed_source_claims")),
        "asr_suspect_terms": _text_list(payload.get("asr_suspect_terms")),
    }


def _fallback_claim_verification(
    *,
    extracted_claims: Mapping[str, Any],
    research_plan: Mapping[str, Any],
    evidence_bundle: Mapping[str, Any],
    market_evidence: list[dict[str, Any]],
    bundle: YouTubeVideoBundle,
) -> dict[str, Any]:
    evidence_items = [
        item
        for item in (evidence_bundle.get("items") or [])
        if isinstance(item, Mapping)
    ]
    evidence_by_claim: dict[str, list[Mapping[str, Any]]] = {}
    for item in evidence_items:
        evidence_by_claim.setdefault(str(item.get("claim_id") or "GLOBAL"), []).append(
            item
        )
    entity_status_by_claim_text = _entity_status_lookup(market_evidence)
    claims: list[dict[str, Any]] = []
    for index, planned in enumerate(research_plan.get("claims") or [], 1):
        if not isinstance(planned, Mapping):
            continue
        claim_id = str(planned.get("claim_id") or f"C{index}")
        claim_text = str(planned.get("claim_text") or "")
        evidence_for_claim = evidence_by_claim.get(claim_id, [])
        status = UNVERIFIED
        confidence = 0.25
        if evidence_for_claim:
            status = PARTIALLY_SUPPORTED
            confidence = 0.55
        for token, entity_status in entity_status_by_claim_text.items():
            if token and token in claim_text:
                if entity_status == CONTRADICTED:
                    status = CONTRADICTED
                    confidence = 0.75
                elif entity_status == STALE and status not in {CONTRADICTED}:
                    status = STALE
                    confidence = 0.45
                elif entity_status == VERIFIED and status == UNVERIFIED:
                    status = PARTIALLY_SUPPORTED
                    confidence = 0.50
        if _has_asr_warning(bundle, research_plan, planned):
            status = ASR_UNCERTAIN if status == UNVERIFIED else status
        claims.append(
            {
                "claim_id": claim_id,
                "claim_text": claim_text,
                "status": status,
                "confidence": confidence,
                "supporting_evidence_ids": [
                    str(item.get("evidence_id") or "")
                    for item in evidence_for_claim[:3]
                    if item.get("evidence_id")
                ],
                "contradicting_evidence_ids": [],
                "verified_facts": [
                    _shorten(str(item.get("title") or item.get("excerpt") or ""), 180)
                    for item in evidence_for_claim[:2]
                    if str(item.get("title") or item.get("excerpt") or "").strip()
                ],
                "counterpoints": []
                if evidence_for_claim
                else [
                    "자동 조사에서 직접 확인 가능한 외부 근거를 충분히 찾지 못했습니다."
                ],
                "investor_implication": "관련 뉴스/공시/가격 데이터를 추가 관찰해야 합니다.",
                "manual_check_required": status in {UNVERIFIED, ASR_UNCERTAIN},
                "notes": "LLM 주장 판정 실패 시 deterministic fallback으로 산출했습니다.",
            }
        )
    if not claims:
        for entity in extracted_claims.get("entities") or []:
            if not isinstance(entity, Mapping):
                continue
            for claim_text in (entity.get("claims") or [])[:2]:
                claims.append(
                    {
                        "claim_id": f"C{len(claims) + 1}",
                        "claim_text": str(claim_text),
                        "status": UNVERIFIED,
                        "confidence": 0.2,
                        "supporting_evidence_ids": [],
                        "contradicting_evidence_ids": [],
                        "verified_facts": [],
                        "counterpoints": ["리서치 플랜이 충분히 생성되지 않았습니다."],
                        "investor_implication": "수동 확인이 필요합니다.",
                        "manual_check_required": True,
                        "notes": "fallback",
                    }
                )
    return {
        "version": 1,
        "overall_status": _overall_claim_status([item["status"] for item in claims]),
        "claims": claims,
        "data_quality_notes": _data_quality_notes(evidence_bundle, bundle),
        "investor_checkpoints": _fallback_investor_checkpoints(extracted_claims),
    }


def _normalize_claim_verification(
    payload: Mapping[str, Any], *, fallback: dict[str, Any]
) -> dict[str, Any]:
    raw_claims = payload.get("claims")
    if not isinstance(raw_claims, list):
        return fallback
    claims: list[dict[str, Any]] = []
    for index, claim in enumerate(raw_claims, 1):
        if not isinstance(claim, Mapping):
            continue
        status = str(claim.get("status") or UNVERIFIED).strip()
        if status not in {
            SUPPORTED,
            PARTIALLY_SUPPORTED,
            CONTRADICTED,
            UNVERIFIED,
            STALE,
            ASR_UNCERTAIN,
        }:
            status = UNVERIFIED
        claims.append(
            {
                "claim_id": str(claim.get("claim_id") or f"C{index}"),
                "claim_text": str(claim.get("claim_text") or ""),
                "status": status,
                "confidence": _bounded_confidence(claim.get("confidence")),
                "supporting_evidence_ids": _text_list(
                    claim.get("supporting_evidence_ids")
                ),
                "contradicting_evidence_ids": _text_list(
                    claim.get("contradicting_evidence_ids")
                ),
                "verified_facts": _text_list(claim.get("verified_facts")),
                "counterpoints": _text_list(claim.get("counterpoints")),
                "investor_implication": str(claim.get("investor_implication") or ""),
                "manual_check_required": bool(
                    claim.get(
                        "manual_check_required", status in {UNVERIFIED, ASR_UNCERTAIN}
                    )
                ),
                "timestamp": str(
                    claim.get("timestamp") or claim.get("source_timestamp") or ""
                ),
                "source_confidence": _bounded_confidence(
                    claim.get("source_confidence")
                ),
                "asr_confidence": _bounded_confidence(claim.get("asr_confidence")),
                "numeric_parse": dict(claim.get("numeric_parse") or {})
                if isinstance(claim.get("numeric_parse"), Mapping)
                else {},
                "notes": str(claim.get("notes") or ""),
            }
        )
    if not claims:
        return fallback
    overall = str(
        payload.get("overall_status")
        or _overall_claim_status([item["status"] for item in claims])
    )
    if overall not in {
        SUPPORTED,
        PARTIALLY_SUPPORTED,
        CONTRADICTED,
        UNVERIFIED,
        STALE,
        ASR_UNCERTAIN,
    }:
        overall = _overall_claim_status([item["status"] for item in claims])
    return {
        "version": 1,
        "overall_status": overall,
        "claims": claims,
        "data_quality_notes": _text_list(payload.get("data_quality_notes")),
        "investor_checkpoints": _text_list(payload.get("investor_checkpoints")),
    }


def _normalize_claims(
    payload: Mapping[str, Any], *, fallback: dict[str, Any]
) -> dict[str, Any]:
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
                "source_timestamps": _text_list(entity.get("source_timestamps")),
                "source_confidence": _bounded_confidence(
                    entity.get("source_confidence")
                ),
            }
        )
    return {
        "overall_thesis": str(
            payload.get("overall_thesis") or fallback.get("overall_thesis") or ""
        ),
        "entities": normalized_entities or fallback.get("entities") or [],
        "verification_items": _text_list(payload.get("verification_items")),
        "asr_suspect_terms": _text_list(payload.get("asr_suspect_terms")),
        "data_quality_notes": _text_list(payload.get("data_quality_notes")),
    }


def _claim_entities(claims: Mapping[str, Any]) -> list[dict[str, Any]]:
    entities = claims.get("entities")
    if not isinstance(entities, list):
        return []
    return [dict(item) for item in entities if isinstance(item, Mapping)]


def _evidence_for_llm(
    evidence_bundle: Mapping[str, Any], *, limit: int
) -> dict[str, Any]:
    items = []
    for item in evidence_bundle.get("items") or []:
        if not isinstance(item, Mapping):
            continue
        items.append(
            {
                "evidence_id": item.get("evidence_id"),
                "claim_id": item.get("claim_id"),
                "title": _shorten(str(item.get("title") or ""), 220),
                "publisher": item.get("publisher"),
                "source_url": item.get("source_url"),
                "published_at": item.get("published_at"),
                "source_tier": item.get("source_tier"),
                "excerpt": _shorten(str(item.get("excerpt") or ""), 700),
            }
        )
        if len(items) >= limit:
            break
    return {
        "status": evidence_bundle.get("status"),
        "generated_at": evidence_bundle.get("generated_at"),
        "evidence_count": evidence_bundle.get("evidence_count"),
        "items": items,
        "errors": list(evidence_bundle.get("errors") or [])[:5],
    }


def _transcript_for_llm(bundle: YouTubeVideoBundle, *, max_chars: int) -> str:
    chunks = _transcript_chunks_for_llm(bundle, max_chars=max_chars)
    if chunks:
        lines = []
        for chunk in chunks:
            prefix = f"[{chunk.get('start_time')} - {chunk.get('end_time')}] "
            lines.append(prefix + str(chunk.get("text") or "").strip())
        return "\n\n".join(lines)[:max_chars]
    transcript = bundle.transcript
    if transcript is None:
        return ""
    return str(transcript.raw_text or "")[:max_chars]


def _transcript_chunks_for_llm(
    bundle: YouTubeVideoBundle, *, max_chars: int
) -> list[dict[str, Any]]:
    transcript = bundle.transcript
    if transcript is None:
        return []
    chunks = _build_transcript_chunks(transcript.segments, transcript.raw_text)
    if not chunks:
        return []
    selected = _select_transcript_chunks(chunks, max_chars=max_chars)
    return [
        {
            "chunk_id": f"T{index + 1}",
            "source_index": chunk["source_index"],
            "start_seconds": chunk["start_seconds"],
            "end_seconds": chunk["end_seconds"],
            "start_time": _format_timestamp(chunk["start_seconds"]),
            "end_time": _format_timestamp(chunk["end_seconds"]),
            "text": chunk["text"],
            "selection_reason": chunk.get("selection_reason", "coverage"),
            "score": round(float(chunk.get("score") or 0.0), 3),
        }
        for index, chunk in enumerate(selected)
    ]


def _build_transcript_chunks(
    segments: tuple[YouTubeTranscriptSegment, ...],
    raw_text: str,
) -> list[dict[str, Any]]:
    max_chunk_chars = max(
        200, int(_env_int_like("TRADINGAGENTS_YOUTUBE_TRANSCRIPT_CHUNK_CHARS", 3200))
    )
    chunks: list[dict[str, Any]] = []
    if segments:
        current: list[str] = []
        start_seconds: float | None = None
        end_seconds = 0.0
        for segment in segments:
            text = str(getattr(segment, "text", "") or "").strip()
            if not text:
                continue
            start = float(getattr(segment, "start_seconds", 0.0) or 0.0)
            duration = float(getattr(segment, "duration_seconds", 0.0) or 0.0)
            candidate = " ".join([*current, text]).strip()
            if current and len(candidate) > max_chunk_chars:
                chunk_text = " ".join(current).strip()
                chunks.append(
                    _make_transcript_chunk(
                        source_index=len(chunks),
                        start_seconds=start_seconds or 0.0,
                        end_seconds=end_seconds,
                        text=chunk_text,
                    )
                )
                current = [text]
                start_seconds = start
            else:
                if start_seconds is None:
                    start_seconds = start
                current.append(text)
            end_seconds = max(end_seconds, start + duration)
        if current:
            chunks.append(
                _make_transcript_chunk(
                    source_index=len(chunks),
                    start_seconds=start_seconds or 0.0,
                    end_seconds=end_seconds,
                    text=" ".join(current).strip(),
                )
            )
        return chunks

    text = str(raw_text or "").strip()
    if not text:
        return []
    for index, start in enumerate(range(0, len(text), max_chunk_chars)):
        chunks.append(
            _make_transcript_chunk(
                source_index=index,
                start_seconds=0.0,
                end_seconds=0.0,
                text=text[start : start + max_chunk_chars].strip(),
            )
        )
    return chunks


def _make_transcript_chunk(
    *, source_index: int, start_seconds: float, end_seconds: float, text: str
) -> dict[str, Any]:
    return {
        "source_index": source_index,
        "start_seconds": round(float(start_seconds or 0.0), 3),
        "end_seconds": round(float(end_seconds or 0.0), 3),
        "text": text,
        "score": _financial_chunk_score(text),
    }


def _select_transcript_chunks(
    chunks: list[dict[str, Any]], *, max_chars: int
) -> list[dict[str, Any]]:
    if not chunks:
        return []
    budget = max(1000, max_chars)
    total_chars = sum(len(str(chunk.get("text") or "")) for chunk in chunks)
    if total_chars <= budget:
        for chunk in chunks:
            chunk["selection_reason"] = "full_coverage"
        return chunks

    selected: dict[int, dict[str, Any]] = {}

    def add(index: int, reason: str) -> None:
        if index < 0 or index >= len(chunks):
            return
        item = dict(chunks[index])
        item["selection_reason"] = reason
        selected[index] = item

    add(0, "opening_context")
    add(len(chunks) - 1, "closing_context")
    max_chunks = max(
        4, _env_int_like("TRADINGAGENTS_YOUTUBE_TRANSCRIPT_MAX_CHUNKS", 12)
    )
    ranked = sorted(
        range(len(chunks)),
        key=lambda idx: float(chunks[idx].get("score") or 0.0),
        reverse=True,
    )
    for index in ranked:
        if len(selected) >= max(3, max_chunks // 2):
            break
        add(index, "claim_dense")
    stride = max(
        1,
        len(chunks)
        // max(
            3, _env_int_like("TRADINGAGENTS_YOUTUBE_TRANSCRIPT_MIN_COVERAGE_CHUNKS", 5)
        ),
    )
    for index in range(stride, len(chunks) - 1, stride):
        if len(selected) >= max_chunks:
            break
        add(index, "time_coverage")
    for index in ranked:
        if len(selected) >= max_chunks:
            break
        add(index, "claim_dense")

    result: list[dict[str, Any]] = []
    used = 0
    for index in sorted(selected):
        chunk = selected[index]
        text = str(chunk.get("text") or "")
        if not text:
            continue
        remaining = budget - used
        if remaining <= 0 or len(result) >= max_chunks:
            break
        if len(text) > remaining:
            if remaining < 500:
                break
            chunk = dict(chunk)
            chunk["text"] = (
                text[:remaining].rsplit(" ", 1)[0].strip() or text[:remaining]
            )
            chunk["selection_reason"] = f"{chunk.get('selection_reason')}_truncated"
        result.append(chunk)
        used += len(str(chunk.get("text") or ""))
    return result


def _financial_chunk_score(text: str) -> float:
    value = str(text or "")
    if not value:
        return 0.0
    score = 0.0
    score += min(8, len(re.findall(r"\d", value))) * 0.4
    score += len(re.findall(r"\b[A-Z]{1,5}(?:\.[A-Z]{1,3})?\b", value)) * 0.7
    keywords = (
        "매수",
        "매도",
        "투자",
        "실적",
        "영업이익",
        "매출",
        "가이던스",
        "컨센서스",
        "금리",
        "환율",
        "유가",
        "정책",
        "리스크",
        "반론",
        "목표가",
        "밸류에이션",
        "FOMC",
        "CPI",
        "PCE",
        "EPS",
        "PER",
    )
    lowered = value.lower()
    score += sum(1.0 for keyword in keywords if keyword.lower() in lowered)
    return score


def _format_timestamp(seconds: Any) -> str:
    value = max(0, int(float(seconds or 0)))
    hours, rem = divmod(value, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def _transcript_quality_for_payload(bundle: YouTubeVideoBundle) -> dict[str, Any]:
    return assess_transcript_reliability(
        bundle.transcript,
        duration_seconds=bundle.metadata.duration_seconds,
    )


def _adaptive_transcript_chars_for_llm(
    bundle: YouTubeVideoBundle,
    *,
    verification_settings: VerificationSettings,
) -> int:
    base = max(1000, int(verification_settings.max_transcript_chars_for_llm or 24000))
    if not verification_settings.adaptive_transcript_budget_enabled:
        return base
    transcript = bundle.transcript
    if transcript is None:
        return base
    quality = _transcript_quality_for_payload(bundle)
    raw_chars = int(quality.get("chars") or len(str(transcript.raw_text or "")))
    if raw_chars <= base:
        return base
    extended = max(
        base, int(verification_settings.extended_transcript_chars_for_llm or base)
    )
    duration_seconds = int(bundle.metadata.duration_seconds or 0)
    source = str(quality.get("source") or "").strip().lower()
    status = str(quality.get("status") or "").strip().lower()
    warnings = [str(item) for item in (quality.get("warnings") or [])]
    should_extend = (
        duration_seconds >= 1800
        or raw_chars >= int(base * 1.35)
        or source in {"automatic", "local_asr"}
        or status in {"usable", "poor", "unavailable"}
        or bool(warnings)
    )
    if not should_extend:
        return base
    return min(extended, raw_chars)


def _env_int_like(name: str, default: int) -> int:
    try:
        return int(float(os.getenv(name, default)))
    except (TypeError, ValueError):
        return default


def _entity_status_lookup(market_evidence: list[dict[str, Any]]) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for item in market_evidence:
        name = str(item.get("name") or "").strip()
        ticker = str(item.get("ticker") or "").strip()
        status = str(item.get("status") or "")
        for token in (name, ticker):
            if token:
                lookup[token] = status
    return lookup


def _has_asr_warning(
    bundle: YouTubeVideoBundle,
    research_plan: Mapping[str, Any],
    planned_claim: Mapping[str, Any],
) -> bool:
    if bundle.transcript is None:
        return True
    quality = _transcript_quality_for_payload(bundle)
    if str(quality.get("status") or "") == "poor":
        return True
    if getattr(bundle.transcript, "source", None) == "local_asr":
        return bool(
            planned_claim.get("asr_suspect_terms")
            or research_plan.get("asr_suspect_terms")
        )
    return False


def _overall_claim_status(statuses: list[str]) -> str:
    status_set = {str(item) for item in statuses if str(item)}
    if not status_set:
        return UNVERIFIED
    if CONTRADICTED in status_set:
        return CONTRADICTED
    if STALE in status_set:
        return STALE
    if ASR_UNCERTAIN in status_set:
        return ASR_UNCERTAIN
    if UNVERIFIED in status_set:
        return UNVERIFIED
    if PARTIALLY_SUPPORTED in status_set:
        return PARTIALLY_SUPPORTED
    if SUPPORTED in status_set:
        return SUPPORTED
    return UNVERIFIED


def _data_quality_notes(
    evidence_bundle: Mapping[str, Any], bundle: YouTubeVideoBundle
) -> list[str]:
    notes: list[str] = []
    if evidence_bundle.get("status") != VERIFIED:
        notes.append("웹/뉴스/공시 근거가 충분히 확보되지 않은 주장이 있습니다.")
    if bundle.transcript is not None and getattr(bundle.transcript, "source", None) in {
        "automatic",
        "local_asr",
    }:
        notes.append(
            "자동자막/ASR 기반 분석이므로 고유명사와 숫자는 수동 확인이 필요할 수 있습니다."
        )
    if evidence_bundle.get("errors"):
        notes.append("일부 검색/페이지 수집 요청이 실패했습니다.")
    return notes


def _fallback_investor_checkpoints(extracted_claims: Mapping[str, Any]) -> list[str]:
    checkpoints: list[str] = []
    for entity in extracted_claims.get("entities") or []:
        if not isinstance(entity, Mapping):
            continue
        checkpoints.extend(_text_list(entity.get("watch_items")))
    return checkpoints[:8] or [
        "영상 주장과 관련된 가격, 공시, 정책 뉴스의 후속 업데이트를 확인합니다."
    ]


def _bounded_confidence(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, number))


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
        "published_at": metadata.published_at.isoformat()
        if metadata.published_at
        else metadata.upload_date,
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
        if (
            len(lines) >= 3
            and lines[0].startswith("```")
            and lines[-1].startswith("```")
        ):
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


def _first_float(
    primary: Mapping[str, Any], secondary: Mapping[str, Any], keys: tuple[str, ...]
) -> float | None:
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
        number = float(str(value).replace(",", ""))
        return None if math.isnan(number) or math.isinf(number) else number
    except (TypeError, ValueError):
        return None


def _requires_closed_source_check(text: str) -> bool:
    lowered = str(text or "").lower()
    return any(
        token in lowered
        for token in (
            "블룸버그",
            "bloomberg",
            "모닝스타",
            "morningstar",
            "그룹 포커스",
            "gurufocus",
        )
    )


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
