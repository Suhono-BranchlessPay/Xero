# Validate M3+M4 — display tests
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location (Join-Path $root "display")
Write-Host "=== Display unit tests ===" -ForegroundColor Cyan
npm test
Write-Host ""
Write-Host "M3+M4 validation complete." -ForegroundColor Green
