"""LangGraph graph assembly for the refund workflow."""
from langgraph.graph import StateGraph, START, END
from workflows.refund.state import RefundState
from workflows.refund.nodes import fetch_order, check_payment, evaluate_refund, process_refund
from workflows.refund.routers import route_after_fetch, route_refund


builder = StateGraph(RefundState)

builder.add_node("fetch_order", fetch_order)
builder.add_node("check_payment", check_payment)
builder.add_node("evaluate_refund", evaluate_refund)
builder.add_node("process_refund", process_refund)


builder.add_edge(START, "fetch_order")

builder.add_conditional_edges("fetch_order", route_after_fetch, {"continue": "check_payment", "failed": END})
builder.add_edge("check_payment", "evaluate_refund")
builder.add_conditional_edges("evaluate_refund", route_refund, {"refund": "process_refund", "reject": END})
builder.add_edge("process_refund", END)

refund_graph = builder.compile()
