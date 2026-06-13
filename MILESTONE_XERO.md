# Milestone — Xero × BranchlessPay (M1 + M2)

Repo: https://github.com/Suhono-BranchlessPay/Xero  
Branch: **`dev` only**  
Status: **Scaffold complete** — awaiting Xero developer app + live E2E

---

## M1 — Webhook receiver

| Deliverable | Status |
|-------------|--------|
| `POST /webhook/xero` | ✅ |
| `x-xero-signature` HMAC-SHA256 (Base64) | ✅ |
| Intent-to-receive validation | ✅ |
| Parse Xero batched webhook JSON | ✅ |
| Dev simulate script | ✅ |
| Docs | ✅ |

---

## M2 — Normalize + BP anchor

| Deliverable | Status |
|-------------|--------|
| Xero REST client (`xero_client.py`) | ✅ |
| Normalizer + BP poster | ✅ |
| Idempotency + failed queue | ✅ |
| OAuth docs | ✅ |
| Unit tests | ✅ |
| Live E2E with Xero trial | ⏳ User setup |

---

## Event mapping

| Xero | BP `event_type` |
|------|-----------------|
| `INVOICE` CREATE | `xero_invoice_created` |
| `INVOICE` UPDATE | `xero_invoice_updated` |
| `PAYMENT` CREATE | `xero_payment_received` |
| `BANKTRANSACTION` CREATE | `xero_transaction_recorded` |

Contact: suhono@branchlesspay.com
