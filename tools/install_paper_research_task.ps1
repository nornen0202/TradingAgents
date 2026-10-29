[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string] $RepositoryRoot = "C:\Projects\TradingAgents",
    [string] $ArchiveRoot = "C:\TradingAgentsData\archive",
    [string] $InstallRoot = "C:\TradingAgentsMaintenance",
    [switch] $NoStart
)
$ErrorActionPreference = 'Stop'
$installedScript = Join-Path $InstallRoot 'run_local_automation.ps1'
$hiddenLauncher = Join-Path $InstallRoot 'run_powershell_hidden.vbs'
if (-not (Test-Path -LiteralPath $installedScript) -or -not (Test-Path -LiteralPath $hiddenLauncher)) {
    throw 'Install the current local automation scripts before adding the research task.'
}
$name = 'LocalAutomation-research-kis'
if ($PSCmdlet.ShouldProcess($name, 'Register an independent paper strategy research task')) {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent().Name
    $principal = New-ScheduledTaskPrincipal -UserId $identity -LogonType Interactive -RunLevel Limited
    $arguments = "//B //Nologo `"$hiddenLauncher`" `"$installedScript`" -Command research-kis -RepositoryRoot `"$RepositoryRoot`" -ArchiveRoot `"$ArchiveRoot`""
    $action = New-ScheduledTaskAction -Execute (Join-Path $env:SystemRoot 'System32\wscript.exe') -Argument $arguments
    $trigger = New-ScheduledTaskTrigger -Once -At ([DateTime]::Now.AddMinutes(1)) -RepetitionInterval (New-TimeSpan -Minutes 5)
    # Research never queues behind itself or owns the quote/order worker locks.
    $settings = New-ScheduledTaskSettingsSet -Priority 4 -MultipleInstances IgnoreNew -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -Hidden -ExecutionTimeLimit (New-TimeSpan -Hours 13)
    Register-ScheduledTask -TaskPath '\TradingAgents\' -TaskName $name -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
    # Delegate daily full research only after the independent task exists.
    # Removing/disabling this marker restores the previous full-run dispatcher.
    $marker = Join-Path $RepositoryRoot '.runtime\local-automation\research-lane-enabled.json'
    [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($marker)) | Out-Null
    $temporary = "$marker.$([Guid]::NewGuid().ToString('N')).tmp"
    try {
        @{ mode = 'PAPER_RESEARCH_INDEPENDENT_V1'; enabled = $true; real_orders_enabled = $false;
           installed_at = [DateTimeOffset]::UtcNow.ToString('o') } | ConvertTo-Json |
            Set-Content -LiteralPath $temporary -Encoding UTF8
        if ([IO.File]::Exists($marker)) { [IO.File]::Replace($temporary, $marker, [NullString]::Value) }
        else { [IO.File]::Move($temporary, $marker) }
    } finally { if ([IO.File]::Exists($temporary)) { [IO.File]::Delete($temporary) } }
    if (-not $NoStart) { Start-ScheduledTask -TaskPath '\TradingAgents\' -TaskName $name }
}
