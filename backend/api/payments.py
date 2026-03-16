"""Payments API: rules and history; HSP-ready flow."""
from flask import Blueprint, request, jsonify

from backend.services import ai_payments, hsp_client

payments_bp = Blueprint("payments", __name__)


def _evaluate_rules_now():
    """Run payment rule evaluation once (same logic as scheduler). Returns number of payments recorded."""
    from config import settings
    from backend.services import chain
    address = (getattr(settings, "WALLET_ADDRESS", "") or "").strip() or "0x0000000000000000000000000000000000000000"
    balance_data = chain.get_balance(address)
    try:
        balance = float(balance_data.get("eth", 0))
    except (TypeError, ValueError):
        balance = 0.0
    triggered = ai_payments.evaluate_rules(balance)
    for rule in triggered:
        symbol = rule.get("symbol") or "HSK"
        req = hsp_client.create_payment_request(rule["amount"], rule["recipient"], rule["id"])
        ai_payments.record_payment(rule["id"], rule["amount"], rule["recipient"], status=req["status"], symbol=symbol)
    return len(triggered)


@payments_bp.route("/payment-rules", methods=["GET"])
def list_rules():
    return {"rules": ai_payments.list_rules()}


@payments_bp.route("/payment-rules", methods=["POST"])
def create_rule():
    data = request.get_json() or {}
    trigger_type = data.get("trigger_type", "balance_above")
    trigger_value = data.get("trigger_value", "0")
    amount = data.get("amount", "0")
    recipient = data.get("recipient", "")
    symbol = (data.get("symbol") or "HSK").strip().upper() or "HSK"
    if not recipient:
        return jsonify({"error": "recipient required"}), 400
    rule = ai_payments.add_rule(trigger_type, trigger_value, amount, recipient, symbol=symbol)
    return jsonify(rule), 201


@payments_bp.route("/payments", methods=["GET"])
def list_payments():
    return {"payments": ai_payments.list_payments()}


@payments_bp.route("/payments/evaluate-now", methods=["POST"])
def evaluate_now():
    """Evaluate payment rules immediately using current wallet balance. For demo: see payments in history without waiting for scheduler."""
    count = _evaluate_rules_now()
    return jsonify({"evaluated": True, "payments_triggered": count, "payments": ai_payments.list_payments()})


@payments_bp.route("/payments/execute", methods=["POST"])
def execute_payment():
    """Create HSP payment request (stub) and record in history."""
    data = request.get_json() or {}
    amount = data.get("amount", "0")
    recipient = data.get("recipient", "")
    rule_id = data.get("rule_id", "")
    symbol = (data.get("symbol") or "HSK").strip().upper() or "HSK"
    if not amount or not recipient:
        return jsonify({"error": "amount and recipient required"}), 400
    req = hsp_client.create_payment_request(amount, recipient, reference=rule_id)
    req["symbol"] = symbol
    record = ai_payments.record_payment(rule_id, amount, recipient, status=req["status"], symbol=symbol)
    return jsonify({"request": req, "record": record}), 201
