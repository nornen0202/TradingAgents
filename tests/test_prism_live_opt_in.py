import os
import unittest

from tradingagents.external.prism_loader import PrismLoaderConfig, load_prism_signals


@unittest.skipUnless(os.getenv("RUN_LIVE_PRISM_TESTS") == "1", "live PRISM dashboard tests are opt-in")
def test_live_prism_dashboard_opt_in_smoke():
    result = load_prism_signals(
        PrismLoaderConfig(
            enabled=True,
            use_live_http=True,
            use_html_scraping=os.getenv("PRISM_USE_HTML_SCRAPING", "").lower() in {"1", "true", "yes", "on"},
            dashboard_json_url=os.getenv("PRISM_DASHBOARD_JSON_URL") or None,
            dashboard_base_url=os.getenv("PRISM_DASHBOARD_BASE_URL") or "https://analysis.stocksimulation.kr",
            timeout_seconds=float(os.getenv("PRISM_TIMEOUT_SECONDS") or 5),
        )
    )

    assert result.enabled is True
    assert isinstance(result.warnings, list)
