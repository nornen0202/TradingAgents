import unittest

from tradingagents.dataflows.yfinance_news import _extract_article_fields


class YfinanceNewsParsingTests(unittest.TestCase):
    def test_extract_article_fields_handles_none_provider(self):
        payload = {
            "content": {
                "provider": None,
                "canonicalUrl": None,
                "clickThroughUrl": None,
                "title": "title",
                "summary": "summary",
                "pubDate": "2026-04-08T00:00:00Z",
            }
        }
        fields = _extract_article_fields(payload)
        self.assertEqual(fields["publisher"], "Unknown")


if __name__ == "__main__":
    unittest.main()
