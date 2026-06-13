"""Xero REST API client with OAuth refresh and retries."""

import logging
import time
from typing import Any

import requests

_logger = logging.getLogger(__name__)

XERO_TOKEN_URL = "https://identity.xero.com/connect/token"
XERO_API_BASE = "https://api.xero.com/api.xro/2.0"
MAX_RETRIES = 3
RETRY_BACKOFF_SEC = 1.5


class XeroClient:
    def __init__(
        self,
        access_token: str,
        tenant_id: str,
        refresh_token: str = "",
        client_id: str = "",
        client_secret: str = "",
    ):
        self.access_token = access_token
        self.tenant_id = tenant_id
        self.refresh_token = refresh_token
        self.client_id = client_id
        self.client_secret = client_secret

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": "Bearer %s" % self.access_token,
            "xero-tenant-id": self.tenant_id,
            "Accept": "application/json",
        }

    def refresh_access_token(self) -> None:
        if not all([self.refresh_token, self.client_id, self.client_secret]):
            raise RuntimeError("OAuth refresh credentials not configured")
        response = requests.post(
            XERO_TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        self.access_token = data["access_token"]
        if data.get("refresh_token"):
            self.refresh_token = data["refresh_token"]
        _logger.info("Xero access token refreshed")

    def _get(self, path: str) -> dict[str, Any]:
        url = "%s/%s" % (XERO_API_BASE, path.lstrip("/"))
        last_error: Exception | None = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.get(url, headers=self._headers, timeout=20)
                if response.status_code == 401 and attempt == 1:
                    self.refresh_access_token()
                    continue
                response.raise_for_status()
                return response.json()
            except Exception as exc:
                last_error = exc
                _logger.warning(
                    "Xero API attempt %s/%s failed: %s", attempt, MAX_RETRIES, exc
                )
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_BACKOFF_SEC * attempt)
        raise RuntimeError(
            "Xero API failed after %s retries: %s" % (MAX_RETRIES, last_error)
        )

    def fetch_document(
        self, event_type: str, tenant_id: str, resource_id: str
    ) -> dict[str, Any]:
        if event_type.startswith("invoice."):
            payload = self._get("Invoices/%s" % resource_id)
            invoices = payload.get("Invoices") or []
            if not invoices:
                raise ValueError("Xero invoice not found: %s" % resource_id)
            return _merge_tenant_document(invoices[0], tenant_id, "Invoice")

        if event_type.startswith("payment."):
            payload = self._get("Payments/%s" % resource_id)
            payments = payload.get("Payments") or []
            if not payments:
                raise ValueError("Xero payment not found: %s" % resource_id)
            return _merge_tenant_document(payments[0], tenant_id, "Payment")

        if event_type.startswith("transaction."):
            payload = self._get("BankTransactions/%s" % resource_id)
            txns = payload.get("BankTransactions") or []
            if not txns:
                raise ValueError("Xero bank transaction not found: %s" % resource_id)
            return _merge_tenant_document(txns[0], tenant_id, "BankTransaction")

        raise ValueError("Unsupported event type for fetch: %s" % event_type)


def _merge_tenant_document(
    document: dict[str, Any], tenant_id: str, document_type: str
) -> dict[str, Any]:
    merged = dict(document)
    merged["tenant_id"] = tenant_id
    merged["document_type"] = document_type
    return merged
