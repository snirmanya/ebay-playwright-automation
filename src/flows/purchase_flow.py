import allure
from playwright.sync_api import Page
from src.pages.home_page import HomePage
from src.pages.search_results_page import SearchResultsPage
from src.utils.logger import LOGS_DIR, get_logger
from src.utils.retry_helper import retry
from typing import List
from src.pages.product_page import ProductPage
from src.pages.cart_page import CartPage


logger = get_logger("ebay_flows")

class PurchaseFlows:
    def __init__(self, page: Page) -> None:
        self.page = page

    def guest_purchase_flow(
        self,
        query: str,
        max_price: float,
        limit: int,
        base_url: str,
        cart_url: str):

        """Complete guest purchase flow: search, filter, collect URLs, add to cart, assert total."""
        logger.info("Starting guest purchase flow")
        with allure.step("Open marketplace home page"):
            self.page.goto(base_url)

        with allure.step("Search for products"):
            self.search_by_query(query=query)

        with allure.step("Apply max price filter"):
            self.apply_max_price_filter(max_price=max_price)

        with allure.step("Collect product URLs"):
            urls = self.collect_item_urls_under_price(max_price=max_price, limit=limit)
        logger.info(f"Collected URLs: {urls}")

        with allure.step("Add collected products to cart"):
            added_count = self.add_items_to_cart(urls=urls)

        with allure.step("Verify cart total does not exceed the allowed budget"):
            self.assert_cart_total_not_exceeds(
                budget_per_item=max_price,
                items_count=added_count,
                cart_url=cart_url,
            )

    def search_by_query(self, query: str) -> None:
        """Run search on the home page. Leaves the user on search results."""
        home = HomePage(self.page)
        retry(lambda: home.search(query))

    def apply_max_price_filter(self, max_price: float) -> None:
        """Apply max price filter on the current search results page, if the filter is available."""
        results = SearchResultsPage(self.page)
        results.apply_max_price_filter_if_available(max_price)

    def collect_item_urls_under_price(
        self, max_price: float, limit: int = 5) -> List[str]:
        """Collect up to `limit` item URLs from the current search results where price <= max_price."""
        results = SearchResultsPage(self.page)
        return retry(
            lambda: results.collect_item_urls_under_price(
                max_price=max_price,
                limit=limit
            )
        )

    def add_items_to_cart(self, urls: List[str]) -> int:
        """Add items to cart; skip missing/removed listings. Returns count of items actually added."""
        count = 0
        for url in urls:
            try:
                logger.info(f"Navigating to product page: {url}")
                retry(lambda: self.page.goto(url))
                product_page = ProductPage(self.page)
                if product_page.is_page_missing():
                    logger.warning(f"Product page missing or removed: {url}")
                    continue
                add_to_cart_locator = product_page.wait_for_product_ready()
                product_page.add_to_cart(add_to_cart_locator)
                count += 1
                logger.info(f"Successfully added item to cart: {url}")
            except Exception as e:
                logger.error(f"Failed to add item to cart: {url}, error: {e}")
                continue
        logger.info(f"Added {count} items to cart out of {len(urls)} URLs")
        return count

    def assert_cart_total_not_exceeds(
            self,
            budget_per_item: float,
            items_count: int,
            cart_url: str) -> None:
        cart = CartPage(self.page)
        logger.info("Navigating to cart page")
        retry(lambda: self.page.goto(cart_url))
        total = retry(cart.get_total)
        allowed_total = budget_per_item * items_count
        logger.info(f"Cart total is {int(total)}, allowed total is {allowed_total}")
        assert total <= allowed_total, f"Cart total {total} exceeds allowed total {allowed_total}"
        cart.screenshot(str(LOGS_DIR / "cart_page.png"))
