# Exchange a fresh Xero authorization code for tokens (code valid ~5 min, single use)
param(
    [string]$Code
)

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

function Exchange-XeroCode {
    param([string]$AuthCode)
    $redirect = Get-EnvValue "XERO_REDIRECT_URI"
    $clientId = Get-EnvValue "XERO_CLIENT_ID"
    $clientSecret = Get-EnvValue "XERO_CLIENT_SECRET"
    if (-not $redirect -or -not $clientId -or -not $clientSecret) {
        throw "XERO_REDIRECT_URI, XERO_CLIENT_ID, XERO_CLIENT_SECRET must be set in .env"
    }
    $AuthCode = $AuthCode.Trim()
    if (-not $AuthCode) { throw "Authorization code is empty" }

    $basic = [Convert]::ToBase64String(
        [Text.Encoding]::ASCII.GetBytes("${clientId}:${clientSecret}")
    )
    $tokenBody = @{
        grant_type   = "authorization_code"
        code         = $AuthCode
        redirect_uri = $redirect
    }
    Write-Host "Exchanging code (redirect_uri=$redirect)..." -ForegroundColor Cyan
    try {
        return Invoke-RestMethod -Method POST -Uri "https://identity.xero.com/connect/token" `
            -Headers @{ Authorization = "Basic $basic" } `
            -Body $tokenBody `
            -ContentType "application/x-www-form-urlencoded"
    } catch {
        Write-Host ""
        Write-Host "Token exchange failed. Common fixes:" -ForegroundColor Yellow
        Write-Host "  - Code expires in ~5 minutes and works ONCE only"
        Write-Host "  - Run oauth_setup.ps1 again and paste the NEW code immediately"
        Write-Host "  - redirect_uri must match: $redirect"
        throw
    }
}

function Save-XeroTokens {
    param($TokenResp)
    $access = $TokenResp.access_token
    $refresh = $TokenResp.refresh_token
    if (-not $access) { throw "Token response missing access_token" }

    Write-Host "Fetching connected organisations..." -ForegroundColor Cyan
    $connections = Invoke-RestMethod -Uri "https://api.xero.com/connections" -Headers @{
        Authorization = "Bearer $access"
        Accept        = "application/json"
    }
    if (-not $connections -or $connections.Count -eq 0) {
        throw "No Xero organisations connected"
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
    Set-DotEnvValue -Path $envPath -Updates @{
        XERO_ACCESS_TOKEN  = $access
        XERO_REFRESH_TOKEN = $refresh
        XERO_TENANT_ID     = $chosen.tenantId
        XERO_ORG_NAME      = $chosen.tenantName
    }
    Write-Host ""
    Write-Host "Saved tokens to .env" -ForegroundColor Green
    Write-Host "  XERO_TENANT_ID = $($chosen.tenantId)"
    Write-Host "  XERO_ORG_NAME  = $($chosen.tenantName)"
}

if (-not $Code) {
    Write-Host "Paste a FRESH code from the browser URL (code=...&scope=...)" -ForegroundColor Yellow
    Write-Host "Do NOT reuse a code you pasted before." -ForegroundColor Yellow
    $Code = Read-Host "Authorization code"
}
$tokenResp = Exchange-XeroCode -AuthCode $Code
Save-XeroTokens -TokenResp $tokenResp
Write-Host ""
Write-Host "Next: powershell -ExecutionPolicy Bypass -File scripts\run_live_e2e.ps1" -ForegroundColor Cyan
