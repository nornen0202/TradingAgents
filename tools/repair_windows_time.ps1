#Requires -RunAsAdministrator
# Run once in an elevated PowerShell. No trading settings or clocks in stored
# market evidence are rewritten. Windows disciplines the real system clock.
[CmdletBinding(SupportsShouldProcess)]
param()
$ErrorActionPreference = 'Stop'
if ($PSCmdlet.ShouldProcess('Windows Time', 'Enable persistent NTP synchronization')) {
    if ((Get-CimInstance -ClassName Win32_ComputerSystem).PartOfDomain) {
        throw 'This PC is domain managed. Ask the domain administrator to repair its time source.'
    }
    Set-Service -Name W32Time -StartupType Automatic
    Start-Service -Name W32Time
    & w32tm /config '/manualpeerlist:time.windows.com,0x9 time.cloudflare.com,0x9' /syncfromflags:manual /update
    if ($LASTEXITCODE -ne 0) { throw 'Windows Time configuration failed.' }
    Set-ItemProperty -LiteralPath 'HKLM:\SYSTEM\CurrentControlSet\Services\W32Time\TimeProviders\NtpClient' -Name SpecialPollInterval -Value 300
    Restart-Service -Name W32Time
    & w32tm /resync /rediscover
    if ($LASTEXITCODE -ne 0) { throw 'Windows Time synchronization failed; check network/domain policy.' }
    & w32tm /query /status
    & w32tm /stripchart /computer:time.windows.com /samples:5 /dataonly
    Write-Output 'Verify a synchronized external source and measured offset before declaring recovery.'
}
