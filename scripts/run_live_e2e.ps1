# Live E2E — OAuth check + create test invoice (webhook -> branchlesspay.com)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
. (Join-Path $PSScriptRoot "load_dotenv.ps1")

Write-Host "=== Xero live E2E (production webhook) ===" -ForegroundColor Cyan
Write-Host ""

$required = @(
    "XERO_CLIENT_ID",
    "XERO_CLIENT_SECRET",
    "XERO_ACCESS_TOKEN",
    "XERO_REFRESH_TOKEN",
    "XERO_TENANT_ID",
    "XERO_WEBHOOK_KEY",
    "BP_LICENSE_KEY"
)
$missing = @()
foreach ($key in $required) {
    if (-not (Get-Item -Path "Env:$key" -ErrorAction SilentlyContinue) -or -not (Get-Item "Env:$key").Value) {
        $missing += $key
    }
}

if ($missing.Count -gt 0) {
    Write-Host "Missing in .env:" -ForegroundColor Yellow
    $missing | ForEach-Object { Write-Host "  - $_" }
    Write-Host ""
    if ($missing -contains "XERO_CLIENT_ID" -or $missing -contains "XERO_CLIENT_SECRET") {
        Write-Host "1. Add XERO_CLIENT_ID + XERO_CLIENT_SECRET from https://developer.xero.com/app/manage" -ForegroundColor Yellow
    }
    if ($missing -match "^XERO_(ACCESS|REFRESH|TENANT)") {
        Write-Host "2. Run: powershell -ExecutionPolicy Bypass -File scripts\oauth_setup.ps1" -ForegroundColor Yellow
    }
    exit 1
}

Write-Host "Org: $($env:XERO_ORG_NAME) ($($env:XERO_TENANT_ID))" -ForegroundColor Green
Write-Host "Webhook: https://branchlesspay.com/api/v1/webhook/xero (intent OK required)" -ForegroundColor Green
Write-Host ""

Write-Host "Pre-flight:" -ForegroundColor Cyan
Write-Host "  [ ] Xero app webhooks subscribed: INVOICE CREATE (and UPDATE if testing updates)"
Write-Host "  [ ] Demo org connected to this Xero app"
Write-Host ""

$confirm = Read-Host "Create test invoice now? (y/n)"
if ($confirm -ne "y") { exit 0 }

$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { $python = "python" }

& $python (Join-Path $PSScriptRoot "live_create_test_invoice.py")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "If webhook delivery shows 202 in Xero portal, anchor succeeded." -ForegroundColor Green
Write-Host "Optional — poll anchor status (paste anchor_id from BP logs):" -ForegroundColor Cyan
$anchorId = Read-Host "anchor_id (or Enter to skip)"
if ($anchorId) {
    $headers = @{ Authorization = "Bearer $($env:BP_LICENSE_KEY)"; Accept = "application/json" }
    try {
        $r = Invoke-RestMethod -Uri "https://branchlesspay.com/api/v1/anchor/$anchorId" -Headers $headers
        $r | ConvertTo-Json -Depth 6
        Write-Host "Verify: https://branchlesspay.com/verify/$anchorId" -ForegroundColor Green
    } catch {
        Write-Host "GET anchor failed: $_" -ForegroundColor Red
    }
}
