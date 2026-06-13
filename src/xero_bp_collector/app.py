"""Flask webhook receiver — M1 + M2 pipeline."""

import json
import logging
from typing import Any

from flask import Flask, Request, jsonify, request

from .bp_poster import BPPoster
from .config import get_settings
from .idempotency import AnchorIdempotencyStore
from .normalizer import normalize_to_bp_payload
from .queue_store import FailedQueue
from .signature import (
    get_signature_header,
    intent_to_receive_response,
    verify_signature,
)
from .webhook_parser import ANCHOR_EVENTS, is_intent_to_receive, parse_webhook_events
from .xero_client import XeroClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
_logger = logging.getLogger(__name__)


def create_app(settings=None) -> Flask:
    settings = settings or get_settings()
    app = Flask(__name__)
    app.config["SETTINGS"] = settings

    @app.get("/health")
    def health():
        return jsonify({"ok": True, "service": "xero-bp-collector"}), 200

    @app.get("/webhook/xero")
    @app.post("/webhook/xero")
    def xero_webhook():
        if request.method == "GET":
            return jsonify({"ok": True, "verification": "ping"}), 200
        return _handle_webhook(request, settings)

    return app


def _handle_webhook(req: Request, settings) -> tuple[Any, int]:
    raw_body = req.get_data(cache=True)

    if not settings.skip_signature_verify and settings.xero_webhook_key:
        signature_header = get_signature_header(req.headers)
        if not verify_signature(settings.xero_webhook_key, raw_body, signature_header):
            _logger.warning("Invalid Xero webhook signature")
            return jsonify({"ok": False, "error": "unauthorized"}), 401
    elif settings.skip_signature_verify:
        _logger.warning("Signature verification skipped (dev mode)")

    try:
        body = json.loads(raw_body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return jsonify({"ok": False, "error": "invalid json"}), 400

    if is_intent_to_receive(body) or not body.get("events"):
        if settings.xero_webhook_key:
            hashed = intent_to_receive_response(settings.xero_webhook_key, raw_body)
            return hashed, 200, {"Content-Type": "text/plain"}
        return jsonify({"ok": True, "verification": "intent"}), 200

    try:
        events = parse_webhook_events(body)
    except ValueError as exc:
        _logger.warning("Webhook parse error: %s", exc)
        return jsonify({"ok": False, "error": str(exc)}), 400

    results = []
    for event in events:
        result, status = _process_event(event, settings)
        results.append(result)
        if status >= 400 and len(events) == 1:
            return jsonify(result), status

    return jsonify({"ok": True, "results": results}), 202


def _process_event(event, settings) -> tuple[dict[str, Any], int]:
    _logger.info(
        "Webhook received event=%s resource_id=%s tenant_id=%s",
        event.event_type,
        event.resource_id,
        event.tenant_id,
    )

    if event.event_type not in ANCHOR_EVENTS:
        return {"ok": True, "ignored": event.event_type}, 200

    idempotency = AnchorIdempotencyStore()
    idem_key = AnchorIdempotencyStore.make_key(
        event.tenant_id, event.event_type, event.resource_id
    )
    cached = idempotency.get(idem_key)
    if cached:
        return cached, 202

    if not settings.xero_access_token:
        return {"ok": False, "error": "xero not configured"}, 503

    tenant_id = event.tenant_id or settings.xero_tenant_id
    client = XeroClient(
        access_token=settings.xero_access_token,
        tenant_id=tenant_id,
        refresh_token=settings.xero_refresh_token,
        client_id=settings.xero_client_id,
        client_secret=settings.xero_client_secret,
    )

    try:
        document = client.fetch_document(
            event.event_type, tenant_id, event.resource_id
        )
    except Exception as exc:
        _logger.exception("Xero fetch failed: %s", exc)
        return {"ok": False, "error": "xero fetch failed"}, 502

    try:
        bp_payload = normalize_to_bp_payload(
            event.event_type,
            document,
            tenant_id=tenant_id,
            org_name=settings.xero_org_name,
            org_address=settings.xero_org_address,
            webhook_timestamp=event.timestamp,
        )
    except (TypeError, ValueError) as exc:
        _logger.exception("Normalize failed: %s", exc)
        return {"ok": False, "error": "normalize failed", "detail": str(exc)}, 422

    poster = BPPoster(
        license_key=settings.bp_license_key,
        api_url=settings.bp_api_url,
        queue=FailedQueue(settings.failed_queue_dir),
    )

    try:
        result = poster.post_anchor(bp_payload)
    except Exception as exc:
        _logger.exception("BP post failed: %s", exc)
        return {"ok": False, "error": str(exc)}, 502

    if not result.get("ok"):
        return result, 502

    anchor_id = result.get("anchor_id")
    response = {
        "ok": True,
        "event_type": event.event_type,
        "reference_id": bp_payload["reference_id"],
        "anchor_id": anchor_id,
        "verify_url": "https://branchlesspay.com/verify/%s" % anchor_id if anchor_id else None,
        "status": result.get("status"),
        "idempotent": False,
    }
    idempotency.save(idem_key, {**response, "idempotent": True})
    _logger.info("Pipeline complete verify_url=%s", response.get("verify_url"))
    return response, 202


if __name__ == "__main__":
    cfg = get_settings()
    create_app(cfg).run(host=cfg.host, port=cfg.port, debug=False)
