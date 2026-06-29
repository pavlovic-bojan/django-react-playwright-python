"""API validation contract: blank/whitespace titles are rejected with 400."""
import allure
import pytest


@allure.feature("API")
@allure.story("Validation")
@pytest.mark.api
@allure.title("POST /todos/ with an empty title returns 400 with a field error")
def test_blank_title_returns_400(api_context):
    res = api_context.post("todos/", data={"title": ""})

    assert res.status == 400, res.text()
    body = res.json()
    # DRF error shape: field-keyed arrays of messages.
    assert "title" in body
    assert isinstance(body["title"], list) and body["title"]


@allure.feature("API")
@allure.story("Validation")
@pytest.mark.api
@allure.title("POST /todos/ with a whitespace-only title returns 400")
def test_whitespace_title_returns_400(api_context):
    res = api_context.post("todos/", data={"title": "   "})

    assert res.status == 400, res.text()
    assert "title" in res.json()
