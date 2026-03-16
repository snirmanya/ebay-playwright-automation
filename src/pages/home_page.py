from src.pages.base_page import BasePage


class HomePage(BasePage):
    SEARCH_INPUT = [
        "input[id='gh-ac']",
        "xpath=//input[@placeholder='Search for anything']",
        "xpath=//input[contains(@aria-label,'Search')]"
    ]

    SEARCH_BUTTON = [
        ".gh-search-button",
        "xpath=//button[@id ='gh-search-btn']",
        "xpath=//button[@class='gh-search-button btn btn--primary']"
    ]

    def search(self, query: str) -> None:
        self.fill(self.SEARCH_INPUT, query)
        self.click(self.SEARCH_BUTTON)