[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet('validate', 'status', 'close')]
    [string]$Mode,
    [Parameter(Mandatory = $true, Position = 1)]
    [string]$ExecutionPath
)
$ErrorActionPreference = 'Stop'
$python = Get-Command python -ErrorAction SilentlyContinue
if ($null -eq $python) { Write-Error 'Python 3 is required.'; exit 3 }
$previousPythonPath = $env:PYTHONPATH
try {
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $env:PYTHONUTF8 = '1'
    $env:PYTHONPATH = Join-Path $PSScriptRoot 'scripts'
    & $python.Source -m harness.work_cli $Mode $ExecutionPath
    exit $LASTEXITCODE
}
finally { $env:PYTHONPATH = $previousPythonPath }
