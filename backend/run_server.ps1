# PowerShell script to setup environment and run the Second-hand Market Backend
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Second-hand Market Backend - Smart Start Script" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# 1. Check for Python
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and try again." -ForegroundColor Yellow
    exit 1
}

# 2. Setup Virtual Environment if missing
if (!(Test-Path ".\venv")) {
    Write-Host "[1/4] Creating virtual environment..." -ForegroundColor Green
    python -m venv venv
}

# 3. Activate and Install Dependencies
Write-Host "[2/4] Activating environment and checking dependencies..." -ForegroundColor Green
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    . .\venv\Scripts\Activate.ps1
} else {
    . ./venv/bin/activate
}

# Check if we need to install/update requirements
# We'll always try to install to ensure everything is there on a new machine
pip install --upgrade pip
pip install -r requirements.txt

# 4. Check for .env file
if (!(Test-Path ".env")) {
    Write-Host "[3/4] Creating default .env file..." -ForegroundColor Yellow
    $envContent = @"
PROJECT_NAME="Second Hand Market API"
DATABASE_URL="sqlite:///./sql_app.db"
SECRET_KEY="$( [System.Guid]::NewGuid().ToString() )"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=["*"]
UPLOAD_DIR="static/uploads"
"@
    $envContent | Out-File -FilePath ".env" -Encoding utf8
}

# 5. Initialize Database/Admin if needed
if (!(Test-Path "sql_app.db")) {
    Write-Host "[4/4] Initializing database and admin account..." -ForegroundColor Green
    python init_admin.py
}

Write-Host "-----------------------------------------------" -ForegroundColor Cyan
Write-Host "Backend is ready! Starting server on http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "-----------------------------------------------" -ForegroundColor Cyan

$env:PYTHONPATH = "."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
