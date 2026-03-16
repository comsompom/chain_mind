"""Dashboard API: balance, recent txs, portfolio summary."""
from flask import Blueprint

from backend.services import chain

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard/balance", methods=["GET"])
def get_balance():
    from config import settings
    address = settings.WALLET_ADDRESS or "0x0000000000000000000000000000000000000000"
    return chain.get_balance(address)


@dashboard_bp.route("/dashboard/transactions", methods=["GET"])
def get_transactions():
    from config import settings
    address = settings.WALLET_ADDRESS or "0x0000000000000000000000000000000000000000"
    limit = 10
    return {"transactions": chain.get_recent_txs(address, limit=limit)}


@dashboard_bp.route("/dashboard/summary", methods=["GET"])
def get_summary():
    from config import settings
    from backend.services.ai_signals import get_insights
    from backend.services import hashkey_sandbox

    address = settings.WALLET_ADDRESS or "0x0000000000000000000000000000000000000000"
    balance_data = chain.get_balance(address)
    insights = get_insights()[:3]
    sandbox_ok = hashkey_sandbox.ping()
    server_time = hashkey_sandbox.server_time() if sandbox_ok else None
    return {
        "balance": balance_data,
        "insights": insights,
        "chain_connected": balance_data.get("connected", False),
        "sandbox_connected": sandbox_ok,
        "sandbox_server_time": server_time.get("serverTime") if server_time else None,
    }
