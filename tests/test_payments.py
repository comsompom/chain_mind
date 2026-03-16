"""Tests for payment rules and HSP stub."""
from backend.services import ai_payments, hsp_client

_ADDR = "0x1234567890123456789012345678901234567890"


def test_add_rule():
    rule = ai_payments.add_rule("balance_above", "10", "0.5", _ADDR)
    assert rule["amount"] == "0.5"
    assert rule["recipient"] == _ADDR
    assert "id" in rule
    assert rule.get("symbol", "HSK") == "HSK"


def test_add_rule_with_symbol():
    rule = ai_payments.add_rule("balance_below", "1", "0.002", _ADDR, symbol="ETH")
    assert rule["symbol"] == "ETH"
    assert rule["trigger_type"] == "balance_below"


def test_list_rules():
    rules = ai_payments.list_rules()
    assert isinstance(rules, list)


def test_get_rule():
    rule = ai_payments.add_rule("balance_above", "5", "0.1", _ADDR)
    found = ai_payments.get_rule(rule["id"])
    assert found is not None
    assert found["id"] == rule["id"]
    assert ai_payments.get_rule("nonexistent_id") is None


def test_evaluate_rules_balance_above():
    rid = ai_payments.add_rule("balance_above", "1", "0.01", _ADDR)["id"]
    to_run = ai_payments.evaluate_rules(2.0)  # balance 2 >= 1
    assert any(r["id"] == rid for r in to_run)
    to_run_low = ai_payments.evaluate_rules(0.5)  # balance 0.5 < 1
    assert not any(r["id"] == rid for r in to_run_low)


def test_evaluate_rules_balance_below():
    rule = ai_payments.add_rule("balance_below", "10", "0.01", _ADDR)
    to_run = ai_payments.evaluate_rules(5.0)  # 5 <= 10
    assert any(r["id"] == rule["id"] for r in to_run)


def test_update_rule():
    rule = ai_payments.add_rule("balance_above", "0", "0.1", _ADDR)
    updated = ai_payments.update_rule(rule["id"], enabled=False)
    assert updated is not None
    assert updated["enabled"] is False
    assert ai_payments.update_rule("nonexistent", enabled=True) is None


def test_delete_rule():
    rule = ai_payments.add_rule("balance_above", "100", "0.1", _ADDR)
    ok = ai_payments.delete_rule(rule["id"])
    assert ok is True
    assert ai_payments.get_rule(rule["id"]) is None
    assert ai_payments.delete_rule("nonexistent") is False


def test_record_payment_and_list():
    ai_payments.record_payment("rule_1", "0.05", _ADDR, status="created", symbol="HSK")
    payments = ai_payments.list_payments()
    assert isinstance(payments, list)
    assert any(p.get("amount") == "0.05" and p.get("symbol") == "HSK" for p in payments)


def test_hsp_create_request():
    req = hsp_client.create_payment_request("0.1", "0xabc")
    assert "request_id" in req
    assert req["status"] == "created"
