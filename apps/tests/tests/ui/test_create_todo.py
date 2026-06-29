import allure
import pytest


@allure.feature("UI")
@allure.story("Create todo")
@pytest.mark.ui
@allure.title("A user can add a new todo from the UI")
def test_user_can_add_a_todo(todo_page, unique_suffix):
    title = f"Buy milk {unique_suffix}"

    with allure.step(f"Add a todo titled '{title}'"):
        todo_page.add_todo(title)

    with allure.step("The new todo appears in the list"):
        todo_page.expect_visible(title)
