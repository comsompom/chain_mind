"""
HashKey Global sandbox API – public endpoints (no key) and account endpoints (API key + secret).

Sandbox base URL: https://api-glb.sim.hashkeydev.com
Docs: https://hashkeyglobal-apidoc.readme.io/reference/preparations
- Public: ping, time, exchangeInfo, ticker (no API key).
- Account balance & trades: require API key + secret (HMAC SHA256 signature).
"""
import hmac
import hashlib
import time
import urllib.request
import urllib.error
import json
from typing import Any

# Sandbox base URL
SANDBOX_BASE = "https://api-glb.sim.hashkeydev.com"


def _get(path: str, params: dict | None = None) -> dict | list | None:
    """GET request to sandbox; returns JSON or None on error."""
    url = SANDBOX_BASE + path
    if params:
        q = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{q}"
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            body = r.read().decode()
            return json.loads(body) if body.strip() else {}
    except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError, OSError):
        return None


def ping() -> bool:
    """Test connectivity. Returns True if sandbox responds 200."""
    data = _get("/api/v1/ping")
    return data is not None


def server_time() -> dict | None:
    """GET /api/v1/time – server time in ms (no API key)."""
    return _get("/api/v1/time")


def exchange_info(symbol: str | None = None) -> dict | None:
    """GET /api/v1/exchangeInfo – trading pairs (no API key). Optional symbol filter."""
    params = {"symbol": symbol} if symbol else None
    return _get("/api/v1/exchangeInfo", params)


def ticker_24hr(symbol: str | None = None) -> list | dict | None:
    """GET /quote/v1/ticker/24hr – 24h ticker. No API key. Returns list of tickers or single if symbol given."""
    params = {"symbol": symbol} if symbol else None
    return _get("/quote/v1/ticker/24hr", params)


def ticker_price(symbol: str | None = None) -> list | dict | None:
    """GET /quote/v1/ticker/price – latest price. No API key."""
    params = {"symbol": symbol} if symbol else None
    return _get("/quote/v1/ticker/price", params)


def _signed_get(api_key: str, secret: str, path: str, params: dict | None = None) -> dict | list | None:
    """
    GET with HMAC SHA256 signature. Required for account balance and account/trades.
    """
    if not api_key or not secret:
        return None
    params = dict(params or {})
    params["timestamp"] = int(time.time() * 1000)
    query = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    sig = hmac.new(
        secret.encode("utf-8"),
        query.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    url = f"{SANDBOX_BASE}{path}?{query}&signature={sig}"
    req = urllib.request.Request(url, method="GET")
    req.add_header("X-HK-APIKEY", api_key)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            body = r.read().decode()
            return json.loads(body) if body.strip() else {}
    except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError, OSError) as e:
        if isinstance(e, urllib.error.HTTPError) and e.code == 401:
            pass  # Invalid key/secret
        return None


def get_account_balance(api_key: str, secret: str) -> dict | None:
    """
    GET /api/v1/account – exchange account balances (requires API key + secret).
    Returns dict with balances[], totalAssetBal, etc., or None on error/unauthorized.
    """
    return _signed_get(api_key, secret, "/api/v1/account")


def get_account_trades(api_key: str, secret: str, limit: int = 10) -> list | None:
    """
    GET /api/v1/account/trades – recent account trade records (requires API key + secret).
    Returns list of trades or None on error.
    """
    data = _signed_get(api_key, secret, "/api/v1/account/trades", {"limit": limit})
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "data" in data:
        return data["data"]
    return None


def get_prices_for_signals(symbols: list[str] | None = None) -> list[float]:
    """
    Fetch latest prices from sandbox for AI signals. No API key.
    If symbols not given, uses first available from 24hr ticker.
    """
    data = ticker_24hr()
    if not data or not isinstance(data, list):
        return []
    # Prefer common pairs
    prefer = ["BTCUSDT", "ETHUSDT", "BTCUSD", "ETHUSD"]
    for s in prefer:
        for t in data:
            if isinstance(t, dict) and t.get("s") == s:
                try:
                    c = t.get("c") or t.get("lastPrice") or "0"
                    return [float(c)]
                except (TypeError, ValueError):
                    pass
    # Fallback: any numeric close price
    out = []
    for t in data[:10]:
        if isinstance(t, dict):
            try:
                c = t.get("c") or t.get("lastPrice") or "0"
                if c and c != "0":
                    out.append(float(c))
            except (TypeError, ValueError):
                pass
    return out[:5] if out else []
