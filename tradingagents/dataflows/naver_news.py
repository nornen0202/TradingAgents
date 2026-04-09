from __future__ import annotations

import html
import re
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

import requests

from .api_keys import get_api_key
from .config import get_config
from .news_models import NewsItem, dedupe_news_items, filter_news_items_by_date, format_news_items_report
from .vendor_exceptions import VendorConfigurationError, VendorMalformedResponseError, VendorTransientError


_NAVER_NEWS_ENDPOINT = "https://openapi.naver.com/v1/search/news.json"


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", html.unescape(text or "")).strip()


def _get_headers() -> dict[str, str]:
    client_id = get_api_key("NAVER_CLIENT_ID")
    client_secret = get_api_key("NAVER_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise VendorConfigurationError("Naver News credentials are not configured.")
    return {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
    }


def validate_naver_credentials(*, sample_query: str = "삼성전자") -> None:
    try:
        response = requests.get(
            _NAVER_NEWS_ENDPOINT,
            headers=_get_headers(),
            params={"query": sample_query, "display": 1, "sort": "date"},
            timeout=float(get_config().get("vendor_timeout", 15)),
        )
        if response.status_code in {401, 403}:
            raise VendorConfigurationError(
                f"Naver News credentials were rejected ({response.status_code} {response.reason})."
            )
        response.raise_for_status()
    except VendorConfigurationError:
        raise
    except requests.RequestException as exc:
        raise VendorTransientError(f"Naver News validation request failed: {exc}") from exc


def normalize_naver_article(article: dict, *, fallback_symbol: str) -> NewsItem:
    published_at = None
    if article.get("pubDate"):
        try:
            published_at = parsedate_to_datetime(article["pubDate"])
        except (TypeError, ValueError, IndexError):
            published_at = None
    return NewsItem(
        title=_strip_html(article.get("title", "No title")),
        source="Naver News",
        published_at=published_at,
        language="ko",
        country="KR",
        symbols=[fallback_symbol.upper()],
        topic_tags=[],
        sentiment=None,
        relevance=None,
        reliability=None,
        url=article.get("originallink") or article.get("link") or "",
        summary=_strip_html(article.get("description", "")),
        raw_vendor="naver",
    )


def fetch_company_news_naver(symbol: str, start_date: str, end_date: str, display: int = 20) -> list[NewsItem]:
    from tradingagents.agents.utils.instrument_resolver import resolve_instrument

    profile = resolve_instrument(symbol)
    query_candidates = [symbol]
    if profile.country == "KR":
        query_candidates = [
            profile.display_name,
            profile.display_name_kr or "",
            profile.display_name_en or "",
            profile.krx_code or "",
            profile.yahoo_symbol or "",
            *list(profile.aliases or ()),
        ]

    unique_queries = [q for q in dict.fromkeys(item.strip() for item in query_candidates if item and item.strip())]
    items: list[dict] = []
    for query in unique_queries[:5]:
        try:
            response = requests.get(
                _NAVER_NEWS_ENDPOINT,
                headers=_get_headers(),
                params={"query": query, "display": display, "sort": "date"},
                timeout=float(get_config().get("vendor_timeout", 15)),
            )
            if response.status_code in {401, 403}:
                raise VendorConfigurationError(
                    f"Naver News credentials were rejected ({response.status_code} {response.reason})."
                )
            response.raise_for_status()
        except VendorConfigurationError:
            raise
        except requests.RequestException as exc:
            raise VendorTransientError(f"Naver News request failed: {exc}") from exc
        payload = response.json()
        query_items = payload.get("items")
        if not isinstance(query_items, list):
            raise VendorMalformedResponseError("Naver News payload did not include an items list.")
        items.extend(query_items)

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
    normalized = dedupe_news_items(
        [normalize_naver_article(article, fallback_symbol=profile.primary_symbol) for article in items]
    )
    return filter_news_items_by_date(normalized, start_date=start_dt, end_date=end_dt)


def get_company_news_naver(symbol: str, start_date: str, end_date: str) -> str:
    items = fetch_company_news_naver(symbol, start_date, end_date)
    if not items:
        return f"No news found for {symbol} between {start_date} and {end_date}"
    return format_news_items_report(
        f"{symbol} Company News, from {start_date} to {end_date}",
        items,
        max_items=15,
    )


def get_social_sentiment_naver(symbol: str, start_date: str, end_date: str) -> str:
    items = fetch_company_news_naver(symbol, start_date, end_date, display=10)
    if not items:
        return (
            f"Dedicated social provider unavailable; Naver company-news sentiment was unavailable for {symbol} "
            f"between {start_date} and {end_date}."
        )
    lines = [
        f"Dedicated social provider unavailable; using Korean news-derived public narrative for {symbol} from {start_date} to {end_date}.",
        "",
    ]
    for item in items[:10]:
        stamp = item.published_at.strftime("%Y-%m-%d") if item.published_at else "undated"
        lines.append(f"- {stamp}: {item.title}")
        if item.summary:
            lines.append(f"  Narrative: {item.summary}")
    return "\n".join(lines)
