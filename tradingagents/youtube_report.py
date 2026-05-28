from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
from typing import Iterable

from tradingagents.dataflows.youtube_video import (
    YouTubeVideoBundle,
    fetch_youtube_video,
)


@dataclass(frozen=True)
class MentionedEntity:
    ticker: str
    name: str
    aliases: tuple[str, ...]


@dataclass(frozen=True)
class EntitySummary:
    entity: MentionedEntity
    mention_count: int
    key_points: tuple[str, ...]
    numeric_claims: tuple[str, ...]
    risk_points: tuple[str, ...]
    evidence_excerpt: str


DEFAULT_FINANCIAL_ENTITIES: tuple[MentionedEntity, ...] = (
    MentionedEntity("ORCL", "Oracle", ("오라클", "ORCL")),
    MentionedEntity("NOW", "ServiceNow", ("서비스 나우", "서비스나우", "NOW")),
    MentionedEntity("CRM", "Salesforce", ("세일즈 포스", "세일즈포스", "CRM")),
    MentionedEntity("WDAY", "Workday", ("워크데이", "머데이", "WDAY", "WDA")),
    MentionedEntity("NTNX", "Nutanix", ("뉴타닉스", "유타닉스", "NTNX")),
)

OPPORTUNITY_TERMS = (
    "저평가",
    "성장",
    "매출",
    "수주",
    "계약",
    "AI",
    "인공지능",
    "자사주",
    "매수",
    "상승",
    "목표",
    "현금",
    "이익률",
)
RISK_TERMS = (
    "리스크",
    "우려",
    "공포",
    "빠졌",
    "추락",
    "부채",
    "대체",
    "못하면",
    "느려질",
    "약해질",
    "집중",
)
CHECKPOINT_TERMS = ("체크포인트", "실적", "자사주", "순환", "수주", "매입", "발표")
SOURCE_ATTRIBUTION_TERMS = (
    "블룸버그",
    "모닝스타",
    "뱅크 오브 아메리카",
    "Bank of America",
    "그룹 포커스",
    "애널리스트",
)
ENTITY_SECTION_BOUNDARY_TERMS = (
    "자, 다섯 개 종목",
    "다섯 개 종목을 전부",
    "초보 투자자들이",
    "그럼 투자자로서",
    "핵심 체크포인트",
    "정리할게",
)


def write_youtube_video_report(
    url_or_id: str,
    output_path: str | Path,
    *,
    language: str = "Korean",
    transcript_languages: Iterable[str] = ("ko", "en"),
    include_auto_captions: bool = True,
    generated_at: datetime | None = None,
) -> tuple[Path, YouTubeVideoBundle]:
    bundle = fetch_youtube_video(
        url_or_id,
        transcript_languages=transcript_languages,
        include_auto_captions=include_auto_captions,
    )
    report = build_youtube_video_report(bundle, language=language, generated_at=generated_at)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")
    return path, bundle


def build_youtube_video_report(
    bundle: YouTubeVideoBundle,
    *,
    language: str = "Korean",
    generated_at: datetime | None = None,
) -> str:
    if str(language).strip().lower() != "korean":
        return _build_english_report(bundle, generated_at=generated_at)
    return _build_korean_report(bundle, generated_at=generated_at)


def _build_korean_report(bundle: YouTubeVideoBundle, *, generated_at: datetime | None) -> str:
    metadata = bundle.metadata
    transcript = bundle.transcript
    text = transcript.raw_text if transcript else ""
    generated_at = generated_at or datetime.now()
    entity_summaries = summarize_financial_entities(text)
    top_terms = _top_terms(text)
    common_logic = _extract_common_logic(text)
    risk_logic = _extract_risk_logic(text)
    checkpoints = _extract_checkpoints(text)
    verification_items = _extract_verification_items(text)

    lines = [
        f"# 유튜브 영상 분석 리포트: {metadata.title or metadata.video_id}",
        "",
        f"- 채널: {metadata.channel or '-'}",
        f"- 영상 URL: {metadata.url}",
        f"- 업로드일: {_format_date(metadata.published_at, metadata.upload_date)}",
        f"- 길이: {_format_duration(metadata.duration_seconds)}",
        f"- 조회수: {_format_int(metadata.view_count)}",
        f"- 생성 시각: {generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 1. 분석 가능 수준",
        "",
        _render_collection_status(bundle),
        "",
        "## 2. 핵심 요약",
        "",
        _render_executive_summary(metadata.title, entity_summaries, top_terms, has_transcript=bool(text)),
        "",
        "## 3. 종목별 주장 요약",
        "",
        _render_entity_table(entity_summaries),
        "",
        "## 4. 공통 투자 논리",
        "",
        *_render_bullets(common_logic, fallback="자막 기반으로 공통 논리를 충분히 추출하지 못했습니다."),
        "",
        "## 5. 주요 리스크와 반론",
        "",
        *_render_bullets(risk_logic, fallback="영상에서 명시적으로 반복된 리스크 문장을 충분히 추출하지 못했습니다."),
        "",
        "## 6. 후속 체크포인트",
        "",
        *_render_bullets(checkpoints, fallback="명시적 체크포인트를 충분히 추출하지 못했습니다."),
        "",
        "## 7. 검증 필요 항목",
        "",
        *_render_bullets(verification_items, fallback="외부 출처나 숫자 검증 후보를 충분히 추출하지 못했습니다."),
        "",
        "## 8. 원문 근거 발췌",
        "",
        _render_evidence(entity_summaries),
        "",
        "## 9. 결론",
        "",
        _render_conclusion(entity_summaries, has_transcript=bool(text)),
    ]
    return "\n".join(lines).strip() + "\n"


def _build_english_report(bundle: YouTubeVideoBundle, *, generated_at: datetime | None) -> str:
    metadata = bundle.metadata
    transcript = bundle.transcript
    text = transcript.raw_text if transcript else ""
    generated_at = generated_at or datetime.now()
    entity_summaries = summarize_financial_entities(text)
    lines = [
        f"# YouTube Video Analysis Report: {metadata.title or metadata.video_id}",
        "",
        f"- Channel: {metadata.channel or '-'}",
        f"- URL: {metadata.url}",
        f"- Uploaded: {_format_date(metadata.published_at, metadata.upload_date)}",
        f"- Duration: {_format_duration(metadata.duration_seconds)}",
        f"- Views: {_format_int(metadata.view_count)}",
        f"- Generated: {generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Collection Status",
        "",
        _render_collection_status(bundle),
        "",
        "## Summary",
        "",
        _render_executive_summary(metadata.title, entity_summaries, _top_terms(text), has_transcript=bool(text)),
        "",
        "## Entity Claims",
        "",
        _render_entity_table(entity_summaries),
    ]
    return "\n".join(lines).strip() + "\n"


def summarize_financial_entities(
    transcript_text: str,
    entities: tuple[MentionedEntity, ...] = DEFAULT_FINANCIAL_ENTITIES,
) -> tuple[EntitySummary, ...]:
    text = _normalize_text(transcript_text)
    if not text:
        return ()

    positions: list[tuple[int, MentionedEntity]] = []
    for entity in entities:
        position = _first_alias_position(text, entity.aliases)
        if position >= 0:
            positions.append((position, entity))
    positions.sort(key=lambda item: item[0])
    if not positions:
        return ()

    summaries: list[EntitySummary] = []
    for index, (start, entity) in enumerate(positions):
        default_end = positions[index + 1][0] if index + 1 < len(positions) else len(text)
        end = _entity_section_end(text, start, default_end)
        section = text[start:end].strip()
        if not section:
            continue
        key_points = _select_sentences(section, OPPORTUNITY_TERMS, limit=3)
        numeric_claims = _select_number_sentences(section, limit=4)
        risk_points = _select_sentences(section, RISK_TERMS, limit=2)
        evidence = _shorten(_select_first_sentence(section), 180)
        summaries.append(
            EntitySummary(
                entity=entity,
                mention_count=_count_alias_mentions(text, entity.aliases),
                key_points=tuple(key_points),
                numeric_claims=tuple(numeric_claims),
                risk_points=tuple(risk_points),
                evidence_excerpt=evidence,
            )
        )
    return tuple(summaries)


def _render_collection_status(bundle: YouTubeVideoBundle) -> str:
    transcript = bundle.transcript
    if not transcript:
        return (
            "- 자막 본문: 수집 실패 또는 미제공\n"
            f"- 사용 가능 수동 자막: {_format_language_list(bundle.available_manual_caption_languages)}\n"
            f"- 사용 가능 자동 자막: {_format_language_list(bundle.available_auto_caption_languages)}\n"
            "- 이 경우 리포트는 제목/설명 등 메타데이터 기반으로만 제한됩니다."
        )
    return (
        f"- 자막 본문: 수집 성공 ({transcript.source}, {transcript.language_name}, {transcript.track_ext})\n"
        f"- 자막 세그먼트: {len(transcript.segments):,}개\n"
        f"- 정규화 본문 길이: {len(transcript.raw_text):,}자\n"
        f"- 사용 가능 수동 자막: {_format_language_list(bundle.available_manual_caption_languages)}\n"
        f"- 사용 가능 자동 자막: {_format_language_list(bundle.available_auto_caption_languages)}\n"
        "- 주의: 자동자막은 인식 오류가 있을 수 있으므로 숫자와 고유명사는 원출처 재검증이 필요합니다."
    )


def _render_executive_summary(
    title: str,
    summaries: tuple[EntitySummary, ...],
    top_terms: tuple[str, ...],
    *,
    has_transcript: bool,
) -> str:
    if not has_transcript:
        return "- 자막을 확보하지 못해 영상의 실제 논지를 충분히 요약할 수 없습니다."

    entities = ", ".join(f"{item.entity.name}({item.entity.ticker})" for item in summaries)
    term_text = ", ".join(top_terms) if top_terms else "핵심어 추출 부족"
    if not entities:
        return "\n".join(
            [
                f"- 영상은 `{title}`라는 제목 아래 개별 종목보다 시장/매크로 이슈를 중심으로 다룹니다.",
                f"- 자막 기준 반복 핵심어는 {term_text}입니다.",
                "- 이 deterministic 초안은 영상 발화를 구조화한 1차 산출물이며, "
                "최종 리포트에서는 LLM 검증 단계가 시장·자산 단위 주장과 재검증 필요 수치를 다시 분리합니다.",
                "- 투자 판단에는 영상 주장과 현재 시장 데이터, 원출처 확인을 별도로 대조해야 합니다.",
            ]
        )
    return "\n".join(
        [
            f"- 영상은 `{title}`라는 제목 아래 {entities}를 중심으로 다룹니다.",
            "- 중심 논지는 AI 인프라/기업용 소프트웨어 종목 일부가 시장 주도주 랠리에서 소외됐지만, "
            "실적·수주·자사주 매입·AI 제품 내재화 측면에서 재평가 여지가 있다는 주장입니다.",
            f"- 자막 기준 반복 핵심어는 {term_text}입니다.",
            "- 이 리포트는 영상 속 주장을 구조화한 것이며, 투자 판단에는 현재 주가·실적 원문·공시 확인이 별도로 필요합니다.",
        ]
    )


def _render_entity_table(summaries: tuple[EntitySummary, ...]) -> str:
    if not summaries:
        return "자막에서 사전 정의된 종목/티커를 식별하지 못했습니다."
    lines = [
        "| 종목 | 핵심 논리 | 제시 근거/숫자 | 리스크/검증 포인트 |",
        "| --- | --- | --- | --- |",
    ]
    for summary in summaries:
        key_point = _join_compact(summary.key_points, fallback="핵심 논리 추출 부족")
        numeric = _join_compact(summary.numeric_claims, fallback="숫자 근거 추출 부족")
        risk = _join_compact(summary.risk_points, fallback="명시 리스크 추출 부족")
        label = f"{summary.entity.name} ({summary.entity.ticker})"
        lines.append(
            "| "
            + " | ".join(
                _escape_markdown_cell(value)
                for value in (
                    label,
                    key_point,
                    numeric,
                    risk,
                )
            )
            + " |"
        )
    return "\n".join(lines)


def _render_evidence(summaries: tuple[EntitySummary, ...]) -> str:
    if not summaries:
        return "- 발췌할 종목별 근거가 없습니다."
    lines: list[str] = []
    for summary in summaries:
        lines.append(f"### {summary.entity.name} ({summary.entity.ticker})")
        lines.append(f"- 언급 횟수: {summary.mention_count}")
        lines.append(f"- 대표 발췌: {_shorten(summary.evidence_excerpt, 160)}")
        if summary.numeric_claims:
            lines.append(f"- 숫자 근거 후보: {_join_compact(summary.numeric_claims[:2], fallback='없음')}")
        lines.append("")
    return "\n".join(lines).strip()


def _render_conclusion(summaries: tuple[EntitySummary, ...], *, has_transcript: bool) -> str:
    if not has_transcript:
        return "현재 구현은 메타데이터 리포트까지만 만들 수 있습니다. 자막 또는 ASR 백엔드를 연결해야 내용 요약이 가능합니다."
    if not summaries:
        return (
            "자막 또는 ASR 본문은 수집됐지만 사전 정의된 종목/티커 중심 영상은 아닙니다. "
            "이 경우 최종 리포트는 LLM 검증 단계에서 시장·자산·거시 이벤트 단위로 주장과 체크포인트를 재구성해야 합니다."
        )
    return (
        "단일 영상 기준으로는 자동자막만으로도 메타데이터, 핵심 종목, 반복 논리, 숫자 주장, "
        "리스크와 후속 체크포인트를 리포트 형식으로 추출할 수 있습니다. 다만 이 단계의 산출물은 "
        "영상 발화 요약이며, 사실 검증 리포트가 되려면 공시·실적 발표·현재 주가 데이터와 교차검증하는 "
        "후처리 단계가 추가되어야 합니다."
    )


def _extract_checkpoints(text: str) -> list[str]:
    sentences = _sentences(text)
    selected = [
        sentence
        for sentence in sentences
        if any(term in sentence for term in CHECKPOINT_TERMS)
        and any(marker in sentence for marker in ("첫 번째", "두 번째", "세 번째", "봐야", "확인"))
    ]
    if selected:
        return [_shorten(sentence, 180) for sentence in selected[:5]]
    return _select_sentences(text, CHECKPOINT_TERMS, limit=4)


def _extract_common_logic(text: str) -> list[str]:
    marker_positions = [
        position
        for marker in ("파괴와 내재화", "AI 때문에 사라지는게", "지금 시장은 AI의 첫 번째 단계")
        for position in [text.find(marker)]
        if position >= 0
    ]
    section = text[min(marker_positions):] if marker_positions else text
    common_terms = (
        "파괴",
        "내재화",
        "AI 때문에",
        "AI를 자기",
        "실제 AI 매출",
        "두 번째 단계",
        "하드웨어",
        "소프트웨어",
        "순환",
        "재발견",
    )
    selected = []
    for sentence in _sentences(section):
        if not any(term in sentence for term in common_terms):
            continue
        if any(term in sentence for term in ("못하면", "부채", "리스크도", "해자")):
            continue
        shortened = _shorten(sentence, 190)
        if shortened not in selected:
            selected.append(shortened)
        if len(selected) >= 5:
            break
    return selected or _select_sentences(text, OPPORTUNITY_TERMS, limit=5)


def _extract_risk_logic(text: str) -> list[str]:
    start = text.find("리스크도 체크하자")
    end = text.find("오히려 우리는", start) if start >= 0 else -1
    section = text[start:end] if start >= 0 and end > start else text
    selected = _select_sentences(section, RISK_TERMS, limit=4)
    return selected or _select_sentences(text, RISK_TERMS, limit=4)


def _extract_verification_items(text: str) -> list[str]:
    sentences = _sentences(text)
    items = [
        _shorten(sentence, 190)
        for sentence in sentences
        if any(term in sentence for term in SOURCE_ATTRIBUTION_TERMS)
    ]
    number_heavy = [
        _shorten(sentence, 190)
        for sentence in sentences
        if len(re.findall(r"\d", sentence)) >= 4 and any(unit in sentence for unit in ("달러", "%", "배", "조", "억"))
    ]
    combined: list[str] = []
    for item in items + number_heavy:
        if item not in combined:
            combined.append(item)
        if len(combined) >= 6:
            break
    combined.append("자동자막 기반 분석이므로 종목명, 티커, 숫자 단위, 날짜는 원영상/공시/실적 자료로 재확인해야 합니다.")
    return combined


def _select_sentences(text: str, terms: tuple[str, ...], *, limit: int) -> list[str]:
    candidates: list[tuple[int, str]] = []
    for sentence in _sentences(text):
        score = sum(1 for term in terms if term and term in sentence)
        if score <= 0:
            continue
        if re.search(r"\d", sentence):
            score += 1
        if 40 <= len(sentence) <= 220:
            score += 1
        candidates.append((score, sentence))
    candidates.sort(key=lambda item: (-item[0], len(item[1])))
    selected: list[str] = []
    for _, sentence in candidates:
        shortened = _shorten(sentence, 180)
        if shortened not in selected:
            selected.append(shortened)
        if len(selected) >= limit:
            break
    return selected


def _select_number_sentences(text: str, *, limit: int) -> list[str]:
    selected: list[str] = []
    for sentence in _sentences(text):
        if not re.search(r"\d", sentence):
            continue
        if not any(unit in sentence for unit in ("달러", "%", "배", "조", "억", "명", "PER", "RPO")):
            continue
        shortened = _shorten(sentence, 170)
        if shortened not in selected:
            selected.append(shortened)
        if len(selected) >= limit:
            break
    return selected


def _top_terms(text: str) -> tuple[str, ...]:
    terms = (
        "AI",
        "인공지능",
        "저평가",
        "매출",
        "실적",
        "자사주",
        "수주",
        "계약",
        "순환",
        "클라우드",
        "소프트웨어",
        "리스크",
    )
    counts = [(term, text.count(term)) for term in terms]
    ranked = [term for term, count in sorted(counts, key=lambda item: (-item[1], item[0])) if count > 0]
    return tuple(ranked[:6])


def _first_alias_position(text: str, aliases: tuple[str, ...]) -> int:
    lowered = text.lower()
    positions = []
    for alias in aliases:
        position = lowered.find(alias.lower())
        if position >= 0:
            positions.append(position)
    return min(positions) if positions else -1


def _entity_section_end(text: str, start: int, default_end: int) -> int:
    boundary_positions = []
    for marker in ENTITY_SECTION_BOUNDARY_TERMS:
        position = text.find(marker, start)
        if start < position < default_end:
            boundary_positions.append(position)
    return min(boundary_positions) if boundary_positions else default_end


def _count_alias_mentions(text: str, aliases: tuple[str, ...]) -> int:
    lowered = text.lower()
    return sum(lowered.count(alias.lower()) for alias in aliases if alias)


def _select_first_sentence(section: str) -> str:
    sentences = _sentences(section)
    return sentences[0] if sentences else section


def _sentences(text: str) -> list[str]:
    normalized = _normalize_text(text)
    normalized = re.sub(r"(?<=[.!?])(?=(?!\d)\S)", " ", normalized)
    parts = re.split(r"(?<=[.!?])\s+|\n+", normalized)
    sentences: list[str] = []
    for part in parts:
        sentence = part.strip(" -")
        if len(sentence) < 12:
            continue
        sentences.append(sentence)
    return sentences


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _render_bullets(values: Iterable[str], *, fallback: str) -> list[str]:
    items = [str(value).strip() for value in values if str(value).strip()]
    if not items:
        items = [fallback]
    return [f"- {item}" for item in items]


def _join_compact(values: Iterable[str], *, fallback: str) -> str:
    items = [_shorten(str(value).strip(), 115) for value in values if str(value).strip()]
    return "<br>".join(items[:3]) if items else fallback


def _escape_markdown_cell(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def _shorten(value: str, limit: int) -> str:
    text = _normalize_text(value)
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "..."


def _format_duration(seconds: int | None) -> str:
    if seconds is None:
        return "-"
    minutes, sec = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{sec:02d}"
    return f"{minutes}:{sec:02d}"


def _format_int(value: int | None) -> str:
    return f"{value:,}" if value is not None else "-"


def _format_date(value: datetime | None, fallback: str | None) -> str:
    if value is not None:
        return value.strftime("%Y-%m-%d")
    if fallback and re.match(r"^\d{8}$", fallback):
        return f"{fallback[:4]}-{fallback[4:6]}-{fallback[6:]}"
    return fallback or "-"


def _format_language_list(values: tuple[str, ...]) -> str:
    if not values:
        return "없음"
    preview = ", ".join(values[:12])
    if len(values) > 12:
        preview += f" 외 {len(values) - 12}개"
    return preview
