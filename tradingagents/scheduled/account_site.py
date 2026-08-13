from __future__ import annotations

import html
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PUBLIC_ACCOUNT_SCHEMA = "tradingagents.public-account-snapshot/v1"
_MARKET_META = {
    "kr": {"code": "KR", "label_ko": "국내", "label_en": "Korea"},
    "us": {"code": "US", "label_ko": "해외", "label_en": "Overseas"},
}


def build_public_account_site(
    *,
    site_dir: Path,
    manifests: list[dict[str, Any]],
    public_base_url: str = "",
) -> dict[str, Any]:
    """Publish an intentionally small, identifier-free account snapshot surface."""

    generated_at = datetime.now(timezone.utc).isoformat()
    markets = {
        market: _latest_public_market_snapshot(manifests, market=market)
        for market in ("kr", "us")
    }
    base_url = str(public_base_url or "").rstrip("/")
    page_url = f"{base_url}/account/" if base_url else "account/index.html"
    json_url = f"{base_url}/account/public.json" if base_url else "account/public.json"
    payload = {
        "schema": PUBLIC_ACCOUNT_SCHEMA,
        "generated_at": generated_at,
        "page_url": page_url,
        "json_url": json_url,
        "currency_note": "All monetary values are normalized to KRW by the KIS account adapter.",
        "privacy": {
            "public_fields": [
                "holding ticker and name",
                "quantity and sellable quantity",
                "average cost and current price",
                "purchase amount and market value",
                "unrealized profit/loss and return",
                "cash and total equity summaries",
            ],
            "excluded_fields": [
                "account number",
                "customer identifier",
                "snapshot identifier",
                "pending orders",
                "broker raw response",
            ],
        },
        "markets": markets,
    }

    account_dir = Path(site_dir) / "account"
    account_dir.mkdir(parents=True, exist_ok=True)
    _write_json(account_dir / "public.json", payload)
    (account_dir / "index.html").write_text(_render_account_page(payload), encoding="utf-8")
    (account_dir / "llms.txt").write_text(_render_llms_text(payload), encoding="utf-8")
    (Path(site_dir) / "robots.txt").write_text("User-agent: *\nAllow: /\n", encoding="utf-8")
    return payload


def _latest_public_market_snapshot(
    manifests: list[dict[str, Any]],
    *,
    market: str,
) -> dict[str, Any]:
    meta = _MARKET_META[market]
    for manifest in manifests:
        if _manifest_market(manifest) != meta["code"]:
            continue
        run_dir_value = manifest.get("_run_dir")
        if not run_dir_value:
            continue
        snapshot_path = Path(str(run_dir_value)) / "portfolio-private" / "account_snapshot.json"
        if not snapshot_path.is_file():
            continue
        try:
            snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(snapshot, dict):
            continue
        health = str(snapshot.get("snapshot_health") or "VALID").strip().upper()
        if health in {"INVALID", "INVALID_SNAPSHOT", "WATCHLIST_ONLY"}:
            continue
        return _public_market_snapshot(snapshot, manifest=manifest, market=market)

    return {
        **meta,
        "status": "unavailable",
        "as_of": None,
        "run_id": None,
        "snapshot_health": "UNAVAILABLE",
        "currency": "KRW",
        "summary": _empty_summary(),
        "positions": [],
    }


def _manifest_market(manifest: dict[str, Any]) -> str:
    settings = manifest.get("settings") if isinstance(manifest.get("settings"), dict) else {}
    return str(settings.get("market") or manifest.get("market") or "").strip().upper()


def _public_market_snapshot(
    snapshot: dict[str, Any],
    *,
    manifest: dict[str, Any],
    market: str,
) -> dict[str, Any]:
    positions: list[dict[str, Any]] = []
    source_positions = snapshot.get("positions") if isinstance(snapshot.get("positions"), list) else []
    for raw in source_positions:
        if not isinstance(raw, dict):
            continue
        ticker = _text(raw.get("canonical_ticker"))
        if not ticker:
            continue
        quantity = _number(raw.get("quantity"))
        sellable_quantity = _number(raw.get("available_qty"))
        average_cost = _integer(raw.get("avg_cost_krw"))
        current_price = _integer(raw.get("market_price_krw"))
        market_value = _integer(raw.get("market_value_krw"))
        purchase_amount = int(round(average_cost * quantity))
        unrealized_pnl = _integer(raw.get("unrealized_pnl_krw"))
        if not unrealized_pnl and market_value and purchase_amount:
            unrealized_pnl = market_value - purchase_amount
        unrealized_return = (unrealized_pnl / purchase_amount * 100.0) if purchase_amount > 0 else None
        positions.append(
            {
                "ticker": ticker,
                "code": _text(raw.get("broker_symbol")) or ticker,
                "name": _text(raw.get("display_name")) or ticker,
                "quantity": quantity,
                "sellable_quantity": sellable_quantity,
                "average_cost_krw": average_cost,
                "current_price_krw": current_price,
                "purchase_amount_krw": purchase_amount,
                "market_value_krw": market_value,
                "unrealized_pnl_krw": unrealized_pnl,
                "unrealized_return_pct": round(unrealized_return, 4) if unrealized_return is not None else None,
            }
        )
    positions.sort(key=lambda item: (-int(item["market_value_krw"]), str(item["ticker"])))

    total_purchase = sum(int(item["purchase_amount_krw"]) for item in positions)
    total_market_value = sum(int(item["market_value_krw"]) for item in positions)
    total_pnl = sum(int(item["unrealized_pnl_krw"]) for item in positions)
    if positions and total_market_value - total_purchase != total_pnl:
        total_pnl = total_market_value - total_purchase
    total_return = (total_pnl / total_purchase * 100.0) if total_purchase > 0 else None
    account_value = _integer(snapshot.get("account_value_krw") or snapshot.get("total_equity_krw"))
    meta = _MARKET_META[market]
    return {
        **meta,
        "status": "available",
        "as_of": _text(snapshot.get("as_of")) or None,
        "run_id": _text(manifest.get("run_id")) or None,
        "snapshot_health": _text(snapshot.get("snapshot_health")) or "VALID",
        "currency": "KRW",
        "summary": {
            "position_count": len(positions),
            "total_purchase_amount_krw": total_purchase,
            "total_market_value_krw": total_market_value,
            "total_unrealized_pnl_krw": total_pnl,
            "total_unrealized_return_pct": round(total_return, 4) if total_return is not None else None,
            "settled_cash_krw": _integer(snapshot.get("settled_cash_krw")),
            "available_cash_krw": _integer(snapshot.get("available_cash_krw")),
            "buying_power_krw": _integer(snapshot.get("buying_power_krw")),
            "total_equity_krw": account_value,
        },
        "positions": positions,
    }


def _empty_summary() -> dict[str, Any]:
    return {
        "position_count": 0,
        "total_purchase_amount_krw": 0,
        "total_market_value_krw": 0,
        "total_unrealized_pnl_krw": 0,
        "total_unrealized_return_pct": None,
        "settled_cash_krw": 0,
        "available_cash_krw": 0,
        "buying_power_krw": 0,
        "total_equity_krw": 0,
    }


def _number(value: Any) -> float:
    try:
        number = float(value or 0)
    except (TypeError, ValueError):
        return 0.0
    return number if math.isfinite(number) else 0.0


def _integer(value: Any) -> int:
    return int(round(_number(value)))


def _text(value: Any) -> str:
    return str(value or "").strip()


def _render_account_page(payload: dict[str, Any]) -> str:
    markets = payload["markets"]
    available = [key for key in ("kr", "us") if markets[key]["status"] == "available"]
    initial = available[0] if available else "kr"
    panels = "".join(_render_market_panel(key, markets[key], initial=initial) for key in ("kr", "us"))
    dataset = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": "TradingAgents public account snapshot",
        "dateModified": payload["generated_at"],
        "url": payload["page_url"],
        "distribution": {
            "@type": "DataDownload",
            "encodingFormat": "application/json",
            "contentUrl": payload["json_url"],
        },
    }
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="국내·해외 주식 계좌의 최신 공개 보유 현황과 평가손익">
  <meta name="robots" content="index,follow">
  <link rel="alternate" type="application/json" href="public.json" title="Public account snapshot JSON">
  <link rel="stylesheet" href="../assets/style.css">
  <title>공개 주식 계좌 현황 · TradingAgents</title>
  <script type="application/ld+json">{json.dumps(dataset, ensure_ascii=False).replace('</', '<\\/')}</script>
</head>
<body>
  <main class="shell account-snapshot-shell">
    <nav class="breadcrumbs"><a href="../index.html">Home</a><a href="public.json">JSON</a><a href="llms.txt">AI 안내</a></nav>
    <section class="account-snapshot-hero">
      <div>
        <p class="eyebrow">PUBLIC ACCOUNT SNAPSHOT</p>
        <h1>주식 잔고 · 손익</h1>
        <p class="subtitle">국내·해외 계좌를 분리해 보여주는 최신 읽기 전용 스냅샷입니다.</p>
      </div>
      <p class="account-generated">페이지 생성<br><strong>{_escape(_format_as_of(payload['generated_at']))}</strong></p>
    </section>
    <div class="account-tabs" role="tablist" aria-label="시장 선택">
      <button type="button" role="tab" data-market="kr" aria-selected="{'true' if initial == 'kr' else 'false'}">국내</button>
      <button type="button" role="tab" data-market="us" aria-selected="{'true' if initial == 'us' else 'false'}">해외</button>
    </div>
    {panels}
    <section class="account-disclosure">
      <strong>공개 범위 안내</strong>
      <p>보유 종목과 평가정보는 공개됩니다. 계좌번호, 고객 식별정보, 스냅샷 ID, 미체결 주문, 브로커 원문 응답은 게시하지 않습니다. 모든 금액은 KIS 어댑터가 원화로 정규화한 값입니다.</p>
      <p><a href="public.json">앱·AI용 공개 JSON</a> · 스키마: <code>{PUBLIC_ACCOUNT_SCHEMA}</code></p>
    </section>
  </main>
  <script>
    (() => {{
      const buttons = [...document.querySelectorAll('[data-market]')];
      const panels = [...document.querySelectorAll('[data-market-panel]')];
      const select = (market) => {{
        buttons.forEach((button) => button.setAttribute('aria-selected', String(button.dataset.market === market)));
        panels.forEach((panel) => panel.hidden = panel.dataset.marketPanel !== market);
        history.replaceState(null, '', `#${{market}}`);
      }};
      buttons.forEach((button) => button.addEventListener('click', () => select(button.dataset.market)));
      const requested = location.hash.slice(1).toLowerCase();
      if (requested === 'kr' || requested === 'us') select(requested);
    }})();
  </script>
</body>
</html>
"""


def _render_market_panel(market: str, value: dict[str, Any], *, initial: str) -> str:
    hidden = "" if market == initial else " hidden"
    if value["status"] != "available":
        content = "<div class='account-empty'>아직 게시할 수 있는 유효 계좌 스냅샷이 없습니다.</div>"
    else:
        content = _render_summary(value["summary"]) + _render_positions(value["positions"])
    return f"""
    <section class="account-market-panel" data-market-panel="{market}"{hidden}>
      <div class="account-panel-head">
        <div><p class="eyebrow">{_escape(value['label_en'])}</p><h2>{_escape(value['label_ko'])} 주식</h2></div>
        <p>기준 시각<br><strong>{_escape(_format_as_of(value.get('as_of')))}</strong></p>
      </div>
      {content}
    </section>
    """


def _render_summary(summary: dict[str, Any]) -> str:
    pnl = int(summary["total_unrealized_pnl_krw"])
    return_pct = summary.get("total_unrealized_return_pct")
    return f"""
      <div class="account-kpis">
        {_kpi("총 평가금액", _won(summary['total_market_value_krw']))}
        {_kpi("총 매입금액", _won(summary['total_purchase_amount_krw']))}
        {_kpi("평가손익", _signed_won(pnl), _tone(pnl))}
        {_kpi("수익률", _pct(return_pct), _tone(return_pct))}
        {_kpi("보유 종목", f"{int(summary['position_count']):,}개")}
        {_kpi("총 계좌 평가액", _won(summary['total_equity_krw']))}
      </div>
    """


def _kpi(label: str, value: str, tone: str = "") -> str:
    return f"<article><span>{_escape(label)}</span><strong class='{tone}'>{_escape(value)}</strong></article>"


def _render_positions(positions: list[dict[str, Any]]) -> str:
    if not positions:
        return "<div class='account-empty'>보유 종목이 없습니다.</div>"
    rows = []
    for position in positions:
        pnl = int(position["unrealized_pnl_krw"])
        rows.append(
            f"""
            <tr>
              <th scope="row"><strong>{_escape(position['name'])}</strong><span>{_escape(position['ticker'])}</span></th>
              <td class="{_tone(pnl)}"><strong>{_signed_won(pnl)}</strong><span>{_pct(position.get('unrealized_return_pct'))}</span></td>
              <td><strong>{_quantity(position['quantity'])}</strong><span>{_quantity(position['sellable_quantity'])}</span></td>
              <td><strong>{_won(position['current_price_krw'])}</strong><span>{_won(position['average_cost_krw'])}</span></td>
              <td><strong>{_won(position['market_value_krw'])}</strong><span>{_won(position['purchase_amount_krw'])}</span></td>
            </tr>
            """
        )
    return f"""
      <div class="account-holdings-table">
        <table>
          <thead><tr>
            <th>종목명<br><span>티커</span></th>
            <th>평가손익<br><span>수익률</span></th>
            <th>보유수량<br><span>매도가능</span></th>
            <th>현재가<br><span>평균단가</span></th>
            <th>평가금액<br><span>매입금액</span></th>
          </tr></thead>
          <tbody>{''.join(rows)}</tbody>
        </table>
      </div>
    """


def _render_llms_text(payload: dict[str, Any]) -> str:
    return "\n".join(
        (
            "# TradingAgents Public Account Snapshot",
            "",
            f"Canonical page: {payload['page_url']}",
            f"Machine-readable JSON: {payload['json_url']}",
            f"Schema: {PUBLIC_ACCOUNT_SCHEMA}",
            "Markets: markets.kr (domestic), markets.us (overseas)",
            "Currency: monetary fields ending in _krw are normalized Korean won values.",
            "Privacy: account/customer identifiers, pending orders, snapshot IDs, and broker raw responses are excluded.",
            "",
        )
    )


def _format_as_of(value: Any) -> str:
    text = _text(value)
    if not text:
        return "데이터 없음"
    return text.replace("T", " ")[:19]


def _won(value: Any) -> str:
    return f"₩{_integer(value):,}"


def _signed_won(value: Any) -> str:
    number = _integer(value)
    sign = "+" if number > 0 else ""
    return f"{sign}₩{number:,}"


def _pct(value: Any) -> str:
    if value is None:
        return "-"
    number = _number(value)
    sign = "+" if number > 0 else ""
    return f"{sign}{number:.2f}%"


def _quantity(value: Any) -> str:
    number = _number(value)
    return f"{number:,.4f}".rstrip("0").rstrip(".")


def _tone(value: Any) -> str:
    number = _number(value)
    return "account-positive" if number > 0 else "account-negative" if number < 0 else "account-neutral"


def _escape(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
