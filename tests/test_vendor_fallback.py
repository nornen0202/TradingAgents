import unittest
import os
from unittest.mock import patch

from tradingagents.dataflows.alpha_vantage_common import AlphaVantageRateLimitError
from tradingagents.dataflows.interface import route_to_vendor
from tradingagents.dataflows.vendor_exceptions import VendorConfigurationError, VendorInputError, VendorMalformedResponseError


class VendorFallbackTests(unittest.TestCase):
    def test_rate_limit_falls_back_to_next_vendor(self):
        with patch("tradingagents.dataflows.interface.get_vendor", return_value="alpha_vantage,yfinance"), patch.dict(
            "tradingagents.dataflows.interface.VENDOR_METHODS",
            {
                "get_company_news": {
                    "alpha_vantage": lambda *_args, **_kwargs: (_ for _ in ()).throw(AlphaVantageRateLimitError("rate")),
                    "yfinance": lambda *_args, **_kwargs: "yfinance result",
                }
            },
            clear=False,
        ):
            result = route_to_vendor("get_company_news", "AAPL", "2026-04-01", "2026-04-02")

        self.assertEqual(result, "yfinance result")

    def test_generic_exception_falls_back_to_next_vendor(self):
        with patch("tradingagents.dataflows.interface.get_vendor", return_value="alpha_vantage,yfinance"), patch.dict(
            "tradingagents.dataflows.interface.VENDOR_METHODS",
            {
                "get_company_news": {
                    "alpha_vantage": lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("boom")),
                    "yfinance": lambda *_args, **_kwargs: "fallback result",
                }
            },
            clear=False,
        ):
            result = route_to_vendor("get_company_news", "AAPL", "2026-04-01", "2026-04-02")

        self.assertEqual(result, "fallback result")

    def test_empty_result_falls_back_to_next_vendor(self):
        with patch("tradingagents.dataflows.interface.get_vendor", return_value="alpha_vantage,yfinance"), patch.dict(
            "tradingagents.dataflows.interface.VENDOR_METHODS",
            {
                "get_company_news": {
                    "alpha_vantage": lambda *_args, **_kwargs: "No news found for AAPL",
                    "yfinance": lambda *_args, **_kwargs: "usable result",
                }
            },
            clear=False,
        ):
            result = route_to_vendor("get_company_news", "AAPL", "2026-04-01", "2026-04-02")

        self.assertEqual(result, "usable result")

    def test_malformed_payload_falls_back_to_next_vendor(self):
        with patch("tradingagents.dataflows.interface.get_vendor", return_value="alpha_vantage,yfinance"), patch.dict(
            "tradingagents.dataflows.interface.VENDOR_METHODS",
            {
                "get_company_news": {
                    "alpha_vantage": lambda *_args, **_kwargs: (_ for _ in ()).throw(VendorMalformedResponseError("bad payload")),
                    "yfinance": lambda *_args, **_kwargs: "usable result",
                }
            },
            clear=False,
        ):
            result = route_to_vendor("get_company_news", "AAPL", "2026-04-01", "2026-04-02")

        self.assertEqual(result, "usable result")

    def test_invalid_user_input_raises_without_fallback(self):
        with self.assertRaises(VendorInputError):
            route_to_vendor("get_company_news", "AAPL", "2026/04/01", "2026-04-02")

    def test_disclosures_degrade_gracefully_when_provider_missing(self):
        with patch("tradingagents.dataflows.interface.get_vendor", return_value="opendart"), patch.dict(
            "tradingagents.dataflows.interface.VENDOR_METHODS",
            {
                "get_disclosures": {
                    "opendart": lambda *_args, **_kwargs: (_ for _ in ()).throw(VendorConfigurationError("missing opendart key")),
                }
            },
            clear=False,
        ):
            result = route_to_vendor("get_disclosures", "000660", "2026-04-01", "2026-04-02")

        self.assertIn("No disclosures found", result)
        self.assertIn("provider unavailable", result)

    def test_social_sentiment_returns_unavailable_when_all_vendors_fail(self):
        with patch("tradingagents.dataflows.interface.get_vendor", return_value="naver,yfinance"), patch.dict(
            "tradingagents.dataflows.interface.VENDOR_METHODS",
            {
                "get_social_sentiment": {
                    "naver": lambda *_args, **_kwargs: (_ for _ in ()).throw(VendorConfigurationError("missing naver key")),
                    "yfinance": lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("yfinance outage")),
                }
            },
            clear=False,
        ):
            result = route_to_vendor("get_social_sentiment", "000660", "2026-04-01", "2026-04-02")

        self.assertIn("No social sentiment data found", result)
        self.assertIn("provider unavailable", result)

    def test_social_sentiment_degrades_gracefully_when_primary_provider_missing(self):
        with patch("tradingagents.dataflows.interface.get_vendor", return_value="naver,yfinance"), patch.dict(
            "tradingagents.dataflows.interface.VENDOR_METHODS",
            {
                "get_social_sentiment": {
                    "naver": lambda *_args, **_kwargs: (_ for _ in ()).throw(VendorConfigurationError("missing naver key")),
                    "yfinance": lambda *_args, **_kwargs: "Dedicated social provider unavailable; using news-derived sentiment for AAPL.",
                }
            },
            clear=False,
        ):
            result = route_to_vendor("get_social_sentiment", "AAPL", "2026-04-01", "2026-04-02")

        self.assertIn("Dedicated social provider unavailable", result)
        self.assertIn("news-derived sentiment", result)

    def test_social_sentiment_fallback_emits_github_actions_warning_log(self):
        with patch("tradingagents.dataflows.interface.get_vendor", return_value="naver,yfinance"), patch.dict(
            "tradingagents.dataflows.interface.VENDOR_METHODS",
            {
                "get_social_sentiment": {
                    "naver": lambda *_args, **_kwargs: (_ for _ in ()).throw(VendorConfigurationError("missing naver key")),
                    "yfinance": lambda *_args, **_kwargs: "ok",
                }
            },
            clear=False,
        ), patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}, clear=False), patch("builtins.print") as mocked_print:
            route_to_vendor("get_social_sentiment", "000660", "2026-04-01", "2026-04-02")

        mocked_print.assert_any_call(
            "::warning::Vendor fallback for get_social_sentiment: naver: missing naver key"
        )

    def test_empty_vendor_results_emit_notice_instead_of_warning(self):
        with patch("tradingagents.dataflows.interface.get_vendor", return_value="yfinance"), patch.dict(
            "tradingagents.dataflows.interface.VENDOR_METHODS",
            {
                "get_social_sentiment": {
                    "yfinance": lambda *_args, **_kwargs: "No social sentiment data found for AAPL.",
                }
            },
            clear=False,
        ), patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}, clear=False), patch("builtins.print") as mocked_print:
            route_to_vendor("get_social_sentiment", "AAPL", "2026-04-01", "2026-04-02")

        calls = [call.args[0] for call in mocked_print.call_args_list]
        self.assertTrue(any(str(item).startswith("::notice::Vendor fallback") for item in calls))
        self.assertFalse(any(str(item).startswith("::warning::Vendor fallback") for item in calls))

    def test_us_symbols_skip_kr_only_vendor_fallbacks(self):
        with patch("tradingagents.dataflows.interface.get_vendor", return_value="yfinance,naver"), patch.dict(
            "tradingagents.dataflows.interface.VENDOR_METHODS",
            {
                "get_social_sentiment": {
                    "yfinance": lambda *_args, **_kwargs: "No social sentiment data found for AAPL.",
                    "naver": lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("naver should be skipped for US symbols")),
                }
            },
            clear=False,
        ):
            result = route_to_vendor("get_social_sentiment", "AAPL", "2026-04-01", "2026-04-02")

        self.assertIn("No social sentiment", result)

    def test_us_symbols_skip_opendart_disclosure_fallback(self):
        with patch("tradingagents.dataflows.interface.get_vendor", return_value="opendart"), patch.dict(
            "tradingagents.dataflows.interface.VENDOR_METHODS",
            {
                "get_disclosures": {
                    "opendart": lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("opendart should be skipped for US symbols")),
                }
            },
            clear=False,
        ):
            result = route_to_vendor("get_disclosures", "AAPL", "2026-04-01", "2026-04-02")

        self.assertIn("No disclosures found", result)


if __name__ == "__main__":
    unittest.main()
