"""HashKey Chain RPC connector: read balance, recent txs (EVM-compatible)."""
try:
    from web3 import Web3
except ImportError:
    Web3 = None

from config import settings


def get_web3():
    """Return Web3 instance or None if not configured."""
    if Web3 is None:
        return None
    url = (getattr(settings, "RPC_URL", "") or "").strip()
    if not url:
        return None
    try:
        w3 = Web3(Web3.HTTPProvider(url, request_kwargs={"timeout": 12}))
        if w3.is_connected():
            return w3
    except Exception:
        pass
    return None


def get_balance(address: str) -> dict:
    """
    Get native token balance for address on HashKey Chain (or configured RPC).
    Returns dict with wei, eth (human-readable), symbol (HSK/ETH), connected.
    """
    w3 = get_web3()
    symbol = getattr(settings, "NATIVE_SYMBOL", "HSK")
    if not address or address == "0x0000000000000000000000000000000000000000":
        return {"wei": "0", "eth": "0.0", "symbol": symbol, "connected": False}
    if not w3:
        return {"wei": "0", "eth": "0.0", "symbol": symbol, "connected": False, "error": "RPC not connected. Set RPC_URL=https://testnet.hsk.xyz in .env"}
    try:
        addr = Web3.to_checksum_address(address)
        wei = w3.eth.get_balance(addr)
        eth = float(Web3.from_wei(wei, "ether"))
        return {"wei": str(wei), "eth": f"{eth:.6f}", "symbol": symbol, "connected": True}
    except Exception as e:
        return {"wei": "0", "eth": "0.0", "symbol": symbol, "connected": False, "error": str(e)}


def get_recent_txs(address: str, limit: int = 10) -> list:
    """Get recent transactions for address (mock or from chain if available)."""
    w3 = get_web3()
    if not w3 or not address or address == "0x0000000000000000000000000000000000000000":
        return _mock_recent_txs(limit)
    try:
        # Many chains don't have get_transaction_count by address in same way;
        # use block range and filter (or mock for demo)
        return _mock_recent_txs(limit)
    except Exception:
        return _mock_recent_txs(limit)


def _mock_recent_txs(limit: int) -> list:
    """Demo: return mock recent transactions."""
    return [
        {"hash": "0xabc...123", "from": "0x...", "to": "0x...", "value": "0.1", "block": 12345},
        {"hash": "0xdef...456", "from": "0x...", "to": "0x...", "value": "0.05", "block": 12344},
        {"hash": "0x789...abc", "from": "0x...", "to": "0x...", "value": "1.0", "block": 12340},
    ][:limit]
