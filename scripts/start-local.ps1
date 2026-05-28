# 本地启动（不依赖 Docker Hub）
# 用法：在 develop 目录执行 .\scripts\start-local.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

Write-Host "== AI H5 Platform 本地启动 ==" -ForegroundColor Cyan

if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "已从 .env.example 创建 .env，请填写 LLM_RELAY_* 后重新运行" -ForegroundColor Yellow
}

# 加载 .env 到进程环境
Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
        [Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), 'Process')
    }
}

Write-Host "[1/2] 构建前端..."
Set-Location "$Root\frontend"
if (-not (Test-Path node_modules)) {
    npm config set registry https://registry.npmmirror.com
    npm install
}
npm run build

Write-Host "[2/2] 启动后端 http://localhost:8080 ..."
Set-Location "$Root\backend"
$env:PYTHONPATH = (Get-Location).Path
if (-not (Test-Path data)) { New-Item -ItemType Directory -Path data | Out-Null }

pip install -q -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
