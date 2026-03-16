## Playwright eBay E2E

This project implements the eBay E2E automation with **Playwright + Pytest**, using **POM**, **OOP**, **data‑driven tests**, **smart locators with fallback**, **retry logic**, and **parallel / multi‑browser runs**.
Install Python version: 3.14
### How to install

- **Create / activate venv** (optional but recommended).
- Install dependencies:

```bash
pip install -r requirements.txt
playwright install
```

### How to run the tests

- **Basic run, all browsers (chromium, firefox, webkit)**:

```bash
pytest --alluredir=allure-results-run_$(date +%Y%m%d_%H%M%S)
```

- **Parallel execution** (leverages `pytest-xdist`):

```bash
pytest -n auto --alluredir=allure-results-run_$(date +%Y%m%d_%H%M%S)
```

- **Generate Allure report** (configured via `pytest.ini` to write into `allure-results`):

```bash
allure serve allure-results-run_$(date +%Y%m%d_%H%M%S) | from the previous step
```

### Architecture overview

- **Tests**:
  - `test_guest_purchase_flow.py` – E2E scenario that calls the flow steps separately:
    - `search_by_query`, `apply_max_price_filter`, `collect_item_urls_under_price`
    - `add_items_to_cart`, `assert_cart_total_not_exceeds`

- **Flows** (`purchase_flow.py`):
  - Search and results (separate steps):
    - `search_by_query(page, query) -> None`
    - `apply_max_price_filter(page, max_price) -> None`
    - `collect_item_urls_under_price(page, max_price, limit=5) -> list[str]`
  - Cart:
    - `add_items_to_cart(page, urls, base_url="") -> int`
    - `assert_cart_total_not_exceeds(page, budget_per_item, items_count, cart_url=...) -> None`
  - Each function uses page objects, **retry logic**, logging, and screenshots.

- **Pages (POM)**:
  - `base_page.py` – shared behaviors, `SmartLocator` usage, screenshots, navigation.
  - `home_page.py` – search box + search button, with multiple locators per element.
  - `search_results_page.py` – collects item URLs under a given max price across pages (paging support).
  - `product_page.py` – random variant selection and add‑to‑cart logic.
  - `cart_page.py` – cart total parsing and assertion.

- **Utils / infrastructure**:
  - `smart_locator.py` – **resilient locator utility**:
    - Accepts a list of locators per element.
    - Tries each with a timeout; logs success/failure per locator.
    - Takes a screenshot and fails clearly if all locators fail.
  - `retry_helper.py` – generic retry helper for unstable environments (timeouts, flakiness).
  - `price_parser.py` – parses numeric value from price strings (e.g. `"US $123.45"`).
  - `logger.py` – central logger, logging both to console and `logs/test_run.log`.

- **Configuration / data‑driven**:
  - `data/test_data.yaml` – external test data:
    - `base_url`, `query`, `max_price`, `limit`, `headless`, `timeout_ms`.
  - `conftest.py` – Pytest fixtures:
    - `test_data` – loads YAML.
    - `browser_page` – parameterized across `chromium`, `firefox`, and `webkit`, sets timeout and headless from data.
  - `pytest.ini` – default options and test path.

### Assumptions / limitations

- **Login**: Tests run as a **guest** (no login step). This matches the exercise requirement without dealing with credentials.
- **Anti-bot protections / CAPTCHA**: Due to anti-bot protections and CAPTCHA on eBay, the solution assumes either guest flow availability or a pre-authenticated session created manually. The automation framework is designed to support real-world protected environments without attempting to bypass security mechanisms.
