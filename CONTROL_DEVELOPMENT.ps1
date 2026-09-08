[CmdletBinding()]
param(
    [switch]$Status,
    [switch]$Plan,
    [switch]$Drive,
    [switch]$Overview,
    [switch]$CheckConsistency,
    [switch]$CloseRole,
    [switch]$CloseMission
)

$ErrorActionPreference = 'Stop'
$selected = @($Status, $Plan, $Drive, $Overview, $CheckConsistency, $CloseRole, $CloseMission) | Where-Object { $_ }
if ($selected.Count -ne 1) {
    Write-Error 'Exactly one control mode is required.'
    exit 2
}

$mode = if ($Overview) { 'overview' }
elseif ($CheckConsistency) { 'check-consistency' }
elseif ($Status) { 'status' }
elseif ($Plan) { 'plan' }
elseif ($Drive) { 'drive' }
elseif ($CloseRole) { 'close-role' }
else { 'close-mission' }

$python = Get-Command python -ErrorAction SilentlyContinue
if ($null -eq $python) {
    Write-Error 'Python 3 is required.'
    exit 3
}

$previousPythonPath = $env:PYTHONPATH
try {
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $env:PYTHONUTF8 = '1'
    $env:PYTHONPATH = Join-Path $PSScriptRoot 'scripts'
    & $python.Source -m harness.cli $mode --root $PSScriptRoot
    exit $LASTEXITCODE
}
finally {
    $env:PYTHONPATH = $previousPythonPath
}
