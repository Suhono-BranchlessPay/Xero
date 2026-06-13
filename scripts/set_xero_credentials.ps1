# Paste Xero Client ID + Secret into .env (interactive)
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "load_dotenv.ps1")

$envPath = Join-Path (Split-Path -Parent $PSScriptRoot) ".env"
if (-not (Test-Path -LiteralPath $envPath)) {
    Copy-Item (Join-Path (Split-Path -Parent $PSScriptRoot) ".env.example") $envPath
}

Write-Host ""
Write-Host "=== Set Xero OAuth credentials ===" -ForegroundColor Cyan
Write-Host "File: $envPath"
Write-Host ""
Write-Host "Get values from: https://developer.xero.com/app/manage"
Write-Host "  -> your app -> Configuration -> Client ID + Client Secret"
Write-Host ""

$clientId = Read-Host "Paste XERO_CLIENT_ID (UUID format)"
$clientSecret = Read-Host "Paste XERO_CLIENT_SECRET" -AsSecureString
$secretPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($clientSecret)
)

$clientId = $clientId.Trim()
$secretPlain = $secretPlain.Trim()

if (-not $clientId) { throw "Client ID is empty" }
if (-not $secretPlain) { throw "Client Secret is empty" }
if ($clientId -notmatch '^[0-9A-Fa-f]{8}-[0-9A-Fa-f-]{27,36}$') {
    Write-Host "WARNING: Client ID does not look like a Xero UUID - continuing anyway." -ForegroundColor Yellow
}

Set-DotEnvValue -Path $envPath -Updates @{
    XERO_CLIENT_ID     = $clientId
    XERO_CLIENT_SECRET = $secretPlain
}

Write-Host ""
Write-Host "Saved to .env:" -ForegroundColor Green
Write-Host "  XERO_CLIENT_ID     (len=$($clientId.Length))"
Write-Host "  XERO_CLIENT_SECRET (len=$($secretPlain.Length))"
Write-Host ""
Write-Host "Next:" -ForegroundColor Cyan
Write-Host "  powershell -ExecutionPolicy Bypass -File scripts\oauth_setup.ps1"
