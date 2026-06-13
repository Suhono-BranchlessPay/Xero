import React from "react";

import {
  buildPdfEvidenceFields,
  buildVerificationInstructions,
  getStatusBadge,
  isXeroAnchor,
  mapBusinessSection,
  mapTransactionSection,
  type XeroAnchorRecord,
} from "./xeroVerifyMapping";

const BADGE_CLASS: Record<string, string> = {
  unpaid: "badge badge--unpaid",
  paid: "badge badge--paid",
  overdue: "badge badge--overdue",
  draft: "badge badge--draft",
  partial: "badge badge--partial",
  saved: "badge badge--saved",
  sent: "badge badge--sent",
  unknown: "badge badge--unknown",
};

export function XeroVerifySections({ anchor }: { anchor: XeroAnchorRecord }) {
  if (!isXeroAnchor(anchor)) {
    return null;
  }

  const businessRows = mapBusinessSection(anchor);
  const transactionRows = mapTransactionSection(anchor);
  const statusBadge = getStatusBadge(anchor.metadata?.status);
  const instructions = buildVerificationInstructions(anchor);
  const pdfFields = buildPdfEvidenceFields(anchor);

  return (
    <div className="xero-verify">
      <section aria-label="Organisation Information">
        <h2>Organisation Information</h2>
        {businessRows.map((row) => (
          <div key={row.label} className="verify-row">
            <span>{row.label}</span>
            <span>{row.value}</span>
          </div>
        ))}
      </section>

      <section aria-label="Transaction Details">
        <h2>Transaction Details</h2>
        {transactionRows.map((row) =>
          row.label === "Status" ? (
            <div key={row.label} className="verify-row">
              <span>{row.label}</span>
              <span className={BADGE_CLASS[statusBadge.variant]}>
                {statusBadge.label}
              </span>
            </div>
          ) : (
            <div key={row.label} className="verify-row">
              <span>{row.label}</span>
              <span>{row.value}</span>
            </div>
          ),
        )}
      </section>

      <section aria-label="Verification Instructions">
        <p>{instructions}</p>
      </section>

      <section aria-label="PDF Evidence Fields" hidden>
        <pre>{JSON.stringify(pdfFields, null, 2)}</pre>
      </section>
    </div>
  );
}
