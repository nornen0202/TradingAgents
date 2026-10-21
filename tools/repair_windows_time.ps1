#Requires -RunAsAdministrator
# Run once in an elevated PowerShell. No trading settings or clocks in stored
# market evidence are rewritten. Windows disciplines the real system clock.
[CmdletBinding(SupportsShouldProcess)]
param([switch] $StepClock)
$ErrorActionPreference = 'Stop'
function Get-VerifiedTimeOffset([string] $Server) {
    $samples = @(& w32tm /stripchart "/computer:$Server" /samples:5 /period:1 /dataonly 2>&1)
    if ($LASTEXITCODE -ne 0) { throw "NTP measurement failed: $Server" }
    $offsets = @($samples | ForEach-Object {
        if ([string]$_ -match '([+-]\d+\.\d+)s\s*$') {
            [double]::Parse($Matches[1], [Globalization.CultureInfo]::InvariantCulture)
        }
    })
    if ($offsets.Count -lt 3) { throw "Insufficient NTP samples: $Server" }
    $ordered = @($offsets | Sort-Object)
    return $ordered[[int][Math]::Floor($ordered.Count / 2)]
}
if ($PSCmdlet.ShouldProcess('Windows Time', 'Enable persistent NTP synchronization')) {
    if ((Get-CimInstance -ClassName Win32_ComputerSystem).PartOfDomain) {
        throw 'This PC is domain managed. Ask the domain administrator to repair its time source.'
    }
    Set-Service -Name W32Time -StartupType Automatic
    Start-Service -Name W32Time
    & w32tm /config '/manualpeerlist:time.cloudflare.com,0x9 time.windows.com,0xb' /syncfromflags:manual /update
    if ($LASTEXITCODE -ne 0) { throw 'Windows Time configuration failed.' }
    Set-ItemProperty -LiteralPath 'HKLM:\SYSTEM\CurrentControlSet\Services\W32Time\TimeProviders\NtpClient' -Name SpecialPollInterval -Value 300
    $configPath = 'HKLM:\SYSTEM\CurrentControlSet\Services\W32Time\Config'
    # 100 x 10ms = 1s. The workstation default was 360000 (one hour).
    Set-ItemProperty -LiteralPath $configPath -Name UpdateInterval -Value 100
    Set-ItemProperty -LiteralPath $configPath -Name MaxPollInterval -Value 9
    Restart-Service -Name W32Time
    $previousPhase = (Get-ItemProperty -LiteralPath $configPath -Name MaxAllowedPhaseOffset).MaxAllowedPhaseOffset
    try {
        if ($StepClock) {
            $primaryOffset = Get-VerifiedTimeOffset 'time.windows.com'
            $secondaryOffset = Get-VerifiedTimeOffset 'time.cloudflare.com'
            if ([Math]::Abs($primaryOffset - $secondaryOffset) -gt 0.2 -or
                [Math]::Abs($primaryOffset) -gt 5 -or [Math]::Abs($secondaryOffset) -gt 5) {
                throw 'NTP sources disagree or offset exceeds the bounded five-second repair.'
            }
            # Use Windows' own synchronized sample for the one-time clock step.
            # The original threshold is always restored, including on failure.
            Set-ItemProperty -LiteralPath $configPath -Name MaxAllowedPhaseOffset -Value 0
            & w32tm /config /update
            if ($LASTEXITCODE -ne 0) { throw 'Clock step configuration failed.' }
        }
        & w32tm /resync /rediscover
        if ($LASTEXITCODE -ne 0) { throw 'Windows Time synchronization failed; check network/domain policy.' }
        Start-Sleep -Seconds 3
    } finally {
        if ($StepClock) {
            Set-ItemProperty -LiteralPath $configPath -Name MaxAllowedPhaseOffset -Value $previousPhase
            & w32tm /config /update
            if ($LASTEXITCODE -ne 0) { throw 'Restore of the original clock-step threshold failed.' }
        }
    }
    # A clock step can invalidate the previous association. Establish a fresh
    # synchronized association after restoring normal correction behaviour.
    & w32tm /resync /rediscover
    if ($LASTEXITCODE -ne 0) { throw 'Final Windows Time synchronization failed.' }
    Start-Sleep -Seconds 3
    $timeStatus = @(& w32tm /query /status)
    $timeStatus | Write-Output
    $primaryOffset = Get-VerifiedTimeOffset 'time.windows.com'
    $secondaryOffset = Get-VerifiedTimeOffset 'time.cloudflare.com'
    Write-Output "Measured offsets: Windows=$primaryOffset seconds; Cloudflare=$secondaryOffset seconds."
    if ([Math]::Abs($primaryOffset) -gt 0.1 -or [Math]::Abs($secondaryOffset) -gt 0.1) {
        throw 'Clock error still exceeds 100ms. Run this script with -StepClock for bounded immediate repair.'
    }
    # W32Time labels are localized. Its first status row is always the numeric
    # leap indicator: 3 means unsynchronized, even if stripchart looks accurate.
    $firstStatusLine = @($timeStatus | Where-Object { [string]$_ -match '\S' })[0]
    if ([string]$firstStatusLine -notmatch '^[^:]+:\s*0\s*\(') {
        throw 'Measured clock is accurate, but Windows Time is not synchronized. Retry without -StepClock.'
    }
    Write-Output 'External clock accuracy verified within 100ms. Confirm the next normal trading observation as well.'
}
