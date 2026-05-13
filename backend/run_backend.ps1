param(
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"
$BackendDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $BackendDir

if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "已根据 .env.example 创建 backend/.env，请先填写数据库密码和 MIMO_API_KEY 后重新运行。" -ForegroundColor Yellow
        exit 1
    }

    Write-Host "缺少 backend/.env，请先创建后再运行。" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "正在创建后端虚拟环境 venv..."
    py -3 -m venv venv
}

$Python = Join-Path $BackendDir "venv\Scripts\python.exe"
$Pip = Join-Path $BackendDir "venv\Scripts\pip.exe"

Write-Host "正在安装/检查后端依赖..."
& $Pip install -r requirements.txt

Write-Host "正在检查数据库连接..."
& $Python -c "from database import test_connection; test_connection()"

Write-Host "启动 FastAPI 后端：http://127.0.0.1:$Port"
& $Python -m uvicorn main:app --host 127.0.0.1 --port $Port --reload
