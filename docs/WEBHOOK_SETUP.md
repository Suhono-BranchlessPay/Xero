# Xero Webhook Setup

## Endpoint

| Item | Value |
|------|-------|
| URL | `https://YOUR-TUNNEL/webhook/xero` |
| Method | POST |
| Signature header | `x-xero-signature` |

## Intent to receive

When you click **Send intent to receive**, Xero POSTs a signed validation payload (`events: []`). The collector:

1. Reads the **raw** request body (no JSON re-serialization)
2. Verifies `x-xero-signature` using `XERO_WEBHOOK_KEY`
3. Returns HTTP **200** if valid, **401** if invalid

Test locally before using a tunnel:

```powershell
# Flask must be running on :8080
powershell -ExecutionPolicy Bypass -File scripts\test_intent.ps1
```

### "Response not 2XX" troubleshooting

| Cause | Fix |
|-------|-----|
| Flask not running | Start `python -m xero_bp_collector.app` |
| Wrong URL path | Must end with `/webhook/xero` |
| ngrok not running / URL changed | Restart ngrok, update Xero portal URL |
| ngrok free browser block | Use **Cloudflare Tunnel** instead: `cloudflared tunnel --url http://127.0.0.1:8080` |
| `XERO_WEBHOOK_KEY` mismatch | Copy key from Xero portal into `.env`, restart Flask — wrong key returns **401** |
| URL tunnel lama | Setelah restart cloudflared, URL berubah — update portal Xero |
| Old Wave collector on :8080 | `/health` must show `xero-bp-collector` |

Check ngrok request log: http://127.0.0.1:4040 — look for status code Xero received.

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
