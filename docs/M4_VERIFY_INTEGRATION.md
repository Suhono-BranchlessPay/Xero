# M4 — Verify Page Integration Guide

For BranchlessPay `VerifyPage.tsx` merge (same pattern as Wave commit `770f391`).

---

## 1. Detect Xero anchors

```typescript
import { isXeroAnchor } from "./integrations/xero/xeroVerifyMapping";

if (isXeroAnchor(anchorRecord)) {
  return <XeroVerifySections anchor={anchorRecord} />;
}
```

---

## 2. Drop-in files

- `display/src/xeroVerifyMapping.ts`
- `display/src/VerifyPageIntegration.example.tsx`

Or use:

```typescript
import { mapXeroVerifyPage } from "./integrations/xero/xeroVerifyMapping";

const { businessRows, transactionRows, statusBadge, instructions, pdfFields } =
  mapXeroVerifyPage(anchor);
```

---

## 3. ERP display label

`ERP_DISPLAY_LABEL = "Xero"` — matches BP merged Wave pattern (`"Wave"` not `"Wave Accounting"`).

---

## 4. Status badges

| Variant | Xero status |
|---------|-------------|
| `draft` | DRAFT |
| `sent` | SUBMITTED |
| `unpaid` | AUTHORISED |
| `paid` | PAID |
| `partial` | PARTIAL |

---

## 5. Tests

```powershell
cd display
npm test
```

Contact: suhono@branchlesspay.com
