import allure
import pytest


@allure.feature("UI")
@allure.story("Delete todo")
@pytest.mark.ui
@allure.title("A user can delete a seeded todo")
def test_user_can_delete_a_todo(todo_page, api, unique_suffix):
    title = f"Old task {unique_suffix}"

    with allure.step("Seed a todo via the API"):
        api.create_todo(title)

    with allure.step("Reload so the seeded todo is rendered"):
        todo_page.goto()
        todo_page.expect_visible(title)

    with allure.step("Delete the todo from the UI"):
        todo_page.delete(title)

    with allure.step("The todo is removed from the list"):
        todo_page.expect_absent(title)
