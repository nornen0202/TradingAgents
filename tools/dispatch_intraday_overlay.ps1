param(
    [ValidateSet("kr", "us", "all")]
    [string] $Profile = "kr",
    [ValidateSet("overlay_only", "selective_rerun_only")]
    [string] $RunMode = "overlay_only",
    [string] $Repo = "nornen0202/TradingAgents",
    [string] $Workflow = "intraday-overlay-refresh.yml",
    [string] $Ref = "main",
    [string] $GhPath = "",
    [int] $RecentRunWindowMinutes = 20,
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

function Resolve-GhPath {
    if ($GhPath) {
        if (Test-Path -LiteralPath $GhPath) {
            return (Resolve-Path -LiteralPath $GhPath).Path
        }
        throw "Configured GhPath does not exist: $GhPath"
    }
    $command = Get-Command gh -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }
    foreach ($candidate in @(
        "C:\Program Files\GitHub CLI\gh.exe",
        "C:\Program Files (x86)\GitHub CLI\gh.exe"
    )) {
        if (Test-Path -LiteralPath $candidate) {
            return $candidate
        }
    }
    throw "GitHub CLI gh.exe was not found in PATH or common install locations."
}

function Convert-ToUtcDateTime {
    param([object] $Value)
    if ($Value -is [DateTime]) {
        return $Value.ToUniversalTime()
    }
    if ($Value -is [DateTimeOffset]) {
        return $Value.UtcDateTime
    }
    $text = [string] $Value
    if (-not $text) {
        return $null
    }
    $styles = [System.Globalization.DateTimeStyles]::AssumeUniversal -bor [System.Globalization.DateTimeStyles]::AdjustToUniversal
    $parsed = [DateTimeOffset]::MinValue
    if ([DateTimeOffset]::TryParse($text, [System.Globalization.CultureInfo]::InvariantCulture, $styles, [ref] $parsed)) {
        return $parsed.UtcDateTime
    }
    return $null
}

Write-DispatchLog "start profile=$Profile run_mode=$RunMode repo=$Repo workflow=$Workflow ref=$Ref"
$gh = Resolve-GhPath
Write-DispatchLog "using gh: $gh"
$nowUtc = [DateTimeOffset]::UtcNow

if (-not $Force) {
    $runsJson = & $gh run list `
        --repo $Repo `
        --workflow $Workflow `
        --limit 12 `
        --json databaseId,event,status,conclusion,createdAt,url 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-DispatchLog "recent-run probe failed; attempting dispatch anyway: $runsJson"
    } else {
        $cutoffUtc = $nowUtc.AddMinutes(-1 * [Math]::Max($RecentRunWindowMinutes, 1))
        $recentRuns = @($runsJson | ConvertFrom-Json | Where-Object {
            $createdUtc = Convert-ToUtcDateTime $_.createdAt
            ($_.event -eq "schedule" -or $_.event -eq "workflow_dispatch") -and
            $createdUtc -ne $null -and
            $createdUtc -ge $cutoffUtc.UtcDateTime
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
$dispatchOutput = & $gh @dispatchArgs 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-DispatchLog "dispatch failed: $dispatchOutput"
    exit $LASTEXITCODE
}
Write-DispatchLog "dispatch accepted: $dispatchOutput"
