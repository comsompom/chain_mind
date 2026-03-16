"""AI trading signals: rule-based + optional ML layer for trend/volatility/suggestions."""
import random
from datetime import datetime
from typing import Any

import numpy as np

# Optional sklearn for demo signals
try:
    from sklearn.linear_model import LinearRegression
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


def get_signals(prices: list[float] | None = None, volume: list[float] | None = None) -> dict[str, Any]:
    """
    Produce trading signals from price/volume (or mock data).
    When prices not provided, tries HashKey sandbox 24hr ticker (no API key).
    Returns chain, data_source, symbols so the UI can show what the signal is based on.
    """
    data_source = "Demo (mock)"
    symbols_used: list[str] = []

    if not prices or len(prices) < 2:
        try:
            from backend.services.hashkey_sandbox import ticker_24hr
            data = ticker_24hr()
            if data and isinstance(data, list):
                for t in data:
                    if isinstance(t, dict):
                        o, c = t.get("o"), t.get("c")
                        sym = t.get("s") or t.get("symbol") or ""
                        if o and c and o != "0" and c != "0":
                            try:
                                o_f, c_f = float(o), float(c)
                                prices = [o_f, (o_f + c_f) / 2, c_f]
                                data_source = "HashKey Global Sandbox"
                                if sym:
                                    symbols_used = [sym]
                                break
                            except (TypeError, ValueError):
                                pass
        except Exception:
            pass
        if not prices or len(prices) < 2:
            prices = _mock_prices(20)

    if not volume:
        volume = [random.uniform(100, 1000) for _ in range(len(prices))]

    prices_arr = np.array(prices)
    trend = _compute_trend(prices_arr)
    volatility = _compute_volatility(prices_arr)
    risk = "on" if trend > 0 and volatility < 0.02 else "off"
    suggestion = _suggestion_text(trend, volatility, risk)

    # Include symbol/chain in suggestion when we have market context
    if symbols_used:
        suggestion = f"{symbols_used[0]}: {suggestion}"

    try:
        from config import settings
        chain_name = getattr(settings, "CHAIN_DISPLAY_NAME", "HashKey Chain Testnet")
    except Exception:
        chain_name = "HashKey Chain Testnet"

    # Confidence: higher when we have real data and volatility is not extreme
    confidence = 0.5 + (0.3 if data_source != "Demo (mock)" else 0) + (0.2 if volatility < 0.05 else 0)
    confidence = min(1.0, round(confidence, 2))
    reason = _reason_text(trend, volatility, risk, data_source)

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "chain": chain_name,
        "data_source": data_source,
        "symbols": symbols_used,
        "trend": round(float(trend), 6),
        "trend_label": "up" if trend > 0 else "down",
        "volatility": round(float(volatility), 6),
        "volatility_regime": "high" if volatility > 0.02 else "normal",
        "risk": risk,
        "suggestion": suggestion,
        "confidence": confidence,
        "reason": reason,
        "prices_sample": [round(float(p), 4) for p in prices[-5:]],
    }


def get_insights() -> list[dict[str, Any]]:
    """Return 1–2 sentence AI insights for dashboard."""
    signals = get_signals()
    insights = [
        {"type": "signal", "text": signals["suggestion"], "timestamp": signals["timestamp"]},
        {"type": "tip", "text": "Consider DCA on pullbacks when volatility is high.", "timestamp": signals["timestamp"]},
    ]
    if signals["volatility_regime"] == "high":
        insights.append({"type": "risk", "text": "High volatility – consider reducing position size.", "timestamp": signals["timestamp"]})
    return insights


def _mock_prices(n: int) -> list[float]:
    """Generate mock price series."""
    base = 100.0
    out = [base]
    for _ in range(n - 1):
        out.append(out[-1] * (1 + random.gauss(0, 0.01)))
    return out


def _compute_trend(prices: np.ndarray) -> float:
    """Simple trend: normalized slope (last - first) / first."""
    if len(prices) < 2:
        return 0.0
    return (prices[-1] - prices[0]) / (prices[0] + 1e-9)


def _compute_volatility(prices: np.ndarray) -> float:
    """Relative volatility (std of returns)."""
    if len(prices) < 2:
        return 0.0
    returns = np.diff(prices) / (prices[:-1] + 1e-9)
    return float(np.std(returns))


def _suggestion_text(trend: float, volatility: float, risk: str) -> str:
    if trend > 0.01 and volatility < 0.02:
        return "Uptrend with low volatility – consider scaling in."
    if trend < -0.01:
        return "Downtrend – consider DCA or wait for stabilization."
    if volatility > 0.02:
        return "High volatility – reduce size or use limit orders."
    return "Sideways – consider range strategies or hold."


def _reason_text(trend: float, volatility: float, risk: str, data_source: str) -> str:
    """Short explanation for the signal (AI 'why')."""
    parts = []
    if trend > 0.01:
        parts.append("positive trend")
    elif trend < -0.01:
        parts.append("negative trend")
    else:
        parts.append("sideways price")
    if volatility > 0.02:
        parts.append("elevated volatility")
    else:
        parts.append("moderate volatility")
    parts.append(f"risk {risk}; data from {data_source}")
    return "; ".join(parts)
