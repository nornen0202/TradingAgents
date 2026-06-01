[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [ValidateSet("kr", "us")]
    [string] $Profile = "kr",
    [string[]] $Times = @("09:55", "10:55", "11:55", "12:55", "13:55", "14:55", "15:40"),
    [string] $TaskFolder = "\TradingAgents",
    [string] $Repo = "nornen0202/TradingAgents",
    [string] $Workflow = "intraday-overlay-refresh.yml",
    [string] $Ref = "main",
    [int] $RecentRunWindowMinutes = 20
)

$ErrorActionPreference = "Stop"

$dispatchScript = Join-Path $PSScriptRoot "dispatch_intraday_overlay.ps1"
if (-not (Test-Path -LiteralPath $dispatchScript)) {
    throw "Missing dispatch script: $dispatchScript"
}

$profileUpper = $Profile.ToUpperInvariant()
$folder = $TaskFolder.TrimEnd("\")
if (-not $folder.StartsWith("\")) {
    $folder = "\" + $folder
}

foreach ($timeText in $Times) {
    if ($timeText -notmatch "^\d{2}:\d{2}$") {
        throw "Invalid time '$timeText'. Use HH:mm."
    }
    $safeTime = $timeText.Replace(":", "")
    $taskName = "$folder\IntradayOverlay-$profileUpper-$safeTime"
    $taskCommand = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$dispatchScript`" -Profile $Profile -Repo `"$Repo`" -Workflow `"$Workflow`" -Ref `"$Ref`" -RecentRunWindowMinutes $RecentRunWindowMinutes"
    $args = @(
        "/Create",
        "/F",
        "/SC",
        "WEEKLY",
        "/D",
        "MON,TUE,WED,THU,FRI",
        "/ST",
        $timeText,
        "/TN",
        $taskName,
        "/TR",
        $taskCommand
    )
    if ($PSCmdlet.ShouldProcess($taskName, "create weekly dispatch watchdog at $timeText")) {
        & schtasks.exe @args
        if ($LASTEXITCODE -ne 0) {
            throw "schtasks failed for $taskName"
        }
    } else {
        Write-Output "Would create $taskName at $timeText -> $taskCommand"
    }
}
