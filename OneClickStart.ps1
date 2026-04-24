# Master Start Script for Second-hand Market System
Write-Host "===============================================" -ForegroundColor Magenta
Write-Host "Second-hand Market - ONE-CLICK START" -ForegroundColor Magenta
Write-Host "===============================================" -ForegroundColor Magenta

# 1. Check Requirements
$hasError = $false

if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[-] Python is missing. Please install Python 3.8+." -ForegroundColor Red
    $hasError = $true
}

if (!(Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "[-] Node.js/NPM is missing. Please install Node.js." -ForegroundColor Red
    $hasError = $true
}

if ($hasError) { exit 1 }

# 2. Frontend Setup
Write-Host "`n[1/3] Setting up Frontend..." -ForegroundColor Cyan
if (!(Test-Path "node_modules")) {
    Write-Host "Installing frontend dependencies (this may take a minute)..." -ForegroundColor Yellow
    npm install
}

# 3. Backend Setup & Start
Write-Host "`n[2/3] Starting Backend in a new window..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\run_server.ps1"

# 4. Frontend Start
Write-Host "`n[3/3] Starting Frontend..." -ForegroundColor Cyan
Write-Host "The application will be available at http://localhost:5173" -ForegroundColor Green
npm run dev
