"""Pricing-related business logic."""
MOCK_PRICES = {
    "burger": 300.0,
    "pizza": 400.0,
    "pasta": 350.0,
    "wrap": 220.0,
    "fries": 150.0,
}


class PriceNotFoundError(Exception):
    """Raised when no price exists for the given item name."""


class PricingService:
    def calculate_total(self, item: str, quantity: int) -> float:
        price = MOCK_PRICES.get(item)
        if price is None:
            raise PriceNotFoundError(f"No price found for item={item}")
        return price * quantity
