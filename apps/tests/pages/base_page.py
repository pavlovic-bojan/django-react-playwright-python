"""Base for all Page Objects."""
from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def goto(self, path: str = "/") -> None:
        """Navigate relative to the configured base_url."""
        self.page.goto(path)
