[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string] $RepositoryRoot = "C:\Projects\TradingAgents",
    [string] $ArchiveRoot = "C:\TradingAgentsData\archive",
    [string] $InstallRoot = "C:\TradingAgentsMaintenance",
    [switch] $UpdateScriptsOnly,
    [switch] $NoStart
)
$ErrorActionPreference = "Stop"
$installedScript = Join-Path $InstallRoot "run_local_automation.ps1"
if ($PSCmdlet.ShouldProcess($installedScript, "Install independent local analysis and publication tasks")) {
    [IO.Directory]::CreateDirectory($InstallRoot) | Out-Null
    # Install the backward-compatible helper first, then atomically replace the
    # entrypoint. Running workers keep their already loaded script and source.
    foreach ($filename in @('local_automation_launcher_notifications.ps1', 'run_local_automation.ps1')) {
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
        $arguments = "-NoLogo -NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$installedScript`" -Command $command -RepositoryRoot `"$RepositoryRoot`" -ArchiveRoot `"$ArchiveRoot`""
        $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $arguments
        $trigger = New-ScheduledTaskTrigger -Once -At ([DateTime]::Now.AddMinutes(1)) -RepetitionInterval (New-TimeSpan -Minutes 5)
        $logon = New-ScheduledTaskTrigger -AtLogOn -User $identity
        $settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -Hidden -ExecutionTimeLimit (New-TimeSpan -Hours 13)
        Register-ScheduledTask -TaskPath "\TradingAgents\" -TaskName $name -Action $action -Trigger @($trigger, $logon) -Principal $principal -Settings $settings -Force | Out-Null
        if (-not $NoStart) { Start-ScheduledTask -TaskPath "\TradingAgents\" -TaskName $name }
    }
}
