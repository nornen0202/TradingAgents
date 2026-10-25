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
from tradingagents.execution.strategy_evaluation import evaluate_strategy_orders

OUTPUT = None
EMPTY_PAGE_URL = None


class CheckedServer(ThreadingHTTPServer):
    """A recovered later request must not hide an earlier server exception."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unhandled_errors = []

    def handle_error(self, request, client_address):
        error = sys.exc_info()[1]
        if not isinstance(error, (BrokenPipeError, ConnectionResetError)):
            self.unhandled_errors.append(type(error).__name__)
        super().handle_error(request, client_address)


def fixture(root):
    run = root / "runs/2026/fixture"
    directory = run / "tickers" / "TEST"
    directory.mkdir(parents=True)
    (run / "run.json").write_text(json.dumps({"run_id": "fixture", "status": "success",
        "started_at": "2026-10-16T09:00:00Z", "finished_at": "2026-10-16T10:00:00Z",
        "tickers": [{"ticker": "TEST", "status": "success"}]}))
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
    paper = root / "paper"
    paper.mkdir()
    (paper / "kis-session-validation.json").write_text(json.dumps({
        "schema": "tradingagents.kis-session-validation/v1", "mode": "KIS_DEMO", "live_orders_enabled": False,
        "checked_at": "2026-10-16T11:00:00Z", "markets": {
            "KR": {"status": "VERIFIED", "checked_at": "2026-10-16T11:00:00Z", "stages": {
                stage: {"verified": True, "observed_at": "2026-10-16T10:59:00Z",
                    "source": "KIS_DEMO_BROKER_ACK" if stage == "submitted" else "KIS_DEMO_BROKER_REPORT",
                    "order_id": "PRIVATE_DO_NOT_DISPLAY"} for stage in ("submitted", "filled", "cancelled")}},
            "US": {"status": "WAITING_SESSION", "checked_at": "2026-10-16T11:00:00Z", "stages": {}}}}))
    (paper / "kis-strategy-runtime.json").write_text(json.dumps({
        "schema": "tradingagents.kis-strategy-runtime/v1", "mode": "KIS_DEMO_STRATEGY", "enabled": True,
        "real_orders_enabled": False, "checked_at": "2026-10-16T11:00:00Z", "markets": {
            "KR": {"status": "ACTIVE", "checked_at": "2026-10-16T11:00:00Z", "gate_passed": True,
                "allocation_diagnostics": {"allocation_mode": "DEMO_NATIVE_ONE_SHARE_V1",
                    "eligible_candidates": 0, "strategy_owned_positions": 1, "real_account_allocation_used": False,
                    "reason_counts": {"NO_AUTHORIZED_EXECUTION_ACTION": 30},
                    "research_entry_actions": {"WAIT": 30}, "research_conditional_entries": {"NONE": 30},
                    "ticker_blockers": {"PRIVATE_DO_NOT_DISPLAY": "PRIVATE_DO_NOT_DISPLAY"}},
                "refresh_attempt": {"market": "kr", "session_date": "2026-10-16", "status": "FAILED",
                    "started_at": "2026-10-16T10:50:00Z", "finished_at": "2026-10-16T10:51:00Z",
                    "consecutive_failures": 3, "real_orders_enabled": False, "error_type": "LocalStorageHeadroomError"},
                "evaluation": evaluate_strategy_orders([{"id": "fixture-buy", "ticker": "005930.KS", "side": "BUY",
                    "quantity": 1, "filled_quantity": 1, "fill_notional": 69900, "status": "FILLED", "mode": "demo",
                    "source": "KIS_DEMO_BROKER_REPORT", "strategy_performance": True,
                    "prepared_at": "2026-10-16T10:59:00Z", "observed_at": "2026-10-16T10:59:10Z",
                    "ingested_at": "2026-10-16T10:59:10Z"}], market="KR", as_of="2026-10-16T11:00:00Z",
                    gross_pnl=100, valuation_complete=True),
                "orders": [{"ticker": "005930.KS", "run_id": "fixture-strategy", "side": "BUY", "quantity": 1,
                    "filled_quantity": 1, "limit_price": 70000, "average_fill_price": 69900, "status": "FILLED",
                    "prepared_at": "2026-10-16T10:59:00Z", "observed_at": "2026-10-16T10:59:10Z", "broker_order_id": "PRIVATE_DO_NOT_DISPLAY"}],
                "performance": {"basis": "STRATEGY_GROSS_CASHFLOWS_PLUS_MARKED_HOLDINGS", "status": "AVAILABLE", "currency": "KRW",
                    "gross_pnl": 100, "observed_at": "2026-10-16T11:00:00Z", "mark_times": ["2026-10-16T10:59:50Z"]}},
            "US": {"status": "WAITING_VALIDATION", "checked_at": "2026-10-16T11:00:00Z", "gate_passed": False, "blockers": ["VALIDATION_REQUIRED"]}}}))
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
        await call("Page.addScriptToEvaluateOnNewDocument", {"source": '''
          window.__reviewRequests=[];
          const wireFetch=window.fetch.bind(window);
          window.fetch=async(url,...args)=>{
            const address=new URL(url,location.origin),row={path:address.pathname,query:Object.fromEntries(address.searchParams)};
            if(['/api/tickers','/api/snapshot'].includes(address.pathname))window.__reviewRequests.push(row);
            const response=await wireFetch(url,...args);
            row.status=response.status;row.generation=response.headers.get('X-Archive-Catalog-Generation');
            return response;
          };
        '''})
        for width in (360, 390, 430, 1440):
            await call("Emulation.setDeviceMetricsOverride", {"width": width, "height": 1000, "deviceScaleFactor": 1, "mobile": width < 600})
            await call("Page.navigate", {"url": page_url})
            for _ in range(100):
                await asyncio.sleep(.1)
                if await evaluate("Boolean(window.reviewSnapshot && document.querySelector('#charts canvas'))"):
                    break
            else:
                diagnostic = await evaluate("({status:document.querySelector('#status')?.textContent,requests:window.__reviewRequests?.slice(-8)})")
                raise RuntimeError("Lightweight Charts did not render its snapshot: " + json.dumps(diagnostic, ensure_ascii=False))
            result = await evaluate('''(() => {
              if (window.__pwned || document.querySelector('#facts img')) throw Error('Evidence executed markup');
              if (!document.querySelector('#reasons').textContent.includes('volume_rule_not_met')) throw Error('Engine reasons missing');
              if (window.reviewSnapshot.broker_orders_sent !== 0) throw Error('Viewer is not read only');
              if (!document.querySelector('#source-context').textContent.includes('조회 기준 시각: '+window.reviewSnapshot.as_of_evaluated_at)) throw Error('Snapshot cutoff was hidden or replaced by completion time');
              if (!document.querySelector('#paper-health').textContent.includes('휴장·장 종료')) throw Error('Paper status absent');
              if (!document.querySelector('#kis-demo-health').textContent.includes('조회 점검 기록 없음') || !document.querySelector('#kis-demo-health').textContent.includes('잔고·주문내역 조회')) throw Error('KIS read/order distinction absent');
              if (!document.querySelector('#kis-validation-health').textContent.includes('주문·체결·취소 확인 완료') || !document.querySelector('#kis-validation-health').textContent.includes('다음 정규장 대기') || !document.querySelector('#kis-validation-health').textContent.includes('미검증')) throw Error('KIS execution stage distinction absent');
              if (document.body.textContent.includes('PRIVATE_DO_NOT_DISPLAY')) throw Error('Private metadata leaked');
              const strategy=document.querySelector('#kis-strategy-health').textContent;
              if (!strategy.includes('fixture-strategy') || !strategy.includes('체결 완료') || !strategy.includes('100 KRW') || !strategy.includes('정규장 검증 통과 대기') || !strategy.includes('순손익은 표시하지 않습니다')) throw Error('KIS strategy execution/performance missing');
              if (!strategy.includes('가정 비용 민감도 · 실제 순손익 아님') || !strategy.includes('실투자 판단 미충족') || !strategy.includes('30 KRW') || !strategy.includes('실투자로 자동 전환하지 않습니다')) throw Error('Cost assumptions or readiness boundary missing');
              const overview=document.querySelector('#strategy-overview').textContent;
              if(!overview.includes('정상 체결') || !overview.includes('다음 확인') || !overview.includes('3분 경과')) throw Error('First unmet evidence summary missing or wrong clock threshold');
              if (!strategy.includes('계획 검사 통과 후보 0개') || !strategy.includes('실행 엔진의 매수·매도 행동 없음') || !strategy.includes('당일 시세 갱신 재시도 한도 소진') || !strategy.includes('저장공간 부족')) throw Error('Actual no-action and producer failure diagnostics missing');
              if (!document.querySelector('#experiment-cards').textContent.includes('paired-test')) throw Error('Experiment card absent');
              if (!document.querySelector('#experiment-cards').textContent.includes('수익률·낙폭을 표시하지 않습니다')) throw Error('Unobserved performance fabricated');
              if (document.documentElement.scrollWidth > innerWidth+2) throw Error('Viewport overflow');
              return {width:innerWidth,canvas:document.querySelectorAll('#charts canvas').length,readOnly:true};
            })()''')
            if result["width"] != width:
                raise RuntimeError(f"Mobile layout viewport expanded from {width} to {result['width']}")
            result["catalog_snapshot_same_generation"] = await evaluate('''(() => {
              const catalog=window.__reviewRequests.find(r=>r.path==='/api/tickers'&&r.status===200);
              const snapshot=window.__reviewRequests.find(r=>r.path==='/api/snapshot');
              if(!catalog||!/^\\d+$/.test(catalog.generation)||!snapshot||snapshot.query.catalog_generation!==catalog.generation)throw Error('First catalog 200 generation was lost before snapshot');
              return true;
            })()''')
            table_layout = await evaluate('''(() => {
              document.querySelectorAll('#kis-strategy-health details').forEach(d=>d.open=true);
              const visible=e=>!!e.getClientRects().length&&getComputedStyle(e).visibility!=='hidden';
              if(!visible(document.querySelector('#status')))throw Error('Progress/status hidden in collapsed settings');
              const tables=[...document.querySelectorAll('table.review-data-table')].filter(visible);
              const wide=tables.filter(t=>t.rows[0].cells.length>=3),simple=tables.filter(t=>t.rows[0].cells.length===2);
              if(!wide.length||!simple.length)throw Error('Readable wide/simple table fixtures absent');
              const measurements=wide.map(t=>{
                const wrapper=t.parentElement,columns=t.rows[0].cells.length;
                const minimum=Math.min(...[...t.rows[0].cells].map(c=>c.getBoundingClientRect().width));
                const range=wrapper.scrollWidth-wrapper.clientWidth;
                if(minimum<136)throw Error('Operational header column collapsed below readable width: '+columns+' columns / '+minimum+'px');
                if(getComputedStyle(wrapper).overflowX!=='auto'||wrapper.tabIndex!==0)throw Error('Wide table has no local keyboard scrolling');
                if([...t.rows[0].cells].some(c=>getComputedStyle(c).wordBreak!=='keep-all'))throw Error('Korean headings break into vertical characters');
                if(innerWidth<600&&range<=0)throw Error('Mobile table unexpectedly shrunk instead of local horizontal scrolling');
                if(wrapper.clientWidth>=columns*144&&range>1)throw Error('Wide desktop table adds unnecessary horizontal scroll');
                return {columns,minimumCellWidth:minimum,scrollRange:range};
              });
              if(simple.some(t=>t.getBoundingClientRect().width>t.parentElement.clientWidth+1))throw Error('Simple two-column table expanded');
              const scroll=wide.map(t=>t.parentElement).find(e=>e.scrollWidth>e.clientWidth+2);
              if(scroll){scroll.scrollIntoView({block:'center'});scroll.scrollLeft=0;scroll.focus();window.__tableScrollTarget=scroll;}
              if(document.documentElement.scrollWidth>innerWidth+2)throw Error('Table overflow escaped into the page');
              return {measurements,simpleTableCount:simple.length,keyboardScrollRequired:!!scroll};
            })()''')
            if table_layout["keyboardScrollRequired"]:
                await call("Input.dispatchKeyEvent", {"type": "keyDown", "key": "ArrowRight", "code": "ArrowRight", "windowsVirtualKeyCode": 39})
                await call("Input.dispatchKeyEvent", {"type": "keyUp", "key": "ArrowRight", "code": "ArrowRight", "windowsVirtualKeyCode": 39})
                for _ in range(20):
                    await asyncio.sleep(.05)
                    if await evaluate("window.__tableScrollTarget.scrollLeft>0"):
                        break
                else:
                    raise RuntimeError("Focused operational table did not scroll with ArrowRight")
                await evaluate("window.__tableScrollTarget.scrollLeft=0;window.__tableScrollTarget.blur();")
            await evaluate("scrollTo(0,0)")
            result["readable_operational_tables"] = table_layout
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
                await evaluate("document.querySelector('#kis-validation-health').scrollIntoView({block:'start'})")
                shot = await call("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False})
                (OUTPUT / f"kis-validation-{width}.png").write_bytes(base64.b64decode(shot["data"]))
                await evaluate("document.querySelector('#kis-strategy-health').scrollIntoView({block:'start'})")
                shot = await call("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False})
                (OUTPUT / f"kis-strategy-costs-{width}.png").write_bytes(base64.b64decode(shot["data"]))
            await evaluate("document.querySelector('#asof').value='2026-10-16T08:00:00Z'; loadSnapshot()")
            await evaluate('''(() => {
              if (window.reviewSnapshot?.series.length || window.reviewSnapshot?.execution_verdict) throw Error('Future data in replay');
              if (document.querySelector('#charts canvas') || document.querySelector('#facts').textContent.includes('<img')) throw Error('Stale future view remained');
              if (document.querySelector('#kis-validation-health').textContent.includes('확인 완료')) throw Error('Future execution validation in replay');
              if (document.querySelector('#kis-strategy-health').textContent.includes('fixture-strategy')) throw Error('Future strategy execution in replay');
              return true;
            })()''')
            result["replay_excludes_future"] = True
            await evaluate("document.querySelector('#asof').value='invalid'; loadSnapshot()")
            if await evaluate("window.reviewSnapshot !== null || document.querySelector('#charts canvas') !== null"):
                raise RuntimeError("Invalid as-of retained a prior view")
            result["invalid_query_clears_view"] = True
            await evaluate("document.querySelector('#asof').value='2026-10-16T12:00:00Z'; document.querySelector('#ticker').value=''; loadSnapshot()")
            if not await evaluate("window.reviewSnapshot === null && document.querySelector('#paper-health').textContent.includes('휴장·장 종료') && document.querySelector('#kis-validation-health').textContent.includes('확인 완료')"):
                raise RuntimeError("Chart failure hid independent operational receipts")
            result["chart_failure_preserves_operations"] = True
            await call("Page.navigate", {"url": EMPTY_PAGE_URL})
            for _ in range(100):
                await asyncio.sleep(.1)
                if await evaluate("document.querySelector('#status')?.textContent.includes('완료된 분석이 없습니다') && document.querySelector('#kis-validation-health')?.textContent.includes('확인 완료')"):
                    break
            else:
                raise RuntimeError("Empty catalog hid operational status")
            if not await evaluate("!document.querySelector('#ticker').options.length && document.querySelector('#paper-health').textContent.includes('휴장·장 종료')"):
                raise RuntimeError("Empty archive status missing")
            if not await evaluate("document.querySelector('#status').getAttribute('aria-busy')==='false' && !document.querySelector('#asof').disabled && !viewBusy"):
                raise RuntimeError("Empty archive stranded refresh controls")
            result["empty_catalog_preserves_operations"] = True
            for catalog_mode in ("indexing", "snapshot-progress", "health-delay", "pending", "timeout", "failed"):
                injected = await call("Page.addScriptToEvaluateOnNewDocument", {"source": '''
                  window.__catalogMode=MODE;
                  const originalFetch=window.fetch.bind(window),originalTimeout=window.setTimeout.bind(window);
                  window.__indexingResponses=0;
                  window.__snapshotProgressResponses=0;
                  window.setTimeout=(fn,ms,...args)=>originalTimeout(fn,window.__catalogMode==='timeout'&&ms===15000?300:ms,...args);
                  function pendingRequest(args){return new Promise((resolve,reject)=>{
                    args[0]?.signal?.addEventListener('abort',()=>reject(new DOMException('aborted','AbortError')),{once:true});
                  });}
                  window.fetch=(url,...args)=>{
                    const address=new URL(url,location.origin),path=address.pathname;
                    const jsonResponse=(payload,status,generation)=>new Response(JSON.stringify(payload),{status,headers:{'Content-Type':'application/json','X-Archive-Catalog-Generation':String(generation)}});
                    const indexProgress=()=>jsonResponse({status:'INDEXING',generation:Number(window.__indexingGeneration),manifests_checked:12,manifests_parsed:12},202,window.__indexingGeneration);
                    const snapshotProgress=()=>{
                      const phase=window.__releaseSnapshot?'BUILD':'REPLAY';
                      if(window.__releaseSnapshot)window.__snapshotBuildShown=true;
                      window.__snapshotProgressResponses++;
                      return jsonResponse({status:'SNAPSHOT_BUILDING',job_token:window.__fixtureJob,generation:Number(window.__snapshotGeneration),phase,elapsed_seconds:20+window.__snapshotProgressResponses,phase_elapsed_seconds:1},202,window.__snapshotGeneration);
                    };
                    if(path==='/api/kis-demo-health' && window.__catalogMode==='health-delay')return pendingRequest(args);
                    if(path==='/api/snapshot' && window.__catalogMode==='snapshot-progress'){
                      if(window.__snapshotPayload){
                        if(!window.__releaseSnapshot||!window.__snapshotBuildShown)return Promise.resolve(snapshotProgress());
                        return Promise.resolve(jsonResponse(window.__snapshotPayload,200,window.__snapshotGeneration));
                      }
                      return originalFetch(url,...args).then(async response=>{
                        if(response.status!==200)return response;
                        window.__snapshotPayload=await response.clone().json();
                        window.__snapshotGeneration=response.headers.get('X-Archive-Catalog-Generation');
                        window.__fixtureJob=address.searchParams.get('snapshot_job')||'fixture_job';
                        return snapshotProgress();
                      });
                    }
                    if(path==='/api/tickers') {
                      if(window.__catalogMode==='indexing'){
                        if(window.__indexingPayload){
                          if(window.__indexingResponses++<2)return Promise.resolve(indexProgress());
                          return Promise.resolve(jsonResponse(window.__indexingPayload,200,window.__indexingGeneration));
                        }
                        return originalFetch(url,...args).then(async response=>{
                          if(response.status!==200)return response;
                          window.__indexingPayload=await response.clone().json();
                          window.__indexingGeneration=response.headers.get('X-Archive-Catalog-Generation');
                          window.__indexingResponses++;
                          return indexProgress();
                        });
                      }
                      if(window.__catalogMode==='timeout')return pendingRequest(args);
                      if(window.__catalogMode==='pending')return new Promise((resolve,reject)=>{
                        const signal=args[0]?.signal;
                        signal?.addEventListener('abort',()=>reject(new DOMException('aborted','AbortError')),{once:true});
                      });
                      if(window.__catalogMode==='failed')return Promise.resolve(new Response('',{status:503}));
                    }
                    return originalFetch(url,...args);
                  };
                '''.replace("MODE", json.dumps(catalog_mode))})
                await call("Page.navigate", {"url": page_url})
                for _ in range(100):
                    await asyncio.sleep(.1)
                    if await evaluate("document.querySelector('#kis-strategy-health')?.textContent.includes('fixture-strategy') && document.querySelector('#paper-health')?.textContent.includes('휴장·장 종료')"):
                        break
                else:
                    raise RuntimeError(f"{catalog_mode} initial catalog hid operational status")
                if catalog_mode == "health-delay" and not await evaluate("document.querySelector('#kis-demo-health').textContent.includes('확인하고 있습니다')"):
                    raise RuntimeError("Slow health fixture did not remain pending")
                if catalog_mode == "indexing":
                    if not await evaluate("document.querySelector('#status').textContent.includes('실행 기록') && viewBusy && document.querySelector('#status').getClientRects().length>0"):
                        raise RuntimeError("202 discovery progress was not visible")
                    for _ in range(60):
                        await asyncio.sleep(.1)
                        if await evaluate("Boolean(window.reviewSnapshot && !viewBusy)"):
                            break
                    else:
                        raise RuntimeError("202 discovery did not complete")
                    if not await evaluate("window.__indexingResponses>=2"):
                        raise RuntimeError("202 fixture not exercised")
                if catalog_mode == "snapshot-progress":
                    for _ in range(60):
                        await asyncio.sleep(.1)
                        if await evaluate("viewBusy && document.querySelector('#status').textContent.includes('체결·성과 이력') && document.querySelector('#status').getClientRects().length>0"):
                            break
                    else:
                        diagnostic = await evaluate("({status:document.querySelector('#status')?.textContent,polls:window.__snapshotProgressResponses,busy:viewBusy})")
                        raise RuntimeError("Snapshot work did not expose separate replay progress: " + json.dumps(diagnostic, ensure_ascii=False))
                    await evaluate("window.__releaseSnapshot=true")
                    for _ in range(60):
                        await asyncio.sleep(.1)
                        if await evaluate("Boolean(window.reviewSnapshot && !viewBusy)"):
                            break
                    else:
                        raise RuntimeError("Snapshot 202 progress did not complete")
                    if not await evaluate("window.__snapshotProgressResponses>=2 && window.__snapshotBuildShown"):
                        raise RuntimeError("Snapshot work-progress fixture was not exercised")
                if catalog_mode == "timeout":
                    for _ in range(30):
                        await asyncio.sleep(.1)
                        if await evaluate("document.querySelector('#status').textContent.includes('15초') && !viewBusy && document.querySelector('#status').getClientRects().length>0"):
                            break
                    else:
                        raise RuntimeError("Timed-out catalog did not restore controls with an actionable error")
                if catalog_mode == "failed" and not await evaluate("document.querySelector('#status').textContent.includes('자료를 읽지 못했습니다') && document.querySelector('#status').getClientRects().length>0"):
                    raise RuntimeError("Failed catalog did not report its own error")
                # Controls/retry must already be registered while the first
                # catalog is pending or failed. No data clock is changed.
                await evaluate("window.__catalogMode='pass'; document.querySelector('#refresh-catalog').click()")
                for _ in range(100):
                    await asyncio.sleep(.1)
                    if await evaluate("Boolean(window.reviewSnapshot && document.querySelector('#charts canvas'))"):
                        break
                else:
                    raise RuntimeError(f"{catalog_mode} initial catalog disabled retry controls")
                await call("Page.removeScriptToEvaluateOnNewDocument", {"identifier": injected["identifier"]})
                result[catalog_mode+"_catalog_preserves_operations_and_retry"] = True
            await evaluate("window.__previousHealthFetch=window.fetch; window.fetch=(url,...args)=>new URL(url,location.origin).pathname==='/api/kis-strategy-health'?Promise.resolve(new Response('',{status:503})):window.__previousHealthFetch(url,...args); document.querySelector('#refresh-catalog').click()")
            for _ in range(100):
                await asyncio.sleep(.1)
                if await evaluate("!viewBusy && document.querySelector('#strategy-overview').textContent.includes('현재 운영 상태를 읽지 못했습니다')"):
                    break
            else:
                raise RuntimeError("Failed strategy health retained a previous overview")
            await evaluate("window.fetch=window.__previousHealthFetch; document.querySelector('#refresh-catalog').click()")
            for _ in range(100):
                await asyncio.sleep(.1)
                if await evaluate("!viewBusy && document.querySelector('#strategy-overview').textContent.includes('정상 체결')"):
                    break
            else:
                raise RuntimeError("Strategy overview did not recover after retry")
            result["overview_error_and_retry"] = True
            # Display fixture only. Actual evidence admission and ledger-derived
            # API costs are independently exercised by settlement projection tests.
            await evaluate("""(async()=>{
              const payload=await getJson('/api/kis-strategy-health?as_of=2026-10-16T12:00:00Z');
              Object.assign(payload.markets.KR.evaluation,{cost_evidence_status:'COMPLETE_REVIEWED_IMPORT',actual_cost:0,net_pnl:100,exact_fifo_available:false});
              renderKisStrategy(payload);
            })()""")
            if not await evaluate("document.querySelector('#kis-strategy-health').textContent.includes('검토한 증권사 원문 비용·정산') && document.querySelector('#strategy-overview').textContent.includes('검토 원문 비용 0 KRW · 체결 비용 차감 순손익 100 KRW')"):
                raise RuntimeError("Explicit zero cost was hidden or unknown costs became zero")
            result["reviewed_cost_display_fixture"] = True
            results.append(result)
    return results


def main():
    global OUTPUT, EMPTY_PAGE_URL
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    if args.output_dir:
        OUTPUT = args.output_dir
        OUTPUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ta-review-ui-") as temporary:
        root = Path(temporary)
        status_path, registry_path = fixture(root)
        server = CheckedServer(("127.0.0.1", 0), make_handler(archive_dir=root, experiment_registry=registry_path, paper_status_path=status_path))
        worker = Thread(target=server.serve_forever, daemon=True)
        worker.start()
        empty = root / "empty"
        (empty / "paper").mkdir(parents=True)
        (empty / "paper/kis-session-validation.json").write_bytes((root / "paper/kis-session-validation.json").read_bytes())
        empty_server = CheckedServer(("127.0.0.1", 0), make_handler(archive_dir=empty, paper_status_path=status_path))
        empty_worker = Thread(target=empty_server.serve_forever, daemon=True)
        empty_worker.start()
        EMPTY_PAGE_URL = f"http://127.0.0.1:{empty_server.server_port}/"
        try:
            layout._probe_viewports = probe
            results = layout._run_probe(f"http://127.0.0.1:{server.server_port}/", root / "chrome")
        except Exception as error:
            if OUTPUT:
                with (OUTPUT / "result.json").open("x", encoding="utf-8") as stream:
                    json.dump({"status": "FAILED", "mode": "FIXTURE_ONLY", "error_type": type(error).__name__,
                               "message": str(error)[:15000]}, stream, ensure_ascii=False, indent=2)
            raise
        finally:
            server.shutdown()
            worker.join(timeout=5)
            server.server_close()
            empty_server.shutdown()
            empty_worker.join(timeout=5)
            empty_server.server_close()
        if server.unhandled_errors or empty_server.unhandled_errors:
            raise RuntimeError(f"Unhandled HTTP errors: {server.unhandled_errors + empty_server.unhandled_errors}")
    report = {"status": "PASSED", "mode": "FIXTURE_ONLY", "viewports": results}
    if OUTPUT:
        with (OUTPUT / "result.json").open("x", encoding="utf-8") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
