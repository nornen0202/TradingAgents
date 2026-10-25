"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),test=require("node:test"),vm=require("node:vm");
const root=path.resolve(__dirname,"../..");
const source=fs.readFileSync(path.join(root,"tradingagents/charting/static/viewer.js"),"utf8")
  .replace(/start\(\)\.catch\(error=>byId\("status"\)\.textContent=error\.message\);\s*$/,"");
function harness(){
  class Element{
    constructor(tag="div"){this.tag=tag;this.children=[];this.style={};this.className="";this.checked=false;this.disabled=false;this.attributes={};this._text="";}
    set textContent(value){this._text=String(value);this.children=[];}
    get textContent(){return this._text+this.children.map(c=>typeof c==="string"?c:c.textContent).join("");}
    append(...values){this.children.push(...values);}
    replaceChildren(...values){this._text="";this.children=values;}
    setAttribute(key,value){this.attributes[key]=value;}
    querySelector(tag){return this.children.filter(c=>typeof c!=="string").flatMap(c=>[c,c.querySelector(tag)]).find(c=>c?.tag===tag)||null;}
    querySelectorAll(tag){return this.children.filter(c=>typeof c!=="string").flatMap(c=>[...(c.tag===tag?[c]:[]),...c.querySelectorAll(tag)]);}
  }
  const nodes=new Map(["price-levels","charts","verdict","freshness","profile","performance","unverified","source-context","experiment-cards","reasons","facts","inferences","events"].map(id=>[id,new Element()]));
  const document={getElementById:id=>nodes.get(id)||null,createElement:tag=>new Element(tag),head:new Element("head")};
  const context=vm.createContext({document,window:{},LightweightCharts:{LineStyle:{Dotted:1,Solid:0,Dashed:2}},console});
  vm.runInContext(source,context);
  return {context,nodes,run:code=>vm.runInContext(code,context)};
}
function all(node,tag){return [...(node.tag===tag?[node]:[]),...node.children.filter(x=>typeof x!=="string").flatMap(x=>all(x,tag))];}
test("default hides only inline names and level axis labels; all prices/styles/colors remain exact",()=>{
  const h=harness();
  for(const [style,expected] of [["DOTTED",1],["SOLID",0],["DASHED",2],["UNKNOWN",2]]){
    const level=Object.freeze({price:342.123456789,label:"AAPL original plan",style});
    const hidden=h.context.priceLevelOptions(level,false),shown=h.context.priceLevelOptions(level,true);
    assert.equal(hidden.price,level.price);assert.equal(hidden.lineStyle,expected);assert.equal(hidden.color,"#90642f");
    assert.equal(hidden.title,"");assert.equal(hidden.axisLabelVisible,false);
    assert.equal(shown.title,level.label);assert.equal(shown.axisLabelVisible,true);
    assert.equal(shown.price,hidden.price);assert.equal(shown.lineStyle,hidden.lineStyle);assert.equal(shown.color,hidden.color);
  }
});
test("legend keeps every duplicate name/price, full precision, supplied source and original clocks",()=>{
  const h=harness(),levels=[{price:342.123456789,label:"same price first",style:"DASHED"},
    {price:342.123456789,label:"same price second",style:"DOTTED",source:{vendor:"recorded-source"},
      event_time:"2026-10-22T20:00:00Z",market_data_asof:"2026-10-22T20:00:00Z",ingested_at:"2026-10-23T01:00:00Z",evaluated_at:"2026-10-23T02:00:00Z"},
    {price:343,label:"<img src=x onerror=bad>",style:"SOLID"}];
  const before=JSON.stringify(levels);
  h.context.renderPriceLevelLegend({price_levels:levels,source_context:{run_id:"original-run"}});
  const area=h.nodes.get("price-levels"),rows=all(area,"tr").slice(1);
  assert.equal(rows.length,3);assert.equal(JSON.stringify(levels),before);
  for(let i=0;i<levels.length;i++){
    assert.equal(rows[i].children[0].textContent,levels[i].label);
    assert.equal(rows[i].children[1].textContent,String(levels[i].price));
  }
  assert.match(area.textContent,/개별 출처 미제공/);assert.match(area.textContent,/recorded-source/);
  assert.match(area.textContent,/2026-10-23T01:00:00Z/);assert.match(area.textContent,/원본 실행: original-run/);
  assert.equal(area.querySelector("table").style.tableLayout,"auto");
  assert.equal(all(area,"details").length,1);assert.match(all(area,"summary")[0].textContent,/원래 시각 4개/);
  assert.equal(all(area,"img").length,0);
  const scroll=all(area,"div").find(node=>node.className==="review-table-scroll");
  assert.equal(scroll.tabIndex,0);assert.equal(scroll.attributes.role,"region");
  assert.match(scroll.attributes["aria-label"],/모든 열/);
});
test("explicit label toggle updates display options only, and clearing drops all old handles",()=>{
  const h=harness(),changes=[];
  h.context.lineA={applyOptions:value=>changes.push(JSON.parse(JSON.stringify(value)))};
  h.run('planPriceLines=[{line:lineA,label:"original label"}]');
  h.run('updatePriceLevelLabels(planPriceLines,true)');
  h.run('updatePriceLevelLabels(planPriceLines,false)');
  assert.deepEqual(changes,[{title:"original label",axisLabelVisible:true},{title:"",axisLabelVisible:false}]);
  h.context.clearSnapshot();h.run('updatePriceLevelLabels(planPriceLines,true)');
  assert.equal(changes.length,2);assert.equal(h.run('planPriceLines.length'),0);
  assert.equal(h.nodes.get("price-levels").textContent,"");
});
test("empty legend is explicit; zero and its unit stay in one narrow span",()=>{
  const h=harness();h.context.renderPriceLevelLegend({price_levels:[],source_context:{}});
  assert.match(h.nodes.get("price-levels").textContent,/가격선 0개/);
  const unit=h.context.unit(0,"회");assert.equal(unit.textContent,"0회");assert.equal(unit.className,"review-unit");
  const html=fs.readFileSync(path.join(root,"tradingagents/charting/static/viewer.html"),"utf8");
  assert.match(html,/\.review-unit\{[^}]*white-space:nowrap/);
  assert.match(html,/id="chart-level-hint"/);
  assert.match(source,/levelToggle\.setAttribute\("aria-controls",element\.id\)/);
});
