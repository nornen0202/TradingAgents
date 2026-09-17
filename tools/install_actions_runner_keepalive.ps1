[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string] $RunnerRoot = "C:\actions-runner",
    [string] $InstallRoot = "C:\TradingAgentsMaintenance",
    [string] $TaskPath = "\TradingAgents\",
    [string] $TaskName = "GitHubActionsRunnerKeepAlive",
    [int] $IntervalMinutes = 5,
    [switch] $NoStart
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

if ($IntervalMinutes -lt 1 -or $IntervalMinutes -gt 60) {
    throw "IntervalMinutes must be between 1 and 60."
}

$source = Join-Path $PSScriptRoot "ensure_actions_runner.ps1"
if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
    throw "Runner keepalive script not found: $source"
}

$resolvedInstallRoot = [IO.Path]::GetFullPath($InstallRoot).TrimEnd(
    [IO.Path]::DirectorySeparatorChar,
    [IO.Path]::AltDirectorySeparatorChar
)
$resolvedRunnerRoot = [IO.Path]::GetFullPath($RunnerRoot).TrimEnd(
    [IO.Path]::DirectorySeparatorChar,
    [IO.Path]::AltDirectorySeparatorChar
)
$installedScript = Join-Path $resolvedInstallRoot "ensure_actions_runner.ps1"

if ($PSCmdlet.ShouldProcess($installedScript, "Install GitHub Actions runner keepalive")) {
    [IO.Directory]::CreateDirectory($resolvedInstallRoot) | Out-Null
    Copy-Item -LiteralPath $source -Destination $installedScript -Force
}

$arguments = (
    "-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass " +
    "-File `"$installedScript`" -RunnerRoot `"$resolvedRunnerRoot`""
)
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$author = [Security.SecurityElement]::Escape($identity.Name)
$sid = [Security.SecurityElement]::Escape($identity.User.Value)
$escapedArguments = [Security.SecurityElement]::Escape($arguments)
$startBoundary = [DateTime]::Now.AddMinutes(1).ToString("yyyy-MM-ddTHH:mm:ss")
$interval = "PT${IntervalMinutes}M"
$taskXml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Author>$author</Author>
    <Description>Keep the TradingAgents GitHub Actions runner alive when service execution is unavailable.</Description>
  </RegistrationInfo>
  <Principals>
    <Principal id="Author">
      <UserId>$sid</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <ExecutionTimeLimit>PT2M</ExecutionTimeLimit>
  </Settings>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
      <UserId>$sid</UserId>
      <Delay>PT30S</Delay>
    </LogonTrigger>
    <CalendarTrigger>
      <StartBoundary>$startBoundary</StartBoundary>
      <Enabled>true</Enabled>
      <Repetition>
        <Interval>$interval</Interval>
        <Duration>P1D</Duration>
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
      <ScheduleByDay><DaysInterval>1</DaysInterval></ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Actions Context="Author">
    <Exec>
      <Command>powershell.exe</Command>
      <Arguments>$escapedArguments</Arguments>
    </Exec>
  </Actions>
</Task>
"@

if ($PSCmdlet.ShouldProcess("$TaskPath$TaskName", "Register runner keepalive task")) {
    Register-ScheduledTask `
        -TaskPath $TaskPath `
        -TaskName $TaskName `
        -Xml $taskXml `
        -Force | Out-Null
    if (-not $NoStart) {
        Start-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName
    }
}

Write-Output (
    "INSTALLED script=$installedScript task=$TaskPath$TaskName " +
    "interval_minutes=$IntervalMinutes"
)
