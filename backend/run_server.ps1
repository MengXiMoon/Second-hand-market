# PowerShell script to run the Second-hand Market Backend
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "Starting Second-hand Market Backend API..." -ForegroundColor Cyan

# Always run from this script directory so relative paths are stable.
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

function Test-PythonCommand {
    param([string]$cmd)

    try {
        if ($cmd -eq "python") {
            & python --version *> $null
        } else {
            if (-not (Test-Path $cmd)) {
                return $false
            }
            & $cmd --version *> $null
        }
        return ($LASTEXITCODE -eq 0)
    } catch {
        return $false
    }
}

$pythonCandidates = @(
    (Join-Path $scriptDir "venv\Scripts\python.exe"),
    (Join-Path $scriptDir ".venv\Scripts\python.exe"),
    (Join-Path (Split-Path $scriptDir -Parent) "venv\Scripts\python.exe"),
    (Join-Path (Split-Path $scriptDir -Parent) ".venv\Scripts\python.exe"),
    "python"
)

$pythonCmd = $null
foreach ($candidate in $pythonCandidates) {
    if (Test-PythonCommand $candidate) {
        $pythonCmd = $candidate
        break
    }
}

if (-not $pythonCmd) {
    throw "No valid Python interpreter found. Please create a venv and install dependencies."
}

Write-Host ("Using Python: " + $pythonCmd) -ForegroundColor Green

# Keep app import path stable
$env:PYTHONPATH = $scriptDir

# Use `python -m uvicorn` to avoid broken launcher paths in copied virtual envs.
& $pythonCmd -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
