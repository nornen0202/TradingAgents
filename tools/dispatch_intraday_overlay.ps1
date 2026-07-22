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
    [int] $FailureCooldownMinutes = 360,
    [int] $MaxIdenticalFailedAttempts = 2,
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

function Test-RunMatchesProfile {
    param(
        [object] $Run,
        [string] $ExpectedProfile
    )
    $title = [string] $Run.displayTitle
    $match = [regex]::Match($title, '\[profile=(kr|us|all)\]', [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
    if (-not $match.Success) {
        # Runs created before profile markers were introduced remain eligible
        # for the short recent-run guard, but not for failure fingerprinting.
        return $null
    }
    $markedProfile = $match.Groups[1].Value.ToLowerInvariant()
    if ($ExpectedProfile -eq "all") {
        return $markedProfile -eq "all"
    }
    return $markedProfile -eq $ExpectedProfile -or $markedProfile -eq "all"
}

function Get-RunMarker {
    param(
        [object] $Run,
        [string] $Name
    )
    $title = [string] $Run.displayTitle
    $match = [regex]::Match(
        $title,
        "\[$([regex]::Escape($Name))=([a-zA-Z0-9_-]+)\]",
        [System.Text.RegularExpressions.RegexOptions]::IgnoreCase
    )
    if (-not $match.Success) {
        return ""
    }
    return $match.Groups[1].Value.ToLowerInvariant()
}

function Get-RunRecoverySource {
    param([object] $Run)
    $marked = Get-RunMarker -Run $Run -Name "recovery_source"
    if ($marked) {
        return $marked
    }
    if (([string] $Run.event).ToLowerInvariant() -eq "schedule") {
        return "native"
    }
    if (([string] $Run.event).ToLowerInvariant() -eq "workflow_dispatch") {
        return "manual"
    }
    return "unknown"
}

function Test-RunMatchesModeAndScope {
    param(
        [object] $Run,
        [string] $ExpectedRunMode
    )
    $runMode = Get-RunMarker -Run $Run -Name "run_mode"
    if ($runMode -and $runMode -ne $ExpectedRunMode) {
        return $false
    }
    $requestScope = Get-RunMarker -Run $Run -Name "request_scope"
    if ($requestScope -in @("custom_tickers", "custom_sources")) {
        return $false
    }
    # A default-scope manual run is valid coverage for duplicate prevention.
    # Manual failures are excluded separately from the automated retry budget.
    return $true
}

function Get-FailureDiagnosticSignature {
    param(
        [string] $Gh,
        [string] $Repository,
        [object] $Run
    )
    $logOutput = & $Gh run view $Run.databaseId --repo $Repository --log-failed 2>&1
    if ($LASTEXITCODE -ne 0) {
        return ""
    }
    $diagnostics = @(
        $logOutput |
            ForEach-Object { [string] $_ } |
            Where-Object { $_ -match '(?i)(OVERLAY_[A-Z0-9_]+|##\[error\]|\b(error|exception|traceback|failed)\b)' } |
            ForEach-Object {
                $line = $_.ToLowerInvariant()
                $line = $line -replace '^\d{4}-\d{2}-\d{2}t\d{2}:\d{2}:\d{2}(\.\d+)?z\s+', ''
                $line = $line -replace 'https?://\S+', '<url>'
                $line = $line -replace '\b[0-9a-f]{12,}\b', '<hex>'
                ($line -replace '\s+', ' ').Trim()
            } |
            Where-Object { $_ } |
            Select-Object -Unique -First 8
    )
    if ($diagnostics.Count -eq 0) {
        return ""
    }
    $bytes = [System.Text.Encoding]::UTF8.GetBytes(($diagnostics -join "`n"))
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    try {
        return ([BitConverter]::ToString($sha256.ComputeHash($bytes))).Replace("-", "").ToLowerInvariant()
    } finally {
        $sha256.Dispose()
    }
}

function Get-TargetFailureFingerprint {
    param(
        [string] $Gh,
        [string] $Repository,
        [object] $Run,
        [string] $ExpectedProfile
    )
    $profileMatch = Test-RunMatchesProfile -Run $Run -ExpectedProfile $ExpectedProfile
    if ($profileMatch -ne $true) {
        return $null
    }
    $viewJson = & $Gh run view $Run.databaseId --repo $Repository --json jobs 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-DispatchLog "failure fingerprint probe skipped for run $($Run.databaseId): $viewJson" | Out-Null
        return $null
    }
    $payload = $viewJson | ConvertFrom-Json
    if ($ExpectedProfile -notin @("kr", "us")) {
        throw "Failure fingerprinting requires one concrete profile."
    }
    if (-not (Test-RunMatchesModeAndScope -Run $Run -ExpectedRunMode $RunMode)) {
        return $null
    }
    $targetNames = @(
        "overlay_gate",
        "overlay_refresh_$ExpectedProfile",
        "publish_overlay_site",
        "deploy_overlay"
    )
    $failedStages = @()
    $successfulTargets = @()
    $workJobConclusion = ""
    foreach ($job in @($payload.jobs)) {
        if ([string] $job.name -notin $targetNames) {
            continue
        }
        $jobConclusion = ([string] $job.conclusion).ToLowerInvariant()
        if ([string] $job.name -eq "overlay_refresh_$ExpectedProfile") {
            $workJobConclusion = $jobConclusion
        }
        if ($jobConclusion -eq "success") {
            $successfulTargets += [string] $job.name
            continue
        }
        if ($jobConclusion -in @("", "success", "skipped", "neutral")) {
            continue
        }
        $failedSteps = @($job.steps | Where-Object {
            ([string] $_.conclusion).ToLowerInvariant() -notin @("", "success", "skipped", "neutral")
        })
        if ($failedSteps.Count -eq 0) {
            $failedStages += "$($job.name):$jobConclusion"
            continue
        }
        foreach ($step in $failedSteps) {
            $failedStages += "$($job.name)/$($step.name):$(([string] $step.conclusion).ToLowerInvariant())"
        }
    }
    $allTargetsSucceeded = @($targetNames | Where-Object { $_ -notin $successfulTargets }).Count -eq 0
    if ($failedStages.Count -eq 0) {
        if ($allTargetsSucceeded) {
            return "__TARGET_SUCCESS__"
        }
        if (
            ([string] $Run.status).ToLowerInvariant() -eq "completed" -and
            ([string] $Run.conclusion).ToLowerInvariant() -eq "success" -and
            $workJobConclusion -in @("skipped", "neutral")
        ) {
            return "__TARGET_SUCCESS__"
        }
        foreach ($targetName in $targetNames) {
            if ($targetName -in $successfulTargets) {
                continue
            }
            $targetJob = @($payload.jobs | Where-Object { [string] $_.name -eq $targetName }) | Select-Object -First 1
            $targetConclusion = if ($targetJob) { ([string] $targetJob.conclusion).ToLowerInvariant() } else { "" }
            if ($targetConclusion -in @("", "skipped", "neutral")) {
                $failedStages += "missing_or_skipped_required_job:$targetName"
            }
        }
        $allFailedJobs = @($payload.jobs | Where-Object {
            ([string] $_.conclusion).ToLowerInvariant() -notin @("", "success", "skipped", "neutral")
        })
        foreach ($job in $allFailedJobs) {
            $failedStages += "$($job.name):$(([string] $job.conclusion).ToLowerInvariant())"
        }
        if ($failedStages.Count -eq 0) {
            $workflowConclusion = ([string] $Run.conclusion).ToLowerInvariant()
            if ($workflowConclusion -notin @("", "success", "skipped", "neutral")) {
                $failedStages += "workflow:$workflowConclusion"
            }
        }
        if ($failedStages.Count -eq 0) {
            return $null
        }
    }
    $headSha = ([string] $Run.headSha).Trim().ToLowerInvariant()
    if (-not $headSha) {
        $headSha = "unknown"
    }
    $diagnosticSignature = Get-FailureDiagnosticSignature -Gh $Gh -Repository $Repository -Run $Run
    $diagnosticContext = if ($diagnosticSignature) { "diagnostic=$diagnosticSignature" } else { "diagnostic=unavailable" }
    return "$headSha|profile=$ExpectedProfile|run_mode=$RunMode|request_scope=default_universe|$diagnosticContext|$((@($failedStages | Sort-Object -Unique)) -join '|')"
}

Write-DispatchLog "start profile=$Profile run_mode=$RunMode recovery_source=local_watchdog repo=$Repo workflow=$Workflow ref=$Ref"
$gh = Resolve-GhPath
Write-DispatchLog "using gh: $gh"
$nowUtc = [DateTimeOffset]::UtcNow
$eligibleProfiles = if ($Profile -eq "all") { @("kr", "us") } else { @($Profile) }

if (-not $Force) {
    $runsJson = & $gh run list `
        --repo $Repo `
        --workflow $Workflow `
        --limit 50 `
        --json databaseId,event,status,conclusion,createdAt,url,headSha,displayTitle 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-DispatchLog "recent-run probe failed; attempting dispatch anyway: $runsJson"
    } else {
        $cutoffUtc = $nowUtc.AddMinutes(-1 * [Math]::Max($RecentRunWindowMinutes, 1))
        # Windows PowerShell 5.1 emits a top-level JSON array as one pipeline
        # object when ConvertFrom-Json is wrapped directly in @(...). Assigning
        # first and normalizing second preserves one run object per element on
        # both Windows PowerShell 5.1 and PowerShell 7.
        $parsedRuns = $runsJson | ConvertFrom-Json
        $allRuns = @($parsedRuns)
        # Never dispatch a second run for a profile that is already active,
        # even when the first run is older than the short recent-run window.
        # Full overlay + Pages publication can legitimately exceed 20 minutes.
        $activeRuns = @($allRuns | Where-Object {
            $candidateEvent = $_.event -eq "schedule" -or $_.event -eq "workflow_dispatch"
            $candidateStatus = ([string] $_.status).ToLowerInvariant()
            if (-not $candidateEvent -or $candidateStatus -eq "completed") {
                return $false
            }
            return [bool](Test-RunMatchesModeAndScope -Run $_ -ExpectedRunMode $RunMode)
        } | Sort-Object createdAt -Descending)
        if ($Profile -eq "all") {
            $eligibleProfiles = @($eligibleProfiles | Where-Object {
                $profileToKeep = $_
                @($activeRuns | Where-Object {
                    (Test-RunMatchesProfile -Run $_ -ExpectedProfile $profileToKeep) -ne $false
                }).Count -eq 0
            })
        } else {
            $activeCoverage = @($activeRuns | Where-Object {
                (Test-RunMatchesProfile -Run $_ -ExpectedProfile $Profile) -ne $false
            }).Count -gt 0
            if ($activeCoverage) {
                $eligibleProfiles = @()
            }
        }
        if ($eligibleProfiles.Count -eq 0) {
            $latest = @($activeRuns | Select-Object -First 1)[0]
            Write-DispatchLog "skip dispatch: active $Workflow coverage exists for profile=$Profile regardless_of_age=true latest_id=$($latest.databaseId) event=$($latest.event) status=$($latest.status) url=$($latest.url)"
            exit 0
        }
        $recentRuns = @($allRuns | Where-Object {
            $createdUtc = Convert-ToUtcDateTime $_.createdAt
            ($_.event -eq "schedule" -or $_.event -eq "workflow_dispatch") -and
            $createdUtc -ne $null -and
            $createdUtc -ge $cutoffUtc.UtcDateTime -and
            (Test-RunMatchesModeAndScope -Run $_ -ExpectedRunMode $RunMode)
        })
        if ($Profile -eq "all") {
            $eligibleProfiles = @($eligibleProfiles | Where-Object {
                $profileToKeep = $_
                @($recentRuns | Where-Object {
                    (Test-RunMatchesProfile -Run $_ -ExpectedProfile $profileToKeep) -eq $true
                }).Count -eq 0
            })
        } else {
            $recentCoverage = @($recentRuns | Where-Object {
                $match = Test-RunMatchesProfile -Run $_ -ExpectedProfile $Profile
                $match -ne $false
            }).Count -gt 0
            if ($recentCoverage) {
                $eligibleProfiles = @()
            }
        }
        if ($eligibleProfiles.Count -eq 0) {
            $latest = $recentRuns | Select-Object -First 1
            Write-DispatchLog "skip dispatch: recent $Workflow coverage exists for profile=$Profile latest_id=$($latest.databaseId) event=$($latest.event) status=$($latest.status) url=$($latest.url)"
            exit 0
        }

        $failureCutoffUtc = $nowUtc.AddMinutes(-1 * [Math]::Max($FailureCooldownMinutes, 1))
        $exhaustedProfiles = @()
        $exhaustedRunIds = @()
        foreach ($profileToCheck in @($eligibleProfiles)) {
            $cooldownRuns = @($allRuns | Where-Object {
                $createdUtc = Convert-ToUtcDateTime $_.createdAt
                $profileMatch = Test-RunMatchesProfile -Run $_ -ExpectedProfile $profileToCheck
                $createdUtc -ne $null -and
                $createdUtc -ge $failureCutoffUtc.UtcDateTime -and
                ([string] $_.status).ToLowerInvariant() -eq "completed" -and
                $profileMatch -eq $true -and
                (Get-RunRecoverySource -Run $_) -ne "manual" -and
                (Test-RunMatchesModeAndScope -Run $_ -ExpectedRunMode $RunMode)
            } | Sort-Object createdAt -Descending)
            $matchingFailures = @()
            $latestFingerprint = $null
            foreach ($candidateRun in $cooldownRuns) {
                $receipt = Get-TargetFailureFingerprint `
                    -Gh $gh `
                    -Repository $Repo `
                    -Run $candidateRun `
                    -ExpectedProfile $profileToCheck
                if ($receipt -eq "__TARGET_SUCCESS__") {
                    break
                }
                if (-not $receipt) {
                    continue
                }
                if (-not $latestFingerprint) {
                    $latestFingerprint = $receipt
                } elseif ($receipt -ne $latestFingerprint) {
                    break
                }
                $matchingFailures += [pscustomobject]@{
                    RunId = $candidateRun.databaseId
                    Fingerprint = $receipt
                }
            }
            if (
                $MaxIdenticalFailedAttempts -gt 0 -and
                $matchingFailures.Count -ge $MaxIdenticalFailedAttempts
            ) {
                $exhaustedProfiles += $profileToCheck
                $exhaustedRunIds += @(
                    $matchingFailures |
                        Select-Object -First $MaxIdenticalFailedAttempts |
                        ForEach-Object { $_.RunId }
                )
            }
        }
        $eligibleProfiles = @($eligibleProfiles | Where-Object { $_ -notin $exhaustedProfiles })
        if ($eligibleProfiles.Count -eq 0) {
            $runIds = (@($exhaustedRunIds | Select-Object -Unique)) -join ","
            Write-DispatchLog "skip dispatch: identical end-to-end failure retry budget exhausted profiles=$($exhaustedProfiles -join ',') max=$MaxIdenticalFailedAttempts cooldown_minutes=$FailureCooldownMinutes run_ids=$runIds"
            exit 0
        }
    }
}

foreach ($dispatchProfile in $eligibleProfiles) {
    $dispatchArgs = @(
        "workflow",
        "run",
        $Workflow,
        "--repo",
        $Repo,
        "--ref",
        $Ref,
        "-f",
        "profile=$dispatchProfile",
        "-f",
        "run_mode=$RunMode",
        "-f",
        "recovery_source=local_watchdog"
    )

    if ($DryRun) {
        Write-DispatchLog "dry-run dispatch: gh $($dispatchArgs -join ' ')"
        continue
    }

    Write-DispatchLog "dispatching: gh $($dispatchArgs -join ' ')"
    $dispatchOutput = & $gh @dispatchArgs 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-DispatchLog "dispatch failed: $dispatchOutput"
        exit $LASTEXITCODE
    }
    Write-DispatchLog "dispatch accepted: $dispatchOutput"
}
