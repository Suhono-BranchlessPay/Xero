# Xero OAuth 2.0 - authorize, exchange code, save tokens + tenant to .env
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "load_dotenv.ps1")

$envPath = Join-Path (Split-Path -Parent $PSScriptRoot) ".env"
$dotenv = Read-DotEnv -Path $envPath

function Get-EnvValue {
    param([string]$Name)
    $item = Get-Item -Path "Env:$Name" -ErrorAction SilentlyContinue
    if ($item -and [string]$item.Value) { return [string]$item.Value }
    if ($dotenv.ContainsKey($Name) -and [string]$dotenv[$Name]) {
        return [string]$dotenv[$Name]
    }
    return ""
}

foreach ($key in @("XERO_CLIENT_ID", "XERO_CLIENT_SECRET", "XERO_REDIRECT_URI")) {
    if (-not (Get-EnvValue $key)) {
        Write-Host ""
        Write-Host "File checked: $envPath" -ForegroundColor Yellow
        throw @"
$key is empty in .env

Fix (pick one):
  1. Run: powershell -ExecutionPolicy Bypass -File scripts\set_xero_credentials.ps1
  2. Edit .env manually - save XERO_CLIENT_ID= and XERO_CLIENT_SECRET= with no spaces around =

Get values: https://developer.xero.com/app/manage -> Configuration
"@
    }
}

# Granular scopes (required for apps created on/after 2 Mar 2026).
# Override in .env with XERO_OAUTH_SCOPES if needed.
$defaultScopes = @(
    "openid"
    "profile"
    "email"
    "offline_access"
    "accounting.settings"
    "accounting.contacts"
    "accounting.invoices"
    "accounting.payments"
    "accounting.banktransactions"
) -join " "
$scopes = Get-EnvValue "XERO_OAUTH_SCOPES"
if (-not $scopes) { $scopes = $defaultScopes }
$redirect = Get-EnvValue "XERO_REDIRECT_URI"
$clientId = Get-EnvValue "XERO_CLIENT_ID"
$state = [guid]::NewGuid().ToString()

Write-Host "Scopes (granular, Mar 2026+ apps): $scopes" -ForegroundColor Gray
Write-Host ""
Write-Host "If browser shows 'Invalid scope' - script already uses granular scopes; re-run after saving this file." -ForegroundColor Yellow
Write-Host ""
Write-Host "=== Xero OAuth ===" -ForegroundColor Cyan
Write-Host "Redirect URI sent to Xero (must be registered EXACTLY in developer portal):" -ForegroundColor Yellow
Write-Host "  $redirect"
Write-Host ""
Write-Host "If you see 'Invalid redirect_uri' in the browser:" -ForegroundColor Yellow
Write-Host "  1. Open https://developer.xero.com/app/manage -> your app -> Configuration"
Write-Host "  2. OAuth 2.0 redirect URIs -> Add this exact line (copy/paste):"
Write-Host "     $redirect"
Write-Host "  3. Save, wait ~30 seconds, run this script again"
Write-Host ""
Write-Host "IMPORTANT - on the Xero consent screen:" -ForegroundColor Yellow
Write-Host "  - Select Demo Company (Global) for FREE dev testing"
Write-Host "  - Do NOT select Branchlesspay if it shows 'Subscription required to connect'"
Write-Host ""
$go = Read-Host "Redirect URI already saved in Xero portal? (y/n)"
if ($go -ne "y") {
    Write-Host "Add the URI above in Xero portal first, then re-run." -ForegroundColor Yellow
    exit 0
}

Write-Host "Opening browser..." -ForegroundColor Yellow

$queryParts = @(
    "response_type=code"
    ("client_id={0}" -f [uri]::EscapeDataString($clientId))
    ("redirect_uri={0}" -f [uri]::EscapeDataString($redirect))
    ("scope={0}" -f [uri]::EscapeDataString($scopes))
    ("state={0}" -f [uri]::EscapeDataString($state))
)
$authUrl = "https://login.xero.com/identity/connect/authorize?" + ($queryParts -join "&")
Start-Process $authUrl

Write-Host @"

After login, Xero redirects to your redirect URI with ?code=... in the URL.
The browser may show 'Not Found' - that is OK.

Copy ONLY the value after code= and BEFORE the next & character.
Example URL:
  .../callback?code=NE5OsZAHdGRFZwDv3B6MCz5z1WEkcSDubKjOri_vpxA&scope=...
  paste -> NE5OsZAHdGRFZwDv3B6MCz5z1WEkcSDubKjOri_vpxA

Do NOT paste session_state=... or state=... values.

IMPORTANT:
  - Code valid ~5 minutes, ONE use only
  - Paste immediately after redirect

"@

$code = (Read-Host "Paste authorization code").Trim()
if (-not $code) { throw "No code provided" }

Write-Host "Exchanging code for tokens..." -ForegroundColor Cyan
$clientSecret = Get-EnvValue "XERO_CLIENT_SECRET"
$basic = [Convert]::ToBase64String(
    [Text.Encoding]::ASCII.GetBytes("${clientId}:${clientSecret}")
)
$tokenBody = @{
    grant_type   = "authorization_code"
    code         = $code
    redirect_uri = $redirect
}
try {
    $tokenResp = Invoke-RestMethod -Method POST -Uri "https://identity.xero.com/connect/token" `
        -Headers @{ Authorization = "Basic $basic" } `
        -Body $tokenBody `
        -ContentType "application/x-www-form-urlencoded"
} catch {
    Write-Host ""
    Write-Host "invalid_grant? The code is single-use and expires in ~5 minutes." -ForegroundColor Yellow
    Write-Host "Run this script again, login in browser, copy the NEW code immediately." -ForegroundColor Yellow
    Write-Host "Or: powershell -ExecutionPolicy Bypass -File scripts\oauth_exchange.ps1" -ForegroundColor Yellow
    throw
}

$access = $tokenResp.access_token
$refresh = $tokenResp.refresh_token
if (-not $access) { throw "Token response missing access_token" }

Write-Host "Fetching connected organisations..." -ForegroundColor Cyan
$connections = Invoke-RestMethod -Uri "https://api.xero.com/connections" -Headers @{
    Authorization = "Bearer $access"
    Accept        = "application/json"
}

if (-not $connections -or $connections.Count -eq 0) {
    throw "No Xero organisations connected - authorise at least one org in the OAuth screen"
}

Write-Host ""
Write-Host "Connected organisations:" -ForegroundColor Green
for ($i = 0; $i -lt $connections.Count; $i++) {
    $c = $connections[$i]
    Write-Host ("  [{0}] {1}  tenantId={2}" -f $i, $c.tenantName, $c.tenantId)
}

$pick = 0
if ($connections.Count -gt 1) {
    $pick = Read-Host "Pick org index (0-based)"
}
$chosen = $connections[[int]$pick]
$tenantId = $chosen.tenantId
$orgName = $chosen.tenantName

$updates = @{
    XERO_ACCESS_TOKEN  = $access
    XERO_REFRESH_TOKEN = $refresh
    XERO_TENANT_ID     = $tenantId
    XERO_ORG_NAME      = $orgName
}
Set-DotEnvValue -Path $envPath -Updates $updates

Write-Host ""
Write-Host "Saved to .env:" -ForegroundColor Green
Write-Host "  XERO_TENANT_ID  = $tenantId"
Write-Host "  XERO_ORG_NAME   = $orgName"
Write-Host "  XERO_ACCESS_TOKEN / XERO_REFRESH_TOKEN updated"
Write-Host ""
Write-Host "Next: powershell -ExecutionPolicy Bypass -File scripts\run_live_e2e.ps1" -ForegroundColor Cyan
