from xero_bp_collector.normalizer import normalize_to_bp_payload


def test_normalize_invoice_created():
    document = {
        "InvoiceID": "inv-1",
        "InvoiceNumber": "INV-0001",
        "Status": "AUTHORISED",
        "Total": 750.0,
        "AmountDue": 750.0,
        "CurrencyCode": "USD",
        "Contact": {"Name": "John Smith"},
        "DueDate": "/Date(1781308800000+0000)/",
        "Date": "/Date(1778716800000+0000)/",
    }
    payload = normalize_to_bp_payload(
        "invoice.created",
        document,
        tenant_id="tenant-123",
        webhook_timestamp="2026-06-12T10:00:00Z",
    )
    assert payload["event_type"] == "xero_invoice_created"
    assert payload["reference_id"] == "INV-0001"
    assert payload["amount"] == 750.0
    assert payload["metadata"]["tenant_id"] == "tenant-123"
    assert payload["metadata"]["contact_name"] == "John Smith"
    assert payload["erp_system"] == "Xero"


def test_normalize_payment():
    document = {
        "PaymentID": "pay-1",
        "Reference": "PAY-001",
        "Amount": 100.0,
        "CurrencyCode": "USD",
        "Date": "/Date(1778716800000+0000)/",
        "Contact": {"Name": "Jane Doe"},
    }
    payload = normalize_to_bp_payload("payment.created", document, tenant_id="tenant-123")
    assert payload["event_type"] == "xero_payment_received"
    assert payload["reference_id"] == "PAY-001"
    assert payload["amount"] == 100.0


def test_normalize_transaction():
    document = {
        "BankTransactionID": "txn-1",
        "Reference": "Office supplies",
        "Total": 75.0,
        "CurrencyCode": "USD",
        "Date": "/Date(1778716800000+0000)/",
    }
    payload = normalize_to_bp_payload("transaction.created", document, tenant_id="tenant-123")
    assert payload["event_type"] == "xero_transaction_recorded"
    assert payload["reference_id"] == "Office supplies"
