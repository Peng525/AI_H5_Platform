# 在 Windows 上释放/绕过 8080 端口保留，并以宿主 8080 启动 Docker Compose
# 必须以管理员身份运行 PowerShell：
#   cd develop
#   .\scripts\setup-host-port-8080.ps1

#Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

function Show-ExcludedRanges {
    Write-Host "== TCP 保留端口 ==" -ForegroundColor Cyan
    netsh interface ipv4 show excludedportrange protocol=tcp
}

function Test-Port8080Excluded {
    $text = netsh interface ipv4 show excludedportrange protocol=tcp | Out-String
    foreach ($line in ($text -split "`n")) {
        if ($line -notmatch '^\s*(\d+)\s+(\d+)') { continue }
        $start = [int]$Matches[1]
        $end = [int]$Matches[2]
        if (8080 -ge $start -and 8080 -le $end) { return $true }
    }
    return $false
}

Show-ExcludedRanges
if (Test-Port8080Excluded) {
    Write-Host "8080 落在 Hyper-V/WSL 保留段内。将先停止 WinNAT，再启动 Docker，绑定成功后再启动 WinNAT。" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "== 停止 WinNAT（释放保留段） ==" -ForegroundColor Cyan
net stop winnat
if ($LASTEXITCODE -ne 0) {
    Write-Error "无法停止 winnat（需管理员）。请以管理员运行本脚本。"
}

Write-Host ""
Write-Host "== 启动 Docker (宿主机 8080) ==" -ForegroundColor Cyan
Remove-Item Env:APP_HOST_PORT -ErrorAction SilentlyContinue
docker compose down 2>$null
docker compose up -d --build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker 绑定 8080 失败。尝试缩小动态端口范围后重试..." -ForegroundColor Yellow
    netsh int ipv4 set dynamic tcp start=49152 num=16384
    if ($LASTEXITCODE -ne 0) { Write-Error "netsh 设置动态端口失败（需管理员）。" }
    net stop winnat
    net start winnat
    Show-ExcludedRanges
    docker compose up -d --build
    if ($LASTEXITCODE -ne 0) {
        net start winnat
        Write-Host "仍失败。请记录上方 excludedportrange，确认 8080 是否仍在保留段内，必要时重启电脑后再运行本脚本。" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "== 启动 WinNAT ==" -ForegroundColor Cyan
net start winnat
if ($LASTEXITCODE -ne 0) {
    Write-Warning "winnat 启动失败，但 Docker 可能已绑定 8080。请手动执行: net start winnat"
}

Start-Sleep -Seconds 2
try {
    $r = Invoke-WebRequest http://localhost:8080/ -UseBasicParsing -TimeoutSec 10
    Write-Host "OK http://localhost:8080/ -> $($r.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "Docker 已启动但无法访问 http://localhost:8080/ : $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "完成。若重启后 8080 再次被保留，请再次以管理员运行本脚本。" -ForegroundColor Green
