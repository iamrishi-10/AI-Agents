"""LangGraph node functions for the order workflow."""
from langgraph.types import interrupt

from services.restaurant_service import RestaurantService, RestaurantNotFoundError
from services.menu_service import MenuService, MenuItemNotFoundError
from services.pricing_service import PricingService, PriceNotFoundError
from services.order_service import OrderService
from workflows.order.state import OrderState


def check_restaurant(state: OrderState) -> dict:
    """Check whether the restaurant is open."""
    restaurant_service = RestaurantService()
    try:
        restaurant_open = restaurant_service.check_restaurant(state["restaurant_id"])
        return {
            "restaurant_open": restaurant_open,
            "error_code": None,
        }
    except RestaurantNotFoundError:
        return {
            "restaurant_open": None,
            "error_code": "restaurant_not_found",
        }


def check_item(state: OrderState) -> dict:
    """Check whether the ordered item is available."""
    menu_service = MenuService()
    try:
        item_available = menu_service.check_item(state["item"])
        return {
            "item_available": item_available,
            "error_code": None,
        }
    except MenuItemNotFoundError:
        return {
            "item_available": None,
            "error_code": "item_not_found",
        }


def calculate_total(state: OrderState) -> dict:
    """Calculate the order total and whether approval is required."""
    pricing_service = PricingService()
    try:
        total_amount = pricing_service.calculate_total(state["item"], state["quantity"])
        return {
            "total_amount": total_amount,
            "approval_required": total_amount > 500,
            "error_code": None,
        }
    except PriceNotFoundError:
        return {
            "total_amount": None,
            "approval_required": None,
            "error_code": "price_not_found",
        }


def request_approval(state: OrderState) -> dict:
    """Pause the workflow and ask a human to approve the order."""
    decision = interrupt(
        {
            "message": "Approval required",
            "restaurant_id": state["restaurant_id"],
            "item": state["item"],
            "quantity": state["quantity"],
            "total_amount": state["total_amount"],
        }
    )
    return {
        "approval_status": decision,
    }


def place_order(state: OrderState) -> dict:
    """Place the order. This is the final side-effect node."""
    order_service = OrderService()
    order_status = order_service.place_order(
        state["restaurant_id"],
        state["item"],
        state["quantity"],
        state["total_amount"],
    )
    return {
        "order_status": order_status,
    }


def handle_failure(state: OrderState) -> dict:
    """Convert the current error_code into a final failed order status."""
    return {
        "order_status": "failed",
    }
