# Quick .env validation (no secrets printed)
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "load_dotenv.ps1")

$envPath = Join-Path (Split-Path -Parent $PSScriptRoot) ".env"
Write-Host "Checking: $envPath" -ForegroundColor Cyan
Write-Host ""

$vars = Read-DotEnv -Path $envPath
$checks = @(
    "XERO_CLIENT_ID",
    "XERO_CLIENT_SECRET",
    "XERO_WEBHOOK_KEY",
    "BP_LICENSE_KEY",
    "XERO_REDIRECT_URI",
    "XERO_ACCESS_TOKEN",
    "XERO_TENANT_ID"
)

foreach ($name in $checks) {
    $val = [string]$vars[$name]
    if ($val) {
        Write-Host ("  OK   {0} (len={1})" -f $name, $val.Length) -ForegroundColor Green
    } else {
        Write-Host ("  MISS {0}" -f $name) -ForegroundColor Yellow
    }
}

Write-Host ""
if (-not $vars["XERO_CLIENT_ID"] -or -not $vars["XERO_CLIENT_SECRET"]) {
    Write-Host "Run: powershell -ExecutionPolicy Bypass -File scripts\set_xero_credentials.ps1" -ForegroundColor Yellow
}
