"""Browser checks for the existing archive's read-only chart and replay view."""
from __future__ import annotations

import argparse
import asyncio
import base64
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import sys
import tempfile
from threading import Thread

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import mobile_layout_regression as layout
from tradingagents.charting.server import make_handler
from tradingagents.execution.experiments import ExperimentRegistry

OUTPUT = None


def fixture(root):
    directory = root / "tickers" / "TEST"
    directory.mkdir(parents=True)
    bars = [{"timestamp": f"2026-10-16T09:{i:02d}:00Z", "available_at": f"2026-10-16T09:{i+1:02d}:00Z",
             "observed_at": "2026-10-16T10:00:00Z", "open": 100+i, "high": 110+i,
             "low": 95+i, "close": 102+i, "volume": 1000+i*100, "session_id": "2026-10-16", "interval": "1m"}
            for i in range(30)]
    payloads = {"chart_evidence.json": {"ticker": "TEST", "bars": bars},
                "analysis.json": {"finished_at": "2026-10-16T10:00:00Z"},
                "execution_contract.json": {"ingested_at": "2026-10-16T10:00:00Z", "structured_levels": [{"price": 110, "label": "계획 진입 기준"}]},
                "execution_update.json": {"execution_asof": "2026-10-16T10:00:00Z", "ingested_at": "2026-10-16T10:00:00Z",
                                          "market_data_asof": "2026-10-16T09:59:00Z", "decision_state": "WAIT",
                                          "reason_codes": ["volume_rule_not_met"]},
                "evidence_ledger.json": {"items": [{"claim": "<img src=x onerror='window.__pwned=true'>", "kind": "fact",
                                          "known_at": "2026-10-16T10:00:00Z", "published_at": "2026-10-16T09:00:00Z", "observed_at": "2026-10-16T10:00:00Z"}]}}
    for name, payload in payloads.items():
        (directory / name).write_text(json.dumps(payload), encoding="utf-8")
    status_path = root / "paper-status.json"
    status_path.write_text(json.dumps({"schema":"tradingagents.paper-runtime/v1","mode":"LOCAL_PAPER_ONLY",
        "enabled":True,"broker_orders_sent":0,"real_orders_enabled":False,"checked_at":"2026-10-16T11:00:00Z",
        "markets":{"kr":{"status":"MARKET_CLOSED","checked_at":"2026-10-16T11:00:00Z",
        "last_quote_at":"2026-10-16T06:29:00Z","last_fill_at":None,"blockers":["MARKET_CLOSED"],
        "ledger_path":"PRIVATE_DO_NOT_DISPLAY","order_counts":{"PENDING":1,"FILLED":0,"REJECTED":0,"CANCELLED":0}}}}))
    registry_path = root / "experiments.sqlite"
    registry = ExperimentRegistry(registry_path, clock=lambda:datetime(2026,10,16,8,tzinfo=timezone.utc))
    registry.register({"id":"paired-test","hypothesis":"검증 전 성과를 만들어 내지 않는 실험 카드", "universe":["TEST"],
        "capital":10000,"currency":"USD","benchmark":"SPY","costs":{"fee_bps":1,"slippage_bps":2},
        "baseline_rules":{"strategy":"fixed"},"ai_rules":{"strategy":"candidate"},
        "training_end":"2026-10-15T20:00:00Z","forward_start":"2026-10-19T13:30:00Z","forward_end":"2026-12-01T21:00:00Z"})
    registry.freeze("paired-test")
    registry.close()
    return status_path, registry_path


async def probe(websocket_url, page_url):
    results, call_id = [], 0
    async with layout.websockets.connect(websocket_url, max_size=8*1024*1024) as socket:
        async def call(method, params=None):
            nonlocal call_id
            call_id += 1
            return await layout._cdp_call(socket, call_id, method, params)

        async def evaluate(expression):
            result = await call("Runtime.evaluate", {"expression": expression, "awaitPromise": True, "returnByValue": True})
            if result.get("exceptionDetails"):
                raise RuntimeError(json.dumps(result["exceptionDetails"]))
            return result.get("result", {}).get("value")

        await call("Page.enable")
        for width in (360, 390, 430, 1440):
            await call("Emulation.setDeviceMetricsOverride", {"width": width, "height": 1000, "deviceScaleFactor": 1, "mobile": width < 600})
            await call("Page.navigate", {"url": page_url})
            for _ in range(100):
                await asyncio.sleep(.1)
                if await evaluate("Boolean(window.reviewSnapshot && document.querySelector('#charts canvas'))"):
                    break
            else:
                raise RuntimeError("Lightweight Charts did not render its snapshot")
            result = await evaluate('''(() => {
              if (window.__pwned || document.querySelector('#facts img')) throw Error('Evidence executed markup');
              if (!document.querySelector('#reasons').textContent.includes('volume_rule_not_met')) throw Error('Engine reasons missing');
              if (window.reviewSnapshot.broker_orders_sent !== 0) throw Error('Viewer is not read only');
              if (!document.querySelector('#paper-health').textContent.includes('휴장·장 종료')) throw Error('Paper status absent');
              if (document.querySelector('#paper-health').textContent.includes('PRIVATE_DO_NOT_DISPLAY')) throw Error('Private path leaked');
              if (!document.querySelector('#experiment-cards').textContent.includes('paired-test')) throw Error('Experiment card absent');
              if (!document.querySelector('#experiment-cards').textContent.includes('수익률·낙폭을 표시하지 않습니다')) throw Error('Unobserved performance fabricated');
              if (document.documentElement.scrollWidth > innerWidth+2) throw Error('Viewport overflow');
              return {width:innerWidth,canvas:document.querySelectorAll('#charts canvas').length,readOnly:true};
            })()''')
            if result["width"] != width:
                raise RuntimeError(f"Mobile layout viewport expanded from {width} to {result['width']}")
            await evaluate("document.querySelector('#condition-text').value='거래대금 100억원 이상 그리고 전일 대비 거래량 1.5배 이상 그리고 거래정지 제외'; compileCondition()")
            if not await evaluate("window.conditionDraft?.status === 'compiled' && document.querySelector('#condition-draft').textContent.includes('저장·활성화 안 됨')"):
                raise RuntimeError("Explicit natural-language draft failed")
            await evaluate("document.querySelector('#condition-text').value='거래량이 많은 종목'; compileCondition()")
            if not await evaluate("window.conditionDraft?.condition === null"):
                raise RuntimeError("Vague condition acquired an invented threshold")
            result["natural_language_draft"] = True
            result["paper_and_experiment_status"] = True
            if OUTPUT and width in (390, 1440):
                shot = await call("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False})
                (OUTPUT / f"investment-review-{width}.png").write_bytes(base64.b64decode(shot["data"]))
            await evaluate("document.querySelector('#asof').value='2026-10-16T08:00:00Z'; loadSnapshot()")
            await evaluate('''(() => {
              if (window.reviewSnapshot.series.length || window.reviewSnapshot.execution_verdict) throw Error('Future data in replay');
              if (document.querySelector('#charts canvas') || document.querySelector('#facts').textContent.includes('<img')) throw Error('Stale future view remained');
              return true;
            })()''')
            result["replay_excludes_future"] = True
            await evaluate("document.querySelector('#asof').value='invalid'; loadSnapshot()")
            if await evaluate("window.reviewSnapshot !== null || document.querySelector('#charts canvas') !== null"):
                raise RuntimeError("Invalid as-of retained a prior view")
            result["invalid_query_clears_view"] = True
            results.append(result)
    return results


def main():
    global OUTPUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    if args.output_dir:
        OUTPUT = args.output_dir
        OUTPUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ta-review-ui-") as temporary:
        root = Path(temporary)
        status_path, registry_path = fixture(root)
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(root, experiment_registry=registry_path, paper_status_path=status_path))
        worker = Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            layout._probe_viewports = probe
            results = layout._run_probe(f"http://127.0.0.1:{server.server_port}/", root / "chrome")
        finally:
            server.shutdown()
            worker.join(timeout=5)
            server.server_close()
    print(json.dumps({"status": "PASSED", "viewports": results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
