# M2 end-to-end verification — unit tests + all four event types
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$env:PYTHONPATH = "src"

Write-Host "=== 1/2 Unit tests ===" -ForegroundColor Cyan
powershell -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "run_tests.ps1")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "=== 2/2 Collector pipeline — all 4 event types (sample docs + real BP) ===" -ForegroundColor Cyan
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { $python = "python" }
& $python (Join-Path $PSScriptRoot "e2e_collector_all_events.py")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "M2 E2E complete. For live Xero webhook, configure OAuth + ngrok then create documents in Xero." -ForegroundColor Green
