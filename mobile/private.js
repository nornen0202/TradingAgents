
(() => {
  'use strict';
  let serial = 0;
  const rendered = new WeakMap();
  const node = (tag, text) => { const el = document.createElement(tag); if (text != null) el.textContent = text; return el; };
  function inline(parent, text) {
    const pattern = /(`[^`]+`|\*\*[^*]+\*\*|\[[^\]]+\]\(https?:\/\/[^\s)]+\))/g;
    let start = 0;
    for (const match of String(text).matchAll(pattern)) {
      parent.append(document.createTextNode(text.slice(start, match.index)));
      const value = match[0];
      if (value.startsWith('`')) parent.append(node('code', value.slice(1, -1)));
      else if (value.startsWith('**')) parent.append(node('strong', value.slice(2, -2)));
      else {
        const link = value.match(/^\[([^\]]+)\]\((.+)\)$/);
        const a = node('a', link[1]); a.href = link[2]; a.rel = 'noopener noreferrer'; parent.append(a);
      }
      start = match.index + value.length;
    }
    parent.append(document.createTextNode(text.slice(start)));
  }
  const cells = line => line.trim().replace(/^\|/, '').replace(/\|$/, '').split(/(?<!\\)\|/).map(v => v.trim().replace(/\\\|/g, '|'));
  function markdown(source) {
    const article = node('article'); article.className = 'reader-prose';
    const lines = source.split(/\r?\n/); let list = null;
    for (let i = 0; i < lines.length; i += 1) {
      const line = lines[i], value = line.trim();
      if (!value) { list = null; continue; }
      if (/^```/.test(value)) {
        const code = []; i += 1;
        while (i < lines.length && !/^```/.test(lines[i].trim())) code.push(lines[i++]);
        const pre = node('pre'); pre.append(node('code', code.join('\n'))); article.append(pre); list = null; continue;
      }
      if (i + 1 < lines.length && value.includes('|') && cells(lines[i + 1]).every(v => /^:?-{3,}:?$/.test(v))) {
        const table = node('table'), head = node('thead'), body = node('tbody');
        const row = (values, tag) => { const tr = node('tr'); values.forEach(v => { const cell = node(tag); if (tag === 'th') cell.scope = 'col'; inline(cell, v); tr.append(cell); }); return tr; };
        head.append(row(cells(line), 'th')); i += 2;
        while (i < lines.length && lines[i].trim() && lines[i].includes('|')) body.append(row(cells(lines[i++]), 'td'));
        i -= 1; table.append(head, body); article.append(table); list = null; continue;
      }
      const heading = value.match(/^(#{1,6})\s+(.+)$/);
      if (heading) { const h = node('h' + Math.min(4, heading[1].length + 1)); inline(h, heading[2]); article.append(h); list = null; continue; }
      const bullet = value.match(/^(?:[-*+] |\d+\. )(.+)$/);
      if (bullet) {
        const tag = /^\d/.test(value) ? 'ol' : 'ul';
        if (!list || list.tagName.toLowerCase() !== tag) { list = node(tag); if (tag === 'ol') list.start = parseInt(value, 10); article.append(list); }
        const li = node('li'); inline(li, bullet[1]); list.append(li); continue;
      }
      list = null;
      if (/^(---+|\*\*\*+)$/.test(value)) { article.append(node('hr')); continue; }
      const p = node(value.startsWith('> ') ? 'blockquote' : 'p'); inline(p, value.startsWith('> ') ? value.slice(2) : line); article.append(p);
    }
    return article;
  }
  function contents(root) {
    root.querySelectorAll(':scope > .reader-contents').forEach(el => el.remove());
    const headings = [...root.querySelectorAll('h2,h3,h4')].filter(h => !h.closest('.card,.run-card,.reader-contents,[data-reader-source],[hidden]'));
    if (headings.length < 2) return;
    const details = node('details'); details.className = 'reader-contents';
    details.append(node('summary', '이 리포트 목차 · ' + headings.length + '개 항목'));
    const nav = node('nav'); nav.setAttribute('aria-label', '리포트 목차');
    headings.forEach(h => {
      if (!h.id) h.id = 'reader-section-' + (++serial);
      h.dataset.readerHeading = ''; h.tabIndex = -1;
      const a = node('a', h.textContent); a.href = '#' + h.id;
      if (h.tagName !== 'H2') a.className = 'reader-subsection';
      a.addEventListener('click', event => {
        event.preventDefault();
        for (let ancestor = h.parentElement; ancestor; ancestor = ancestor.parentElement) if (ancestor.tagName === 'DETAILS') ancestor.open = true;
        h.scrollIntoView({block: 'start'}); h.focus({preventScroll: true});
      }); nav.append(a);
    });
    details.append(nav); root.prepend(details);
  }
  function enhance(root) {
    if (!root) return;
    root.querySelectorAll('pre[data-report-markdown]').forEach(pre => {
      const previous = rendered.get(pre);
      if (previous && previous.source === pre.textContent) return;
      const article = markdown(pre.textContent);
      if (previous) previous.article.replaceWith(article);
      else {
        const details = node('details'); details.dataset.readerSource = '';
        details.append(node('summary', 'Markdown 원문 보기'));
        pre.before(article, details); details.append(pre);
      }
      rendered.set(pre, {source: pre.textContent, article});
    });
    root.querySelectorAll('table').forEach(table => {
      if (table.closest('.reader-table,.account-table-wrap,.summary-scroll')) return;
      const wrap = node('div'); wrap.className = 'reader-table'; wrap.tabIndex = 0;
      wrap.setAttribute('role', 'region'); wrap.setAttribute('aria-label', '리포트 표 · 가로로 스크롤하여 전체 보기');
      table.before(wrap); wrap.append(table);
    });
    root.querySelectorAll('.grid').forEach(grid => {
      const cards = [...grid.querySelectorAll(':scope > a.card')];
      if (cards.length < 2 || grid.dataset.readerSearch) return;
      grid.dataset.readerSearch = 'true';
      const box = node('div'); box.className = 'reader-search';
      const input = node('input'); input.type = 'search'; input.placeholder = '제목 · 종목 · 채널 · 키워드'; input.id = 'report-search-' + (++serial);
      const label = node('label', '리포트 찾기'); label.htmlFor = input.id;
      const status = node('p'); status.setAttribute('role', 'status'); status.setAttribute('aria-live', 'polite');
      const update = () => {
        const terms = input.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean); let count = 0;
        cards.forEach(card => { card.hidden = !terms.every(t => card.textContent.toLocaleLowerCase().includes(t)); if (!card.hidden) count += 1; });
        status.textContent = cards.length + '개 중 ' + count + '개 표시' + (count ? '' : ' · 검색어를 지우거나 다른 키워드를 입력하세요.');
      };
      input.addEventListener('input', update); box.append(label, input, status); grid.before(box); update();
    });
    contents(root);
  }
  window.TradingAgentsReader = {enhance};
  const main = document.querySelector('main');
  if (main && !main.hasAttribute('data-reader-dynamic')) enhance(main);
  if (main) {
    const top = node('button', '↑ 맨 위'); top.type = 'button'; top.className = 'reader-back'; top.setAttribute('aria-label', '리포트 맨 위로 이동');
    top.addEventListener('click', () => { const target = document.querySelector('h1') || main; target.tabIndex = -1; target.scrollIntoView({block: 'start'}); target.focus({preventScroll: true}); });
    document.body.append(top);
  }
})();
(() => {
  'use strict';
  const status = document.getElementById('private-status');
  const root = document.getElementById('private-root');
  const tabs = document.getElementById('private-tabs');
  const pipelineExplainer = document.querySelector('.pipeline-explainer');
  if (pipelineExplainer && matchMedia('(max-width: 659px)').matches) pipelineExplainer.open = false;
  const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (ch) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const numeric = (value) => (typeof value === 'number' || (typeof value === 'string' && value.trim() !== '')) && Number.isFinite(Number(value)) ? Number(value) : NaN;
  const fmt = (value) => Number.isFinite(numeric(value)) ? Number(value).toLocaleString(undefined, {maximumFractionDigits: 2}) : '-';
  const dateTime = (value) => {
    const parsed = new Date(value || '');
    if (!Number.isFinite(parsed.getTime())) return '-';
    return new Intl.DateTimeFormat('ko-KR', {year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', timeZoneName: 'short'}).format(parsed);
  };
  const actionLabels = {
    NONE: '추가 행동 없음', NO_ACTION: '분석 결론 유지', HOLD: '보유 유지', WATCH: '관심 종목으로 관찰',
    WATCH_TRIGGER: '조건 충족 여부 관찰', WATCH_RISK: '위험 조건 관찰', WAIT: '조건 확인 전 대기', AVOID: '신규 매수 회피',
    BULLISH: '긍정적 관점', NEUTRAL: '중립적 관점', BEARISH: '보수적 관점',
    STARTER: '초기 분할매수', STARTER_NOW: '초기 분할매수 검토',
    STARTER_IF_TRIGGERED: '조건 충족 시 신규 분할매수',
    ADD: '분할 추가매수', ADD_NOW: '분할 추가매수 검토', BUY: '매수 검토', BUY_NOW: '매수 검토',
    ADD_IF_TRIGGERED: '조건 충족 시 추가 매수',
    REDUCE: '비중 축소', REDUCE_NOW: '비중 축소 검토', TRIM_NOW: '일부 축소 검토',
    TRIM_TO_FUND: '현금이 꼭 필요할 때 자금 마련 후보',
    REDUCE_RISK: '리스크 축소', REDUCE_IF_TRIGGERED: '조건 충족 시 비중 축소',
    TAKE_PROFIT: '이익 실현', TAKE_PROFIT_NOW: '이익 실현 검토', TAKE_PROFIT_IF_TRIGGERED: '조건 충족 시 이익 실현',
    STOP_LOSS: '손절 검토', STOP_LOSS_NOW: '손절 검토', STOP_LOSS_IF_TRIGGERED: '조건 충족 시 손절',
    EXIT: '청산 검토', EXIT_NOW: '청산 검토', EXIT_IF_TRIGGERED: '조건 충족 시 청산', SELL: '매도 검토',
    FULL_EXIT: '전량 정리', PARTIAL_20: '20% 분할 매도', PARTIAL_35: '35% 분할 매도',
    CUSTOM: '세부 실행 계획 확인'
  };
  const internalCode = (value) => /^[A-Z][A-Z0-9_]*$/.test(String(value || '').trim());
  const actionLabel = (value) => {
    const text = String(value || '').trim();
    if (!text) return '';
    return actionLabels[text.toUpperCase()] || (internalCode(text) ? '세부 실행 계획 확인' : text);
  };
  const actionKind = (value) => {
    const text = String(value || '').trim().toUpperCase();
    if (/SELL|EXIT|STOP_LOSS|청산|손절|매도/.test(text)) return 'sell';
    if (/REDUCE|TRIM|TAKE_PROFIT|축소|익절|이익 실현/.test(text)) return 'reduce';
    if (/AVOID|NO_ENTRY|회피|보류/.test(text)) return 'avoid';
    if (/BUY|ADD|STARTER|매수|진입/.test(text)) return 'buy';
    if (/HOLD|WAIT|WATCH|보유|관찰|대기/.test(text)) return 'hold';
    return 'research';
  };
  const isDirectional = (value) => actionKind(value) !== 'research';
  const won = (value) => {
    if (!Number.isFinite(numeric(value))) return '-';
    return new Intl.NumberFormat('ko-KR', {style: 'currency', currency: 'KRW', maximumFractionDigits: 0, signDisplay: 'always'}).format(Number(value));
  };
  const percent = (value) => Number.isFinite(numeric(value)) ? new Intl.NumberFormat('ko-KR', {style: 'percent', maximumFractionDigits: 1}).format(Number(value)) : '-';
  const sizingText = (delta, target) => combineDistinct(
    Number.isFinite(numeric(delta)) && Number(delta) !== 0 ? `조정 금액 ${won(delta)}` : '',
    Number.isFinite(numeric(target)) && Number(target) >= 0 && Number(target) <= 1 ? `목표 비중 ${percent(target)}` : '',
  );
  const query = new URLSearchParams(location.search);
  const requestedMarket = query.get('market') === 'us' ? 'us' : 'kr';
  const requestedRun = query.get('run') || '';
  let expiryTimer;

  function investorText(value) {
    let text = String(value == null ? '' : value);
    const replacements = [
      [/\blive recheck\b/gi, '실시간 재확인'],
      [/\bpacket\b/gi, '분석 자료'],
      [/패킷/g, '분석 자료'],
      [/파일럿/g, '시험 진입'],
      [/\bthesis\b/gi, '투자 논지'],
      [/\bconfidence\b/gi, '신뢰도'],
      [/\bsizing\b/gi, '비중 조절'],
      [/\bexecution\b/gi, '실행 판단'],
      [/\blive\b/gi, '실시간'],
      [/\bgate\b/gi, '확인 절차'],
      [/\bcurrent\b/gi, '최신'],
    ];
    for (const [source, target] of replacements) text = text.replace(source, target);
    text = text
      .replace(/새 최신/g, '새로운 최신')
      .replace(/분석 자료이(?=\s)/g, '분석 자료가')
      .replace(/분석 자료과/g, '분석 자료와');
    return text;
  }
  function valueText(value) {
    if (value == null || value === '') return '';
    if (Array.isArray(value)) return value.map(valueText).filter(Boolean).join(' · ');
    if (typeof value === 'object') {
      for (const field of ['text', 'label', 'summary', 'condition', 'action', 'description', 'stance']) {
        if (value[field]) return valueText(value[field]);
      }
      return '';
    }
    return investorText(value);
  }
  function combineDistinct(...values) {
    const parts = values.map(valueText).map((value) => value.trim()).filter(Boolean);
    return [...new Set(parts)].join(' · ');
  }
  function conditionItems(value) {
    if (value == null || value === '') return [];
    if (Array.isArray(value)) return value.flatMap(conditionItems);
    if (typeof value === 'object') {
      for (const field of ['condition', 'text', 'label', 'summary', 'description']) {
        if (value[field]) return conditionItems(value[field]);
      }
      return [];
    }
    const text = investorText(value).trim();
    if (!text || /^(?:none|n\/a|custom|unknown|-+)$/i.test(text)) return [];
    return text.split(/\s+(?:\/|\||·)\s+|\n+/).map((item) => item.trim()).filter(Boolean);
  }
  function distinctConditions(...values) {
    const seen = new Set();
    const result = [];
    values.flatMap(conditionItems).forEach((item) => {
      const key = item.replace(/\s+/g, ' ').trim().toLocaleLowerCase();
      if (!seen.has(key)) { seen.add(key); result.push(item); }
    });
    return result;
  }
  function fullConditions(...values) { return distinctConditions(...values).join(' · '); }
  function humanPlan(value) {
    if (value == null || value === '') return '';
    if (typeof value === 'string') {
      const text = value.trim();
      if (!text || /^CUSTOM$/i.test(text)) return '';
      return internalCode(text) ? actionLabel(text) : investorText(text);
    }
    if (Array.isArray(value)) return combineDistinct(...value.map(humanPlan));
    if (typeof value === 'object') {
      for (const field of ['text', 'summary', 'plan', 'description', 'action', 'label']) {
        if (value[field]) return humanPlan(value[field]);
      }
      if (value.enabled === false) return '';
      const stages = [1, 2, 3].map((stage) => {
        const fraction = value[`stage_${stage}_fraction`];
        return Number.isFinite(Number(fraction)) ? `${stage}차 ${percent(fraction)}` : '';
      }).filter(Boolean);
      return stages.length ? `단계 실행 비중 ${stages.join(' · ')}` : '';
    }
    return '';
  }
  function tickerKeys(value) {
    const ticker = String(value || '').trim().toUpperCase();
    const result = ticker ? [ticker] : [];
    if (ticker.endsWith('.KS') || ticker.endsWith('.KQ')) result.push(ticker.slice(0, -3));
    return result;
  }
  const strategyIndexes = new WeakMap();
  function workStrategy(item, ticker) {
    if (((item.integrated_report || {}).lineage || {}).current_action_cards_enriched === false) return {};
    if (!strategyIndexes.has(item)) {
      const index = new Map();
      for (const field of ['integrated_report']) {
        const structured = ((item[field] || {}).structured_report || {});
        for (const strategy of structured.strategies || []) {
          for (const key of tickerKeys(strategy.ticker)) if (!index.has(key)) index.set(key, strategy);
        }
      }
      strategyIndexes.set(item, index);
    }
    const index = strategyIndexes.get(item);
    return tickerKeys(ticker).map((key) => index.get(key)).find(Boolean) || {};
  }
  function normalizeRole(value, held) {
    if (held) return 'HOLDING';
    const role = String(value || '').toUpperCase();
    if (role.includes('HOLD') || role.includes('OWN') || role.includes('보유')) return 'HOLDING';
    if (role.includes('NEW') || role.includes('SCANNER') || role.includes('DISCOVERY') || role.includes('신규')) return 'NEW_CANDIDATE';
    return 'WATCHLIST';
  }
  const roleLabel = (role) => ({HOLDING: '보유', WATCHLIST: '관심', NEW_CANDIDATE: '신규 후보'}[role] || '관심');

  function immediateContractComplete(market) {
    const coverage = (market || {}).universe_coverage || {};
    const provenance = (market || {}).provenance || {};
    const source = (market || {}).source || {};
    const quality = (market || {}).quality || {};
    const guardrails = (market || {}).guardrails || {};
    const expected = numeric(coverage.expected_analysis_count);
    const total = numeric(coverage.analysis_total_count);
    const successful = numeric(coverage.analysis_successful_count);
    const zeroCounts = [
      coverage.missing_holding_count,
      coverage.missing_watchlist_count,
      coverage.missing_analysis_count,
      coverage.analysis_failed_count,
    ].every((value) => Number.isInteger(numeric(value)) && numeric(value) === 0);
    const runId = String((market || {}).run_id || '');
    const universeMode = String(coverage.ticker_universe_mode || '').toLowerCase();
    const accountReady = !['config_plus_account', 'account_only'].includes(universeMode)
      || String(coverage.account_snapshot_status || '').toLowerCase() === 'loaded';
    const boundRunIds = [
      provenance.surface_run_id,
      provenance.manifest_run_id,
      provenance.universe_source_run_id,
      provenance.decision_bundle_run_id,
    ].map((value) => String(value || ''));
    return coverage.status === 'COMPLETE'
      && coverage.complete === true
      && Number.isInteger(expected) && expected > 0
      && Number.isInteger(total) && total === expected
      && Number.isInteger(successful) && successful === expected
      && zeroCounts
      && accountReady
      && String((market || {}).manifest_status || '').toLowerCase() === 'success'
      && String(source.status || '').toLowerCase() === 'success'
      && (market || {}).decision_ready === true
      && quality.decision_ready === true
      && guardrails.decision_ready === true
      && runId !== ''
      && boundRunIds.every((value) => value === runId);
  }
  function baseLiveReadiness(row, market) {
    const quality = row.quality || {};
    const sourceHealth = String((market || {}).source_health || 'MISSING').toUpperCase();
    const guardrails = (market || {}).guardrails || {};
    const marketValid = Date.parse(guardrails.valid_until || '');
    if (sourceHealth !== 'OK') return {code: 'RECHECK', label: '주문 전 실시간 확인', note: '원천 데이터 상태를 다시 확인하세요.'};
    if (guardrails.expired_at_build === true || !Number.isFinite(marketValid) || marketValid <= Date.now()) {
      return {code: 'RECHECK', label: '주문 전 실시간 확인', note: '분석 시점 이후 가격이 변했을 수 있습니다.'};
    }
    const valid = Date.parse(quality.row_valid_until || '');
    if (quality.expired_at_build === true || !Number.isFinite(valid) || valid <= Date.now()) {
      return {code: 'RECHECK', label: '주문 전 실시간 확인', note: '이 종목의 실시간 조건을 다시 확인하세요.'};
    }
    const declared = String(quality.investor_state || 'UNAVAILABLE').toUpperCase();
    if (declared === 'READY' && (
      !immediateContractComplete(market)
      || quality.execution_ready !== true
      || quality.generated_in_current_run !== true
    )) return {code: 'RECHECK', label: '주문 전 실시간 확인', note: '분석 커버리지와 주문 조건을 한 번 더 확인하세요.'};
    if (declared === 'READY') return {code: 'READY', label: '실시간 조건 확인됨', note: '표시된 조건과 주문 수량을 최종 확인하세요.'};
    if (declared === 'CONDITIONAL') return {code: 'CONDITIONAL', label: '조건 확인 후 실행', note: '아래 진입·축소 조건이 실제로 충족됐는지 확인하세요.'};
    if (declared === 'RECHECK') return {code: 'RECHECK', label: '주문 전 실시간 확인', note: '분석 시점 이후 가격과 주문 조건을 다시 확인하세요.'};
    return {code: 'RESEARCH', label: '분석 시점 참고', note: '실시간 데이터 확인 후 전략을 적용하세요.'};
  }
  const workReadinessPolicy = {
    READY_NOW: {code: 'READY', label: '실시간 조건 확인됨', note: 'Work 분석은 현재 실행 가능으로 분류했습니다. 표시된 조건과 주문 수량을 최종 확인하세요.'},
    WAIT_FOR_TRIGGER: {code: 'CONDITIONAL', label: '조건 확인 후 실행', note: 'Work 분석의 진입·축소 조건이 실제로 충족되기 전에는 실행하지 마세요.'},
    NEEDS_LIVE_RECHECK: {code: 'RECHECK', label: '주문 전 실시간 확인', note: '분석 결론은 유지하되 현재가·거래량·호가를 다시 확인하세요.'},
    MARKET_CLOSED: {code: 'RECHECK', label: '개장 후 다시 확인', note: '시장 폐장 중 생성된 판단입니다. 개장 후 가격과 주문 가능 상태를 다시 확인하세요.'},
    DATA_OUTAGE: {code: 'RECHECK', label: '데이터 복구 후 확인', note: '필수 데이터가 중단됐습니다. 데이터 복구와 최신 시세를 확인하기 전에는 실행하지 마세요.'},
    RESEARCH_ONLY: {code: 'RESEARCH', label: '분석 참고 전용', note: '리서치 전용 판단이며 현재 주문 행동으로 사용하지 마세요.'},
  };
  const readinessSeverity = (code) => ({READY: 0, CONDITIONAL: 1, RECHECK: 2, RESEARCH: 3}[code] ?? 3);
  function liveReadiness(row, market, strategy) {
    const base = baseLiveReadiness(row, market);
    const workExecution = strategy.execution || {};
    const declared = String(workExecution.readiness || '').trim().toUpperCase();
    if (!declared) return base;
    const configured = workReadinessPolicy[declared];
    const workGate = configured
      ? {...configured}
      : {code: 'RECHECK', label: 'Work 상태 재확인', note: `알 수 없는 Work 준비 상태(${declared})입니다. 주문 전에 원본 분석을 다시 확인하세요.`};
    const explicitRechecks = valueText(workExecution.required_rechecks);
    if (explicitRechecks && workGate.code !== 'READY') workGate.note = explicitRechecks;
    return readinessSeverity(workGate.code) >= readinessSeverity(base.code) ? workGate : base;
  }
  function sourceChips(value) {
    const entries = Array.isArray(value)
      ? value
      : value && typeof value === 'object'
        ? Object.entries(value).map(([source, detail]) => ({source, detail}))
        : [];
    return entries.map((item) => {
      const source = valueText(item.source || item.name || item.label || item.channel || '출처');
      const detail = valueText(item.detail || item.summary || item.contribution || item.weight || item.confidence || '반영');
      return `<span class="source-chip">${esc(source)} · ${esc(detail)}</span>`;
    }).join('');
  }
  function companyName(row, strategy) {
    const ticker = String(row.ticker || strategy.ticker || '').trim();
    const identities = new Set(tickerKeys(ticker));
    for (const candidate of [row.display_name, strategy.display_name]) {
      const text = String(candidate || '').trim();
      if (text && !identities.has(text.toUpperCase())) return text;
    }
    return ticker || '종목명 확인 필요';
  }
  function evidenceItems(thesis, strategy) {
    const result = [];
    const add = (value, impact = 'mixed', meta = '') => {
      const text = valueText(value).trim();
      if (!text || result.some((item) => item.text === text)) return;
      result.push({text, impact: String(impact || 'mixed').toLowerCase(), meta});
    };
    for (const item of thesis.major_news_issues || []) {
      if (typeof item === 'string') add(item);
      else if (item && typeof item === 'object') add(
        combineDistinct(item.title, item.reason, item.investor_implication),
        item.impact,
        combineDistinct(item.source, item.occurred_at ? dateTime(item.occurred_at) : ''),
      );
    }
    for (const item of thesis.bullish_drivers || thesis.strength_drivers || []) add(item, 'bullish');
    for (const item of thesis.bearish_drivers || thesis.weakness_drivers || []) add(item, 'bearish');
    for (const item of strategy.source_contributions || []) {
      if (!item || typeof item !== 'object') continue;
      add(
        combineDistinct(item.reason, item.summary, item.contribution),
        item.direction || item.impact,
        combineDistinct(item.source, item.event_key),
      );
    }
    if (!result.length) for (const item of thesis.rationale || []) add(item, 'mixed');
    return result.slice(0, 8);
  }
  function evidenceList(thesis, strategy) {
    const items = evidenceItems(thesis, strategy);
    if (!items.length) return '';
    return `<div class="card-rationale"><strong>주요 뉴스·이슈와 강약 이유</strong><ul class="evidence-list">${items.map((item) => `<li class="${['bullish','bearish'].includes(item.impact) ? item.impact : 'mixed'}">${esc(item.text)}${item.meta ? `<small>${esc(item.meta)}</small>` : ''}</li>`).join('')}</ul></div>`;
  }
  function signalStrip(row, confidence) {
    const numericConfidence = numeric(confidence);
    const confidenceWidth = Number.isFinite(numericConfidence) ? Math.max(0, Math.min(100, numericConfidence * 100)) : 0;
    const change = numeric(row.price_change_pct);
    const changeText = Number.isFinite(change) ? `${change > 0 ? '+' : ''}${change.toFixed(2)}%` : '-';
    return `<div class="signal-strip" aria-label="핵심 신호 요약">
      <div class="signal"><span>분석 신뢰도</span><strong>${Number.isFinite(numericConfidence) ? percent(numericConfidence) : '-'}</strong><meter class="confidence-track" min="0" max="100" value="${confidenceWidth}" aria-label="분석 신뢰도">${confidenceWidth}%</meter></div>
      <div class="signal"><span>당일 등락</span><strong>${esc(changeText)}</strong></div>
      <div class="signal"><span>상대 거래량</span><strong>${fmt(row.relative_volume)}배</strong></div>
    </div>`;
  }
  function rowPriority(row, strategy) {
    const action = row.portfolio_action || {};
    const code = `${action.action_now || ''} ${action.action_if_triggered || ''} ${(strategy.execution || {}).action_now || ''} ${(strategy.thesis || {}).stance || ''}`.toUpperCase();
    let score = /EXIT|STOP|SELL|REDUCE|TRIM|TAKE_PROFIT/.test(code) ? 100 : /BUY|ADD|STARTER/.test(code) ? 80 : row.is_held ? 50 : 20;
    const rank = Number(strategy.rank ?? row.portfolio_priority ?? row.table_priority ?? row.display_priority);
    if (Number.isFinite(rank)) score += Math.max(0, 20 - rank);
    return score;
  }
  function analysisDirection(row, strategy) {
    const thesis = strategy.thesis || row.thesis || {};
    const workExecution = strategy.execution || {};
    const action = row.portfolio_action || {};
    const workCandidates = [
      thesis.stance,
      workExecution.action_now,
    ];
    const workSelected = workCandidates.find(isDirectional);
    if (workSelected) {
      if (actionKind(workSelected) === 'buy' && (thesis.stance_basis || (row.thesis || {}).stance_basis) === 'CONDITIONAL_ENTRY') {
        return {text: row.is_held ? '조건 확인 후 추가매수 검토' : '조건 확인 후 분할매수 검토', kind: 'buy'};
      }
      return {text: actionLabel(workSelected), kind: actionKind(workSelected)};
    }
    const rowCandidates = [
      row.strategy_code,
      row.strategy_ko,
    ];
    const rowSelected = rowCandidates.find(isDirectional);
    const weakRowConclusion = /^(DATA_CHECK|RESEARCH|RESEARCH_ONLY|ANALYSIS_ONLY|CUSTOM)$/.test(String(row.strategy_code || '').trim().toUpperCase())
      || /분석 참고|데이터 확인|추가 분석/.test(String(row.strategy_ko || ''));
    const fallbackCandidates = [
      action.action_now,
      action.portfolio_relative_action,
    ];
    const conditional = [
      workExecution.action_if_triggered,
      action.action_if_triggered,
    ].find((value) => {
      const kind = actionKind(value);
      return isDirectional(value) && ['buy', 'reduce', 'sell', 'avoid'].includes(kind);
    });
    if ((!rowSelected || weakRowConclusion) && conditional) {
      const conditionalKind = actionKind(conditional);
      const conditionalText = {
        buy: row.is_held === true ? '조건 확인 후 추가매수 검토' : '조건 확인 후 분할매수 검토',
        reduce: '조건 확인 후 일부 축소 검토',
        sell: '조건 확인 후 매도·청산 검토',
        avoid: '신규 매수 보류',
      }[conditionalKind];
      return {text: conditionalText, kind: conditionalKind};
    }
    const selected = rowSelected || fallbackCandidates.find(isDirectional);
    const selectedKind = actionKind(selected);
    return {
      text: selected ? actionLabel(selected) : '추가 분석 후 방향 결정',
      kind: selectedKind,
    };
  }
  function currentExecutionAction(row, action) {
    const delta = Number(action.delta_krw_now);
    const code = String(action.action_now || '').trim().toUpperCase();
    if (Number.isFinite(delta) && delta < 0) {
      return combineDistinct(actionLabel(code || 'REDUCE'), won(delta));
    }
    if (Number.isFinite(delta) && delta > 0) {
      return combineDistinct(actionLabel(code || 'BUY'), won(delta));
    }
    if (row.is_held === true) return '현재 주문 없음 · 기존 보유 유지';
    return '현재 주문 없음';
  }
  function accountGuidance(row, action) {
    const relative = String(action.portfolio_relative_action || '').trim().toUpperCase();
    const reasonCodes = new Set((action.relative_action_reason_codes || []).map((value) => String(value || '').trim().toUpperCase()));
    if (relative === 'TRIM_TO_FUND') {
      if (reasonCodes.has('CONCENTRATION')) {
        return '계좌 내 비중이 높아 추가 매수는 제한합니다. 현재 매도 지시가 아니며, 현금이 꼭 필요한 경우에만 자금 마련 후보로 검토합니다.';
      }
      if (reasonCodes.has('OPPORTUNITY_COST')) {
        return '현재 매도 지시가 아닙니다. 더 우선순위가 높은 조건부 후보가 실제 발동하고 현금이 부족할 때만 축소 후보로 재검토합니다.';
      }
      if (reasonCodes.has('NO_COVERAGE')) {
        return '현재 매도 지시가 아닙니다. 최신 종목 분석이 확보되지 않은 상태이므로 추가 매수는 멈추고, 현금이 필요할 때만 보수적으로 축소를 재검토합니다.';
      }
      return '현재 매도 지시가 아닙니다. 다른 종목의 발동 조건과 계좌 현금을 함께 확인한 뒤에만 자금 마련 후보로 재검토합니다.';
    }
    if (['REDUCE_RISK', 'TAKE_PROFIT', 'STOP_LOSS', 'EXIT'].includes(relative)) {
      const delta = Number(action.delta_krw_now);
      if (!Number.isFinite(delta) || delta >= 0) {
        return combineDistinct(
          '현재 매도 지시가 아닙니다.',
          `${actionLabel(relative)} 조건이 실시간으로 확인될 때만 축소·매도를 재검토합니다.`,
          action.relative_action_reason,
        );
      }
      return combineDistinct(actionLabel(relative), action.relative_action_reason);
    }
    return '';
  }
  function strategyActivationAction(thesis, workExecution, action, hasWork) {
    const workTriggered = workExecution.action_if_triggered
      ? actionLabel(workExecution.action_if_triggered)
      : '';
    const sizing = humanPlan(thesis.position_sizing);
    if (hasWork && workTriggered) return combineDistinct(workTriggered, sizing);
    if (hasWork && sizing) {
      const stanceKind = actionKind(thesis.stance);
      const label = {
        buy: '조건 충족 시 신규·추가 매수 검토',
        hold: '관찰 조건 충족 시 투자 논지 재평가',
        reduce: '조건 충족 시 비중 축소',
        sell: '조건 충족 시 매도·청산',
        avoid: '신규 매수 보류 유지',
        research: /신규|시험|매수|진입|비중/.test(sizing)
          ? '조건 충족 시 신규·추가 매수 재검토'
          : '조건 확인 후 전략 방향 재분석',
      }[stanceKind];
      return combineDistinct(label, sizing);
    }
    return combineDistinct(
      action.action_if_triggered ? actionLabel(action.action_if_triggered) : '',
      sizingText(action.delta_krw_if_triggered, action.target_weight_if_triggered),
      humanPlan(action.sell_size_plan),
    ) || '조건 확인 후 전략 방향 재분석';
  }
  function card(row, market, topTickers, marketId) {
    const strategy = workStrategy(market, row.ticker);
    const hasWork = Object.keys(strategy).length > 0;
    const hasThesis = hasWork || Boolean(row.thesis);
    const thesis = strategy.thesis || row.thesis || {};
    const workExecution = strategy.execution || {};
    const readiness = liveReadiness(row, market, strategy);
    const action = row.portfolio_action || {};
    const role = normalizeRole(row.universe_role || row.portfolio_role, row.is_held === true);
    const baseConclusion = valueText(row.strategy_ko) || (action.action_now ? actionLabel(action.action_now) : '');
    const direction = analysisDirection(row, strategy);
    const executionAction = currentExecutionAction(row, action);
    const guidance = accountGuidance(row, action);
    const workEntryConditions = fullConditions(thesis.entry_conditions);
    const riskDirected = ['SELL', 'REDUCE', 'AVOID'].includes(row.strategy_code);
    const baseEntryConditions = fullConditions(row.execution_condition_ko, riskDirected ? null : action.trigger_conditions);
    const entryCondition = (hasThesis ? workEntryConditions : baseEntryConditions) || '조건 정보 없음';
    const triggeredAction = strategyActivationAction(thesis, workExecution, action, hasThesis);
    const workInvalidation = fullConditions(thesis.invalidation_conditions);
    const baseInvalidation = fullConditions(row.risk_condition_ko, action.invalidation_condition, action.risk_condition);
    const invalidation = fullConditions(row.risk_condition_ko, hasThesis ? workInvalidation : baseInvalidation) || '무효화 조건 정보 없음';
    const baseRiskAction = combineDistinct(
      action.risk_action ? actionLabel(action.risk_action) : '',
      humanPlan(action.risk_action_level),
      humanPlan(action.profit_taking_plan),
    );
    const workRiskAction = humanPlan(thesis.invalidation_action || workExecution.risk_action);
    const riskAction = (hasThesis ? workRiskAction : baseRiskAction) || '무효화 시 행동 정보 없음';
    const confidence = hasThesis ? thesis.confidence : action.confidence;
    const confidenceText = Number.isFinite(numeric(confidence)) && Number(confidence) >= 0 && Number(confidence) <= 1 ? percent(confidence) : valueText(confidence);
    const displayName = companyName(row, strategy);
    const tickerIdentity = tickerKeys(row.ticker)[0];
    const fullWorkEntry = fullConditions(thesis.entry_conditions);
    const fullWorkInvalidation = fullConditions(thesis.invalidation_conditions);
    const fullBaseEntry = fullConditions(row.execution_condition_ko, riskDirected ? null : action.trigger_conditions);
    const fullBaseInvalidation = fullConditions(row.risk_condition_ko, action.invalidation_condition, action.risk_condition);
    const original = row.thesis || {};
    const axisLabels = {HOLD: '보유', WAIT: '관찰', NONE: '없음', BULLISH: '긍정', BEARISH: '부정', NEUTRAL: '중립', STARTER: '신규 분할 진입', ADD: '추가매수'};
    const axes = original.rating ? `<p class="readiness-note analysis-axes">원등급 ${esc(axisLabels[original.rating] || actionLabel(original.rating))} · 방향 관점 ${esc(axisLabels[original.portfolio_stance] || original.portfolio_stance || '-')} · 분석 당시 진입 ${esc(axisLabels[original.entry_action] || original.entry_action || '-')} · 조건부 계획 ${esc(axisLabels[original.conditional_entry_action] || original.conditional_entry_action || '-')} · 보유 위험 계획 ${esc(actionLabel(original.risk_action || 'NONE'))}<br>판단 기준 ${esc(original.decision_asof || '-')} · 일봉 가격 기준 ${esc(original.price_reference_date || '-')} · 조건부 계획 만료 ${esc(dateTime(original.conditional_entry_valid_until))}</p>` : '';
    const sourceCoverage = original.source_coverage || {};
    const sourceLabels = {get_disclosures: '공시', get_macro_indicators: '거시 지표', get_social_sentiment: '감성'};
    const coverageLabels = {OBSERVED: '수집 관측', UNAVAILABLE: '수집 불가', NOT_COLLECTED: '미수집', VERIFIED_ZERO: '조회 구간 0건 확인', UNMAPPED_INSTRUMENT: '종목 매핑·적용 대상 미확인', PARTIAL_WINDOW: '조회 기간 일부만 확인'};
    const sources = Object.entries(sourceCoverage).map(([key, value]) => `${sourceLabels[key] || key}: ${coverageLabels[value.status] || value.status}${value.missing_configuration ? ' (구성 누락)' : ''}${value.source_type === 'NEWS_DERIVED' ? ' (뉴스 기반 대체 자료)' : ''}`).join(' · ');
    const supportingDetail = `<details><summary>${hasWork ? '기본 분석·전체 조건 보기' : '전체 조건 보기'}</summary>
      ${hasWork ? `<p><strong>기본 분석 결론</strong><br>${esc(baseConclusion || '정보 없음')}</p>` : ''}
      ${fullWorkEntry ? `<p><strong>${hasWork ? 'Work' : '원분석'} 전체 진입·축소 조건</strong><br>${esc(fullWorkEntry)}</p>` : ''}
      ${fullConditions(original.observation_conditions) ? `<p><strong>원분석 관찰 목록 · 진입 신호와 구별</strong><br>${esc(fullConditions(original.observation_conditions))}</p>` : ''}
      ${fullWorkInvalidation ? `<p><strong>${hasWork ? 'Work' : '원분석'} 전체 무효화 조건</strong><br>${esc(fullWorkInvalidation)}</p>` : ''}
      ${fullBaseEntry ? `<p><strong>기본 분석 전체 조건</strong><br>${esc(fullBaseEntry)}</p>` : ''}
      ${fullBaseInvalidation ? `<p><strong>기본 분석 전체 무효화 조건</strong><br>${esc(fullBaseInvalidation)}</p>` : ''}
      ${action.rationale ? `<p><strong>기본 분석 근거</strong><br>${esc(valueText(action.rationale))}</p>` : ''}
    </details>`;
    return `<article class="action-card" id="strategy-${esc(marketId)}-${esc(encodeURIComponent(tickerIdentity))}" tabindex="-1" data-ticker="${esc(tickerIdentity)}" data-name="${esc(displayName)}" data-direction="${esc(direction.kind)}" data-search="${esc(`${displayName} ${row.ticker || ''} ${row.sector || ''}`.toLocaleLowerCase())}" data-change="${numeric(row.price_change_pct)}" data-readiness="${esc(readiness.code)}" data-group="${esc(role)}" data-top="${topTickers.has(tickerIdentity) ? 'true' : 'false'}">
      <button type="button" class="back-to-overview">↑ 전략 요약표로</button>
      <div class="card-title"><div><strong>${esc(displayName)} <span class="role-badge">${esc(roleLabel(role))}</span></strong><span class="ticker-code">${esc(row.ticker || '-')}</span></div><span class="row-mode mode-${esc(readiness.code.toLowerCase())}">${esc(readiness.label)}</span></div>
      <div class="price-line"><strong>${fmt(row.last_price)}</strong><span>시세 ${esc(dateTime(row.market_data_asof || workExecution.as_of))}</span></div>
      <div class="private-action" data-direction="${esc(direction.kind)}"><strong>분석 시점 전략 방향</strong><span class="strategy-direction">${esc(direction.text)}</span></div>
      ${axes}
      <div class="execution-status"><div><strong>현재 실행 상태·행동</strong><span class="row-mode mode-${esc(readiness.code.toLowerCase())}">${esc(readiness.label)}</span></div><span class="execution-action">${esc(executionAction)}</span><p class="readiness-note">${esc(readiness.note)}</p></div>
      ${guidance ? `<div class="account-guidance"><strong>계좌 운용 참고 · 현재 매도 지시와 별개</strong><p>${esc(guidance)}</p></div>` : ''}
      ${signalStrip(row, confidence)}
      <div class="condition-grid">
        <div class="condition-block"><strong>전략 발동 조건</strong><p>${esc(entryCondition)}</p></div>
        <div class="condition-block"><strong>발동 조건 충족 시 행동</strong><p>${esc(triggeredAction)}</p></div>
        <div class="condition-block risk"><strong>위험 대응·무효화 조건</strong><p>${esc(invalidation)}</p></div>
        <div class="condition-block risk"><strong>위험 대응 조건 충족 시 행동</strong><p>${esc(riskAction)}</p></div>
      </div>
      <dl>
        <div><dt>VWAP</dt><dd>${esc(row.vwap_position_ko || '-')}</dd></div>
        <div><dt>상대 거래량</dt><dd>${fmt(row.relative_volume)}배</dd></div>
        <div><dt>분석 신뢰도</dt><dd>${esc(confidenceText || '-')}</dd></div>
      </dl>
      ${evidenceList(thesis, strategy)}
      ${(hasThesis ? thesis.rationale : action.rationale) ? `<p class="card-rationale"><strong>종합 판단 근거</strong><br>${esc(valueText(hasThesis ? thesis.rationale : action.rationale))}</p>` : ''}
      ${supportingDetail}
      <details><summary>금액·비중·출처 세부 보기</summary><dl>
        <div><dt>근거 수집 상태</dt><dd>${esc(sources || '미확인')}</dd></div>
        <div><dt>시세 공급자 제한</dt><dd>${esc(valueText((row.quality || {}).provider_limitations) || '제공 정보 없음')}</dd></div>
        <div><dt>현재 증감</dt><dd>${esc(won(action.delta_krw_now))}</dd></div>
        <div><dt>조건부 증감</dt><dd>${esc(won(action.delta_krw_if_triggered))}</dd></div>
        <div><dt>목표 비중</dt><dd>${esc(percent(action.target_weight_now ?? action.target_weight_if_triggered))}</dd></div>
        <div><dt>이익 실현 계획</dt><dd>${esc(humanPlan(action.profit_taking_plan) || '-')}</dd></div>
      </dl><div class="source-chips">${sourceChips(strategy.source_contributions)}</div></details>
    </article>`;
  }
  function workTopAction(item) {
    if (typeof item === 'string') return `<div class="work-action"><strong>${esc(internalCode(item) ? actionLabel(item) : item)}</strong></div>`;
    const title = combineDistinct(item.ticker, item.display_name, item.title) || '핵심 액션';
    const detail = combineDistinct(
      item.action ? actionLabel(item.action) : '',
      item.action_now ? actionLabel(item.action_now) : '',
      item.action_if_triggered ? actionLabel(item.action_if_triggered) : '',
      item.summary,
      item.rationale,
      item.condition,
    );
    return `<div class="work-action"><strong>${esc(title)}</strong>${detail ? `<span>${esc(detail)}</span>` : ''}</div>`;
  }
  function marketOverview(rows, item) {
    const buckets = {BUY: 0, HOLD: 0, REDUCE: 0, SELL: 0, AVOID: 0, RESEARCH: 0};
    rows.forEach((row) => {
      const strategy = workStrategy(item, row.ticker);
      const kind = analysisDirection(row, strategy).kind.toUpperCase();
      buckets[Object.hasOwn(buckets, kind) ? kind : 'RESEARCH'] += 1;
    });
    const labels = {BUY: '매수·추가 검토', HOLD: '보유·관찰', REDUCE: '축소 검토', SELL: '매도·청산', AVOID: '신규 매수 보류', RESEARCH: '추가 조사'};
    return `<div class="overview-help"><span>분석 방향을 누르면 해당 종목만 표시합니다.</span><button type="button" class="clear-direction" data-direction-target="all">전체 방향</button></div><div class="market-overview" role="group" aria-label="전략 방향 필터">${Object.entries(buckets).map(([key, count]) => `<button type="button" class="overview-stat" data-direction="${key.toLowerCase()}" data-direction-target="${key.toLowerCase()}" aria-pressed="false" aria-label="${labels[key]} ${count}종목 보기"><strong>${count}</strong><span>${labels[key]}</span></button>`).join('')}</div>`;
  }
  function attemptStatus(item) {
    const attempt = item.latest_attempt || {};
    if (!attempt.run_id) return '';
    const labels = {SUCCESS: '완료', FAILED: '실패', FAILURE: '실패', INTERRUPTED: '연결 중단·심박 만료', RUNNING: '진행 중', PARTIAL_FAILURE: '일부 실패', UNVERIFIED: '확인 필요'};
    const complete = item.latest_completed_analysis || {};
    const status = String(attempt.status || 'UNVERIFIED').toUpperCase();
    return `<p class="analysis-attempt ${status === 'SUCCESS' ? 'readiness-note' : 'expiry-warning'}">최근 전체 분석 시도(사이트 생성 시점): ${esc(labels[status] || status)} · 시작 ${esc(dateTime(attempt.started_at))}<br>현재 참조하는 전체 분석: ${esc(complete.run_id || '미확인')} · 완료 ${esc(dateTime(complete.finished_at))}</p>`;
  }
  function evidenceAudit(sourceSummary) {
    const receipt = ((sourceSummary || {}).external_evidence_receipt || {});
    const sources = receipt.sources || {};
    const rows = ['youtube', 'prism'].map((source) => {
      const payload = sources[source] || {};
      const coverage = payload.coverage || {};
      const transmitted = Number(coverage.transmitted_events ?? (payload.event_keys || []).length ?? 0);
      const windowEvents = Number(coverage.window_events ?? transmitted);
      const omitted = Number(coverage.omitted_events ?? Math.max(0, windowEvents - transmitted));
      const health = String(payload.source_health || 'MISSING').toUpperCase();
      return `<p><strong>${source === 'youtube' ? 'YouTube' : 'PRISM'} · ${esc(health)}</strong><span>전달 ${transmitted} / 검토창 ${windowEvents} · 미전달 ${omitted}</span></p>`;
    }).join('');
    if (!rows || !receipt.schema) return '';
    return `<details class="evidence-audit"><summary>외부 근거 포함·누락 영수증</summary><div class="report-audit-grid">${rows}</div><p class="readiness-note">관련 근거는 순위·신뢰도·위험 한도 안의 비중·조사 우선순위에 반영하되 주문 실행 gate는 우회하지 않습니다.</p></details>`;
  }
  function modelAudit(receipt) {
    if (!receipt || !receipt.schema) return '';
    const analysis = receipt.market_analysis || {};
    const work = receipt.work_synthesis || {};
    const observed = Object.keys(analysis.observed_models || {});
    const analysisModels = observed.length ? observed.join(', ') : Object.values(analysis.requested_models || {}).filter(Boolean).join(', ');
    const analysisStatus = analysis.verification_status === 'RUNTIME_USAGE_OBSERVED' ? '실행 사용량 관측' : '설정만 확인';
    const workStatus = work.verification_status === 'RUNTIME_VERIFIED' ? '런타임 검증' : '설정만 확인 · Chat/Pro 모드 미증명';
    return `<details class="model-audit"><summary>모델 실행 영수증</summary><div class="report-audit-grid">
      <p><strong>종목 분석 · ${esc(analysisStatus)}</strong><span>${esc(analysisModels || '-')} · 호출 ${Number(analysis.observed_calls || 0)}</span></p>
      <p><strong>Work 종합 · ${esc(workStatus)}</strong><span>${esc(work.requested_model || '-')} · reasoning ${esc(work.requested_reasoning_effort || '-')}</span></p>
    </div></details>`;
  }
  function integratedReport(item, field = 'integrated_report') {
    const report = item[field] || {};
    const isReference = field === 'reference_report';
    const analysisOnly = report.analysis_only === true;
    const structured = report.structured_report || {};
    if (!report.report_markdown && !Object.keys(structured).length) return '';
    const title = structured.title || `${item.market || ''} ChatGPT Work 통합 전략`;
    const summary = valueText(structured.summary);
    const topActions = Array.isArray(structured.top_actions) ? structured.top_actions : [];
    const contributions = sourceChips(structured.source_summary);
    return `<section class="integrated-report${isReference ? ' reference-report' : ''}">
      <p class="eyebrow">${isReference ? 'CHATGPT WORK · 분석 시점 참고 전략' : 'CHATGPT WORK · 통합 전략'}</p>
      <h3>${esc(title)}</h3>
      ${isReference ? '<p class="expiry-warning">이 Work 내용은 과거 분석 시점의 참고 보고서입니다. 현재 카드의 방향·순위·분류에는 적용하지 않습니다.</p>' : ''}
      ${analysisOnly ? '<p class="readiness-note">Work 종합 전략 전문과 투자 논지·순위·출처를 유지했습니다. 핵심 액션은 분석 시점 참고이며, 카드의 실행 행동과 준비 상태는 현재 장중 갱신 분석을 사용합니다.</p>' : ''}
      <div class="source-meta"><span>입력 시세 기준 ${esc(dateTime(structured.as_of))}</span><span>Work 게시 ${esc(dateTime(report.published_at || structured.generated_at))}</span></div>
      ${summary ? `<p class="summary">${esc(summary)}</p>` : ''}
      ${analysisOnly && topActions.length ? '<p class="readiness-note"><strong>분석 시점 핵심 액션 참고:</strong> 현재 주문 가능 여부가 아니라 Work 분석 당시 제안입니다.</p>' : ''}
      ${topActions.length ? `<div class="work-top-actions">${topActions.slice(0, 3).map(workTopAction).join('')}</div>` : ''}
      ${topActions.length > 3 ? `<details><summary>통합 핵심 액션 전체 보기</summary><div class="work-top-actions">${topActions.map(workTopAction).join('')}</div></details>` : ''}
      ${contributions ? `<details><summary>자료·출처 상세</summary><div class="source-chips">${contributions}</div></details>` : ''}
      ${evidenceAudit(structured.source_summary)}
      ${modelAudit(structured.model_receipt)}
      ${structured.next_checkpoint ? `<p class="readiness-note"><strong>다음 확인:</strong> ${esc(valueText(structured.next_checkpoint))}</p>` : ''}
      ${report.report_markdown ? `<details><summary>통합 리포트 전체 보기</summary><pre class="markdown-report" data-report-markdown>${esc(report.report_markdown)}</pre></details>` : ''}
    </section>`;
  }
  function marketHealth(item, rows) {
    const sourceHealth = String((item || {}).source_health || 'MISSING').toUpperCase();
    const sourceStatus = String(((item || {}).source || {}).status || (item || {}).manifest_status || '').toLowerCase();
    const coverage = (item || {}).universe_coverage || (item || {}).coverage || {};
    const validUntil = Date.parse(((item || {}).guardrails || {}).valid_until || '');
    const expired = ((item || {}).guardrails || {}).expired_at_build === true || !Number.isFinite(validUntil) || validUntil <= Date.now();
    if (!rows.length) return {className: 'missing', label: '전략 행 없음', empty: '현재 확인 가능한 전략 행이 없습니다. 분석 커버리지가 복구된 뒤 다시 확인하세요.'};
    if (sourceHealth === 'MISSING' || sourceHealth === 'FAILED' || ['failed', 'error'].includes(sourceStatus)) {
      return {className: 'missing', label: '원천 분석 사용 불가', empty: '원천 분석을 사용할 수 없어 현재 전략을 실행 판단에 쓰지 마세요.'};
    }
    if (coverage.status !== 'COMPLETE' || coverage.complete !== true) {
      return {className: 'missing', label: '커버리지 불완전', empty: '필수 종목 분석이 불완전합니다. 누락 분석이 복구될 때까지 기다리세요.'};
    }
    if (sourceHealth !== 'OK' || expired) {
      return {className: 'degraded', label: expired ? '주문 전 실시간 확인' : '원천 상태 재확인', empty: ''};
    }
    if (immediateContractComplete(item)) return {className: 'ok', label: '실행 데이터 확인됨', empty: ''};
    return {className: 'degraded', label: '전략 제공 · 주문 전 확인', empty: ''};
  }
const groups = ['TOP', 'HOLDING', 'WATCHLIST', 'NEW_CANDIDATE', 'ALL'];
  const directions = ['all', 'buy', 'hold', 'reduce', 'sell', 'avoid', 'research'];
  const directionLabels = {all: '전체 방향', buy: '매수·추가 검토', hold: '보유·관찰', reduce: '축소 검토', sell: '매도·청산', avoid: '신규 매수 보류', research: '추가 조사'};
  const sorts = ['priority', 'name', 'change'];
  let selectedMarket = requestedMarket;
  let currentPayload;
  let loading = false;
  const refreshButton = document.getElementById('strategy-refresh');
  const views = Object.fromEntries(['kr', 'us'].map((market) => [market, {
    group: market === requestedMarket && groups.includes(query.get('group')) ? query.get('group') : 'ALL',
    direction: market === requestedMarket && directions.includes(query.get('direction')) ? query.get('direction') : 'all',
    search: market === requestedMarket ? (query.get('q') || '').slice(0, 100) : '',
    sort: market === requestedMarket && sorts.includes(query.get('sort')) ? query.get('sort') : 'priority',
  }]));
  function syncUrl() {
    const url = new URL(location.href);
    const view = views[selectedMarket];
    url.searchParams.set('market', selectedMarket);
    for (const [key, value, fallback] of [['group', view.group, 'ALL'], ['direction', view.direction, 'all'], ['q', view.search, ''], ['sort', view.sort, 'priority']]) {
      if (value === fallback) url.searchParams.delete(key); else url.searchParams.set(key, value);
    }
    history.replaceState(null, '', url);
  }
  function tradePlans(item, ticker) {
    const keys = tickerKeys(ticker);
    const plans = ((item.trade_plan || {}).rows || []);
    if (!Array.isArray(plans)) return [];
    return plans.filter((plan) => plan && typeof plan === 'object' && tickerKeys(plan.ticker).some((key) => keys.includes(key)));
  }
  function planMoney(value, currency) {
    if (!Number.isFinite(numeric(value))) return '미확정';
    const number = Number(value).toLocaleString('ko-KR', {minimumFractionDigits: currency === 'USD' ? 2 : 0, maximumFractionDigits: currency === 'USD' ? 2 : 0});
    return currency === 'USD' ? '$' + number : number + '원';
  }
  function planPhase(plan) {
    if (plan.phase === 'OBSERVE') return '현재 주문 없음';
    return (plan.phase === 'CONDITIONAL' ? '조건 충족 시 ' : '검토 ') + (plan.action_label || actionLabel(plan.action) || '계획');
  }
  function planParts(plans, renderPart) {
    return plans.map((plan) => '<div class="plan-part"><span class="plan-phase">' + esc(planPhase(plan)) + '</span>' + renderPart(plan) + '</div>').join('');
  }
  function planPrice(plan) {
    if (plan.price_kind === 'NONE') return '해당 없음';
    const low = numeric(plan.price_low), high = numeric(plan.price_high);
    if (!Number.isFinite(low) || !Number.isFinite(high) || low <= 0 || high < low) return '범위 미확정';
    const band = planMoney(low, plan.currency) + (low === high ? '' : ' ~ ' + planMoney(high, plan.currency));
    const comparator = {'>=': ' 이상', '>': ' 초과', '<=': ' 이하', '<': ' 미만'}[plan.price_comparator] || '';
    return band + (plan.price_kind === 'TRIGGER' ? comparator : '');
  }
  function tradeSummaryRow(entry, item) {
    const ticker = entry.dataset.ticker;
    const direction = entry.querySelector('.strategy-direction').textContent;
    const readiness = entry.querySelector('.card-title .row-mode').textContent;
    const inputPrice = entry.querySelector('.price-line strong').textContent;
    let plans = tradePlans(item, ticker);
    if (!plans.length) plans = [{phase: 'OBSERVE', action: 'WAIT', quantity: null, currency: panelCurrency(item), reasons: ['수량·가격 계획 자료를 다시 생성해야 합니다.'], conditions: []}];
    const quantities = planParts(plans, (plan) => {
      const qty = numeric(plan.quantity);
      const valid = Number.isInteger(qty) && qty >= 0;
      return '<strong class="plan-value">' + (valid ? esc(fmt(qty)) + '주' : '산출 보류') + '</strong><small>' + esc(valid && qty === 0 ? plan.status_label || '추가 거래 없음' : '입력 계좌 기준 검토 수량') + '</small>';
    });
    const prices = planParts(plans, (plan) => '<strong class="plan-value">' + esc(planPrice(plan)) + '</strong><small>' + esc(['TRIGGER', 'TRIGGER_RANGE', 'REFERENCE'].includes(plan.price_kind) ? '발동 기준 · 체결 범위 아님' : plan.price_kind === 'NONE' ? '추가 거래 계획 없음' : '분석의 가격 범위') + '</small>');
    const amounts = planParts(plans, (plan) => {
      const amount = plan.estimated_net_cash ?? plan.estimated_gross_high;
      const fee = numeric(plan.estimated_fees);
      const costKnown = Number.isFinite(numeric(plan.estimated_net_cash));
      const label = !costKnown && Number.isFinite(numeric(amount)) ? '거래대금 · 비용 미확정' : plan.action === 'SELL' ? '상단 기준 예상 수령액' : plan.action === 'BUY' ? '상단 기준 예상 지출' : '추가 거래 금액';
      return '<strong class="plan-value">' + esc(planMoney(Number.isFinite(numeric(amount)) ? Math.abs(Number(amount)) : null, plan.currency)) + '</strong><small>' + esc(label) + (Number.isFinite(fee) ? ' · 수수료·거래세 ' + esc(planMoney(fee, plan.currency)) : '') + '</small>';
    });
    const conditions = planParts(plans, (plan) => {
      const quantity = numeric(plan.quantity);
      const deadline = Date.parse(plan.valid_until || '');
      const planRecheck = plan.status === 'RECHECK' || !Number.isFinite(deadline) || deadline <= Date.now() || (item.trade_plan || {}).account_fresh !== true;
      const current = entry.dataset.readiness === 'READY' && plan.phase === 'NOW' && quantity > 0 && plan.status === 'CONDITIONAL' && !planRecheck;
      const state = current ? '검토 가능 · 주문 전 최종 확인' : plan.phase === 'OBSERVE' ? '현재 주문 없음' : planRecheck || entry.dataset.readiness === 'RECHECK' || entry.dataset.readiness === 'RESEARCH' ? '현재 주문 없음 · 시세·계좌 재확인' : '조건 충족 전 주문 없음';
      const reasons = fullConditions(plan.reasons);
      const trigger = fullConditions(plan.condition, plan.trigger_conditions);
      const issue = Array.isArray(plan.reasons) ? plan.reasons[0] : '';
      return '<span class="plan-status">' + esc(state) + '</span>' + (issue ? '<small>' + esc(issue) + '</small>' : '') + (trigger || reasons ? '<details class="plan-details" data-plan-id="' + esc(plan.id || ticker + ':' + plan.phase) + '"><summary>발동 조건·산출 근거 전체 보기</summary>' + (trigger ? '<span class="plan-condition">' + esc(trigger) + '</span>' : '') + (reasons ? '<small>' + esc(reasons) + '</small>' : '') + (plan.valid_until ? '<small>기한 ' + esc(dateTime(plan.valid_until)) + '</small>' : '') + '</details>' : '');
    });
    return `<tr data-ticker="${esc(ticker)}"><td class="plan-symbol" data-label="종목"><button type="button" class="summary-detail" data-detail-target="${esc(entry.id)}" aria-label="${esc(entry.dataset.name)} 전략 조건·위험 상세 보기">${esc(entry.dataset.name)}</button><small>${esc(ticker)} · ${esc(roleLabel(entry.dataset.group))}</small><small>입력 시세 ${esc(inputPrice)}${panelCurrency(item) === 'USD' ? ' USD' : '원'}</small></td><td class="plan-action" data-label="전략"><span class="summary-direction" data-direction="${esc(entry.dataset.direction)}">${esc(direction)}</span><small>${esc(readiness)}</small></td><td class="plan-quantity" data-label="검토 수량">${quantities}</td><td class="plan-price" data-label="가격 범위·기준">${prices}</td><td class="plan-amount" data-label="예상 금액">${amounts}</td><td class="plan-check" data-label="발동 조건·현재 상태">${conditions}</td></tr>`;
  }
  function panelCurrency(item) { return String(item.market || '').toUpperCase() === 'US' ? 'USD' : 'KRW'; }
  function applyView(panel) {
    const view = views[panel.dataset.market];
    const entries = [...panel.querySelectorAll('.action-card')];
    const ordered = [...entries].sort((a, b) => {
      if (view.sort === 'name') return a.dataset.search.localeCompare(b.dataset.search, 'ko');
      if (view.sort === 'change') {
        const left = numeric(a.dataset.change), right = numeric(b.dataset.change);
        if (!Number.isFinite(left)) return Number.isFinite(right) ? 1 : 0;
        if (!Number.isFinite(right)) return -1;
        return right - left;
      }
      return Number(a.dataset.order) - Number(b.dataset.order);
    });
    const container = panel.querySelector('.cards');
    if (ordered.some((entry, index) => entry !== entries[index])) container.append(...ordered);
    const terms = view.search.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    let visible = 0;
    for (const entry of entries) {
      const inGroup = view.group === 'ALL' || (view.group === 'TOP' ? entry.dataset.top === 'true' : entry.dataset.group === view.group);
      entry.hidden = !inGroup || (view.direction !== 'all' && entry.dataset.direction !== view.direction) || !terms.every((term) => entry.dataset.search.includes(term));
      if (!entry.hidden) visible += 1;
    }
    panel.querySelectorAll('[data-group-target]').forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.groupTarget === view.group)));
    panel.querySelectorAll('[data-direction-target]').forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.directionTarget === view.direction)));
    panel.querySelector('.result-count').textContent = entries.length + '개 중 ' + visible + '개 표시 · ' + directionLabels[view.direction];
    panel.querySelector('.strategy-summary h3').textContent = view.direction === 'all' && view.group === 'ALL' && !view.search ? '전체 전략 한눈에' : directionLabels[view.direction] + ' · ' + visible + '종목';
    panel.querySelector('.filter-empty').hidden = visible > 0 || entries.length === 0;
    const scroll = panel.querySelector('.summary-scroll');
    const scrollTop = scroll.scrollTop;
    const openPlans = new Set([...scroll.querySelectorAll('.plan-details[open]')].map((detail) => detail.dataset.planId));
    const focusedPlan = document.activeElement?.closest('.plan-details')?.dataset.planId;
    panel.querySelector('.strategy-summary tbody').innerHTML = ordered.filter((entry) => !entry.hidden).map((entry) => tradeSummaryRow(entry, currentPayload.markets[panel.dataset.market] || {})).join('');
    panel.querySelectorAll('.plan-details').forEach((detail) => {
      detail.open = openPlans.has(detail.dataset.planId);
      if (detail.dataset.planId === focusedPlan) detail.querySelector('summary').focus({preventScroll: true});
    });
    scroll.scrollTop = scrollTop;
    scroll.hidden = visible === 0;
  }
  function updateCards(panel, item) {
    const rows = Array.isArray(item.rows) ? item.rows : [];
    const ranked = [...rows].sort((a, b) => rowPriority(b, workStrategy(item, b.ticker)) - rowPriority(a, workStrategy(item, a.ticker)));
    const topTickers = new Set(ranked.slice(0, Math.min(3, ranked.length)).map((row) => tickerKeys(row.ticker)[0]));
    const opened = new Set();
    panel.querySelectorAll('.action-card').forEach((entry) => entry.querySelectorAll('details').forEach((detail, index) => {
      if (detail.open) opened.add(entry.dataset.ticker + ':' + index);
    }));
    const active = document.activeElement;
    const focusedDirection = active && active.dataset.directionTarget;
    const focusedDetail = active && active.dataset.detailTarget;
    const focusedCard = active && active.closest('.action-card');
    const focusedIndex = focusedCard ? [...focusedCard.querySelectorAll('summary, a, button')].indexOf(active) : -1;
    const focusedTicker = focusedCard && focusedCard.dataset.ticker;
    const health = marketHealth(item, rows);
    panel.querySelector('.market-health').className = 'health market-health health-' + health.className;
    panel.querySelector('.market-health').textContent = health.label;
    panel.querySelector('.overview-container').innerHTML = marketOverview(rows, item);
    panel.querySelector('.cards').innerHTML = ranked.map((row) => card(row, item, topTickers, panel.dataset.market)).join('') || '<p class="empty">' + esc(health.empty || '현재 표시할 전략 데이터가 없습니다.') + '</p>';
    const counts = {TOP: topTickers.size, ALL: rows.length};
    panel.querySelectorAll('.action-card').forEach((entry, index) => {
      entry.dataset.order = String(index);
      counts[entry.dataset.group] = (counts[entry.dataset.group] || 0) + 1;
      entry.querySelectorAll('details').forEach((detail, detailIndex) => { detail.open = opened.has(entry.dataset.ticker + ':' + detailIndex); });
    });
    panel.querySelectorAll('[data-group-target]').forEach((button) => {
      button.textContent = button.dataset.label + ' ' + (counts[button.dataset.groupTarget] || 0);
    });
    applyView(panel);
    if (focusedDirection) [...panel.querySelectorAll('[data-direction-target]')].find((node) => node.dataset.directionTarget === focusedDirection)?.focus({preventScroll: true});
    if (focusedDetail) [...panel.querySelectorAll('[data-detail-target]')].find((node) => node.dataset.detailTarget === focusedDetail)?.focus({preventScroll: true});
    if (focusedTicker && focusedIndex >= 0) {
      const entry = [...panel.querySelectorAll('.action-card')].find((node) => node.dataset.ticker === focusedTicker);
      if (entry && !entry.hidden) entry.querySelectorAll('summary, a, button')[focusedIndex]?.focus({preventScroll: true});
    }
  }
  function mountMarket(panel) {
    if (panel.dataset.mounted) return;
    const market = panel.dataset.market;
    const item = currentPayload.markets[market] || {};
    const view = views[market];
    const sourceLabel = item.integrated_report
      ? item.integrated_report.analysis_only === true ? 'Work 분석 결합 · 현재 실행 우선' : '현재 Work 종합 완료'
      : item.reference_report ? '기본 전략 · 분석 시점 Work 참고' : '기본 전략';
    panel.innerHTML = '<div class="market-head"><div><p class="eyebrow">' + market.toUpperCase() + ' STRATEGY</p><h2>' + market.toUpperCase() + ' 투자 액션</h2></div><div><span class="health health-neutral">' + sourceLabel + '</span><span class="health market-health"></span></div></div><p class="snapshot-clock">입력 시세 ' + esc(dateTime((item.freshness_receipt || {}).market_data_oldest_at)) + '</p><details class="source-disclosure"><summary>자료 시점·분석 상태 확인</summary>' + attemptStatus(item)
      + '<div class="source-meta"><span>일봉 가격 기준일 ' + esc((item.freshness_receipt || {}).analysis_trade_date_oldest || '미확인') + '</span><span>시세 기준 ' + esc(dateTime((item.freshness_receipt || {}).market_data_oldest_at)) + '</span><span>계좌 기준 ' + esc(dateTime((item.freshness_receipt || {}).account_as_of)) + '</span><span>자료 갱신 실행 ' + esc(dateTime(item.started_at)) + '</span><span>실행 ID ' + esc(item.run_id || '-') + '</span></div></details><div class="overview-container"></div>'
      + '<div class="strategy-toolbar"><label for="search-' + market + '">종목 검색<input id="search-' + market + '" type="search" maxlength="100" placeholder="종목명 · 티커 · 업종" value="' + esc(view.search) + '" autocomplete="off" aria-controls="cards-' + market + '"></label>'
      + '<label for="sort-' + market + '">정렬<select id="sort-' + market + '"><option value="priority">우선순위</option><option value="name">종목명순</option><option value="change">등락률순 ↓</option></select></label></div>'
      + '<nav class="strategy-filters" aria-label="종목 유형">' + groups.map((group, index) => '<button type="button" data-group-target="' + group + '" data-label="' + ['핵심','보유','관심','신규','전체'][index] + '" aria-pressed="false"></button>').join('') + '</nav>'
      + '<p class="result-count" role="status" aria-live="polite" aria-atomic="true"></p>'
      + '<section class="strategy-summary" id="summary-' + market + '" tabindex="-1"><h3>전체 전략 한눈에</h3><p class="readiness-note">매매 전략표 · 수량 → 가격 → 발동 조건 순서로 확인하세요. 종목명을 누르면 상세 근거가 열립니다.</p><p class="plan-source-note">' + esc((item.trade_plan || {}).account_asof ? '수량 기준 계좌 ' + dateTime(item.trade_plan.account_asof) : '수량 기준 계좌 확인 불가') + ' · KR 원화 / US 달러</p><details class="plan-method"><summary>수량·비용 계산 기준</summary><p>' + esc(fullConditions((item.trade_plan || {}).assumptions) || '정수 수량과 수수료를 반영한 검토안입니다. 자료가 부족하면 수량·가격을 임의로 만들지 않습니다.') + '</p><p>조건부 계획은 현재 주문과 구분합니다. 여러 계획은 동시에 실행하는 주문 묶음이 아닙니다. 매도 예정 대금을 미리 매수 예산으로 쓰지 않으며, 종목별 상세 근거와 현재 상태를 함께 확인하세요.</p></details><div class="filter-empty" hidden><p>검색 조건에 맞는 종목이 없습니다.</p><button type="button" class="reset-filters">검색·필터 초기화</button></div><div class="summary-scroll" role="region" aria-label="종목별 매매 전략표 · 스크롤하여 전체 보기" tabindex="0"><table><thead><tr><th scope="col">종목</th><th scope="col">전략</th><th scope="col">검토 수량</th><th scope="col">가격 범위·기준</th><th scope="col">예상 금액</th><th scope="col">발동 조건·현재 상태</th></tr></thead><tbody></tbody></table></div></section>'
      + '<div class="cards" id="cards-' + market + '"></div>' + integratedReport(item) + integratedReport(item, 'reference_report');
    const search = panel.querySelector('input');
    const sort = panel.querySelector('select');
    sort.value = view.sort;
    const update = () => { applyView(panel); syncUrl(); };
    panel.addEventListener('click', (event) => {
      const direction = event.target.closest('[data-direction-target]');
      if (direction) {
        view.direction = direction.dataset.directionTarget === view.direction ? 'all' : direction.dataset.directionTarget;
        view.group = 'ALL'; view.search = ''; search.value = ''; update();
        const summary = panel.querySelector('.strategy-summary');
        summary.scrollIntoView({block: 'start'}); summary.focus({preventScroll: true});
      }
      const detail = event.target.closest('[data-detail-target]');
      if (detail) {
        const card = document.getElementById(detail.dataset.detailTarget);
        if (card && !card.hidden) { card.scrollIntoView({block: 'start'}); card.focus({preventScroll: true}); }
      }
      if (event.target.closest('.back-to-overview')) {
        const summary = panel.querySelector('.strategy-summary');
        summary.scrollIntoView({block: 'start'}); summary.focus({preventScroll: true});
      }
    });
    search.addEventListener('input', () => {
      view.search = search.value;
      if (view.search.trim() && view.group === 'TOP') view.group = 'ALL';
      update();
    });
    sort.addEventListener('change', () => { view.sort = sort.value; update(); });
    panel.querySelectorAll('[data-group-target]').forEach((button) => button.addEventListener('click', () => { view.group = button.dataset.groupTarget; update(); }));
    panel.querySelector('.reset-filters').addEventListener('click', () => {
      view.group = 'ALL'; view.direction = 'all'; view.search = ''; view.sort = 'priority'; search.value = ''; sort.value = 'priority'; update(); search.focus();
    });
    if (view.search.trim() && view.group === 'TOP') view.group = 'ALL';
    panel.dataset.mounted = 'true';
    updateCards(panel, item);
    panel.querySelectorAll('.integrated-report').forEach(report => window.TradingAgentsReader?.enhance(report));
  }
  function selectMarket(market) {
    selectedMarket = market;
    tabs.querySelectorAll('button').forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.target === market)));
    root.querySelectorAll('[data-market]').forEach((panel) => {
      panel.hidden = panel.dataset.market !== market;
      if (!panel.hidden) mountMarket(panel);
    });
    syncUrl();
  }
  function scheduleExpiry() {
    clearTimeout(expiryTimer);
    const now = Date.now();
    const deadlines = Object.values(currentPayload.markets).flatMap((item) => [
      Date.parse((item.guardrails || {}).valid_until || ''),
      ...(item.rows || []).map((row) => Date.parse((row.quality || {}).row_valid_until || '')),
    ]).filter((deadline) => Number.isFinite(deadline) && deadline > now);
    if (deadlines.length) expiryTimer = setTimeout(refreshExpiry, Math.min(2147483647, Math.max(50, Math.min(...deadlines) - now + 50)));
  }
  function refreshExpiry() {
    if (!currentPayload) return;
    root.querySelectorAll('[data-mounted]').forEach((panel) => updateCards(panel, currentPayload.markets[panel.dataset.market] || {}));
    scheduleExpiry();
  }
  function render(payload) {
    if (requestedRun && String((payload.markets[requestedMarket] || {}).run_id || '') !== requestedRun) {
      throw new Error('Telegram 링크의 분석 실행 ID와 현재 투자 대시보드 실행 ID가 일치하지 않습니다. 최신 알림을 사용하세요.');
    }
    currentPayload = payload;
    tabs.hidden = false;
    tabs.innerHTML = ['kr', 'us'].map((market) => '<button type="button" data-target="' + market + '" aria-pressed="false">' + market.toUpperCase() + '</button>').join('');
    root.innerHTML = ['kr', 'us'].map((market) => '<section class="market-panel" data-market="' + market + '" hidden></section>').join('');
    tabs.querySelectorAll('button').forEach((button) => button.addEventListener('click', () => selectMarket(button.dataset.target)));
    selectMarket(selectedMarket);
    status.textContent = '페이지 생성 ' + dateTime(payload.generated_at) + ' · 게시 시각은 원분석·시세·계좌의 갱신 시각이 아닙니다.';
    scheduleExpiry();
  }
  async function start() {
    if (loading) return;
    loading = true;
    refreshButton.disabled = true;
    root.setAttribute('aria-busy', 'true');
    status.classList.remove('error');
    status.textContent = '최신 전략 데이터를 확인하고 있습니다.';
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15000);
    try {
      const response = await fetch(document.body.dataset.strategyUrl || 'strategy.json', {cache: 'no-store', credentials: 'omit', signal: controller.signal});
      if (!response.ok) throw new Error('통합 투자 전략이 아직 게시되지 않았습니다.');
      const payload = await response.json();
      if (payload.schema !== 'tradingagents.mobile-strategy/v1' || !payload.markets || typeof payload.markets !== 'object' || Array.isArray(payload.markets)
          || Object.values(payload.markets).some((item) => !item || typeof item !== 'object' || Array.isArray(item)
            || (item.rows != null && (!Array.isArray(item.rows) || item.rows.some((row) => !row || typeof row !== 'object' || Array.isArray(row)))))) {
        throw new Error('통합 전략 데이터 형식이 올바르지 않습니다.');
      }
      const previousPayload = currentPayload;
      try {
        render(payload);
      } catch (error) {
        // Keep the last known snapshot if nested report data cannot render.
        if (previousPayload) render(previousPayload);
        else { currentPayload = undefined; tabs.hidden = true; root.replaceChildren(); }
        throw error;
      }
    } catch (error) {
      status.classList.add('error');
      status.textContent = (error.name === 'AbortError' ? '데이터 연결 시간이 초과되었습니다.' : error.message || '통합 투자 전략을 열 수 없습니다.')
        + (currentPayload ? ' 이전에 받은 데이터를 표시 중입니다.' : '') + ' 새로고침으로 다시 시도하세요.';
    } finally {
      clearTimeout(timeout);
      loading = false;
      refreshButton.disabled = false;
      root.setAttribute('aria-busy', 'false');
    }
  }
  refreshButton.addEventListener('click', start);
  document.addEventListener('visibilitychange', () => { if (!document.hidden) refreshExpiry(); });
  window.addEventListener('pageshow', refreshExpiry);
  start();
})();