[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string] $RepositoryRoot = "C:\Projects\TradingAgents",
    [string] $ArchiveRoot = "C:\TradingAgentsData\archive",
    [string] $InstallRoot = "C:\TradingAgentsMaintenance",
    [switch] $NoStart
)
$ErrorActionPreference = "Stop"
$installedScript = Join-Path $InstallRoot "run_local_automation.ps1"
if ($PSCmdlet.ShouldProcess($installedScript, "Install independent local analysis and publication tasks")) {
    [IO.Directory]::CreateDirectory($InstallRoot) | Out-Null
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot "run_local_automation.ps1") -Destination $installedScript -Force
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
