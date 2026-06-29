"""API error-case contract tests.

Covers every 400 and 404 status code specified in the api-contract that is
not already covered by ``test_todos_crud.py`` or ``test_todos_validation.py``:

  - PATCH /todos/{id}/  → 400 (blank title), 404 (missing)
  - PUT  /todos/{id}/   → 400 (blank title), 404 (missing)
  - DELETE /todos/{id}/ → 404 (missing)
  - POST /todos/        → 400 (title > 255 chars)
  - POST /todos/        → 201 with completed defaulting to false when omitted
"""
import allure
import jsonschema
import pytest

from schemas.todo_schemas import ERROR_400_SCHEMA, ERROR_404_SCHEMA

MISSING_ID = 99999999  # an id that almost certainly does not exist


# ---------------------------------------------------------------------------
# PATCH — 400 and 404
# ---------------------------------------------------------------------------


@allure.feature("API")
@allure.story("Validation")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.api
@allure.title("PATCH /todos/{id}/ with a blank title returns 400 matching error schema")
def test_patch_blank_title_returns_400(api_context, api_cleanup, unique_suffix):
    with allure.step("Seed a todo"):
        created = api_context.post(
            "todos/", data={"title": f"Patch blank {unique_suffix}"}
        ).json()
        api_cleanup.append(created["id"])

    with allure.step("PATCH with an empty title"):
        res = api_context.patch(f"todos/{created['id']}/", data={"title": ""})

    with allure.step("Status code is 400"):
        assert res.status == 400, res.text()

    with allure.step("Response body matches the ERROR_400_SCHEMA"):
        jsonschema.validate(instance=res.json(), schema=ERROR_400_SCHEMA)

    with allure.step("Error is keyed on 'title'"):
        assert "title" in res.json()


@allure.feature("API")
@allure.story("Not found")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.api
@allure.title("PATCH /todos/{id}/ for a non-existent todo returns 404")
def test_patch_nonexistent_todo_returns_404(api_context):
    with allure.step(f"PATCH /todos/{MISSING_ID}/ (does not exist)"):
        res = api_context.patch(f"todos/{MISSING_ID}/", data={"completed": True})

    with allure.step("Status code is 404"):
        assert res.status == 404, res.text()

    with allure.step("Response body matches the ERROR_404_SCHEMA"):
        jsonschema.validate(instance=res.json(), schema=ERROR_404_SCHEMA)


# ---------------------------------------------------------------------------
# PUT — 400 and 404
# ---------------------------------------------------------------------------


@allure.feature("API")
@allure.story("Validation")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.api
@allure.title("PUT /todos/{id}/ with a blank title returns 400 matching error schema")
def test_put_blank_title_returns_400(api_context, api_cleanup, unique_suffix):
    with allure.step("Seed a todo"):
        created = api_context.post(
            "todos/", data={"title": f"Put blank {unique_suffix}"}
        ).json()
        api_cleanup.append(created["id"])

    with allure.step("PUT with an empty title"):
        res = api_context.put(
            f"todos/{created['id']}/", data={"title": "", "completed": False}
        )

    with allure.step("Status code is 400"):
        assert res.status == 400, res.text()

    with allure.step("Response body matches the ERROR_400_SCHEMA"):
        jsonschema.validate(instance=res.json(), schema=ERROR_400_SCHEMA)

    with allure.step("Error is keyed on 'title'"):
        assert "title" in res.json()


@allure.feature("API")
@allure.story("Not found")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.api
@allure.title("PUT /todos/{id}/ for a non-existent todo returns 404")
def test_put_nonexistent_todo_returns_404(api_context):
    with allure.step(f"PUT /todos/{MISSING_ID}/ (does not exist)"):
        res = api_context.put(
            f"todos/{MISSING_ID}/",
            data={"title": "Ghost", "completed": False},
        )

    with allure.step("Status code is 404"):
        assert res.status == 404, res.text()

    with allure.step("Response body matches the ERROR_404_SCHEMA"):
        jsonschema.validate(instance=res.json(), schema=ERROR_404_SCHEMA)


# ---------------------------------------------------------------------------
# DELETE — 404
# ---------------------------------------------------------------------------


@allure.feature("API")
@allure.story("Not found")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.api
@allure.title("DELETE /todos/{id}/ for a non-existent todo returns 404")
def test_delete_nonexistent_todo_returns_404(api_context):
    with allure.step(f"DELETE /todos/{MISSING_ID}/ (does not exist)"):
        res = api_context.delete(f"todos/{MISSING_ID}/")

    with allure.step("Status code is 404"):
        assert res.status == 404, res.text()

    with allure.step("Response body matches the ERROR_404_SCHEMA"):
        jsonschema.validate(instance=res.json(), schema=ERROR_404_SCHEMA)


# ---------------------------------------------------------------------------
# POST — title length limit (> 255 chars)
# ---------------------------------------------------------------------------


@allure.feature("API")
@allure.story("Validation")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.api
@allure.title("POST /todos/ with a 256-character title returns 400")
def test_post_title_too_long_returns_400(api_context):
    """The contract caps title at 255 chars; 256+ must be rejected by the server."""
    long_title = "a" * 256

    with allure.step("POST with a 256-character title"):
        res = api_context.post("todos/", data={"title": long_title})

    with allure.step("Status code is 400"):
        assert res.status == 400, res.text()

    with allure.step("Response body matches the ERROR_400_SCHEMA"):
        jsonschema.validate(instance=res.json(), schema=ERROR_400_SCHEMA)


# ---------------------------------------------------------------------------
# POST — completed defaults to false when omitted
# ---------------------------------------------------------------------------


@allure.feature("API")
@allure.story("Create")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.api
@allure.title("POST /todos/ without a 'completed' field defaults completed to false")
def test_create_without_completed_defaults_to_false(api_context, api_cleanup, unique_suffix):
    with allure.step("POST with only a title (no completed field)"):
        res = api_context.post("todos/", data={"title": f"Default completed {unique_suffix}"})

    with allure.step("Status code is 201"):
        assert res.status == 201, res.text()
        body = res.json()
        api_cleanup.append(body["id"])

    with allure.step("completed field is false"):
        assert body["completed"] is False
