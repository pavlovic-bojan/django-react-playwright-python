"""Unit tests for the todos selector layer.

Selectors are read-only query functions.  Each test isolates a single
selector, uses ``TodoFactory`` for data setup, and asserts on the returned
QuerySet or instance.
"""

import allure
import pytest

from todos.models import Todo
from todos.selectors import get_todo_by_pk, get_todo_list
from todos.tests.factories import TodoFactory


@allure.feature("Todos API")
@allure.story("Selectors")
@pytest.mark.unit
@pytest.mark.django_db
class TestGetTodoList:
    def test_returns_all_todos(self) -> None:
        TodoFactory.create_batch(3)
        assert get_todo_list().count() == 3

    def test_empty_database_returns_empty_queryset(self) -> None:
        assert get_todo_list().count() == 0

    def test_ordered_newest_first(self) -> None:
        first = TodoFactory(title="first")
        second = TodoFactory(title="second")
        ids = list(get_todo_list().values_list("pk", flat=True))
        assert ids == [second.pk, first.pk]


@allure.feature("Todos API")
@allure.story("Selectors")
@pytest.mark.unit
@pytest.mark.django_db
class TestGetTodoByPk:
    def test_returns_existing_todo(self) -> None:
        todo = TodoFactory()
        found = get_todo_by_pk(todo.pk)
        assert found.pk == todo.pk
        assert found.title == todo.title

    def test_raises_does_not_exist_for_missing_pk(self) -> None:
        with pytest.raises(Todo.DoesNotExist):
            get_todo_by_pk(999_999)
