"""Tests for payment rules and HSP stub."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.services import ai_payments, hsp_client


def test_add_rule():
    rule = ai_payments.add_rule("balance_above", "10", "0.5", "0x1234567890123456789012345678901234567890")
    assert rule["amount"] == "0.5"
    assert rule["recipient"] == "0x1234567890123456789012345678901234567890"
    assert "id" in rule


def test_hsp_create_request():
    req = hsp_client.create_payment_request("0.1", "0xabc")
    assert "request_id" in req
    assert req["status"] == "created"
