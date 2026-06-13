# Test Xero intent-to-receive locally (same logic as Xero portal button)
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "load_dotenv.ps1")

if (-not $env:XERO_WEBHOOK_KEY) {
    throw "XERO_WEBHOOK_KEY is not set in .env"
}

$body = '{"events":[],"firstEventSequence":0,"lastEventSequence":0,"entropy":"local-test"}'
$bytes = [Text.Encoding]::UTF8.GetBytes($body)
$hmac = New-Object System.Security.Cryptography.HMACSHA256
$hmac.Key = [Text.Encoding]::UTF8.GetBytes($env:XERO_WEBHOOK_KEY)
$hash = [Convert]::ToBase64String($hmac.ComputeHash($bytes))
$headers = @{ "x-xero-signature" = $hash; "Content-Type" = "application/json" }

Write-Host "POST http://127.0.0.1:8080/webhook/xero (intent-to-receive)" -ForegroundColor Cyan
try {
    $resp = Invoke-WebRequest -Method POST -Uri "http://127.0.0.1:8080/webhook/xero" `
        -Body $body -Headers $headers -UseBasicParsing
    Write-Host ("Status: {0}" -f $resp.StatusCode) -ForegroundColor Green
    Write-Host ("Body:   '{0}'" -f $resp.Content)
    if ($resp.StatusCode -eq 200) {
        Write-Host "Intent signature OK - collector ready for Xero validation." -ForegroundColor Green
    } else {
        Write-Host "WARNING: expected HTTP 200 for valid signature." -ForegroundColor Yellow
    }
} catch {
    $status = $_.Exception.Response.StatusCode.value__
    Write-Host ("FAILED HTTP {0}" -f $status) -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        Write-Host $reader.ReadToEnd()
    }
    exit 1
}
