"""Current company-news sample; historical article revisions are not supplied.

Massive's publication timestamp is not an article-version timestamp. Therefore
this adapter is restricted to windows containing the current UTC day; it must
not backfill an earlier research decision with today's article text.
"""
from datetime import datetime, timezone
import json

import requests

from .api_keys import get_api_key
from .config import get_config
from .integrity import safe_symbol, utc_window
from .vendor_exceptions import VendorConfigurationError, VendorMalformedResponseError, VendorUnavailableError

URL = "https://api.massive.com/v2/reference/news"


def get_company_news_massive(ticker: str, start_date: str, end_date: str) -> str:
    symbol = safe_symbol(ticker)
    api_symbol = symbol.replace("-", ".")
    start, end = utc_window(start_date, end_date)
    began = datetime.now(timezone.utc)
    context = get_config().get("analysis_as_of")
    if context:
        # Exact past instants require versioned content, which this feed lacks.
        if not isinstance(context, str) or len(context) != 10:
            raise VendorUnavailableError("Massive news has no historical article-version timestamps")
        _, context_end = utc_window(context, context)
        end = min(end, context_end)
    if not start <= began < end:
        raise VendorUnavailableError("Massive news cannot verify historical article revisions")
    key = get_api_key("MASSIVE_API_KEY") or get_api_key("POLYGON_API_KEY")
    if not key:
        raise VendorConfigurationError("Massive news credentials are not configured")
    try:
        response = requests.get(URL, headers={"Authorization": f"Bearer {key}"},
                                params={"ticker": api_symbol, "published_utc.gte": start.isoformat(),
                                        "published_utc.lte": began.isoformat(), "limit": 50,
                                        "sort": "published_utc", "order": "desc"},
                                timeout=20, allow_redirects=False)
        if response.status_code != 200:
            raise VendorUnavailableError(f"Massive news unavailable (HTTP {response.status_code})")
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise VendorUnavailableError("Massive news request failed") from exc
    retrieved = datetime.now(timezone.utc)
    if not start <= retrieved < end:
        raise VendorUnavailableError("Massive current news crossed the analysis date boundary")
    rows = payload.get("results") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        raise VendorMalformedResponseError("Massive news response has no article list")
    articles, seen = [], set()
    for row in rows:
        try:
            published = datetime.fromisoformat(row["published_utc"].replace("Z", "+00:00"))
            title, url, source = row["title"], row["article_url"], row["publisher"]["name"]
            symbols = row["tickers"]
            if (published.tzinfo is None or not start <= published <= began or published >= end
                    or not isinstance(symbols, list) or api_symbol not in symbols
                    or not all(isinstance(value, str) and value.strip() for value in (title, url, source))
                    or not url.startswith("https://") or url in seen):
                continue
        except (KeyError, TypeError, ValueError, AttributeError):
            continue
        seen.add(url)
        articles.append({"title": title, "source": source, "url": url,
                         "published_at": published.astimezone(timezone.utc).isoformat(),
                         "symbols": symbols, "summary": str(row.get("description") or "")})
    if not articles:
        raise VendorUnavailableError("Massive news has no verifiable articles in the requested window")
    articles.sort(key=lambda article: article["published_at"], reverse=True)
    return json.dumps({"provider": "massive", "ticker": symbol, "start": start.isoformat(),
                       "end_exclusive": end.isoformat(), "analysis_cutoff": began.isoformat(),
                       "retrieved_at": retrieved.isoformat(), "article_version": "current_snapshot_only",
                       "coverage": "bounded_sample", "truncated": bool(payload.get("next_url")) or len(articles) > 25,
                       "articles": articles[:25]}, ensure_ascii=False)
