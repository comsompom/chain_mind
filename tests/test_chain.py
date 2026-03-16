"""Tests for chain service."""
from backend.services.chain import get_balance, get_recent_txs


def test_get_balance_empty_address():
    b = get_balance("0x0000000000000000000000000000000000000000")
    assert "eth" in b
    assert b.get("connected") is False or "eth" in b


def test_get_recent_txs_returns_list():
    txs = get_recent_txs("0x0000000000000000000000000000000000000000", limit=5)
    assert isinstance(txs, list)
    assert len(txs) <= 5
