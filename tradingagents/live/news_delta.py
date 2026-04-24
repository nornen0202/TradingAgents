from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any

from tradingagents.dataflows.interface import route_to_vendor


_NEWS_REASON_PATTERNS: tuple[tuple[str, str], ...] = (
    ("earnings_estimate_upgraded", r"\b(upgrade|upgraded|raised guidance|estimate(?:s)? raised|target price raised)\b"),
    ("earnings_estimate_downgraded", r"\b(downgrade|downgraded|cut guidance|estimate(?:s)? cut|target price lowered)\b"),
    ("new_contract", r"\b(contract|order win|supply deal|partnership|agreement)\b"),
    ("sector_rotation", r"\b(sector rotation|rotation into|rotation out of)\b"),
    ("regulatory_overhang", r"\b(investigation|probe|regulatory|lawsuit|fine)\b"),
)


def build_news_delta(
    *,
    ticker: str,
    market: str,
    as_of: str | None,
    analysis_payload: dict[str, Any] | None = None,
) -> list[str]:
    analysis_payload = analysis_payload or {}
    tags = _tags_from_analysis_payload(analysis_payload)

    fetched = _fetch_latest_news_text(
        ticker=ticker,
        market=market,
        as_of=as_of,
    )
    if fetched:
        tags.extend(_extract_reason_tags(fetched))

    deduped: list[str] = []
    for tag in tags:
        normalized = str(tag).strip()
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return deduped


def _tags_from_analysis_payload(analysis_payload: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    decision_blob = str(analysis_payload.get("decision") or "")
    tags.extend(_extract_reason_tags(decision_blob))
    return tags


def _fetch_latest_news_text(*, ticker: str, market: str, as_of: str | None) -> str:
    end_dt = _safe_parse_datetime(as_of) or datetime.now()
    start_dt = end_dt - timedelta(days=3)
    try:
        result = route_to_vendor(
            "get_company_news",
            ticker,
            start_dt.date().isoformat(),
            end_dt.date().isoformat(),
        )
    except Exception:
        return ""
    return str(result or "")


def _extract_reason_tags(text: str) -> list[str]:
    normalized = str(text or "").lower()
    tags = [
        reason_code
        for reason_code, pattern in _NEWS_REASON_PATTERNS
        if re.search(pattern, normalized)
    ]
    return tags


def _safe_parse_datetime(value: str | None) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None
