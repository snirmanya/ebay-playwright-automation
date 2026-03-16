import yaml
import pytest
import logging
from pathlib import Path
from playwright.sync_api import sync_playwright

# Set up logging
artifacts_logs_dir = Path("artifacts/logs")
artifacts_logs_dir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(artifacts_logs_dir / "test_run.log")
    ]
)

def load_data():
    """
    Load test data from a YAML file.
    Returns:
        dict: The loaded test data.
    Raises:
        FileNotFoundError: If the test data file is not found.
        yaml.YAMLError: If there's an error parsing the YAML file.
    """
    try:
        with open("src/data/test_data.yaml", "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
            logging.info("Test data loaded successfully.")
            return data
    except FileNotFoundError:
        logging.error("Test data file 'src/data/test_data.yaml' not found.")
        raise
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML file: {e}")
        raise

@pytest.fixture(scope="session")
def test_data():
    """
    Session-scoped fixture to provide test data loaded from YAML.
    Returns:
        dict: Test data dictionary.
    """
    return load_data()

def pytest_addoption(parser):
    """
    Add command-line options to pytest.
    Args:
        parser: Pytest parser object to add options to.
    """
    parser.addoption("--headless", action="store", default="true", help="Run browser in headless mode (true/false)")

# "webkit"
@pytest.fixture(params=["chromium", "firefox"])
def browser_page(test_data, request):
    """
    Fixture to provide a Playwright page instance for each browser type.
    This fixture launches a browser (chromium, firefox, or webkit), sets up context with video recording,
    tracing, and creates a new page. It yields the page for tests to use, and after the test,
    stops tracing, saves the trace, takes a screenshot on failure, and closes the browser.
    Args:
        test_data: Test data fixture.
        request: Pytest request object.
    Yields:
        Page: Playwright page object.
    """
    browser_name = request.param
    headless = str(request.config.getoption("--headless")).strip().lower() == "true"
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    videos_dir = artifacts_dir / "videos"
    videos_dir.mkdir(parents=True, exist_ok=True)
    traces_dir = artifacts_dir / "traces"
    traces_dir.mkdir(parents=True, exist_ok=True)
    screenshots_dir = artifacts_dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    logging.info(f"Launching {browser_name} browser in {'headless' if headless else 'headed'} mode.")

    try:
        with sync_playwright() as p:
            browser_type = getattr(p, browser_name)
            browser = browser_type.launch(
                headless=headless
            )
            context = browser.new_context(
                record_video_dir=str(videos_dir),
                record_video_size={"width": 1280, "height": 720},
            )
            context.tracing.start(
                screenshots=True,
                snapshots=True,
                sources=True,
            )
            page = context.new_page()
            page.set_default_timeout(test_data.get("timeout_ms", 30000))
            logging.info(f"Browser {browser_name} launched and page created.")
            yield page

            # Stop tracing and save
            test_name = request.node.name
            trace_file = traces_dir / f"{test_name}.zip"
            context.tracing.stop(path=str(trace_file))
            logging.info(f"Trace saved to {trace_file}")

            # Screenshot on failure
            rep_call = getattr(request.node, "rep_call", None)
            if rep_call and rep_call.failed:
                screenshot_file = screenshots_dir / f"{test_name}.png"
                page.screenshot(path=str(screenshot_file), full_page=True)
                logging.info(f"Screenshot saved to {screenshot_file} due to test failure.")

            context.close()
            browser.close()
            logging.info(f"Browser {browser_name} closed.")
    except Exception as e:
        logging.error(f"Error during browser setup or teardown for {browser_name}: {e}")
        raise
