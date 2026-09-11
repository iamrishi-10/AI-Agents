"""Order-related business logic."""


class OrderService:
    def place_order(
        self,
        restaurant_id: int,
        item: str,
        quantity: int,
        total_amount: float,
    ) -> str:
        """Simulate placing the order. No real side effect for this mock exercise."""
        return "placed"
