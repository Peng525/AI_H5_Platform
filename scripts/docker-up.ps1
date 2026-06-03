# Docker 启动（develop 目录执行：.\scripts\docker-up.ps1）
# 未设置 APP_HOST_PORT 时默认 8080

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

if (-not $env:APP_HOST_PORT) {
    $env:APP_HOST_PORT = "8080"
}

$port = $env:APP_HOST_PORT
Write-Host "== docker compose up (http://localhost:$port) ==" -ForegroundColor Cyan
docker compose up -d --build @args
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "访问 http://localhost:$port" -ForegroundColor Green