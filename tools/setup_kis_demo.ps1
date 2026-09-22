$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonWindow = Join-Path $projectRoot '.venv\Scripts\pythonw.exe'
if (-not (Test-Path -LiteralPath $pythonWindow)) {
    throw 'Project Python is missing. Run the project setup first.'
}
$setupScript = Join-Path $PSScriptRoot 'setup_kis_demo.py'
Start-Process -FilePath $pythonWindow -ArgumentList @(('"{0}"' -f $setupScript)) -WorkingDirectory $projectRoot -WindowStyle Hidden
