import allure
import pytest

from todos.models import Todo

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@allure.feature("Todos API")
@allure.story("Create")
def test_create_todo_returns_201(api_client):
    res = api_client.post("/api/todos/", {"title": "Buy milk"}, format="json")
    assert res.status_code == 201
    assert res.data["id"] is not None
    assert res.data["title"] == "Buy milk"
    assert res.data["completed"] is False
    assert "created_at" in res.data
    assert "updated_at" in res.data


@allure.feature("Todos API")
@allure.story("Create")
def test_create_trims_title(api_client):
    res = api_client.post("/api/todos/", {"title": "  Walk dog  "}, format="json")
    assert res.status_code == 201
    assert res.data["title"] == "Walk dog"


@allure.feature("Todos API")
@allure.story("Create")
def test_create_blank_title_returns_400(api_client):
    res = api_client.post("/api/todos/", {"title": "   "}, format="json")
    assert res.status_code == 400
    assert "title" in res.data


@allure.feature("Todos API")
@allure.story("List")
def test_list_returns_200_newest_first(api_client):
    a = Todo.objects.create(title="oldest")
    b = Todo.objects.create(title="middle")
    c = Todo.objects.create(title="newest")

    res = api_client.get("/api/todos/")
    assert res.status_code == 200
    returned_ids = [row["id"] for row in res.data]
    assert returned_ids == [c.id, b.id, a.id]


@allure.feature("Todos API")
@allure.story("Retrieve")
def test_retrieve_returns_200(api_client):
    todo = Todo.objects.create(title="findme")
    res = api_client.get(f"/api/todos/{todo.id}/")
    assert res.status_code == 200
    assert res.data["title"] == "findme"


@allure.feature("Todos API")
@allure.story("Retrieve")
def test_retrieve_missing_returns_404(api_client):
    res = api_client.get("/api/todos/999999/")
    assert res.status_code == 404


@allure.feature("Todos API")
@allure.story("Update")
def test_patch_toggle_completed_returns_200(api_client):
    todo = Todo.objects.create(title="toggle me", completed=False)
    res = api_client.patch(f"/api/todos/{todo.id}/", {"completed": True}, format="json")
    assert res.status_code == 200
    assert res.data["completed"] is True
    assert res.data["title"] == "toggle me"
    todo.refresh_from_db()
    assert todo.completed is True


@allure.feature("Todos API")
@allure.story("Update")
def test_patch_blank_title_returns_400(api_client):
    todo = Todo.objects.create(title="keep")
    res = api_client.patch(f"/api/todos/{todo.id}/", {"title": "  "}, format="json")
    assert res.status_code == 400
    assert "title" in res.data


@allure.feature("Todos API")
@allure.story("Update")
def test_put_replaces_returns_200(api_client):
    todo = Todo.objects.create(title="before", completed=False)
    res = api_client.put(
        f"/api/todos/{todo.id}/",
        {"title": "after", "completed": True},
        format="json",
    )
    assert res.status_code == 200
    assert res.data["title"] == "after"
    assert res.data["completed"] is True


@allure.feature("Todos API")
@allure.story("Update")
def test_put_missing_returns_404(api_client):
    res = api_client.put(
        "/api/todos/999999/",
        {"title": "x", "completed": False},
        format="json",
    )
    assert res.status_code == 404


@allure.feature("Todos API")
@allure.story("Delete")
def test_delete_returns_204(api_client):
    todo = Todo.objects.create(title="delete me")
    res = api_client.delete(f"/api/todos/{todo.id}/")
    assert res.status_code == 204
    assert not Todo.objects.filter(id=todo.id).exists()


@allure.feature("Todos API")
@allure.story("Delete")
def test_delete_missing_returns_404(api_client):
    res = api_client.delete("/api/todos/999999/")
    assert res.status_code == 404


@allure.feature("Todos API")
@allure.story("Health")
def test_health_returns_200(api_client):
    res = api_client.get("/api/health/")
    assert res.status_code == 200
    assert res.data == {"status": "ok"}
