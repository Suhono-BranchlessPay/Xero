"""Map Xero documents to BranchlessPay anchor payload."""

from datetime import datetime, timezone
from typing import Any

EVENT_TYPE_MAP = {
    "invoice.created": "xero_invoice_created",
    "invoice.updated": "xero_invoice_updated",
    "payment.created": "xero_payment_received",
    "transaction.created": "xero_transaction_recorded",
}

DOCUMENT_TYPE_MAP = {
    "invoice.created": "Invoice",
    "invoice.updated": "Invoice",
    "payment.created": "Payment",
    "transaction.created": "Bank Transaction",
}

ERP_DISPLAY_LABEL = "Xero"


def map_event_type(xero_event: str) -> str:
    mapped = EVENT_TYPE_MAP.get(xero_event)
    if not mapped:
        raise ValueError("Unsupported Xero event: %s" % xero_event)
    return mapped


def normalize_to_bp_payload(
    xero_event: str,
    document: dict[str, Any],
    *,
    tenant_id: str = "",
    org_name: str = "",
    org_address: str = "",
    webhook_timestamp: str = "",
) -> dict[str, Any]:
    event_type = map_event_type(xero_event)
    document_type = DOCUMENT_TYPE_MAP[xero_event]
    amount, currency = _extract_amount(document, xero_event)
    reference_id = _extract_reference_id(document, xero_event)
    contact_name = _extract_contact_name(document)
    status = str(document.get("Status") or document.get("status") or "UNKNOWN").upper()
    business = org_name or _extract_org_name(document)
    address = org_address or _extract_org_address(document)
    voucher_date = _extract_voucher_date(document, xero_event)
    timestamp = _extract_timestamp(document, webhook_timestamp)
    resolved_tenant_id = tenant_id or str(document.get("tenant_id") or "")

    metadata: dict[str, Any] = {
        "erp": "xero",
        "erp_system": ERP_DISPLAY_LABEL,
        "company_name": business,
        "business_name": business,
        "business_address": address,
        "tenant_id": resolved_tenant_id,
        "document_type": document_type,
        "contact_name": contact_name,
        "status": status,
        "xero_id": str(document.get("InvoiceID") or document.get("PaymentID") or document.get("BankTransactionID") or document.get("id") or ""),
        "xero_event": xero_event,
        "voucher_date": voucher_date,
        "create_date": voucher_date,
    }

    if xero_event.startswith("invoice."):
        metadata["invoice_number"] = reference_id
        metadata["due_date"] = _extract_due_date(document)
    elif xero_event.startswith("payment."):
        metadata["payment_date"] = voucher_date
    elif xero_event.startswith("transaction."):
        metadata["transaction_date"] = voucher_date

    payload: dict[str, Any] = {
        "event_type": event_type,
        "reference_id": reference_id,
        "amount": amount,
        "currency": currency,
        "voucher_date": voucher_date,
        "timestamp": timestamp,
        "metadata": metadata,
    }

    if business:
        payload["business_name"] = business
    if address:
        payload["business_address"] = address
    if resolved_tenant_id:
        payload["tenant_id"] = resolved_tenant_id
    payload["erp_system"] = ERP_DISPLAY_LABEL

    return payload


def _parse_amount(raw: Any) -> float:
    if raw is None:
        return 0.0
    text = str(raw).strip().replace(",", "")
    if not text:
        return 0.0
    return float(text)


def _extract_amount(document: dict[str, Any], event_type: str) -> tuple[float, str]:
    if event_type.startswith("invoice."):
        for key in ("AmountDue", "Total", "amountDue", "total"):
            if document.get(key) is not None:
                return _parse_amount(document[key]), str(document.get("CurrencyCode") or "USD")
    if event_type.startswith("payment."):
        amount = document.get("Amount")
        if amount is not None:
            return _parse_amount(amount), str(document.get("CurrencyCode") or "USD")
    if event_type.startswith("transaction."):
        total = document.get("Total")
        if total is not None:
            return _parse_amount(total), str(document.get("CurrencyCode") or "USD")
    return 0.0, str(document.get("CurrencyCode") or "USD")


def _extract_reference_id(document: dict[str, Any], event_type: str) -> str:
    if event_type.startswith("invoice."):
        return str(document.get("InvoiceNumber") or document.get("InvoiceID") or "unknown")
    if event_type.startswith("payment."):
        return str(document.get("Reference") or document.get("PaymentID") or "unknown")
    if event_type.startswith("transaction."):
        return str(document.get("Reference") or document.get("BankTransactionID") or "unknown")
    return str(document.get("id") or "unknown")


def _extract_contact_name(document: dict[str, Any]) -> str:
    contact = document.get("Contact")
    if isinstance(contact, dict):
        name = contact.get("Name")
        if name:
            return str(name)
    return "Unknown"


def _extract_org_name(document: dict[str, Any]) -> str:
    return str(document.get("org_name") or document.get("business_name") or "Xero Organisation")


def _extract_org_address(document: dict[str, Any]) -> str:
    direct = document.get("org_address") or document.get("business_address")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()
    return ""


def _extract_voucher_date(document: dict[str, Any], event_type: str) -> str:
    keys = ("Date", "UpdatedDateUTC", "date")
    if event_type.startswith("payment."):
        keys = ("Date", "UpdatedDateUTC")
    if event_type.startswith("transaction."):
        keys = ("Date",)
    for key in keys:
        value = document.get(key)
        if value:
            return _date_only(str(value))
    return ""


def _extract_due_date(document: dict[str, Any]) -> str:
    value = document.get("DueDate")
    if value:
        return _date_only(str(value))
    return ""


def _extract_timestamp(document: dict[str, Any], webhook_timestamp: str) -> str:
    if webhook_timestamp:
        if "T" in webhook_timestamp:
            return webhook_timestamp.replace(" ", "T")
        return "%sT00:00:00Z" % _date_only(webhook_timestamp)
    for key in ("UpdatedDateUTC", "Date"):
        value = document.get(key)
        if value:
            text = str(value)
            if text.startswith("/Date("):
                return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            if "T" in text:
                return text.replace(" ", "T")
            return "%sT00:00:00Z" % _date_only(text)
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _date_only(value: str) -> str:
    if value.startswith("/Date("):
        return value
    return value.split("T")[0].split(" ")[0]
