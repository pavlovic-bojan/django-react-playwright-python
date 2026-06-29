import allure
import pytest


@allure.feature("UI")
@allure.story("Validation")
@pytest.mark.ui
@allure.title("Submitting a blank title shows a validation error")
def test_blank_title_is_rejected(todo_page):
    with allure.step("Submit the form with an empty title"):
        todo_page.add_todo("")

    with allure.step("The 'Title is required' error is shown"):
        todo_page.expect_validation_error()
