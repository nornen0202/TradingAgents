"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),test=require("node:test"),vm=require("node:vm");
const root=path.resolve(__dirname,"../..");
const source=fs.readFileSync(path.join(root,"tradingagents/charting/static/viewer.js"),"utf8")
  .replace(/start\(\)\.catch\(error=>byId\("status"\)\.textContent=error\.message\);\s*$/,"");
function harness(){
  class Element{
    constructor(tag="div"){this.tag=tag;this.children=[];this.style={};this.className="";this.checked=false;this.disabled=false;this.isConnected=true;this.attributes={};this.listeners={};this._text="";}
    set textContent(value){this._text=String(value);this.children=[];}
    get textContent(){return this._text+this.children.map(c=>typeof c==="string"?c:c.textContent).join("");}
    append(...values){this.children.push(...values);}
    replaceChildren(...values){this._text="";this.children=values;}
    setAttribute(key,value){this.attributes[key]=value;}
    addEventListener(type,callback){this.listeners[type]=callback;}
    change(value){this.checked=value;this.listeners.change?.();}
    querySelectorAll(tag){return this.children.filter(c=>typeof c!=="string").flatMap(c=>[...(c.tag===tag?[c]:[]),...c.querySelectorAll(tag)]);}
  }
  const ids=["historical-signal-records","price-levels","charts","verdict","freshness","profile","performance","unverified","source-context","experiment-cards","reasons","facts","inferences","events"];
  const nodes=new Map(ids.map(id=>[id,new Element()]));
  const document={getElementById:id=>nodes.get(id)||null,createElement:tag=>new Element(tag),head:new Element("head")};
  const context=vm.createContext({document,window:{},LightweightCharts:{LineStyle:{Dotted:1,Solid:0,Dashed:2}},console});
  vm.runInContext(source,context);
  return {context,nodes,run:code=>vm.runInContext(code,context)};
}
function plain(value){return JSON.parse(JSON.stringify(value));}
const marker=(category,text,time=1792137600)=>({category,text,time,position:"belowBar",shape:"arrowUp",color:"#13785f"});
test("only SIGNAL text is hidden; original order, duplicates and all fills/other kinds remain exact",()=>{
  const h=harness(),markers=[marker("SIGNAL","추천 · ADD_IF_CONFIRMED"),marker("SIGNAL","추천 · ADD_IF_CONFIRMED"),
    marker("REAL_FILL","실제 체결 · BUY"),marker("DEMO_FILL","데모 체결 · SELL"),marker("PAPER_FILL","모의 체결 · BUY"),
    marker("EVENT_GUARD","공시"),marker("BLOCK_REASON","차단"),marker("UNRECOGNIZED","원래 문구")];
  const before=JSON.stringify(markers),hidden=plain(h.context.chartMarkerProjection(markers,false));
  assert.equal(hidden.length,markers.length);
  markers.forEach(({category,...original},index)=>assert.deepEqual(hidden[index],category==="SIGNAL"?{...original,text:""}:original));
  assert.deepEqual(plain(h.context.chartMarkerProjection(markers,true)),markers.map(({category,...original})=>original));
  assert.equal(JSON.stringify(markers),before);assert.deepEqual(plain(h.context.chartMarkerProjection([],false)),[]);
});
test("original marker text and raw precise clocks stay accessible without invented pairing or private fields",()=>{
  const h=harness(),raw="2026-10-16T09:00:00.123456+00:00",payload={action:"<img src=x onerror=bad>",side:"BUY",source:"TradingAgents",run_id:"20261016T090000_full",
    account:"PRIVATE_ACCOUNT",order_id:"PRIVATE_ORDER",owner:"PRIVATE_OWNER",path:"C:/PRIVATE_PATH",nested:{secret:"PRIVATE_NESTED"}};
  const event={kind:"SIGNAL",occurred_at:raw,available_at:"2026-10-16T09:00:01.123457Z",ingested_at:"2026-10-16T09:00:02.123458+00:00",payload};
  const snapshot={source_context:{run_id:"GLOBAL_RUN_NOT_INDIVIDUAL"},markers:[marker("SIGNAL","추천 · <img src=x onerror=bad>"),marker("SIGNAL","추천 · duplicate"),marker("DEMO_FILL","데모 체결")],
    lifecycle:{events:[event,event,{kind:"SIGNAL",payload:{action:"WAIT",source:{secret:"PRIVATE_SOURCE_OBJECT"},run_id:"C:/PRIVATE_RUN"},occurred_at:null,available_at:{secret:"PRIVATE_CLOCK"}},
      {kind:"FILL",payload:{action:"PRIVATE_FILL_ACTION"}}]}};
  const before=JSON.stringify(snapshot);h.context.renderHistoricalSignals(snapshot);
  const area=h.nodes.get("historical-signal-records"),tables=area.querySelectorAll("table"),rows=tables.map(t=>t.querySelectorAll("tr").slice(1));
  assert.equal(rows[0].length,2);assert.equal(rows[1].length,3);
  assert.equal(rows[0][0].children[1].textContent,snapshot.markers[0].text);
  assert.equal(rows[0][0].children[2].textContent,String(snapshot.markers[0].time));
  assert.equal(rows[1][0].children[1].textContent,rows[1][1].children[1].textContent);
  for(const clock of [raw,event.available_at,event.ingested_at])assert.ok(area.textContent.includes(clock));
  assert.match(area.textContent,/사건: 미제공/);assert.match(area.textContent,/형식 미확인/);
  assert.match(area.textContent,/과거 추천은 현재 승인이나 체결이 아닙니다/);assert.match(area.textContent,/두 표의 행을 임의로 서로 연결하지 않습니다/);
  assert.match(area.textContent,/초 단위 표시 좌표이며 원래 정밀 시각이 아닙니다/);
  assert.doesNotMatch(area.textContent,/PRIVATE_|GLOBAL_RUN_NOT_INDIVIDUAL/);
  assert.equal(area.querySelectorAll("img").length,0);assert.equal(JSON.stringify(snapshot),before);
  const regions=area.querySelectorAll("div").filter(e=>e.className==="review-table-scroll");
  assert.equal(regions.length,2);regions.forEach(e=>{assert.equal(e.tabIndex,0);assert.equal(e.attributes.role,"region");});
});
test("no events or clocks never borrow the selected run or a converted marker second",()=>{
  const h=harness();h.context.renderHistoricalSignals({markers:[marker("SIGNAL","추천 · WAIT")],lifecycle:{events:[]},source_context:{run_id:"CAPTURED_RUN_ONLY"}});
  const area=h.nodes.get("historical-signal-records");assert.match(area.textContent,/도표 문구 1개 \/ 원장 기록 0개/);
  assert.doesNotMatch(area.textContent,/CAPTURED_RUN_ONLY|2026-10-16T/);assert.match(area.textContent,/연결된 기록이 없습니다/);
  assert.match(area.textContent,/원장 원문·정밀 시각은 이 응답에 제공되지 않았습니다/);
  h.context.renderHistoricalSignals({markers:[],lifecycle:{events:[{kind:"SIGNAL",payload:{action:{private:"SECRET_ACTION"},side:{private:"SECRET_SIDE"}}}]}});
  assert.match(area.textContent,/원문 문자열 미제공/);assert.match(area.textContent,/원장 기록 1개/);
  assert.doesNotMatch(area.textContent,/SECRET_ACTION|SECRET_SIDE/);
});
test("two chart controls have independent native labels; old version, detached and removed chart handles do nothing",()=>{
  const h=harness(),markers=[marker("SIGNAL","추천 · WAIT"),marker("DEMO_FILL","데모 체결 · BUY")],callsA=[],callsB=[];
  const chartA={remove(){}},chartB={remove(){}},elementA={id:"chart-a"},elementB={id:"chart-b"};
  h.context.chartA=chartA;h.context.chartB=chartB;h.run("requestVersion=7;charts=[chartA,chartB]");
  const a=h.context.signalTextControl(markers,elementA,"1d",7,0),b=h.context.signalTextControl(markers,elementB,"1m",7,1);
  const apiA={setMarkers:value=>callsA.push(plain(value))},apiB={setMarkers:value=>callsB.push(plain(value))};
  h.context.bindSignalTextControl(a.toggle,chartA,apiA,markers,7,elementA.id);h.context.bindSignalTextControl(b.toggle,chartB,apiB,markers,7,elementB.id);
  assert.notEqual(a.toggle.id,b.toggle.id);assert.equal(a.toggle.type,"checkbox");assert.equal(a.toggle.checked,false);assert.equal(a.toggle.disabled,false);
  assert.equal(a.toggle.attributes["aria-controls"],"chart-a");assert.equal(a.toggle.attributes["aria-describedby"],"chart-signal-hint");
  a.toggle.change(true);assert.equal(callsA.length,1);assert.equal(callsA[0][0].text,markers[0].text);assert.equal(callsB.length,0);
  a.toggle.change(false);assert.equal(callsA[1][0].text,"");assert.equal(callsA[1][1].text,markers[1].text);
  b.toggle.change(true);assert.equal(callsB.length,1);assert.equal(callsB[0][0].text,markers[0].text);
  h.run("requestVersion=8");a.toggle.change(true);assert.equal(callsA.length,2);
  h.run("requestVersion=7");a.toggle.isConnected=false;a.toggle.change(false);assert.equal(callsA.length,2);
  a.toggle.isConnected=true;h.context.clearSnapshot();a.toggle.change(true);assert.equal(callsA.length,2);assert.equal(h.run("chartSignalMarkers.length"),0);
  assert.equal(h.context.signalTextControl([],elementA,"1d",8,0).toggle.disabled,true);
  assert.equal(h.context.signalTextControl([marker("DEMO_FILL","fill")],elementA,"1d",8,1).toggle.disabled,true);
});
test("native controls and historical records have their own hint and local scrolling styles",()=>{
  const html=fs.readFileSync(path.join(root,"tradingagents/charting/static/viewer.html"),"utf8");
  assert.match(html,/id="chart-signal-hint"/);assert.match(html,/id="historical-signal-records"/);
  assert.match(html,/\.historical-signal-records \.review-table-scroll\{max-height:20rem;overflow-y:auto/);
  assert.match(html,/체결 표식과 글자는 그대로 표시합니다/);
});
