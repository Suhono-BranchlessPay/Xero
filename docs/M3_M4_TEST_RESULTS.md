# M3 + M4 Test Results — Wave Verify Page

Branch: `dev`  
Date: 2026-06-13

---

## Display unit tests

Run:

```powershell
cd display
npm test
```

| Test | Result |
|------|--------|
| `isWaveAnchor` | PASS |
| Business section M3 fields | PASS |
| Live fixture `invoice.created` (9d938e0d) | PASS |
| Live fixture `payment.created` (587583dd) | PASS |
| Due date hidden for payments | PASS |
| Status badges (UNPAID, PAID, SAVED, …) | PASS |
| Transaction status row hidden | PASS |
| Currency USD/CAD | PASS |
| PDF evidence fields | PASS |
| Verification instructions | PASS |

**Total: 11 tests — PASS**

---

## Sample verify URLs (live anchors)

| Event | Anchor ID | Status (API) | Verify |
|-------|-----------|----------------|--------|
| `invoice.created` | `9d938e0d-e64d-44da-91fd-1345e2ab60a4` | anchored | https://branchlesspay.com/verify/9d938e0d-e64d-44da-91fd-1345e2ab60a4 |
| `payment.created` | `587583dd-ef70-47c8-8c6f-ed4480e46ba1` | anchored | https://branchlesspay.com/verify/587583dd-ef70-47c8-8c6f-ed4480e46ba1 |

Mapping validated against fixtures in `display/fixtures/` (derived from M2 anchor payloads).

---

## Preview command

```powershell
cd display
node --experimental-strip-types scripts/preview_verify.mjs
```

---

## BP merge status

| Item | Status |
|------|--------|
| `waveVerifyMapping.ts` | ✅ Ready |
| `VerifyPageIntegration.example.tsx` | ✅ Ready |
| Production `VerifyPage.tsx` merge | ⏳ Pending BP |

Contact: suhono@branchlesspay.com
