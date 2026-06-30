# PRISM Telegram Integration

TradingAgents can collect `@stock_ai_agent` Telegram messages as a secondary PRISM evidence source while keeping PRISM dashboard JSON as the primary source.

## Source Priority

1. PRISM dashboard JSON / SQLite remains primary.
2. Telegram messages can add new ticker-level advisory signals.
3. If dashboard and Telegram signals match the same ticker/action/trigger, the dashboard signal wins and Telegram is attached as evidence.
4. Cross-market filtering remains unchanged: US runs use US ticker-level signals; KR runs use KR ticker-level signals.

Telegram signals never bypass TradingAgents risk gates, account constraints, or execution approval.

## Modes

```toml
[external.prism.telegram]
enabled = true
mode = "public_preview"
channel = "stock_ai_agent"
lookback_minutes = 360
max_messages = 80
download_pdfs = false
```

Supported modes:

- `public_preview`: Reads public `https://t.me/s/stock_ai_agent` HTML. No login is required. Text, message metadata, image URLs, and document filenames are available. PDF body download is not reliable in this mode.
- `bot_api`: Uses `TELEGRAM_BOT_TOKEN` and Telegram Bot API `getUpdates`. This can download files only for updates the bot receives. It generally requires the bot to be present in the channel and does not provide arbitrary historical channel backfill.
- `user_session`: Uses MTProto through Telethon. This is the recommended authenticated mode when your logged-in Telegram account can see the channel and download PDFs in Telegram Web/Desktop.

## Authenticated User Session Setup

You need three values for MTProto/Telethon:

1. `TELEGRAM_API_ID`
2. `TELEGRAM_API_HASH`
3. either `TELEGRAM_SESSION_STRING` or a local `TELEGRAM_SESSION_PATH`

Create `api_id` and `api_hash` at Telegram's API application page, then create a Telethon session locally. Do not commit the session file or string.

Typical environment:

```text
PRISM_TELEGRAM_MODE=user_session
PRISM_TELEGRAM_DOWNLOAD_PDFS=true
TELEGRAM_API_ID=...
TELEGRAM_API_HASH=...
TELEGRAM_SESSION_STRING=...
PRISM_TELEGRAM_PRIVATE_ARCHIVE_DIR=C:/TradingAgentsData/prism-telegram-private
```

The private archive can contain raw PDFs and local paths. The public site only publishes message metadata, ticker-level signals, and short PDF text summaries.

## Bot Token Notes

A bot token alone is not the same as a user session. It can help only if the bot receives channel updates. Configure it as a secret or local environment variable:

```text
PRISM_TELEGRAM_MODE=bot_api
TELEGRAM_BOT_TOKEN=...
PRISM_TELEGRAM_DOWNLOAD_PDFS=true
```

If the bot is not connected to the channel or has no pending updates, TradingAgents falls back to public preview when `fallback_to_public_preview = true`.

If a bot token was pasted into a chat, rotate it with BotFather before production use.

## Standalone Report

Run:

```powershell
python -m tradingagents.prism_telegram --config config/prism_telegram_daily.toml
```

Output:

```text
.runtime/prism-telegram-archive/runs/YYYY/prism_telegram_*/prism_telegram_run.json
site/prism-telegram/index.html
site/prism-telegram/feed.json
```

GitHub Actions workflow:

```text
.github/workflows/daily-prism-telegram-reports.yml
```

Use repository secrets for `TELEGRAM_BOT_TOKEN`, `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, and `TELEGRAM_SESSION_STRING`.
