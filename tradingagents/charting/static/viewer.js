/* Display only: all evidence filtering and indicators come from the snapshot API. */
"use strict";
const byId = id => document.getElementById(id);
let charts = [];
let requestVersion = 0;
const number = value => typeof value === "number" && Number.isFinite(value) ? value.toLocaleString("ko-KR", {maximumFractionDigits:3}) : "확인 불가";
function table(title, headings, rows) {
  const section = document.createElement("section");
  const heading = document.createElement("h3"); heading.textContent = title; section.append(heading);
  if (!rows.length) { const empty = document.createElement("p"); empty.textContent = "연결된 기록이 없습니다."; section.append(empty); return section; }
  const scroll = document.createElement("div"); scroll.style.overflowX = "auto";
  const grid = document.createElement("table"); grid.style.cssText = "border-collapse:collapse;width:100%;text-align:left";
  for (const [i, row] of [headings, ...rows].entries()) {
    const tr = document.createElement("tr");
    row.forEach(value=>{const cell=document.createElement(i===0?"th":"td");cell.style.cssText="padding:8px;border-bottom:1px solid #dce4ee;overflow-wrap:anywhere";cell.textContent=value??"확인 불가";tr.append(cell);});
    grid.append(tr);
  }
  scroll.append(grid); section.append(scroll); return section;
}
function renderPerformance(history) {
  const signals = history.signals || [], fills = history.fills || [], intents = history.intents || [];
  byId("performance").replaceChildren(
    table("추천 사후 가격 경로", ["판단", "연결 의도", "체결 기록", "5거래일 가격 변화", "기준지수", "지수 대비"], signals.filter(row=>row.recommendation).map(row=>[
      row.recommendation.action || "확인 불가", (row.intent_ids||[]).length, (row.fill_event_ids||[]).length,
      typeof row.recommendation_outcome?.return_5d === "number" ? number(row.recommendation_outcome.return_5d*100)+"%" : "관측 대기",
      typeof row.recommendation_outcome?.benchmark_return_5d === "number" ? number(row.recommendation_outcome.benchmark_return_5d*100)+"%" : "관측 대기",
      typeof row.recommendation_outcome?.benchmark_excess_5d === "number" ? number(row.recommendation_outcome.benchmark_excess_5d*100)+"%p" : "관측 대기"])),
    table("주문 의도", ["방향", "신청 수량", "체결 수량", "상태"], intents.map(row=>[
      row.side==="BUY"?"매수":"매도",number(row.quantity),number(row.filled_quantity),row.status])),
    table("비용을 반영한 체결", ["구분", "방향", "수량", "가격", "비용", "불리한 슬리피지", "정산 시각"], fills.map(row=>[
      row.mode==="actual"?"실제":row.mode==="demo"?"증권사 모의":"내부 모의", row.side==="BUY"?"매수":"매도",
      number(row.quantity),number(row.price),number(row.cost)+" "+row.currency,
      row.adverse_slippage_bps===null?"기준 가격 미확인":number(row.adverse_slippage_bps)+"bp",row.settled_at])),
    table("정산 후 회고", ["종목", "청산 수량", "비용 차감 손익", "실현 수익률"], (history.retrospectives||[]).map(row=>[
      row.ticker,number(row.closed_quantity),number(row.net_profit)+" "+(row.currency||""),number(row.realized_return_pct)+"%"]))
  );
}
function renderProfile(series) {
  byId("profile").replaceChildren(...series.map(item=>table(item.interval+" · 봉 구간에 균등 배분한 근사 거래량",
    ["가격 구간", "추정 거래량"], item.profile.bins.map(row=>[number(row.low)+" ~ "+number(row.high),number(row.volume)]))));
}
function list(id, values) {
  byId(id).replaceChildren(...values.map(value => {
    const item = document.createElement("li"); item.textContent = value; return item;
  }));
}
async function loadSnapshot() {
  const version = ++requestVersion;
  byId("status").textContent = "기준 시각의 자료를 확인하고 있습니다.";
  const params = new URLSearchParams({ ticker: byId("ticker").value, as_of: byId("asof").value });
  if (byId("anchor").value) params.set("anchor", byId("anchor").value);
  try {
    const response = await fetch("/api/snapshot?" + params);
    if (!response.ok) throw new Error("시각과 보관 자료를 확인해 주세요.");
    const snapshot = await response.json();
    if (version !== requestVersion) return;
    charts.forEach(chart => chart.remove()); charts = [];
    byId("charts").replaceChildren();
    byId("verdict").textContent = snapshot.execution_verdict
      ? "당시 판단: " + snapshot.execution_verdict + " · " + snapshot.execution.execution_asof
      : "판단 기록 없음";
    const freshnessLabels = {FRESH:"10분 미만",STALE:"10분 경과·재확인 필요",MISSING:"관측 시각 없음",INVALID:"시각 확인 필요",FUTURE:"미래 시각 차단"};
    const researchLabels = {FRESH_REGULAR_SESSION:"정규장 자료 확인",EXTENDED_SESSION_RESEARCH_ONLY:"장전·장후 참고 자료",LATEST_REGULAR_CLOSE_RESEARCH_ONLY:"최근 정규장 종가 확인",UNVERIFIED_RESEARCH_INPUT:"유효성 미확인"};
    byId("freshness").textContent = "실행 시세: " + (freshnessLabels[snapshot.freshness_status]||snapshot.freshness_status)
      + " · 연구 자료: " + (researchLabels[snapshot.research_status]||snapshot.research_status);
    byId("freshness").title = snapshot.freshness_status + " / " + snapshot.research_status;
    list("reasons", snapshot.block_reasons);
    list("facts", snapshot.evidence_summary.facts.map(row => row.claim));
    list("inferences", snapshot.evidence_summary.inferences.map(row => row.claim));
    byId("unverified").textContent = "시각 미검증 근거 " + snapshot.evidence_summary.unverified_count + "건 제외";
    list("events", snapshot.events.events.map(row => (row.title || "공시") + " · 발표 " + (row.published_at || "시각 미확인") + " · 최초 감지 " + (row.first_seen_at || "별도 기록 없음") + " · 관측 " + row.observed_at + " · 정정 " + (row.is_amended ? "예" : "아니오") + " · 버전 " + row.version_id));
    renderPerformance(snapshot.lifecycle);
    renderProfile(snapshot.series);
    for (const item of snapshot.series) {
      const wrapper = document.createElement("div");
      const label = document.createElement("h3"); label.textContent = item.interval;
      const element = document.createElement("div"); element.className = "chart";
      const clocks = document.createElement("p"); clocks.className="muted";
      if(item.bars.length){const latest=item.bars[item.bars.length-1];clocks.textContent="최근 봉 " + latest.event_time + " · 관측 " + latest.ingested_at + " · 평가 " + latest.evaluated_at;}
      wrapper.append(label, clocks, element); byId("charts").append(wrapper);
      const chart = LightweightCharts.createChart(element, {autoSize:true, layout:{attributionLogo:true}, timeScale:{timeVisible:item.interval !== "1d"}});
      charts.push(chart);
      const candles = chart.addSeries(LightweightCharts.CandlestickSeries);
      const data = item.bars.map(bar => ({time:Math.floor(Date.parse(bar.timestamp)/1000),open:bar.open,high:bar.high,low:bar.low,close:bar.close}));
      candles.setData(data);
      const vwap = chart.addSeries(LightweightCharts.LineSeries,{color:"#395dd1",lineWidth:2});
      vwap.setData(item.avwap.series.filter(row=>row.value !== null).map(row=>({time:Math.floor(Date.parse(row.timestamp)/1000),value:row.value})));
      snapshot.price_levels.forEach(level=>candles.createPriceLine({price:level.price,title:level.label,lineStyle:LightweightCharts.LineStyle.Dashed,color:"#90642f"}));
      if (data.length) {
        const markers = snapshot.markers.filter(m=>m.time>=data[0].time && m.time<=data[data.length-1].time).map(({category,...marker})=>marker);
        LightweightCharts.createSeriesMarkers(candles, markers);
      }
      chart.timeScale().fitContent();
    }
    if (!snapshot.series.length) byId("charts").textContent = "이 시점까지 수집된 완료 봉이 없습니다.";
    byId("status").textContent = snapshot.as_of_evaluated_at + " 기준 · 읽기전용";
    window.reviewSnapshot = snapshot;
  } catch (error) {
    if (version === requestVersion) {
      charts.forEach(chart=>chart.remove()); charts=[]; byId("charts").replaceChildren();
      ["verdict","freshness","profile","performance","unverified"].forEach(id=>byId(id).textContent="");
      ["reasons","facts","inferences","events"].forEach(id=>list(id,[]));
      byId("status").textContent = error.message; window.reviewSnapshot = null;
    }
  }
}
async function start() {
  byId("asof").value = new Date().toISOString();
  const response = await fetch("/api/tickers");
  if (!response.ok) throw new Error("보관 종목 목록을 읽지 못했습니다.");
  const tickers = await response.json();
  tickers.forEach(ticker=>{const option=document.createElement("option");option.value=ticker;option.textContent=ticker;byId("ticker").append(option);});
  list("candidates",tickers);
  byId("load").addEventListener("click",loadSnapshot);
  byId("ticker").addEventListener("change",loadSnapshot);
  if (tickers.length) await loadSnapshot();
}
start().catch(error=>byId("status").textContent=error.message);
