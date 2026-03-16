"""Tests for Flask API routes (app, health, status, dashboard, trading, payments)."""
import pytest


@pytest.fixture
def client():
    """Flask test client."""
    from backend.app import create_app
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.get_json()
    assert data.get("status") == "ok"
    assert data.get("app") == "ChainMind"


def test_api_status(client):
    r = client.get("/api/status")
    assert r.status_code == 200
    data = r.get_json()
    assert "app" in data
    assert "chain_connected" in data
    assert "payment_rules" in data


def test_dashboard_summary(client):
    r = client.get("/api/dashboard/summary")
    assert r.status_code == 200
    data = r.get_json()
    assert "balance" in data
    assert "insights" in data
    assert "payment_rules_count" in data
    assert "portfolio_assets" in data


def test_dashboard_balance(client):
    r = client.get("/api/dashboard/balance")
    assert r.status_code == 200
    data = r.get_json()
    assert "eth" in data
    assert "symbol" in data


def test_dashboard_transactions(client):
    r = client.get("/api/dashboard/transactions")
    assert r.status_code == 200
    data = r.get_json()
    assert "transactions" in data
    assert isinstance(data["transactions"], list)


def test_signals(client):
    r = client.get("/api/signals")
    assert r.status_code == 200
    data = r.get_json()
    assert "trend" in data
    assert "suggestion" in data
    assert "confidence" in data
    assert "reason" in data


def test_insights(client):
    r = client.get("/api/insights")
    assert r.status_code == 200
    data = r.get_json()
    assert "insights" in data
    assert isinstance(data["insights"], list)


def test_payment_rules_list(client):
    r = client.get("/api/payment-rules")
    assert r.status_code == 200
    data = r.get_json()
    assert "rules" in data


def test_payments_list(client):
    r = client.get("/api/payments")
    assert r.status_code == 200
    data = r.get_json()
    assert "payments" in data


def test_payments_suggested_rule(client):
    r = client.get("/api/payments/suggested-rule")
    assert r.status_code == 200
    data = r.get_json()
    assert "balance_eth" in data
    assert "suggested_rule" in data


def test_create_rule_validation_no_recipient(client):
    r = client.post(
        "/api/payment-rules",
        json={"trigger_type": "balance_above", "amount": "0.1", "recipient": ""},
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 400
    data = r.get_json()
    assert "error" in data


def test_create_rule_validation_invalid_address(client):
    r = client.post(
        "/api/payment-rules",
        json={"trigger_type": "balance_above", "amount": "0.1", "recipient": "not-an-address"},
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 400
    data = r.get_json()
    assert "error" in data


def test_create_rule_validation_invalid_amount(client):
    r = client.post(
        "/api/payment-rules",
        json={
            "trigger_type": "balance_above",
            "amount": "0",
            "recipient": "0x1234567890123456789012345678901234567890",
        },
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 400
    data = r.get_json()
    assert "error" in data


def test_create_rule_success(client):
    r = client.post(
        "/api/payment-rules",
        json={
            "trigger_type": "balance_above",
            "trigger_value": "1",
            "amount": "0.01",
            "recipient": "0x1234567890123456789012345678901234567890",
            "symbol": "HSK",
        },
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 201
    data = r.get_json()
    assert data["amount"] == "0.01"
    assert "id" in data


def test_payments_export(client):
    r = client.get("/api/payments/export")
    assert r.status_code == 200
    assert "text/csv" in r.content_type
    assert b"ID," in r.data or b"ID," in r.get_data()
