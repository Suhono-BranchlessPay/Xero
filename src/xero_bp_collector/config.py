"""Environment configuration — no hardcoded credentials."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

_PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
load_dotenv(os.path.join(_PROJECT_ROOT, ".env"), override=True)


@dataclass(frozen=True)
class Settings:
    bp_license_key: str
    bp_api_url: str
    xero_client_id: str
    xero_client_secret: str
    xero_access_token: str
    xero_refresh_token: str
    xero_tenant_id: str
    xero_org_name: str
    xero_org_address: str
    xero_webhook_key: str
    host: str
    port: int
    skip_signature_verify: bool
    failed_queue_dir: str


def get_settings() -> Settings:
    root = _PROJECT_ROOT
    return Settings(
        bp_license_key=os.getenv("BP_LICENSE_KEY", "").strip(),
        bp_api_url=os.getenv(
            "BP_API_URL", "https://branchlesspay.com/api/v1/anchor"
        ).rstrip("/"),
        xero_client_id=os.getenv("XERO_CLIENT_ID", "").strip(),
        xero_client_secret=os.getenv("XERO_CLIENT_SECRET", "").strip(),
        xero_access_token=os.getenv("XERO_ACCESS_TOKEN", "").strip(),
        xero_refresh_token=os.getenv("XERO_REFRESH_TOKEN", "").strip(),
        xero_tenant_id=os.getenv("XERO_TENANT_ID", "").strip(),
        xero_org_name=os.getenv("XERO_ORG_NAME", "").strip(),
        xero_org_address=os.getenv("XERO_ORG_ADDRESS", "").strip(),
        xero_webhook_key=os.getenv("XERO_WEBHOOK_KEY", "").strip(),
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8080")),
        skip_signature_verify=os.getenv("XERO_SKIP_SIGNATURE_VERIFY", "0").strip()
        in ("1", "true", "yes"),
        failed_queue_dir=os.getenv(
            "FAILED_QUEUE_DIR", os.path.join(root, "data", "failed_queue")
        ),
    )
