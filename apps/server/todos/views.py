"""Views — thin HTTP layer for the todos domain.

Each viewset method delegates to the selector/service layer so that no
business logic lives here.  DRF handles status codes, serialization, and
404/405 responses automatically.
"""

import logging

from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from . import selectors, services
from .models import Todo
from .serializers import TodoSerializer

logger = logging.getLogger(__name__)


class TodoViewSet(viewsets.ModelViewSet):
    """CRUD for todos under ``/api/todos/``.

    Ordering is driven by ``Todo.Meta.ordering`` (newest-first).  DRF
    supplies the standard status codes: 201 create, 200 retrieve/update,
    204 delete, 400 validation, 404 missing.

    The viewset does not declare a ``queryset`` class attribute so that
    ``get_queryset`` is always called at request time (safe for future
    per-request filtering such as auth scoping).  ``basename="todo"`` is
    therefore required on the router registration (see ``todos/urls.py``).
    """

    serializer_class = TodoSerializer

    def get_queryset(self) -> QuerySet[Todo]:
        return selectors.get_todo_list()

    def perform_create(self, serializer: TodoSerializer) -> None:  # type: ignore[override]
        todo = services.create_todo(
            title=serializer.validated_data["title"],
            completed=serializer.validated_data.get("completed", False),
        )
        # Bind the created instance so DRF serializes it in the 201 response.
        serializer.instance = todo

    def perform_update(self, serializer: TodoSerializer) -> None:  # type: ignore[override]
        todo = services.update_todo(
            serializer.instance,  # type: ignore[arg-type]
            **serializer.validated_data,
        )
        serializer.instance = todo

    def perform_destroy(self, instance: Todo) -> None:  # type: ignore[override]
        services.delete_todo(instance)


@api_view(["GET"])
def health(_request: Request) -> Response:
    """Liveness probe polled by the container entrypoint."""
    return Response({"status": "ok"})
