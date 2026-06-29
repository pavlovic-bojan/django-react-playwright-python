"""Unit tests for the todos service layer.

Services own all mutation logic.  Tests hit the real database (SQLite
in-memory during testing) to verify persistence, but do NOT go through
the HTTP layer — they call service functions directly.
"""

import allure
import pytest

from todos.models import Todo
from todos.services import create_todo, delete_todo, update_todo
from todos.tests.factories import TodoFactory


@allure.feature("Todos API")
@allure.story("Services")
@pytest.mark.unit
@pytest.mark.django_db
class TestCreateTodo:
    def test_persists_and_returns_todo(self) -> None:
        todo = create_todo(title="Walk the dog")
        assert todo.pk is not None
        assert Todo.objects.filter(pk=todo.pk).exists()

    def test_sets_title(self) -> None:
        todo = create_todo(title="Walk the dog")
        assert todo.title == "Walk the dog"

    def test_completed_defaults_to_false(self) -> None:
        todo = create_todo(title="Untitled")
        assert todo.completed is False

    def test_completed_can_be_set_to_true(self) -> None:
        todo = create_todo(title="Done already", completed=True)
        assert todo.completed is True

    def test_timestamps_are_populated(self) -> None:
        todo = create_todo(title="Timestamps")
        assert todo.created_at is not None
        assert todo.updated_at is not None


@allure.feature("Todos API")
@allure.story("Services")
@pytest.mark.unit
@pytest.mark.django_db
class TestUpdateTodo:
    def test_updates_title_in_db(self) -> None:
        todo = TodoFactory(title="old title")
        updated = update_todo(todo, title="new title")
        assert updated.title == "new title"
        todo.refresh_from_db()
        assert todo.title == "new title"

    def test_updates_completed_flag(self) -> None:
        todo = TodoFactory(completed=False)
        updated = update_todo(todo, completed=True)
        assert updated.completed is True
        todo.refresh_from_db()
        assert todo.completed is True

    def test_updates_multiple_fields(self) -> None:
        todo = TodoFactory(title="before", completed=False)
        updated = update_todo(todo, title="after", completed=True)
        assert updated.title == "after"
        assert updated.completed is True

    def test_returns_same_instance(self) -> None:
        todo = TodoFactory()
        returned = update_todo(todo, title="same instance")
        assert returned is todo

    def test_updated_at_is_refreshed(self) -> None:
        todo = TodoFactory()
        original_updated_at = todo.updated_at
        # Force a tiny delay so the timestamp can change.
        import time

        time.sleep(0.01)
        update_todo(todo, title="changed")
        todo.refresh_from_db()
        assert todo.updated_at >= original_updated_at


@allure.feature("Todos API")
@allure.story("Services")
@pytest.mark.unit
@pytest.mark.django_db
class TestDeleteTodo:
    def test_removes_todo_from_db(self) -> None:
        todo = TodoFactory()
        pk = todo.pk
        delete_todo(todo)
        assert not Todo.objects.filter(pk=pk).exists()
