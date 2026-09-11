[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$InstallRoot = "C:\TradingAgentsMaintenance",
    [string]$TaskPath = "\TradingAgents\",
    [string]$TaskName = "StorageMaintenance",
    [datetime]$DailyAt = ([datetime]::Today.AddHours(16).AddMinutes(30))
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$source = Join-Path $PSScriptRoot "maintain_project_storage.ps1"
if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
    throw "Maintenance script not found: $source"
}

$resolvedInstallRoot = [IO.Path]::GetFullPath($InstallRoot).TrimEnd([IO.Path]::DirectorySeparatorChar)
$installedScript = Join-Path $resolvedInstallRoot "maintain_project_storage.ps1"

if ($PSCmdlet.ShouldProcess($installedScript, "Install TradingAgents storage maintenance")) {
    [IO.Directory]::CreateDirectory($resolvedInstallRoot) | Out-Null
    Copy-Item -LiteralPath $source -Destination $installedScript -Force
}

$arguments = "-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File $installedScript -Apply"
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$author = [Security.SecurityElement]::Escape($identity.Name)
$sid = [Security.SecurityElement]::Escape($identity.User.Value)
$escapedArguments = [Security.SecurityElement]::Escape($arguments)
$startBoundary = $DailyAt.ToString("yyyy-MM-ddTHH:mm:ss")
$taskXml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Author>$author</Author>
    <Description>Keep TradingAgents archives and self-hosted runner artifacts within bounded retention.</Description>
  </RegistrationInfo>
  <Principals>
    <Principal id="Author">
      <UserId>$sid</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <DisallowStartIfOnBatteries>true</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>true</StopIfGoingOnBatteries>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <StartWhenAvailable>true</StartWhenAvailable>
    <ExecutionTimeLimit>PT2H</ExecutionTimeLimit>
  </Settings>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>$startBoundary</StartBoundary>
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

if ($PSCmdlet.ShouldProcess("$TaskPath$TaskName", "Register daily storage-maintenance task")) {
    Register-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName -Xml $taskXml -Force | Out-Null
}

Write-Output "INSTALLED script=$installedScript task=$TaskPath$TaskName daily_at=$($DailyAt.ToString('HH:mm'))"
