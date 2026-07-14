from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from types import ModuleType
from unittest.mock import patch

from tradingagents.external.prism_loader import PrismLoaderConfig, load_prism_signals
from tradingagents.external.prism_models import PrismExternalSignal, PrismIngestionResult, PrismSignalAction, PrismSourceKind
from tradingagents.external.prism_telegram_common import (
    PrismTelegramCollection,
    PrismTelegramDocument,
    PrismTelegramMessage,
    PrismTelegramRuntimeConfig,
    message_to_signals,
)
from tradingagents.external.prism_telegram_preview import parse_public_preview_html
from tradingagents.prism_telegram.config import PrismTelegramDailyConfig, PrismTelegramSiteSettings, PrismTelegramSourceSettings, PrismTelegramStorageSettings
from tradingagents.prism_telegram.runner import execute_prism_telegram_run


def test_public_preview_parser_extracts_text_document_and_time():
    html = """
    <div class="tgme_widget_message_wrap"><div class="tgme_widget_message js-widget_message" data-post="stock_ai_agent/12050">
      <div class="tgme_widget_message_text js-message_text" dir="auto">📊 <b>Advanced Micro Devices, Inc.</b> (AMD) O&#39;Neil 인사이트<br/>차트 참고</div>
      <a class="tgme_widget_message_document_wrap" href="https://t.me/stock_ai_agent/12049">
        <div class="tgme_widget_message_document_title accent_color" dir="auto">AMD_Advanced_Micro_Devices_20260701.pdf</div>
        <div class="tgme_widget_message_document_extra" dir="auto">800.9 KB</div>
      </a>
      <a class="tgme_widget_message_date" href="https://t.me/stock_ai_agent/12050"><time datetime="2026-06-30T19:31:45+00:00">19:31</time></a>
    </div></div>
    """

    messages = parse_public_preview_html(html, channel="stock_ai_agent")

    assert len(messages) == 1
    assert messages[0].message_id == "12050"
    assert "Advanced Micro Devices" in messages[0].text
    assert messages[0].posted_at == datetime(2026, 6, 30, 19, 31, 45, tzinfo=timezone.utc)
    assert messages[0].documents[0].filename == "AMD_Advanced_Micro_Devices_20260701.pdf"


def test_telegram_message_to_signals_maps_skip_alert_and_stop_loss():
    skip_message = PrismTelegramMessage(
        message_id="1",
        text="""⚠️ 매수 보류: Sandisk Corporation(SNDK)
현재가: $2,203.95
매수 Score: 8/10
결정: Skip
📡 Trigger Win Rate: 46% (332 trades)""",
        posted_at=datetime(2026, 7, 1, tzinfo=timezone.utc),
    )
    stop_message = PrismTelegramMessage(
        message_id="2",
        text="""⚠️ Portfolio Adjustment: Take-Two Interactive Software, (TTWO)
Stop Loss: $232.71 (upward)
Reason: trailing stop activated""",
        posted_at=datetime(2026, 7, 1, tzinfo=timezone.utc),
    )

    skip_signal = message_to_signals(skip_message, default_market="US")[0]
    stop_signal = message_to_signals(stop_message, default_market="US")[0]

    assert skip_signal.canonical_ticker == "SNDK"
    assert skip_signal.signal_action == PrismSignalAction.NO_ENTRY
    assert skip_signal.current_price == 2203.95
    assert skip_signal.confidence == 0.8
    assert skip_signal.win_rate_30d_by_trigger == 0.46
    assert stop_signal.canonical_ticker == "TTWO"
    assert stop_signal.signal_action == PrismSignalAction.STOP_LOSS
    assert stop_signal.stop_loss_price == 232.71


def test_multi_ticker_message_scopes_prices_and_scores_to_each_ticker_block():
    message = PrismTelegramMessage(
        message_id="multi",
        text="""Holdings
Alpha Corp (AAA)
Current: $10.00
Target: $12.00
Stop: $9.00
Score: 8/10
Beta Corp (BBB)
Current: $20.00
Target: $24.00
Stop: $18.00
Score: 6/10""",
        posted_at=datetime(2026, 7, 14, tzinfo=timezone.utc),
    )

    by_ticker = {item.canonical_ticker: item for item in message_to_signals(message, default_market="US")}

    assert by_ticker["AAA"].current_price == 10.0
    assert by_ticker["AAA"].target_price == 12.0
    assert by_ticker["AAA"].stop_loss_price == 9.0
    assert by_ticker["AAA"].confidence == 0.8
    assert by_ticker["BBB"].current_price == 20.0
    assert by_ticker["BBB"].target_price == 24.0
    assert by_ticker["BBB"].stop_loss_price == 18.0
    assert by_ticker["BBB"].confidence == 0.6


def test_document_filename_yields_watch_signal_without_publishing_private_path():
    message = PrismTelegramMessage(
        message_id="3",
        text="",
        documents=(
            PrismTelegramDocument(
                filename="ASML_ASML_Holding_N_V_New_York_Re_20260701_afternoon.pdf",
                local_path="C:/secret/private.pdf",
                text_summary={"status": "ok", "excerpt": "ASML Holding N.V. - New York Re (ASML) report"},
            ),
        ),
    )

    signal = message_to_signals(message, default_market="US")[0]
    public = message.to_dict(include_private_paths=False)

    assert signal.canonical_ticker == "ASML"
    assert signal.signal_action == PrismSignalAction.WATCH
    assert public["documents"][0].get("local_path") is None


def test_user_session_skips_non_pdf_media_without_filename():
    from tradingagents.external.prism_telegram_user import _documents_for_message

    class FakeFile:
        name = None
        title = None
        mime_type = "image/jpeg"
        size = 1234

    class FakeMessage:
        id = 12110
        file = FakeFile()

    class FakeClient:
        async def download_media(self, *_args, **_kwargs):
            raise AssertionError("non-PDF media should not be downloaded")

    docs = asyncio.run(
        _documents_for_message(
            FakeClient(),
            FakeMessage(),
            PrismTelegramRuntimeConfig(download_pdfs=True),
            channel="stock_ai_agent",
        )
    )

    assert len(docs) == 1
    assert docs[0].mime_type == "image/jpeg"
    assert docs[0].local_path is None
    assert docs[0].text_summary is None


def test_prism_loader_keeps_dashboard_primary_and_merges_telegram_evidence():
    primary = PrismIngestionResult(
        enabled=True,
        ok=True,
        source_kind=PrismSourceKind.DASHBOARD_LIVE,
        source="https://example.test/us_dashboard_data.json",
        signals=[
            PrismExternalSignal(
                canonical_ticker="AMD",
                market="US",
                source_kind=PrismSourceKind.DASHBOARD_LIVE,
                signal_action=PrismSignalAction.WATCH,
                trigger_type="telegram_oneil_insight",
                rationale="dashboard rationale",
            )
        ],
    )
    telegram = PrismIngestionResult(
        enabled=True,
        ok=True,
        source_kind=PrismSourceKind.TELEGRAM_PUBLIC_PREVIEW,
        source="https://t.me/s/stock_ai_agent",
        signals=[
            PrismExternalSignal(
                canonical_ticker="AMD",
                market="US",
                source_kind=PrismSourceKind.TELEGRAM_PUBLIC_PREVIEW,
                signal_action=PrismSignalAction.WATCH,
                trigger_type="telegram_oneil_insight",
                rationale="telegram rationale",
            ),
            PrismExternalSignal(
                canonical_ticker="SNDK",
                market="US",
                source_kind=PrismSourceKind.TELEGRAM_PUBLIC_PREVIEW,
                signal_action=PrismSignalAction.NO_ENTRY,
                trigger_type="telegram_buy_skip",
            ),
        ],
    )

    with (
        patch("tradingagents.external.prism_loader._load_primary_prism_signals", return_value=primary),
        patch("tradingagents.external.prism_loader.load_telegram_prism_signals", return_value=telegram),
    ):
        result = load_prism_signals(
            PrismLoaderConfig(
                enabled=True,
                use_live_http=True,
                market="US",
                telegram=PrismTelegramRuntimeConfig(enabled=True),
            )
        )

    tickers = [signal.canonical_ticker for signal in result.signals]
    amd = result.signals[tickers.index("AMD")]
    assert result.source_kind == PrismSourceKind.MIXED
    assert tickers == ["AMD", "SNDK"]
    assert "telegram_evidence" in amd.raw
    assert "telegram rationale" in (amd.rationale or "")


def test_prism_telegram_runner_writes_public_site_without_private_pdf_path(tmp_path):
    archive_dir = tmp_path / "archive"
    site_dir = tmp_path / "site"
    private_pdf = tmp_path / "private" / "AMD.pdf"
    config = PrismTelegramDailyConfig(
        source=PrismTelegramSourceSettings(enabled=True, mode="public_preview", channel="stock_ai_agent"),
        storage=PrismTelegramStorageSettings(archive_dir=archive_dir, site_dir=site_dir),
        site=PrismTelegramSiteSettings(title="PRISM Telegram 리포트", max_runs=10, max_messages_on_index=10),
    )
    collection = PrismTelegramCollection(
        enabled=True,
        ok=True,
        source_kind=PrismSourceKind.TELEGRAM_PUBLIC_PREVIEW,
        source="https://t.me/s/stock_ai_agent",
        messages=(
            PrismTelegramMessage(
                message_id="12051",
                url="https://t.me/stock_ai_agent/12051",
                posted_at=datetime(2026, 7, 1, tzinfo=timezone.utc),
                text="📊 Advanced Micro Devices, Inc. (AMD) O'Neil 인사이트",
                documents=(
                    PrismTelegramDocument(
                        filename="AMD_report.pdf",
                        local_path=private_pdf.as_posix(),
                        text_summary={"status": "ok", "excerpt": "AMD summary"},
                    ),
                ),
            ),
        ),
    )

    manifest = execute_prism_telegram_run(config, collection_fetcher=lambda _config: collection)

    assert manifest["summary"]["messages"] == 1
    assert manifest["summary"]["signals"] == 1
    assert (site_dir / "prism-telegram" / "index.html").is_file()
    public_text = "\n".join(path.read_text(encoding="utf-8") for path in (site_dir / "prism-telegram").rglob("*") if path.is_file())
    assert "AMD summary" in public_text
    assert private_pdf.as_posix() not in public_text
    feed = json.loads((site_dir / "prism-telegram" / "feed.json").read_text(encoding="utf-8"))
    assert feed["items"][0]["message_id"] == "12051"


def test_bot_api_missing_token_falls_back_to_public_preview():
    from tradingagents.external.prism_telegram import load_telegram_prism_signals

    preview = PrismIngestionResult(
        enabled=True,
        ok=True,
        source_kind=PrismSourceKind.TELEGRAM_PUBLIC_PREVIEW,
        source="https://t.me/s/stock_ai_agent",
        signals=[PrismExternalSignal(canonical_ticker="AMD", market="US", signal_action=PrismSignalAction.WATCH)],
    )
    with patch("tradingagents.external.prism_telegram.load_telegram_public_preview", return_value=preview):
        result = load_telegram_prism_signals(
            PrismTelegramRuntimeConfig(enabled=True, mode="bot_api", bot_token=None),
            default_market="US",
        )

    assert result.ok is True
    assert result.signals[0].canonical_ticker == "AMD"
    assert any("telegram_bot_token_missing" in warning for warning in result.warnings)


def test_session_cli_uses_telethon_default_phone_prompt_when_phone_omitted(monkeypatch, capsys):
    from tradingagents.prism_telegram import session as session_cli

    calls: list[dict[str, object]] = []

    class FakeStringSession:
        def save(self) -> str:
            return "SESSION_STRING"

    class FakeTelegramClient:
        def __init__(self, session, api_id, api_hash):
            self.session = session
            self.api_id = api_id
            self.api_hash = api_hash

        def start(self, **kwargs):
            calls.append(kwargs)

        def disconnect(self):
            calls.append({"disconnect": True})

    telethon_module = ModuleType("telethon")
    telethon_sessions_module = ModuleType("telethon.sessions")
    telethon_module.TelegramClient = FakeTelegramClient
    telethon_sessions_module.StringSession = FakeStringSession
    monkeypatch.setitem(sys.modules, "telethon", telethon_module)
    monkeypatch.setitem(sys.modules, "telethon.sessions", telethon_sessions_module)

    result = session_cli.main(["--api-id", "123", "--api-hash", "hash", "--quiet"])

    assert result == 0
    assert calls[0].get("phone") is None
    assert "phone" not in calls[0]
    assert "SESSION_STRING" in capsys.readouterr().out
