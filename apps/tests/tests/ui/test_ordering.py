import allure
import pytest
from playwright.sync_api import expect


@allure.feature("UI")
@allure.story("List ordering")
@pytest.mark.ui
@allure.title("Newly added todos appear newest-first in the list")
def test_list_is_ordered_newest_first(todo_page, unique_suffix):
    # Two todos sharing this run's unique suffix so we can isolate them from the
    # ~10 seeded demo todos and assert ONLY on relative order of our own data.
    first = f"First {unique_suffix}"
    second = f"Second {unique_suffix}"

    with allure.step("Add two todos in sequence"):
        todo_page.add_todo(first)
        todo_page.expect_visible(first)
        todo_page.add_todo(second)
        todo_page.expect_visible(second)

    with allure.step("Only our two todos match the unique suffix"):
        ours = todo_page.items().filter(has_text=unique_suffix)
        expect(ours).to_have_count(2)

    with allure.step("The most recently created todo is listed first"):
        expect(ours.nth(0)).to_contain_text(second)
        expect(ours.nth(1)).to_contain_text(first)
