"""Scheduled jobs: evaluate payment rules, refresh signals."""
from apscheduler.schedulers.background import BackgroundScheduler

from config import settings
from backend.services import chain, ai_payments, hsp_client


def evaluate_payment_rules():
    """Periodically evaluate rules and create HSP payment requests for demo."""
    address = settings.WALLET_ADDRESS or "0x0000000000000000000000000000000000000000"
    balance_data = chain.get_balance(address)
    try:
        balance_eth = float(balance_data.get("eth", 0))
    except (TypeError, ValueError):
        balance_eth = 0.0
    for rule in ai_payments.evaluate_rules(balance_eth):
        # Stub: create request and record (in production, queue to HSP)
        req = hsp_client.create_payment_request(rule["amount"], rule["recipient"], rule["id"])
        ai_payments.record_payment(rule["id"], rule["amount"], rule["recipient"], status=req["status"])


def start_scheduler():
    """Start background scheduler (call from app after first request or on startup)."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(evaluate_payment_rules, "interval", minutes=5, id="payment_rules")
    scheduler.start()
    return scheduler
