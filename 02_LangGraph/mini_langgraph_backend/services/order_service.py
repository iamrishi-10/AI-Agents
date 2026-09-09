"""Order-related business logic."""

_MOCK_ORDERS = {
    7821: {"order_id": 7821, "status": "lost"},
    1001: {"order_id": 1001, "status": "delivered"},
}


class OrderNotFoundError(Exception):
    """Raised when no order exists for the given order_id."""


class OrderService:
    def get_order(self, order_id: int) -> dict:
        order = _MOCK_ORDERS.get(order_id)
        if order is None:
            raise OrderNotFoundError(f"No order found for order_id={order_id}")
        return order
