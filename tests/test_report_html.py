from html.parser import HTMLParser
import json

from tradingagents.report_html import render_report_html
from tradingagents.reporting import save_report_bundle


class _Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.tags = []
        self.links = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        if tag == "a":
            self.links.append(dict(attrs).get("href", ""))


def test_html_is_offline_and_escapes_model_markup():
    page = render_report_html(
        '# Report\n\n## News\n<script>alert(1)</script>\n'
        '<img src="https://tracker.invalid/a" onerror="alert(1)">\n\n'
        '![tracking](https://tracker.invalid/pixel)\n'
        '[bad](javascript:alert%281%29) [file](file:///etc/passwd) '
        '[data](data:text/html,evil) [good](https://example.com/news)\n\n'
        '| Date | News |\n| --- | --- |\n| Today | 한국어 |',
        title='AAPL</title><script>alert(2)</script>', language="Korean",
    )
    parsed = _Page(page)
    assert not {"script", "img", "iframe", "object", "embed", "form", "link"}.intersection(parsed.tags)
    assert "table" in parsed.tags
    # Disabled image syntax can be a plain link; it must never load an asset.
    assert set(parsed.links) == {"#section-1", "https://example.com/news", "https://tracker.invalid/pixel"}
    assert "default-src 'none'" in page
    assert '<html lang="ko">' in page
    assert "한국어" in page


def test_bundle_preserves_markdown_and_records_only_public_settings(tmp_path):
    settings = {
        "llm_provider": "codex", "quick_think_llm": "gpt-6-sol",
        "deep_think_provider": "openai", "deep_think_llm": "manager-model",
        "analysts": ["market", "news"], "max_tokens": 1024,
        "backend_url": "https://user:SECRET_PASSWORD@host/?token=SECRET_QUERY",
        "api_key": "SECRET_API", "codex_workspace_dir": "PRIVATE_HOME",
        "nested": {"password": "SECRET_NESTED"},
        "data_vendors": {"news_data": "alpha_vantage,yfinance", "api_key": "SECRET_VENDOR"},
        "tool_vendors": {"get_company_news": "yfinance", "api_key": "SECRET_TOOL"},
    }
    path = save_report_bundle(
        {"market_report": "## 시장 상황\n\n한국어 분석", "trade_date": "2026-04-02"},
        "005930.KS", tmp_path, language="Korean", settings=settings,
    )
    assert path == tmp_path / "complete_report.md"
    assert (tmp_path / "1_analysts" / "market.md").read_text(encoding="utf-8").endswith("한국어 분석")
    metadata = json.loads((tmp_path / "run_settings.json").read_text(encoding="utf-8"))
    assert metadata["deep_think_provider"] == "openai"
    assert metadata["quick_think_provider"] == "codex"
    assert metadata["output_think_provider"] == "codex"
    assert metadata["max_tokens"] == 1024
    assert metadata["analysts"] == ["market", "news"]
    for artifact in (path, tmp_path / "run_settings.json", tmp_path / "complete_report.html"):
        text = artifact.read_text(encoding="utf-8")
        assert "SECRET" not in text
        assert "PRIVATE_HOME" not in text
    assert "실행 설정" in path.read_text(encoding="utf-8")
    assert "시장 데이터 기준일: 2026-04-02" in (tmp_path / "complete_report.html").read_text(encoding="utf-8")


def test_html_can_be_disabled(tmp_path):
    save_report_bundle({"market_report": "Earlier"}, "AAPL", tmp_path, settings={"llm_provider": "codex"})
    save_report_bundle({"market_report": "Market"}, "AAPL", tmp_path, html=False)
    assert not (tmp_path / "complete_report.html").exists()
    assert not (tmp_path / "run_settings.json").exists()


def test_html_keeps_repeated_section_anchors_unique():
    page = render_report_html("## News\nFirst\n\n## News\nSecond", title="Repeated")
    assert 'id="section-1"' in page
    assert 'id="section-2"' in page


def test_settings_cannot_close_markdown_code_fence(tmp_path):
    path = save_report_bundle({}, "AAPL", tmp_path, settings={"quick_think_llm": "```\n<script>evil</script>"})
    page = (tmp_path / "complete_report.html").read_text(encoding="utf-8")
    assert "script" not in _Page(page).tags
    assert "````json" in path.read_text(encoding="utf-8")
