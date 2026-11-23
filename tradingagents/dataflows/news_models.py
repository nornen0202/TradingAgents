from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable

from .config import get_config
from .integrity import parse_analysis_cutoff
from .vendor_exceptions import VendorInputError


@dataclass(frozen=True)
class NewsItem:
    title: str
    source: str
    published_at: datetime | None
    language: str | None = None
    country: str | None = None
    symbols: list[str] = field(default_factory=list)
    topic_tags: list[str] = field(default_factory=list)
    sentiment: float | None = None
    relevance: float | None = None
    reliability: float | None = None
    url: str = ""
    summary: str = ""
    raw_vendor: str = ""


@dataclass(frozen=True)
class DisclosureItem:
    title: str
    source: str
    published_at: datetime | None
    url: str
    summary: str
    symbol: str
    raw_vendor: str


def normalize_datetime(value: datetime | str | int | float | None) -> datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(value, tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
            return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed
        except ValueError:
            try:
                return datetime.strptime(text, "%Y%m%dT%H%M").replace(tzinfo=timezone.utc)
            except ValueError:
                pass
            try:
                return datetime.strptime(text, "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)
            except ValueError:
                pass
            try:
                return datetime.fromtimestamp(float(text), tz=timezone.utc)
            except (OverflowError, OSError, ValueError):
                return None
    return None


def dedupe_news_items(items: Iterable[NewsItem]) -> list[NewsItem]:
    deduped: list[NewsItem] = []
    seen: set[str] = set()
    for item in items:
        identity = build_news_identity(item)
        if identity in seen:
            continue
        seen.add(identity)
        deduped.append(item)
    return deduped


def build_news_identity(item: NewsItem) -> str:
    if item.url:
        return item.url.strip()
    stamp = item.published_at.isoformat() if item.published_at else ""
    return f"{item.source.strip()}::{item.title.strip()}::{stamp}"


def filter_news_items_by_date(
    items: Iterable[NewsItem],
    *,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    market_timezone: str = "UTC",
) -> list[NewsItem]:
    start_date = normalize_datetime(start_date)
    end_date = normalize_datetime(end_date)
    cutoff = datetime.now(timezone.utc)
    configured_cutoff = get_config().get("analysis_as_of")
    if configured_cutoff:
        try:
            cutoff = min(cutoff, parse_analysis_cutoff(configured_cutoff, market_timezone))
        except (TypeError, ValueError) as exc:
            raise VendorInputError("Invalid news analysis_as_of cutoff") from exc
    filtered: list[NewsItem] = []
    for item in items:
        published_at = item.published_at
        if published_at is None or published_at.tzinfo is None or published_at.utcoffset() is None:
            continue
        published = published_at.astimezone(timezone.utc)
        if published > cutoff:
            continue
        if start_date and published < start_date:
            continue
        if end_date and published >= end_date:
            continue
        filtered.append(item)
    return filtered


def format_news_items_report(
    heading: str,
    items: Iterable[NewsItem],
    *,
    max_items: int = 10,
) -> str:
    selected = list(items)[:max_items]
    if not selected:
        return f"No news found for {heading}"

    lines = [f"## {heading}", ""]
    for item in selected:
        date_prefix = ""
        if item.published_at:
            date_prefix = f"[{item.published_at.strftime('%Y-%m-%d')}] "
        lines.append(f"### {date_prefix}{item.title} (source: {item.source})")
        if item.summary:
            lines.append(item.summary)
        if item.sentiment is not None:
            lines.append(f"Sentiment score: {item.sentiment:.2f}")
        if item.url:
            lines.append(f"Link: {item.url}")
        lines.append("")
    return "\n".join(lines).strip()


def format_disclosure_items_report(
    heading: str,
    items: Iterable[DisclosureItem],
    *,
    max_items: int = 10,
) -> str:
    selected = list(items)[:max_items]
    if not selected:
        return f"No disclosures found for {heading}"

    lines = [f"## {heading}", ""]
    for item in selected:
        date_prefix = ""
        if item.published_at:
            date_prefix = f"[{item.published_at.strftime('%Y-%m-%d')}] "
        lines.append(f"### {date_prefix}{item.title} (source: {item.source})")
        if item.summary:
            lines.append(item.summary)
        if item.url:
            lines.append(f"Link: {item.url}")
        lines.append("")
    return "\n".join(lines).strip()
