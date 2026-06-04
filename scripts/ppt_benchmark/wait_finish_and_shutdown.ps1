# 横评完成后归档 PPT、汇总评分并关机
# 用法（PowerShell 管理员非必须）:
#   Set-ExecutionPolicy -Scope Process Bypass
#   .\develop\scripts\ppt_benchmark\wait_finish_and_shutdown.ps1

$ErrorActionPreference = "Continue"
$Develop = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$Results = Join-Path $Develop "docs\ppt-master-benchmark\results"
$ExpectedRuns = 15   # 5 chat models x 3 types (gpt-image-2 为 SKIP)
$Log = Join-Path $Results "shutdown-watch.log"

function Write-Log($msg) {
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $msg"
    Add-Content -Path $Log -Value $line
    Write-Host $line
}

Write-Log "Watching for $ExpectedRuns phase1 result files..."

while ($true) {
    $done = @(Get-ChildItem $Results -Filter "*-phase1*.md" -ErrorAction SilentlyContinue).Count
    Write-Log "Results: $done / $($ExpectedRuns + 3) (incl. 3 SKIP)"
    if ($done -ge ($ExpectedRuns + 3)) { break }
    Start-Sleep -Seconds 120
}

Write-Log "Running finalize_and_archive..."
Set-Location $Develop
$env:HTTP_PROXY = ""
$env:HTTPS_PROXY = ""
python (Join-Path $Develop "scripts\ppt_benchmark\finalize_and_archive.py") 2>&1 | Tee-Object -Append $Log

Write-Log "Scheduling shutdown in 60 seconds..."
shutdown /s /t 60 /c "PPT横评已完成，PPT已保存至 results/pptx，60秒后关机"
Write-Log "Done."
