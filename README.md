# BranchlessPay Audit Shield — Xero Collector

Immutable audit trail for Xero invoices, payments, and bank transactions.

| Item | Value |
|------|-------|
| Scope | **M1 + M2** webhook/collector · **M3 + M4** verify display mapping |
| Local webhook | `POST http://127.0.0.1:8080/webhook/xero` |
| BP anchor API | `POST https://branchlesspay.com/api/v1/anchor` |
| GitHub | https://github.com/Suhono-BranchlessPay/Xero |
| Branch | **`dev` only** |

---

## What this does

1. Xero fires a webhook (`INVOICE`, `PAYMENT`, `BANKTRANSACTION` events).
2. Collector verifies `x-xero-signature` (HMAC-SHA256, Base64).
3. Fetches full document from Xero REST API (OAuth 2.0 + tenant ID).
4. Normalizes to BranchlessPay anchor format (`erp: xero`).
5. POSTs to BranchlessPay → verify at `https://branchlesspay.com/verify/[anchor_id]`.
6. **M3+M4:** `display/src/xeroVerifyMapping.ts` for verify page sections.

---

## Event mapping

| Xero event | BP `event_type` | Document |
|------------|-----------------|----------|
| `INVOICE` CREATE | `xero_invoice_created` | Invoice |
| `INVOICE` UPDATE | `xero_invoice_updated` | Invoice |
| `PAYMENT` CREATE | `xero_payment_received` | Payment |
| `BANKTRANSACTION` CREATE | `xero_transaction_recorded` | Bank Transaction |

---

## Quick start

```powershell
cd Xero
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Edit .env — BP_LICENSE_KEY, Xero OAuth, XERO_TENANT_ID, XERO_WEBHOOK_KEY

$env:PYTHONPATH = "src"
python -m xero_bp_collector.app
```

Health: http://127.0.0.1:8080/health

---

## Tests

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_tests.ps1
```

---

## Project layout

```
Xero/
├── display/                   # M3+M4 verify-page mapping
├── src/xero_bp_collector/     # M1+M2 Flask webhook pipeline
├── scripts/
├── tests/
├── docs/
├── MILESTONE_XERO.md
└── MILESTONE_M3_M4.md
```

Contact: suhono@branchlesspay.com
