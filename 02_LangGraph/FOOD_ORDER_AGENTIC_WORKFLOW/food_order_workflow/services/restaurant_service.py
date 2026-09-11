"""Restaurant-related business logic."""
MOCK_RESTAURANTS = {
    101: {"name": "Urban Bites", "open": True},
    202: {"name": "Spice Route", "open": False},
    303: {"name": "Pizza Hub", "open": True},
}


class RestaurantNotFoundError(Exception):
    """Raised when no restaurant exists for the given restaurant_id."""


class RestaurantService:
    def check_restaurant(self, restaurant_id: int) -> bool:
        """Return True if the restaurant is open, False if it's closed."""
        restaurant = MOCK_RESTAURANTS.get(restaurant_id)
        if restaurant is None:
            raise RestaurantNotFoundError(f"No restaurant found for restaurant_id={restaurant_id}")
        return restaurant["open"]
