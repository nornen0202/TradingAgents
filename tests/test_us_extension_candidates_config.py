from tradingagents.scheduled.config import load_scheduled_config


def test_us_extension_candidates_are_in_daily_analysis_universe():
    config = load_scheduled_config("config/scheduled_analysis.toml")
    candidates = {
        "CRM": "Salesforce",
        "DELL": "Dell Technologies",
        "HPE": "Hewlett Packard Enterprise",
        "IBM": "International Business Machines",
        "NTAP": "NetApp",
        "OKTA": "Okta",
        "SMCI": "Super Micro Computer",
    }

    assert config.run.market == "US"
    assert candidates.keys() <= set(config.run.tickers)
    assert {ticker: config.run.ticker_name_overrides[ticker] for ticker in candidates} == candidates
