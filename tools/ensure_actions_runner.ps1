[CmdletBinding()]
param(
    [string] $RunnerRoot = "C:\actions-runner",
    [int] $StartupWaitSeconds = 45,
    [switch] $SkipServiceStart
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$resolvedRunnerRoot = [IO.Path]::GetFullPath($RunnerRoot).TrimEnd(
    [IO.Path]::DirectorySeparatorChar,
    [IO.Path]::AltDirectorySeparatorChar
)
$listenerPath = [IO.Path]::GetFullPath(
    (Join-Path $resolvedRunnerRoot "bin\Runner.Listener.exe")
)
$runCommand = Join-Path $resolvedRunnerRoot "run.cmd"
$serviceMarker = Join-Path $resolvedRunnerRoot ".service"

if (-not (Test-Path -LiteralPath $listenerPath -PathType Leaf)) {
    throw "GitHub Actions listener not found: $listenerPath"
}
if (-not (Test-Path -LiteralPath $runCommand -PathType Leaf)) {
    throw "GitHub Actions run command not found: $runCommand"
}

function Get-TargetRunnerListener {
    @(Get-CimInstance Win32_Process -Filter "Name='Runner.Listener.exe'" -ErrorAction SilentlyContinue) |
        Where-Object {
            $candidate = [string]$_.ExecutablePath
            if ([string]::IsNullOrWhiteSpace($candidate)) {
                return $false
            }
            try {
                return [IO.Path]::GetFullPath($candidate).Equals(
                    $listenerPath,
                    [StringComparison]::OrdinalIgnoreCase
                )
            } catch {
                return $false
            }
        }
}

function Wait-ForTargetRunnerListener {
    param([int] $Seconds)

    $deadline = [DateTimeOffset]::Now.AddSeconds([Math]::Max(1, $Seconds))
    do {
        $listener = @(Get-TargetRunnerListener)
        if ($listener.Count -gt 0) {
            return $listener
        }
        Start-Sleep -Seconds 1
    } while ([DateTimeOffset]::Now -lt $deadline)
    return @()
}

$mutex = [Threading.Mutex]::new(
    $false,
    "Local\TradingAgentsActionsRunnerKeepAlive"
)
$ownsMutex = $false
try {
    try {
        $ownsMutex = $mutex.WaitOne(0)
    } catch [Threading.AbandonedMutexException] {
        $ownsMutex = $true
    }
    if (-not $ownsMutex) {
        Write-Output "NOOP another keepalive check is active"
        return
    }

    $listener = @(Get-TargetRunnerListener)
    if ($listener.Count -gt 0) {
        Write-Output "HEALTHY runner listener is active pid=$($listener[0].ProcessId)"
        return
    }

    if (-not $SkipServiceStart -and (Test-Path -LiteralPath $serviceMarker -PathType Leaf)) {
        $serviceName = (Get-Content -LiteralPath $serviceMarker -Raw).Trim()
        if (-not [string]::IsNullOrWhiteSpace($serviceName)) {
            $service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
            if ($null -ne $service) {
                try {
                    if ($service.Status -ne [ServiceProcess.ServiceControllerStatus]::Running) {
                        Start-Service -Name $serviceName -ErrorAction Stop
                    }
                    $listener = @(Wait-ForTargetRunnerListener -Seconds 15)
                    if ($listener.Count -gt 0) {
                        Write-Output "RECOVERED service runner listener pid=$($listener[0].ProcessId)"
                        return
                    }
                } catch {
                    Write-Warning (
                        "Runner service could not start; using the current-user fallback. " +
                        $_.Exception.Message
                    )
                }
            }
        }
    }

    $launcher = Start-Process `
        -FilePath $runCommand `
        -WorkingDirectory $resolvedRunnerRoot `
        -WindowStyle Hidden `
        -PassThru
    $listener = @(Wait-ForTargetRunnerListener -Seconds $StartupWaitSeconds)
    if ($listener.Count -eq 0) {
        throw (
            "Runner fallback launcher pid=$($launcher.Id) did not start " +
            "Runner.Listener.exe within $StartupWaitSeconds seconds."
        )
    }
    Write-Output "RECOVERED current-user runner listener pid=$($listener[0].ProcessId)"
} finally {
    if ($ownsMutex) {
        $mutex.ReleaseMutex()
    }
    $mutex.Dispose()
}
