"""Dated, symbol-tagged company news from the configured Alpaca connection.

This is a bounded news sample, not proof that no other news exists. Empty or
unverifiable responses fail over; they never certify a news-free interval.
"""
from datetime import datetime, timezone
import json

import requests

from .api_keys import get_api_key
from .config import get_config
from .integrity import safe_symbol, utc_window
from .vendor_exceptions import (
    VendorConfigurationError, VendorInputError, VendorMalformedResponseError,
    VendorUnavailableError,
)

URL = "https://data.alpaca.markets/v1beta1/news"
MAX_PAGES = 5
MAX_ARTICLES = 25


def _aware(value):
    if not isinstance(value, str):
        raise ValueError("Missing timestamp")
    stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if stamp.tzinfo is None:
        raise ValueError("Unknown timestamp timezone")
    return stamp.astimezone(timezone.utc)


def get_company_news_alpaca(ticker: str, start_date: str, end_date: str) -> str:
    symbol = safe_symbol(ticker)
    # Alpaca uses a dot for US class shares, while the research symbol uses '-'.
    api_symbol = symbol.replace("-", ".")
    start, end = utc_window(start_date, end_date)
    cutoff = datetime.now(timezone.utc)
    context_cutoff = get_config().get("analysis_as_of")
    if context_cutoff:
        try:
            if len(str(context_cutoff)) == 10:
                _, context_end = utc_window(str(context_cutoff), str(context_cutoff))
                end = min(end, context_end)
            else:
                cutoff = min(cutoff, _aware(context_cutoff))
        except (TypeError, ValueError) as exc:
            raise VendorInputError("Invalid news analysis_as_of") from exc
    if start >= end or start > cutoff:
        raise VendorInputError("News window is outside the analysis cutoff")
    key, secret = get_api_key("ALPACA_API_KEY_ID"), get_api_key("ALPACA_SECRET_KEY")
    if not key or not secret:
        raise VendorConfigurationError("Alpaca news credentials are not configured")
    headers = {"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": secret}
    params = {"symbols": api_symbol, "start": start.isoformat(),
              "end": min(end, cutoff).isoformat(), "sort": "desc", "limit": 50,
              "include_content": "false"}
    articles, seen, tokens = [], set(), set()
    truncated = False
    for page in range(MAX_PAGES):
        try:
            response = requests.get(URL, headers=headers, params=params, timeout=20, allow_redirects=False)
            if response.status_code != 200:
                raise VendorUnavailableError(f"Alpaca news unavailable (HTTP {response.status_code})")
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise VendorUnavailableError("Alpaca news request failed") from exc
        rows = payload.get("news") if isinstance(payload, dict) else None
        if not isinstance(rows, list):
            raise VendorMalformedResponseError("Alpaca news response has no article list")
        for row in rows:
            try:
                published, updated = _aware(row["created_at"]), _aware(row["updated_at"])
                symbols = row["symbols"]
                title, url, source = row["headline"], row["url"], row["source"]
                if (not start <= published < end or published > cutoff
                        or updated < published or updated >= end or updated > cutoff
                        or not isinstance(symbols, list) or api_symbol not in symbols
                        or not all(isinstance(value, str) and value.strip() for value in (title, url, source))
                        or not url.startswith("https://")):
                    continue
            except (KeyError, TypeError, ValueError):
                continue
            if url in seen:
                continue
            seen.add(url)
            articles.append({"title": title, "source": source, "url": url,
                             "published_at": published.isoformat(), "updated_at": updated.isoformat(),
                             "symbols": symbols, "summary": str(row.get("summary") or "")})
        token = payload.get("next_page_token")
        if len(articles) >= MAX_ARTICLES:
            truncated = bool(token) or len(articles) > MAX_ARTICLES
            break
        if not token:
            break
        if not isinstance(token, str) or token in tokens:
            raise VendorMalformedResponseError("Alpaca news pagination did not advance")
        tokens.add(token)
        params["page_token"] = token
    else:
        truncated = True
    if not articles:
        raise VendorUnavailableError("Alpaca news has no verifiable articles in the requested window")
    articles.sort(key=lambda article: article["published_at"], reverse=True)
    return json.dumps({"provider": "alpaca", "ticker": symbol, "start": start.isoformat(),
                       "end_exclusive": end.isoformat(), "analysis_cutoff": min(end, cutoff).isoformat(),
                       "coverage": "bounded_sample", "truncated": truncated,
                       "articles": articles[:MAX_ARTICLES]}, ensure_ascii=False)
