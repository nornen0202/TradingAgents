param(
    [ValidateSet("run-due", "publish", "paper", "review", "validate-kis")][string] $Command,
    [string] $RepositoryRoot = "C:\Projects\TradingAgents",
    [string] $ArchiveRoot = "C:\TradingAgentsData\archive",
    [ValidateRange(1024, 65535)][int] $ReviewPort = 8766,
    [switch] $DryRun
)
$ErrorActionPreference = "Stop"
$stateRoot = Join-Path $RepositoryRoot ".runtime\local-automation"
$pythonPath = Join-Path $RepositoryRoot ".venv\Scripts\python.exe"
. (Join-Path $PSScriptRoot 'local_automation_launcher_notifications.ps1')
$pythonInvoked = $false
$locationPushed = $false
$launcherErrorType = 'LocalRuntimeUnavailable'

# Never change the user's checkout or the runner workspaces. Materialize a
# tracked, immutable main revision for each run; no credentials are copied.
try {
    if (-not (Test-Path -LiteralPath $pythonPath)) { throw "Local Python runtime is unavailable." }
    $launcherErrorType = 'StateDirectoryUnavailable'
    [IO.Directory]::CreateDirectory($stateRoot) | Out-Null
    $launcherErrorType = 'SourceFetchFailed'
    Push-Location $RepositoryRoot
    $locationPushed = $true
    # Both five-minute lanes share this checkout. Serialize the remote-ref update
    # and revision selection before taking the immutable snapshot's own lock.
    $repositoryIdentity = (Get-Location).ProviderPath.TrimEnd('\', '/').ToUpperInvariant()
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        $repositoryKey = ([BitConverter]::ToString($sha.ComputeHash(
            [Text.Encoding]::UTF8.GetBytes($repositoryIdentity)))).Replace('-', '').ToLowerInvariant()
    } finally { $sha.Dispose() }
    $fetchMutex = [Threading.Mutex]::new($false, "Local\TradingAgentsSourceFetch-$repositoryKey")
    $fetchOwned = $false
    try {
        try { $fetchOwned = $fetchMutex.WaitOne(60000) } catch [Threading.AbandonedMutexException] { $fetchOwned = $true }
        if (-not $fetchOwned) { throw "Source refresh is still active." }
        & git fetch fork main --quiet
        if ($LASTEXITCODE -ne 0) { throw "Could not refresh fork/main." }
        $launcherErrorType = 'SourceRevisionInvalid'
        $revision = (& git rev-parse fork/main).Trim()
        if ($revision -notmatch '^[0-9a-f]{40}$') { throw "Invalid source revision." }
    } finally {
        if ($fetchOwned) { $fetchMutex.ReleaseMutex() }
        $fetchMutex.Dispose()
    }
    $launcherErrorType = 'SourceSnapshotUnavailable'
    $sourceRoot = Join-Path $stateRoot "source\$revision"
    $sourceMutex = [Threading.Mutex]::new($false, "Local\TradingAgentsSource-$revision")
    $sourceOwned = $false
    try {
        try { $sourceOwned = $sourceMutex.WaitOne(60000) } catch [Threading.AbandonedMutexException] { $sourceOwned = $true }
        if (-not $sourceOwned) { throw "Source snapshot preparation is still active." }
        if (-not (Test-Path -LiteralPath (Join-Path $sourceRoot ".source-ready"))) {
            $zipPath = Join-Path $stateRoot "$revision-$Command.zip"
            & git archive --format=zip "--output=$zipPath" $revision
            if ($LASTEXITCODE -ne 0) { throw "Could not export trusted source." }
            Expand-Archive -LiteralPath $zipPath -DestinationPath $sourceRoot -Force
            Remove-Item -LiteralPath $zipPath -Force
            Set-Content -LiteralPath (Join-Path $sourceRoot ".source-ready") -Value $revision
        }
    } finally {
        if ($sourceOwned) { $sourceMutex.ReleaseMutex() }
        $sourceMutex.Dispose()
    }
    $launcherErrorType = 'WorkerPreparationFailed'
    $env:PYTHONUTF8 = "1"
    $env:TRADINGAGENTS_SOURCE_SHA = $revision
    $env:TRADINGAGENTS_API_KEYS_PATH = Join-Path $RepositoryRoot "config\api_keys.json"
    $env:TRADINGAGENTS_PRISM_TELEGRAM_ARCHIVE_DIR = "C:\TradingAgentsData\prism-telegram-archive"
    $env:TRADINGAGENTS_YOUTUBE_ARCHIVE_DIR = Join-Path $ArchiveRoot "youtube-archive"
    $env:TRADINGAGENTS_MARKET_CALENDAR_CACHE_PATH = Join-Path $stateRoot "market-calendar.json"
    $env:TRADINGAGENTS_AUTOMATION_BACKEND = "local"
    $runtimeSettingsPath = Join-Path $stateRoot 'runtime-settings.json'
    if (Test-Path -LiteralPath $runtimeSettingsPath) {
        $runtimeSettings = Get-Content -LiteralPath $runtimeSettingsPath -Raw | ConvertFrom-Json
        if ($runtimeSettings.codex_workspace_dir) {
            $workspacePath = [string]$runtimeSettings.codex_workspace_dir
            if (-not [IO.Path]::IsPathRooted($workspacePath)) { throw 'Codex workspace must be an absolute local path.' }
            [IO.Directory]::CreateDirectory($workspacePath) | Out-Null
            $env:TRADINGAGENTS_CODEX_WORKSPACE_DIR = [IO.Path]::GetFullPath($workspacePath)
        }
    }
    Set-Location $sourceRoot
    $logPath = Join-Path $stateRoot "$Command.log"
    $arguments = @("-u", "-m", "tradingagents.local_automation", $Command,
        "--archive-dir", $ArchiveRoot, "--state-dir", $stateRoot,
        "--runtime-dir", (Join-Path $RepositoryRoot ".runtime\chatgpt-work"))
    if ($DryRun) { $arguments += "--dry-run" }
    if ($Command -eq 'review') { $arguments += @('--review-port', [string]$ReviewPort) }
    # Windows PowerShell converts redirected native stderr to error records.
    # A recoverable Python warning must not terminate the worker mid-attempt.
    $savedErrorActionPreference = $ErrorActionPreference
    $launcherErrorType = 'WorkerLaunchFailed'
    $exitSentinel = [int]::MinValue
    $global:LASTEXITCODE = $exitSentinel
    try {
        $ErrorActionPreference = "Continue"
        & $pythonPath @arguments *>> $logPath
        $workerExitCode = $LASTEXITCODE
    } finally {
        # Native launch/redirection errors leave LASTEXITCODE unset. A real
        # Python exit, including failure, owns its existing terminal notification.
        $pythonInvoked = $LASTEXITCODE -ne $exitSentinel
        $ErrorActionPreference = $savedErrorActionPreference
    }
    if (-not $pythonInvoked) { throw "Local Python worker could not start." }
    if ($workerExitCode -ne 0) { throw "Local $Command failed. See $logPath" }
    # End worker process boundary.
} catch {
    if (-not $pythonInvoked -and -not $DryRun) {
        try { Send-LocalAutomationLauncherFailure -StateRoot $stateRoot -ErrorType $launcherErrorType }
        catch { Write-Warning 'Launcher notification remains pending; durable state or dispatch was unavailable.' }
    }
    throw
} finally {
    if ($locationPushed) { Pop-Location }
}
