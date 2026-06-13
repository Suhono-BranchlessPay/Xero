# Xero OAuth 2.0

## Scopes required

```
openid profile email accounting.transactions accounting.contacts accounting.settings offline_access
```

## Authorize URL

```
https://login.xero.com/identity/connect/authorize
  ?response_type=code
  &client_id=YOUR_CLIENT_ID
  &redirect_uri=YOUR_REDIRECT_URI
  &scope=openid profile email accounting.transactions accounting.contacts accounting.settings offline_access
  &state=123
```

## Token exchange

```powershell
# After redirect with ?code=
$body = @{
  grant_type    = "authorization_code"
  code          = $code
  redirect_uri  = $env:XERO_REDIRECT_URI
  client_id     = $env:XERO_CLIENT_ID
  client_secret = $env:XERO_CLIENT_SECRET
}
Invoke-RestMethod -Method POST -Uri "https://identity.xero.com/connect/token" -Body $body
```

## Get tenant ID

```powershell
Invoke-RestMethod -Uri "https://api.xero.com/connections" -Headers @{
  Authorization = "Bearer $env:XERO_ACCESS_TOKEN"
  Accept = "application/json"
}
```

Save `tenantId` to `.env` as `XERO_TENANT_ID`.

Contact: suhono@branchlesspay.com
