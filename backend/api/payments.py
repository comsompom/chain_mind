"""Payments API: rules and history; HSP-ready flow."""
from flask import Blueprint, request, jsonify

from backend.services import ai_payments, hsp_client

payments_bp = Blueprint("payments", __name__)


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
    if not recipient:
        return jsonify({"error": "recipient required"}), 400
    rule = ai_payments.add_rule(trigger_type, trigger_value, amount, recipient)
    return jsonify(rule), 201


@payments_bp.route("/payments", methods=["GET"])
def list_payments():
    return {"payments": ai_payments.list_payments()}


@payments_bp.route("/payments/execute", methods=["POST"])
def execute_payment():
    """Create HSP payment request (stub) and record in history."""
    data = request.get_json() or {}
    amount = data.get("amount", "0")
    recipient = data.get("recipient", "")
    rule_id = data.get("rule_id", "")
    if not amount or not recipient:
        return jsonify({"error": "amount and recipient required"}), 400
    req = hsp_client.create_payment_request(amount, recipient, reference=rule_id)
    record = ai_payments.record_payment(rule_id, amount, recipient, status=req["status"])
    return jsonify({"request": req, "record": record}), 201
