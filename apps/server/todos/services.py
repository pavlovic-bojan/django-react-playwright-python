"""Service functions — write/mutation layer for the todos domain.

Services encapsulate all business logic and state changes. Views call
services instead of touching the ORM directly. This keeps views thin and
makes the domain logic independently testable.
"""

import logging
from typing import Any

from .models import Todo

logger = logging.getLogger(__name__)


def create_todo(*, title: str, completed: bool = False) -> Todo:
    """Create and persist a new todo item.

    Args:
        title: The todo title (already validated/trimmed by the serializer).
        completed: Initial completion state; defaults to ``False``.

    Returns:
        The newly created ``Todo`` instance with all fields populated.
    """
    todo = Todo.objects.create(title=title, completed=completed)
    logger.debug("Created todo pk=%d title=%r", todo.pk, todo.title)
    return todo


def update_todo(todo: Todo, **fields: Any) -> Todo:
    """Update arbitrary fields on an existing todo and persist the change.

    Only the fields present in ``**fields`` are touched; ``updated_at`` is
    refreshed automatically via ``auto_now=True``.

    Args:
        todo: The existing ``Todo`` instance to mutate.
        **fields: Field-name / value pairs to apply (e.g. ``title="new"``).

    Returns:
        The same ``Todo`` instance after saving.
    """
    for attr, value in fields.items():
        setattr(todo, attr, value)
    todo.save()
    logger.debug("Updated todo pk=%d fields=%s", todo.pk, list(fields))
    return todo


def delete_todo(todo: Todo) -> None:
    """Hard-delete a todo item from the database.

    Args:
        todo: The ``Todo`` instance to remove.
    """
    pk = todo.pk
    todo.delete()
    logger.debug("Deleted todo pk=%d", pk)
