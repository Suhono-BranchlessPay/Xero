/**
 * Xero verify-page field mapping for BranchlessPay VerifyPage.tsx.
 */

export type XeroStatus =
  | "DRAFT"
  | "SUBMITTED"
  | "AUTHORISED"
  | "PAID"
  | "VOIDED"
  | "PARTIAL"
  | string;

export type StatusBadgeVariant =
  | "unpaid"
  | "paid"
  | "overdue"
  | "draft"
  | "partial"
  | "saved"
  | "sent"
  | "unknown";

export interface XeroAnchorMetadata {
  erp?: string;
  erp_system?: string;
  company_name?: string | null;
  business_name?: string | null;
  business_address?: string | null;
  tenant_id?: string | null;
  document_type?: string | null;
  contact_name?: string | null;
  invoice_number?: string | null;
  status?: XeroStatus | null;
  due_date?: string | null;
  voucher_date?: string | null;
  create_date?: string | null;
  payment_date?: string | null;
  transaction_date?: string | null;
  xero_event?: string | null;
  xero_id?: string | null;
  amount_enriched?: boolean | null;
}

export interface XeroAnchorRecord {
  event_type?: string;
  reference_id?: string;
  amount?: number;
  currency?: string;
  voucher_date?: string;
  timestamp?: string;
  tenant_id?: string;
  business_name?: string;
  business_address?: string;
  erp_system?: string;
  metadata?: XeroAnchorMetadata;
}

export interface VerifyRow {
  label: string;
  value: string;
  hidden?: boolean;
}

export interface StatusBadge {
  label: string;
  variant: StatusBadgeVariant;
}

export interface PdfEvidenceFields {
  documentNumber: string;
  clientName: string;
  dueDate: string | null;
  documentType: string;
  amountFormatted: string;
  currency: string;
}

export interface XeroVerifyPageData {
  businessRows: VerifyRow[];
  transactionRows: VerifyRow[];
  statusBadge: StatusBadge;
  instructions: string;
  pdfFields: PdfEvidenceFields;
}

export const ERP_DISPLAY_LABEL = "Xero";

export const EVENT_TYPE_LABELS: Record<string, string> = {
  xero_invoice_created: "Xero Invoice",
  xero_invoice_updated: "Xero Invoice (Updated)",
  xero_payment_received: "Xero Payment",
  xero_transaction_recorded: "Xero Bank Transaction",
  xero_creditnote_created: "Xero Credit Note",
};

export const STATUS_LABELS: Record<string, string> = {
  DRAFT: "Draft",
  SUBMITTED: "Submitted",
  AUTHORISED: "Authorised",
  PAID: "Paid",
  VOIDED: "Voided",
  PARTIAL: "Partial",
  DELETED: "Deleted",
};

export const STATUS_BADGE_VARIANTS: Record<string, StatusBadgeVariant> = {
  DRAFT: "draft",
  SUBMITTED: "sent",
  AUTHORISED: "unpaid",
  PAID: "paid",
  VOIDED: "unknown",
  PARTIAL: "partial",
  DELETED: "unknown",
};

const INVOICE_EVENT_TYPES = new Set([
  "xero_invoice_created",
  "xero_invoice_updated",
]);

const SUPPORTED_CURRENCIES = new Set(["USD", "CAD", "AUD", "NZD", "GBP"]);

export function isXeroAnchor(anchor: XeroAnchorRecord): boolean {
  const erp = anchor.metadata?.erp?.toLowerCase();
  const vendor = (anchor.metadata as { vendor?: string } | undefined)?.vendor?.toLowerCase();
  const eventType = anchor.event_type ?? "";
  return erp === "xero" || vendor === "xero" || eventType.startsWith("xero_");
}

export function displayOrDash(value: string | null | undefined): string {
  if (value === null || value === undefined) {
    return "-";
  }
  const trimmed = String(value).trim();
  return trimmed === "" ? "-" : trimmed;
}

export function formatCurrency(amount: number, currency = "USD"): string {
  const code = (currency || "USD").toUpperCase();
  const safeAmount = Number.isFinite(amount) ? amount : 0;
  const fixed = safeAmount.toFixed(2);

  switch (code) {
    case "USD":
      return `$${fixed}`;
    case "CAD":
      return `CA$${fixed}`;
    case "AUD":
      return `A$${fixed}`;
    case "NZD":
      return `NZ$${fixed}`;
    case "GBP":
      return `£${fixed}`;
    default:
      return `${code} ${fixed}`;
  }
}

/** BP webhook anchors may show amount=0 until xeroEnrichmentWorker runs. */
export function formatAmountForDisplay(anchor: XeroAnchorRecord): string {
  const amount = anchor.amount ?? 0;
  const currency = anchor.currency ?? "USD";
  const formatted = formatCurrency(amount, currency);
  if (amount === 0 && !anchor.metadata?.amount_enriched) {
    return `${formatted} (pending enrichment)`;
  }
  return formatted;
}

export function isAmountPendingEnrichment(anchor: XeroAnchorRecord): boolean {
  return (anchor.amount ?? 0) === 0 && !anchor.metadata?.amount_enriched;
}

export function formatDisplayDate(value: string | null | undefined): string {
  if (!value) {
    return "-";
  }
  if (value.startsWith("/Date(")) {
    return value;
  }
  const dateOnly = value.split("T")[0].split(" ")[0];
  const parsed = new Date(`${dateOnly}T00:00:00Z`);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  }).format(parsed);
}

export function getEventTypeLabel(eventType: string | undefined): string {
  if (!eventType) {
    return ERP_DISPLAY_LABEL;
  }
  return EVENT_TYPE_LABELS[eventType] ?? eventType;
}

export function isInvoiceEvent(anchor: XeroAnchorRecord): boolean {
  return INVOICE_EVENT_TYPES.has(anchor.event_type ?? "");
}

export function getStatusBadge(status: XeroStatus | null | undefined): StatusBadge {
  const normalized = String(status ?? "UNKNOWN").toUpperCase();
  const label = STATUS_LABELS[normalized] ?? displayOrDash(status ?? undefined);
  const variant = STATUS_BADGE_VARIANTS[normalized] ?? "unknown";
  return { label, variant };
}

export function getBusinessName(anchor: XeroAnchorRecord): string {
  const metadata = anchor.metadata ?? {};
  return displayOrDash(
    metadata.business_name ?? metadata.company_name ?? anchor.business_name,
  );
}

export function getBusinessAddress(anchor: XeroAnchorRecord): string {
  const metadata = anchor.metadata ?? {};
  return displayOrDash(metadata.business_address ?? anchor.business_address);
}

export function getReferenceId(anchor: XeroAnchorRecord): string {
  const metadata = anchor.metadata ?? {};
  if (metadata.invoice_number) {
    return displayOrDash(metadata.invoice_number);
  }
  const ref = anchor.reference_id ?? "";
  const resourceId = (metadata as { resource_id?: string }).resource_id;
  if (ref.startsWith("xero_") && resourceId) {
    return displayOrDash(resourceId);
  }
  return displayOrDash(ref);
}

export function getTransactionDate(anchor: XeroAnchorRecord): string {
  const metadata = anchor.metadata ?? {};
  const eventType = anchor.event_type ?? "";

  let raw: string | undefined;
  if (eventType === "xero_payment_received") {
    raw = metadata.payment_date ?? anchor.voucher_date ?? metadata.voucher_date;
  } else if (eventType === "xero_transaction_recorded") {
    raw = metadata.transaction_date ?? anchor.voucher_date ?? metadata.voucher_date;
  } else {
    raw = anchor.voucher_date ?? metadata.voucher_date ?? metadata.create_date ?? anchor.timestamp;
  }

  return formatDisplayDate(raw);
}

export function shouldShowDueDate(anchor: XeroAnchorRecord): boolean {
  if (!isInvoiceEvent(anchor)) {
    return false;
  }
  const dueDate = anchor.metadata?.due_date;
  return Boolean(dueDate && String(dueDate).trim() !== "");
}

export function shouldShowStatus(anchor: XeroAnchorRecord): boolean {
  const status = anchor.metadata?.status;
  if (!status || String(status).trim() === "") {
    return false;
  }
  if (anchor.event_type === "xero_transaction_recorded") {
    return false;
  }
  return true;
}

export function getPartyLabel(anchor: XeroAnchorRecord): string {
  if (anchor.event_type === "xero_transaction_recorded") {
    return "Reference";
  }
  return "Contact";
}

export function getPartyValue(anchor: XeroAnchorRecord): string {
  const metadata = anchor.metadata ?? {};
  if (anchor.event_type === "xero_transaction_recorded") {
    return displayOrDash(anchor.reference_id ?? metadata.contact_name);
  }
  return displayOrDash(metadata.contact_name);
}

export function mapBusinessSection(anchor: XeroAnchorRecord): VerifyRow[] {
  return [
    { label: "Organisation", value: getBusinessName(anchor) },
    { label: "Address", value: getBusinessAddress(anchor) },
    { label: "ERP System", value: ERP_DISPLAY_LABEL },
  ];
}

export function mapTransactionSection(anchor: XeroAnchorRecord): VerifyRow[] {
  const metadata = anchor.metadata ?? {};
  const rows: VerifyRow[] = [
    { label: "Reference", value: getReferenceId(anchor) },
    {
      label: "Document Type",
      value: displayOrDash(
        getEventTypeLabel(anchor.event_type) ?? metadata.document_type ?? undefined,
      ),
    },
    { label: getPartyLabel(anchor), value: getPartyValue(anchor) },
    { label: "Date", value: getTransactionDate(anchor) },
  ];

  if (shouldShowDueDate(anchor)) {
    rows.push({
      label: "Due Date",
      value: formatDisplayDate(metadata.due_date),
    });
  }

  rows.push({
    label: "Amount",
    value: formatAmountForDisplay(anchor),
  });

  if (shouldShowStatus(anchor)) {
    const badge = getStatusBadge(metadata.status);
    rows.push({ label: "Status", value: badge.label });
  }

  return rows;
}

export function buildVerificationInstructions(anchor: XeroAnchorRecord): string {
  const metadata = anchor.metadata ?? {};
  const documentType = metadata.document_type ?? "document";
  const timestamp = formatDisplayDate(anchor.timestamp);
  const tenantId = displayOrDash(
    metadata.tenant_id ??
      (metadata as { xero_tenant_id?: string }).xero_tenant_id ??
      anchor.tenant_id,
  );
  const eventLabel = getEventTypeLabel(anchor.event_type);

  let instructions =
    `This ${eventLabel} (${documentType}) from Xero was anchored to the Monad blockchain on ${timestamp}. ` +
    `Original record in Xero organisation ${tenantId}. Verify the content hash and transaction hash below.`;

  if (isAmountPendingEnrichment(anchor)) {
    instructions +=
      " Transaction amount is pending Xero API enrichment and may show as $0.00 until sync completes.";
  }

  return instructions;
}

export function buildPdfEvidenceFields(anchor: XeroAnchorRecord): PdfEvidenceFields {
  const metadata = anchor.metadata ?? {};
  const currency = (anchor.currency ?? "USD").toUpperCase();
  const safeCurrency = SUPPORTED_CURRENCIES.has(currency) ? currency : "USD";

  return {
    documentNumber: getReferenceId(anchor),
    clientName: getPartyValue(anchor),
    dueDate: shouldShowDueDate(anchor)
      ? formatDisplayDate(metadata.due_date)
      : null,
    documentType: displayOrDash(
      metadata.document_type ?? getEventTypeLabel(anchor.event_type),
    ),
    amountFormatted: formatAmountForDisplay(anchor),
    currency: safeCurrency,
  };
}

export function mapXeroVerifyPage(anchor: XeroAnchorRecord): XeroVerifyPageData {
  return {
    businessRows: mapBusinessSection(anchor),
    transactionRows: mapTransactionSection(anchor),
    statusBadge: getStatusBadge(anchor.metadata?.status),
    instructions: buildVerificationInstructions(anchor),
    pdfFields: buildPdfEvidenceFields(anchor),
  };
}
