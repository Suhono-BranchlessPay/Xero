# Fetch live anchor from BP API and save fixture for M3+M4 preview
param(
    [Parameter(Mandatory = $true)]
    [string]$AnchorId
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "load_dotenv.ps1")

$token = $env:BP_LICENSE_KEY
if (-not $token) { throw "BP_LICENSE_KEY not set in .env" }

$url = "https://branchlesspay.com/api/v1/anchor/$AnchorId"
Write-Host "GET $url" -ForegroundColor Cyan
$anchor = Invoke-RestMethod -Uri $url -Headers @{
    Authorization = "Bearer $token"
    Accept        = "application/json"
}

$fixturesDir = Join-Path (Split-Path -Parent $PSScriptRoot) "display\fixtures"
if (-not (Test-Path $fixturesDir)) {
    New-Item -ItemType Directory -Path $fixturesDir | Out-Null
}
$outFile = Join-Path $fixturesDir "live-$AnchorId.json"
$anchor | ConvertTo-Json -Depth 12 | Set-Content -Path $outFile -Encoding UTF8

Write-Host ""
Write-Host "Saved: $outFile" -ForegroundColor Green
Write-Host "Verify: https://branchlesspay.com/verify/$AnchorId" -ForegroundColor Green
Write-Host ""
Write-Host "Preview mapping:" -ForegroundColor Cyan
Set-Location (Join-Path (Split-Path -Parent $PSScriptRoot) "display")
node --experimental-strip-types scripts/preview_verify.mjs
