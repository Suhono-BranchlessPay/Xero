"""Xero webhook HMAC-SHA256 verification (x-xero-signature header)."""

import base64
import hashlib
import hmac
from typing import Mapping


def compute_signature(webhook_key: str, raw_body: bytes | str) -> str:
    if isinstance(raw_body, str):
        raw_body = raw_body.encode("utf-8")
    digest = hmac.new(
        webhook_key.encode("utf-8"),
        raw_body,
        digestmod=hashlib.sha256,
    ).digest()
    return base64.b64encode(digest).decode("utf-8")


def verify_signature(
    webhook_key: str,
    raw_body: bytes | str,
    signature_header: str | None,
) -> bool:
    if not webhook_key or not signature_header:
        return False
    expected = compute_signature(webhook_key, raw_body)
    return hmac.compare_digest(expected, signature_header.strip())


def intent_to_receive_response(webhook_key: str, raw_body: bytes | str) -> str:
    """Return hashed signature body for Xero intent-to-receive validation."""
    return compute_signature(webhook_key, raw_body)


def get_signature_header(headers: Mapping[str, str]) -> str | None:
    for key, value in headers.items():
        if key.lower() == "x-xero-signature":
            return value
    return None
