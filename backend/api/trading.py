"""Trading API: signals and insights."""
from flask import Blueprint, request

from backend.services.ai_signals import get_signals, get_insights

trading_bp = Blueprint("trading", __name__)


@trading_bp.route("/signals", methods=["GET"])
def signals():
    """GET /api/signals - trading signals with chain/symbol context (optional query: prices as CSV)."""
    prices_param = request.args.get("prices")
    prices = [float(x) for x in prices_param.split(",")] if prices_param else None
    out = get_signals(prices=prices)
    # Ensure chain is set from config if missing
    if not out.get("chain"):
        try:
            from config import settings
            out["chain"] = getattr(settings, "CHAIN_DISPLAY_NAME", "HashKey Chain Testnet")
        except Exception:
            out["chain"] = "HashKey Chain Testnet"
    return out


@trading_bp.route("/insights", methods=["GET"])
def insights():
    """GET /api/insights - short AI insights for dashboard."""
    return {"insights": get_insights()}
