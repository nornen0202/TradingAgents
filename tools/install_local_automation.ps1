[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string] $RepositoryRoot = "C:\Projects\TradingAgents",
    [string] $ArchiveRoot = "C:\TradingAgentsData\archive",
    [string] $InstallRoot = "C:\TradingAgentsMaintenance",
    [ValidateSet(5, 10, 15, 20, 30, 60)][int] $PollIntervalMinutes = 15,
    [switch] $UpdateScriptsOnly,
    [switch] $NoStart
)
$ErrorActionPreference = "Stop"
$installedScript = Join-Path $InstallRoot "run_local_automation.ps1"
if ($PSCmdlet.ShouldProcess($installedScript, "Install independent local analysis and publication tasks")) {
    [IO.Directory]::CreateDirectory($InstallRoot) | Out-Null
    # Install the backward-compatible helper first, then atomically replace the
    # entrypoint. Running workers keep their already loaded script and source.
    foreach ($filename in @('run_powershell_hidden.vbs', 'local_automation_launcher_notifications.ps1', 'run_local_automation.ps1')) {
        $destination = Join-Path $InstallRoot $filename
        $temporary = "$destination.$([Guid]::NewGuid().ToString('N')).tmp"
        try {
            Copy-Item -LiteralPath (Join-Path $PSScriptRoot $filename) -Destination $temporary
            if ([IO.File]::Exists($destination)) { [IO.File]::Replace($temporary, $destination, [NullString]::Value) }
            else { [IO.File]::Move($temporary, $destination) }
        } finally {
            if ([IO.File]::Exists($temporary)) { [IO.File]::Delete($temporary) }
        }
    }
    if ($UpdateScriptsOnly) { return }
    $stateRoot = Join-Path $RepositoryRoot ".runtime\local-automation"
    [IO.Directory]::CreateDirectory($stateRoot) | Out-Null
    $legacyTasks = @(Get-ScheduledTask -TaskPath "\TradingAgents\" -ErrorAction SilentlyContinue | Where-Object {
        $_.TaskName -like "IntradayOverlay-*" -and $_.Actions.Arguments -match 'nornen0202/TradingAgents'
    })
    $legacyReceipt = Join-Path $stateRoot "legacy-dispatch-tasks.json"
    if (-not (Test-Path -LiteralPath $legacyReceipt)) {
        @($legacyTasks | Select-Object TaskName, TaskPath, State) | ConvertTo-Json | Set-Content -LiteralPath $legacyReceipt -Encoding UTF8
    }
    foreach ($task in $legacyTasks) { $task | Disable-ScheduledTask | Out-Null }
    @{ backend = "local"; installed_at = [DateTimeOffset]::Now.ToString("o") } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $stateRoot "enabled.json") -Encoding UTF8
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent().Name
    $principal = New-ScheduledTaskPrincipal -UserId $identity -LogonType Interactive -RunLevel Limited
    foreach ($command in @("run-due", "publish")) {
        $name = "LocalAutomation-$command"
        # Set the initial window state before PowerShell starts. Its own
        # -WindowStyle Hidden is applied after Windows can show a Terminal window.
        $hiddenLauncher = Join-Path $InstallRoot 'run_powershell_hidden.vbs'
        $arguments = "//B //Nologo `"$hiddenLauncher`" `"$installedScript`" -Command $command -RepositoryRoot `"$RepositoryRoot`" -ArchiveRoot `"$ArchiveRoot`""
        $action = New-ScheduledTaskAction -Execute (Join-Path $env:SystemRoot 'System32\wscript.exe') -Argument $arguments
        # Quarter-hour production ticks retain the 01:00/03:00 and
        # 10:30/13:30/14:30 overlay boundaries. Offset publishing to avoid
        # contending for the shared source-fetch lock on every idle tick.
        $offset = if ($command -eq 'publish') { 2 } else { 0 }
        $now = [DateTime]::Now
        $anchor = $now.Date.AddMinutes($offset)
        $nextTick = $anchor.AddMinutes(([Math]::Floor(($now - $anchor).TotalMinutes / $PollIntervalMinutes) + 1) * $PollIntervalMinutes)
        $trigger = New-ScheduledTaskTrigger -Once -At $nextTick -RepetitionInterval (New-TimeSpan -Minutes $PollIntervalMinutes)
        $logon = New-ScheduledTaskTrigger -AtLogOn -User $identity
        $logon.Delay = if ($command -eq 'publish') { 'PT2M' } else { 'PT30S' }
        $triggers = @($trigger, $logon)
        if ($command -eq 'run-due') {
            # The US full-research admission window opens at 17:50 KST,
            # between quarter hours. Preserve that boundary explicitly.
            $triggers += New-ScheduledTaskTrigger -Weekly -WeeksInterval 1 -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At ($now.Date.AddHours(17).AddMinutes(50))
        }
        $settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -Hidden -ExecutionTimeLimit (New-TimeSpan -Hours 13)
        Register-ScheduledTask -TaskPath "\TradingAgents\" -TaskName $name -Action $action -Trigger $triggers -Principal $principal -Settings $settings -Force | Out-Null
        if (-not $NoStart) { Start-ScheduledTask -TaskPath "\TradingAgents\" -TaskName $name }
    }
}
