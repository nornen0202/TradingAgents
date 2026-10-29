[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string] $RepositoryRoot = "C:\Projects\TradingAgents",
    [string] $ArchiveRoot = "C:\TradingAgentsData\archive",
    [string] $InstallRoot = "C:\TradingAgentsMaintenance",
    [ValidateRange(1024, 65535)][int] $ReviewPort = 8766,
    [switch] $NoStart
)
$ErrorActionPreference = 'Stop'
$stateRoot = Join-Path $RepositoryRoot '.runtime\local-automation'
if ($PSCmdlet.ShouldProcess($stateRoot, 'Enable persistent local-only paper simulation and private read-only review')) {
    & (Join-Path $PSScriptRoot 'install_local_automation.ps1') -RepositoryRoot $RepositoryRoot -ArchiveRoot $ArchiveRoot -InstallRoot $InstallRoot -UpdateScriptsOnly
    $paperState = Join-Path $stateRoot 'paper'
    [IO.Directory]::CreateDirectory($paperState) | Out-Null
    $enabledPath = Join-Path $paperState 'enabled.json'
    if (-not (Test-Path -LiteralPath $enabledPath)) {
        @{ mode='LOCAL_PAPER_ONLY'; enabled=$true; created_at=[DateTimeOffset]::Now.ToString('o'); real_orders_enabled=$false } |
            ConvertTo-Json | Set-Content -LiteralPath $enabledPath -Encoding utf8
    } else {
        $existing = Get-Content -LiteralPath $enabledPath -Raw | ConvertFrom-Json
        if ($existing.mode -ne 'LOCAL_PAPER_ONLY' -or $existing.real_orders_enabled -ne $false) { throw 'Existing paper configuration is invalid.' }
    }
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent().Name
    $principal = New-ScheduledTaskPrincipal -UserId $identity -LogonType Interactive -RunLevel Limited
    foreach ($command in @('paper', 'review')) {
        $name = "LocalAutomation-$command"
        $launcher = Join-Path $InstallRoot 'run_powershell_hidden.vbs'
        $script = Join-Path $InstallRoot 'run_local_automation.ps1'
        $arguments = "//B //Nologo `"$launcher`" `"$script`" -Command $command -RepositoryRoot `"$RepositoryRoot`" -ArchiveRoot `"$ArchiveRoot`""
        if ($command -eq 'review') { $arguments += " -ReviewPort $ReviewPort" }
        $action = New-ScheduledTaskAction -Execute (Join-Path $env:SystemRoot 'System32\wscript.exe') -Argument $arguments
        $minutes = if ($command -eq 'paper') { 1 } else { 15 }
        $periodic = New-ScheduledTaskTrigger -Once -At ([DateTime]::Now.AddSeconds(30)) -RepetitionInterval (New-TimeSpan -Minutes $minutes)
        $logon = New-ScheduledTaskTrigger -AtLogOn -User $identity
        $logon.Delay = 'PT30S'
        $settings = New-ScheduledTaskSettingsSet -Priority 4 -MultipleInstances IgnoreNew -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -Hidden `
            -ExecutionTimeLimit $(if ($command -eq 'paper') { New-TimeSpan -Minutes 10 } else { [TimeSpan]::Zero }) `
            -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
        Register-ScheduledTask -TaskPath '\TradingAgents\' -TaskName $name -Action $action -Trigger @($periodic,$logon) -Principal $principal -Settings $settings -Force | Out-Null
        if (-not $NoStart) { Start-ScheduledTask -TaskPath '\TradingAgents\' -TaskName $name }
    }
    Write-Output "Local paper simulation enabled. Private review: http://127.0.0.1:$ReviewPort (this PC only). Real order routing remains disabled."
}
