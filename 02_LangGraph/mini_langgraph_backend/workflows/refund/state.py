"""LangGraph state definition for the refund workflow."""
from typing import TypedDict


class RefundState(TypedDict):
    """State definition for the refund workflow."""
    order_id: int
    order_status: str | None
    payment_status: str | None
    refund_eligible: bool | None
    refund_status: str | None
    error: str | None   