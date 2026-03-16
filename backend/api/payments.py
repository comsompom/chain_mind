"""Payments API: rules and history; HSP-ready flow."""
from flask import Blueprint, request, jsonify

from backend.services import ai_payments, hsp_client

payments_bp = Blueprint("payments", __name__)


def _current_balance():
    """Get current wallet/account balance (chain or sandbox) for rule suggestions."""
    from config import settings
    from backend.services import chain
    from backend.api.dashboard import _balance_from_sandbox
    address = (getattr(settings, "WALLET_ADDRESS", "") or "").strip()
    if address and address != "0x0000000000000000000000000000000000000000":
        result = chain.get_balance(address)
        if result.get("connected"):
            try:
                return float(result.get("eth", 0) or 0), result.get("symbol", "HSK")
            except (TypeError, ValueError):
                pass
    sandbox = _balance_from_sandbox()
    if sandbox:
        try:
            return float(sandbox.get("eth", 0) or 0), "HSK"
        except (TypeError, ValueError):
            pass
    return 0.0, getattr(settings, "NATIVE_SYMBOL", "HSK")


def _evaluate_rules_now():
    """Run payment rule evaluation once (same logic as scheduler). Returns number of payments recorded."""
    balance, _ = _current_balance()
    triggered = ai_payments.evaluate_rules(balance)
    for rule in triggered:
        symbol = rule.get("symbol") or "HSK"
        req = hsp_client.create_payment_request(rule["amount"], rule["recipient"], rule["id"])
        ai_payments.record_payment(rule["id"], rule["amount"], rule["recipient"], status=req["status"], symbol=symbol)
    return len(triggered)


@payments_bp.route("/payment-rules", methods=["GET"])
def list_rules():
    return {"rules": ai_payments.list_rules()}


@payments_bp.route("/payments/suggested-rule", methods=["GET"])
def suggested_rule():
    """Return current balance and a rule suggestion that will trigger with that balance."""
    from config import settings
    balance_eth, symbol = _current_balance()
    wallet = (getattr(settings, "WALLET_ADDRESS", "") or "").strip()
    # Suggest a rule that will trigger *now*: balance_above (threshold slightly below current)
    if balance_eth > 0:
        threshold = max(0.001, round(balance_eth * 0.5, 4))  # e.g. 0.1 -> 0.05
        amount = min(0.002, round(balance_eth * 0.1, 4)) or 0.002  # small amount
        return jsonify({
            "balance_eth": balance_eth,
            "symbol": symbol,
            "wallet_address": wallet if wallet else None,
            "suggested_rule": {
                "trigger_type": "balance_above",
                "trigger_value": str(threshold),
                "amount": str(amount),
                "symbol": symbol,
                "message": f"With your balance {balance_eth} {symbol}, use «Balance above» {threshold} and amount {amount} — this will trigger when you click «Check rules now».",
            },
        })
    return jsonify({
        "balance_eth": 0,
        "symbol": symbol,
        "wallet_address": wallet if wallet else None,
        "suggested_rule": {
            "trigger_type": "balance_above",
            "trigger_value": "0.01",
            "amount": "0.002",
            "symbol": symbol,
            "message": "Add testnet HSK from the faucet first, then create a «Balance above» rule (e.g. 0.05) to trigger a payment.",
        },
    })


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
