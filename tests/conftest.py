import base64
import os
import logging
from pathlib import Path

import pytest
import pandas as pd
from dotenv import load_dotenv
from playwright.sync_api import Playwright, Browser
import pytest_html

from pages.index import Pages
from utils.api_manager import APIManager
from services.pedigree_service import PedigreeService
from pedigree.api.data import load_data, build_index
from utils.integrity import IntegrityValidators


load_dotenv(Path(__file__).parent.parent / ".env", override=True)

HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

print(f"\nBrowser headless mode: {HEADLESS}")


@pytest.fixture(scope="session")
def api_base_url():
    return os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


@pytest.fixture(scope="session")
def api_manager(api_base_url):
    api = APIManager(api_base_url)

    api.session.cookies.set("isAutomationTestRun", "true", domain="127.0.0.1", path="/")

    return api


@pytest.fixture(scope="session")
def pedigree_service(api_manager):
    return PedigreeService(api_manager)


@pytest.fixture(scope="session")
def ui_base_url():
    return os.getenv("UI_BASE_URL", "http://localhost:5500")


@pytest.fixture(scope="session")
def browser(playwright: Playwright):
    browser = playwright.chromium.launch(headless=HEADLESS)
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def page(browser: Browser):
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture
def pages(page, ui_base_url) -> Pages:
    return Pages(page, ui_base_url)


@pytest.fixture
def clean_data():
    return load_data()


@pytest.fixture
def clean_index(clean_data):
    return build_index(clean_data)


@pytest.fixture
def integrity_validators():
    return IntegrityValidators()


@pytest.fixture
def load_scenario_csv():

    def _clean_id(value):
        if pd.isna(value):
            return None
        if isinstance(value, str) and not value.strip():
            return None
        return str(int(float(value)))

    def _load(scenario_name=None, path=None):
        logger = logging.getLogger("conftest")

        if path is None:
            path = Path(f"data/manipulation/scenarios/{scenario_name}.csv")
            logger.info(f"Loading scenario: {path}")
        else:
            logger.info(f"Loading from path: {path}")

        df = pd.read_csv(path)
        df.columns = df.columns.str.strip()

        data = [
            {
                "id": str(int(float(row["ID"]))),
                "name": (
                    row["Name"].strip() if isinstance(row["Name"], str) else row["Name"]
                ),
                "breed": (
                    row["Breed"].strip()
                    if isinstance(row["Breed"], str)
                    else row["Breed"]
                ),
                "sex": (
                    row["Sex"].strip() if isinstance(row["Sex"], str) else row["Sex"]
                ),
                "height_cm": (
                    float(row["Height_cm"]) if pd.notna(row["Height_cm"]) else None
                ),
                "weight_kg": (
                    float(row["Weight_kg"]) if pd.notna(row["Weight_kg"]) else None
                ),
                "sire_id": _clean_id(row["Sire_ID"]),
                "dam_id": _clean_id(row["Dam_ID"]),
            }
            for _, row in df.iterrows()
        ]

        logger.info(f"Loaded {len(data)} dogs")
        return data

    return _load


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    marker = item.get_closest_marker("testcase")

    if marker:
        report.testcase_id = str(marker.args[0])

    extra = getattr(report, "extra", [])

    if report.failed:
        page = item.funcargs.get("page")

        if page:
            screenshot = page.screenshot(full_page=True)
            encoded = base64.b64encode(screenshot).decode()

            extra.append(pytest_html.extras.image(f"data:image/png;base64,{encoded}"))  # type: ignore

    report.extras = extra


def pytest_html_results_table_header(cells):
    cells.append("TestCase ID")


def pytest_html_results_table_row(report, cells):
    cells.append(getattr(report, "testcase_id", ""))
