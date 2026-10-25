"""Browser checks for the existing archive's read-only chart and replay view."""
from __future__ import annotations

import argparse
import asyncio
import base64
from datetime import datetime, timedelta, timezone
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
MARKER_ONLY = False


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
    for i in range(30):
        stamp = datetime(2026, 9, 16, 20, tzinfo=timezone.utc) + timedelta(days=i)
        bars.append({"timestamp": stamp.isoformat(), "available_at": (stamp + timedelta(hours=1)).isoformat(),
                     "observed_at": "2026-10-16T10:00:00Z", "open": 100+i, "high": 110+i,
                     "low": 95+i, "close": 102+i, "volume": 1000+i*100,
                     "session_id": stamp.date().isoformat(), "interval": "1d"})
    payloads = {"chart_evidence.json": {"ticker": "TEST", "bars": bars},
                "analysis.json": {"finished_at": "2026-10-16T10:00:00Z"},
                "execution_contract.json": {"ingested_at": "2026-10-16T10:00:00Z", "structured_levels": [
                    {"price": 123.123456789 + (i//3)*.1, "label": f"원래 계획 {i+1} · 동일 가격의 긴 진입·무효화 조건"}
                    for i in range(18)]},
                "execution_update.json": {"execution_asof": "2026-10-16T10:00:00Z", "ingested_at": "2026-10-16T10:00:00Z",
                                          "market_data_asof": "2026-10-16T09:59:00Z", "decision_state": "WAIT",
                                          "session_vwap": 123.987654321,
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
            if(address.pathname==='/api/snapshot'&&response.status===200){
              // Synthetic display fixture only: do not modify backend evidence,
              // order counts, verdicts, fills or accounting calculations.
              const body=await response.clone().json();
              if(body.series?.length===2){
                const events=[],markers=[];
                for(const stamp of ['2026-10-15T20:00:00.123456+00:00','2026-10-16T09:10:00.123456Z']){
                  const time=Math.floor(Date.parse(stamp)/1000);
                  for(let i=0;i<2;i++){
                    markers.push({category:'SIGNAL',text:'추천 · ADD_IF_CONFIRMED · <img src=x onerror=bad>',time,position:'belowBar',shape:'arrowUp',color:'#13785f'});
                    events.push({kind:'SIGNAL',occurred_at:stamp,available_at:stamp,ingested_at:'2026-10-16T10:00:00.654321Z',payload:{action:'ADD_IF_CONFIRMED',source:'TradingAgents',run_id:'fixture-original-signal',account:'PRIVATE_DO_NOT_DISPLAY',order_id:'PRIVATE_DO_NOT_DISPLAY',path:'PRIVATE_DO_NOT_DISPLAY'}});
                  }
                  for(const [category,text] of [['REAL_FILL','실제 체결 · BUY'],['DEMO_FILL','데모 체결 · SELL'],['PAPER_FILL','모의 체결 · BUY']])markers.push({category,text,time,position:'aboveBar',shape:'arrowDown',color:'#c53b51'});
                  markers.push({category:'EVENT_GUARD',text:'공시 표식 유지',time,position:'aboveBar',shape:'circle',color:'#90642f'});
                }
                body.markers=[...markers,...body.markers].sort((a,b)=>a.time-b.time);
                body.lifecycle.events=[...events,...(body.lifecycle.events||[])];
                return new Response(JSON.stringify(body),{status:200,headers:response.headers});
              }
            }
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
            result["historical_signal_clarity"] = await evaluate('''(() => {
              const snapshot=window.reviewSnapshot,controls=[...document.querySelectorAll('.chart-signal-control input')];
              if(controls.length!==2||new Set(controls.map(c=>c.id)).size!==2)throw Error('Historical text needs unique controls on both charts');
              if(controls.some(c=>c.type!=='checkbox'||c.checked||c.disabled||!document.getElementById(c.getAttribute('aria-controls'))||c.getAttribute('aria-describedby')!=='chart-signal-hint'))throw Error('Native historical control lacks its own accessible binding');
              if(document.querySelector('#chart-signal-hint').textContent.indexOf('현재 승인이나 체결이 아닙니다')<0)throw Error('Past signal is confused with approval');
              window.__historicalBefore=JSON.stringify(snapshot);
              for(const record of chartSignalMarkers){
                const expected=chartMarkerProjection(record.markers,false),actual=record.api.markers();
                if(JSON.stringify(actual)!==JSON.stringify(expected))throw Error('Default signal text or fill markers changed');
                if(record.markers.filter(m=>m.category==='SIGNAL').length!==2||record.markers.filter(m=>m.category.endsWith('_FILL')).length!==3)throw Error('Synthetic signal/fill categories did not reach chart');
              }
              const area=document.querySelector('#historical-signal-records'),details=area.querySelector('details');
              if(!details||details.open)throw Error('Historical disclosure absent or covers default chart');
              details.open=true;
              const tables=[...area.querySelectorAll('table')],rows=tables.map(t=>[...t.rows].slice(1));
              if(rows[0].length!==4||rows[1].length!==4)throw Error('Historical duplicates lost');
              if(rows[0].some(r=>r.cells[1].textContent!=='추천 · ADD_IF_CONFIRMED · <img src=x onerror=bad>'))throw Error('Original complete marker text was lost');
              if(!area.textContent.includes('2026-10-16T09:10:00.123456Z')||!area.textContent.includes('2026-10-15T20:00:00.123456+00:00')||!area.textContent.includes('확정: 미제공'))throw Error('Raw precision or missing clocks changed');
              if(area.querySelector('img')||area.textContent.includes('PRIVATE_DO_NOT_DISPLAY')||window.__pwned)throw Error('Historical display leaked private fields or interpreted markup');
              if(!area.textContent.includes('두 표의 행을 임의로 서로 연결하지 않습니다')||!area.textContent.includes('초 단위 표시 좌표이며 원래 정밀 시각이 아닙니다'))throw Error('Unproved pairing or original clock reconstruction implied');
              if(document.documentElement.scrollWidth>innerWidth+2)throw Error('Historical table overflow escaped page');
              details.open=false;controls[0].focus();
              window.__oldSignalControl=controls[0];window.__oldSignalApi=chartSignalMarkers[0].api;
              return {charts:controls.length,signalRows:rows[0].length,originalRows:rows[1].length,defaultSignalText:false,fillMarkersUnchanged:true,rawPrecision:true,privacy:true};
            })()''')
            for chart_index in (0, 1):
                await evaluate(f"document.querySelectorAll('.chart-signal-control input')[{chart_index}].focus()")
                for enabled in (True, False):
                    await call("Input.dispatchKeyEvent", {"type": "keyDown", "key": " ", "code": "Space", "windowsVirtualKeyCode": 32})
                    await call("Input.dispatchKeyEvent", {"type": "keyUp", "key": " ", "code": "Space", "windowsVirtualKeyCode": 32})
                    if not await evaluate('''(() => {
                      const controls=[...document.querySelectorAll('.chart-signal-control input')],enabled=ENABLED,index=CHARTINDEX;
                      if(controls.some((control,i)=>control.checked!==(enabled&&i===index)))throw Error('Historical keyboard toggle crossed charts');
                      for(const record of chartSignalMarkers){const show=enabled&&record.control_id===controls[index].id;
                        if(JSON.stringify(record.api.markers())!==JSON.stringify(chartMarkerProjection(record.markers,show)))throw Error('Marker display differs from exact projection');}
                      if(planPriceLines.some(p=>p.line.options().axisLabelVisible||p.line.options().title!==''))throw Error('Historical text toggle changed price labels');
                      if(JSON.stringify(window.reviewSnapshot)!==window.__historicalBefore)throw Error('Historical display mutated original snapshot');
                      return true;
                    })()'''.replace("ENABLED", json.dumps(enabled)).replace("CHARTINDEX", str(chart_index))):
                        raise RuntimeError("Historical text keyboard toggle failed")
            result["historical_signal_clarity"]["keyboard_chart_scoped_toggle"] = True
            await evaluate("document.querySelector('#historical-signal-records summary').focus()")
            await call("Input.dispatchKeyEvent", {"type": "keyDown", "key": " ", "code": "Space", "windowsVirtualKeyCode": 32})
            await call("Input.dispatchKeyEvent", {"type": "keyUp", "key": " ", "code": "Space", "windowsVirtualKeyCode": 32})
            if not await evaluate("document.querySelector('#historical-signal-records details').open"):
                raise RuntimeError("Historical original records did not open with the keyboard")
            if OUTPUT:
                await evaluate("document.querySelector('#charts').scrollIntoView({block:'start'})")
                shot = await call("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False})
                (OUTPUT / f"historical-signals-chart-{width}.png").write_bytes(base64.b64decode(shot["data"]))
                await evaluate("document.querySelector('#historical-signal-records').scrollIntoView({block:'start'})")
                shot = await call("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False})
                (OUTPUT / f"historical-signals-records-{width}.png").write_bytes(base64.b64decode(shot["data"]))
            if width < 600:
                await evaluate("window.__signalRegion=document.querySelector('#historical-signal-records .review-table-scroll');window.__signalRegion.scrollIntoView({block:'center'});window.__signalRegion.focus();")
                await call("Input.dispatchKeyEvent", {"type": "keyDown", "key": "ArrowRight", "code": "ArrowRight", "windowsVirtualKeyCode": 39})
                await call("Input.dispatchKeyEvent", {"type": "keyUp", "key": "ArrowRight", "code": "ArrowRight", "windowsVirtualKeyCode": 39})
                for _ in range(20):
                    await asyncio.sleep(.05)
                    if await evaluate("window.__signalRegion.scrollLeft>0"):
                        break
                else:
                    raise RuntimeError("Historical record table did not scroll with the keyboard")
                await evaluate("window.__signalRegion.scrollLeft=0;window.__signalRegion.blur();")
            result["historical_signal_clarity"]["keyboard_details_and_scroll"] = True
            await evaluate("document.querySelector('#historical-signal-records details').open=false;loadSnapshot()")
            for _ in range(100):
                await asyncio.sleep(.1)
                if await evaluate("!viewBusy&&window.reviewSnapshot&&document.querySelector('.chart-signal-control input')!==window.__oldSignalControl"):
                    break
            else:
                raise RuntimeError("New snapshot did not replace historical control")
            if not await evaluate('''(() => {
              window.__oldSignalTouched=false;window.__oldSignalApi.setMarkers=()=>{window.__oldSignalTouched=true;};
              window.__oldSignalControl.checked=true;window.__oldSignalControl.dispatchEvent(new Event('change'));
              if(window.__oldSignalTouched)throw Error('Detached historical control touched a removed chart');
              if(chartSignalMarkers.some(r=>r.api.markers().some(m=>m.text.startsWith('추천 ·'))))throw Error('Old control changed new chart');
              if(JSON.stringify(window.reviewSnapshot)!==window.__historicalBefore)throw Error('Reload changed synthetic evidence');
              return true;
            })()'''):
                raise RuntimeError("Old historical chart handle remained active")
            result["historical_signal_clarity"]["stale_handle_ignored"] = True
            if MARKER_ONLY:
                results.append(result)
                continue
            result["readable_price_levels"] = await evaluate('''(() => {
              const levels=window.reviewSnapshot.price_levels,controls=[...document.querySelectorAll('.chart-level-control input')];
              const rows=[...document.querySelectorAll('#price-levels table tr')].slice(1);
              if(levels.length!==19||rows.length!==levels.length)throw Error('Dense levels or duplicate names were lost');
              rows.forEach((row,i)=>{if(row.cells[0].textContent!==levels[i].label||row.cells[1].textContent!==String(levels[i].price))throw Error('Legend rounded or changed original levels');});
              rows.forEach(row=>{const cell=row.cells[1],range=document.createRange();range.selectNodeContents(cell);if(range.getBoundingClientRect().width>cell.clientWidth-15)throw Error('Exact price text overlaps the source column');});
              if(!document.querySelector('#price-levels').textContent.includes('개별 출처 미제공')||!document.querySelector('#price-levels').textContent.includes('원래 시세 2026-10-16T09:59:00Z'))throw Error('Original source clocks or unknown-source boundary lost');
              const originalClocks=document.querySelector('#price-levels details');
              if(!originalClocks||originalClocks.open||!originalClocks.querySelector('summary').textContent.includes('원래 시각 4개'))throw Error('Original clock disclosure missing or obscuring default price list');
              if(controls.length!==window.reviewSnapshot.series.length||controls.length!==2)throw Error('Each interval requires its own label control');
              if(new Set(controls.map(c=>c.id)).size!==controls.length)throw Error('Duplicate chart control id');
              controls.forEach(c=>{if(c.checked||!document.getElementById(c.getAttribute('aria-controls'))?.classList.contains('chart')||!c.closest('label')?.textContent.includes('차트에 가격 이름 표시'))throw Error('Chart control lacks an accessible unique binding');});
              const options=planPriceLines.map(p=>p.line.options());
              if(options.length!==levels.length*controls.length||options.some(p=>p.axisLabelVisible||p.title!==''))throw Error('Default level labels still obscure candles');
              const styles={DOTTED:LightweightCharts.LineStyle.Dotted,SOLID:LightweightCharts.LineStyle.Solid,DASHED:LightweightCharts.LineStyle.Dashed};
              options.forEach((p,i)=>{const level=levels[i%levels.length];if(p.price!==level.price||p.color!=='#90642f'||p.lineStyle!==(styles[level.style]??LightweightCharts.LineStyle.Dashed)||p.lineVisible!==true)throw Error('Price line economics/style changed');});
              if([...document.querySelectorAll('#strategy-overview .review-unit')].some(e=>getComputedStyle(e).whiteSpace!=='nowrap'||e.getClientRects().length!==1))throw Error('Count and unit wrap separately');
              window.__levelSnapshotBefore=JSON.stringify(window.reviewSnapshot);
              controls[0].focus();
              return {levels:levels.length,charts:controls.length,default_inline_names:false,exact_legend:true,zero_roundtrip_unit:[...document.querySelectorAll('#strategy-overview .review-unit')].some(e=>e.textContent==='0회')};
            })()''')
            for _ in range(2):
                await call("Input.dispatchKeyEvent", {"type": "keyDown", "key": " ", "code": "Space", "windowsVirtualKeyCode": 32})
                await call("Input.dispatchKeyEvent", {"type": "keyUp", "key": " ", "code": "Space", "windowsVirtualKeyCode": 32})
                enabled = _ == 0
                if not await evaluate('''(() => {
                  const controls=[...document.querySelectorAll('.chart-level-control input')],enabled=ENABLED;
                  if(controls[0].checked!==enabled||controls[1].checked)throw Error('Keyboard label toggle crossed charts');
                  for(const p of planPriceLines){const options=p.line.options(),show=enabled&&p.control_id===controls[0].id;if(options.axisLabelVisible!==show||options.title!==(show?p.label:''))throw Error('Keyboard label display did not match its chart');}
                  if(JSON.stringify(window.reviewSnapshot)!==window.__levelSnapshotBefore)throw Error('Display toggle mutated snapshot evidence');
                  return true;
                })()'''.replace("ENABLED", json.dumps(enabled))):
                    raise RuntimeError("Chart labels did not respond to keyboard")
            result["readable_price_levels"]["keyboard_chart_scoped_toggle"] = True
            # Capture the actual default legend before the keyboard-scroll
            # interaction changes its position. Native key scrolling may
            # continue animating after keyUp; that is not its initial layout.
            if OUTPUT:
                await evaluate("document.querySelector('#charts').scrollIntoView({block:'start'})")
                shot = await call("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False})
                (OUTPUT / f"chart-levels-{width}.png").write_bytes(base64.b64decode(shot["data"]))
                await evaluate("document.querySelector('#price-levels').scrollIntoView({block:'start'})")
                shot = await call("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False})
                (OUTPUT / f"chart-level-legend-{width}.png").write_bytes(base64.b64decode(shot["data"]))
            await evaluate("document.querySelector('#price-levels details summary').focus()")
            for opened in (True, False):
                await call("Input.dispatchKeyEvent", {"type": "keyDown", "key": " ", "code": "Space", "windowsVirtualKeyCode": 32})
                await call("Input.dispatchKeyEvent", {"type": "keyUp", "key": " ", "code": "Space", "windowsVirtualKeyCode": 32})
                if not await evaluate("document.querySelector('#price-levels details').open===" + json.dumps(opened)):
                    raise RuntimeError("Original price-level clocks did not open with keyboard")
            result["readable_price_levels"]["keyboard_original_clock_details"] = True
            if width < 600:
                await evaluate("window.__legendRegion=document.querySelector('#price-levels .review-table-scroll');window.__legendRegion.scrollIntoView({block:'center'});window.__legendRegion.focus();")
                await call("Input.dispatchKeyEvent", {"type": "keyDown", "key": "ArrowRight", "code": "ArrowRight", "windowsVirtualKeyCode": 39})
                await call("Input.dispatchKeyEvent", {"type": "keyUp", "key": "ArrowRight", "code": "ArrowRight", "windowsVirtualKeyCode": 39})
                for _ in range(20):
                    await asyncio.sleep(.05)
                    if await evaluate("window.__legendRegion.scrollLeft>0"):
                        break
                else:
                    raise RuntimeError("Price-level legend did not scroll with the keyboard")
                await evaluate("window.__legendRegion.scrollTo({left:0,behavior:'instant'});window.__legendRegion.blur();")
                result["readable_price_levels"]["keyboard_legend_scroll"] = True
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
    global OUTPUT, EMPTY_PAGE_URL, MARKER_ONLY
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--marker-only", action="store_true", help="Run only the small synthetic historical-marker browser checks")
    args = parser.parse_args()
    MARKER_ONLY = args.marker_only
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
