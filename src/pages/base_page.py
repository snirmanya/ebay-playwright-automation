from playwright.sync_api import Page
from src.utils.smart_locator import SmartLocator
from src.utils.logger import get_logger


class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.smart = SmartLocator(page)
        self.logger = get_logger(self.__class__.__name__)

    def open(self, url: str) -> None:
        self.logger.info(f"Opening URL: {url}")
        self.page.goto(url)

    def click(self, locators: list[str]) -> None:
        self.smart.find_first_visible(locators).click()

    def fill(self, locators: list[str], value: str) -> None:
        self.smart.find_first_visible(locators).fill(value)

    def get_text(self, locators: list[str]) -> str:
        return self.smart.find_first_visible(locators).inner_text()

    def is_visible(self, locators: list[str], timeout: int = 2000) -> bool:
        """Returns True if any of the locators finds a visible element. Uses optional=True so missing is logged as WARNING."""
        try:
            self.smart.find_first_visible(locators, timeout_per_locator=timeout, optional=True)
            return True
        except Exception:
            return False

    def screenshot(self, path: str) -> None:
        self.page.screenshot(
            path=path,
            full_page=True
        )