/* Display only: all evidence filtering and indicators come from the snapshot API. */
"use strict";
const byId = id => document.getElementById(id);
let charts = [];
let requestVersion = 0;
const number = value => typeof value === "number" && Number.isFinite(value) ? value.toLocaleString("ko-KR", {maximumFractionDigits:3}) : "확인 불가";
const display = value => value === null || value === undefined ? "확인 불가" : typeof value === "object" ? JSON.stringify(value) : String(value);
function paragraph(text) { const element=document.createElement("p");element.textContent=text;return element; }
async function getJson(url) { const response=await fetch(url);if(!response.ok)throw Error("자료를 읽지 못했습니다.");return response.json(); }
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
function renderHealth(health) {
  const labels={MARKET_CLOSED:"휴장·장 종료",WAITING_SOURCE:"새 분석·시세 대기",ACTIVE:"모의 점검 진행",VALUATION_ONLY:"보유 평가만 진행 · 신규 판단 대기",BLOCKED:"조건 차단",ERROR:"점검 오류"};
  if(health.status!=="AVAILABLE") { byId("paper-health").replaceChildren(paragraph("이 시점의 모의 운영 상태 기록이 없습니다. 주문·체결 여부를 추정하지 않습니다."));return; }
  byId("paper-health").replaceChildren(paragraph("최근 운영 점검: "+health.checked_at+(health.stale?" · 10분 경과·운영 확인 필요":"")+" · "+(health.enabled?"모의 운용 설정 켜짐":"모의 운용 설정 꺼짐")+" · 실주문 전송 0건"),
    table("시장별 모의 상태",["시장","현재 상태","최근 시세 관측","최근 모의 체결","대기 / 체결 / 거절 / 취소","차단 이유"],Object.entries(health.markets).map(([key,row])=>[
      key.toUpperCase(),labels[row.status]||row.status,row.last_quote_at||row.last_observation_at||"아직 없음",row.last_fill_at||"아직 없음",
      ["PENDING","FILLED","REJECTED","CANCELLED"].map(state=>number(row.order_counts[state])).join(" / "),row.blockers.join(", ")||"없음"])),
    paragraph("운영 점검 시각과 실제 시세·체결 시각은 별개입니다. 휴장 중 점검이 성공해도 체결 기록이 새로 생기지 않습니다."));
  if(health.markets.us)byId("paper-health").append(paragraph("원화 현금 모의 포트폴리오 / 미국 주식은 증권사 기준환율 평가 / 실제 달러계좌 수익률과 다름"));
}
function renderCards(payload) {
  const cards=payload.cards||[];
  const nodes=[];
  if(!cards.length)nodes.push(paragraph("이 시점에 등록된 실험이 없습니다. 먼저 규칙과 동일 자본·비용을 등록하고 동결해야 미래 모의 비교가 시작됩니다."));
  for(const card of cards){
    const article=document.createElement("article");article.className="panel";
    const title=document.createElement("h4");title.textContent=card.id+" · "+(card.status_label||card.status);article.append(title);
    article.append(paragraph(card.hypothesis||"가설 설명 없음"));
    const labels={baseline:"기존 규칙",ai:"AI 보강 규칙",universe:"대상 종목",benchmark:"기준지수",training_end:"연구 종료 시각",forward_start:"미래 관측 시작",forward_end:"미래 관측 종료",dataset_versions:"데이터 버전",input_data_as_of:"입력 자료 기준 시각",initial_capital:"시작 가상자본",currency:"통화",fee_bps_per_side:"편도 수수료 (bp)",slippage_bps_per_side:"편도 슬리피지 (bp)",model_cost:"모델 비용",validation_seconds:"검증 시간 (초)"};
    for(const [key,label] of [["rules","고정 규칙"],["data","대상·데이터"],["costs","자본·비용"]]){
      const value=card[key];if(value&&typeof value==="object")article.append(table(label,["항목","기록"],Object.entries(value).filter(([name])=>name!=="status").map(([name,item])=>[labels[name]||name,display(item)])));
    }
    article.append(paragraph("모델: "+(card.model?.status==="not_recorded"?"알 수 없음 (식별자 미기록)":display(card.model?.declared))));
    article.append(paragraph(card.results?.message||"성과 관측 기록 없음"));
    if(card.results?.arms)article.append(table("동일 조건의 미래 모의 성과",["실험군","기록"],Object.entries(card.results.arms).map(([name,value])=>[name,display(value)])));
    article.append(paragraph("규칙 해시: "+(card.spec_hash||"미확인")+" · 기준 "+(card.as_of||payload.as_of)));
    for(const limitation of card.limitations||[])article.append(paragraph(limitation));
    nodes.push(article);
  }
  byId("experiment-cards").replaceChildren(...nodes);
}
async function compileCondition() {
  byId("condition-draft").replaceChildren(paragraph("조건을 검토하고 있습니다."));
  try {
    const params=new URLSearchParams({text:byId("condition-text").value,market:byId("condition-market").value});
    const draft=await getJson("/api/condition-draft?"+params);
    const nodes=[paragraph(draft.status==="compiled"?"조건 초안 변환 완료 · 저장·활성화 안 됨":"조건을 더 구체적으로 입력해 주세요.")];
    for(const rule of draft.normalized_rules||[])nodes.push(paragraph(rule));
    for(const issue of draft.issues||[])nodes.push(paragraph(issue));
    if(draft.condition){const details=document.createElement("details"),summary=document.createElement("summary"),pre=document.createElement("pre");summary.textContent="기존 스캐너 조건 형식 확인";pre.textContent=JSON.stringify(draft.condition,null,2);details.append(summary,pre);nodes.push(details);}
    byId("condition-draft").replaceChildren(...nodes);window.conditionDraft=draft;
  }catch(error){byId("condition-draft").replaceChildren(paragraph(error.message));window.conditionDraft=null;}
}
function list(id, values) {
  byId(id).replaceChildren(...values.map(value => {
    const item = document.createElement("li"); item.textContent = value; return item;
  }));
}
function clearSnapshot() {
  charts.forEach(chart=>chart.remove());charts=[];byId("charts").replaceChildren();
  ["verdict","freshness","profile","performance","unverified","source-context","paper-health","experiment-cards"].forEach(id=>byId(id).textContent="");
  ["reasons","facts","inferences","events"].forEach(id=>list(id,[]));window.reviewSnapshot=null;
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
    const source=snapshot.source_context||{};
    byId("source-context").textContent="원본 실행: "+(source.run_id||"미확인")+" · 연구 완료 "+(source.research_finished_at||"시각 미확인")+" · 완료 봉 "+snapshot.series.reduce((sum,item)=>sum+item.bars.length,0)+"개 · 이벤트 "+snapshot.events.events.length+"건";
    if(source.chart_capture_status){
      const capture=source.chart_capture_status;
      byId("source-context").textContent+=" · 차트 갱신 "+(capture.status==="REFRESHED"?"확인":"자료 확보 실패·원본 유지")+" "+capture.checked_at;
      if(capture.error_type)byId("source-context").textContent+=" ("+capture.error_type+")";
    }
    const secondary=await Promise.allSettled([getJson("/api/paper-health?as_of="+encodeURIComponent(snapshot.as_of_evaluated_at)),getJson("/api/experiment-cards?as_of="+encodeURIComponent(snapshot.as_of_evaluated_at))]);
    if(version!==requestVersion)return;
    if(secondary[0].status==="fulfilled")renderHealth(secondary[0].value);else byId("paper-health").replaceChildren(paragraph("모의 운영 상태를 읽지 못했습니다."));
    if(secondary[1].status==="fulfilled")renderCards(secondary[1].value);else byId("experiment-cards").replaceChildren(paragraph("실험 카드를 읽지 못했습니다."));
    byId("verdict").textContent = snapshot.execution_verdict
      ? "당시 판단: " + snapshot.execution_verdict + " · " + snapshot.execution.execution_asof
      : "판단 기록 없음";
    if(snapshot.execution.provenance==="reobserved_archive")byId("verdict").textContent+=" · 현재 재관측한 과거 기록 ("+snapshot.execution.archive_observed_at+")";
    const freshnessLabels = {FRESH:"10분 미만",STALE:"10분 경과·재확인 필요",MISSING:"관측 시각 없음",INVALID:"시각 확인 필요",FUTURE:"미래 시각 차단"};
    const researchLabels = {FRESH_REGULAR_SESSION:"정규장 자료 확인",EXTENDED_SESSION_RESEARCH_ONLY:"장전·장후 참고 자료",LATEST_REGULAR_CLOSE_RESEARCH_ONLY:"최근 정규장 종가 확인",UNVERIFIED_RESEARCH_INPUT:"유효성 미확인"};
    byId("freshness").textContent = "실행 시세: " + (freshnessLabels[snapshot.freshness_status]||snapshot.freshness_status)
      + " · 연구 자료: " + (researchLabels[snapshot.research_status]||snapshot.research_status);
    byId("freshness").title = snapshot.freshness_status + " / " + snapshot.research_status;
    list("reasons", snapshot.block_reasons);
    list("facts", snapshot.evidence_summary.facts.length?snapshot.evidence_summary.facts.map(row => row.claim):["확인 시각을 검증한 사실 기록이 없습니다."]);
    list("inferences", snapshot.evidence_summary.inferences.length?snapshot.evidence_summary.inferences.map(row => row.claim):["이 시점의 추론 기록이 없습니다."]);
    byId("unverified").textContent = "시각 미검증 근거 " + snapshot.evidence_summary.unverified_count + "건 제외";
    list("events", snapshot.events.events.length?snapshot.events.events.map(row => (row.title || "공시") + " · 발표 " + (row.published_at || "시각 미확인") + " · 최초 감지 " + (row.first_seen_at || "별도 기록 없음") + " · 관측 " + row.observed_at + " · 정정 " + (row.is_amended ? "예" : "아니오") + " · 버전 " + row.version_id):["발표·정정 시각을 검증한 이벤트 기록이 없습니다. 일정이 없다는 뜻은 아닙니다."]);
    renderPerformance(snapshot.lifecycle);
    renderProfile(snapshot.series);
    for (const item of snapshot.series) {
      const wrapper = document.createElement("div");
      const label = document.createElement("h3"); label.textContent = item.interval + " · UTC";
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
      snapshot.price_levels.forEach(level=>candles.createPriceLine({price:level.price,title:level.label,lineStyle:({DOTTED:LightweightCharts.LineStyle.Dotted,SOLID:LightweightCharts.LineStyle.Solid,DASHED:LightweightCharts.LineStyle.Dashed})[level.style] ?? LightweightCharts.LineStyle.Dashed,color:"#90642f"}));
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
      clearSnapshot();byId("status").textContent = error.message;
    }
  }
}
async function refreshCatalog() {
  const selected=byId("ticker").value;
  const tickers=await getJson("/api/tickers?as_of="+encodeURIComponent(byId("asof").value));
  byId("ticker").replaceChildren(...tickers.map(ticker=>{const option=document.createElement("option");option.value=ticker;option.textContent=ticker;return option;}));
  if(tickers.includes(selected))byId("ticker").value=selected;
  list("candidates",tickers);
  if(!tickers.length){clearSnapshot();byId("status").textContent="이 시점까지 완료된 분석이 없습니다.";return false;}return true;
}
async function start() {
  byId("asof").value = new Date().toISOString();
  const available=await refreshCatalog();
  byId("load").addEventListener("click",loadSnapshot);
  byId("ticker").addEventListener("change",loadSnapshot);
  byId("asof").addEventListener("input",()=>byId("follow-current").checked=false);
  byId("compile-condition").addEventListener("click",compileCondition);
  byId("refresh-catalog").addEventListener("click",async()=>{if(byId("follow-current").checked)byId("asof").value=new Date().toISOString();try{if(await refreshCatalog())await loadSnapshot();}catch(error){byId("status").textContent=error.message;}});
  setInterval(()=>{if(byId("follow-current").checked)byId("refresh-catalog").click();},60000);
  if (available) await loadSnapshot();
}
start().catch(error=>byId("status").textContent=error.message);
