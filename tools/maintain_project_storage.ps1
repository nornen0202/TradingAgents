[CmdletBinding()]
param(
    [string]$DataRoot = "C:\TradingAgentsData",
    [string]$RunnerRoot = "C:\actions-runner",
    [string]$RepositoryRoot = "C:\Projects\TradingAgents",
    [ValidateRange(1, 3650)]
    [int]$RetentionDays = 14,
    [ValidateRange(1, 3650)]
    [int]$RunnerDiagnosticRetentionDays = 14,
    [ValidateRange(1, 3650)]
    [int]$RunnerUpdateRetentionDays = 7,
    [ValidateRange(0, 720)]
    [int]$RunnerArtifactMinimumAgeHours = 6,
    [ValidateRange(1, 3650)]
    [int]$RepositoryArtifactRetentionDays = 30,
    [ValidateRange(1, 3650)]
    [int]$CodexAttachmentRetentionDays = 30,
    [string]$LogPath = "C:\TradingAgentsData\automation-logs\storage-maintenance.log",
    [switch]$Apply
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

trap {
    try {
        if (-not [string]::IsNullOrWhiteSpace($LogPath)) {
            $errorLogParent = Split-Path -Parent $LogPath
            if ($errorLogParent) {
                [IO.Directory]::CreateDirectory($errorLogParent) | Out-Null
            }
            Add-Content -LiteralPath $LogPath -Value "ERROR time=$((Get-Date).ToString('s')) message=$($_.Exception.Message)" -Encoding utf8
        }
    }
    catch {
        # Preserve the original maintenance failure.
    }
    [Console]::Error.WriteLine($_.ToString())
    exit 1
}

$script:plannedBytes = [int64]0
$script:removedBytes = [int64]0
$script:plannedItems = 0
$script:removedItems = 0

function Resolve-NormalizedPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    return [IO.Path]::GetFullPath($Path).TrimEnd(
        [IO.Path]::DirectorySeparatorChar,
        [IO.Path]::AltDirectorySeparatorChar
    )
}

function Assert-ChildPath {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Root
    )

    $resolvedPath = Resolve-NormalizedPath $Path
    $resolvedRoot = Resolve-NormalizedPath $Root
    $prefix = $resolvedRoot + [IO.Path]::DirectorySeparatorChar
    if (
        $resolvedPath -eq $resolvedRoot -or
        -not $resolvedPath.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)
    ) {
        throw "Refusing destructive target outside the validated root: $resolvedPath"
    }
    return $resolvedPath
}

function Get-TreeBytes {
    param([Parameter(Mandatory = $true)][string]$Path)

    $total = [int64]0
    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        return $total
    }
    foreach ($filePath in [IO.Directory]::EnumerateFiles($Path, "*", [IO.SearchOption]::AllDirectories)) {
        try {
            $total += ([IO.FileInfo]::new($filePath)).Length
        }
        catch {
            Write-Warning "Could not measure $filePath`: $($_.Exception.Message)"
        }
    }
    return $total
}

function Remove-ValidatedTree {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$Reason
    )

    $target = Assert-ChildPath -Path $Path -Root $Root
    if (-not (Test-Path -LiteralPath $target -PathType Container)) {
        return
    }
    $bytes = Get-TreeBytes $target
    $script:plannedBytes += $bytes
    $script:plannedItems++
    if (-not $Apply) {
        Write-Output "WOULD_REMOVE tree=$target bytes=$bytes reason=$Reason"
        return
    }

    foreach ($filePath in [IO.Directory]::EnumerateFiles($target, "*", [IO.SearchOption]::AllDirectories)) {
        try {
            [IO.File]::SetAttributes($filePath, [IO.FileAttributes]::Normal)
        }
        catch {
            Write-Warning "Could not clear file attributes for $filePath`: $($_.Exception.Message)"
        }
    }
    foreach ($directoryPath in (
        [IO.Directory]::EnumerateDirectories($target, "*", [IO.SearchOption]::AllDirectories) |
            Sort-Object Length -Descending
    )) {
        try {
            [IO.File]::SetAttributes($directoryPath, [IO.FileAttributes]::Directory)
        }
        catch {
            Write-Warning "Could not clear directory attributes for $directoryPath`: $($_.Exception.Message)"
        }
    }
    [IO.File]::SetAttributes($target, [IO.FileAttributes]::Directory)
    [IO.Directory]::Delete($target, $true)
    $script:removedBytes += $bytes
    $script:removedItems++
    Write-Output "REMOVED tree=$target bytes=$bytes reason=$Reason"
}

function Remove-ValidatedFile {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$Reason
    )

    $target = Assert-ChildPath -Path $Path -Root $Root
    if (-not (Test-Path -LiteralPath $target -PathType Leaf)) {
        return
    }
    $bytes = ([IO.FileInfo]::new($target)).Length
    $script:plannedBytes += $bytes
    $script:plannedItems++
    if (-not $Apply) {
        Write-Output "WOULD_REMOVE file=$target bytes=$bytes reason=$Reason"
        return
    }
    [IO.File]::SetAttributes($target, [IO.FileAttributes]::Normal)
    [IO.File]::Delete($target)
    $script:removedBytes += $bytes
    $script:removedItems++
    Write-Output "REMOVED file=$target bytes=$bytes reason=$Reason"
}

function Get-LatestRunIds {
    param([Parameter(Mandatory = $true)][string]$Root)

    $ids = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($relativePath in @(
        "archive\latest-run.json",
        "archive\youtube-archive\latest-youtube-run.json",
        "prism-telegram-archive\latest-prism-telegram-run.json"
    )) {
        $manifestPath = Join-Path $Root $relativePath
        if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
            continue
        }
        try {
            $manifestText = Get-Content -LiteralPath $manifestPath -Raw
            if ($manifestText -match '"run_id"\s*:\s*"([^"]+)"') {
                [void]$ids.Add([string]$Matches[1])
            }
        }
        catch {
            Write-Warning "Could not read latest-run pointer $manifestPath`: $($_.Exception.Message)"
        }
    }
    return $ids
}

function Test-TradingAgentsRunnerBusy {
    param([Parameter(Mandatory = $true)][string]$Root)

    $resolvedRoot = Resolve-NormalizedPath $Root
    foreach ($process in @(Get-Process -Name "Runner.Worker" -ErrorAction SilentlyContinue)) {
        try {
            if (-not $process.Path) {
                return $true
            }
            if ((Resolve-NormalizedPath $process.Path).StartsWith(
                $resolvedRoot + [IO.Path]::DirectorySeparatorChar,
                [StringComparison]::OrdinalIgnoreCase
            )) {
                return $true
            }
        }
        catch {
            # If Windows denies the executable path, fail closed and preserve the workspace.
            return $true
        }
    }
    return $false
}

function Write-MaintenanceLog {
    param([Parameter(Mandatory = $true)][string]$Message)

    if (-not $Apply -or [string]::IsNullOrWhiteSpace($LogPath)) {
        return
    }
    $parent = Split-Path -Parent $LogPath
    if ($parent) {
        [IO.Directory]::CreateDirectory($parent) | Out-Null
    }
    Add-Content -LiteralPath $LogPath -Value $Message -Encoding utf8
}

$mutex = [Threading.Mutex]::new($false, "Local\TradingAgentsStorageMaintenance")
$hasMutex = $false
try {
    $hasMutex = $mutex.WaitOne(0)
    if (-not $hasMutex) {
        throw "Another TradingAgents storage-maintenance run is active."
    }

    $startedAt = Get-Date
    $runnerBusy = Test-TradingAgentsRunnerBusy -Root $RunnerRoot
    $latestRunIds = Get-LatestRunIds -Root $DataRoot

    if ($runnerBusy) {
        Write-Warning "TradingAgents Runner.Worker is active; archive and runner cleanup were skipped."
    }
    else {
        $archiveCutoff = (Get-Date).Date.AddDays(-$RetentionDays)
        $archiveSpecs = @(
            @{ Root = Join-Path $DataRoot "archive\runs"; Pattern = "^(\d{8})T" },
            @{ Root = Join-Path $DataRoot "archive\youtube-archive\runs"; Pattern = "^youtube_(\d{8})_" },
            @{ Root = Join-Path $DataRoot "prism-telegram-archive\runs"; Pattern = "^prism_telegram_(\d{8})_" }
        )
        foreach ($spec in $archiveSpecs) {
            if (-not (Test-Path -LiteralPath $spec.Root -PathType Container)) {
                continue
            }
            foreach ($yearDirectory in Get-ChildItem -LiteralPath $spec.Root -Force -Directory) {
                foreach ($runDirectory in Get-ChildItem -LiteralPath $yearDirectory.FullName -Force -Directory) {
                    if ($runDirectory.Name -notmatch $spec.Pattern) {
                        continue
                    }
                    $runDate = [datetime]::ParseExact(
                        $Matches[1],
                        "yyyyMMdd",
                        [Globalization.CultureInfo]::InvariantCulture
                    )
                    if ($runDate -ge $archiveCutoff -or $latestRunIds.Contains($runDirectory.Name)) {
                        continue
                    }
                    if (Test-TradingAgentsRunnerBusy -Root $RunnerRoot) {
                        throw "TradingAgents Runner.Worker started during archive cleanup."
                    }
                    Remove-ValidatedTree -Path $runDirectory.FullName -Root $spec.Root -Reason "archive older than $RetentionDays days"
                }
            }
        }

        $workspaceRoot = Join-Path $RunnerRoot "_work\TradingAgents\TradingAgents"
        $artifactCutoff = (Get-Date).AddHours(-$RunnerArtifactMinimumAgeHours)
        if (Test-Path -LiteralPath $workspaceRoot -PathType Container) {
            foreach ($directory in Get-ChildItem -LiteralPath $workspaceRoot -Force -Directory) {
                $knownArtifact = (
                    $directory.Name -eq "portfolio-artifacts" -or
                    $directory.Name -eq ".codex-preflight" -or
                    $directory.Name -match "^site-\d+$" -or
                    $directory.Name -match "^source-\d+$" -or
                    $directory.Name -match "^analysis-diagnostics-(kr|us)$"
                )
                if ($knownArtifact -and $directory.LastWriteTime -lt $artifactCutoff) {
                    if (Test-TradingAgentsRunnerBusy -Root $RunnerRoot) {
                        throw "TradingAgents Runner.Worker started during runner cleanup."
                    }
                    Remove-ValidatedTree -Path $directory.FullName -Root $workspaceRoot -Reason "completed runner artifact older than $RunnerArtifactMinimumAgeHours hours"
                }
            }
        }

        $diagnosticRoot = Join-Path $RunnerRoot "_diag"
        $diagnosticCutoff = (Get-Date).Date.AddDays(-$RunnerDiagnosticRetentionDays)
        if (Test-Path -LiteralPath $diagnosticRoot -PathType Container) {
            foreach ($file in Get-ChildItem -LiteralPath $diagnosticRoot -Force -File -Recurse) {
                if ($file.LastWriteTime -lt $diagnosticCutoff) {
                    if (Test-TradingAgentsRunnerBusy -Root $RunnerRoot) {
                        throw "TradingAgents Runner.Worker started during diagnostic cleanup."
                    }
                    Remove-ValidatedFile -Path $file.FullName -Root $diagnosticRoot -Reason "runner diagnostic older than $RunnerDiagnosticRetentionDays days"
                }
            }
        }

        $runnerUpdateCutoff = (Get-Date).Date.AddDays(-$RunnerUpdateRetentionDays)
        $updateStaging = Join-Path $RunnerRoot "_work\_update"
        if (
            (Test-Path -LiteralPath $updateStaging -PathType Container) -and
            (Get-Item -LiteralPath $updateStaging).LastWriteTime -lt $runnerUpdateCutoff
        ) {
            if (Test-TradingAgentsRunnerBusy -Root $RunnerRoot) {
                throw "TradingAgents Runner.Worker started during update cleanup."
            }
            Remove-ValidatedTree -Path $updateStaging -Root $RunnerRoot -Reason "completed runner update staging older than $RunnerUpdateRetentionDays days"
        }

        foreach ($prefix in @("bin.", "externals.")) {
            $backups = @(
                Get-ChildItem -LiteralPath $RunnerRoot -Force -Directory |
                    Where-Object { $_.Name.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase) } |
                    Sort-Object LastWriteTime -Descending
            )
            foreach ($backup in @($backups | Select-Object -Skip 1)) {
                if ($backup.LastWriteTime -lt $runnerUpdateCutoff) {
                    if (Test-TradingAgentsRunnerBusy -Root $RunnerRoot) {
                        throw "TradingAgents Runner.Worker started during backup cleanup."
                    }
                    Remove-ValidatedTree -Path $backup.FullName -Root $RunnerRoot -Reason "superseded runner backup older than $RunnerUpdateRetentionDays days"
                }
            }
        }
        foreach ($installer in Get-ChildItem -LiteralPath $RunnerRoot -Force -File -Filter "actions-runner-win-*.zip") {
            if ($installer.LastWriteTime -lt $runnerUpdateCutoff) {
                if (Test-TradingAgentsRunnerBusy -Root $RunnerRoot) {
                    throw "TradingAgents Runner.Worker started during installer cleanup."
                }
                Remove-ValidatedFile -Path $installer.FullName -Root $RunnerRoot -Reason "runner installer older than $RunnerUpdateRetentionDays days"
            }
        }
    }

    $repositoryCutoff = (Get-Date).Date.AddDays(-$RepositoryArtifactRetentionDays)
    $siteRoot = Join-Path $RepositoryRoot "site"
    if (
        (Test-Path -LiteralPath $siteRoot -PathType Container) -and
        (Get-Item -LiteralPath $siteRoot).LastWriteTime -lt $repositoryCutoff
    ) {
        Remove-ValidatedTree -Path $siteRoot -Root $RepositoryRoot -Reason "ignored local site older than $RepositoryArtifactRetentionDays days"
    }

    $runtimeRoot = Join-Path $RepositoryRoot ".runtime"
    if (Test-Path -LiteralPath $runtimeRoot -PathType Container) {
        foreach ($directory in Get-ChildItem -LiteralPath $runtimeRoot -Force -Directory) {
            $knownGeneratedRuntime = (
                $directory.Name -match "^public-account-verify-" -or
                $directory.Name -match "^run-\d+.*-artifacts" -or
                $directory.Name -match "smoke$" -or
                $directory.Name -in @(
                    "codex-preflight-test",
                    "verify-prism-site",
                    "conditional-replay",
                    "decision-bundle-smoke"
                )
            )
            if ($knownGeneratedRuntime -and $directory.LastWriteTime -lt $repositoryCutoff) {
                Remove-ValidatedTree -Path $directory.FullName -Root $runtimeRoot -Reason "known generated runtime older than $RepositoryArtifactRetentionDays days"
            }
        }
    }

    $attachmentRoot = Join-Path $RepositoryRoot ".codex-remote-attachments"
    $attachmentCutoff = (Get-Date).Date.AddDays(-$CodexAttachmentRetentionDays)
    if (Test-Path -LiteralPath $attachmentRoot -PathType Container) {
        foreach ($directory in Get-ChildItem -LiteralPath $attachmentRoot -Force -Directory) {
            $knownAttachmentCache = (
                $directory.Name -match "^run-\d+(-diagnostics)?$" -or
                $directory.Name -match "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
            )
            if ($knownAttachmentCache -and $directory.LastWriteTime -lt $attachmentCutoff) {
                Remove-ValidatedTree -Path $directory.FullName -Root $attachmentRoot -Reason "Codex attachment cache older than $CodexAttachmentRetentionDays days"
            }
        }
    }

    $summary = "SUMMARY time=$($startedAt.ToString('s')) mode=$(if ($Apply) {'apply'} else {'dry-run'}) planned_items=$script:plannedItems planned_bytes=$script:plannedBytes removed_items=$script:removedItems removed_bytes=$script:removedBytes runner_busy=$runnerBusy"
    Write-Output $summary
    Write-MaintenanceLog $summary
}
finally {
    if ($hasMutex) {
        $mutex.ReleaseMutex()
    }
    $mutex.Dispose()
}
