"""Menu-related business logic."""
MOCK_MENU = {
    "burger": {"price": 300.0, "available": True},
    "pizza": {"price": 400.0, "available": True},
    "pasta": {"price": 350.0, "available": False},
    "wrap": {"price": 220.0, "available": True},
    "fries": {"price": 150.0, "available": True},
}


class MenuItemNotFoundError(Exception):
    """Raised when no menu item exists for the given item name."""


class MenuService:
    def check_item(self, item: str) -> bool:
        """Return True if the item is available, False if it's unavailable."""
        menu_item = MOCK_MENU.get(item)
        if menu_item is None:
            raise MenuItemNotFoundError(f"No menu item found for item={item}")
        return menu_item["available"]
