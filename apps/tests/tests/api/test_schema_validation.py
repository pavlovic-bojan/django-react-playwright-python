"""JSON Schema validation for every successful API response.

Every endpoint that returns a Todo or a list of Todos must produce a body that
satisfies the schema in ``schemas/todo_schemas.py`` (which mirrors the
api-contract). These tests are the schema-level regression layer on top of the
status-code + field assertions in ``test_todos_crud.py``.
"""
import allure
import jsonschema
import pytest

from schemas.todo_schemas import TODO_LIST_SCHEMA, TODO_SCHEMA


@allure.feature("API")
@allure.story("Schema")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.api
@allure.title("POST /todos/ response matches the Todo JSON schema")
def test_create_response_matches_schema(api_context, api_cleanup, unique_suffix):
    with allure.step("Create a todo"):
        res = api_context.post(
            "todos/", data={"title": f"Schema create {unique_suffix}", "completed": False}
        )
        assert res.status == 201, res.text()
        body = res.json()
        api_cleanup.append(body["id"])

    with allure.step("Validate response body against TODO_SCHEMA"):
        jsonschema.validate(instance=body, schema=TODO_SCHEMA)


@allure.feature("API")
@allure.story("Schema")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.api
@allure.title("GET /todos/ response matches the Todo list JSON schema")
def test_list_response_matches_schema(api_context, api_cleanup, unique_suffix):
    with allure.step("Seed one todo so the list is non-empty"):
        created = api_context.post(
            "todos/", data={"title": f"Schema list {unique_suffix}"}
        ).json()
        api_cleanup.append(created["id"])

    with allure.step("GET /todos/"):
        res = api_context.get("todos/")
        assert res.status == 200, res.text()

    with allure.step("Validate response body against TODO_LIST_SCHEMA"):
        jsonschema.validate(instance=res.json(), schema=TODO_LIST_SCHEMA)


@allure.feature("API")
@allure.story("Schema")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.api
@allure.title("GET /todos/{id}/ response matches the Todo JSON schema")
def test_retrieve_response_matches_schema(api_context, api_cleanup, unique_suffix):
    with allure.step("Seed a todo"):
        created = api_context.post(
            "todos/", data={"title": f"Schema retrieve {unique_suffix}"}
        ).json()
        api_cleanup.append(created["id"])

    with allure.step(f"GET /todos/{created['id']}/"):
        res = api_context.get(f"todos/{created['id']}/")
        assert res.status == 200, res.text()

    with allure.step("Validate response body against TODO_SCHEMA"):
        jsonschema.validate(instance=res.json(), schema=TODO_SCHEMA)


@allure.feature("API")
@allure.story("Schema")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.api
@allure.title("PATCH /todos/{id}/ response matches the Todo JSON schema")
def test_patch_response_matches_schema(api_context, api_cleanup, unique_suffix):
    with allure.step("Seed a todo"):
        created = api_context.post(
            "todos/", data={"title": f"Schema patch {unique_suffix}", "completed": False}
        ).json()
        api_cleanup.append(created["id"])

    with allure.step("PATCH completed=true"):
        res = api_context.patch(
            f"todos/{created['id']}/", data={"completed": True}
        )
        assert res.status == 200, res.text()

    with allure.step("Validate response body against TODO_SCHEMA"):
        jsonschema.validate(instance=res.json(), schema=TODO_SCHEMA)


@allure.feature("API")
@allure.story("Schema")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.api
@allure.title("PUT /todos/{id}/ response matches the Todo JSON schema")
def test_put_response_matches_schema(api_context, api_cleanup, unique_suffix):
    with allure.step("Seed a todo"):
        created = api_context.post(
            "todos/", data={"title": f"Schema put {unique_suffix}", "completed": False}
        ).json()
        api_cleanup.append(created["id"])

    with allure.step("PUT with updated title and completed=true"):
        res = api_context.put(
            f"todos/{created['id']}/",
            data={"title": f"Schema put updated {unique_suffix}", "completed": True},
        )
        assert res.status == 200, res.text()

    with allure.step("Validate response body against TODO_SCHEMA"):
        jsonschema.validate(instance=res.json(), schema=TODO_SCHEMA)


@allure.feature("API")
@allure.story("Schema")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.api
@allure.title("GET /todos/ returns a plain array — no pagination wrapper")
def test_list_is_plain_array_not_paginated(api_context):
    """The contract specifies Todo[] — no {count, next, previous, results} envelope."""
    with allure.step("GET /todos/"):
        res = api_context.get("todos/")
        assert res.status == 200, res.text()

    with allure.step("Response is a JSON array, not a paginated object"):
        body = res.json()
        assert isinstance(body, list), (
            f"Expected a plain list, got {type(body).__name__}: {body!r}"
        )
