import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

import {
  formatAmountForDisplay,
  formatCurrency,
  getStatusBadge,
  isAmountPendingEnrichment,
  isXeroAnchor,
  mapBusinessSection,
  mapTransactionSection,
  mapXeroVerifyPage,
} from "../src/xeroVerifyMapping.ts";

const __dirname = dirname(fileURLToPath(import.meta.url));
const fixturesDir = join(__dirname, "..", "fixtures");
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

test("live INV-0003 fixture — pending enrichment amount", () => {
  const live = JSON.parse(
    readFileSync(join(fixturesDir, "live-inv-0003.json"), "utf8"),
  );
  assert.equal(isXeroAnchor(live), true);
  assert.equal(isAmountPendingEnrichment(live), true);
  const page = mapXeroVerifyPage(live);
  assert.equal(page.businessRows[0].value, "Branchlesspay");
  assert.equal(
    page.transactionRows.find((r) => r.label === "Reference")?.value,
    "INV-0003",
  );
  assert.equal(
    page.transactionRows.find((r) => r.label === "Amount")?.value,
    "$0.00 (pending enrichment)",
  );
  assert.match(page.instructions, /pending Xero API enrichment/);
});

test("live INV-0002 fixture maps Branchlesspay org", () => {
  const live = JSON.parse(
    readFileSync(join(fixturesDir, "live-inv-0002.json"), "utf8"),
  );
  const page = mapXeroVerifyPage(live);
  assert.equal(page.transactionRows.find((r) => r.label === "Reference")?.value, "INV-0002");
  assert.equal(formatAmountForDisplay(live), "$0.00 (pending enrichment)");
});

test("enriched invoice shows normal amount", () => {
  const enriched = JSON.parse(
    readFileSync(join(fixturesDir, "sample-enriched-invoice.json"), "utf8"),
  );
  assert.equal(isAmountPendingEnrichment(enriched), false);
  assert.equal(formatAmountForDisplay(enriched), "$125.00");
});

test("BP raw canonical payload maps resource_id as reference", () => {
  const raw = JSON.parse(
    readFileSync(join(fixturesDir, "live-inv-0001-bp-raw.json"), "utf8"),
  );
  assert.equal(isXeroAnchor(raw), true);
  const page = mapXeroVerifyPage(raw);
  assert.equal(
    page.transactionRows.find((r) => r.label === "Reference")?.value,
    "6a74d133-300c-4890-b118-4e071086e57a",
  );
  assert.equal(
    page.transactionRows.find((r) => r.label === "Amount")?.value,
    "$0.00 (pending enrichment)",
  );
});