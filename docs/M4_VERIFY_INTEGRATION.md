# M4 — Verify Page Integration Guide

For BranchlessPay `VerifyPage.tsx` merge.

---

## 1. Detect Wave anchors

```typescript
import { isWaveAnchor } from "./integrations/wave/waveVerifyMapping";

if (isWaveAnchor(anchorRecord)) {
  return <WaveVerifySections anchor={anchorRecord} />;
}
```

---

## 2. Drop-in component

Copy from this repo:

- `display/src/waveVerifyMapping.ts` — pure mapping (no React deps)
- `display/src/VerifyPageIntegration.example.tsx` — React sections

Or use the single helper:

```typescript
import { mapWaveVerifyPage } from "./integrations/wave/waveVerifyMapping";

const { businessRows, transactionRows, statusBadge, instructions, pdfFields } =
  mapWaveVerifyPage(anchor);
```

---

## 3. CSS badge variants

| Variant | Wave status | Suggested color |
|---------|-------------|-----------------|
| `unpaid` | UNPAID | blue |
| `paid` | PAID | green |
| `overdue` | OVERDUE | red |
| `draft` | DRAFT | grey |
| `partial` | PARTIAL | yellow |
| `saved` | SAVED | grey |
| `sent` | SENT, VIEWED | blue |

---

## 4. Sample verify URLs (QA)

| Event | URL |
|-------|-----|
| `invoice.created` | https://branchlesspay.com/verify/9d938e0d-e64d-44da-91fd-1345e2ab60a4 |
| `payment.created` | https://branchlesspay.com/verify/587583dd-ef70-47c8-8c6f-ed4480e46ba1 |

Fixtures matching these anchors: `display/fixtures/`

Preview locally:

```powershell
cd display
node --experimental-strip-types scripts/preview_verify.mjs
npm test
```

---

## 5. PDF evidence export

Use `buildPdfEvidenceFields(anchor)` for audit PDF footer:

- `documentNumber`, `clientName`, `dueDate`, `documentType`, `amountFormatted`, `currency`

---

## 6. Pending BP platform

- Merge `WaveVerifySections` into production `VerifyPage.tsx`
- Pass full anchor payload (including `metadata`) from GET anchor API to verify page renderer

Contact: suhono@branchlesspay.com
