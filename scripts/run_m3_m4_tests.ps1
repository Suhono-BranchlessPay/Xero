# Validate M3+M4 — display tests + fixture preview
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location (Join-Path $root "display")
Write-Host "=== Display unit tests ===" -ForegroundColor Cyan
npm test
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host ""
Write-Host "=== Fixture preview ===" -ForegroundColor Cyan
node --experimental-strip-types scripts/preview_verify.mjs
Write-Host ""
Write-Host "M3+M4 validation complete." -ForegroundColor Green