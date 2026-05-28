# Copy Edge-downloaded BGM into backend/static/bgm for preview/share testing
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$destDir = Join-Path $root 'backend\media\bgm'
$destDirLegacy = Join-Path $root 'backend\static\bgm'
$destNamed = Join-Path $destDir 'happier-sakura-girl.mp3'
$destDemo = Join-Path $destDir 'demo-loop.mp3'
$edgeDir = 'E:\EdgeDownload'
$bgmDir = $destDirLegacy

$src = $null
$found = Get-ChildItem -Path $bgmDir -Filter '*.mp3' -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -notin @('happier-sakura-girl.mp3', 'demo-loop.mp3') } |
  Select-Object -First 1
if ($found) { $src = $found.FullName }
if (-not $src) {
  $found = Get-ChildItem -Path $edgeDir -Filter '*Happier*.mp3' -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($found) { $src = $found.FullName }
}
if (-not $src) {
  $found = Get-ChildItem -Path $edgeDir -Filter '*Sakura*.mp3' -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($found) { $src = $found.FullName }
}
if (-not $src) {
  $found = Get-ChildItem -Path $edgeDir -Filter '*.mp3' -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($found) { $src = $found.FullName }
}

if (-not $src) {
  Write-Host 'MP3 not found. Place file in backend/static/bgm/ or E:\EdgeDownload\, then re-run.' -ForegroundColor Yellow
  exit 1
}

New-Item -ItemType Directory -Force -Path $destDir | Out-Null
New-Item -ItemType Directory -Force -Path $destDirLegacy | Out-Null
Copy-Item -LiteralPath $src -Destination $destNamed -Force
Copy-Item -LiteralPath $src -Destination $destDemo -Force
Copy-Item -LiteralPath $src -Destination (Join-Path $destDirLegacy 'happier-sakura-girl.mp3') -Force
Copy-Item -LiteralPath $src -Destination (Join-Path $destDirLegacy 'demo-loop.mp3') -Force
Write-Host 'BGM installed:' -ForegroundColor Green
Write-Host "  $destNamed"
Write-Host "  $destDemo"
Write-Host 'Restart backend; tap the preview screen once to unlock audio playback.'
