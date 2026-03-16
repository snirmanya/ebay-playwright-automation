from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError
from src.utils.logger import LOGS_DIR, get_logger


class SmartLocator:
    def __init__(self, page: Page):
        self.page = page
        self.logger = get_logger(self.__class__.__name__)

    def find_first_visible(
        self,
        locators: list[str],
        timeout_per_locator: int = 2000,
        optional: bool = False,
    ) -> Locator:
        attempts = 0
        for index, locator_str in enumerate(locators, start=1):
            attempts += 1
            try:
                self.logger.info(f"Trying locator #{index}/{len(locators)}: {locator_str}")
                locator = self.page.locator(locator_str).first
                locator.wait_for(
                    state="visible",
                    timeout=timeout_per_locator
                )
                self.logger.info(f"Locator succeeded after {attempts} attempt(s): {locator_str}")
                return locator
            except PlaywrightTimeoutError:
                self.logger.warning(f"Locator failed (#{index}): {locator_str}")
        if optional:
            self.logger.warning(f"Optional element not found: all {len(locators)} locators failed after {attempts} attempts")
        else:
            self.logger.error(f"All {len(locators)} locators failed after {attempts} attempts")
            self.page.screenshot(path=str(LOGS_DIR / "final_locator_failure.png"))
        raise Exception(f"All locators failed: {locators}")