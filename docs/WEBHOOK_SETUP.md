# Xero Webhook Setup

## Endpoint

| Item | Value |
|------|-------|
| URL | `https://YOUR-TUNNEL/webhook/xero` |
| Method | POST |
| Signature header | `x-xero-signature` |

## Intent to receive

When you first save the webhook URL in Xero Developer Portal, Xero POSTs a validation payload. The collector:

1. Computes HMAC-SHA256 of the raw body using `XERO_WEBHOOK_KEY`
2. Base64-encodes the hash
3. Returns it as plain text with HTTP 200

## Events to subscribe

| Category | Event | Maps to |
|----------|-------|---------|
| INVOICE | CREATE | `xero_invoice_created` |
| INVOICE | UPDATE | `xero_invoice_updated` |
| PAYMENT | CREATE | `xero_payment_received` |
| BANKTRANSACTION | CREATE | `xero_transaction_recorded` |

## Local dev

Set `XERO_SKIP_SIGNATURE_VERIFY=1` in `.env` and use:

```powershell
.\scripts\simulate_webhook.ps1 -EventType invoice.created
```

Contact: suhono@branchlesspay.com
