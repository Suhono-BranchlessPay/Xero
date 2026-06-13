import json
from unittest.mock import patch

import pytest

from xero_bp_collector.app import create_app
from xero_bp_collector.config import Settings


def _settings(**overrides):
    base = dict(
        bp_license_key="bp_test_dummy",
        bp_api_url="https://branchlesspay.com/api/v1/anchor",
        xero_client_id="cid",
        xero_client_secret="sec",
        xero_access_token="access",
        xero_refresh_token="refresh",
        xero_tenant_id="tenant-123",
        xero_org_name="Test Org LLC",
        xero_org_address="123 Main St",
        xero_webhook_key="xero_test_key",
        host="127.0.0.1",
        port=8080,
        skip_signature_verify=True,
        failed_queue_dir="data/failed_queue",
    )
    base.update(overrides)
    return Settings(**base)


SAMPLE_DOCS = {
    "invoice.created": {
        "InvoiceID": "inv-1",
        "InvoiceNumber": "INV-0001",
        "Status": "AUTHORISED",
        "Total": 750.0,
        "CurrencyCode": "USD",
        "Contact": {"Name": "John Smith"},
        "Date": "2026-06-12",
    },
    "invoice.updated": {
        "InvoiceID": "inv-1",
        "InvoiceNumber": "INV-0001",
        "Status": "PAID",
        "Total": 750.0,
        "CurrencyCode": "USD",
        "Contact": {"Name": "John Smith"},
        "Date": "2026-06-12",
    },
    "payment.created": {
        "PaymentID": "pay-1",
        "Reference": "PAY-001",
        "Amount": 100.0,
        "CurrencyCode": "USD",
        "Date": "2026-06-12",
        "Contact": {"Name": "Jane Doe"},
    },
    "transaction.created": {
        "BankTransactionID": "txn-1",
        "Reference": "Office supplies",
        "Total": 75.0,
        "CurrencyCode": "USD",
        "Date": "2026-06-12",
    },
}


def _xero_webhook_body(event_type: str, resource_id: str):
    category_map = {
        "invoice.created": ("INVOICE", "CREATE"),
        "invoice.updated": ("INVOICE", "UPDATE"),
        "payment.created": ("PAYMENT", "CREATE"),
        "transaction.created": ("BANKTRANSACTION", "CREATE"),
    }
    category, xero_type = category_map[event_type]
    return {
        "events": [
            {
                "resourceId": resource_id,
                "eventType": xero_type,
                "eventCategory": category,
                "tenantId": "tenant-123",
                "eventDateUtc": "2026-06-12T10:00:00Z",
                "resourceUrl": "https://api.xero.com/api.xro/2.0/test/%s" % resource_id,
            }
        ],
        "firstEventSequence": 1,
        "lastEventSequence": 1,
        "entropy": "test",
    }


@pytest.mark.parametrize("event_type", list(SAMPLE_DOCS.keys()))
@patch("xero_bp_collector.app.AnchorIdempotencyStore")
@patch("xero_bp_collector.app.XeroClient.fetch_document")
@patch("xero_bp_collector.app.BPPoster.post_anchor")
def test_webhook_pipeline_all_events(mock_post, mock_fetch, mock_idem_cls, event_type):
    mock_idem_cls.return_value.get.return_value = None
    mock_fetch.return_value = SAMPLE_DOCS[event_type]
    mock_post.return_value = {
        "ok": True,
        "anchor_id": "test-anchor-%s" % event_type.replace(".", "-"),
        "status": "queued",
    }

    app = create_app(_settings())
    client = app.test_client()
    payload = _xero_webhook_body(event_type, SAMPLE_DOCS[event_type].get("InvoiceID") or SAMPLE_DOCS[event_type].get("PaymentID") or SAMPLE_DOCS[event_type].get("BankTransactionID") or "res-1")
    response = client.post(
        "/webhook/xero",
        data=json.dumps(payload),
        content_type="application/json",
    )

    assert response.status_code == 202
    body = response.get_json()
    assert body["ok"] is True
    assert body["results"][0]["anchor_id"]


def test_intent_to_receive_returns_signature():
    app = create_app(_settings())
    client = app.test_client()
    raw = '{"events":[],"firstEventSequence":0,"lastEventSequence":0,"entropy":"abc"}'
    response = client.post(
        "/webhook/xero",
        data=raw,
        content_type="application/json",
    )
    assert response.status_code == 200
    assert len(response.get_data(as_text=True)) > 10
