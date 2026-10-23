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
  const reasons={CLOCK_SYNC_REVIEW_REQUIRED:"PC 시간 동기화 확인 필요 · 미래 호가 제외",ORDERBOOK_CLOCK_STALE_OR_FUTURE:"호가 시각이 오래됐거나 미래임",SOURCE_EXECUTION_EXPIRED:"실행 원본 유효시간 만료"};
  if(health.status!=="AVAILABLE") { byId("paper-health").replaceChildren(paragraph("이 시점의 모의 운영 상태 기록이 없습니다. 주문·체결 여부를 추정하지 않습니다."));return; }
  byId("paper-health").replaceChildren(paragraph("최근 운영 점검: "+health.checked_at+(health.stale?" · 10분 경과·운영 확인 필요":"")+" · "+(health.enabled?"모의 운용 설정 켜짐":"모의 운용 설정 꺼짐")+" · 실주문 전송 0건"),
    table("시장별 모의 상태",["시장","현재 상태","최근 시세 관측","최근 모의 체결","대기 / 체결 / 거절 / 취소","차단 이유"],Object.entries(health.markets).map(([key,row])=>[
      key.toUpperCase(),(labels[row.status]||row.status)+(row.stale?" · 점검 10분 경과":""),row.last_quote_at||row.last_observation_at||"아직 없음",row.last_fill_at||"아직 없음",
      ["PENDING","FILLED","REJECTED","CANCELLED"].map(state=>number(row.order_counts[state])).join(" / "),row.blockers.map(code=>reasons[code]||code).join(", ")||"없음"])),
    paragraph("운영 점검 시각과 실제 시세·체결 시각은 별개입니다. 휴장 중 점검이 성공해도 체결 기록이 새로 생기지 않습니다."));
  if(health.markets.us)byId("paper-health").append(paragraph("원화 현금 모의 포트폴리오 / 미국 주식은 증권사 기준환율 평가 / 실제 달러계좌 수익률과 다름"));
}
function renderKisHealth(health) {
  const labels={READ_CONNECTION_VERIFIED:"조회 연결 확인",READY_TO_PROBE:"조회 점검 대기",MISSING_DEMO_SETTINGS:"모의 연결 설정 필요",CONFIGURATION_UNREADABLE:"모의 설정 확인 필요",CONNECTION_UNVERIFIED:"조회 연결 미확인",UNAVAILABLE:"이 시점의 조회 점검 기록 없음"};
  const markets=health.markets||{};
  byId("kis-demo-health").replaceChildren(table("KIS 모의 조회 점검",["시장","조회 연결","확인 시각","이 조회 점검의 범위","이 조회 점검에서 전송한 주문"],["KR","US"].map(market=>{
    const row=markets[market]||{};
    return [market==="KR"?"한국":"미국",labels[row.status]||labels.UNAVAILABLE,row.checked_at||"기록 없음","잔고·주문내역 조회",row.checked_at?0:"기록 없음"];
  })),paragraph("조회 성공은 주문·체결·취소 검증 완료를 뜻하지 않습니다. 주문 검증 결과는 아래 별도 기록으로 확인합니다."));
}
function renderKisValidation(health) {
  const labels={WAITING_SESSION:"다음 정규장 대기",RUNNING:"모의 서버 검증 진행",VERIFIED:"주문·체결·취소 확인 완료",BLOCKED:"조건 차단 · 확인 필요",ATTENTION:"미확정 결과 · 확인 필요",UNAVAILABLE:"이 시점의 주문 검증 기록 없음"};
  const blockers={MARKET_CLOSED:"정규장 대기",CALENDAR_UNVERIFIED:"거래일 확인 대기",SESSION_EDGE:"개장·마감 인접 시간 대기",HALTED:"운영 중지 설정",EVIDENCE_UNAVAILABLE:"현재 시세·계좌 확인 필요",AMBIGUOUS_ORDER:"주문 응답 미확정",AMBIGUOUS_CANCELLATION:"취소 응답 미확정",ORDER_REJECTED:"모의 주문 거절",ORDER_NOT_SENT:"주문 전송 전 차단",CAMPAIGN_BUDGET_EXHAUSTED:"검증 한도 도달",CANCELLATION_RACE:"취소 전 체결 발생",FILL_NOT_OBSERVED:"체결 확인 대기",STATE_INVALID:"운영 기록 확인 필요",JOURNAL_RECOVERY_REQUIRED:"주문 기록 복구 확인 필요",DAY_ORDER_REQUIRES_REVIEW:"당일 미완료 주문 확인 필요",CANCELLATION_REJECTED:"취소 거절",ORDER_REPORT_UNVERIFIED:"증권사 주문내역 확인 필요",CANCELLATION_NOT_CONFIRMED:"취소 완료 확인 대기",OPERATOR_REVIEW_REQUIRED:"운영 확인 필요"};
  const markets=health.markets||{};
  const clock=value=>value?new Date(value).toLocaleString("ko-KR",{timeZone:"Asia/Seoul",hour12:false})+" KST":"기록 없음";
  const stage=proof=>proof?.verified===true?"확인 · "+clock(proof.observed_at):"미검증";
  const heading=document.createElement("h3");heading.textContent="KIS 모의 주문·체결·취소 검증";
  const cards=document.createElement("div");cards.style.cssText="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,360px),1fr));gap:12px";
  for(const market of ["KR","US"]){
    const row=markets[market]||{};
    const card=document.createElement("article");card.style.cssText="min-width:0;border:1px solid #dce4ee;border-radius:8px;padding:12px";
    const title=document.createElement("h4");title.style.margin="0 0 8px";title.textContent=(market==="KR"?"한국":"미국")+" · "+(labels[row.status]||labels.UNAVAILABLE);card.append(title);
    if(row.blocker)card.append(paragraph(blockers[row.blocker]||blockers.OPERATOR_REVIEW_REQUIRED));
    card.append(paragraph("최근 점검: "+clock(row.checked_at)),table("검증 단계",["항목","증권사 결과"],[["모의 주문 접수",stage(row.stages?.submitted)],["모의 체결 확인",stage(row.stages?.filled)],["모의 취소 확인",stage(row.stages?.cancelled)]]));cards.append(card);
  }
  byId("kis-validation-health").replaceChildren(heading,cards,paragraph("접수는 체결과 다르며, 취소 요청 접수만으로 취소 완료를 표시하지 않습니다. 표시 시각은 증권사 결과를 확인한 한국 시각이며 실제 체결·정산 시각과 다를 수 있습니다. 이 화면은 읽기전용입니다."));
  if(Object.values(markets).some(row=>["ATTENTION","BLOCKED"].includes(row.status)))byId("kis-validation-health").append(paragraph("추가 확인이 필요한 기록이 있습니다. 미확정 주문은 자동 재전송하지 않습니다."));
}
async function loadOperational(asof,version) {
  const views=[['kis-strategy-health',renderKisStrategy,"KIS 전략 운영 기록을 읽지 못했습니다."],['paper-health',renderHealth,"모의 운영 상태를 읽지 못했습니다."],['kis-demo-health',renderKisHealth,"모의 서버 조회 점검 기록을 읽지 못했습니다."],['kis-validation-health',renderKisValidation,"모의 서버 주문 검증 기록을 읽지 못했습니다."]];
  views.forEach(([id])=>byId(id).replaceChildren(paragraph("운영 기록을 확인하고 있습니다.")));
  const results=await Promise.allSettled(views.map(([id])=>getJson("/api/"+id+"?as_of="+encodeURIComponent(asof))));
  if(version!==requestVersion)return;
  views.forEach(([id,render,error],index)=>results[index].status==="fulfilled"?render(results[index].value):byId(id).replaceChildren(paragraph(error)));
}
function renderKisStrategy(payload) {
  const target=byId("kis-strategy-health");
  if(payload.status!=="AVAILABLE"){target.replaceChildren(paragraph("지속 모의매매 운영 기록 대기"));return;}
  const labels={DISABLED:"운용 꺼짐",WAITING_VALIDATION:"정규장 검증 통과 대기",WAITING_SIGNAL:"유효한 새 전략 신호 대기",MARKET_CLOSED:"정규장 대기",BLOCKED:"조건 차단 · 이유 확인",ACTIVE:"전략 모의 운용 중"};
  const reasons={STRATEGY_ACCOUNT_POSITION_UNVERIFIED:"모의계좌 보유 수량과 전략 체결 기록 대조 필요",SOURCE_EVIDENCE_UNVERIFIED:"원래 전략 보고서의 시각·판단 근거 확인 필요",DAILY_ORDER_LIMIT:"오늘의 원주문 시도 한도 도달",NO_STRATEGY_QUANTITY_WITHIN_LIMITS:"모의 보유 수량·주문 한도 내 수량 없음",BUDGET_FX_UNVERIFIED:"전략 예산의 달러 환산 근거 확인 필요",PROPOSAL_QUANTITY_INVALID:"제안 수량 확인 필요",CANDIDATE_EVIDENCE_UNVERIFIED:"후보의 최신 시세·계좌 근거 확인 필요",VALIDATION_REQUIRED:"이 시장의 주문·체결·취소 검증 필요",NO_FRESH_EXECUTABLE_STRATEGY:"유효 시간 내 실행 가능한 새 전략 없음",HALTED:"운영 중지 설정",MARKET_CLOSED:"정규장 대기",SESSION_EDGE:"개장·마감 인접 시간",CALENDAR_UNVERIFIED:"거래일 확인 필요",AMBIGUOUS_ORDER:"미확정 주문 확인 필요",ORDER_REPORT_UNVERIFIED:"주문내역 확인 필요",SUBMISSION_BLOCKED_OR_UNRESOLVED:"주문 조건 차단 또는 응답 확인 필요",VALUATION_UNVERIFIED:"평가 시세 미확인",RUNTIME_EVIDENCE_UNVERIFIED:"전략·시세·계좌 근거 확인 필요",PREVIOUS_SESSION_ORDER_UNRESOLVED:"이전 거래일 미완료 주문 확인 필요"};
  const states={ACKNOWLEDGED:"접수",OPEN:"미체결",PARTIAL:"부분체결",FILLED:"체결 완료",CANCELLED:"취소 완료",REJECTED:"거절",NOT_SENT:"미전송",BLOCKED:"조건 차단",UNKNOWN:"응답 미확정",UNRESOLVED:"대조 필요"};
  Object.assign(reasons,{SOURCE_EXECUTION_EXPIRED:"실행 원본 유효시간 만료",SOURCE_SIGNALS_EXPIRED_OR_UNDATED:"개별 신호의 시세 시각 만료·미확인",SOURCE_DATA_NOT_EXECUTION_READY:"실행에 필요한 시세·거래상태 자료 미충족",NO_RECENT_COMPLETED_SOURCE:"최근 완료된 분석 원본 없음"});
  const clock=value=>value?new Date(value).toLocaleString("ko-KR",{timeZone:"Asia/Seoul",hour12:false}):"확인 전";
  target.replaceChildren(paragraph("최근 점검: "+clock(payload.checked_at)+(payload.stale?" · 3분 이상 경과·운영 확인 필요":"")+" · 실계좌 자동 주문 비활성"));
  for(const market of ["KR","US"]){
    const row=payload.markets?.[market];if(!row)continue;
    const card=document.createElement("article");card.className="panel";
    const title=document.createElement("h3");title.textContent=(market==="KR"?"국내":"미국")+" · "+labels[row.status];card.append(title);
    card.append(paragraph("정규장 연결 검증: "+(row.gate_passed?"통과":"대기")+" · "+(row.blockers||[]).map(code=>reasons[code]||"운영 확인 필요").join(" / ")));
    const diagnostic=row.source_diagnostics;
    if(diagnostic?.strategy_rows!==undefined)card.append(paragraph("분석 "+number(diagnostic.strategy_rows)+"종목 · 신선한 관측자료 "+number(diagnostic.execution_ready_rows)+"종목"+(typeof diagnostic.allocated_orders==="number"?" · 보고서 배정 주문 "+number(diagnostic.allocated_orders)+"건":"")+". 시세 준비는 매수·매도 승인이 아닙니다."));
    const allocation=row.allocation_diagnostics;
    if(allocation){
      const planningReasons={NO_AUTHORIZED_EXECUTION_ACTION:"실행 엔진의 매수·매도 행동 없음",OUTSIDE_APPROVED_UNIVERSE:"허용 종목 밖",NO_STRATEGY_OWNED_POSITION:"정상 전략 소유 보유분 없음",STRATEGY_POSITION_ALREADY_OPEN:"이미 보유 중인 전략 종목",STRATEGY_OBSERVATION_NOT_EXECUTABLE:"시세 만료·실행 자료 미충족",STRATEGY_LINEAGE_MISMATCH:"연구·실행 계보 불일치",ENTRY_ORIGINAL_RESEARCH_UNVERIFIED:"원래 연구 확인 필요",ENTRY_RESEARCH_DECISION_MISMATCH:"원래 연구와 파생 판단 불일치",ENTRY_NOT_AUTHORIZED_BY_RESEARCH:"원래 연구의 매수 승인 없음",ENTRY_AUTHORIZATION_MISMATCH:"승인 내용 불일치",ENTRY_RESEARCH_EXPIRED:"원래 연구 유효시간 만료",ENTRY_RESEARCH_REVIEW_REQUIRED:"연구 재검토 필요",ENTRY_RESEARCH_EVIDENCE_INCOMPLETE:"필수 연구 자료 미충족",STRATEGY_AUTHORIZATION_EXPIRED:"조건부 승인 만료",SELL_SIZE_REQUIRES_EXPLICIT_ALLOCATION:"매도 수량의 원래 근거 필요",STRATEGY_EVIDENCE_UNVERIFIED:"전략 근거 확인 필요"};
      card.append(paragraph("계획 검사 통과 후보 "+number(allocation.eligible_candidates)+"개 · 정상 전략 소유 보유 종목 "+number(allocation.strategy_owned_positions)+"개. 계좌·호가·위험 한도는 주문 직전에 다시 검사합니다."));
      if(Object.keys(allocation.reason_counts||{}).length)card.append(table("주문까지 가지 못한 이유",["이유","종목 수"],Object.entries(allocation.reason_counts).map(([reason,count])=>[planningReasons[reason]||"근거 확인 필요",number(count)])));
    }else card.append(paragraph("이번 점검에는 종목별 주문 계획 검사 결과가 없습니다. 휴장·점검 성공만으로 매매 준비 완료를 판단하지 않습니다."));
    const refresh=row.refresh_health;
    const refreshLabels={RETRY_LIMIT_REACHED:"당일 시세 갱신 재시도 한도 소진",LAST_ATTEMPT_FAILED:"최근 시세 갱신 실패",LAST_ATTEMPT_COMPLETED:"최근 시세 갱신 완료 · 연속 신선도는 별도 검증",COMPLETION_UNVERIFIED:"시세 갱신 시작 기록 · 현재 실행 여부와 완료 미확인",PREVIOUS_SESSION:"이전 거래일의 갱신 기록",UNVERIFIED:"시세 갱신 기록 검증 필요",UNAVAILABLE:"시세 갱신 기록 미수집"};
    card.append(paragraph("시세 생산: "+(refreshLabels[refresh?.status]||refreshLabels.UNAVAILABLE)+(refresh?.session_date?" · 거래일 "+refresh.session_date+" · 연속 실패 "+number(refresh.consecutive_failures)+"/"+number(refresh.max_consecutive_failures):"")));
    if(refresh?.error_type==="LocalStorageHeadroomError")card.append(paragraph("마지막 실패 원인은 저장공간 부족입니다. 현재 여유 공간과 다음 정상 생산을 별도로 확인해야 하며, 공간이 늘어도 소진한 재시도 한도는 초기화되지 않습니다."));
    if(diagnostic?.reason_counts?.limited_halt_status)card.append(paragraph("거래정지 상태를 확인하지 못한 종목이 있어 실행이 제한됩니다."));
    const perf=row.performance;
    card.append(paragraph("전략 누적 평가손익(비용 전): "+(perf?.status==="AVAILABLE"?number(perf.gross_pnl)+" "+perf.currency:perf?.status==="NO_FILLS"?"아직 체결 없음":"체결 금액·평가 시세 확인 대기")));
    const evaluation=row.evaluation;
    if(evaluation){
      const sample=evaluation.sample||{};
      card.append(paragraph("정상 전략 체결 표본: 매수 "+number(sample.buy_filled_orders)+"건 · 매도 "+number(sample.sell_filled_orders)+"건 · 보유분 청산 왕복 "+number(sample.closed_inventory_episodes)+"회 · 주문 거래일 "+number(sample.order_session_count)+"일"));
      if(evaluation.status!=="NO_FILLS")card.append(table("가정 비용 민감도 · 실제 순손익 아님",["총 체결대금 대비 가정 비용","가정 비용액","가정 비용 차감 후 손익"],(evaluation.cost_sensitivity?.scenarios||[]).map(s=>[
        number(s.assumed_cost_bps_on_turnover/100)+"%",number(s.estimated_cost)+" "+evaluation.currency,number(s.estimated_pnl_after_assumed_cost)+" "+evaluation.currency])));
      const unmet={ACTUAL_FEES_TAXES_FX_UNVERIFIED:"실제 수수료·세금·환전비용",SETTLEMENT_UNVERIFIED:"정산",BROKER_CORRECTIONS_UNVERIFIED:"증권사 사후 체결 정정",STATISTICAL_AND_OUT_OF_SAMPLE_VALIDATION_REQUIRED:"반복 표본·별도 기간 성과 검증",NO_STRATEGY_FILLS:"정상 전략 체결",STRATEGY_BUY_FILL_REQUIRED:"정상 전략 매수 체결",STRATEGY_SELL_FILL_REQUIRED:"정상 전략 매도 체결",CLOSED_STRATEGY_ROUND_TRIP_UNVERIFIED:"정상 전략 왕복 체결",FILL_NOTIONAL_UNVERIFIED:"체결 대금",GROSS_VALUATION_INCOMPLETE:"보유분 평가",OPEN_STRATEGY_INVENTORY:"열린 보유분의 청산 평가",ORDER_PENDING_OR_UNRESOLVED:"미결·미확정 주문 대사"};
      card.append(paragraph("실투자 판단 미충족: "+(evaluation.unmet_criteria||[]).map(code=>unmet[code]||"근거 확인").join(" · ")+". 실투자로 자동 전환하지 않습니다."));
      if(evaluation.status!=="NO_FILLS")card.append(paragraph("0.1%·0.3%·0.5%는 이미 확인한 매수·매도 체결대금에 적용한 비교 가정입니다. 실제 증권사 요율이 아니며, 앞으로 보유분을 매도할 비용은 포함하지 않습니다."));
    }
    if(row.performance_history?.length)card.append(table("최근 확인한 성과",["평가 확인 시각 (한국시간)","누적 평가손익 · 비용 전"],row.performance_history.slice(-10).reverse().map(p=>[clock(p.observed_at),number(p.gross_pnl)+" "+p.currency])));
    card.append(table("전략 주문·체결·취소",["종목 / 전략 실행","방향","주문 / 체결 수량","지정가 / 평균 체결가","상태 / 취소","마지막 확인 (한국시간)"],(row.orders||[]).slice().reverse().map(order=>[
      order.ticker+" / "+order.run_id,order.side==="BUY"?"매수":"매도",number(order.quantity)+" / "+number(order.filled_quantity),number(order.limit_price)+" / "+number(order.average_fill_price),
      (states[order.status]||"확인 필요")+" / "+(order.cancel_status==="CONFIRMED"?"취소 확인":order.cancel_status==="ACKNOWLEDGED"?"취소 요청 접수":order.cancel_status?"취소 결과 확인 필요":"—"),clock(order.observed_at||order.prepared_at)])));
    target.append(card);
  }
  target.append(paragraph("손익은 이 전략의 확인된 체결 대금과 보유 수량의 최신 시세 평가를 합산합니다. 국내는 원화, 미국은 달러로 구분하며 계좌 전체 수익률이 아닙니다. 비용·정산이 확인되지 않아 순손익은 표시하지 않습니다. 접수는 체결과 다릅니다."));
  target.append(paragraph("검증 순서: 정상 연구·원래 승인 → 신선한 시세·계좌·한도 검사 → 모의 주문·체결 → 실제 비용·정산 → 반복 표본·별도 기간 성과. 실투자는 이 근거를 검토한 뒤 별도 승인하며 수익을 보장하거나 자동 전환하지 않습니다."));
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
  ["verdict","freshness","profile","performance","unverified","source-context","experiment-cards"].forEach(id=>byId(id).textContent="");
  ["reasons","facts","inferences","events"].forEach(id=>list(id,[]));window.reviewSnapshot=null;
}
async function loadSnapshot() {
  const version = ++requestVersion;
  byId("status").textContent = "기준 시각의 자료를 확인하고 있습니다.";
  const params = new URLSearchParams({ ticker: byId("ticker").value, as_of: byId("asof").value });
  // Operational receipts must remain visible even when a ticker has no chart.
  const operational = loadOperational(params.get("as_of"),version);
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
    const secondary=await Promise.allSettled([getJson("/api/experiment-cards?as_of="+encodeURIComponent(snapshot.as_of_evaluated_at)),operational]);
    if(version!==requestVersion)return;
    if(secondary[0].status==="fulfilled")renderCards(secondary[0].value);else byId("experiment-cards").replaceChildren(paragraph("실험 카드를 읽지 못했습니다."));
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
  } finally {
    await operational;
  }
}
async function refreshCatalog() {
  const selected=byId("ticker").value;
  const tickers=await getJson("/api/tickers?as_of="+encodeURIComponent(byId("asof").value));
  byId("ticker").replaceChildren(...tickers.map(ticker=>{const option=document.createElement("option");option.value=ticker;option.textContent=ticker;return option;}));
  if(tickers.includes(selected))byId("ticker").value=selected;
  list("candidates",tickers);
  if(!tickers.length){const version=++requestVersion;clearSnapshot();byId("status").textContent="이 시점까지 완료된 분석이 없습니다.";await loadOperational(byId("asof").value,version);return false;}return true;
}
async function start() {
  byId("asof").value = new Date().toISOString();
  byId("load").addEventListener("click",loadSnapshot);
  byId("ticker").addEventListener("change",loadSnapshot);
  byId("asof").addEventListener("input",()=>byId("follow-current").checked=false);
  byId("compile-condition").addEventListener("click",compileCondition);
  byId("refresh-catalog").addEventListener("click",async()=>{
    if(byId("follow-current").checked)byId("asof").value=new Date().toISOString();
    const version=++requestVersion;
    const operational=loadOperational(byId("asof").value,version);
    try{if(await refreshCatalog())await loadSnapshot();}
    catch(error){if(version===requestVersion)byId("status").textContent=error.message;}
    finally{await operational;}
  });
  setInterval(()=>{if(byId("follow-current").checked)byId("refresh-catalog").click();},60000);
  byId("refresh-catalog").click();
}
start().catch(error=>byId("status").textContent=error.message);
