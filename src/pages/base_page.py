import logging
from pathlib import Path
from typing import Self

from playwright.sync_api import Page


class BasePage:
    path: str = ""
    page: Page
    base_url: str

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url
        self.log = logging.getLogger(self.__class__.__name__)

    def navigate(self) -> Self:
        self.page.goto(f"{self.base_url}{self.path}")
        return self

    def _log_and_screenshot(self, message: str) -> None:
        self.log.error(message)

        try:
            screenshots_dir = Path("reports/screenshots")
            screenshots_dir.mkdir(parents=True, exist_ok=True)

            file_path = screenshots_dir / f"{self.__class__.__name__}.png"
            self.page.screenshot(path=str(file_path))

            self.log.error(f"Screenshot saved: {file_path}")

        except Exception as e:
            self.log.error(f"Failed to capture screenshot: {e}")
