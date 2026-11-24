[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string] $RepositoryRoot = 'C:\Projects\TradingAgents',
    [string] $ArchiveRoot = 'C:\TradingAgentsData\archive',
    [string] $InstallRoot = 'C:\TradingAgentsMaintenance',
    [switch] $EnableExecutionRefresh
)

$ErrorActionPreference = 'Stop'
if (-not $EnableExecutionRefresh) { throw 'Explicit -EnableExecutionRefresh is required.' }
$name = 'LocalAutomation-refresh-kis'
$path = '\TradingAgents\'
if (-not $PSCmdlet.ShouldProcess($name, 'Enable the independent execution data producer')) { return }

$launcher = Join-Path $InstallRoot 'run_powershell_hidden.vbs'
$entrypoint = Join-Path $InstallRoot 'run_local_automation.ps1'
if (-not (Test-Path -LiteralPath $launcher -PathType Leaf) -or
    -not (Select-String -LiteralPath $entrypoint -Quiet -Pattern '"refresh-kis"')) {
    throw 'Install the deployed local launcher before enabling the refresh task.'
}

$state = Join-Path $RepositoryRoot '.runtime\local-automation'
$marker = Join-Path $state 'execution-refresh-enabled.json'
$arguments = "//B //Nologo `"$launcher`" `"$entrypoint`" -Command refresh-kis -RepositoryRoot `"$RepositoryRoot`" -ArchiveRoot `"$ArchiveRoot`""
$task = Get-ScheduledTask -TaskPath $path -TaskName $name -ErrorAction SilentlyContinue
if ($task -and ($task.Actions.Count -ne 1 -or $task.Actions.Arguments -cne $arguments -or
               $task.Settings.MultipleInstances -ne 2)) {
    throw 'Existing task differs from the execution producer definition.'
}

# Hold the old and new byte-range locks while changing ownership. An already
# running legacy overlay must finish before a second quote producer can start.
$locks = [System.Collections.Generic.List[System.IO.FileStream]]::new()
try {
    foreach ($lockName in 'run-due.lock', 'execution-refresh.lock') {
        $stream = [IO.File]::Open((Join-Path $state $lockName), 'OpenOrCreate', 'ReadWrite', 'ReadWrite')
        $locks.Add($stream)
        try { $stream.Lock(0, 1) } catch [IO.IOException] { throw 'An existing quote producer is active. Retry after it completes.' }
    }
    if (Test-Path -LiteralPath $marker) {
        $prior = Get-Content -LiteralPath $marker -Raw | ConvertFrom-Json
        if ($prior.mode -cne 'KIS_EXECUTION_REFRESH_V1' -or $prior.real_orders_enabled -ne $false) {
            throw 'Existing execution producer marker is invalid.'
        }
    } else {
        $prior = [pscustomobject]@{ mode = 'KIS_EXECUTION_REFRESH_V1'; enabled = $false; real_orders_enabled = $false }
    }
    if (-not $task) {
        $identity = [Security.Principal.WindowsIdentity]::GetCurrent().Name
        $principal = New-ScheduledTaskPrincipal -UserId $identity -LogonType Interactive -RunLevel Limited
        $action = New-ScheduledTaskAction -Execute (Join-Path $env:SystemRoot 'System32\wscript.exe') -Argument $arguments
        $timer = New-ScheduledTaskTrigger -Once -At ([DateTime]::Now.AddMinutes(1)) -RepetitionInterval (New-TimeSpan -Minutes 1)
        $settings = New-ScheduledTaskSettingsSet -Priority 4 -MultipleInstances IgnoreNew -StartWhenAvailable `
            -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -Hidden -ExecutionTimeLimit (New-TimeSpan -Minutes 10)
        Register-ScheduledTask -TaskPath $path -TaskName $name -Action $action -Trigger $timer `
            -Principal $principal -Settings $settings | Out-Null
    } elseif (-not $task.Settings.Enabled) {
        Enable-ScheduledTask -TaskPath $path -TaskName $name | Out-Null
    }
    $prior.enabled = $true
    $temporary = "$marker.$([Guid]::NewGuid().ToString('N')).tmp"
    try {
        $prior | ConvertTo-Json | Set-Content -LiteralPath $temporary -Encoding UTF8
        if ([IO.File]::Exists($marker)) { [IO.File]::Replace($temporary, $marker, [NullString]::Value) }
        else { [IO.File]::Move($temporary, $marker) }
    } finally { [IO.File]::Delete($temporary) }
} finally {
    foreach ($stream in $locks) { $stream.Dispose() }
}
Start-ScheduledTask -TaskPath $path -TaskName $name
