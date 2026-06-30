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
mode = "user_session"
channel = "stock_ai_agent"
lookback_minutes = 360
max_messages = 80
download_pdfs = true
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

To generate the user session string on a trusted local machine:

```powershell
python -m pip install -e ".[telegram]"
$env:TELEGRAM_API_ID = "<your api_id>"
$env:TELEGRAM_API_HASH = "<your api_hash>"
python -m tradingagents.prism_telegram.session
```

Telegram will ask for the account phone number, the login code, and the 2FA password when the account has one. Save the printed value as the `TELEGRAM_SESSION_STRING` GitHub Actions secret. As an alternative for a self-hosted runner, create a persistent session file:

```powershell
python -m tradingagents.prism_telegram.session --session-path C:\TradingAgentsData\telegram-stock-ai-agent
```

In that case, set the repository variable `TELEGRAM_SESSION_PATH` to the same path on the runner.

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

Use repository secrets for `TELEGRAM_BOT_TOKEN`, `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, and `TELEGRAM_SESSION_STRING`. The daily workflow defaults to `user_session` mode and PDF downloads, but can be overridden with repository variables `PRISM_TELEGRAM_MODE` and `PRISM_TELEGRAM_DOWNLOAD_PDFS` or by manual workflow inputs.
