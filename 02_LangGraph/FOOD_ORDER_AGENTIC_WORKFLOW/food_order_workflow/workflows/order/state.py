"""LangGraph state definition for the order workflow."""
from typing import TypedDict


class OrderState(TypedDict):
    """State definition for the order workflow."""

    restaurant_id: int
    item: str
    quantity: int

    restaurant_open: bool | None
    item_available: bool | None

    total_amount: float | None

    approval_required: bool | None
    approval_status: str | None

    order_status: str | None

    retry_count: int

    error_code: str | None