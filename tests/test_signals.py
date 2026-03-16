"""Tests for AI signals."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.services.ai_signals import get_signals, get_insights


def test_get_signals():
    out = get_signals()
    assert "trend" in out
    assert "suggestion" in out
    assert "risk" in out


def test_get_signals_with_prices():
    out = get_signals(prices=[100, 101, 102, 101, 103])
    assert "trend" in out
    assert out["trend_label"] in ("up", "down")


def test_get_insights():
    insights = get_insights()
    assert isinstance(insights, list)
    assert len(insights) >= 1
    assert "text" in insights[0]
