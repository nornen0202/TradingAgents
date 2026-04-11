import unittest
from unittest.mock import Mock, patch

import requests

from tradingagents.portfolio.account_models import AccountConstraints, PortfolioProfile
from tradingagents.portfolio.kis import (
    KisClient,
    PortfolioConfigurationError,
    _extract_cash_snapshot,
    load_account_snapshot_from_kis,
    validate_kis_credentials,
)


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

    def test_extract_cash_snapshot_marks_watchlist_only_when_cash_is_below_min_trade(self):
        profile = PortfolioProfile(
            name="kis-test",
            enabled=True,
            broker="kis",
            broker_environment="real",
            read_only=True,
            account_no="12345678",
            product_code="01",
            manual_snapshot_path=None,
            csv_positions_path=None,
            private_output_dirname="portfolio-private",
            watch_tickers=tuple(),
            trigger_budget_krw=500000,
            constraints=AccountConstraints(min_cash_buffer_krw=2500000, min_trade_krw=100000),
        )

        snapshot = _extract_cash_snapshot(
            summary_payload={"dnca_tot_amt": "2", "tot_evlu_amt": "2"},
            positions_market_value=0,
            profile=profile,
        )

        self.assertEqual(snapshot["snapshot_health"], "WATCHLIST_ONLY")
        self.assertEqual(snapshot["available_cash_krw"], 2)
        self.assertEqual(snapshot["total_equity_krw"], 2)

    def test_extract_cash_snapshot_prefers_reported_total_equity_when_present(self):
        profile = PortfolioProfile(
            name="kis-test",
            enabled=True,
            broker="kis",
            broker_environment="real",
            read_only=True,
            account_no="12345678",
            product_code="01",
            manual_snapshot_path=None,
            csv_positions_path=None,
            private_output_dirname="portfolio-private",
            watch_tickers=tuple(),
            trigger_budget_krw=500000,
            constraints=AccountConstraints(min_cash_buffer_krw=0, min_trade_krw=100000),
        )

        snapshot = _extract_cash_snapshot(
            summary_payload={"dnca_tot_amt": "300000", "tot_evlu_amt": "5200000", "ord_psbl_amt": "300000"},
            positions_market_value=2000000,
            profile=profile,
        )

        self.assertEqual(snapshot["snapshot_health"], "VALID")
        self.assertEqual(snapshot["total_equity_krw"], 5200000)
        self.assertEqual(snapshot["cash_diagnostics"]["selected_fields"]["total_equity"], "tot_evlu_amt")

    @patch("tradingagents.portfolio.kis.KisClient.from_api_keys")
    def test_load_account_snapshot_continues_when_pending_orders_fail(self, mock_from_api_keys):
        response = Mock()
        response.status_code = 500
        response.reason = "Internal Server Error"
        pending_error = requests.HTTPError(
            "500 Server Error: Internal Server Error for url: "
            "https://openapi.koreainvestment.com:9443/uapi/domestic-stock/v1/trading/inquire-daily-ccld"
            "?CANO=12345678&ACNT_PRDT_CD=01"
        )
        pending_error.response = response

        client = Mock()
        client.fetch_balance.return_value = (
            [],
            {"dnca_tot_amt": "300000", "ord_psbl_amt": "300000", "tot_evlu_amt": "300000"},
        )
        client.fetch_pending_orders.side_effect = pending_error
        mock_from_api_keys.return_value = client

        profile = PortfolioProfile(
            name="kis-test",
            enabled=True,
            broker="kis",
            broker_environment="real",
            read_only=True,
            account_no="12345678",
            product_code="01",
            manual_snapshot_path=None,
            csv_positions_path=None,
            private_output_dirname="portfolio-private",
            watch_tickers=tuple(),
            trigger_budget_krw=500000,
            constraints=AccountConstraints(min_cash_buffer_krw=0, min_trade_krw=100000),
        )

        snapshot = load_account_snapshot_from_kis(profile)

        self.assertEqual(snapshot.snapshot_health, "VALID")
        self.assertEqual(snapshot.pending_orders, tuple())
        self.assertTrue(any("pending-order lookup failed" in warning for warning in snapshot.warnings))
        self.assertFalse(any("12345678" in warning for warning in snapshot.warnings))


if __name__ == "__main__":
    unittest.main()
