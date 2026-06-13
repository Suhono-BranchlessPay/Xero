# Simulate Xero webhook (dev — set XERO_SKIP_SIGNATURE_VERIFY=1)
param(
    [ValidateSet("invoice.created", "invoice.updated", "payment.created", "transaction.created")]
    [string]$EventType = "invoice.created",
    [string]$ResourceId = "00000000-0000-0000-0000-000000000001",
    [string]$BaseUrl = "http://127.0.0.1:8080"
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "load_dotenv.ps1")

$map = @{
    "invoice.created"     = @{ Category = "INVOICE"; Type = "CREATE" }
    "invoice.updated"     = @{ Category = "INVOICE"; Type = "UPDATE" }
    "payment.created"     = @{ Category = "PAYMENT"; Type = "CREATE" }
    "transaction.created" = @{ Category = "BANKTRANSACTION"; Type = "CREATE" }
}
$meta = $map[$EventType]

$payload = @{
    events = @(
        @{
            resourceId     = $ResourceId
            eventType      = $meta.Type
            eventCategory  = $meta.Category
            tenantId       = $env:XERO_TENANT_ID
            eventDateUtc   = (Get-Date).ToUniversalTime().ToString("o")
            resourceUrl    = "https://api.xero.com/api.xro/2.0/test/$ResourceId"
        }
    )
    firstEventSequence = 1
    lastEventSequence  = 1
    entropy            = "dev-simulate"
} | ConvertTo-Json -Depth 6 -Compress

Write-Host ("POST {0}/webhook/xero event={1}" -f $BaseUrl, $EventType) -ForegroundColor Cyan
Invoke-RestMethod -Method POST -Uri "$BaseUrl/webhook/xero" -Body $payload -ContentType "application/json"
