# Intraday Overlay Dispatch Watchdog

GitHub scheduled workflow events can be delayed or dropped before any runner job starts. The primary scheduler remains `.github/workflows/intraday-overlay-refresh.yml`, but a self-hosted Windows runner can register a local watchdog that dispatches the same workflow when GitHub has not created a recent run.

The watchdog does not run analysis locally. It calls:

```powershell
gh workflow run intraday-overlay-refresh.yml --repo nornen0202/TradingAgents --ref main -f profile=kr -f run_mode=overlay_only
```

Before dispatching, `tools/dispatch_intraday_overlay.ps1` checks recent runs for the same workflow. If a scheduled or manual run already exists inside the recent-run window, it logs a skip and exits. The default window is 20 minutes so the watchdog avoids duplicate native GitHub primary/fallback runs without blocking the next hourly checkpoint.

## Register KR Watchdog Tasks

Run from the repository root on the self-hosted Windows runner:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/register_intraday_overlay_watchdog.ps1
```

Default KR watchdog times are `09:55`, `10:55`, `11:55`, `12:55`, `13:55`, `14:55`, and `15:40` KST on weekdays. These sit five minutes after the GitHub fallback cron probes, so native GitHub schedule events still have priority.

Dry-run the registration:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/register_intraday_overlay_watchdog.ps1 -WhatIf
```

Dry-run a dispatch:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/dispatch_intraday_overlay.ps1 -Profile kr -Force -DryRun
```

Logs are written to `C:\TradingAgentsData\automation-logs\intraday-overlay-dispatch.log` by default.
