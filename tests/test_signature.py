"""Xero webhook signature tests."""

from xero_bp_collector.signature import (
    compute_signature,
    intent_to_receive_response,
    verify_signature,
)


def test_compute_and_verify_signature():
    key = "test_webhook_key"
    body = b'{"events":[],"firstEventSequence":0,"lastEventSequence":0}'
    sig = compute_signature(key, body)
    assert verify_signature(key, body, sig)
    assert not verify_signature(key, body, "invalid")


def test_intent_to_receive_response():
    key = "test_webhook_key"
    body = '{"events":[]}'
    assert intent_to_receive_response(key, body) == compute_signature(key, body)
