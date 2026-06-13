# M3 + M4 Test Results — Xero Verify Page

Branch: `dev` · Live E2E: 2026-06-13 (Branchlesspay org)

---

## Display unit tests

Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_m3_m4_tests.ps1
```

| Test | Result |
|------|--------|
| `isXeroAnchor` | PASS |
| Business section M3 fields | PASS |
| Status badges (AUTHORISED, PAID) | PASS |
| `mapXeroVerifyPage` | PASS |
| Payment due date hidden | PASS |
| Currency AUD | PASS |
| Live fixture INV-0003 (pending enrichment) | PASS |
| Live fixture INV-0002 | PASS |
| Enriched amount display | PASS |

**Total: 9 tests — PASS**

---

## Live fixtures (M3+M4 QA)

| Fixture | Source | Notes |
|---------|--------|-------|
| `display/fixtures/live-inv-0003.json` | INV-0003 / script E2E | amount=0 pending enrichment |
| `display/fixtures/live-inv-0002.json` | Manual UI invoice $21 | amount=0 until BP worker |
| `display/fixtures/sample-enriched-invoice.json` | Future enriched shape | amount=$125 when worker live |

Preview:

```powershell
cd display
node --experimental-strip-types scripts/preview_verify.mjs
```

Fetch real anchor from BP (paste `anchor_id` from verify URL):

```powershell
powershell -ExecutionPolicy Bypass -File scripts\fetch_live_anchor.ps1 -AnchorId <uuid>
```

---

## Live verify URLs (2026-06-13)

| Invoice | Event | Verify URL | Anchor ID |
|---------|-------|------------|-----------|
| INV-0001 | Create | https://branchlesspay.com/verify/85c80ab2-5014-4d87-a5ed-62eb4851e244 | `85c80ab2-…` |
| INV-0002 | Create | https://branchlesspay.com/verify/21309f86-e1c1-4010-91f7-61ff853bab38 | `21309f86-…` |
| INV-0002 | Update | https://branchlesspay.com/verify/6c005b64-9c0f-49cf-9cf6-804db5630801 | `6c005b64-…` |
| INV-0003 | Create | https://branchlesspay.com/verify/f90bae2f-7e1a-47cb-bb0f-515cee0edf12 | `f90bae2f-…` |
| INV-0003 | Update | https://branchlesspay.com/verify/eece8209-9264-4e87-aaa6-397f808d8651 | `eece8209-…` |

All 5 status = **anchored** on Monad.

### INV-0001 verify test (2026-06-13)

| Check | Result |
|-------|--------|
| Page loads | ✅ HTTP 200 |
| Blockchain | ✅ TX `0x4c01c74b…` on Monad Testnet |
| Content hash | ✅ SHA-256 present |
| Status | ✅ VERIFIED / anchored |
| M3 display (pre-merge) | ⏳ Business/ERP `—`, Reference = erp_doc_id, Amount `$0.00` |
| After `xeroVerifyMapping` merge | INV-0001, Branchlesspay, `$0.00 (pending enrichment)` |

---

## Screenshots (M4)

Capture verify page for each live URL → save under `docs/screenshots/`:

| File | Event |
|------|-------|
| `m3m4-inv-0003.png` | `xero_invoice_created` |
| `m3m4-inv-0002.png` | `xero_invoice_created` |
| `m3m4-payment.png` | `xero_payment_received` (when available) |
| `m3m4-transaction.png` | `xero_transaction_recorded` (when available) |

---

## BP merge status

| Item | Status |
|------|--------|
| `xeroVerifyMapping.ts` | ✅ Ready (granular scopes + enrichment pending) |
| Production `VerifyPage.tsx` | ⏳ Pending BP merge (Wave pattern `770f391`) |
| `xeroEnrichmentWorker` | ⏳ BP backend — amount sync |

Contact: suhono@branchlesspay.com
