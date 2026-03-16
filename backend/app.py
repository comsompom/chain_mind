"""ChainMind Flask app factory. Run from project root: flask --app backend.app run"""
import sys
from pathlib import Path

# Ensure project root is on path for config and backend imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, redirect, render_template

from config import settings

try:
    from flask_cors import CORS
except ImportError:
    CORS = None


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=str(PROJECT_ROOT / "templates"),
        static_folder=str(PROJECT_ROOT / "static"),
        static_url_path="/static",
    )
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    if CORS is not None:
        CORS(app)

    # Health check
    @app.route("/health")
    def health():
        return {"status": "ok", "app": "ChainMind"}

    # Status: chain, sandbox, wallet, rules (for monitoring / professional dashboards)
    @app.route("/api/status")
    def api_status():
        from backend.services import chain
        from backend.api.dashboard import _balance_from_sandbox
        try:
            from backend.services import ai_payments
            all_rules = ai_payments.list_rules()
            rules_count = sum(1 for r in all_rules if r.get("enabled", True))
            payments_count = len(ai_payments.list_payments())
        except Exception:
            rules_count = 0
            payments_count = 0
        wallet = (getattr(settings, "WALLET_ADDRESS", "") or "").strip()
        try:
            chain_ok = bool(chain.get_web3() and chain.get_web3().is_connected())
        except Exception:
            chain_ok = False
        sandbox_ok = False
        try:
            from backend.services import hashkey_sandbox
            sandbox_ok = hashkey_sandbox.ping()
        except Exception:
            pass
        return {
            "app": "ChainMind",
            "chain_connected": chain_ok,
            "sandbox_connected": sandbox_ok,
            "wallet_configured": bool(wallet and wallet != "0x0000000000000000000000000000000000000000"),
            "payment_rules": rules_count,
            "payment_history_entries": payments_count,
        }

    # Sandbox status (no API key required)
    @app.route("/api/sandbox/status")
    def sandbox_status():
        from backend.services import hashkey_sandbox
        ok = hashkey_sandbox.ping()
        time_data = hashkey_sandbox.server_time() if ok else None
        return {
            "sandbox_connected": ok,
            "message": "HashKey sandbox public API (no API key)" if ok else "Sandbox unreachable",
            "server_time": time_data.get("serverTime") if time_data else None,
        }

    # Register blueprints
    from backend.api.dashboard import dashboard_bp
    from backend.api.trading import trading_bp
    from backend.api.payments import payments_bp

    app.register_blueprint(dashboard_bp, url_prefix="/api")
    app.register_blueprint(trading_bp, url_prefix="/api")
    app.register_blueprint(payments_bp, url_prefix="/api")

    # Page routes (UI)
    @app.route("/")
    def index():
        return redirect("/dashboard")

    @app.route("/dashboard")
    def page_dashboard():
        return render_template("dashboard.html")

    @app.route("/trading")
    def page_trading():
        return render_template("trading.html")

    @app.route("/payments")
    def page_payments():
        return render_template("payments.html")

    # Start background scheduler so payment rules are evaluated periodically
    try:
        from backend.tasks import start_scheduler
        start_scheduler()
    except Exception:
        pass

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=(settings.FLASK_ENV == "development"))
