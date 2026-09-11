"""Order API routes."""
import uuid

from fastapi import APIRouter, HTTPException, Request
from langgraph.types import Command

from schemas.order import (
    StartOrderRequest,
    StartOrderResponse,
    OrderDecisionRequest,
    OrderDecisionResponse,
)

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)


def _build_response_fields(result: dict) -> dict:
    """Derive the API-level status/message from a raw graph result."""
    total_amount = result.get("total_amount")
    order_status = result.get("order_status")

    if result.get("__interrupt__"):
        return {
            "status": "pending_approval",
            "total_amount": total_amount,
            "order_status": order_status,
            "message": "Approval required before this order can proceed.",
        }

    if order_status == "placed":
        return {
            "status": "completed",
            "total_amount": total_amount,
            "order_status": order_status,
            "message": "Order placed successfully.",
        }

    if order_status == "failed":
        if result.get("error_code"):
            message = f"Order failed: {result['error_code']}"
        elif result.get("restaurant_open") is False:
            message = "Restaurant is currently closed."
        elif result.get("item_available") is False:
            message = "Item is currently unavailable."
        else:
            message = "Order failed."
        return {
            "status": "failed",
            "total_amount": total_amount,
            "order_status": order_status,
            "message": message,
        }

    if result.get("approval_status") == "rejected":
        return {
            "status": "rejected",
            "total_amount": total_amount,
            "order_status": order_status,
            "message": "Order was rejected.",
        }

    return {
        "status": "unknown",
        "total_amount": total_amount,
        "order_status": order_status,
        "message": "Order is in an unexpected state.",
    }


@router.post("/start", response_model=StartOrderResponse)
async def start_order(request: StartOrderRequest, http_request: Request) -> StartOrderResponse:
    thread_id = str(uuid.uuid4())
    initial_state = {
        "restaurant_id": request.restaurant_id,
        "item": request.item,
        "quantity": request.quantity,
        "restaurant_open": None,
        "item_available": None,
        "total_amount": None,
        "approval_required": None,
        "approval_status": None,
        "order_status": None,
        "retry_count": 0,
        "error_code": None,
    }

    order_graph = http_request.app.state.order_graph
    config = {"configurable": {"thread_id": thread_id}}
    result = await order_graph.ainvoke(initial_state, config=config)

    return StartOrderResponse(
        thread_id=thread_id,
        **_build_response_fields(result),
    )


@router.post("/decision", response_model=OrderDecisionResponse)
async def order_decision(request: OrderDecisionRequest, http_request: Request) -> OrderDecisionResponse:
    order_graph = http_request.app.state.order_graph
    config = {"configurable": {"thread_id": request.thread_id}}

    existing_state = await order_graph.aget_state(config)
    if not existing_state.values:
        raise HTTPException(status_code=404, detail="thread_id not found")

    result = await order_graph.ainvoke(Command(resume=request.decision), config=config)

    return OrderDecisionResponse(
        thread_id=request.thread_id,
        **_build_response_fields(result),
    )
