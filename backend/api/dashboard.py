"""Dashboard API: balance, recent txs, portfolio summary."""
from flask import Blueprint

from backend.services import chain
from backend.services import hashkey_sandbox

dashboard_bp = Blueprint("dashboard", __name__)


def _balance_from_sandbox():
    """If API key + secret set, return sandbox account balance normalized for UI."""
    from config import settings
    if not (getattr(settings, "HSP_API_KEY", "") and getattr(settings, "HSP_SECRET", "")):
        return None
    data = hashkey_sandbox.get_account_balance(settings.HSP_API_KEY, settings.HSP_SECRET)
    if not data or not isinstance(data, dict):
        return None
    balances = data.get("balances") or []
    total_asset = data.get("totalAssetBal")
    try:
        eth_equiv = str(total_asset) if total_asset else "0"
        if not eth_equiv and balances:
            eth_equiv = str(balances[0].get("total") or "0")
    except Exception:
        eth_equiv = "0"
    return {
        "wei": "0",
        "eth": eth_equiv,
        "connected": True,
        "source": "sandbox",
        "balances": balances,
    }


def _transactions_from_sandbox(limit=10):
    """If API key + secret set, return sandbox account trades normalized for UI."""
    from config import settings
    if not (getattr(settings, "HSP_API_KEY", "") and getattr(settings, "HSP_SECRET", "")):
        return None
    trades = hashkey_sandbox.get_account_trades(settings.HSP_API_KEY, settings.HSP_SECRET, limit=limit)
    if not trades or not isinstance(trades, list):
        return None
    return [
        {
            "hash": str(t.get("id", t.get("orderId", ""))),
            "from": "exchange",
            "to": t.get("symbol", ""),
            "value": str(t.get("qty") or t.get("price", "")),
            "block": t.get("time", ""),
            "side": "BUY" if t.get("isBuyer") else "SELL",
            "symbol": t.get("symbol", ""),
        }
        for t in trades[:limit]
    ]


@dashboard_bp.route("/dashboard/balance", methods=["GET"])
def get_balance():
    from config import settings
    address = (getattr(settings, "WALLET_ADDRESS", "") or "").strip()
    # Prefer chain (HashKey Testnet) balance when user has set WALLET_ADDRESS
    if address and address != "0x0000000000000000000000000000000000000000":
        result = chain.get_balance(address)
        if result.get("connected"):
            return result
        # If chain not connected, fall back to sandbox if configured
    sandbox_balance = _balance_from_sandbox()
    if sandbox_balance is not None:
        return sandbox_balance
    return chain.get_balance(address or "0x0000000000000000000000000000000000000000")


@dashboard_bp.route("/dashboard/transactions", methods=["GET"])
def get_transactions():
    sandbox_trades = _transactions_from_sandbox(limit=10)
    if sandbox_trades is not None:
        return {"transactions": sandbox_trades, "source": "sandbox"}
    from config import settings
    address = settings.WALLET_ADDRESS or "0x0000000000000000000000000000000000000000"
    return {"transactions": chain.get_recent_txs(address, limit=10)}


@dashboard_bp.route("/dashboard/summary", methods=["GET"])
def get_summary():
    from config import settings
    from backend.services.ai_signals import get_insights
    from backend.services import hashkey_sandbox

    address = (getattr(settings, "WALLET_ADDRESS", "") or "").strip()
    has_wallet = bool(address and address != "0x0000000000000000000000000000000000000000")
    # Prefer chain balance when user has set WALLET_ADDRESS (show their HSK on HashKey Testnet)
    if has_wallet:
        balance_data = chain.get_balance(address)
        if not balance_data.get("connected"):
            sandbox_balance = _balance_from_sandbox()
            if sandbox_balance is not None:
                balance_data = sandbox_balance
    else:
        sandbox_balance = _balance_from_sandbox()
        if sandbox_balance is not None:
            balance_data = sandbox_balance
        else:
            balance_data = chain.get_balance("0x0000000000000000000000000000000000000000")
    insights = get_insights()[:3]
    sandbox_ok = hashkey_sandbox.ping()
    server_time = hashkey_sandbox.server_time() if sandbox_ok else None
    return {
        "balance": balance_data,
        "insights": insights,
        "chain_connected": balance_data.get("connected", False) if balance_data.get("source") != "sandbox" else False,
        "sandbox_connected": sandbox_ok,
        "sandbox_account_used": sandbox_balance is not None,
        "sandbox_server_time": server_time.get("serverTime") if server_time else None,
    }
