# M3 + M4 Screenshots

Save verify-page screenshots here after live anchor E2E.

## Capture steps

1. Get `anchor_id` from verify URL or BP logs
2. Open `https://branchlesspay.com/verify/{anchor_id}`
3. Screenshot full verify page (Organisation + Transaction + hash section)
4. Save as filename below

| File | Event | Live sample |
|------|-------|-------------|
| `m3m4-inv-0003.png` | `xero_invoice_created` | INV-0003 / BP-E2E-20260613-060015 |
| `m3m4-inv-0002.png` | `xero_invoice_created` | INV-0002 / $21 noodle ramen |
| `m3m4-inv-updated.png` | `xero_invoice_updated` | TBD |
| `m3m4-payment.png` | `xero_payment_received` | TBD |
| `m3m4-transaction.png` | `xero_transaction_recorded` | TBD |

## Expected M3 display (pre-enrichment)

- Organisation: **Branchlesspay**
- Amount: **$0.00 (pending enrichment)** until BP worker syncs
- ERP System: **Xero**

## Fetch fixture from live anchor

```powershell
powershell -ExecutionPolicy Bypass -File scripts\fetch_live_anchor.ps1 -AnchorId <uuid>
```
