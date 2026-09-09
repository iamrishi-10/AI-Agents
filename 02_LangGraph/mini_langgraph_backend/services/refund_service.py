"""Refund-related business logic."""

_MOCK_REFUNDS = {
    7821: "refunded",
}


class RefundService:
    def create_refund(self, order_id: int) -> str:
        status = _MOCK_REFUNDS.get(order_id)
        if status is None:
            raise ValueError(f"Cannot create refund for order_id={order_id}")
        return status
