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

Default KR watchdog times are `09:55`, `10:55`, `11:55`, `12:55`, `13:55`, `14:55`, and `15:25` KST on weekdays. The first six sit five minutes after the GitHub fallback cron probes, so native GitHub schedule events still have priority. The final watchdog runs five minutes after the 15:20 close checkpoint because a later post-close dispatch can fall back to the 14:35 artifact instead of producing a fresh 15:20 snapshot.

Dry-run the registration:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/register_intraday_overlay_watchdog.ps1 -WhatIf
```

Dry-run a dispatch:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/dispatch_intraday_overlay.ps1 -Profile kr -Force -DryRun
```

Logs are written to `C:\TradingAgentsData\automation-logs\intraday-overlay-dispatch.log` by default.

## Register US Watchdog Tasks

US watchdog tasks are registered in the runner's local Windows timezone. On the current KST runner, the following pair covers both US daylight-saving and standard-time XNYS checkpoints while keeping GitHub's native schedule as the primary path:

```powershell
.\tools\register_intraday_overlay_watchdog.ps1 -Profile us -Times "23:10" -Days "MON,TUE,WED,THU,FRI"
.\tools\register_intraday_overlay_watchdog.ps1 -Profile us -Times @("00:10","01:10","02:10","03:10","04:10","05:00","05:10","06:00") -Days "TUE,WED,THU,FRI,SAT"
```

These local times dispatch `profile=us` only. The workflow runner still applies the XNYS session gate and checkpoint selection, and the 20-minute recent-run window suppresses nearby duplicate dispatches when native GitHub schedule events are healthy.
