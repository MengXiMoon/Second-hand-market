# PowerShell script to run the Second-hand Market Backend
Write-Host "Starting Second-hand Market Backend API..." -ForegroundColor Cyan

# Check if virtual environment exists
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    . .\venv\Scripts\Activate.ps1
} else {
    Write-Host "Warning: Virtual environment not found at .\venv" -ForegroundColor Yellow
}

# Set environment variables (optional if .env exists)
$env:PYTHONPATH = "."

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
