import random
from playwright.sync_api import Locator

from src.pages.base_page import BasePage


class ProductPage(BasePage):
    ADD_TO_CART = [
        "#atcBtn_btn_1",
        "[data-testid='x-atc-action']",
        "xpath=//span[contains(text(),'Add to cart')]"
    ]

    # Only product-area dropdowns (size/color/qty); fallback to any select, max 5 to avoid header/footer
    DROPDOWNS_SCOPED = "main select"
    DROPDOWNS_FALLBACK = "select"
    MAX_DROPDOWNS = 5

    # eBay "page not found" / listing removed
    PAGE_MISSING_TEXT = "We looked everywhere"

    def is_page_missing(self) -> bool:
        """True if we landed on eBay's 'page is missing' / listing removed error."""
        try:
            return self.page.get_by_text(self.PAGE_MISSING_TEXT, exact=False).is_visible(timeout=2000)
        except Exception:
            return False

    def wait_for_product_ready(self, timeout_ms: int = 8000) -> Locator:
        """Wait for product page to be ready (Add to cart visible). Returns the button locator for reuse."""
        return self.smart.find_first_visible(self.ADD_TO_CART, timeout_per_locator=timeout_ms)

    def choose_random_variants_if_exist(self) -> None:
        dropdowns = self.page.locator(self.DROPDOWNS_SCOPED)
        try:
            count = dropdowns.count()
        except Exception:
            count = 0
        if count == 0:
            dropdowns = self.page.locator(self.DROPDOWNS_FALLBACK)
            try:
                count = min(dropdowns.count(), self.MAX_DROPDOWNS)
            except Exception:
                return
        else:
            count = min(count, self.MAX_DROPDOWNS)

        for i in range(count):
            dropdown = dropdowns.nth(i)
            try:
                options = dropdown.locator("option")
                option_count = min(options.count(), 20)
                valid_indexes = [
                    idx for idx in range(1, option_count)
                    if options.nth(idx).get_attribute("value")
                ]
                if valid_indexes:
                    chosen = random.choice(valid_indexes)
                    value = options.nth(chosen).get_attribute("value")
                    if value:
                        dropdown.select_option(value=value, timeout=2000)
            except Exception:
                continue

    def add_to_cart(self, add_to_cart_locator: Locator | None = None) -> None:
        self.choose_random_variants_if_exist()
        if add_to_cart_locator is not None:
            add_to_cart_locator.click()
        else:
            self.click(self.ADD_TO_CART)