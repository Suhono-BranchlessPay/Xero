"""Live E2E — all four Xero event types through the collector pipeline."""

from __future__ import annotations

import json
import os
import sys
from unittest.mock import patch

from xero_bp_collector.app import create_app
from xero_bp_collector.config import get_settings

SAMPLE_DOCS = {
    "invoice.created": {
        "InvoiceID": "inv-sample-1",
        "InvoiceNumber": "INV-E2E-001",
        "Status": "AUTHORISED",
        "Total": 1500.0,
        "CurrencyCode": "USD",
        "Contact": {"Name": "Acme Corp"},
        "Date": "2026-06-12",
        "DueDate": "2026-06-12",
    },
    "invoice.updated": {
        "InvoiceID": "inv-sample-1",
        "InvoiceNumber": "INV-E2E-001",
        "Status": "PAID",
        "Total": 1500.0,
        "CurrencyCode": "USD",
        "Contact": {"Name": "Acme Corp"},
        "Date": "2026-06-12",
    },
    "payment.created": {
        "PaymentID": "pay-sample-1",
        "Reference": "PAY-E2E-001",
        "Amount": 500.0,
        "CurrencyCode": "USD",
        "Date": "2026-06-12",
        "Contact": {"Name": "Acme Corp"},
    },
    "transaction.created": {
        "BankTransactionID": "txn-sample-1",
        "Reference": "Office supplies",
        "Total": 75.0,
        "CurrencyCode": "USD",
        "Date": "2026-06-12",
    },
}

CATEGORY_MAP = {
    "invoice.created": ("INVOICE", "CREATE", "inv-sample-1"),
    "invoice.updated": ("INVOICE", "UPDATE", "inv-sample-1-upd"),
    "payment.created": ("PAYMENT", "CREATE", "pay-sample-1"),
    "transaction.created": ("BANKTRANSACTION", "CREATE", "txn-sample-1"),
}


def run_event(app, client, event_type: str) -> dict:
    document = SAMPLE_DOCS[event_type]
    category, xero_type, resource_id = CATEGORY_MAP[event_type]

    def _fetch(*_args, **_kwargs):
        return document

    payload = {
        "events": [
            {
                "resourceId": resource_id,
                "eventType": xero_type,
                "eventCategory": category,
                "tenantId": app.config["SETTINGS"].xero_tenant_id or "tenant-e2e",
                "eventDateUtc": "2026-06-13T12:00:00Z",
                "resourceUrl": "https://api.xero.com/api.xro/2.0/test/%s" % resource_id,
            }
        ],
        "firstEventSequence": 1,
        "lastEventSequence": 1,
        "entropy": "e2e",
    }

    with patch("xero_bp_collector.app.XeroClient.fetch_document", side_effect=_fetch), patch(
        "xero_bp_collector.app.AnchorIdempotencyStore"
    ) as mock_idem:
        mock_idem.return_value.get.return_value = None
        response = client.post("/webhook/xero", json=payload)

    body = response.get_json() or {}
    result = (body.get("results") or [{}])[0] if body.get("results") else body
    return {
        "event_type": event_type,
        "http_status": response.status_code,
        "ok": result.get("ok"),
        "anchor_id": result.get("anchor_id"),
        "verify_url": result.get("verify_url"),
        "error": result.get("error"),
    }


def main() -> int:
    settings = get_settings()
    if not settings.bp_license_key:
        print("BP_LICENSE_KEY is not configured", file=sys.stderr)
        return 1

    app = create_app(settings)
    client = app.test_client()
    results = [run_event(app, client, event_type) for event_type in SAMPLE_DOCS]
    print(json.dumps(results, indent=2))
    failed = [r for r in results if r.get("http_status") not in (200, 202) or not r.get("ok")]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
