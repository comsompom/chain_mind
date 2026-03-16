"""AI-driven payment rules: evaluate triggers and suggest timing/amount."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

# In-memory store for demo (replace with DB in production)
_payment_rules: list[dict] = []
_payment_history: list[dict] = []


class TriggerType(str, Enum):
    BALANCE_ABOVE = "balance_above"
    BALANCE_BELOW = "balance_below"
    TIME = "time"
    MANUAL = "manual"


@dataclass
class PaymentRule:
    id: str
    trigger_type: str
    trigger_value: str  # e.g. "100" for balance, "09:00" for time
    amount: str
    recipient: str
    enabled: bool = True
    ai_suggestion: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


def add_rule(trigger_type: str, trigger_value: str, amount: str, recipient: str) -> dict:
    """Add a payment rule and return it with id."""
    rule_id = f"rule_{len(_payment_rules) + 1}_{datetime.utcnow().strftime('%H%M%S')}"
    suggestion = _ai_suggest_timing(trigger_type, amount)
    rule = {
        "id": rule_id,
        "trigger_type": trigger_type,
        "trigger_value": trigger_value,
        "amount": amount,
        "recipient": recipient,
        "enabled": True,
        "ai_suggestion": suggestion,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    _payment_rules.append(rule)
    return rule


def list_rules() -> list[dict]:
    return list(_payment_rules)


def list_payments() -> list[dict]:
    return list(reversed(_payment_history))


def evaluate_rules(current_balance_eth: float) -> list[dict]:
    """
    Evaluate all rules; return list of payment requests to execute.
    AI layer suggests optimal timing/amount; backend creates payment requests.
    """
    to_execute = []
    for r in _payment_rules:
        if not r.get("enabled"):
            continue
        if r["trigger_type"] == TriggerType.BALANCE_ABOVE:
            try:
                if current_balance_eth >= float(r["trigger_value"]):
                    to_execute.append(r)
            except ValueError:
                pass
        elif r["trigger_type"] == TriggerType.BALANCE_BELOW:
            try:
                if current_balance_eth <= float(r["trigger_value"]):
                    to_execute.append(r)
            except ValueError:
                pass
    return to_execute


def record_payment(rule_id: str, amount: str, recipient: str, status: str = "submitted") -> dict:
    """Record a payment in history (e.g. after HSP submit)."""
    entry = {
        "id": f"pay_{len(_payment_history) + 1}",
        "rule_id": rule_id,
        "amount": amount,
        "recipient": recipient,
        "status": status,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    _payment_history.append(entry)
    return entry


def _ai_suggest_timing(trigger_type: str, amount: str) -> str:
    """AI suggestion for optimal timing or risk check."""
    if trigger_type == TriggerType.TIME:
        return "Scheduled payments can reduce gas by batching. Consider off-peak hours."
    if trigger_type in (TriggerType.BALANCE_ABOVE, TriggerType.BALANCE_BELOW):
        return "Rule will trigger automatically when condition is met. Ensure sufficient gas."
    return "Review amount and recipient before enabling."
