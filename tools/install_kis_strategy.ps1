[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string] $RepositoryRoot = "C:\Projects\TradingAgents",
    [string] $ArchiveRoot = "C:\TradingAgentsData\archive",
    [string] $InstallRoot = "C:\TradingAgentsMaintenance",
    [switch] $EnableDemoStrategy,
    [switch] $NoStart
)
$ErrorActionPreference = 'Stop'
if (-not $EnableDemoStrategy) { throw 'Explicit -EnableDemoStrategy is required for continuous KIS mock-server strategy execution after proven validation.' }
$stateRoot = Join-Path $RepositoryRoot '.runtime\local-automation\kis-strategy'
if ($PSCmdlet.ShouldProcess($stateRoot, 'Enable validation-gated KR/US KIS mock strategy execution')) {
    & (Join-Path $PSScriptRoot 'install_local_automation.ps1') -RepositoryRoot $RepositoryRoot -ArchiveRoot $ArchiveRoot -InstallRoot $InstallRoot -UpdateScriptsOnly
    [IO.Directory]::CreateDirectory($stateRoot) | Out-Null
    $enabledPath = Join-Path $stateRoot 'enabled.json'
    if (Test-Path -LiteralPath $enabledPath) {
        $existing = Get-Content -LiteralPath $enabledPath -Raw | ConvertFrom-Json
        if ($existing.mode -ne 'KIS_DEMO_STRATEGY' -or $existing.real_orders_enabled -ne $false -or $existing.enabled -ne $true) {
            throw 'Existing validation configuration is disabled or invalid; it was preserved.'
        }
    } else {
        @{ mode='KIS_DEMO_STRATEGY'; enabled=$true; created_at=[DateTimeOffset]::Now.ToString('o'); real_orders_enabled=$false } |
            ConvertTo-Json | Set-Content -LiteralPath $enabledPath -Encoding utf8
    }
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent().Name
    $principal = New-ScheduledTaskPrincipal -UserId $identity -LogonType Interactive -RunLevel Limited
    $launcher = Join-Path $InstallRoot 'run_powershell_hidden.vbs'
    $script = Join-Path $InstallRoot 'run_local_automation.ps1'
    $arguments = "//B //Nologo `"$launcher`" `"$script`" -Command strategy-kis -RepositoryRoot `"$RepositoryRoot`" -ArchiveRoot `"$ArchiveRoot`""
    $action = New-ScheduledTaskAction -Execute (Join-Path $env:SystemRoot 'System32\wscript.exe') -Argument $arguments
    $periodic = New-ScheduledTaskTrigger -Once -At ([DateTime]::Now.AddSeconds(45)) -RepetitionInterval (New-TimeSpan -Minutes 1)
    $logon = New-ScheduledTaskTrigger -AtLogOn -User $identity
    $logon.Delay = 'PT45S'
    $settings = New-ScheduledTaskSettingsSet -Priority 4 -MultipleInstances IgnoreNew -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -Hidden `
        -ExecutionTimeLimit (New-TimeSpan -Minutes 10) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
    Register-ScheduledTask -TaskPath '\TradingAgents\' -TaskName 'LocalAutomation-strategy-kis' -Action $action -Trigger @($periodic,$logon) -Principal $principal -Settings $settings -Force | Out-Null
    if (-not $NoStart) { Start-ScheduledTask -TaskPath '\TradingAgents\' -TaskName 'LocalAutomation-strategy-kis' }
    Write-Output 'KIS strategy worker scheduled every minute; each market waits for original broker validation proofs. Real orders remain disabled.'
}
