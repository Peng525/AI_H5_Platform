@echo off
REM 双击或在普通 CMD 中运行；会自动请求管理员权限并释放 8080 后启动 Docker
net session >nul 2>&1
if %errorLevel% neq 0 (
    powershell -NoProfile -Command "Start-Process powershell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"%~dp0setup-host-port-8080.ps1\"' -Verb RunAs"
    exit /b
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup-host-port-8080.ps1"
