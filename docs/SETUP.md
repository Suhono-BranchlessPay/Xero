# Xero Setup Guide

## 1. Prerequisites

| Item | Notes |
|------|-------|
| Xero account | https://www.xero.com (trial org) |
| Xero developer app | https://developer.xero.com/app/manage |
| ngrok or tunnel | For local webhook testing |
| BP test token | `BP_LICENSE_KEY` from suhono@branchlesspay.com |

## 2. Install

```powershell
cd Xero
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

## 3. Configure `.env`

| Variable | Source |
|----------|--------|
| `BP_LICENSE_KEY` | BranchlessPay test token |
| `XERO_CLIENT_ID` | Xero developer portal |
| `XERO_CLIENT_SECRET` | Xero developer portal |
| `XERO_ACCESS_TOKEN` | OAuth flow |
| `XERO_REFRESH_TOKEN` | OAuth flow |
| `XERO_TENANT_ID` | Connections API after OAuth |
| `XERO_WEBHOOK_KEY` | Webhook signing key in app settings |
| `XERO_ORG_NAME` | Optional — verify page display |
| `XERO_ORG_ADDRESS` | Optional — verify page display |

## 4. Run collector

```powershell
$env:PYTHONPATH = "src"
python -m xero_bp_collector.app
```

Or: `powershell -ExecutionPolicy Bypass -File scripts\run_server.ps1`

## 5. Test flow

1. Start ngrok: `ngrok http 8080`
2. Register webhook URL in Xero app: `https://YOUR-NGROK/webhook/xero`
3. Pass intent-to-receive validation (collector returns signed hash)
4. Create test invoice in Xero
5. Watch logs for `Pipeline complete verify_url=...`

See [WEBHOOK_SETUP.md](WEBHOOK_SETUP.md) and [OAUTH.md](OAUTH.md).
