"""UI state tests: empty list, loading indicator, error alert, Retry recovery.

These tests use Playwright's ``page.route()`` to intercept the ``/api/todos/``
endpoint so that the SPA renders each state deterministically without relying
on timing or network conditions.

All route handlers are scoped to the page instance and cleaned up automatically
when the page is closed (per-test isolation guaranteed by pytest-playwright).
"""
import allure
import pytest
from playwright.sync_api import Page, expect

from pages.todo_page import EMPTY_STATE_TEXT, TodoPage


# ---------------------------------------------------------------------------
# Empty state
# ---------------------------------------------------------------------------


@allure.feature("UI")
@allure.story("Empty state")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ui
@allure.title("Empty state message is shown when the API returns an empty list")
def test_empty_state_shown_when_no_todos(page: Page, base_url: str):
    """Intercept the list endpoint to return [] and verify the empty-state text."""
    with allure.step("Intercept GET /api/todos/ to return an empty array"):
        page.route(
            "**/api/todos/",
            lambda route: route.fulfill(
                status=200,
                content_type="application/json",
                body="[]",
            ),
        )

    tp = TodoPage(page)

    with allure.step("Navigate to the SPA"):
        tp.goto()

    with allure.step("The empty-state message is visible"):
        tp.expect_empty_state()


# ---------------------------------------------------------------------------
# Error state
# ---------------------------------------------------------------------------


@allure.feature("UI")
@allure.story("Error state")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
@allure.title("Error alert is shown when the API returns a 500 error")
def test_error_state_shown_on_api_failure(page: Page, base_url: str):
    """Intercept the list endpoint to return 500 and verify the error alert."""
    with allure.step("Intercept GET /api/todos/ to return a 500 error"):
        page.route(
            "**/api/todos/",
            lambda route: route.fulfill(
                status=500,
                content_type="application/json",
                body='{"detail": "Internal Server Error"}',
            ),
        )

    tp = TodoPage(page)

    with allure.step("Navigate to the SPA"):
        tp.goto()

    with allure.step("The error alert is visible"):
        tp.expect_error_state()

    with allure.step("The Retry button is visible inside the alert"):
        tp.expect_retry_visible()


# ---------------------------------------------------------------------------
# Retry recovery
# ---------------------------------------------------------------------------


@allure.feature("UI")
@allure.story("Error state")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
@allure.title("Clicking Retry recovers from an API error and shows the todo list")
def test_retry_recovers_from_error(page: Page, api, unique_suffix: str):
    """All automated requests (including TanStack Query's auto-retry) return 500.
    Once the error state is shown, the interceptor is removed and the manual
    Retry click hits the real server and recovers.

    TanStack Query is configured with retry=1 so the error state appears only
    after the original request plus one automatic retry both fail. The
    ``expect_error_state()`` auto-waits up to 5 s, which is plenty.
    """
    title = f"Retry recovery {unique_suffix}"

    with allure.step("Seed a todo via the API so the recovery has data to show"):
        api.create_todo(title)

    url_pattern = "**/api/todos/"

    with allure.step("Intercept ALL GET /api/todos/ requests to return 500"):
        page.route(
            url_pattern,
            lambda route: route.fulfill(
                status=500,
                content_type="application/json",
                body='{"detail": "Internal Server Error"}',
            ),
        )

    tp = TodoPage(page)

    with allure.step("Navigate — initial load and auto-retry both fail"):
        tp.goto()

    with allure.step("Error alert is visible after TanStack Query exhausts retries"):
        tp.expect_error_state()

    with allure.step("Remove the route interceptor so the next request reaches the server"):
        page.unroute(url_pattern)

    with allure.step("Click Retry"):
        tp.click_retry()

    with allure.step("The list loads and the seeded todo is visible"):
        tp.expect_visible(title)
