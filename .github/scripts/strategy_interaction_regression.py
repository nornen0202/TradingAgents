"""Browser regressions for strategy search, recovery, expiry, and missing data."""
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
            item["rows"].append(row)
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
