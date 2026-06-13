"""Create a test AUTHORISED sales invoice in Xero (triggers INVOICE CREATE webhook)."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone

import requests
from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT, ".env"), override=True)

API = "https://api.xero.com/api.xro/2.0"
TOKEN_URL = "https://identity.xero.com/connect/token"


def _require(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        print("ERROR: %s is not set in .env - run scripts/oauth_setup.ps1 first" % name)
        sys.exit(1)
    return value


def _headers(access: str, tenant: str) -> dict[str, str]:
    return {
        "Authorization": "Bearer %s" % access,
        "xero-tenant-id": tenant,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def _refresh_access_token(refresh: str, client_id: str, client_secret: str) -> str:
    basic = requests.auth._basic_auth_str(client_id, client_secret)
    resp = requests.post(
        TOKEN_URL,
        data={"grant_type": "refresh_token", "refresh_token": refresh},
        headers={
            "Authorization": basic,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def _get_revenue_account_code(access: str, tenant: str) -> str:
    override = os.getenv("XERO_SALES_ACCOUNT_CODE", "").strip()
    if override:
        return override
    resp = requests.get(
        "%s/Accounts" % API,
        headers=_headers(access, tenant),
        params={"where": 'Type=="REVENUE" && Status=="ACTIVE"'},
        timeout=20,
    )
    resp.raise_for_status()
    for acc in resp.json().get("Accounts") or []:
        code = str(acc.get("Code") or "").strip()
        if code:
            print("Using revenue account code: %s (%s)" % (code, acc.get("Name", "")))
            return code
    raise RuntimeError(
        "No active REVENUE account found. Set XERO_SALES_ACCOUNT_CODE in .env"
    )


def _get_tax_type(access: str, tenant: str) -> str:
    override = os.getenv("XERO_TAX_TYPE", "").strip()
    if override:
        return override
    resp = requests.get(
        "%s/TaxRates" % API,
        headers=_headers(access, tenant),
        timeout=20,
    )
    resp.raise_for_status()
    rates = resp.json().get("TaxRates") or []
    for preferred in ("NONE", "EXEMPTOUTPUT", "OUTPUT", "OUTPUT2", "TAX001"):
        for rate in rates:
            if rate.get("TaxType") == preferred and rate.get("Status") == "ACTIVE":
                print("Using tax type: %s" % preferred)
                return preferred
    for rate in rates:
        tax_type = str(rate.get("TaxType") or "").strip()
        if tax_type and rate.get("Status") == "ACTIVE":
            print("Using tax type: %s" % tax_type)
            return tax_type
    return "NONE"


def main() -> int:
    access = _require("XERO_ACCESS_TOKEN")
    tenant = _require("XERO_TENANT_ID")
    client_id = os.getenv("XERO_CLIENT_ID", "").strip()
    client_secret = os.getenv("XERO_CLIENT_SECRET", "").strip()
    refresh = os.getenv("XERO_REFRESH_TOKEN", "").strip()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    ref = "BP-E2E-%s" % stamp
    today = datetime.now(timezone.utc).date()
    due = today + timedelta(days=30)

    try:
        account_code = _get_revenue_account_code(access, tenant)
        tax_type = _get_tax_type(access, tenant)
    except requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code == 401 and refresh:
            access = _refresh_access_token(refresh, client_id, client_secret)
            account_code = _get_revenue_account_code(access, tenant)
            tax_type = _get_tax_type(access, tenant)
        else:
            raise

    payload = {
        "Invoices": [
            {
                "Type": "ACCREC",
                "Contact": {"Name": "BranchlessPay E2E Test"},
                "Date": today.isoformat(),
                "DueDate": due.isoformat(),
                "LineAmountTypes": "Exclusive",
                "LineItems": [
                    {
                        "Description": "Audit Shield live webhook test %s" % stamp,
                        "Quantity": 1,
                        "UnitAmount": 125.0,
                        "AccountCode": account_code,
                        "TaxType": tax_type,
                    }
                ],
                "Reference": ref,
                "Status": "AUTHORISED",
            }
        ]
    }

    def post_invoice(token: str) -> requests.Response:
        return requests.post(
            "%s/Invoices" % API,
            headers=_headers(token, tenant),
            json=payload,
            timeout=30,
        )

    response = post_invoice(access)
    if response.status_code == 401 and refresh and client_id and client_secret:
        access = _refresh_access_token(refresh, client_id, client_secret)
        response = post_invoice(access)

    if response.status_code >= 400:
        print("ERROR: Xero API HTTP %s" % response.status_code)
        print(response.text)
        return 1

    data = response.json()
    invoices = data.get("Invoices") or []
    if not invoices:
        print("ERROR: no invoice returned")
        print(json.dumps(data, indent=2))
        return 1

    inv = invoices[0]
    invoice_id = inv.get("InvoiceID", "")
    invoice_number = inv.get("InvoiceNumber", ref)
    total = inv.get("Total", 0)

    print("")
    print("=== Test invoice created ===")
    print("InvoiceID:     %s" % invoice_id)
    print("InvoiceNumber: %s" % invoice_number)
    print("Reference:     %s" % ref)
    print("Total:         %s" % total)
    print("")
    print("Webhook target: https://branchlesspay.com/api/v1/webhook/xero")
    print("Expected event: INVOICE CREATE -> xero_invoice_created")
    print("erp_doc_id (BP): xero_%s_create" % invoice_id)
    print("")
    print("Check Xero developer portal -> Webhooks -> recent deliveries (expect 202).")
    print("Verify page (after anchor_id known): https://branchlesspay.com/verify/{anchor_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
