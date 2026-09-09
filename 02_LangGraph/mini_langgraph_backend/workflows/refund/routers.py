"""Conditional edge routing logic for the refund workflow."""
from typing import Literal
from workflows.refund.state import RefundState


def route_after_fetch(state: RefundState) -> Literal["continue", "failed"]:
    """Route after fetching the order."""
    if state["error"] is None:
        return "continue"
    else:
        return "failed"

def route_refund(state: RefundState) -> Literal["refund", "reject"]:
    """Route based on refund eligibility."""
    if state["refund_eligible"] is True:
        return "refund"
    else:
        return "reject"