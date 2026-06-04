# PPT Master 首跑安装脚本（Windows）
# 用法：在 PowerShell 中执行
#   Set-ExecutionPolicy -Scope Process Bypass
#   .\develop\scripts\setup_ppt_master.ps1

$ErrorActionPreference = "Stop"
$H5Develop = Split-Path $PSScriptRoot -Parent
$Target = Join-Path $H5Develop "ppt-master-main"

Write-Host "==> Target: $Target"

if (-not (Test-Path (Join-Path $Target "requirements.txt"))) {
    Write-Host "ppt-master-main not found. Download ZIP from:"
    Write-Host "  https://atomgit.com/hugohe3/ppt-master"
    Write-Host "Or clone:"
    Write-Host "  git clone https://atomgit.com/hugohe3/ppt-master.git ppt-master-main"
    exit 1
}

Set-Location $Target
Write-Host "==> pip install (clear proxy if needed)"
$env:HTTP_PROXY = ""
$env:HTTPS_PROXY = ""
$env:ALL_PROXY = ""
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

Write-Host "==> Verify core deps"
python -c "import pptx; import fitz; print('All core dependencies OK')"

Write-Host ""
Write-Host "==> Verify env"
python (Join-Path $H5Develop "scripts\verify_ppt_env.py")
python (Join-Path $H5Develop "scripts\print_cursor_profile.py")

Write-Host ""
Write-Host "Skill: repo already includes skills/ppt-master/SKILL.md"
Write-Host "Optional: npx skills add hugohe3/ppt-master (requires Node.js)"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Cursor -> Open Folder -> $Target"
Write-Host "  2. Settings -> Models -> sync values from print_cursor_profile.py output"
Write-Host "  3. New Agent chat -> paste smoke test prompt from docs/AI-PPT生成指南.md"
