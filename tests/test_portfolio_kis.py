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

    def test_ensure_access_token_refreshes_when_expired(self):
        session = Mock()
        token_response = Mock()
        token_response.raise_for_status.return_value = None
        token_response.json.return_value = {"access_token": "fresh-token", "expires_in": 86400}
        session.post.return_value = token_response

        client = KisClient(
            app_key="app-key",
            app_secret="app-secret",
            session=session,
            token_file_cache_enabled=False,
            token_refresh_skew_seconds=0,
            token_ttl_seconds_default=1,
        )
        token_1 = client.ensure_access_token()
        token_2 = client.ensure_access_token()

        self.assertEqual(token_1, "fresh-token")
        self.assertEqual(token_2, "fresh-token")
        self.assertEqual(session.post.call_count, 1)

    def test_request_json_retries_after_401(self):
        session = Mock()

        first_token = Mock()
        first_token.raise_for_status.return_value = None
        first_token.json.return_value = {"access_token": "old-token", "expires_in": 86400}

        second_token = Mock()
        second_token.raise_for_status.return_value = None
        second_token.json.return_value = {"access_token": "new-token", "expires_in": 86400}
        session.post.side_effect = [first_token, second_token]

        unauthorized = Mock()
        unauthorized.status_code = 401
        unauthorized.raise_for_status.side_effect = RuntimeError("unauthorized")

        success = Mock()
        success.status_code = 200
        success.raise_for_status.return_value = None
        success.json.return_value = {"rt_cd": "0", "output": []}
        success.headers = {"tr_cont": ""}
        session.request.side_effect = [unauthorized, success]

        client = KisClient(
            app_key="app-key",
            app_secret="app-secret",
            session=session,
            token_file_cache_enabled=False,
        )

        payload, _headers = client.request_json(
            method="GET",
            path="/uapi/domestic-stock/v1/trading/inquire-balance",
            tr_id="TTTC8434R",
            params={},
        )

        self.assertEqual(payload["rt_cd"], "0")
        self.assertEqual(session.post.call_count, 2)
        self.assertEqual(session.request.call_count, 2)


if __name__ == "__main__":
    unittest.main()
