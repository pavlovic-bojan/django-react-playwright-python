"""Page Object Model for the Todo SPA.

Semantic, user-facing locators only (get_by_role / get_by_label / get_by_text).
No CSS/XPath, no sleeps — methods are intention-revealing and assertions use
web-first ``expect(...)`` which auto-retries.

Expected accessible surface (from the frontend source and api-contract):
* A labeled "Title" text input
* An "Add" submit button
* Each todo rendered as a ``listitem`` containing its title text
* A ``checkbox`` aria-labeled by the todo title
* A delete button aria-labeled ``Delete <title>``
* Validation message exactly ``"Title is required"``
* Loading indicator: ``role="status"`` containing "Loading todos"
* Error indicator: ``role="alert"`` containing a Retry button
* Empty state:  paragraph "No todos yet. Add your first one above."
"""
from playwright.sync_api import Locator, Page, expect

from .base_page import BasePage

VALIDATION_REQUIRED = "Title is required"
EMPTY_STATE_TEXT = "No todos yet. Add your first one above."


class TodoPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.title_input = page.get_by_label("Title")
        self.add_button = page.get_by_role("button", name="Add")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def add_todo(self, title: str) -> None:
        """Fill the title input and click Add."""
        self.title_input.fill(title)
        self.add_button.click()

    def toggle(self, title: str) -> None:
        """Click the checkbox for the named todo (checked ↔ unchecked)."""
        self.checkbox(title).click()

    def delete(self, title: str) -> None:
        """Click the delete button for the named todo."""
        self.item(title).get_by_role("button", name=f"Delete {title}").click()

    def click_retry(self) -> None:
        """Click the Retry button shown in the error state."""
        self.retry_button().click()

    # ------------------------------------------------------------------
    # Locators
    # ------------------------------------------------------------------

    def item(self, title: str) -> Locator:
        """The listitem element containing the given title text."""
        return self.page.get_by_role("listitem").filter(has_text=title)

    def items(self) -> Locator:
        """All listitem elements (the full todo list)."""
        return self.page.get_by_role("listitem")

    def checkbox(self, title: str) -> Locator:
        """The checkbox aria-labeled by the given todo title."""
        return self.page.get_by_role("checkbox", name=title)

    def validation_error(self) -> Locator:
        """The 'Title is required' validation message element."""
        return self.page.get_by_text(VALIDATION_REQUIRED)

    def loading_status(self) -> Locator:
        """The loading spinner region (role='status')."""
        return self.page.get_by_role("status")

    def error_alert(self) -> Locator:
        """The error state container (role='alert')."""
        return self.page.get_by_role("alert")

    def retry_button(self) -> Locator:
        """The Retry button shown inside the error alert."""
        return self.page.get_by_role("button", name="Retry")

    def empty_state(self) -> Locator:
        """The 'No todos yet' paragraph shown when the list is empty."""
        return self.page.get_by_text(EMPTY_STATE_TEXT)

    # ------------------------------------------------------------------
    # Web-first assertions (auto-retrying via expect())
    # ------------------------------------------------------------------

    def expect_visible(self, title: str) -> None:
        """Assert the todo with the given title is visible in the list."""
        expect(self.item(title)).to_be_visible()

    def expect_absent(self, title: str) -> None:
        """Assert no listitem with the given title exists."""
        expect(self.item(title)).to_have_count(0)

    def expect_completed(self, title: str) -> None:
        """Assert the checkbox for the named todo is checked."""
        expect(self.checkbox(title)).to_be_checked()

    def expect_not_completed(self, title: str) -> None:
        """Assert the checkbox for the named todo is NOT checked."""
        expect(self.checkbox(title)).not_to_be_checked()

    def expect_validation_error(self) -> None:
        """Assert the 'Title is required' validation message is visible."""
        expect(self.validation_error()).to_be_visible()

    def expect_empty_state(self) -> None:
        """Assert the empty-state message is visible."""
        expect(self.empty_state()).to_be_visible()

    def expect_error_state(self) -> None:
        """Assert the error alert is visible."""
        expect(self.error_alert()).to_be_visible()

    def expect_retry_visible(self) -> None:
        """Assert the Retry button is visible inside the error alert."""
        expect(self.retry_button()).to_be_visible()
