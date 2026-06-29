import allure
import pytest


@allure.feature("UI")
@allure.story("Complete todo")
@pytest.mark.ui
@allure.title("A user can mark a seeded todo as completed")
def test_user_can_complete_a_todo(todo_page, api, unique_suffix):
    title = f"Walk dog {unique_suffix}"

    with allure.step("Seed an incomplete todo via the API"):
        api.create_todo(title, completed=False)

    with allure.step("Reload so the seeded todo is rendered"):
        todo_page.goto()
        todo_page.expect_visible(title)

    with allure.step("Toggle the todo's checkbox"):
        todo_page.toggle(title)

    with allure.step("The checkbox is now checked"):
        todo_page.expect_completed(title)
