"""Selector functions — read-only query layer for the todos domain.

Selectors encapsulate all database reads so views stay thin and the query
logic is testable in isolation. They never mutate state.
"""

from django.db.models import QuerySet

from .models import Todo


def get_todo_list() -> QuerySet[Todo]:
    """Return all todos ordered newest-first (from ``Todo.Meta.ordering``)."""
    return Todo.objects.all()


def get_todo_by_pk(pk: int) -> Todo:
    """Return a single todo by primary key.

    Raises ``Todo.DoesNotExist`` if not found — the caller is responsible for
    converting that to a 404 (DRF's ``get_object`` does this automatically).
    """
    return Todo.objects.get(pk=pk)
