"""HSP (HashKey Settlement Protocol) client stub for PayFi.
When HSP API spec is available, replace stub with real HTTP client for:
- create payment request
- confirm payment
- query status
"""
from datetime import datetime
from typing import Any

from config import settings


def create_payment_request(amount: str, recipient: str, reference: str = "") -> dict[str, Any]:
    """
    Stub: create payment request. In production, POST to HSP_URL.
    Returns request_id and status for demo.
    """
    request_id = f"hsp_req_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    return {
        "request_id": request_id,
        "amount": amount,
        "recipient": recipient,
        "reference": reference,
        "status": "created",
        "hsp_url": getattr(settings, "HSP_URL", ""),
        "message": "HSP-ready: integrate with real HSP API when spec is available.",
    }


def confirm_payment(request_id: str) -> dict[str, Any]:
    """Stub: confirm payment. In production, POST to HSP confirm endpoint."""
    return {
        "request_id": request_id,
        "status": "confirmed",
        "message": "HSP-ready: confirmation will be sent to HSP when integrated.",
    }


def get_payment_status(request_id: str) -> dict[str, Any]:
    """Stub: get payment status. In production, GET from HSP."""
    return {
        "request_id": request_id,
        "status": "confirmed",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "message": "HSP-ready: status sync from HSP when integrated.",
    }
