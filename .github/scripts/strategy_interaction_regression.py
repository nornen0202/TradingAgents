"""Browser regressions for strategy filtering and account-sized trade plans."""
from __future__ import annotations

import asyncio
import copy
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import mobile_layout_regression as layout


def fixture() -> dict[str, Any]:
    payload = layout._strategy_fixture()
    for market, item in payload["markets"].items():
        template = item["rows"][0]
        template["price_change_pct"] = -2
        for ticker, change in (("BETA", 3), ("ALPHA", 1), ("MISSING", None)):
            row = copy.deepcopy(template)
            row.update(ticker=ticker, display_name=ticker, is_held=False,
                       universe_role="WATCHLIST", price_change_pct=change)
            if ticker == "MISSING":
                row.update(display_name='<img src=x onerror="alert(1)">', last_price=None, relative_volume=None)
                row["portfolio_action"]["confidence"] = None
            if ticker in {"ALPHA", "BETA"}:
                row["thesis"] = {"stance": "BUY" if ticker == "ALPHA" else "SELL", "entry_conditions": ["Close AND volume must confirm"], "invalidation_conditions": ["Risk below 90 after close"]}
            if ticker == "BETA":
                row.update(is_held=True, universe_role="HOLDING", held_quantity=3)
            item["rows"].append(row)
        currency = "KRW" if market == "kr" else "USD"
        unit = 1000 if market == "kr" else 1
        plans = []
        for ticker, action, quantity, status in (
            (template["ticker"], "BUY", 0, "1주 매수 예산 부족"),
            ("ALPHA", "BUY", 2, "조건 충족 시 검토"),
            ("BETA", "SELL", 3, "보유 수량 이내 축소"),
            ("MISSING", "BUY", None, "가격·수량 근거 확인 필요"),
        ):
            known = quantity is not None
            gross = quantity * 101.5 * unit if known else None
            fees = gross * (0.00147 if market == "kr" else 0.0025) if known else None
            plans.append({
                "id": f"{market}-{ticker}-conditional",
                "ticker": ticker,
                "display_name": ticker,
                "action": action,
                "action_label": "매도·축소" if action == "SELL" else "매수",
                "action_now": "HOLD" if ticker in {template["ticker"], "BETA"} else "WAIT",
                "phase": "CONDITIONAL",
                "quantity": quantity,
                "price_low": 99 * unit if known else None,
                "price_high": 101.5 * unit if known else None,
                "price_kind": "TRIGGER_RANGE" if known else "UNAVAILABLE",
                "price_comparator": ">=" if known else None,
                "price_confirmation": "CLOSE" if known else None,
                "currency": currency,
                "estimated_gross_low": quantity * 99 * unit if known else None,
                "estimated_gross_high": gross,
                "estimated_fees": fees,
                "estimated_net_cash": (
                    gross - fees if action == "SELL" else -(gross + fees)
                ) if known else None,
                "status": "UNSIZED" if not known else "NO_QUANTITY" if quantity == 0 else "CONDITIONAL",
                "status_label": status,
                "condition": "종가·거래량 조건을 모두 확인",
                "trigger_conditions": [
                    "종가·거래량 조건을 모두 확인",
                    "장중 가격과 종가 조건을 혼동하지 않고 확인합니다. " * 12 + "긴 조건의 마지막 확인 문구",
                    "변경된 현금과 보유 수량으로 다시 계산",
                    "네 번째 조건도 생략하지 않음",
                    '<img src=x onerror="alert(1)">',
                ],
                "reasons": [status, "추가 산출 근거의 마지막 확인 문구"],
                "held_quantity": 3 if ticker == "BETA" else 0,
                "account_asof": payload["generated_at"],
                "price_asof": payload["generated_at"],
                "quote_asof": payload["generated_at"],
                "valid_until": item["guardrails"]["valid_until"],
                "order_ready": False,
            })
        item["trade_plan"] = {
            "schema": "tradingagents.manual-trade-plan/v1",
            "market": market.upper(),
            "currency": currency,
            "account_asof": payload["generated_at"],
            "account_fresh": True,
            "rows": plans,
            "summary": {"row_count": 4, "buy_count": 3, "sell_count": 1, "sized_count": 2},
            "assumptions": ["입력 계좌 기준 검토 수량", "실제 주문은 직접 확인 후 실행"],
        }
    return payload


async def probe(websocket_url: str, page_url: str) -> list[dict[str, Any]]:
    results = []
    call_id = 0
    async with layout.websockets.connect(websocket_url, max_size=8 * 1024 * 1024) as socket:
        async def call(method, params=None):
            nonlocal call_id
            call_id += 1
            return await layout._cdp_call(socket, call_id, method, params)

        await call("Page.enable")
        await call("Page.addScriptToEvaluateOnNewDocument", {"source":
            "window.__auditOffset = 0; const realNow = Date.now.bind(Date); "
            "Date.now = () => realNow() + window.__auditOffset;"})
        for width in (360, 390, 430, 1440):
            await call("Emulation.setDeviceMetricsOverride", {
                "width": width, "height": 1000, "deviceScaleFactor": 1, "mobile": width < 600,
            })
            await call("Page.navigate", {"url": page_url})
            for _ in range(100):
                await asyncio.sleep(.1)
                value = await call("Runtime.evaluate", {
                    "expression": "document.querySelectorAll('.action-card').length", "returnByValue": True,
                })
                if value.get("result", {}).get("value") == 4:
                    break
            else:
                raise RuntimeError("Strategy did not render")
            value = await call("Runtime.evaluate", {
                "expression": Path(__file__).with_name("strategy_interaction_checks.js").read_text(encoding="utf-8"),
                "awaitPromise": True, "returnByValue": True,
            })
            if value.get("exceptionDetails"):
                raise RuntimeError(json.dumps(value["exceptionDetails"], ensure_ascii=False))
            results.append(value["result"]["value"])
            await call("Page.navigate", {"url": page_url + "&direction=sell"})
            for _ in range(100):
                await asyncio.sleep(.05)
                value = await call("Runtime.evaluate", {
                    "expression": "(() => { const panel = document.querySelector('.market-panel:not([hidden])'); if (!panel || !panel.querySelector('.action-card')) return false; const rows = panel.querySelectorAll('.action-card:not([hidden])'); return rows.length === 1 && rows[0].dataset.ticker === 'BETA' && panel.querySelector('[data-direction-target=sell]').getAttribute('aria-pressed') === 'true' && panel.querySelectorAll('.strategy-summary tbody tr').length === 1; })()",
                    "returnByValue": True,
                })
                if value.get("result", {}).get("value") is True:
                    break
            else:
                raise RuntimeError("Reloaded direction deep link did not restore its filtered table")
            results[-1]["direction_deep_link_restored"] = True
    return results


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="tradingagents-strategy-ui-") as temp:
        root = Path(temp)
        site = root / "site"
        layout.build_mobile_site(site_dir=site, archive_dir=root / "archive")
        (site / "mobile/strategy.json").write_text(json.dumps(fixture(), ensure_ascii=False), encoding="utf-8")
        # Reuse the existing isolated, headless browser launcher and its retry.
        layout._probe_viewports = probe
        with layout._serve(site) as page_url:
            results = layout._run_probe(page_url, root / "chrome")
    print(json.dumps({"status": "PASSED", "viewports": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
