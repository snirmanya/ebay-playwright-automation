from src.pages.base_page import BasePage
from src.utils.price_parser import parse_price


class CartPage(BasePage):
    CART_TOTAL = [
        "xpath=//div[@data-testid='cart-summary']",
        "span[data-testid='x-price-primary']",
        "xpath=//span[contains(@class,'price') or contains(@class,'cart')]",
        "xpath=//*[contains(text(),'US $')]"
    ]

    def get_total(self) -> float:
        total_text = self.get_text(self.CART_TOTAL)
        total = parse_price(total_text)
        if total is None:
            raise AssertionError(f"Could not parse cart total from text: {total_text}")
        return total

    def assert_total_not_exceeds(self, budget_per_item: float, items_count: int) -> None:
        total = self.get_total()
        allowed_total = budget_per_item * items_count
        assert total <= allowed_total, f"Cart total {total} exceeds allowed total {allowed_total}"