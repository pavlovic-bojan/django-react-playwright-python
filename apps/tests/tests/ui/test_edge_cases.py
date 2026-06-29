"""UI edge-case tests.

Covers: title trimming, long title (max length), whitespace-only validation,
completed-state persistence across a reload, and uncompleting a todo.

All tests are isolated via ``unique_suffix`` and the ``api`` fixture so they
never depend on seeded demo data and are safe to run in any order.
"""
import allure
import pytest
from playwright.sync_api import expect


# ---------------------------------------------------------------------------
# Title validation — whitespace-only input
# ---------------------------------------------------------------------------


@allure.feature("UI")
@allure.story("Validation")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ui
@allure.title("Whitespace-only title shows the required-field validation error")
def test_whitespace_only_title_shows_validation_error(todo_page):
    """Zod trims the value before length check, so '   ' → '' → validation error."""
    with allure.step("Submit the form with a whitespace-only title"):
        todo_page.add_todo("   ")

    with allure.step("The 'Title is required' error is shown"):
        todo_page.expect_validation_error()


# ---------------------------------------------------------------------------
# Title trimming
# ---------------------------------------------------------------------------


@allure.feature("UI")
@allure.story("Create todo")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ui
@allure.title("Leading and trailing spaces are trimmed before the todo is created")
def test_title_is_trimmed_on_create(todo_page, unique_suffix):
    """The zod schema applies .trim(); the stored title must match the trimmed form."""
    raw_title = f"  Trimmed test {unique_suffix}  "
    clean_title = f"Trimmed test {unique_suffix}"

    with allure.step(f"Add a todo with extra surrounding spaces: '{raw_title}'"):
        todo_page.add_todo(raw_title)

    with allure.step(f"The list shows the trimmed title '{clean_title}'"):
        todo_page.expect_visible(clean_title)


# ---------------------------------------------------------------------------
# Max-length title (255 characters)
# ---------------------------------------------------------------------------


@allure.feature("UI")
@allure.story("Create todo")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.ui
@allure.title("A 255-character title is accepted and displayed in the list")
def test_255_char_title_is_accepted(todo_page, unique_suffix):
    """Boundary: contract allows titles up to 255 chars; the UI must accept them."""
    # Build a title that is exactly 255 chars and still contains the unique suffix
    # so the item can be located without ambiguity.
    prefix = f"Long {unique_suffix} "
    padding = "x" * (255 - len(prefix))
    title_255 = prefix + padding
    assert len(title_255) == 255, f"Expected 255 chars, got {len(title_255)}"

    with allure.step("Add a 255-character todo"):
        todo_page.add_todo(title_255)

    with allure.step("The todo appears in the list"):
        todo_page.expect_visible(title_255)


# ---------------------------------------------------------------------------
# Completed-state persistence across a full page reload
# ---------------------------------------------------------------------------


@allure.feature("UI")
@allure.story("Complete todo")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.ui
@allure.title("Completed state is persisted after a full page reload")
def test_completed_state_persists_after_reload(todo_page, api, unique_suffix):
    """Toggling sends a PATCH; the state must survive a reload (server-side truth)."""
    title = f"Persist reload {unique_suffix}"

    with allure.step("Seed an incomplete todo via the API"):
        api.create_todo(title, completed=False)

    with allure.step("Reload and verify the todo appears"):
        todo_page.goto()
        todo_page.expect_visible(title)

    with allure.step("Toggle the todo to completed"):
        todo_page.toggle(title)
        todo_page.expect_completed(title)

    with allure.step("Reload the page"):
        todo_page.goto()

    with allure.step("The todo is still shown as completed after reload"):
        todo_page.expect_completed(title)


# ---------------------------------------------------------------------------
# Uncompleting a todo (toggle from checked → unchecked)
# ---------------------------------------------------------------------------


@allure.feature("UI")
@allure.story("Complete todo")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.ui
@allure.title("A completed todo can be unchecked back to incomplete")
def test_user_can_uncomplete_a_todo(todo_page, api, unique_suffix):
    """Toggling a completed todo should uncheck it (PATCH completed=false)."""
    title = f"Uncomplete me {unique_suffix}"

    with allure.step("Seed a completed todo via the API"):
        api.create_todo(title, completed=True)

    with allure.step("Reload so the seeded todo renders as checked"):
        todo_page.goto()
        todo_page.expect_completed(title)

    with allure.step("Click the checkbox to uncheck it"):
        todo_page.toggle(title)

    with allure.step("The checkbox is now unchecked"):
        todo_page.expect_not_completed(title)


# ---------------------------------------------------------------------------
# Duplicate titles
# ---------------------------------------------------------------------------


@allure.feature("UI")
@allure.story("Create todo")
@allure.severity(allure.severity_level.MINOR)
@pytest.mark.ui
@allure.title("Two todos with identical titles can coexist in the list")
def test_duplicate_titles_are_allowed(todo_page, unique_suffix):
    """The API contract does not impose uniqueness; duplicates must both appear."""
    title = f"Dupe {unique_suffix}"

    with allure.step("Add the same title twice"):
        todo_page.add_todo(title)
        todo_page.expect_visible(title)
        todo_page.add_todo(title)

    with allure.step("Both copies are present (count = 2)"):
        expect(todo_page.items().filter(has_text=title)).to_have_count(2)
