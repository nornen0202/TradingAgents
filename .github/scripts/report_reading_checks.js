(async () => {
  let checks = 0;
  const check = (ok, message) => { checks += 1; if (!ok) throw new Error(message); };
  const tick = async () => {
    for (let n = 0; n < 100 && document.getElementById('report').hidden; n += 1) await new Promise(r => setTimeout(r, 30));
    check(!document.getElementById('report').hidden, 'Report request completed');
  };
  await tick();
  check(document.querySelectorAll('.reader-prose h2,.reader-prose h3').length === 3, 'Markdown headings become navigable sections');
  check(document.querySelector('.reader-prose strong').textContent === 'AND', 'Compound condition emphasis preserved');
  check(document.querySelector('.reader-prose table').textContent.includes('Below 90'), 'Markdown risk table preserved');
  check(!window.readerInjected && !document.querySelector('.reader-prose script'), 'Report HTML is inert text');
  check(!document.querySelector('.reader-prose a[href^="javascript:"]'), 'Dangerous Markdown URL is inert');
  check(document.querySelector('[data-reader-source] pre').textContent.includes('<script>'), 'Original source remains inspectable');
  check(document.documentElement.scrollWidth <= innerWidth + 1, 'Work reader fits viewport');
  const contents = document.querySelector('#report > .reader-contents');
  contents.querySelector('a').click();
  check(document.activeElement.hasAttribute('data-reader-heading'), 'Work TOC focuses section');
  const kr = document.querySelector('[data-surface=kr]');
  kr.dispatchEvent(new KeyboardEvent('keydown', {key: 'ArrowRight', bubbles: true}));
  await tick();
  check(document.getElementById('title').textContent === 'US report' && document.activeElement.dataset.surface === 'us', 'Arrow-key market navigation');
  const realFetch = window.fetch;
  let release;
  const slow = {report_markdown: '## OLD\nold report', structured_report: {title: 'OLD delayed response'}};
  window.fetch = async (url, options) => {
    if (url.includes('/kr/')) return new Promise(resolve => { release = () => resolve({ok: true, json: async () => slow}); });
    return realFetch(url, options);
  };
  kr.click();
  document.querySelector('[data-surface=us]').click();
  await tick(); release(); await new Promise(r => setTimeout(r, 0));
  check(document.getElementById('title').textContent === 'US report', 'Old slow response cannot replace newly selected report');
  check(new URL(location.href).searchParams.get('surface') === 'us', 'Selected report URL stays consistent');
  window.fetch = async () => { throw new Error('offline test'); };
  document.querySelector('[data-surface=prism]').click();
  for (let n = 0; n < 100 && document.getElementById('retry-report').hidden; n += 1) await new Promise(r => setTimeout(r, 20));
  check(!document.getElementById('retry-report').hidden, 'Connection failure offers retry');
  window.fetch = realFetch;
  document.getElementById('retry-report').click(); await tick();
  check(document.getElementById('title').textContent === 'PRISM report', 'Retry loads the failed selection');
  check(document.querySelectorAll('.reader-contents').length === 1 && document.querySelectorAll('.reader-prose').length === 1, 'Switching does not duplicate reader controls');
  return {passed: checks};
})()
