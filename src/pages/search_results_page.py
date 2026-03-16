from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from src.pages.base_page import BasePage


class SearchResultsPage(BasePage):
    PRODUCT_LINK_IN_CARD = (
        "xpath=//ul[contains(@class,'srp-results')]//li//a[contains(@class,'s-card__link') "
        "and contains(@class,'image-treatment')]"
    )
    NEXT_BUTTONS = [
        "a[aria-label='Go to next search page']",
        "xpath=//a[contains(@aria-label,'next')]"
    ]

    MAX_PRICE_INPUT = [
        "xpath=//input[contains(@aria-label,'Maximum')]",
        "input[aria-label*='Maximum']"
    ]

    APPLY_PRICE_BUTTON = [
        "xpath=//button[contains(@aria-label,'Submit price range')]",
        "button[aria-label*='Submit price range']"
    ]

    def apply_max_price_filter_if_available(self, max_price: float) -> None:
        try:
            max_price_input = self.smart.find_first_visible(
                self.MAX_PRICE_INPUT,
                timeout_per_locator=5000,
            )
        except Exception as e:
            self.logger.warning(f"Max price filter not available or timed out: {e}")
            return

        try:
            max_price_input.fill(str(int(max_price)))
            self.page.locator("body").click()  # Trigger to activate the apply button
            apply_button = self.smart.find_first_visible(
                self.APPLY_PRICE_BUTTON,
                timeout_per_locator=2000
            )
            apply_button.click(timeout=5000)
            self.page.wait_for_load_state("domcontentloaded")
            self.logger.info(f"Applied max price filter: {max_price}")
        except PlaywrightTimeoutError as e:
            self.logger.warning(f"Max price filter not available or timed out: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error applying max price filter: {e}")

    def collect_item_urls_under_price(self, max_price: float, limit: int = 5) -> list[str]:
        """Return the first `limit` product href links from search results using XPath."""
        try:
            self.page.wait_for_selector(
                self.PRODUCT_LINK_IN_CARD,
                timeout=5000
            )
            links = self.page.locator(self.PRODUCT_LINK_IN_CARD)
            link_count = min(links.count(), limit)
            urls: list[str] = []
            for i in range(link_count):
                href = links.nth(i).get_attribute("href", timeout=3000)
                if href:
                    urls.append(href)
            self.logger.info(f"Collected {len(urls)} product href links.")
            return urls
        except PlaywrightTimeoutError:
            self.logger.warning("No product cards found on the search results page.")
            return []

