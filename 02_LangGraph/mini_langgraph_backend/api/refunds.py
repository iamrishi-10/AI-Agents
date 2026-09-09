"""Refund API routes."""
from fastapi import APIRouter, HTTPException

from schemas.refund import RefundRequest, RefundResponse
from workflows.refund.graph import refund_graph

router = APIRouter(
    prefix="/refunds",
    tags=["refunds"],
)

@router.post("/check", response_model=RefundResponse)
async def check_refund(request: RefundRequest) -> RefundResponse:
    initial_state = {
        "order_id": request.order_id,
        "order_status": None,
        "payment_status": None,
        "refund_eligible": None,
        "refund_status": None,
        "error": None,
    }

    final_state = await refund_graph.ainvoke(initial_state)

    if final_state["error"] is not None:
        raise HTTPException(status_code=404, detail=final_state["error"])

    return RefundResponse(
        order_id=final_state["order_id"],
        order_status=final_state["order_status"],
        payment_status=final_state["payment_status"],
        refund_eligible=final_state["refund_eligible"],
        refund_status=final_state["refund_status"] or "not_refunded",
    )
