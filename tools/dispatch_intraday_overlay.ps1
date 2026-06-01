param(
    [ValidateSet("kr", "us", "all")]
    [string] $Profile = "kr",
    [ValidateSet("overlay_only", "selective_rerun_only")]
    [string] $RunMode = "overlay_only",
    [string] $Repo = "nornen0202/TradingAgents",
    [string] $Workflow = "intraday-overlay-refresh.yml",
    [string] $Ref = "main",
    [int] $RecentRunWindowMinutes = 40,
    [string] $LogPath = "C:\TradingAgentsData\automation-logs\intraday-overlay-dispatch.log",
    [switch] $Force,
    [switch] $DryRun
)

$ErrorActionPreference = "Stop"

function Write-DispatchLog {
    param([string] $Message)
    $timestamp = [DateTimeOffset]::Now.ToString("o")
    $line = "[$timestamp] $Message"
    Write-Output $line
    if ($LogPath) {
        $parent = Split-Path -Parent $LogPath
        if ($parent -and -not (Test-Path -LiteralPath $parent)) {
            New-Item -ItemType Directory -Path $parent -Force | Out-Null
        }
        Add-Content -Path $LogPath -Value $line -Encoding UTF8
    }
}

$gh = Get-Command gh -ErrorAction Stop
$nowUtc = [DateTimeOffset]::UtcNow

if (-not $Force) {
    $runsJson = & $gh.Source run list `
        --repo $Repo `
        --workflow $Workflow `
        --limit 12 `
        --json databaseId,event,status,conclusion,createdAt,url 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-DispatchLog "recent-run probe failed; attempting dispatch anyway: $runsJson"
    } else {
        $cutoffUtc = $nowUtc.AddMinutes(-1 * [Math]::Max($RecentRunWindowMinutes, 1))
        $recentRuns = @($runsJson | ConvertFrom-Json | Where-Object {
            ($_.event -eq "schedule" -or $_.event -eq "workflow_dispatch") -and
            ([DateTimeOffset]::Parse([string] $_.createdAt).UtcDateTime -ge $cutoffUtc.UtcDateTime)
        })
        if ($recentRuns.Count -gt 0) {
            $latest = $recentRuns | Select-Object -First 1
            Write-DispatchLog "skip dispatch: recent $Workflow run exists id=$($latest.databaseId) event=$($latest.event) status=$($latest.status) url=$($latest.url)"
            exit 0
        }
    }
}

$dispatchArgs = @(
    "workflow",
    "run",
    $Workflow,
    "--repo",
    $Repo,
    "--ref",
    $Ref,
    "-f",
    "profile=$Profile",
    "-f",
    "run_mode=$RunMode"
)

if ($DryRun) {
    Write-DispatchLog "dry-run dispatch: gh $($dispatchArgs -join ' ')"
    exit 0
}

Write-DispatchLog "dispatching: gh $($dispatchArgs -join ' ')"
$dispatchOutput = & $gh.Source @dispatchArgs 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-DispatchLog "dispatch failed: $dispatchOutput"
    exit $LASTEXITCODE
}
Write-DispatchLog "dispatch accepted: $dispatchOutput"
