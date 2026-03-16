"""Payments API: rules and history; HSP-ready flow."""
import csv
import io
import re
from flask import Blueprint, request, jsonify, Response

from backend.services import ai_payments, hsp_client

payments_bp = Blueprint("payments", __name__)

# Basic EVM address: 0x + 40 hex chars
_ADDRESS_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")


def _validate_recipient(recipient: str) -> str | None:
    """Return error message if invalid, else None."""
    if not recipient or not isinstance(recipient, str):
        return "Recipient address is required."
    a = recipient.strip()
    if not _ADDRESS_RE.match(a):
        return "Recipient must be a valid EVM address (0x followed by 40 hex characters)."
    return None


def _validate_amount(amount: str) -> str | None:
    """Return error message if invalid, else None."""
    if amount is None or (isinstance(amount, str) and not amount.strip()):
        return "Amount is required."
    try:
        v = float(str(amount).strip())
        if v <= 0:
            return "Amount must be greater than 0."
    except ValueError:
        return "Amount must be a valid number."
    return None


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
    amount = (data.get("amount") or "").strip() or "0"
    recipient = (data.get("recipient") or "").strip()
    symbol = (data.get("symbol") or "HSK").strip().upper() or "HSK"
    err = _validate_recipient(recipient)
    if err:
        return jsonify({"error": err}), 400
    err = _validate_amount(amount)
    if err:
        return jsonify({"error": err}), 400
    rule = ai_payments.add_rule(trigger_type, trigger_value, amount, recipient, symbol=symbol)
    return jsonify(rule), 201


@payments_bp.route("/payment-rules/<rule_id>", methods=["DELETE"])
def delete_rule(rule_id):
    """Delete a payment rule by id."""
    if ai_payments.delete_rule(rule_id):
        return jsonify({"deleted": True, "id": rule_id}), 200
    return jsonify({"error": "Rule not found"}), 404


@payments_bp.route("/payment-rules/<rule_id>", methods=["PATCH"])
def update_rule(rule_id):
    """Enable or disable a rule. Body: { \"enabled\": true|false }."""
    data = request.get_json() or {}
    enabled = data.get("enabled")
    if enabled is None:
        return jsonify({"error": "enabled (true/false) required"}), 400
    rule = ai_payments.update_rule(rule_id, enabled=bool(enabled))
    if rule is None:
        return jsonify({"error": "Rule not found"}), 404
    return jsonify(rule), 200


@payments_bp.route("/payments", methods=["GET"])
def list_payments():
    return {"payments": ai_payments.list_payments()}


@payments_bp.route("/payments/receipt/<payment_id>", methods=["GET"])
def get_receipt(payment_id):
    """Get a single payment as receipt (PayFi / HSP narrative: request ID, status, etc.)."""
    payments = ai_payments.list_payments()
    for p in payments:
        if p.get("id") == payment_id:
            receipt = dict(p)
            receipt["hsp_request_id"] = f"HSP-{payment_id}-{receipt.get('timestamp', '')[:10]}"
            return jsonify(receipt)
    return jsonify({"error": "Payment not found"}), 404


@payments_bp.route("/payments/export", methods=["GET"])
def export_payments():
    """Export payment history as CSV."""
    payments = ai_payments.list_payments()
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["ID", "Rule ID", "Amount", "Symbol", "Recipient", "Status", "Time"])
    for p in payments:
        w.writerow([
            p.get("id", ""),
            p.get("rule_id", ""),
            p.get("amount", ""),
            p.get("symbol", ""),
            p.get("recipient", ""),
            p.get("status", ""),
            p.get("timestamp", ""),
        ])
    resp = Response(out.getvalue(), mimetype="text/csv")
    resp.headers["Content-Disposition"] = "attachment; filename=chainmind_payments.csv"
    return resp


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
