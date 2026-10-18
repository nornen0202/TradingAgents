[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string] $RepositoryRoot = "C:\Projects\TradingAgents",
    [string] $ArchiveRoot = "C:\TradingAgentsData\archive",
    [string] $InstallRoot = "C:\TradingAgentsMaintenance",
    [switch] $EnableDemoValidation,
    [switch] $NoStart
)
$ErrorActionPreference = 'Stop'
if (-not $EnableDemoValidation) { throw 'Explicit -EnableDemoValidation is required for bounded KIS mock-server validation.' }
$stateRoot = Join-Path $RepositoryRoot '.runtime\local-automation\kis-validation'
if ($PSCmdlet.ShouldProcess($stateRoot, 'Enable bounded KR/US KIS mock-server session validation')) {
    & (Join-Path $PSScriptRoot 'install_local_automation.ps1') -RepositoryRoot $RepositoryRoot -ArchiveRoot $ArchiveRoot -InstallRoot $InstallRoot -UpdateScriptsOnly
    [IO.Directory]::CreateDirectory($stateRoot) | Out-Null
    $enabledPath = Join-Path $stateRoot 'enabled.json'
    if (Test-Path -LiteralPath $enabledPath) {
        $existing = Get-Content -LiteralPath $enabledPath -Raw | ConvertFrom-Json
        if ($existing.mode -ne 'KIS_DEMO_SESSION_VALIDATION' -or $existing.real_orders_enabled -ne $false -or $existing.enabled -ne $true) {
            throw 'Existing validation configuration is disabled or invalid; it was preserved.'
        }
    } else {
        @{ mode='KIS_DEMO_SESSION_VALIDATION'; enabled=$true; created_at=[DateTimeOffset]::Now.ToString('o'); real_orders_enabled=$false } |
            ConvertTo-Json | Set-Content -LiteralPath $enabledPath -Encoding utf8
    }
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent().Name
    $principal = New-ScheduledTaskPrincipal -UserId $identity -LogonType Interactive -RunLevel Limited
    $launcher = Join-Path $InstallRoot 'run_powershell_hidden.vbs'
    $script = Join-Path $InstallRoot 'run_local_automation.ps1'
    $arguments = "//B //Nologo `"$launcher`" `"$script`" -Command validate-kis -RepositoryRoot `"$RepositoryRoot`" -ArchiveRoot `"$ArchiveRoot`""
    $action = New-ScheduledTaskAction -Execute (Join-Path $env:SystemRoot 'System32\wscript.exe') -Argument $arguments
    $periodic = New-ScheduledTaskTrigger -Once -At ([DateTime]::Now.AddSeconds(45)) -RepetitionInterval (New-TimeSpan -Minutes 1)
    $logon = New-ScheduledTaskTrigger -AtLogOn -User $identity
    $logon.Delay = 'PT45S'
    $settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -Hidden `
        -ExecutionTimeLimit (New-TimeSpan -Minutes 10) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
    Register-ScheduledTask -TaskPath '\TradingAgents\' -TaskName 'LocalAutomation-validate-kis' -Action $action -Trigger @($periodic,$logon) -Principal $principal -Settings $settings -Force | Out-Null
    if (-not $NoStart) { Start-ScheduledTask -TaskPath '\TradingAgents\' -TaskName 'LocalAutomation-validate-kis' }
    Write-Output 'KIS mock validation scheduled every minute; regular-session guards and finite campaign limits apply. Real order routing remains disabled.'
}
