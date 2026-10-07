"""Offline HTML companion for the existing localized Markdown report.

Report/model text cannot introduce raw HTML, scripts, images, or remote assets.
"""

from html import escape
from urllib.parse import urlsplit

from markdown_it import MarkdownIt


_CSS = """
:root { color-scheme: light; --ink:#18232d; --muted:#52616b; --rule:#dce4e8; }
* { box-sizing:border-box; }
body { margin:0; background:#f7f9fa; color:var(--ink);
  font:16px/1.75 system-ui,-apple-system,'Segoe UI','Malgun Gothic',sans-serif; }
.page { max-width:960px; margin:auto; padding:40px 36px 80px; background:white; }
h1 { font-size:2rem; line-height:1.3; } h2 { margin-top:2.5rem; border-top:2px solid var(--rule); padding-top:1.3rem; }
h3 { margin-top:1.8rem; } h1,h2,h3,h4 { scroll-margin-top:20px; overflow-wrap:anywhere; }
a { color:#006b59; overflow-wrap:anywhere; } a:focus-visible { outline:2px solid #006b59; }
nav { border:1px solid var(--rule); border-radius:8px; padding:16px 24px; }
nav ul { padding-left:20px; } nav a { text-decoration:none; } nav a:hover { text-decoration:underline; }
p,li,td { overflow-wrap:anywhere; } blockquote { border-left:3px solid var(--rule); margin-left:0; padding-left:20px; color:var(--muted); }
pre { overflow:auto; padding:16px; background:#f1f5f6; border-radius:6px; }
code { font-size:.9em; } .table { overflow-x:auto; }
table { width:100%; border-collapse:collapse; font-size:.9rem; }
th,td { text-align:left; padding:9px 12px; border-bottom:1px solid var(--rule); vertical-align:top; }
th { background:#f1f5f6; } footer { color:var(--muted); border-top:1px solid var(--rule); margin-top:40px; padding-top:16px; }
@media(max-width:600px) { .page { padding:24px 18px 48px; } h1 { font-size:1.6rem; } }
@media print { body,.page { background:white; } .page { max-width:none; padding:0; }
  nav { display:none; } h1,h2,h3,h4 { break-after:avoid; } pre { white-space:pre-wrap; } .table { overflow:visible; } }
"""


def _safe_link(value: str) -> bool:
    try:
        return value.startswith("#") or urlsplit(value).scheme.lower() in {"http", "https"}
    except ValueError:
        return False


def render_report_html(markdown: str, *, title: str, language: str = "English") -> str:
    """Render one portable page. Links can navigate only to HTTP(S) or anchors."""
    md = MarkdownIt("commonmark", {"html": False, "breaks": True}).enable("table").disable("image")
    md.validateLink = _safe_link
    md.add_render_rule("table_open", lambda *args: '<div class="table"><table>\n')
    md.add_render_rule("table_close", lambda *args: "</table></div>\n")
    tokens = md.parse(markdown)
    contents = []
    for index, token in enumerate(tokens):
        if token.type == "heading_open" and token.tag == "h2":
            anchor = f"section-{len(contents) + 1}"
            token.attrSet("id", anchor)
            text = tokens[index + 1].content if index + 1 < len(tokens) else ""
            contents.append(f'<li><a href="#{anchor}">{escape(text)}</a></li>')
    body = md.renderer.render(tokens, md.options, {})
    korean = language.strip().lower() == "korean"
    navigation = (f'<nav aria-label="{"목차" if korean else "Contents"}">'
                  f'<strong>{"목차" if korean else "Contents"}</strong><ul>'
                  + "".join(contents) + "</ul></nav>") if contents else ""
    return (
        '<!doctype html>\n<html lang="' + ("ko" if korean else "en") + '"><head>'
        '<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; '
        'style-src \'unsafe-inline\'; img-src \'none\'; base-uri \'none\'; form-action \'none\'">'
        '<meta name="referrer" content="no-referrer">'
        f'<title>{escape(title)}</title><style>{_CSS}</style></head><body><div class="page">'
        f'{navigation}<main>{body}</main><footer>TradingAgents</footer></div></body></html>\n'
    )
