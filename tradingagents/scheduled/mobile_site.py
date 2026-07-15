from __future__ import annotations

import base64
import hashlib
import html
import json
import os
import secrets
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from tradingagents.work.packet import build_surface_packet


MOBILE_SCHEMA = "tradingagents.mobile-dashboard/v1"
ENCRYPTED_SCHEMA = "tradingagents.mobile-encrypted/v1"
PRIVATE_SCHEMA = "tradingagents.mobile-private/v1"
PRIVATE_AAD = b"TradingAgents/mobile-private/v1"
MARKETS = ("kr", "us")

_PUBLIC_ROW_FIELDS = (
    "ticker",
    "display_name",
    "last_price",
    "market_data_asof",
    "session_vwap",
    "vwap_distance_pct",
    "vwap_position_ko",
    "relative_volume",
    "trading_value",
    "price_change_pct",
    "spread_bps",
    "day_high",
    "day_low",
    "sync_summary_ko",
    "data_status_ko",
    "reason_codes_ko",
    "quality",
)

_PRIVATE_ROW_FIELDS = (
    "ticker",
    "display_name",
    "is_held",
    "sector",
    "strategy_code",
    "strategy_ko",
    "last_price",
    "market_data_asof",
    "session_vwap",
    "vwap_distance_pct",
    "vwap_position_ko",
    "relative_volume",
    "trading_value",
    "price_change_pct",
    "spread_bps",
    "day_high",
    "day_low",
    "sync_summary_ko",
    "execution_condition_ko",
    "risk_condition_ko",
    "data_status_ko",
    "decision_state_ko",
    "execution_timing_ko",
    "reason_codes_ko",
    "quality",
)

_PRIVATE_ACTION_FIELDS = (
    "canonical_ticker",
    "confidence",
    "action_now",
    "delta_krw_now",
    "target_weight_now",
    "action_if_triggered",
    "delta_krw_if_triggered",
    "target_weight_if_triggered",
    "strategy_state",
    "execution_feasibility_now",
    "portfolio_relative_action",
    "risk_action",
    "sell_side_category",
    "sell_intent",
    "sell_size_plan",
    "position_metrics",
    "profit_taking_plan",
    "reason_codes",
    "gate_reasons",
)

_FORBIDDEN_PUBLIC_KEYS = {
    "is_held",
    "private_portfolio_overlay",
    "actions",
    "action_now",
    "action_if_triggered",
    "delta_krw_now",
    "delta_krw_if_triggered",
    "target_weight_now",
    "target_weight_if_triggered",
    "position_metrics",
    "account_id",
    "account_no",
    "broker_account_id",
    "quantity",
    "market_value",
    "average_price",
    "avg_price",
}


def build_mobile_site(
    *,
    site_dir: Path,
    archive_dir: Path,
    public_base_url: str = "",
) -> dict[str, Any]:
    """Build a public research hub and an optional encrypted personal dashboard.

    Plaintext personal rows never touch ``site_dir``.  The private payload is built
    in memory and only the AES-GCM envelope is written to the Pages artifact.
    """

    site_root = Path(site_dir)
    mobile_root = site_root / "mobile"
    mobile_root.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now().astimezone().isoformat()

    public_payload = {
        "schema": MOBILE_SCHEMA,
        "generated_at": generated_at,
        "privacy": "PUBLIC_RESEARCH_ONLY_NO_PORTFOLIO_MEMBERSHIP_OR_ACTIONS",
        "markets": {},
    }
    private_payload = {
        "schema": PRIVATE_SCHEMA,
        "generated_at": generated_at,
        "privacy": "CLIENT_SIDE_DECRYPTION_REQUIRED",
        "markets": {},
    }

    for market in MARKETS:
        public_packet = _read_public_work_packet(site_root, market)
        if not public_packet:
            public_packet = build_surface_packet(market, archive_dir=archive_dir, public=True)
        private_packet = build_surface_packet(market, archive_dir=archive_dir, public=False)
        public_payload["markets"][market] = _public_market_payload(public_packet)
        private_payload["markets"][market] = _private_market_payload(private_packet)

    key_text = os.getenv("TRADINGAGENTS_MOBILE_DASHBOARD_KEY", "").strip()
    envelope: dict[str, Any] | None = None
    if key_text:
        key = decode_dashboard_key(key_text)
        envelope = encrypt_private_payload(private_payload, key=key)
    elif _private_payload_has_portfolio_actions(private_payload):
        # A successful production build must never silently drop an action
        # dashboard merely because its encryption secret was not injected.
        # Research-only builds remain useful without the optional key.
        raise ValueError(
            "TRADINGAGENTS_MOBILE_DASHBOARD_KEY is required when private portfolio actions exist."
        )

    assert_public_payload_safe(public_payload)
    _write_json(mobile_root / "public.json", public_payload)
    _write_text(mobile_root / "index.html", _public_html(public_payload, public_base_url=public_base_url))
    _write_text(mobile_root / "mobile.css", _MOBILE_CSS)
    _write_text(mobile_root / "private.html", _private_html())
    _write_text(mobile_root / "private.js", _PRIVATE_JS)

    private_status: dict[str, Any]
    if envelope is not None:
        _write_json(mobile_root / "private.enc.json", envelope)
        private_status = {
            "enabled": True,
            "envelope_sha256": _sha256_json(envelope),
            "key_delivery": "URL_FRAGMENT_ONLY",
        }
    else:
        (mobile_root / "private.enc.json").unlink(missing_ok=True)
        private_status = {
            "enabled": False,
            "reason": "TRADINGAGENTS_MOBILE_DASHBOARD_KEY_NOT_CONFIGURED",
        }

    status = {
        "schema": MOBILE_SCHEMA,
        "generated_at": generated_at,
        "public_url": _join_url(public_base_url, "mobile/"),
        "private_url_template": _join_url(
            public_base_url,
            "mobile/private.html#key=<base64url-key>&market=<kr|us>",
        ),
        "public_payload_sha256": _sha256_json(public_payload),
        "private_dashboard": private_status,
    }
    _write_json(mobile_root / "status.json", status)
    return status


def sanitize_public_decision_bundle(
    bundle: dict[str, Any],
    *,
    max_candidates: int | None = None,
    allowed_tickers: Iterable[Any] | None = None,
) -> dict[str, Any]:
    """Return a fail-closed public recovery bundle.

    With an explicit public watchlist/scanner allow-list, those research rows are
    retained regardless of ownership while all membership fields are removed.
    Without that contract, held rows fail closed. Portfolio-derived strategies
    and execution conditions are always excluded.
    """

    if not isinstance(bundle, dict) or not bundle:
        return {}
    allowed = (
        {identity for value in allowed_tickers for identity in _ticker_identity_keys(value)}
        if allowed_tickers is not None
        else None
    )
    candidate_limit = None if max_candidates is None else max(0, int(max_candidates))
    rows: list[dict[str, Any]] = []
    for source in bundle.get("strategy_table") or []:
        if candidate_limit is not None and len(rows) >= candidate_limit:
            break
        if not isinstance(source, dict):
            continue
        identities = set(_ticker_identity_keys(source.get("ticker")))
        if allowed is None:
            if source.get("is_held") is True:
                continue
        elif not identities.intersection(allowed):
            continue
        row = {key: source.get(key) for key in _PUBLIC_ROW_FIELDS if source.get(key) is not None}
        row["quality"] = _public_quality(source.get("quality"))
        rows.append(row)
    quality = bundle.get("quality") if isinstance(bundle.get("quality"), dict) else {}
    result = {
        key: bundle.get(key)
        for key in (
            "artifact_type",
            "version",
            "run_id",
            "market",
            "generated_at",
            "analysis_source_run_id",
            "execution_source_run_id",
            "checkpoint",
            "checkpoint_timezone",
        )
        if bundle.get(key) is not None
    }
    result.update(
        {
            "quality": {
                key: quality.get(key)
                for key in (
                    "report_mode",
                    "decision_ready",
                    "conditional_strategy_ready",
                    "quality_label_ko",
                    "fresh_row_ratio",
                    "conditional_row_ratio",
                )
                if quality.get(key) is not None
            }
            | {"portfolio_membership_omitted": True},
            "strategy_table": rows,
            "transmission_scope": {
                "public_recovery_only": True,
                "portfolio_membership_omitted": True,
                "portfolio_actions_omitted": True,
                "transmitted_research_candidate_count": len(rows),
            },
        }
    )
    assert_public_payload_safe(result)
    return result


def decode_dashboard_key(value: str) -> bytes:
    text = str(value or "").strip()
    if not text:
        raise ValueError("Dashboard encryption key is empty.")
    if len(text) != 43 or any(character not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_" for character in text):
        raise ValueError("TRADINGAGENTS_MOBILE_DASHBOARD_KEY must be a 43-character base64url key.")
    try:
        candidate = base64.urlsafe_b64decode(text + "=")
    except (ValueError, TypeError) as exc:
        raise ValueError("TRADINGAGENTS_MOBILE_DASHBOARD_KEY is not valid base64url.") from exc
    if len(candidate) != 32 or _b64url(candidate) != text:
        raise ValueError("TRADINGAGENTS_MOBILE_DASHBOARD_KEY must decode to exactly 32 bytes.")
    return candidate


def encrypt_private_payload(payload: dict[str, Any], *, key: bytes, nonce: bytes | None = None) -> dict[str, Any]:
    if len(key) != 32:
        raise ValueError("AES-256-GCM requires a 32-byte key.")
    nonce_bytes = nonce or secrets.token_bytes(12)
    if len(nonce_bytes) != 12:
        raise ValueError("AES-GCM nonce must be 12 bytes.")
    plaintext = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ciphertext = AESGCM(key).encrypt(nonce_bytes, plaintext, PRIVATE_AAD)
    return {
        "schema": ENCRYPTED_SCHEMA,
        "alg": "A256GCM",
        "aad": _b64url(PRIVATE_AAD),
        "nonce": _b64url(nonce_bytes),
        "ciphertext": _b64url(ciphertext),
    }


def decrypt_private_payload(envelope: dict[str, Any], *, key: bytes) -> dict[str, Any]:
    if envelope.get("schema") != ENCRYPTED_SCHEMA or envelope.get("alg") != "A256GCM":
        raise ValueError("Unsupported mobile dashboard envelope.")
    nonce = _b64url_decode(envelope.get("nonce"))
    ciphertext = _b64url_decode(envelope.get("ciphertext"))
    aad = _b64url_decode(envelope.get("aad"))
    if aad != PRIVATE_AAD:
        raise ValueError("Invalid mobile dashboard authenticated context.")
    plaintext = AESGCM(key).decrypt(nonce, ciphertext, aad)
    payload = json.loads(plaintext)
    if not isinstance(payload, dict) or payload.get("schema") != PRIVATE_SCHEMA:
        raise ValueError("Invalid private mobile dashboard payload.")
    return payload


def assert_public_payload_safe(value: Any, *, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).strip().lower()
            if normalized in _FORBIDDEN_PUBLIC_KEYS:
                raise ValueError(f"Forbidden private key in public mobile payload at {path}.{key}")
            assert_public_payload_safe(item, path=f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            assert_public_payload_safe(item, path=f"{path}[{index}]")


def _read_public_work_packet(site_root: Path, market: str) -> dict[str, Any]:
    path = site_root / "work" / "v1" / market / "latest.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _public_market_payload(packet: dict[str, Any]) -> dict[str, Any]:
    body = packet.get("body") if isinstance(packet.get("body"), dict) else {}
    current = body.get("current") if isinstance(body.get("current"), dict) else {}
    bundle = current.get("bundle") if isinstance(current.get("bundle"), dict) else {}
    rows = []
    for source in bundle.get("strategy_table") or []:
        if not isinstance(source, dict) or source.get("is_held") is True:
            continue
        row = {key: source.get(key) for key in _PUBLIC_ROW_FIELDS if source.get(key) is not None}
        row["quality"] = _public_quality(source.get("quality"))
        rows.append(row)
    result = {
        "market": str(body.get("market") or packet.get("surface") or "").upper(),
        "event_id": packet.get("event_id"),
        "source_health": body.get("source_health") or "MISSING",
        "report_mode": body.get("report_mode") or "RESEARCH",
        "run_id": current.get("run_id"),
        "started_at": current.get("started_at"),
        "source": _safe_mapping(body.get("source"), ("run_id", "last_run_at", "status")),
        "guardrails": _safe_mapping(
            body.get("guardrails"),
            ("valid_until", "expired_at_build", "decision_ready", "conditional_strategy_ready", "report_mode"),
        ),
        "quality": _safe_mapping(
            bundle.get("quality"),
            (
                "report_mode",
                "decision_ready",
                "conditional_strategy_ready",
                "quality_label_ko",
                "fresh_row_ratio",
                "conditional_row_ratio",
            ),
        ),
        "rows": rows,
        "coverage": {
            "research_candidate_count": len(rows),
            "portfolio_membership_omitted": True,
            "portfolio_actions_omitted": True,
        },
    }
    assert_public_payload_safe(result)
    return result


def _private_market_payload(packet: dict[str, Any]) -> dict[str, Any]:
    body = packet.get("body") if isinstance(packet.get("body"), dict) else {}
    current = body.get("current") if isinstance(body.get("current"), dict) else {}
    bundle = current.get("bundle") if isinstance(current.get("bundle"), dict) else {}
    quality = bundle.get("quality") if isinstance(bundle.get("quality"), dict) else {}
    source_metadata = body.get("source") if isinstance(body.get("source"), dict) else {}
    universe_coverage = (
        current.get("universe_coverage")
        if isinstance(current.get("universe_coverage"), dict)
        else {}
    )
    overlay = current.get("private_portfolio_overlay") if isinstance(current.get("private_portfolio_overlay"), dict) else {}
    actions = []
    for action_source in overlay.get("actions") or []:
        if isinstance(action_source, dict):
            actions.append(
                {
                    key: action_source.get(key)
                    for key in _PRIVATE_ACTION_FIELDS
                    if action_source.get(key) is not None
                }
            )
    action_by_ticker: dict[str, dict[str, Any]] = {}
    for item in actions:
        for identity in _ticker_identity_keys(item.get("canonical_ticker")):
            action_by_ticker.setdefault(identity, item)
    rows = []
    for row_source in bundle.get("strategy_table") or []:
        if not isinstance(row_source, dict):
            continue
        row = {
            key: row_source.get(key)
            for key in _PRIVATE_ROW_FIELDS
            if row_source.get(key) is not None
        }
        action = next(
            (action_by_ticker[key] for key in _ticker_identity_keys(row.get("ticker")) if key in action_by_ticker),
            None,
        )
        if action:
            row["portfolio_action"] = action
        rows.append(row)
    return {
        "market": str(body.get("market") or packet.get("surface") or "").upper(),
        "event_id": packet.get("event_id"),
        "source_health": body.get("source_health") or "MISSING",
        "report_mode": body.get("report_mode") or "RESEARCH",
        "run_id": current.get("run_id"),
        "started_at": current.get("started_at"),
        "manifest_status": source_metadata.get("status"),
        "decision_ready": quality.get("decision_ready"),
        "source": _safe_mapping(source_metadata, ("run_id", "last_run_at", "status")),
        "guardrails": body.get("guardrails") if isinstance(body.get("guardrails"), dict) else {},
        "quality": quality,
        "universe_coverage": universe_coverage,
        "provenance": {
            "surface_run_id": current.get("run_id"),
            "manifest_run_id": source_metadata.get("run_id"),
            "universe_source_run_id": universe_coverage.get("source_run_id"),
            "decision_bundle_run_id": bundle.get("run_id"),
            "analysis_source_run_id": bundle.get("analysis_source_run_id"),
            "execution_source_run_id": bundle.get("execution_source_run_id"),
        },
        "portfolio_action_count": len(actions),
        "rows": rows,
        "coverage": universe_coverage,
        "transmission_scope": (
            bundle.get("transmission_scope")
            if isinstance(bundle.get("transmission_scope"), dict)
            else {}
        ),
    }


def _private_payload_has_portfolio_actions(payload: dict[str, Any]) -> bool:
    markets = payload.get("markets") if isinstance(payload.get("markets"), dict) else {}
    for market in markets.values():
        if not isinstance(market, dict):
            continue
        if isinstance(market.get("portfolio_action_count"), int) and market["portfolio_action_count"] > 0:
            return True
        for row in market.get("rows") or []:
            if isinstance(row, dict) and isinstance(row.get("portfolio_action"), dict):
                return True
    return False


def _public_quality(value: Any) -> dict[str, Any]:
    return _safe_mapping(
        value,
        (
            "row_mode",
            "execution_ready",
            "conditional_strategy_ready",
            "current_execution_promotion",
            "generated_in_current_run",
            "freshness_class",
            "execution_eligibility",
            "data_status",
            "provider_status",
            "row_valid_until",
            "expired_at_build",
        ),
    )


def _safe_mapping(value: Any, keys: tuple[str, ...]) -> dict[str, Any]:
    source = value if isinstance(value, dict) else {}
    return {key: source.get(key) for key in keys if source.get(key) is not None}


def _ticker_identity_keys(value: Any) -> tuple[str, ...]:
    ticker = str(value or "").strip().upper()
    if not ticker:
        return ()
    keys = [ticker]
    for suffix in (".KS", ".KQ"):
        if ticker.endswith(suffix):
            keys.append(ticker[: -len(suffix)])
            break
    return tuple(dict.fromkeys(keys))


def _public_html(payload: dict[str, Any], *, public_base_url: str) -> str:
    market_sections = []
    for market in MARKETS:
        item = payload["markets"].get(market) or {}
        rows = item.get("rows") or []
        cards = "".join(_public_card(row) for row in rows)
        if not cards:
            cards = "<p class='empty'>공개 가능한 신규 리서치 후보가 없습니다.</p>"
        market_sections.append(
            f"""
            <section class="market-panel" data-market="{market}" id="market-{market}">
              <div class="market-head">
                <div><p class="eyebrow">{market.upper()} MARKET</p><h2>{market.upper()} 리서치 후보</h2></div>
                <span class="health health-{_css_token(item.get('source_health'))}">{_escape(item.get('source_health') or 'MISSING')}</span>
              </div>
              <div class="source-meta">
                <span>Run {_escape(item.get('run_id') or '-')}</span>
                <span>{_escape(item.get('started_at') or '-')}</span>
                <span>{len(rows)}개 공개 후보</span>
              </div>
              <div class="cards">{cards}</div>
            </section>
            """
        )
    private_url = _join_url(public_base_url, "mobile/private.html") or "private.html"
    embedded = html.escape(json.dumps(payload, ensure_ascii=False), quote=False)
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="theme-color" content="#081a2b">
  <meta name="referrer" content="no-referrer">
  <title>TradingAgents 모바일 리서치</title>
  <link rel="stylesheet" href="mobile.css">
</head>
<body>
  <header class="topbar"><a href="../index.html">TradingAgents</a><span>공개 리서치</span></header>
  <main>
    <section class="hero-mobile">
      <p class="eyebrow">MOBILE INVESTMENT HUB</p>
      <h1>장중 리서치 한눈에 보기</h1>
      <p>보유 여부와 계좌 액션은 공개하지 않습니다. 행별 데이터 유효시간이 지나면 화면에서 자동으로 실행 차단 상태로 바뀝니다.</p>
      <div class="privacy-banner">공개 안전 모드 · 개인 계좌 정보 없음</div>
      <a class="private-link" href="{_escape(private_url)}">암호화된 내 액션표 열기</a>
    </section>
    <nav class="market-tabs" aria-label="시장 선택">
      <button type="button" data-target="kr" aria-pressed="true">KR</button>
      <button type="button" data-target="us" aria-pressed="false">US</button>
    </nav>
    {''.join(market_sections)}
    <p class="footer-note">자동 주문 지시가 아닙니다. 오래되거나 불완전한 데이터는 실행에 사용하지 마세요.</p>
  </main>
  <script id="mobile-data" type="application/json">{embedded}</script>
  <script>
  (() => {{
    const tabs = [...document.querySelectorAll('[data-target]')];
    const panels = [...document.querySelectorAll('[data-market]')];
    function select(market) {{
      tabs.forEach((tab) => tab.setAttribute('aria-pressed', String(tab.dataset.target === market)));
      panels.forEach((panel) => panel.hidden = panel.dataset.market !== market);
    }}
    tabs.forEach((tab) => tab.addEventListener('click', () => select(tab.dataset.target)));
    const requestedMarket = new URLSearchParams(location.search).get('market');
    select(requestedMarket === 'us' ? 'us' : 'kr');
    function refreshExpiry() {{
      const now = Date.now();
      let nextDeadline = Number.POSITIVE_INFINITY;
      document.querySelectorAll('[data-valid-until]').forEach((card) => {{
        const deadline = Date.parse(card.dataset.validUntil || '');
        if (!Number.isFinite(deadline)) return;
        if (deadline <= now) {{
          card.dataset.rowMode = 'BLOCKED_STALE';
          const badge = card.querySelector('.row-mode');
          if (badge) badge.textContent = 'BLOCKED_STALE';
          const warning = card.querySelector('.expiry-warning');
          if (warning) warning.hidden = false;
        }} else {{
          nextDeadline = Math.min(nextDeadline, deadline);
        }}
      }});
      if (Number.isFinite(nextDeadline)) setTimeout(refreshExpiry, Math.max(50, nextDeadline - now + 50));
    }}
    refreshExpiry();
  }})();
  </script>
</body>
</html>
"""


def _public_card(row: dict[str, Any]) -> str:
    quality = row.get("quality") if isinstance(row.get("quality"), dict) else {}
    mode = str(quality.get("row_mode") or "MISSING")
    valid_until = str(quality.get("row_valid_until") or "")
    return f"""
    <article class="action-card" data-row-mode="{_escape(mode)}" data-valid-until="{_escape(valid_until)}">
      <div class="card-title"><div><strong>{_escape(row.get('ticker') or '-')}</strong><span>{_escape(row.get('display_name') or '')}</span></div><span class="row-mode mode-{_css_token(mode)}">{_escape(mode)}</span></div>
      <p class="expiry-warning" hidden>유효시간 경과 · 실행 차단</p>
      <div class="price-line"><strong>{_fmt_price(row.get('last_price'))}</strong><span>{_escape(row.get('market_data_asof') or '-')}</span></div>
      <dl>
        <div><dt>VWAP</dt><dd>{_escape(row.get('vwap_position_ko') or '-')}</dd></div>
        <div><dt>상대 거래량</dt><dd>{_fmt_ratio(row.get('relative_volume'))}</dd></div>
        <div><dt>섹터·지수</dt><dd>{_escape(row.get('sync_summary_ko') or '-')}</dd></div>
        <div><dt>데이터</dt><dd>{_escape(row.get('data_status_ko') or quality.get('freshness_class') or '-')}</dd></div>
      </dl>
    </article>
    """


def _private_html() -> str:
    return """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="theme-color" content="#081a2b">
  <meta name="referrer" content="no-referrer">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'">
  <title>TradingAgents 암호화 개인 액션표</title>
  <link rel="stylesheet" href="mobile.css">
</head>
<body class="private-body">
  <header class="topbar"><a href="index.html">공개 리서치</a><span>암호화 개인 액션</span></header>
  <main>
    <section class="hero-mobile">
      <p class="eyebrow">PRIVATE · AES-256-GCM</p>
      <h1>내 투자 전략 액션표</h1>
      <p>복호화 키는 URL의 #key fragment에서만 읽으며 서버로 전송하거나 기기에 저장하지 않습니다.</p>
    </section>
    <div id="private-status" class="privacy-banner" role="status">암호화 payload를 여는 중입니다.</div>
    <nav id="private-tabs" class="market-tabs" aria-label="시장 선택" hidden></nav>
    <div id="private-root"></div>
  </main>
  <script src="private.js" defer></script>
</body>
</html>
"""


_MOBILE_CSS = r"""
:root {
  color-scheme: dark;
  --bg: #06111d;
  --panel: #0c2033;
  --panel-2: #102b43;
  --text: #f6f8fb;
  --muted: #a9bacb;
  --line: rgba(255,255,255,.12);
  --accent: #59d6c7;
  --warn: #ffc45b;
  --danger: #ff7c83;
  --ok: #75dfa0;
}
* { box-sizing: border-box; }
html { background: var(--bg); }
body { min-width: 0; margin: 0; background: radial-gradient(circle at top right, #12395a 0, var(--bg) 34rem); color: var(--text); font: 16px/1.55 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans KR", sans-serif; }
a { color: inherit; }
.topbar { position: sticky; top: 0; z-index: 20; display: flex; justify-content: space-between; gap: 12px; min-height: 52px; padding: max(10px, env(safe-area-inset-top)) 16px 10px; border-bottom: 1px solid var(--line); background: rgba(6,17,29,.94); backdrop-filter: blur(14px); font-size: .88rem; color: var(--muted); }
.topbar a { color: var(--text); font-weight: 750; text-decoration: none; }
main { width: 100%; max-width: 760px; min-width: 0; margin: 0 auto; padding: 22px 14px calc(42px + env(safe-area-inset-bottom)); }
.hero-mobile { padding: 12px 2px 20px; }
.eyebrow { margin: 0 0 7px; color: var(--accent); font-size: .72rem; font-weight: 800; letter-spacing: .12em; }
h1, h2, p { overflow-wrap: anywhere; }
h1 { margin: 0; font-size: clamp(1.8rem, 8vw, 2.55rem); line-height: 1.08; letter-spacing: -.04em; }
h2 { margin: 0; font-size: 1.25rem; }
.hero-mobile > p:not(.eyebrow) { margin: 12px 0; color: var(--muted); }
.privacy-banner { min-width: 0; max-width: 100%; margin: 14px 0; padding: 11px 13px; border: 1px solid rgba(89,214,199,.35); border-radius: 12px; background: rgba(89,214,199,.09); color: #c9fff8; overflow-wrap: anywhere; font-size: .9rem; }
.privacy-banner.error { border-color: rgba(255,124,131,.45); background: rgba(255,124,131,.10); color: #ffd8da; }
.private-link { display: inline-flex; align-items: center; min-height: 44px; padding: 10px 15px; border-radius: 12px; background: var(--accent); color: #04201f; font-weight: 800; text-decoration: none; }
.market-tabs { position: sticky; top: calc(53px + max(0px, env(safe-area-inset-top) - 10px)); z-index: 15; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; min-width: 0; max-width: 100%; margin: 0 -2px 18px; padding: 9px 2px; background: rgba(6,17,29,.94); backdrop-filter: blur(14px); }
.market-tabs button { min-width: 0; min-height: 44px; border: 1px solid var(--line); border-radius: 12px; background: var(--panel); color: var(--muted); overflow-wrap: anywhere; font: inherit; font-weight: 800; }
.market-tabs button[aria-pressed="true"] { border-color: var(--accent); background: rgba(89,214,199,.14); color: var(--text); }
.market-panel, #private-root { min-width: 0; max-width: 100%; }
.market-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin: 8px 0; }
.health, .row-mode, .held-badge { display: inline-flex; align-items: center; flex: 0 0 auto; min-height: 28px; padding: 4px 8px; border-radius: 999px; background: var(--panel-2); color: var(--muted); font-size: .7rem; font-weight: 850; letter-spacing: .03em; }
.health-ok, .mode-immediate { color: var(--ok); }
.health-degraded, .mode-conditional { color: var(--warn); }
.health-failed, .health-stale, .mode-blocked_stale, .mode-missing { color: var(--danger); }
.source-meta { display: flex; flex-wrap: wrap; gap: 6px 12px; margin-bottom: 12px; color: var(--muted); font-size: .78rem; }
.source-meta span, .card-title strong, .card-title div > span, .price-line strong, .price-line span { min-width: 0; overflow-wrap: anywhere; }
.cards { display: grid; grid-template-columns: minmax(0, 1fr); gap: 12px; }
.action-card { min-width: 0; padding: 15px; border: 1px solid var(--line); border-radius: 17px; background: linear-gradient(145deg, rgba(16,43,67,.96), rgba(10,29,47,.96)); box-shadow: 0 12px 28px rgba(0,0,0,.18); }
.action-card[data-row-mode="BLOCKED_STALE"], .action-card[data-row-mode="MISSING"] { border-color: rgba(255,124,131,.28); }
.card-title { display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; }
.card-title div { min-width: 0; }
.card-title strong { display: block; font-size: 1.12rem; }
.card-title div > span { display: block; color: var(--muted); font-size: .82rem; }
.price-line { display: flex; justify-content: space-between; align-items: baseline; gap: 10px; margin: 15px 0; }
.price-line strong { font-size: 1.5rem; letter-spacing: -.025em; }
.price-line span { color: var(--muted); font-size: .74rem; text-align: right; }
.expiry-warning { margin: 10px 0 0; padding: 8px 10px; border-radius: 9px; background: rgba(255,124,131,.13); color: #ffc1c5; font-size: .82rem; font-weight: 750; }
dl { display: grid; gap: 0; margin: 0; }
dl div { display: grid; grid-template-columns: minmax(86px, .65fr) minmax(0, 1.35fr); gap: 10px; padding: 9px 0; border-top: 1px solid var(--line); }
dt { color: var(--muted); font-size: .8rem; }
dd { margin: 0; text-align: right; overflow-wrap: anywhere; font-size: .88rem; }
.private-action { margin: 12px 0; padding: 12px; border-radius: 12px; background: rgba(89,214,199,.08); }
.private-action strong { display: block; color: var(--accent); }
.held-badge { margin-left: 6px; color: var(--accent); }
.empty, .footer-note { color: var(--muted); }
.footer-note { margin: 24px 2px 0; font-size: .78rem; }
details { margin-top: 10px; }
summary { min-height: 44px; padding: 11px 0; color: var(--muted); cursor: pointer; }
@media (min-width: 660px) {
  main { padding-left: 20px; padding-right: 20px; }
  .cards { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { scroll-behavior: auto !important; } }
""".strip()


_PRIVATE_JS = r"""
(() => {
  'use strict';
  const status = document.getElementById('private-status');
  const root = document.getElementById('private-root');
  const tabs = document.getElementById('private-tabs');
  const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (ch) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const b64 = (value) => {
    const normalized = String(value || '').replace(/-/g, '+').replace(/_/g, '/');
    const padded = normalized + '='.repeat((4 - normalized.length % 4) % 4);
    const raw = atob(padded);
    return Uint8Array.from(raw, (ch) => ch.charCodeAt(0));
  };
  const fmt = (value) => Number.isFinite(Number(value)) ? Number(value).toLocaleString(undefined, {maximumFractionDigits: 2}) : '-';
  const actionLabels = {
    NO_ACTION: '지금은 주문 없음', HOLD: '보유 유지', WATCH: '관찰', WAIT: '대기',
    STARTER: '초기 분할매수', STARTER_NOW: '지금 초기 분할매수 검토',
    ADD: '분할 추가매수', ADD_NOW: '지금 분할 추가매수 검토', BUY: '매수 검토', BUY_NOW: '지금 매수 검토',
    REDUCE: '비중 축소', REDUCE_NOW: '지금 비중 축소 검토', TRIM_NOW: '지금 일부 축소 검토',
    REDUCE_RISK: '리스크 축소', REDUCE_IF_TRIGGERED: '조건 충족 시 비중 축소',
    TAKE_PROFIT: '이익 실현', TAKE_PROFIT_NOW: '지금 이익 실현 검토', TAKE_PROFIT_IF_TRIGGERED: '조건 충족 시 이익 실현',
    STOP_LOSS: '손절 검토', STOP_LOSS_NOW: '지금 손절 검토', STOP_LOSS_IF_TRIGGERED: '조건 충족 시 손절',
    EXIT: '청산 검토', EXIT_NOW: '지금 청산 검토', EXIT_IF_TRIGGERED: '조건 충족 시 청산', SELL: '매도 검토'
  };
  const actionLabel = (value) => actionLabels[String(value || '').toUpperCase()] || String(value || '-');
  const won = (value) => {
    if (!Number.isFinite(Number(value))) return '-';
    return new Intl.NumberFormat('ko-KR', {style: 'currency', currency: 'KRW', maximumFractionDigits: 0, signDisplay: 'always'}).format(Number(value));
  };
  const percent = (value) => Number.isFinite(Number(value)) ? new Intl.NumberFormat('ko-KR', {style: 'percent', maximumFractionDigits: 1}).format(Number(value)) : '-';
  const fragment = new URLSearchParams(location.hash.replace(/^#/, ''));
  const keyText = fragment.get('key') || fragment.get('k') || '';
  const requestedMarket = fragment.get('market') === 'us' ? 'us' : 'kr';
  const requestedRun = fragment.get('run') || '';
  if (location.hash) history.replaceState(history.state, document.title, `${location.pathname}${location.search}`);
  let expiryTimer;

  function immediateContractComplete(market) {
    const coverage = (market || {}).universe_coverage || {};
    const provenance = (market || {}).provenance || {};
    const source = (market || {}).source || {};
    const quality = (market || {}).quality || {};
    const guardrails = (market || {}).guardrails || {};
    const expected = Number(coverage.expected_analysis_count);
    const total = Number(coverage.analysis_total_count);
    const successful = Number(coverage.analysis_successful_count);
    const zeroCounts = [
      coverage.missing_holding_count,
      coverage.missing_watchlist_count,
      coverage.missing_analysis_count,
      coverage.analysis_failed_count,
    ].every((value) => Number.isInteger(Number(value)) && Number(value) === 0);
    const runId = String((market || {}).run_id || '');
    const universeMode = String(coverage.ticker_universe_mode || '').toLowerCase();
    const accountReady = !['config_plus_account', 'account_only'].includes(universeMode)
      || String(coverage.account_snapshot_status || '').toLowerCase() === 'loaded';
    const boundRunIds = [
      provenance.surface_run_id,
      provenance.manifest_run_id,
      provenance.universe_source_run_id,
      provenance.decision_bundle_run_id,
    ].map((value) => String(value || ''));
    return coverage.status === 'COMPLETE'
      && coverage.complete === true
      && Number.isInteger(expected) && expected > 0
      && Number.isInteger(total) && total === expected
      && Number.isInteger(successful) && successful === expected
      && zeroCounts
      && accountReady
      && String((market || {}).manifest_status || '').toLowerCase() === 'success'
      && String(source.status || '').toLowerCase() === 'success'
      && (market || {}).decision_ready === true
      && quality.decision_ready === true
      && guardrails.decision_ready === true
      && runId !== ''
      && boundRunIds.every((value) => value === runId);
  }
  function effectiveMode(row, market) {
    const quality = row.quality || {};
    const sourceHealth = String((market || {}).source_health || 'MISSING').toUpperCase();
    const guardrails = (market || {}).guardrails || {};
    const marketValid = Date.parse(guardrails.valid_until || '');
    if (sourceHealth !== 'OK') return 'BLOCKED_STALE';
    if (guardrails.expired_at_build === true || !Number.isFinite(marketValid) || marketValid <= Date.now()) return 'BLOCKED_STALE';
    const valid = Date.parse(quality.row_valid_until || '');
    if (quality.expired_at_build === true || !Number.isFinite(valid) || valid <= Date.now()) return 'BLOCKED_STALE';
    const declared = String(quality.row_mode || 'MISSING').toUpperCase();
    if (declared === 'IMMEDIATE' && (
      !immediateContractComplete(market)
      || quality.execution_ready !== true
      || quality.generated_in_current_run !== true
    )) return 'BLOCKED_INCOMPLETE';
    return declared;
  }
  function card(row, market) {
    const mode = effectiveMode(row, market);
    const action = row.portfolio_action || {};
    const actionNow = mode === 'IMMEDIATE'
      ? actionLabel(action.action_now || row.strategy_ko || '데이터 확인 전 대기')
      : mode === 'CONDITIONAL'
        ? '지금은 주문하지 말고 조건 충족을 기다리세요'
        : '데이터 만료·불완전 — 지금 주문하지 마세요';
    const conditional = actionLabel(action.action_if_triggered || row.execution_condition_ko || '-');
    const risk = actionLabel(action.risk_action || row.risk_condition_ko || '-');
    return `<article class="action-card" data-row-mode="${esc(mode)}">
      <div class="card-title"><div><strong>${esc(row.ticker || '-')} ${row.is_held ? '<span class="held-badge">보유</span>' : ''}</strong><span>${esc(row.display_name || '')}</span></div><span class="row-mode mode-${esc(mode.toLowerCase())}">${esc(mode)}</span></div>
      ${mode.startsWith('BLOCKED_') ? '<p class="expiry-warning">커버리지·상태·유효시간 확인 필요 · 지금 주문하지 마세요</p>' : ''}
      <div class="price-line"><strong>${fmt(row.last_price)}</strong><span>${esc(row.market_data_asof || '-')}</span></div>
      <div class="private-action"><strong>지금 할 일</strong>${esc(actionNow)}</div>
      <dl>
        <div><dt>조건 충족 시</dt><dd>${esc(conditional)}</dd></div>
        <div><dt>위험·무효화</dt><dd>${esc(risk)}</dd></div>
        <div><dt>VWAP</dt><dd>${esc(row.vwap_position_ko || '-')}</dd></div>
        <div><dt>상대 거래량</dt><dd>${fmt(row.relative_volume)}배</dd></div>
        <div><dt>데이터</dt><dd>${esc(row.data_status_ko || (row.quality || {}).freshness_class || '-')}</dd></div>
      </dl>
      <details><summary>포트폴리오 세부 액션</summary><dl>
        <div><dt>현재 증감</dt><dd>${esc(won(action.delta_krw_now))}</dd></div>
        <div><dt>조건부 증감</dt><dd>${esc(won(action.delta_krw_if_triggered))}</dd></div>
        <div><dt>목표 비중</dt><dd>${esc(percent(action.target_weight_now ?? action.target_weight_if_triggered))}</dd></div>
      </dl></details>
    </article>`;
  }
  function render(payload) {
    const markets = payload.markets || {};
    if (requestedRun && String((markets[requestedMarket] || {}).run_id || '') !== requestedRun) {
      throw new Error('Telegram 링크의 분석 run과 현재 개인 대시보드 run이 일치하지 않습니다. 최신 알림을 사용하세요.');
    }
    tabs.hidden = false;
    tabs.innerHTML = ['kr', 'us'].map((market, index) => `<button type="button" data-target="${market}" aria-pressed="${index === 0}">${market.toUpperCase()}</button>`).join('');
    root.innerHTML = ['kr', 'us'].map((market) => {
      const item = markets[market] || {};
      const rows = Array.isArray(item.rows) ? item.rows : [];
      return `<section class="market-panel" data-market="${market}"><div class="market-head"><div><p class="eyebrow">${market.toUpperCase()} PRIVATE</p><h2>${market.toUpperCase()} 개인 액션</h2></div><span class="health health-${esc(String(item.source_health || 'missing').toLowerCase())}">${esc(item.source_health || 'MISSING')}</span></div><div class="source-meta"><span>Run ${esc(item.run_id || '-')}</span><span>${rows.length}개 행</span></div><div class="cards">${rows.map((row) => card(row, item)).join('') || '<p class="empty">개인 액션 데이터가 없습니다.</p>'}</div></section>`;
    }).join('');
    const buttons = [...tabs.querySelectorAll('button')];
    const panels = [...root.querySelectorAll('[data-market]')];
    const select = (market) => { buttons.forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.target === market))); panels.forEach((panel) => panel.hidden = panel.dataset.market !== market); };
    buttons.forEach((button) => button.addEventListener('click', () => select(button.dataset.target)));
    select(requestedMarket);
    status.textContent = `복호화 완료 · ${payload.generated_at || '-'}`;
    clearTimeout(expiryTimer);
    const now = Date.now();
    const deadlines = Object.values(markets).flatMap((item) => [
      Date.parse((item.guardrails || {}).valid_until || ''),
      ...(item.rows || []).map((row) => Date.parse((row.quality || {}).row_valid_until || '')),
    ]).filter((deadline) => Number.isFinite(deadline) && deadline > now);
    if (deadlines.length) expiryTimer = setTimeout(() => render(payload), Math.max(50, Math.min(...deadlines) - now + 50));
  }
  async function start() {
    if (!keyText) throw new Error('URL에 #key=... 복호화 키가 없습니다. Telegram의 개인 링크를 사용하세요.');
    if (!/^[A-Za-z0-9_-]{43}$/.test(keyText)) throw new Error('복호화 키 형식이 올바르지 않습니다.');
    const response = await fetch('private.enc.json', {cache: 'no-store', credentials: 'omit'});
    if (!response.ok) throw new Error('암호화 개인 대시보드가 아직 게시되지 않았습니다.');
    const envelope = await response.json();
    if (envelope.schema !== 'tradingagents.mobile-encrypted/v1' || envelope.alg !== 'A256GCM') throw new Error('지원하지 않는 암호화 형식입니다.');
    if (envelope.aad !== 'VHJhZGluZ0FnZW50cy9tb2JpbGUtcHJpdmF0ZS92MQ') throw new Error('암호화 context가 올바르지 않습니다.');
    const keyBytes = b64(keyText);
    if (keyBytes.byteLength !== 32) throw new Error('복호화 키 길이가 올바르지 않습니다.');
    const key = await crypto.subtle.importKey('raw', keyBytes, 'AES-GCM', false, ['decrypt']);
    const plaintext = await crypto.subtle.decrypt({name: 'AES-GCM', iv: b64(envelope.nonce), additionalData: b64(envelope.aad), tagLength: 128}, key, b64(envelope.ciphertext));
    const payload = JSON.parse(new TextDecoder().decode(plaintext));
    if (payload.schema !== 'tradingagents.mobile-private/v1') throw new Error('개인 대시보드 payload 계약이 올바르지 않습니다.');
    render(payload);
  }
  start().catch((error) => { status.classList.add('error'); status.textContent = error.message || '개인 대시보드를 열 수 없습니다.'; root.replaceChildren(); });
})();
""".strip()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _write_text(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def _write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def _b64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64url_decode(value: Any) -> bytes:
    text = str(value or "")
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def _sha256_json(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _join_url(base: str, suffix: str) -> str:
    root = str(base or "").strip().rstrip("/")
    return f"{root}/{suffix.lstrip('/')}" if root else suffix


def _escape(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def _css_token(value: Any) -> str:
    return "".join(character.lower() if character.isalnum() else "_" for character in str(value or "missing")).strip("_") or "missing"


def _fmt_price(value: Any) -> str:
    try:
        return f"{float(value):,.2f}"
    except (TypeError, ValueError):
        return "-"


def _fmt_ratio(value: Any) -> str:
    try:
        return f"{float(value):.2f}배"
    except (TypeError, ValueError):
        return "-"
