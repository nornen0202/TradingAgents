# Bootstrap only: no Python, account configuration, or Telegram credentials.
function Write-LocalLauncherJson {
    param([string] $Path, $Payload)
    [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($Path)) | Out-Null
    $temporary = "$Path.$([Guid]::NewGuid().ToString('N')).tmp"
    try {
        [IO.File]::WriteAllText($temporary, ($Payload | ConvertTo-Json -Compress), [Text.UTF8Encoding]::new($false))
        if ([IO.File]::Exists($Path)) { [IO.File]::Replace($temporary, $Path, [NullString]::Value) }
        else { [IO.File]::Move($temporary, $Path) }
    } finally {
        if ([IO.File]::Exists($temporary)) { [IO.File]::Delete($temporary) }
    }
}

function Send-LocalAutomationLauncherFailure {
    param(
        [string] $StateRoot,
        [ValidateSet('LocalRuntimeUnavailable', 'StateDirectoryUnavailable', 'SourceFetchFailed',
                     'SourceRevisionInvalid', 'SourceSnapshotUnavailable', 'WorkerPreparationFailed',
                     'WorkerLaunchFailed')]
        [string] $ErrorType,
        [DateTimeOffset] $ObservedAt = [DateTimeOffset]::Now
    )
    $notificationRoot = Join-Path $StateRoot 'notifications'
    [IO.Directory]::CreateDirectory($notificationRoot) | Out-Null
    # The two launcher lanes share a queue lock; normal Python owns no launcher
    # events. Keep the event even when another dispatcher currently owns its lock.
    $stream = [IO.File]::Open((Join-Path $notificationRoot 'launcher.lock'),
        [IO.FileMode]::OpenOrCreate, [IO.FileAccess]::ReadWrite, [IO.FileShare]::ReadWrite)
    $owned = $false
    try {
        if ($stream.Length -eq 0) { $stream.WriteByte(0); $stream.Flush() }
        $stream.Lock(0, 1)
        $owned = $true
        $sourceKey = 'launcher:' + $ObservedAt.ToOffset([TimeSpan]::FromHours(9)).ToString('yyyy-MM-dd')
        $eventsRoot = Join-Path $notificationRoot 'events'
        [IO.Directory]::CreateDirectory($eventsRoot) | Out-Null
        $key = $null
        foreach ($file in Get-ChildItem -LiteralPath $eventsRoot -Filter '*.json' -File) {
            $existing = Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json
            if ($existing.kind -eq 'failure' -and $existing.stage -eq 'launcher' -and
                $existing.source_key -eq $sourceKey -and $existing.error_type -eq $ErrorType) {
                $key = $file.BaseName
                break
            }
        }
        if (-not $key) {
            # Alphabetical fields and ASCII values match Python's canonical hash.
            $event = [ordered]@{ error_type = $ErrorType; finished_at = $ObservedAt.ToString('o');
                kind = 'failure'; schema = 'tradingagents.local-notification/v1';
                source_key = $sourceKey; stage = 'launcher' }
            $sha = [Security.Cryptography.SHA256]::Create()
            try {
                $bytes = [Text.Encoding]::UTF8.GetBytes(($event | ConvertTo-Json -Compress))
                $key = ([BitConverter]::ToString($sha.ComputeHash($bytes))).Replace('-', '').ToLowerInvariant()
            } finally { $sha.Dispose() }
            Write-LocalLauncherJson (Join-Path $eventsRoot "$key.json") $event
        }
        if ($key -notmatch '^[0-9a-f]{64}$') { throw 'Invalid launcher event identity.' }
        $stream.Unlock(0, 1)
        $owned = $false
        $stream.Dispose()
        # Same byte-range lock as atomic_io.interprocess_file_lock on Windows.
        $stream = [IO.File]::Open((Join-Path $notificationRoot 'dispatch.lock'),
            [IO.FileMode]::OpenOrCreate, [IO.FileAccess]::ReadWrite, [IO.FileShare]::ReadWrite)
        if ($stream.Length -eq 0) { $stream.WriteByte(0); $stream.Flush() }
        try { $stream.Lock(0, 1) } catch [IO.IOException] { return }
        $owned = $true
        $receiptPath = Join-Path $notificationRoot "dispatches\$key.json"
        if ((Test-Path -LiteralPath $receiptPath) -or
            (Test-Path -LiteralPath (Join-Path $notificationRoot "results\$key.json"))) { return }
        # Reserve exactly one attempt before contacting GitHub. The normal Python
        # reconciler owns any remaining retry budget after the runtime recovers.
        $receipt = [ordered]@{ status = 'DISPATCHING'; attempts = 1;
            dispatched_at = $ObservedAt.ToString('o') }
        Write-LocalLauncherJson $receiptPath $receipt
        $process = [Diagnostics.Process]::new()
        try {
            $process.StartInfo.FileName = 'gh'
            $process.StartInfo.Arguments = "workflow run tradingagents-mobile-notifications.yml --repo nornen0202/TradingAgents --ref main -f local_event_id=$key"
            $process.StartInfo.UseShellExecute = $false
            $process.StartInfo.CreateNoWindow = $true
            $process.StartInfo.RedirectStandardOutput = $true
            $process.StartInfo.RedirectStandardError = $true
            if (-not $process.Start()) { throw 'Launcher notification dispatch could not start.' }
            $stdout = $process.StandardOutput.ReadToEndAsync()
            $stderr = $process.StandardError.ReadToEndAsync()
            if (-not $process.WaitForExit(30000)) {
                $process.Kill()
                $receipt.status = 'DISPATCH_UNKNOWN'
            } else {
                $receipt.status = if ($process.ExitCode -eq 0) { 'DISPATCH_ACCEPTED' } else { 'DISPATCH_FAILED' }
            }
        } catch {
            $receipt.status = 'DISPATCH_FAILED'
        } finally { $process.Dispose() }
        Write-LocalLauncherJson $receiptPath $receipt
    } finally {
        if ($owned) { $stream.Unlock(0, 1) }
        $stream.Dispose()
    }
}
