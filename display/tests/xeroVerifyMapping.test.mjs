import assert from "node:assert/strict";
import test from "node:test";

import {
  formatCurrency,
  getStatusBadge,
  isXeroAnchor,
  mapBusinessSection,
  mapTransactionSection,
  mapXeroVerifyPage,
} from "../src/xeroVerifyMapping.ts";

const sampleInvoice = {
  event_type: "xero_invoice_created",
  reference_id: "INV-0001",
  amount: 750,
  currency: "AUD",
  voucher_date: "2026-06-12",
  timestamp: "2026-06-12T10:00:00Z",
  metadata: {
    erp: "xero",
    business_name: "Test Org LLC",
    business_address: "123 Main St, Sydney",
    tenant_id: "tenant-123",
    document_type: "Invoice",
    contact_name: "John Smith",
    invoice_number: "INV-0001",
    status: "AUTHORISED",
    due_date: "2026-07-12",
  },
};

test("isXeroAnchor detects Xero records", () => {
  assert.equal(isXeroAnchor(sampleInvoice), true);
  assert.equal(isXeroAnchor({ event_type: "wave_invoice_created" }), false);
});

test("business section maps M3 fields", () => {
  const rows = mapBusinessSection(sampleInvoice);
  assert.equal(rows[0].label, "Organisation");
  assert.equal(rows[0].value, "Test Org LLC");
  assert.equal(rows[2].value, "Xero");
});

test("status badges for Xero invoice statuses", () => {
  assert.deepEqual(getStatusBadge("AUTHORISED"), {
    label: "Authorised",
    variant: "unpaid",
  });
  assert.deepEqual(getStatusBadge("PAID"), { label: "Paid", variant: "paid" });
});

test("mapXeroVerifyPage builds full verify output", () => {
  const page = mapXeroVerifyPage(sampleInvoice);
  assert.equal(page.transactionRows.find((r) => r.label === "Amount")?.value, "A$750.00");
  assert.match(page.instructions, /Xero/);
});

test("payment hides due date", () => {
  const payment = {
    ...sampleInvoice,
    event_type: "xero_payment_received",
    metadata: { ...sampleInvoice.metadata, due_date: null, status: "PAID" },
  };
  assert.equal(
    mapTransactionSection(payment).some((row) => row.label === "Due Date"),
    false,
  );
});

test("formatCurrency AUD", () => {
  assert.equal(formatCurrency(750, "AUD"), "A$750.00");
});
