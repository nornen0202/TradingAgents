"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const source = fs.readFileSync(path.resolve(__dirname, "../../tradingagents/charting/static/viewer.js"), "utf8")
  .replace(/start\(\)\.catch\(error=>byId\("status"\)\.textContent=error\.message\);\s*$/, "");
function response(body, status=200, generation) {
  return new Response(JSON.stringify(body), {status, headers: {
    "Content-Type": "application/json", ...(generation===undefined?{}:{"X-Archive-Catalog-Generation":String(generation)})
  }});
}
function progress(token="job_A", phase="REPLAY", generation=7, elapsed=20) {
  return {status:"SNAPSHOT_BUILDING",job_token:token,generation,phase,
          elapsed_seconds:elapsed,phase_elapsed_seconds:1};
}
function harness(fetch) {
  let clock=0, nextTimer=0;
  const timers=new Map(), delays=[], requests=[], nodes=new Map();
  function element() {return {value:"",textContent:"",children:[],replaceChildren(...items){this.children=items;if(!this.value&&items[0]?.value)this.value=items[0].value;},append(...items){this.children.push(...items);}};}
  const document={getElementById(id){if(!nodes.has(id))nodes.set(id,element());return nodes.get(id);},createElement:element};
  const context=vm.createContext({URL,URLSearchParams,Response,AbortController,DOMException,console,document,
    location:{origin:"http://127.0.0.1:9876"},window:{},performance:{now:()=>clock},
    setTimeout(fn,ms){const id=++nextTimer;delays.push(ms);if(ms===500){clock+=ms;queueMicrotask(fn);}else timers.set(id,fn);return id;},
    clearTimeout(id){timers.delete(id);},fetch:async(url,options)=>{
      requests.push(new URL(url));return fetch(new URL(url),options,()=>{clock+=10000;});
    }});
  vm.runInContext(source,context);
  return {context,nodes,requests,timers,delays,run:code=>vm.runInContext(code,context)};
}

test("first 200 and INDEXING both retain catalog generation", async()=>{
  let count=0;
  const h=harness(()=>++count===1?response({status:"INDEXING",generation:7,manifests_checked:12},202,7):response(["TEST"],200,7));
  const receipt={};
  assert.equal(JSON.stringify(await h.context.getJson("/api/tickers?as_of=2026-10-16T12:00:00Z",undefined,undefined,receipt)), '["TEST"]');
  assert.equal(receipt.generation,7);
  assert.equal(h.requests[1].searchParams.get("catalog_generation"),"7");
  const direct=harness(()=>response(["TEST"],200,9)), ready={};
  await direct.context.getJson("/api/tickers",undefined,undefined,ready);
  assert.equal(ready.generation,9);
});

test("more than 15s total joins one job and preserves the cohort", async()=>{
  let count=0;
  const h=harness((url,options,advance)=>{
    advance();
    return ++count<4?response(progress("job_A",["REPLAY","BUILD","VERIFY"][count-1],7,count*10),202,7):response({done:true},200,7);
  });
  const stages=[];
  const value=await h.context.getJson("/api/snapshot?ticker=TEST&as_of=2026-10-16T12%3A00%3A00Z&anchor=2026-10-16T09%3A00%3A00Z&catalog_generation=7",p=>stages.push(p.phase));
  assert.equal(value.done,true);
  assert.deepEqual(stages,["REPLAY","BUILD","VERIFY"]);
  assert.equal(h.requests.filter(r=>!r.searchParams.has("snapshot_job")).length,1);
  for(const url of h.requests.slice(1)){
    assert.equal(url.searchParams.get("snapshot_job"),"job_A");
    assert.equal(url.searchParams.get("ticker"),"TEST");
    assert.equal(url.searchParams.get("as_of"),"2026-10-16T12:00:00Z");
    assert.equal(url.searchParams.get("anchor"),"2026-10-16T09:00:00Z");
    assert.equal(url.searchParams.get("catalog_generation"),"7");
  }
  assert.equal(h.delays.filter(n=>n===15000).length,4);
  assert.equal(h.timers.size,0);
});

test("one pending HTTP request still has its unchanged 15s deadline", async()=>{
  const h=harness((url,{signal})=>new Promise((resolve,reject)=>signal.addEventListener("abort",()=>reject(new DOMException("aborted","AbortError")),{once:true})));
  const pending=h.context.getJson("/api/snapshot?ticker=TEST");
  assert.equal(h.delays[0],15000);
  [...h.timers.values()][0]();
  await assert.rejects(pending,/15초/);
  assert.equal(h.requests.length,1);
});

test("202 jobs keep the existing total 120s budget", async()=>{
  const h=harness((url,options,advance)=>{advance();return response(progress(),202,7);});
  await assert.rejects(h.context.getJson("/api/snapshot?ticker=TEST"),/차트 자료를 아직 준비 중/);
  assert.equal(h.requests.length,12);
  assert.ok(h.delays.filter(n=>n!==500).every(n=>n===15000));
});

test("changed job, generation, unsafe phase and malformed clocks are refused", async()=>{
  for(const mutate of [p=>p.job_token="job_B",p=>p.generation=8,p=>p.phase="PRIVATE_RAW_ERROR",
    p=>p.elapsed_seconds=-1,p=>p.phase_elapsed_seconds=null,p=>p.job_token="../escape"]){
    let count=0;
    const h=harness(()=>{const p=progress();if(++count===2)mutate(p);return response(p,202,7);});
    await assert.rejects(h.context.getJson("/api/snapshot?ticker=TEST"));
    assert.equal(h.requests.length,2);
  }
  const h=harness(()=>response(["TEST"],200,"bad"));
  await assert.rejects(h.context.getJson("/api/tickers",undefined,undefined,{}),/세대/);
});

test("catalog first-200 generation is passed to the same cutoff snapshot", async()=>{
  const h=harness(url=>url.pathname==="/api/tickers"?response(["TEST"],200,11):response({},503));
  h.nodes.set("asof",{value:"2026-10-16T12:00:00Z"});
  await h.context.refreshCatalog();
  await h.context.showSnapshot(Promise.resolve(),0);
  assert.equal(h.requests[1].searchParams.get("catalog_generation"),"11");
  assert.equal(h.requests[1].searchParams.get("ticker"),"TEST");
});

test("a new cutoff never borrows an old catalog/job token", async()=>{
  const h=harness(()=>response({},503));
  h.run("currentCatalog={asOf:'2026-10-16T12:00:00Z',generation:11};");
  h.context.document.getElementById("asof").value="2026-10-16T13:00:00Z";
  h.context.document.getElementById("ticker").value="TEST";
  await h.context.showSnapshot(Promise.resolve(),0);
  assert.equal(h.requests[0].searchParams.has("catalog_generation"),false);
  assert.equal(h.requests[0].searchParams.has("snapshot_job"),false);
});

test("late old-view catalog completion cannot replace the new catalog", async()=>{
  let release;
  const h=harness(url=>url.searchParams.get("as_of")==="old"?new Promise(resolve=>{release=resolve;}):response(["NEW"],200,12));
  const older=new AbortController(),newer=new AbortController();
  h.context.document.getElementById("asof").value="old";
  h.run("requestVersion=1;");
  const old=h.context.refreshCatalog(1,older.signal);
  const observed=old.catch(error=>error.name);
  h.context.document.getElementById("asof").value="new";
  h.run("requestVersion=2;");older.abort();
  await h.context.refreshCatalog(2,newer.signal);
  release(response(["OLD"],200,11));
  assert.equal(await observed,"AbortError");
  assert.equal(h.run("currentCatalog.generation"),12);
  assert.equal(h.run("currentCatalog.asOf"),"new");
  assert.equal(h.context.document.getElementById("ticker").children[0].value,"NEW");
});

test("aborted old snapshot job cannot leak into a new anchor request", async()=>{
  let releaseOld,oldCount=0,newCount=0;
  const h=harness(url=>{
    if(url.searchParams.get("anchor")==="old"){
      if(++oldCount===1)return response(progress("old_job"),202,7);
      return new Promise(resolve=>{releaseOld=resolve;});
    }
    return ++newCount===1?response(progress("new_job","BUILD"),202,7):response({done:"new"},200,7);
  });
  const oldController=new AbortController(),newController=new AbortController();
  const old=h.context.getJson("/api/snapshot?ticker=TEST&as_of=2026-10-16T12:00:00Z&anchor=old&catalog_generation=7",undefined,oldController.signal);
  const oldResult=old.catch(error=>error.name);
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(typeof releaseOld,"function");
  oldController.abort();
  const newer=await h.context.getJson("/api/snapshot?ticker=TEST&as_of=2026-10-16T12:00:00Z&anchor=new&catalog_generation=7",undefined,newController.signal);
  releaseOld(response({done:"old"},200,7));
  assert.equal(await oldResult,"AbortError");
  assert.equal(newer.done,"new");
  const requests=h.requests.filter(url=>url.searchParams.get("anchor")==="new");
  assert.equal(requests[0].searchParams.has("snapshot_job"),false);
  assert.equal(requests[1].searchParams.get("snapshot_job"),"new_job");
});

test("expired cohorts and active capacity errors require explicit fresh query", async()=>{
  for(const [status,message] of [[409,/목록을 새로/],[410,/종료됐거나 만료/],[429,/준비 작업이 많/]]){
    const h=harness(()=>response({private_error:"NEVER_DISPLAY"},status));
    await assert.rejects(h.context.getJson("/api/snapshot?ticker=TEST"),message);
    assert.equal(h.requests.length,1);
  }
});

test("source context keeps the requested cutoff rather than worker completion", ()=>{
  const h=harness(()=>assert.fail("Source text must not fetch or refresh clocks"));
  const snapshot={as_of_evaluated_at:"2026-10-16T12:00:00+00:00",completed_at:"2026-10-16T12:01:30+00:00",
    source_context:{run_id:"original-run",research_finished_at:"2026-10-16T10:00:00Z"},
    series:[{bars:[{},{}]}],events:{events:[{}]}};
  const before=JSON.stringify(snapshot),text=h.context.snapshotSourceText(snapshot);
  assert.ok(text.includes("조회 기준 시각: "+snapshot.as_of_evaluated_at));
  assert.ok(text.includes("원본 실행: original-run · 연구 완료 "+snapshot.source_context.research_finished_at));
  assert.ok(text.includes("완료 봉 2개 · 이벤트 1건"));
  assert.equal(text.includes(snapshot.completed_at),false);
  assert.equal(JSON.stringify(snapshot),before);
});
