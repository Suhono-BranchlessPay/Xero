"""Parse Xero webhook JSON payload (batched events)."""

from dataclasses import dataclass
from typing import Any


ANCHOR_EVENTS = frozenset(
    {
        "invoice.created",
        "invoice.updated",
        "payment.created",
        "transaction.created",
    }
)

_CATEGORY_TYPE_MAP = {
    ("INVOICE", "CREATE"): "invoice.created",
    ("INVOICE", "UPDATE"): "invoice.updated",
    ("PAYMENT", "CREATE"): "payment.created",
    ("BANKTRANSACTION", "CREATE"): "transaction.created",
}


@dataclass(frozen=True)
class WebhookEvent:
    event_type: str
    resource_id: str
    tenant_id: str
    timestamp: str
    resource_url: str
    raw: dict[str, Any]


def is_intent_to_receive(body: dict[str, Any]) -> bool:
    return bool(body.get("intentToReceive") or body.get("challenge"))


def map_xero_event(category: str, event_type: str) -> str | None:
    key = (category.strip().upper(), event_type.strip().upper())
    return _CATEGORY_TYPE_MAP.get(key)


def parse_webhook_events(body: dict[str, Any]) -> list[WebhookEvent]:
    events_raw = body.get("events")
    if not isinstance(events_raw, list):
        raise ValueError("Missing Xero events array")

    parsed: list[WebhookEvent] = []
    for item in events_raw:
        if not isinstance(item, dict):
            continue
        category = str(item.get("eventCategory") or "").strip()
        xero_type = str(item.get("eventType") or "").strip()
        mapped = map_xero_event(category, xero_type)
        if not mapped:
            continue

        resource_id = str(item.get("resourceId") or "").strip()
        tenant_id = str(item.get("tenantId") or "").strip()
        if not resource_id:
            raise ValueError("Missing resourceId for %s.%s" % (category, xero_type))
        if not tenant_id:
            raise ValueError("Missing tenantId")

        parsed.append(
            WebhookEvent(
                event_type=mapped,
                resource_id=resource_id,
                tenant_id=tenant_id,
                timestamp=str(item.get("eventDateUtc") or "").strip(),
                resource_url=str(item.get("resourceUrl") or "").strip(),
                raw=item,
            )
        )

    if not parsed:
        raise ValueError("No anchorable events in payload")
    return parsed
