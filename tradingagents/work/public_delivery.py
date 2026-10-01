"""Read-only, nonce-discovered, commit-pinned public research input gate.

This verifies inputs, not investment merit or arbitrary cloud-chat output.
No credentials, trades, schedule changes, or writes to remote services.
"""
from __future__ import annotations

import hashlib
import json
import re
import uuid
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen

from .freshness import aware_datetime

REPO = "nornen0202/TradingAgents"
REF = f"https://api.github.com/repos/{REPO}/git/ref/heads/public-context"
RAW = f"https://raw.githubusercontent.com/{REPO}"
MAX_AGE = timedelta(minutes=30)


class PublicDeliveryError(ValueError):
    pass


def fetch(url: str) -> bytes:
    request = Request(url, headers={"Cache-Control": "no-cache, no-store", "Pragma": "no-cache",
                                   "User-Agent": "TradingAgents-Verified-Input"})
    with urlopen(request, timeout=25) as response:
        data = response.read(600_001)
    if len(data) > 600_000:
        raise PublicDeliveryError("Response exceeds public input budget")
    return data


def validate_input(payload: dict, *, market: str, now: datetime) -> list[str]:
    """All executable-account gates fail closed; reference research may continue."""
    if now.tzinfo is None:
        raise PublicDeliveryError("Verification time must be timezone-aware")
    if not isinstance(payload, dict):
        return ["PAYLOAD_INVALID"]
    for key in ("freshness_receipt", "account"):
        if not isinstance(payload.get(key), dict):
            return ["PAYLOAD_INVALID"]
    account = payload["account"]
    if (not isinstance(account.get("summary"), dict)
            or not isinstance(account.get("positions"), list)
            or not isinstance(payload.get("rows"), list)):
        return ["PAYLOAD_INVALID"]
    reasons = []
    if payload.get("schema") != "tradingagents.ai-context/v1" or payload.get("market") != market:
        reasons.append("SCHEMA_OR_MARKET_MISMATCH")
    def clock(value, label, budget=MAX_AGE):
        observed = aware_datetime(value)
        if observed is None or observed > now or now - observed >= budget:
            reasons.append(label)
        return observed
    clock(payload.get("generated_at"), "PUBLICATION_EXPIRED_OR_INVALID")
    freshness = payload.get("freshness_receipt") or {}
    clock(freshness.get("analysis_completed_at"), "RESEARCH_EXPIRED_OR_INVALID", timedelta(hours=36))
    if freshness.get("analysis_lineage_status") != "RESOLVED":
        reasons.append("RESEARCH_LINEAGE_UNVERIFIED")
    oldest = clock(freshness.get("market_data_oldest_at"), "QUOTE_EXPIRED_OR_INVALID")
    latest = clock(freshness.get("market_data_latest_at"), "QUOTE_EXPIRED_OR_INVALID")
    if oldest and latest and oldest > latest:
        reasons.append("QUOTE_CLOCK_ORDER_INVALID")
    account = payload.get("account") or {}
    clock(account.get("as_of"), "ACCOUNT_EXPIRED_OR_INVALID")
    if account.get("status") != "available" or account.get("snapshot_health") != "VALID":
        reasons.append("ACCOUNT_UNVERIFIED")
    for key in ("available_cash_krw", "total_equity_krw"):
        value = (account.get("summary") or {}).get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not (0 <= value < float("inf")):
            reasons.append("ACCOUNT_CASH_OR_EQUITY_UNVERIFIED")
    positions = account.get("positions") or []
    identities = [p.get("ticker") for p in positions if isinstance(p, dict)]
    if (len(identities) != len(positions) or any(not t for t in identities)
            or len(set(identities)) != len(identities)
            or (account.get("summary") or {}).get("position_count") != len(positions)):
        reasons.append("ACCOUNT_COVERAGE_INVALID")
    for position in positions:
        for key in ("quantity", "sellable_quantity"):
            value = position.get(key) if isinstance(position, dict) else None
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not (0 <= value < float("inf")):
                reasons.append("ACCOUNT_QUANTITY_INVALID")
    rows = payload.get("rows") or []
    row_tickers = [r.get("ticker") for r in rows if isinstance(r, dict)]
    if len(row_tickers) != len(set(row_tickers)) or not set(identities).issubset(row_tickers):
        reasons.append("HOLDING_ROWS_MISSING_OR_DUPLICATE")
    for row in rows:
        if not isinstance(row, dict):
            reasons.append("ROW_INVALID")
            continue
        observed = clock(row.get("market_data_asof"), "ROW_QUOTE_EXPIRED_OR_INVALID")
        quality = row.get("quality_at_build")
        if not isinstance(quality, dict):
            reasons.append("ROW_QUALITY_INVALID")
            quality = {}
        valid_until = aware_datetime(quality.get("row_valid_until"))
        if (observed is None or valid_until is None or valid_until <= now
                or valid_until > observed + MAX_AGE):
            reasons.append("ROW_VALIDITY_EXPIRED_OR_INVALID")
        price = row.get("last_price")
        if isinstance(price, bool) or not isinstance(price, (int, float)) or not 0 < price < float("inf"):
            reasons.append("ROW_PRICE_INVALID")
        # A session VWAP cannot lie outside that same session's high/low.
        # Do not guess which provider/session is wrong; require reconciliation.
        low, high, vwap = (row.get(k) for k in ("day_low", "day_high", "session_vwap"))
        if all(isinstance(v, (int, float)) and not isinstance(v, bool) and 0 < v < float("inf")
               for v in (low, high, vwap)):
            epsilon = max(high, vwap) * 1e-6
            if low > high or vwap < low - epsilon or vwap > high + epsilon:
                reasons.append("ROW_SESSION_RANGE_INCONSISTENT")
        if quality.get("execution_ready") is not True and row.get("strategy_code") == "BUY_NOW":
            reasons.append("ROW_EXECUTION_LABEL_CONFLICT")
    return sorted(set(reasons))


def source_diagnostics(payload: dict, *, now: datetime) -> dict:
    """Non-sensitive clocks and counts, including when personalization is blocked."""
    freshness = payload.get("freshness_receipt")
    freshness = freshness if isinstance(freshness, dict) else {}
    account = payload.get("account")
    account = account if isinstance(account, dict) else {}
    def age(value):
        parsed = aware_datetime(value)
        return (now - parsed).total_seconds() if parsed else None
    positions = account.get("positions")
    rows = payload.get("rows")
    return {
        "age_seconds": {
            "publication": age(payload.get("generated_at")),
            "analysis": age(freshness.get("analysis_completed_at")),
            "oldest_quote": age(freshness.get("market_data_oldest_at")),
            "account": age(account.get("as_of")),
        },
        "holding_count": len(positions) if isinstance(positions, list) else None,
        "row_count": len(rows) if isinstance(rows, list) else None,
        "publication_does_not_refresh_inputs": True,
    }


def parse_discovery(data: bytes) -> dict:
    lines = data.decode("utf-8").splitlines()
    if not lines or lines[0] != "TradingAgents public input discovery v1":
        raise PublicDeliveryError("Unexpected discovery schema")
    values = {}
    for line in lines[1:]:
        if ": " not in line:
            continue
        key, value = line.split(": ", 1)
        if key in values:
            raise PublicDeliveryError("Duplicate discovery key")
        values[key] = value
    if not re.fullmatch(r"[0-9a-f]{40}", values.get("snapshot_commit", "")):
        raise PublicDeliveryError("Invalid discovery snapshot commit")
    return values


def _head(fetcher) -> str:
    value = json.loads(fetcher(f"{REF}?request_id={uuid.uuid4().hex}"))
    if value.get("ref") != "refs/heads/public-context" or (value.get("object") or {}).get("type") != "commit":
        raise PublicDeliveryError("Unexpected public ref")
    sha = value["object"]["sha"]
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise PublicDeliveryError("Invalid immutable commit")
    return sha


def prepare_public_delivery(market: str, *, fetcher=fetch, now: datetime | None = None) -> dict:
    if market not in ("kr", "us"):
        raise PublicDeliveryError("Unsupported market")
    for _ in range(2):
        head = _head(fetcher)
        discovery = parse_discovery(fetcher(f"{RAW}/{head}/discovery.txt"))
        sha = discovery["snapshot_commit"]
        base = f"{RAW}/{sha}"
        for field, path in (("manifest_url", "manifest.json"),
                            (f"{market}_json_url", f"{market}/latest.json"),
                            (f"{market}_txt_url", f"{market}/latest.txt")):
            if discovery.get(field) != f"{base}/{path}":
                raise PublicDeliveryError("Discovery URL is outside the pinned snapshot")
        manifest_bytes = fetcher(f"{base}/manifest.json")
        if (str(len(manifest_bytes)) != discovery.get("manifest_bytes")
                or hashlib.sha256(manifest_bytes).hexdigest() != discovery.get("manifest_sha256")):
            raise PublicDeliveryError("Manifest hash/size mismatch")
        manifest = json.loads(manifest_bytes)
        if manifest.get("schema") != "tradingagents.ai-context/v1":
            raise PublicDeliveryError("Unexpected manifest schema")
        if manifest.get("generated_at") != discovery.get("generated_at"):
            raise PublicDeliveryError("Discovery and manifest generations disagree")
        contents = {}
        for ext in ("json", "txt"):
            path = f"{market}/latest.{ext}"
            data = fetcher(f"{base}/{path}")
            expected = (manifest.get("files") or {}).get(path) or {}
            if len(data) != expected.get("bytes") or hashlib.sha256(data).hexdigest() != expected.get("sha256"):
                raise PublicDeliveryError("Public input hash/size mismatch")
            contents[ext] = data
        if _head(fetcher) != head:
            continue
        payload = json.loads(contents["json"])
        if not isinstance(payload, dict):
            raise PublicDeliveryError("Public input must be an object")
        if payload.get("generated_at") != manifest.get("generated_at"):
            raise PublicDeliveryError("Mixed publication generation")
        checked = now or datetime.now(timezone.utc)
        reasons = validate_input(payload, market=market, now=checked)
        if "PAYLOAD_INVALID" in reasons:
            raise PublicDeliveryError("Invalid public input container types")
        from tradingagents.scheduled.ai_context import render_payload
        if render_payload(payload).encode("utf-8") != contents["txt"]:
            raise PublicDeliveryError("Text and structured inputs disagree")
        return {
            "schema": "tradingagents.verified-public-delivery/v1", "market": market,
            "checked_at": checked.isoformat(), "commit": sha,
            "head_commit": head, "latest_head_checked": True,
            "byte_integrity_verified": True,
            "source_url": f"{base}/{market}/latest.json",
            "text_url": f"{base}/{market}/latest.txt",
            "source_sha256": hashlib.sha256(contents["json"]).hexdigest(),
            "status": "REFERENCE_ONLY" if reasons else "VERIFIED_CURRENT_INPUT",
            "blockers": reasons, "publication_at": payload.get("generated_at"),
            "freshness_receipt": payload.get("freshness_receipt"),
            "account_as_of": (payload.get("account") or {}).get("as_of"),
            "diagnostics": source_diagnostics(payload, now=checked),
            "personalized_input": None if reasons else payload,
            "context_text": None if reasons else contents["txt"].decode("utf-8"),
            "not_order_authorization": True,
        }
    raise PublicDeliveryError("Public head changed twice during verification")
