"""LangGraph node functions for the refund workflow."""
from services.order_service import OrderService, OrderNotFoundError
from services.payment_service import PaymentService
from services.refund_service import RefundService
from workflows.refund.state import RefundState

def fetch_order(state: RefundState) -> dict:
    """Fetch the order details for the given order_id."""
    order_service = OrderService()
    try:
        order = order_service.get_order(state["order_id"])
        return {
            "order_status": order["status"],
            "error": None,
        }
    except OrderNotFoundError:
        return {
            "order_status": None,
            "error": "order_not_found",
        }


def check_payment(state: RefundState) -> dict:
    """Check the payment status for the given order_id."""
    payment_service = PaymentService()
    try:
        payment_status = payment_service.get_payment_status(state["order_id"])
        return {
            "payment_status": payment_status,
            "error": None,
        }
    except ValueError:
        return {
            "payment_status": None,
            "error": "payment_not_found",
        }

def evaluate_refund(state: RefundState) -> dict:
    """Check if the order is eligible for a refund."""
    if state["order_status"] == "lost" and state["payment_status"] == "paid":
        return {
            "refund_eligible": True,
            "error": None,
        }
    else:
        return {
            "refund_eligible": False,
            "error": None,
        }


def process_refund(state: RefundState) -> dict:
    """Execute the refund if eligible."""
    if state["refund_eligible"]:
        refund_service = RefundService()
        refund_status = refund_service.create_refund(state["order_id"])
        return {
            "refund_status": refund_status,
            "error": None,
        }
    else:
        return {
            "refund_status": None,
            "error": None,
        }