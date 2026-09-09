"""Payment-related business logic."""

_MOCK_PAYMENTS = {
    7821: "paid",
    1001: "paid",
}


class PaymentService:
    def get_payment_status(self, order_id: int) -> str:
        status = _MOCK_PAYMENTS.get(order_id)
        if status is None:
            raise ValueError(f"No payment status found for order_id={order_id}")
        return status
