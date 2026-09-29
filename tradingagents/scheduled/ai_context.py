"""Small, static AI readers projected ONLY from already-published public surfaces."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "tradingagents.ai-context/v1"
MIRROR_BASE = "https://raw.githubusercontent.com/nornen0202/TradingAgents/public-context"
ROW_FIELDS = (
    "ticker", "display_name", "is_held", "strategy_code", "strategy_ko", "last_price",
    "market_data_asof", "session_vwap", "relative_volume", "spread_bps", "day_high", "day_low",
    "execution_condition_ko", "risk_condition_ko", "decision_state_ko",
)
QUALITY_FIELDS = ("execution_ready", "current_execution_promotion", "generated_in_current_run", "row_valid_until")
POSITION_FIELDS = ("ticker", "name", "quantity", "sellable_quantity", "average_cost_krw",
                   "current_price_krw", "market_value_krw", "unrealized_pnl_krw")
SUMMARY_FIELDS = ("position_count", "total_purchase_amount_krw", "total_market_value_krw",
                  "total_unrealized_pnl_krw", "settled_cash_krw", "available_cash_krw",
                  "buying_power_krw", "total_equity_krw")
CLOCK_FIELDS = ("producer_run_id", "producer_finished_at", "analysis_run_id", "analysis_completed_at",
                "analysis_trade_date_oldest", "analysis_trade_date_latest", "analysis_lineage_status",
                "market_data_oldest_at", "market_data_latest_at", "market_data_status")


def project(value: Any, fields: tuple[str, ...]) -> dict:
    value = value if isinstance(value, dict) else {}
    return {key: value.get(key) for key in fields}


def render_context(market: str, strategy: dict, account: dict, status: dict, *, generated_at: str) -> str:
    return render_payload(public_context(market, strategy, account, status, generated_at=generated_at))


def public_context(market: str, strategy: dict, account: dict, status: dict, *, generated_at: str) -> dict:
    rows = strategy.get("rows") or []
    account_view = project(account, ("status", "as_of", "snapshot_health", "currency"))
    account_view["summary"] = project(account.get("summary"), SUMMARY_FIELDS)
    account_view["positions"] = [project(row, POSITION_FIELDS) for row in account.get("positions", [])]
    selected_rows = []
    published_holdings = {row.get("ticker") for row in account_view["positions"]}
    for row in rows:
        if row.get("is_held") is True and row.get("ticker") not in published_holdings:
            continue
        selected = project(row, ROW_FIELDS)
        selected["quality_at_build"] = project(row.get("quality"), QUALITY_FIELDS)
        selected_rows.append(selected)
    report = project(status.get("integrated_report"), ("published_at", "as_of", "markdown_url", "readable_url"))
    return {"schema": SCHEMA, "market": market, "generated_at": generated_at,
            "freshness_receipt": project(strategy.get("freshness_receipt"), CLOCK_FIELDS),
            "account": account_view, "rows": selected_rows, "report": report}


def render_payload(payload: dict) -> str:
    market, generated_at = payload["market"], payload["generated_at"]
    account_view, selected_rows, report = payload["account"], payload["rows"], payload["report"]
    parts = [
        f"# TradingAgents {market.upper()} 최신 공개 입력",
        f"schema: {SCHEMA}\n문서 생성: {generated_at}",
        "이 문서는 이미 공개된 자료의 축약 전사이며 새 분석·주문 승인이 아닙니다. "
        "원분석 거래일(완료 일봉), 분석 완료, 장중 시세, 계좌 관측, 문서 생성은 서로 다른 시각입니다. "
        "휴장·주말의 마지막 완료 거래일을 장애로 단정하지 마세요. null은 미확인이지 0이 아닙니다. "
        "빌드 당시 실행 상태는 현재 상태가 아니며 row_valid_until과 현재 세션을 다시 확인해야 합니다. "
        "현재 문서를 읽지 못하면 과거 대화의 계좌·한도를 최신 사실로 재사용하지 마세요.",
        "통화: 계좌 요약·평단·평가액의 *_krw는 모두 원화입니다. "
        "종목별 last_price·VWAP·고저가는 KR 시장 KRW, US 시장 USD이며 서로 직접 비교하지 마세요.",
        "## 원본 링크",
        "\n".join(f"- https://nornen0202.github.io/TradingAgents/{path}" for path in
                  ("account/public.json", "mobile/strategy.json", f"work/v1/{market}/status.json")),
        "## 원분석·시세 시각\n```json\n" + json.dumps(payload["freshness_receipt"], ensure_ascii=False, indent=2) + "\n```",
        "## 계좌 관측값 — 계좌번호·주문·인증정보 제외\n```json\n" + json.dumps(account_view, ensure_ascii=False, indent=2) + "\n```",
        "## 종목별 원안과 조건 — 현재 재검증 필요",
    ]
    for row in selected_rows:
        parts.append("```json\n" + json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n```")
    parts.append("## 별도로 발행된 Work 보고서 — 현재 입력과 시각이 다를 수 있음\n```json\n" + json.dumps(report, ensure_ascii=False, indent=2) + "\n```")
    return "\n\n".join(parts) + "\n"


def build_ai_context(site_dir: Path, *, now: datetime | None = None) -> dict:
    def read(relative: str) -> dict:
        path = site_dir / relative
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}

    strategy = read("mobile/strategy.json")
    account = read("account/public.json")
    stamp = (now or datetime.now(timezone.utc)).isoformat()
    manifest: dict = {"schema": SCHEMA, "generated_at": stamp, "files": {}, "mirror_base": MIRROR_BASE}
    for market in ("kr", "us"):
        market_strategy = (strategy.get("markets") or {}).get(market) or {}
        payload = public_context(market, market_strategy, (account.get("markets") or {}).get(market) or {},
                                 read(f"work/v1/{market}/status.json"), generated_at=stamp)
        body = render_payload(payload)
        content = body.encode("utf-8")
        if len(content) > 250_000:
            raise ValueError(f"AI reader exceeds safe budget: {market}")
        relative = f"{market}/latest.md"
        target = site_dir / "ai" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        manifest["files"][relative] = {"sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content)}
        for extension, data in (("txt", content), ("json", (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))):
            relative = f"{market}/latest.{extension}"
            (site_dir / "ai" / relative).write_bytes(data)
            manifest["files"][relative] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    (site_dir / "ai" / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest
