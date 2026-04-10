import unittest
from unittest.mock import Mock, patch

from tradingagents.portfolio.kis import KisClient, PortfolioConfigurationError, validate_kis_credentials


class PortfolioKisTests(unittest.TestCase):
    @patch("tradingagents.portfolio.kis.get_api_key")
    @patch("tradingagents.portfolio.kis.requests.Session.post")
    def test_validate_kis_credentials_issues_access_token(self, mock_post, mock_get_api_key):
        mock_get_api_key.side_effect = lambda name: {
            "KIS_APP_KEY": "app-key",
            "KIS_APP_SECRET": "app-secret",
        }.get(name)
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"access_token": "token-value"}
        mock_post.return_value = response

        result = validate_kis_credentials(require_account=False)

        self.assertTrue(result["token_issued"])
        self.assertEqual(result["environment"], "real")

    @patch("tradingagents.portfolio.kis.get_api_key", return_value=None)
    def test_from_api_keys_requires_credentials(self, _mock_key):
        with self.assertRaises(PortfolioConfigurationError):
            KisClient.from_api_keys()


if __name__ == "__main__":
    unittest.main()
