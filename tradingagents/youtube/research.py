from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
import json
import os
import re
from typing import Any, Callable, Mapping
from urllib.parse import parse_qs, unquote, urlparse

import requests
import yfinance as yf

from tradingagents.dataflows.api_keys import get_api_key
from tradingagents.youtube.verification_status import UNVERIFIED, VERIFIED


ResearchSearchProvider = Callable[[str, int, datetime], list[dict[str, Any]]]
UrlFetcher = Callable[[str, int], dict[str, Any] | None]

_NAVER_NEWS_ENDPOINT = "https://openapi.naver.com/v1/search/news.json"
_DUCKDUCKGO_HTML_ENDPOINT = "https://duckduckgo.com/html/"
_USER_AGENT = (
    "Mozilla/5.0 (compatible; TradingAgentsResearch/1.0; "
    "+https://github.com/nornen0202/TradingAgents)"
)


@dataclass(frozen=True)
class EvidenceItem:
    evidence_id: str
    claim_id: str
    query: str
    source_type: str
    source_tier: str
    title: str
    source_url: str
    publisher: str
    published_at: str | None
    fetched_at: str
    excerpt: str
    relevance: str = "candidate"
    status: str = VERIFIED
    error: str = ""


def collect_research_evidence(
    research_plan: Mapping[str, Any],
    *,
    generated_at: datetime,
    max_queries: int,
    max_evidence_items: int,
    max_evidence_per_claim: int,
    fetch_web_pages: bool,
    max_web_pages: int,
    evidence_relevance_gate_enabled: bool = True,
    min_evidence_relevance_score: float = 0.12,
    search_provider: ResearchSearchProvider | None = None,
    url_fetcher: UrlFetcher | None = None,
) -> dict[str, Any]:
    if generated_at.tzinfo is None:
        generated_at = generated_at.replace(tzinfo=timezone.utc)
    fetched_at = datetime.now(timezone.utc).isoformat()
    queries = _planned_queries(research_plan, max_queries=max_queries)
    search_provider = search_provider or default_search_provider
    url_fetcher = url_fetcher or fetch_url_excerpt
    evidence: list[EvidenceItem] = []
    seen_urls: set[str] = set()
    fetched_pages = 0
    errors: list[str] = []
    claim_context = _claim_context_by_id(research_plan)

    for query_item in queries:
        if len(evidence) >= max_evidence_items:
            break
        query = str(query_item.get("query") or "").strip()
        claim_id = str(query_item.get("claim_id") or "").strip() or "GLOBAL"
        if not query:
            continue
        try:
            results = search_provider(query, max_evidence_per_claim, generated_at)
        except Exception as exc:
            errors.append(f"{query}: {exc}")
            continue
        per_claim_count = 0
        for result in results:
            if len(evidence) >= max_evidence_items or per_claim_count >= max_evidence_per_claim:
                break
            url = str(result.get("source_url") or result.get("url") or "").strip()
            if url and url in seen_urls:
                continue
            title = _clean_text(result.get("title") or result.get("name") or query, 180)
            excerpt = _clean_text(result.get("excerpt") or result.get("summary") or result.get("snippet") or "", 700)
            publisher = _clean_text(result.get("publisher") or result.get("source") or _publisher_from_url(url), 120)
            published_at = _iso_or_none(result.get("published_at"))
            source_type = str(result.get("source_type") or result.get("source") or "web_search")
            source_tier = str(result.get("source_tier") or _source_tier(url, publisher, source_type))

            if fetch_web_pages and url and fetched_pages < max_web_pages:
                fetched = url_fetcher(url, 900)
                fetched_pages += 1
                if fetched:
                    fetched_excerpt = _clean_text(fetched.get("excerpt") or "", 900)
                    if fetched_excerpt and fetched_excerpt not in excerpt:
                        excerpt = _clean_text(f"{excerpt} {fetched_excerpt}", 900)
                    publisher = publisher or _clean_text(fetched.get("publisher") or "", 120)
                    source_type = str(fetched.get("source_type") or source_type)
                    source_tier = str(fetched.get("source_tier") or source_tier)

            relevance_score, relevance_reason = _evidence_relevance_score(
                query=query,
                claim=claim_context.get(claim_id),
                title=title,
                excerpt=excerpt,
                publisher=publisher,
                source_url=url,
            )
            if (
                evidence_relevance_gate_enabled
                and claim_id != "GLOBAL"
                and relevance_score < min_evidence_relevance_score
            ):
                errors.append(f"low_relevance_skipped:{claim_id}:{relevance_score:.2f}:{title[:80]}")
                continue
            if url:
                seen_urls.add(url)
            evidence.append(
                EvidenceItem(
                    evidence_id=f"E{len(evidence) + 1}",
                    claim_id=claim_id,
                    query=query,
                    source_type=source_type,
                    source_tier=source_tier,
                    title=title,
                    source_url=url,
                    publisher=publisher,
                    published_at=published_at,
                    fetched_at=fetched_at,
                    excerpt=excerpt,
                    relevance=f"score:{relevance_score:.2f};{relevance_reason}",
                    status=VERIFIED if (url or excerpt) else UNVERIFIED,
                )
            )
            per_claim_count += 1

    return {
        "version": 1,
        "status": VERIFIED if evidence else UNVERIFIED,
        "generated_at": fetched_at,
        "query_count": len(queries),
        "evidence_count": len(evidence),
        "items": [asdict(item) for item in evidence],
        "errors": errors[:10],
        "source_policy": {
            "raw_transcript_included": False,
            "excerpts_only": True,
            "evidence_relevance_gate_enabled": evidence_relevance_gate_enabled,
            "min_evidence_relevance_score": min_evidence_relevance_score,
            "search_providers": ["naver_news", "yfinance_search", "duckduckgo_html"],
        },
    }


def default_search_provider(query: str, limit: int, generated_at: datetime) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for provider in (_search_naver_news, _search_yfinance_news, _search_duckduckgo_html):
        remaining = max(0, limit - len(results))
        if remaining <= 0:
            break
        try:
            results.extend(provider(query, remaining, generated_at))
        except Exception:
            continue
    return _dedupe_result_items(results)[:limit]


def fetch_url_excerpt(url: str, limit: int = 900) -> dict[str, Any] | None:
    parsed = urlparse(str(url or ""))
    if parsed.scheme not in {"http", "https"}:
        return None
    try:
        response = requests.get(
            url,
            headers={"User-Agent": _USER_AGENT, "Accept-Language": "ko,en;q=0.8"},
            timeout=float(os.getenv("TRADINGAGENTS_YOUTUBE_RESEARCH_TIMEOUT", "12")),
        )
        response.raise_for_status()
    except requests.RequestException:
        return None
    content_type = response.headers.get("content-type", "")
    if "text" not in content_type and "html" not in content_type and "json" not in content_type:
        return None
    text = response.text
    if "html" in content_type or "<html" in text[:1000].lower():
        text = _html_to_text(text)
    else:
        try:
            payload = response.json()
            text = json.dumps(payload, ensure_ascii=False)
        except ValueError:
            pass
    return {
        "source_type": "web_page",
        "source_tier": _source_tier(url, "", "web_page"),
        "publisher": _publisher_from_url(url),
        "excerpt": _clean_text(text, limit),
    }


def fallback_research_plan(
    claims: Mapping[str, Any],
    *,
    video_title: str,
    max_queries: int,
) -> dict[str, Any]:
    plan_claims: list[dict[str, Any]] = []
    query_budget = max_queries
    for entity_index, entity in enumerate(claims.get("entities") or [], 1):
        if not isinstance(entity, Mapping):
            continue
        claim_texts = [str(item).strip() for item in (entity.get("claims") or []) if str(item).strip()]
        claim_texts += [str(item).strip() for item in (entity.get("numeric_claims") or []) if str(item).strip()]
        name = str(entity.get("name") or entity.get("ticker") or "").strip()
        ticker = str(entity.get("ticker") or "").strip()
        for claim_index, claim_text in enumerate(claim_texts[:3], 1):
            claim_id = f"C{entity_index}_{claim_index}"
            query_terms = " ".join(part for part in (name, ticker, claim_text[:80]) if part).strip()
            queries = []
            if query_budget > 0 and query_terms:
                queries.append(
                    {
                        "query": query_terms,
                        "language": "ko",
                        "source_priority": ["official", "news", "market"],
                        "reason": "claim verification fallback query",
                    }
                )
                query_budget -= 1
            plan_claims.append(
                {
                    "claim_id": claim_id,
                    "entity": name or ticker,
                    "ticker": ticker,
                    "claim_text": claim_text,
                    "claim_type": _infer_claim_type(claim_text),
                    "time_window": "최근 7일",
                    "queries": queries,
                    "required_evidence": ["news", "market_data"],
                    "asr_suspect_terms": [],
                }
            )
            if query_budget <= 0:
                break
        if query_budget <= 0:
            break
    if not plan_claims and video_title and max_queries > 0:
        plan_claims.append(
            {
                "claim_id": "C1",
                "entity": "",
                "ticker": "",
                "claim_text": video_title,
                "claim_type": "video_topic",
                "time_window": "최근 7일",
                "queries": [{"query": video_title, "language": "ko", "source_priority": ["news"], "reason": "video topic"}],
                "required_evidence": ["news"],
                "asr_suspect_terms": [],
            }
        )
    return {
        "version": 1,
        "status": "fallback",
        "claims": plan_claims,
        "global_queries": [],
        "closed_source_claims": [],
        "asr_suspect_terms": [],
    }


def public_evidence_summary(evidence: Mapping[str, Any], *, per_claim_limit: int = 2) -> list[dict[str, Any]]:
    by_claim: dict[str, int] = {}
    public_items: list[dict[str, Any]] = []
    for item in evidence.get("items") or []:
        if not isinstance(item, Mapping):
            continue
        claim_id = str(item.get("claim_id") or "GLOBAL")
        if by_claim.get(claim_id, 0) >= per_claim_limit:
            continue
        by_claim[claim_id] = by_claim.get(claim_id, 0) + 1
        public_items.append(
            {
                "evidence_id": str(item.get("evidence_id") or "") or None,
                "claim_id": claim_id,
                "title": _clean_text(item.get("title") or "", 160),
                "source_url": str(item.get("source_url") or ""),
                "publisher": _clean_text(item.get("publisher") or "", 100),
                "published_at": item.get("published_at"),
                "source_tier": item.get("source_tier"),
                "excerpt": _clean_text(item.get("excerpt") or "", 260),
            }
        )
    return public_items


_RELEVANCE_TOKEN_RE = re.compile(r"[A-Za-z0-9가-힣][A-Za-z0-9가-힣._%-]{1,}")
_RELEVANCE_STOPWORDS = {
    "관련",
    "기사",
    "뉴스",
    "시장",
    "투자",
    "증시",
    "경제",
    "분석",
    "전망",
    "최근",
    "today",
    "market",
    "markets",
    "stock",
    "stocks",
    "news",
    "finance",
    "analysis",
    "investing",
    "update",
}


def _claim_context_by_id(plan: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    context: dict[str, Mapping[str, Any]] = {}
    for index, claim in enumerate(plan.get("claims") or [], 1):
        if not isinstance(claim, Mapping):
            continue
        claim_id = str(claim.get("claim_id") or f"C{index}")
        context[claim_id] = claim
    return context


def _evidence_relevance_score(
    *,
    query: str,
    claim: Mapping[str, Any] | None,
    title: str,
    excerpt: str,
    publisher: str,
    source_url: str,
) -> tuple[float, str]:
    claim = claim or {}
    claim_text = " ".join(
        str(part or "")
        for part in (
            claim.get("claim_text"),
            claim.get("entity"),
            claim.get("ticker"),
            query,
        )
    )
    evidence_text = " ".join(str(part or "") for part in (title, excerpt, publisher, source_url))
    claim_tokens = _relevance_tokens(claim_text)
    evidence_tokens = _relevance_tokens(evidence_text)
    if not claim_tokens:
        return 1.0, "no_claim_tokens"
    overlap = claim_tokens & evidence_tokens
    denominator = max(4, min(len(claim_tokens), 12))
    score = min(1.0, len(overlap) / denominator)

    numbers = _numeric_tokens(claim_text)
    if numbers:
        number_overlap = numbers & _numeric_tokens(evidence_text)
        if number_overlap:
            score = min(1.0, score + 0.20)

    ticker = str(claim.get("ticker") or "").strip().lower()
    entity = str(claim.get("entity") or "").strip().lower()
    haystack = evidence_text.lower()
    if ticker and ticker in haystack:
        score = min(1.0, score + 0.35)
    if entity and len(entity) >= 2 and entity in haystack:
        score = min(1.0, score + 0.25)

    if overlap:
        return score, "overlap:" + ",".join(sorted(overlap)[:8])
    return score, "no_overlap"


def _relevance_tokens(text: str) -> set[str]:
    tokens = set()
    for match in _RELEVANCE_TOKEN_RE.findall(str(text or "").lower()):
        token = match.strip("._%-")
        if len(token) < 2 or token in _RELEVANCE_STOPWORDS:
            continue
        tokens.add(token)
    return tokens


def _numeric_tokens(text: str) -> set[str]:
    return {match.group(0) for match in re.finditer(r"\d+(?:\.\d+)?%?", str(text or ""))}


def _planned_queries(plan: Mapping[str, Any], *, max_queries: int) -> list[dict[str, str]]:
    queries: list[dict[str, str]] = []
    for claim in plan.get("claims") or []:
        if not isinstance(claim, Mapping):
            continue
        claim_id = str(claim.get("claim_id") or f"C{len(queries) + 1}")
        for query_item in claim.get("queries") or []:
            if isinstance(query_item, Mapping):
                query = str(query_item.get("query") or "").strip()
            else:
                query = str(query_item or "").strip()
            if query:
                queries.append({"claim_id": claim_id, "query": query})
            if len(queries) >= max_queries:
                return queries
    for query_item in plan.get("global_queries") or []:
        if len(queries) >= max_queries:
            break
        if isinstance(query_item, Mapping):
            query = str(query_item.get("query") or "").strip()
        else:
            query = str(query_item or "").strip()
        if query:
            queries.append({"claim_id": "GLOBAL", "query": query})
    return queries[:max_queries]


def _search_naver_news(query: str, limit: int, generated_at: datetime) -> list[dict[str, Any]]:
    client_id = get_api_key("NAVER_CLIENT_ID")
    client_secret = get_api_key("NAVER_CLIENT_SECRET")
    if not client_id or not client_secret:
        return []
    try:
        response = requests.get(
            _NAVER_NEWS_ENDPOINT,
            headers={"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret},
            params={"query": query, "display": min(max(1, limit), 10), "sort": "date"},
            timeout=float(os.getenv("TRADINGAGENTS_YOUTUBE_RESEARCH_TIMEOUT", "12")),
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError):
        return []
    items = payload.get("items") if isinstance(payload, Mapping) else None
    if not isinstance(items, list):
        return []
    results = []
    for article in items:
        if not isinstance(article, Mapping):
            continue
        results.append(
            {
                "title": _strip_html(str(article.get("title") or "")),
                "excerpt": _strip_html(str(article.get("description") or "")),
                "source_url": str(article.get("originallink") or article.get("link") or ""),
                "publisher": "Naver News",
                "published_at": str(article.get("pubDate") or ""),
                "source_type": "naver_news",
                "source_tier": "news",
            }
        )
    return results


def _search_yfinance_news(query: str, limit: int, generated_at: datetime) -> list[dict[str, Any]]:
    try:
        search = yf.Search(query=query, news_count=min(max(1, limit), 10), enable_fuzzy_query=True)
        items = getattr(search, "news", None) or []
    except Exception:
        return []
    results = []
    for item in items[:limit]:
        if not isinstance(item, Mapping):
            continue
        content = item.get("content") if isinstance(item.get("content"), Mapping) else {}
        provider = content.get("provider") if isinstance(content.get("provider"), Mapping) else {}
        url_obj = content.get("canonicalUrl") or content.get("clickThroughUrl") or {}
        if not isinstance(url_obj, Mapping):
            url_obj = {}
        title = content.get("title") or item.get("title") or ""
        summary = content.get("summary") or item.get("summary") or ""
        published_at = content.get("pubDate") or item.get("providerPublishTime")
        results.append(
            {
                "title": str(title),
                "excerpt": str(summary),
                "source_url": str(url_obj.get("url") or item.get("link") or ""),
                "publisher": str(provider.get("displayName") or item.get("publisher") or "Yahoo Finance"),
                "published_at": _iso_or_none(published_at),
                "source_type": "yfinance_search",
                "source_tier": "news",
            }
        )
    return results


def _search_duckduckgo_html(query: str, limit: int, generated_at: datetime) -> list[dict[str, Any]]:
    try:
        response = requests.get(
            _DUCKDUCKGO_HTML_ENDPOINT,
            params={"q": query, "kl": "kr-kr"},
            headers={"User-Agent": _USER_AGENT, "Accept-Language": "ko,en;q=0.8"},
            timeout=float(os.getenv("TRADINGAGENTS_YOUTUBE_RESEARCH_TIMEOUT", "12")),
        )
        response.raise_for_status()
    except requests.RequestException:
        return []
    parser = _DuckDuckGoParser()
    parser.feed(response.text)
    results = []
    for item in parser.results[:limit]:
        url = _unwrap_duckduckgo_url(item.get("url") or "")
        results.append(
            {
                "title": item.get("title") or "",
                "excerpt": item.get("snippet") or "",
                "source_url": url,
                "publisher": _publisher_from_url(url),
                "published_at": None,
                "source_type": "duckduckgo_html",
                "source_tier": _source_tier(url, "", "duckduckgo_html"),
            }
        )
    return results


class _DuckDuckGoParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.results: list[dict[str, str]] = []
        self._in_link = False
        self._in_snippet = False
        self._current: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {key: value or "" for key, value in attrs}
        class_name = attr.get("class", "")
        if tag == "a" and "result__a" in class_name:
            self._in_link = True
            self._current = {"url": attr.get("href", ""), "title": "", "snippet": ""}
        elif tag in {"a", "div"} and "result__snippet" in class_name:
            self._in_snippet = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._in_link:
            self._in_link = False
            if self._current.get("title") and self._current not in self.results:
                self.results.append(dict(self._current))
        if self._in_snippet and tag in {"a", "div"}:
            self._in_snippet = False

    def handle_data(self, data: str) -> None:
        if self._in_link:
            self._current["title"] = _clean_text(self._current.get("title", "") + " " + data, 200)
        elif self._in_snippet and self.results:
            self.results[-1]["snippet"] = _clean_text(self.results[-1].get("snippet", "") + " " + data, 400)


def _html_to_text(html: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return unescape(text)


def _strip_html(text: str) -> str:
    return _clean_text(re.sub(r"<[^>]+>", "", unescape(text or "")), 400)


def _clean_text(value: Any, limit: int) -> str:
    text = re.sub(r"\s+", " ", unescape(str(value or ""))).strip()
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)].rstrip() + "..."


def _iso_or_none(value: Any) -> str | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(float(value), tz=timezone.utc).isoformat()
        except (OSError, OverflowError, ValueError):
            return None
    text = str(value).strip()
    if not text:
        return None
    try:
        from email.utils import parsedate_to_datetime

        parsed = parsedate_to_datetime(text)
        return parsed.isoformat()
    except Exception:
        pass
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).isoformat()
    except ValueError:
        return text[:80]


def _publisher_from_url(url: str) -> str:
    host = urlparse(str(url or "")).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def _source_tier(url: str, publisher: str, source_type: str) -> str:
    haystack = f"{url} {publisher} {source_type}".lower()
    official_markers = (
        "dart.fss.or.kr",
        "kind.krx.co.kr",
        "krx.co.kr",
        ".go.kr",
        "assembly.go.kr",
        "sec.gov",
        "investor.",
        "ir.",
    )
    if any(marker in haystack for marker in official_markers):
        return "official"
    if any(marker in haystack for marker in ("yfinance", "finance.yahoo", "naver")):
        return "market_or_news"
    if "news" in source_type.lower():
        return "news"
    return "web"


def _unwrap_duckduckgo_url(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower().rstrip(".")
    if (
        parsed.scheme.lower() in {"http", "https"}
        and host in {"duckduckgo.com", "www.duckduckgo.com"}
        and parsed.path.endswith("/l/")
    ):
        redirect = parse_qs(parsed.query).get("uddg")
        if redirect:
            return unquote(redirect[0])
    return url


def _dedupe_result_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in items:
        url = str(item.get("source_url") or item.get("url") or "").strip()
        title = str(item.get("title") or "").strip().lower()
        key = url or title
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _infer_claim_type(text: str) -> str:
    lowered = text.lower()
    if any(token in text for token in ("정부", "정책", "국회", "토론회", "배당금")):
        return "policy"
    if any(token in lowered for token in ("kospi", "코스피", "지수", "환율", "유가")):
        return "market"
    if re.search(r"\d", text):
        return "numeric"
    return "company_or_macro"
