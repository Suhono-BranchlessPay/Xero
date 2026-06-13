# M3 Field Mapping — Xero Verify Page

Implementation: `display/src/xeroVerifyMapping.ts`

Detect Xero anchors: `metadata.erp === "xero"` or `event_type.startsWith("xero_")`.

---

## Organisation Information

| Label | Source | Fallback |
|-------|--------|----------|
| Organisation | `metadata.business_name` | `company_name`, `-` |
| Address | `metadata.business_address` | `-` |
| ERP System | hardcoded | `"Xero"` |

---

## Transaction Details

| Label | Source | Notes |
|-------|--------|-------|
| Reference | `metadata.invoice_number` | else `reference_id` |
| Document Type | event label map | see below |
| Contact | `metadata.contact_name` | Payment/invoice |
| Reference | `reference_id` | Bank transaction |
| Date | `voucher_date` / `payment_date` / `transaction_date` | Event-specific |
| Due Date | `metadata.due_date` | Invoice events only |
| Amount | `amount` + `currency` | USD/CAD/AUD/NZD/GBP |
| Status | `metadata.status` | Hidden for bank transactions |

---

## Event labels

| `event_type` | Display |
|--------------|---------|
| `xero_invoice_created` | Xero Invoice |
| `xero_invoice_updated` | Xero Invoice (Updated) |
| `xero_payment_received` | Xero Payment |
| `xero_transaction_recorded` | Xero Bank Transaction |

---

## Status badges

| Xero status | Label | Variant |
|-------------|-------|---------|
| DRAFT | Draft | `draft` |
| SUBMITTED | Submitted | `sent` |
| AUTHORISED | Authorised | `unpaid` |
| PAID | Paid | `paid` |
| PARTIAL | Partial | `partial` |
| VOIDED | Voided | `unknown` |

See [M4_VERIFY_INTEGRATION.md](M4_VERIFY_INTEGRATION.md) for BP merge steps.
