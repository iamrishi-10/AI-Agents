"""LangGraph graph assembly for the order workflow."""
from langgraph.graph import StateGraph, START, END

from workflows.order.state import OrderState
from workflows.order.nodes import (
    check_restaurant,
    check_item,
    calculate_total,
    request_approval,
    place_order,
    handle_failure,
)
from workflows.order.routers import (
    route_after_restaurant,
    route_after_item,
    route_after_pricing,
    route_after_approval,
)

builder = StateGraph(OrderState)

builder.add_node("check_restaurant", check_restaurant)
builder.add_node("check_item", check_item)
builder.add_node("calculate_total", calculate_total)
builder.add_node("request_approval", request_approval)
builder.add_node("place_order", place_order)
builder.add_node("handle_failure", handle_failure)

builder.add_edge(START, "check_restaurant")

builder.add_conditional_edges(
    "check_restaurant",
    route_after_restaurant,
    {
        "continue": "check_item",
        "closed": "handle_failure",
        "failed": "handle_failure",
    },
)

builder.add_conditional_edges(
    "check_item",
    route_after_item,
    {
        "continue": "calculate_total",
        "unavailable": "handle_failure",
        "failed": "handle_failure",
    },
)

builder.add_conditional_edges(
    "calculate_total",
    route_after_pricing,
    {
        "continue": "place_order",
        "approval_required": "request_approval",
        "failed": "handle_failure",
    },
)

builder.add_conditional_edges(
    "request_approval",
    route_after_approval,
    {
        "continue": "place_order",
        "rejected": END,
        "failed": "handle_failure",
    },
)

builder.add_edge("place_order", END)
builder.add_edge("handle_failure", END)


def build_order_graph(checkpointer):
    """Compile the order graph with the given durable checkpointer."""
    return builder.compile(checkpointer=checkpointer)
