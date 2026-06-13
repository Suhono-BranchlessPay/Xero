# Xero OAuth 2.0

## Quick setup (Windows)

1. Add `XERO_CLIENT_ID` and `XERO_CLIENT_SECRET` to `.env` from [developer.xero.com/app/manage](https://developer.xero.com/app/manage)
2. Register redirect URI in the app: `http://localhost:8080/oauth/callback` (must match `XERO_REDIRECT_URI`)
3. Run:

```powershell
cd "C:\Users\Thinkbook\Downloads\Audit Shield\Xero"
powershell -ExecutionPolicy Bypass -File scripts\oauth_setup.ps1
```

4. Live invoice E2E (production webhook at `branchlesspay.com`):

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_live_e2e.ps1
```

## Scopes required

Apps created **on or after 2 March 2026** must use **granular scopes** (not `accounting.transactions`):

```
openid profile email offline_access
accounting.settings accounting.contacts
accounting.invoices accounting.payments accounting.banktransactions
```

Optional in `.env`: `XERO_OAUTH_SCOPES=` (space-separated, overrides default)

Legacy apps (before Mar 2026) may still use `accounting.transactions` until Sep 2027.

## Authorize URL

```
https://login.xero.com/identity/connect/authorize
  ?response_type=code
  &client_id=YOUR_CLIENT_ID
  &redirect_uri=YOUR_REDIRECT_URI
  &scope=openid profile email offline_access accounting.settings accounting.contacts accounting.invoices accounting.payments accounting.banktransactions
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

---

## Troubleshooting

### `Invalid redirect_uri`

Add this **exact** URI in developer portal → Configuration → OAuth 2.0 redirect URIs:

```
http://localhost:8080/oauth/callback
```

### `Invalid scope`

App **Bp Audit Shield** (created after 2 Mar 2026) cannot use `accounting.transactions`.  
`oauth_setup.ps1` now requests granular scopes automatically. Re-run the script.

### `Subscription required to connect` (Branchlesspay org greyed out)

| Cause | Fix |
|-------|-----|
| Org has **no active Xero plan** (trial expired, cancelled) | Renew Xero subscription for that org, **or** connect **Demo Company** instead (free) |
| App type is **Custom Connection** | Custom Connection needs paid add-on (~$5–10/mo per org). For dev, create a **Web app** instead at [developer.xero.com/app/manage](https://developer.xero.com/app/manage) |
| Wrong org selected | On OAuth screen, pick **Demo Company (Global)** — not Branchlesspay — for free testing |
| User role too low | Connecting user must be **Standard** or **Adviser** level in that org |

### Recommended for Audit Shield dev (free)

1. Confirm app type = **Web app** (not Custom Connection)
2. Run `scripts\oauth_setup.ps1` again
3. On consent screen, select **Demo Company** only → **Allow access**
4. Create test invoices in **Demo Company** (webhook + OAuth use the same connected org)

### If you must use org Branchlesspay (production)

- Activate paid Xero plan on Branchlesspay org, **or**
- Purchase **Custom Connection** subscription (AU/NZ/UK/US only): [Xero Central — custom integrations](https://central.xero.com/s/article/Create-custom-integrations-and-apps-with-Xero)

Webhook intent-to-receive (`branchlesspay.com/api/v1/webhook/xero`) does **not** need OAuth — but live invoice tests need at least one **subscribed / Demo** org connected to the app.

Contact: suhono@branchlesspay.com
