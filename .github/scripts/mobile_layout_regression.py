from __future__ import annotations

import asyncio
import json
import os
import shutil
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Iterator

import websockets

from tradingagents.scheduled.mobile_site import STRATEGY_SCHEMA, build_mobile_site


VIEWPORTS = (360, 390, 430)


def _strategy_fixture() -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    valid_until = (now + timedelta(hours=2)).isoformat()
    markets = {}
    for market, ticker in (("kr", "005930.KS"), ("us", "NVDA")):
        run_id = f"layout-{market}"
        markets[market] = {
            "market": market.upper(),
            "run_id": run_id,
            "source_health": "OK",
            "manifest_status": "success",
            "decision_ready": False,
            "conditional_strategy_ready": True,
            "guardrails": {
                "valid_until": valid_until,
                "expired_at_build": False,
                "conditional_strategy_ready": True,
            },
            "quality": {"decision_ready": False, "conditional_strategy_ready": True},
            "universe_coverage": {
                "status": "COMPLETE",
                "complete": True,
                "ticker_universe_mode": "config_plus_account",
                "account_snapshot_status": "loaded",
                "expected_analysis_count": 1,
                "analysis_total_count": 1,
                "analysis_successful_count": 1,
                "missing_holding_count": 0,
                "missing_watchlist_count": 0,
                "missing_analysis_count": 0,
                "analysis_failed_count": 0,
            },
            "provenance": {
                key: run_id
                for key in (
                    "surface_run_id",
                    "manifest_run_id",
                    "universe_source_run_id",
                    "decision_bundle_run_id",
                    "analysis_source_run_id",
                    "execution_source_run_id",
                )
            },
            "role_counts": {"HOLDING": 1, "WATCHLIST": 0, "NEW_CANDIDATE": 0},
            "rows": [
                {
                    "ticker": ticker,
                    "display_name": "아주 긴 종목명과 조건에서도 모바일 카드가 가로로 넘치지 않는지 검증",
                    "is_held": True,
                    "universe_role": "HOLDING",
                    "last_price": 1234567,
                    "market_data_asof": now.isoformat(),
                    "session_vwap": 1220000,
                    "vwap_position_ko": "거래량가중평균가격 위",
                    "relative_volume": 1.42,
                    "strategy_code": "HOLD",
                    "strategy_ko": "조건을 확인하며 보유",
                    "execution_condition_ko": (
                        "종가가 기준가격을 상회하고 상대거래량 1.2배 이상과 VWAP 지지를 동시에 확인"
                    ),
                    "risk_condition_ko": "무효화 가격 이탈 또는 거래량 동반 추세 훼손",
                    "quality": {
                        "row_mode": "CONDITIONAL",
                        "conditional_strategy_ready": True,
                        "row_valid_until": valid_until,
                    },
                    "portfolio_action": {
                        "action_now": "HOLD",
                        "action_if_triggered": "ADD_IF_TRIGGERED",
                        "risk_action": "REDUCE_RISK",
                        "trigger_conditions": [
                            "종가 기준가격 상회",
                            "상대거래량 1.2배 이상",
                            "당일 VWAP 위에서 30분 이상 유지",
                        ],
                        "invalidation_condition": "무효화 가격을 종가로 이탈",
                        "delta_krw_now": 0,
                        "delta_krw_if_triggered": 1000000,
                        "target_weight_if_triggered": 0.08,
                        "confidence": 0.78,
                    },
                }
            ],
        }
    return {
        "schema": STRATEGY_SCHEMA,
        "generated_at": now.isoformat(),
        "markets": markets,
    }


class _QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, _format: str, *_args: Any) -> None:
        return


@contextmanager
def _serve(directory: Path) -> Iterator[str]:
    handler = lambda *args, **kwargs: _QuietHandler(  # noqa: E731
        *args,
        directory=str(directory),
        **kwargs,
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/mobile/private.html?market=kr"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def _chrome_binary() -> Path:
    configured = os.getenv("CHROME_BIN", "").strip()
    candidates = [
        Path(configured) if configured else None,
        Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
        Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
        Path("/usr/bin/google-chrome"),
        Path("/usr/bin/chromium"),
        Path("/usr/bin/chromium-browser"),
    ]
    for candidate in candidates:
        if candidate and candidate.is_file():
            return candidate
    for name in ("google-chrome", "chrome", "chromium", "chromium-browser"):
        resolved = shutil.which(name)
        if resolved:
            return Path(resolved)
    raise RuntimeError("Chrome/Chromium was not found for mobile layout regression")


def _devtools_endpoint(profile: Path, *, timeout_seconds: float = 15.0) -> tuple[int, str]:
    marker = profile / "DevToolsActivePort"
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if marker.is_file():
            lines = marker.read_text(encoding="utf-8").splitlines()
            if len(lines) >= 2:
                return int(lines[0]), lines[1]
        time.sleep(0.1)
    raise RuntimeError("Chrome DevToolsActivePort was not created")


async def _cdp_call(socket: Any, call_id: int, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    await socket.send(json.dumps({"id": call_id, "method": method, "params": params or {}}))
    while True:
        message = json.loads(await asyncio.wait_for(socket.recv(), timeout=15))
        if message.get("id") == call_id:
            if message.get("error"):
                raise RuntimeError(f"CDP {method} failed: {message['error']}")
            return message.get("result") or {}


async def _probe_viewports(websocket_url: str, page_url: str) -> list[dict[str, Any]]:
    results = []
    call_id = 0
    async with websockets.connect(websocket_url, max_size=8 * 1024 * 1024) as socket:
        for width in VIEWPORTS:
            call_id += 1
            await _cdp_call(
                socket,
                call_id,
                "Emulation.setDeviceMetricsOverride",
                {
                    "width": width,
                    "height": 900,
                    "deviceScaleFactor": 1,
                    "mobile": True,
                    "screenWidth": width,
                    "screenHeight": 900,
                },
            )
            call_id += 1
            await _cdp_call(socket, call_id, "Page.navigate", {"url": page_url})
            deadline = time.monotonic() + 15
            measurement = None
            while time.monotonic() < deadline:
                await asyncio.sleep(0.2)
                call_id += 1
                response = await _cdp_call(
                    socket,
                    call_id,
                    "Runtime.evaluate",
                    {
                        "returnByValue": True,
                        "expression": """
                        (() => {
                          const cards = [...document.querySelectorAll('.action-card')];
                          const visible = [...document.querySelectorAll('body *')].filter((element) => {
                            const style = getComputedStyle(element);
                            const rect = element.getBoundingClientRect();
                            return style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0;
                          });
                          const overflow = visible.filter((element) => {
                            const rect = element.getBoundingClientRect();
                            return rect.left < -1 || rect.right > window.innerWidth + 1;
                          }).map((element) => `${element.tagName}.${element.className}`.slice(0, 120));
                          const heading = document.querySelector('.market-head h2');
                          const headingRange = document.createRange();
                          if (heading) headingRange.selectNodeContents(heading);
                          const headingLineCount = heading
                            ? [...headingRange.getClientRects()].filter((rect) => rect.width > 0).length
                            : 0;
                          return {
                            ready: cards.length > 0,
                            innerWidth: window.innerWidth,
                            visualWidth: window.visualViewport && window.visualViewport.width,
                            documentScrollWidth: document.documentElement.scrollWidth,
                            bodyScrollWidth: document.body.scrollWidth,
                            cardCount: cards.length,
                            overflow: overflow.slice(0, 20),
                            headingLineCount,
                            hasStrategyDirection: document.body.innerText.includes('분석 시점 전략 방향'),
                            hasExecutionStatus: document.body.innerText.includes('현재 실행 상태'),
                            hasEntryCondition: document.body.innerText.includes('전략 발동 조건'),
                            hasTriggeredAction: document.body.innerText.includes('발동 조건 충족 시 행동'),
                            hasInvalidation: document.body.innerText.includes('악화·손실 제한 조건'),
                            hasInvalidationAction: document.body.innerText.includes('악화 조건 충족 시 행동'),
                          };
                        })()
                        """,
                    },
                )
                measurement = ((response.get("result") or {}).get("value"))
                if isinstance(measurement, dict) and measurement.get("ready"):
                    break
            if not isinstance(measurement, dict) or not measurement.get("ready"):
                raise RuntimeError(f"Mobile strategy cards did not render at {width}px")
            measurement["requestedWidth"] = width
            results.append(measurement)
    return results


def _run_probe_once(page_url: str, profile: Path) -> list[dict[str, Any]]:
    chrome = _chrome_binary()
    process = subprocess.Popen(
        [
            str(chrome),
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            "--remote-debugging-port=0",
            "--remote-allow-origins=*",
            f"--user-data-dir={profile}",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        port, browser_path = _devtools_endpoint(profile, timeout_seconds=30.0)
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=5) as response:
            targets = json.loads(response.read().decode("utf-8"))
        page = next((target for target in targets if target.get("type") == "page"), None)
        if page is None:
            raise RuntimeError(f"Chrome page target unavailable: {browser_path}")
        return asyncio.run(_probe_viewports(str(page["webSocketDebuggerUrl"]), page_url))
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def _run_probe(page_url: str, profile: Path) -> list[dict[str, Any]]:
    """Run the browser probe with one clean-profile startup retry.

    Hosted Windows runners occasionally launch Chrome too slowly to create
    DevToolsActivePort on the first attempt. A separate profile prevents a
    half-created first launch from poisoning the retry, while deterministic
    layout failures still surface after the second attempt.
    """

    failures: list[str] = []
    for attempt in range(1, 3):
        attempt_profile = profile.parent / f"{profile.name}-attempt-{attempt}"
        try:
            return _run_probe_once(page_url, attempt_profile)
        except (OSError, RuntimeError, TimeoutError, urllib.error.URLError) as exc:
            failures.append(f"attempt {attempt}: {exc}")
            if attempt < 2:
                time.sleep(1.0)
    raise RuntimeError("Chrome mobile layout probe failed after 2 attempts: " + "; ".join(failures))


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="tradingagents-mobile-layout-") as temp:
        root = Path(temp)
        site = root / "site"
        archive = root / "archive"
        build_mobile_site(site_dir=site, archive_dir=archive)
        strategy_path = site / "mobile" / "strategy.json"
        strategy_path.write_text(
            json.dumps(_strategy_fixture(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        with _serve(site) as page_url:
            results = _run_probe(page_url, root / "chrome-profile")
    failures = []
    for result in results:
        width = int(result["requestedWidth"])
        if abs(float(result.get("innerWidth") or 0) - width) > 1:
            failures.append(f"{width}px innerWidth mismatch: {result.get('innerWidth')}")
        if float(result.get("documentScrollWidth") or 0) > width + 1:
            failures.append(f"{width}px document overflow: {result.get('documentScrollWidth')}")
        if float(result.get("bodyScrollWidth") or 0) > width + 1:
            failures.append(f"{width}px body overflow: {result.get('bodyScrollWidth')}")
        if result.get("overflow"):
            failures.append(f"{width}px overflowing elements: {result['overflow']}")
        if int(result.get("headingLineCount") or 0) != 1:
            failures.append(
                f"{width}px market heading wrapped to {result.get('headingLineCount')} lines"
            )
        for field in (
            "hasStrategyDirection",
            "hasExecutionStatus",
            "hasEntryCondition",
            "hasTriggeredAction",
            "hasInvalidation",
            "hasInvalidationAction",
        ):
            if result.get(field) is not True:
                failures.append(f"{width}px missing investor field: {field}")
    print(json.dumps({"status": "FAILED" if failures else "PASSED", "viewports": results, "failures": failures}, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
