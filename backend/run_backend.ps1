param(
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"
$BackendDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $BackendDir

if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "Created backend/.env from .env.example. Please fill DB settings and MIMO_API_KEY, then run again." -ForegroundColor Yellow
        exit 1
    }

    Write-Host "Missing backend/.env. Please create it before running backend." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "Creating backend virtual environment: venv..."
    py -3 -m venv venv
}

$Python = Join-Path $BackendDir "venv\Scripts\python.exe"
$Pip = Join-Path $BackendDir "venv\Scripts\pip.exe"

Write-Host "Installing/checking backend dependencies..."
& $Pip install -r requirements.txt

Write-Host "Checking database connection..."
& $Python -c "from database import test_connection; test_connection()"

Write-Host "Starting FastAPI backend: http://127.0.0.1:$Port"
& $Python -m uvicorn main:app --host 127.0.0.1 --port $Port --reload