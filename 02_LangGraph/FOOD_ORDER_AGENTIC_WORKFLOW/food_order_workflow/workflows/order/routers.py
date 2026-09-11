"""Conditional edge routing logic for the order workflow."""
from typing import Literal
from workflows.order.state import OrderState



def route_after_restaurant(state: OrderState) -> Literal["continue", "closed", "failed"]:
    """Route after checking the restaurant."""
    if state["error_code"] is not None:
        return "failed"
    elif state["restaurant_open"] is False:
        return "closed"
    else:
        return "continue"

def route_after_item(state: OrderState) -> Literal["continue", "unavailable", "failed"]:
    """Route after checking the item."""
    if state["error_code"] is not None:
        return "failed"
    elif state["item_available"] is False:
        return "unavailable"
    else:
        return "continue"


def route_after_pricing(state: OrderState) -> Literal["continue", "approval_required", "failed"]:
    """Route after calculating the total."""
    if state["error_code"] is not None:
        return "failed"
    elif state["approval_required"] is True:
        return "approval_required"
    else:
        return "continue"


def route_after_approval(state: OrderState) -> Literal["continue", "rejected", "failed"]:
    """Route after requesting approval."""
    if state["approval_status"] == "approved":
        return "continue"
    if state["approval_status"] == "rejected":
        return "rejected"
    else:
        return "failed"