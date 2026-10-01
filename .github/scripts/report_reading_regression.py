"""Exercise report navigation, safe Markdown, search and request races in a browser."""
from __future__ import annotations

import asyncio
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import mobile_layout_regression as layout
from tradingagents.prism_telegram.site import _page as prism_page
from tradingagents.scheduled.site import _page_template
from tradingagents.work.site import _readable_html, _work_report_index_html
from tradingagents.youtube.site import _page as youtube_page


class _AbortAwareHandler(layout._QuietHandler):
    def handle(self):
        try:
            super().handle()
        except (ConnectionResetError, BrokenPipeError):
            # The race test deliberately aborts requests when changing tabs.
            pass


async def probe(websocket_url: str, page_url: str) -> list[dict]:
    results = []
    call_id = 0
    origin = page_url.split('/mobile/')[0]
    async with layout.websockets.connect(websocket_url, max_size=8 * 1024 * 1024) as socket:
        async def call(method, params=None):
            nonlocal call_id
            call_id += 1
            return await layout._cdp_call(socket, call_id, method, params)

        async def evaluate(expression):
            value = await call('Runtime.evaluate', {'expression': expression, 'awaitPromise': True, 'returnByValue': True})
            if value.get('exceptionDetails'):
                raise RuntimeError(json.dumps(value['exceptionDetails'], ensure_ascii=False))
            return value['result'].get('value')

        await call('Page.enable')
        for width in (360, 390, 430, 1440):
            await call('Emulation.setDeviceMetricsOverride', {'width': width, 'height': 900, 'deviceScaleFactor': 1, 'mobile': width < 600})
            for surface in ('youtube', 'prism', 'research', 'static', 'work'):
                await call('Page.navigate', {'url': origin + '/' + surface + '/index.html'})
                for _ in range(100):
                    await asyncio.sleep(.05)
                    if await evaluate("Boolean(window.TradingAgentsReader && document.querySelector('.reader-contents'))"):
                        break
                else:
                    raise RuntimeError('Report enhancement did not initialize: ' + surface)
                if surface == 'work':
                    checks = await evaluate(Path(__file__).with_name('report_reading_checks.js').read_text(encoding='utf-8'))
                else:
                    checks = await evaluate(r"""(() => {
                      const check = (ok, message) => { if (!ok) throw new Error(message); };
                      const link = document.querySelector('.reader-contents a'); link.click();
                      check(document.activeElement.id === link.hash.slice(1), 'TOC moves keyboard focus');
                      check(document.querySelector('.reader-table'), 'Report table can scroll independently');
                      check(document.documentElement.scrollWidth <= innerWidth + 1, 'Report must not overflow viewport');
                      const input = document.querySelector('.reader-search input');
                      if (input) {
                        input.value = 'semiconductor'; input.dispatchEvent(new Event('input'));
                        check(document.querySelectorAll('.grid > a.card:not([hidden])').length === 1, 'Report search filters cards');
                        input.value = 'no-match'; input.dispatchEvent(new Event('input'));
                        check(document.querySelector('.reader-search [role=status]').textContent.includes('0개 표시'), 'No-results explanation');
                        input.value = ''; input.dispatchEvent(new Event('input'));
                        check(document.querySelectorAll('.grid > a.card:not([hidden])').length === 2, 'Clearing query restores cards');
                      }
                      document.querySelector('.reader-back').click();
                      check(document.activeElement.tagName === 'H1', 'Return to top restores heading focus');
                      return {search: Boolean(input), toc: true, overflow: false};
                    })()""")
                results.append({'surface': surface, 'width': width, 'checks': checks})
    return results


def main() -> int:
    with tempfile.TemporaryDirectory(prefix='tradingagents-report-reader-') as temp:
        root = Path(temp)
        body = ('<h1>투자 리포트</h1><h2>핵심 근거</h2><p>조건과 위험을 보존합니다.</p>'
                '<div class="grid"><a class="card" href="#">Semiconductor research</a><a class="card" href="#">Energy report</a></div>'
                '<h2>종목 비교</h2><table><tr><th>종목</th><th>조건</th><th>위험</th><th>출처</th></tr>'
                '<tr><td>ALPHA</td><td>Close AND volume</td><td>Below 90</td><td>Original evidence</td></tr></table>')
        pages = {
            'youtube': youtube_page(title='YouTube', body=body),
            'prism': prism_page(title='PRISM', body=body),
            'research': _page_template('Research', body, prefix='../'),
            'static': _readable_html('Work', body, enhance=True),
            'work': _work_report_index_html(),
        }
        # Serve the real research stylesheet as well, including its mobile rules.
        from tradingagents.scheduled.site import _STYLE_CSS
        (root/'assets').mkdir()
        (root/'assets/style.css').write_text(_STYLE_CSS, encoding='utf-8')
        for surface, page in pages.items():
            (root/surface).mkdir()
            (root/surface/'index.html').write_text(page, encoding='utf-8')
        for surface in ('kr', 'us', 'youtube', 'prism'):
            target = root/'work/v1'/surface/'report'
            target.mkdir(parents=True)
            payload = {'surface': surface, 'report_markdown': '# Overview\n\n## Conditions\n\n- Close **AND** volume\n\n| Ticker | Risk |\n| --- | --- |\n| ALPHA | Below 90 |\n\n<script>window.readerInjected=true</script>\n\n[bad](javascript:alert(1))\n\n## Evidence\n\n[Source](https://example.com/source)\n', 'structured_report': {'title': surface.upper() + ' report', 'summary': 'Conditions remain unchanged.'}}
            (target/'latest.json').write_text(json.dumps(payload), encoding='utf-8')
        layout._probe_viewports = probe
        layout._QuietHandler = _AbortAwareHandler
        with layout._serve(root) as url:
            results = layout._run_probe(url, root/'chrome')
    print(json.dumps({'status': 'PASSED', 'viewports': results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
