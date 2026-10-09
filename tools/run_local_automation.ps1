param(
    [ValidateSet("run-due", "publish")][string] $Command,
    [string] $RepositoryRoot = "C:\Projects\TradingAgents",
    [string] $ArchiveRoot = "C:\TradingAgentsData\archive",
    [switch] $DryRun
)
$ErrorActionPreference = "Stop"
$stateRoot = Join-Path $RepositoryRoot ".runtime\local-automation"
$pythonPath = Join-Path $RepositoryRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $pythonPath)) { throw "Local Python runtime is unavailable." }
[IO.Directory]::CreateDirectory($stateRoot) | Out-Null

# Never change the user's checkout or the runner workspaces. Materialize a
# tracked, immutable main revision for each run; no credentials are copied.
Push-Location $RepositoryRoot
try {
    & git fetch fork main --quiet
    if ($LASTEXITCODE -ne 0) { throw "Could not refresh fork/main." }
    $revision = (& git rev-parse fork/main).Trim()
    if ($revision -notmatch '^[0-9a-f]{40}$') { throw "Invalid source revision." }
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
    $env:PYTHONUTF8 = "1"
    $env:TRADINGAGENTS_SOURCE_SHA = $revision
    $env:TRADINGAGENTS_API_KEYS_PATH = Join-Path $RepositoryRoot "config\api_keys.json"
    $env:TRADINGAGENTS_PRISM_TELEGRAM_ARCHIVE_DIR = "C:\TradingAgentsData\prism-telegram-archive"
    $env:TRADINGAGENTS_YOUTUBE_ARCHIVE_DIR = Join-Path $ArchiveRoot "youtube-archive"
    $env:TRADINGAGENTS_MARKET_CALENDAR_CACHE_PATH = Join-Path $stateRoot "market-calendar.json"
    $env:TRADINGAGENTS_AUTOMATION_BACKEND = "local"
    Set-Location $sourceRoot
    $logPath = Join-Path $stateRoot "$Command.log"
    $arguments = @("-u", "-m", "tradingagents.local_automation", $Command,
        "--archive-dir", $ArchiveRoot, "--state-dir", $stateRoot,
        "--runtime-dir", (Join-Path $RepositoryRoot ".runtime\chatgpt-work"))
    if ($DryRun) { $arguments += "--dry-run" }
    & $pythonPath @arguments *>> $logPath
    if ($LASTEXITCODE -ne 0) { throw "Local $Command failed. See $logPath" }
} finally { Pop-Location }
