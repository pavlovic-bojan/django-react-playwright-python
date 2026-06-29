"""REST contract tests driven by Playwright's APIRequestContext.

Assert HTTP status codes AND JSON bodies against the api-contract skill:
fields {id, title, completed, created_at, updated_at}; list newest-first.
"""
import allure
import pytest

CONTRACT_FIELDS = {"id", "title", "completed", "created_at", "updated_at"}


@allure.feature("API")
@allure.story("Create")
@pytest.mark.api
@allure.title("POST /todos/ returns 201 and the contract Todo shape")
def test_create_returns_201_and_contract_shape(api_context, api_cleanup, unique_suffix):
    title = f"API create {unique_suffix}"

    res = api_context.post("todos/", data={"title": title, "completed": False})

    assert res.status == 201, res.text()
    body = res.json()
    api_cleanup.append(body["id"])

    assert CONTRACT_FIELDS.issubset(body.keys())
    assert isinstance(body["id"], int)
    assert body["title"] == title
    assert body["completed"] is False
    assert isinstance(body["created_at"], str) and body["created_at"]
    assert isinstance(body["updated_at"], str) and body["updated_at"]


@allure.feature("API")
@allure.story("List")
@pytest.mark.api
@allure.title("GET /todos/ returns 200 and is ordered newest-first")
def test_list_returns_200_newest_first(api_context, api_cleanup, unique_suffix):
    older = api_context.post(
        "todos/", data={"title": f"API older {unique_suffix}"}
    ).json()
    newer = api_context.post(
        "todos/", data={"title": f"API newer {unique_suffix}"}
    ).json()
    api_cleanup.extend([older["id"], newer["id"]])

    res = api_context.get("todos/")
    assert res.status == 200, res.text()
    todos = res.json()
    assert isinstance(todos, list)

    # Look only at the two todos this test created (suffix-scoped, isolation-safe).
    ours = [t for t in todos if t["id"] in {older["id"], newer["id"]}]
    assert [t["id"] for t in ours] == [newer["id"], older["id"]]


@allure.feature("API")
@allure.story("Retrieve")
@pytest.mark.api
@allure.title("GET /todos/{id}/ returns 200 for existing, 404 for missing")
def test_retrieve_200_and_404(api_context, api_cleanup, unique_suffix):
    created = api_context.post(
        "todos/", data={"title": f"API retrieve {unique_suffix}"}
    ).json()
    api_cleanup.append(created["id"])

    ok = api_context.get(f"todos/{created['id']}/")
    assert ok.status == 200, ok.text()
    assert ok.json()["id"] == created["id"]

    missing = api_context.get("todos/99999999/")
    assert missing.status == 404


@allure.feature("API")
@allure.story("Update")
@pytest.mark.api
@allure.title("PATCH /todos/{id}/ toggles completed and returns 200")
def test_patch_toggles_completed(api_context, api_cleanup, unique_suffix):
    created = api_context.post(
        "todos/", data={"title": f"API patch {unique_suffix}", "completed": False}
    ).json()
    api_cleanup.append(created["id"])

    res = api_context.patch(f"todos/{created['id']}/", data={"completed": True})
    assert res.status == 200, res.text()
    body = res.json()
    assert body["completed"] is True
    assert body["title"] == created["title"]


@allure.feature("API")
@allure.story("Update")
@pytest.mark.api
@allure.title("PUT /todos/{id}/ replaces the resource and returns 200")
def test_put_replaces_resource(api_context, api_cleanup, unique_suffix):
    created = api_context.post(
        "todos/", data={"title": f"API put {unique_suffix}", "completed": False}
    ).json()
    api_cleanup.append(created["id"])

    new_title = f"API put updated {unique_suffix}"
    res = api_context.put(
        f"todos/{created['id']}/",
        data={"title": new_title, "completed": True},
    )
    assert res.status == 200, res.text()
    body = res.json()
    assert body["title"] == new_title
    assert body["completed"] is True


@allure.feature("API")
@allure.story("Delete")
@pytest.mark.api
@allure.title("DELETE /todos/{id}/ returns 204 and the todo is gone")
def test_delete_returns_204(api_context, unique_suffix):
    created = api_context.post(
        "todos/", data={"title": f"API delete {unique_suffix}"}
    ).json()

    res = api_context.delete(f"todos/{created['id']}/")
    assert res.status == 204

    gone = api_context.get(f"todos/{created['id']}/")
    assert gone.status == 404
